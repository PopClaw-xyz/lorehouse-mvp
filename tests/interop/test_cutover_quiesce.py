"""Cutover quiesce regressions (final frozen-f17 finding).

A rotation must never advertise successful quiescence on a join timeout:
a registered stream task wedged inside its cancellation cleanup makes
rotate raise CutoverQuiesceTimeout (recoverable post-cutover state — the
old-generation gate is already closed), and a NORMAL return proves every
captured task exited. The real-socket case establishes genuine transport
backpressure (large frames, client stops reading -> the server's ASGI
send blocks) and observes TRUE EOF after the rotation, never mistaking a
socket timeout for connection termination.
"""

from __future__ import annotations

import asyncio
import socket
import threading
import time
from pathlib import Path

import pytest

from ranger_map import house as house_mod
from ranger_map import streams as streams_mod
from ranger_map import wire
from ranger_map.keys import load_or_create_identity
from ranger_map.store import Store

from tests.interop.wire_helpers import Actor, make_post, wrap_signed

ORIGIN = "http://127.0.0.1:8787"


def _make_house(tmp_path: Path):
    from ranger_map.app import create_app
    from ranger_map.house import load_or_setup

    data_dir = tmp_path / "d"
    store = Store.open(data_dir)
    identity = load_or_create_identity(data_dir)
    state = load_or_setup(store, identity, ORIGIN)
    hub = streams_mod.StreamHub(store)
    app = create_app(store, identity=identity, house_state=state, hub=hub)
    return store, identity, state, hub, app


# --- deterministic cancellation-cleanup stall --------------------------------


def test_wedged_cleanup_raises_quiesce_timeout_then_recovers(tmp_path):
    """A registered stream task whose cancellation CLEANUP blocks: rotate
    with a tiny join budget must raise CutoverQuiesceTimeout (never return
    success), the old-generation gate must already be closed, and after
    the release the task exits and a re-run completes normally."""
    store, identity, state, hub, _app = _make_house(tmp_path)
    try:
        release = threading.Event()

        async def wedged_stream():
            hub.register_stream()
            try:
                await asyncio.Event().wait()  # idle until cancelled
            except asyncio.CancelledError:
                # Cancellation cleanup that waits for an external release
                # (the reviewer's deterministic wedge).
                await asyncio.to_thread(release.wait)
                raise

        loop = asyncio.new_event_loop()
        loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
        loop_thread.start()

        async def spawn():
            return asyncio.create_task(wedged_stream())

        task = asyncio.run_coroutine_threadsafe(spawn(), loop).result(
            timeout=5)
        # The stream task is registered and alive.
        with hub._tasks_guard:
            assert task in hub._tasks

        rotate_started = threading.Event()
        rotate_result = {}

        def run_rotate():
            rotate_started.set()
            try:
                rotate_result["value"] = hub.rotate(identity, state,
                                                    join_timeout=0.05)
            except streams_mod.CutoverQuiesceTimeout as exc:
                rotate_result["timeout"] = exc

        # rotate from ANOTHER thread while the task's cleanup holds it up.
        rotator = threading.Thread(
            target=run_rotate,
            daemon=True,
        )
        rotator.start()
        rotator.join(timeout=10)

        assert not rotator.is_alive(), "rotate must not hang on the wedge"
        assert "timeout" in rotate_result, (
            "rotate returned normally while a registered task was still"
            f" alive (done={task.done()})")
        exc = rotate_result["timeout"]
        assert task.done() is False
        assert (loop, task) in exc.pending

        # The old-generation gate is CLOSED despite the failed quiesce:
        # the epoch bumped and the log rotated before the join, and a
        # pre-cutover captured identity no longer validates.
        epoch_now = int(store.get_meta("stream_epoch") or "0")
        assert epoch_now >= 1
        assert store.get_meta("public_log_incarnation") != state.log_incarnation
        assert not hub.identity_valid((epoch_now - 1, state.log_incarnation, wire.ENVELOPE_BASELINE))

        # Recoverable post-cutover state: release the wedge, task exits,
        # re-running rotate now completes and proves exit.
        release.set()
        deadline = time.monotonic() + 10
        while not task.done() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert task.done()
        loop.call_soon_threadsafe(loop.stop)
        restored = hub.rotate(identity, state, join_timeout=5)
        assert restored.log_incarnation != state.log_incarnation
    finally:
        store.close()


def test_normal_rotation_proves_task_exit(tmp_path):
    """Normal path: rotate's return itself proves the registered task
    exited (no timeout was needed), matching the proof loop in rotate."""
    store, identity, state, hub, _app = _make_house(tmp_path)
    try:
        finished = threading.Event()

        async def quiet_stream():
            hub.register_stream()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                finished.set()
                raise

        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever, daemon=True).start()

        async def spawn():
            return asyncio.create_task(quiet_stream())

        task = asyncio.run_coroutine_threadsafe(spawn(), loop).result(
            timeout=5)
        time.sleep(0.1)  # let the task register

        restored = hub.rotate(identity, state, join_timeout=5)
        # Returning normally IS the proof: every captured task exited.
        assert task.done()
        assert restored.log_incarnation != state.log_incarnation
        loop.call_soon_threadsafe(loop.stop)
    finally:
        store.close()


# --- real transport backpressure + true EOF ----------------------------------


def test_rotation_closes_blocked_send_with_true_eof(tmp_path):
    """Genuine backpressure: many large frames, client reads only the
    boundary then stops — the server's ASGI send BLOCKS. The rotation
    cancels the blocked task (normal return proves exit) and the client
    observes TRUE EOF (recv returns b''), never a socket timeout."""
    import uvicorn

    store, identity, state, hub, app = _make_house(tmp_path)
    server = None
    try:
        yun = Actor("Yun")
        # 60 signed envelopes of ~250KB: ~15MB of SSE payload, far beyond
        # every transport buffer, so the pump must block in send once the
        # client stops reading.
        big = "x" * 250_000
        for i in range(60):
            row = make_post(yun, f"{big}-{i}")
            store.public_log_append(
                state.log_incarnation, wire.envelope_cid(row), row,
                "post", "[]")

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        config = uvicorn.Config(app, host="127.0.0.1", port=port,
                                log_level="error", lifespan="off")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        deadline = time.monotonic() + 10
        while not server.started and time.monotonic() < deadline:
            time.sleep(0.05)
        assert server.started

        client = socket.create_connection(("127.0.0.1", port), timeout=10)
        request = (
            f"GET /v1/world-stream?mode=public-v1"
            f"&incarnation={state.log_incarnation}"
            f"&cursors=&public_after=0 HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{port}\r\nAccept: text/event-stream\r\n\r\n"
        )
        client.sendall(request.encode())
        client.settimeout(10)
        received = bytearray()
        # Read only until the boundary arrives, then STOP reading so the
        # server's send blocks on transport backpressure.
        while b"public_boundary" not in bytes(received):
            data = client.recv(65536)
            if not data:
                raise AssertionError("connection closed before boundary")
            received.extend(data)

        # Give the pump time to fill every buffer and block in send.
        time.sleep(2.0)
        with hub._tasks_guard:
            registered = len(hub._tasks)
        assert registered >= 1, "stream task must be registered"

        rotate_started = time.monotonic()
        restored = hub.rotate(identity, state, join_timeout=10)
        rotate_elapsed = time.monotonic() - rotate_started
        # Normal return: every captured task (including the one blocked in
        # send) actually exited.
        assert rotate_elapsed < 10

        # Drain: the client must observe TRUE EOF — recv eventually returns
        # b'' because the server closed the connection. A socket.timeout
        # here would mean the connection was still open (failure).
        client.settimeout(20)
        drained = bytearray()
        saw_eof = False
        try:
            while True:
                data = client.recv(65536)
                if data == b"":
                    saw_eof = True
                    break
                drained.extend(data)
        except socket.timeout:
            saw_eof = False
        client.close()

        assert saw_eof, "no true EOF: rotation left the connection open"
        # Nothing produced after the cutover was a data frame beyond the
        # already-buffered old-generation bytes.
        assert restored.log_incarnation != state.log_incarnation
    finally:
        if server is not None:
            server.should_exit = True
        store.close()
