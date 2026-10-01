"""Regressions for the frozen-61311fd follow-up findings.

1. Deterministic-barrier reproduction of the same-request_id double-miss
   race (both authenticated first attempts miss the outside-tx lookup,
   synchronise, then serialise INSIDE the write transaction).
2. Idle inbox streams close on leave/expiry even with no pending frames.
3. Rotation stop/JOIN evidence against a real in-process uvicorn server:
   a live SSE connection suspended mid-read is cancelled AND joined, and
   the server closes the socket; no old-log bytes arrive afterwards.
"""

from __future__ import annotations

import asyncio
import base64
import json
import socket
import threading
import time
import urllib.request
from pathlib import Path

import pytest

from ranger_map import sessions as sessions_mod
from ranger_map import streams as streams_mod
from ranger_map import wire

from tests.interop.test_streams_live import LiveServer
from tests.interop.wire_helpers import (
    Actor,
    check_in_intent,
    make_dm,
    make_post,
    parse_ack,
    session_request,
    wrap_signed,
)

ENTER, LEAVE = 1, 3
ORIGIN = "http://127.0.0.1:8787"


# --- 1. deterministic same-request_id double-miss race -----------------------


def test_same_request_id_double_miss_serialises_in_tx(house, monkeypatch):
    """Two authenticated FIRST attempts, same request_id, both miss the
    outside-tx lookup before either commits — forced deterministically via
    a barrier injected at the miss, not by timing luck."""
    actor = Actor("Yun")
    payloads = [session_request(actor, ENTER, 10, request_id="req-race-1",
                                nonce=f"race-{i}") for i in range(2)]
    original_query_one = house.store.query_one
    barrier = threading.Barrier(2, timeout=10)
    waited = {"count": 0}
    lock = threading.Lock()

    def racing_query_one(sql, params=()):
        row = original_query_one(sql, params)
        if (row is None and "FROM session_requests" in sql
                and "WHERE request_id" in sql):
            with lock:
                first_wait = waited["count"] < 2
                if first_wait:
                    waited["count"] += 1
            if first_wait:
                # Both threads have now MISSED outside any transaction; hold
                # them here until the pair is synchronised.
                barrier.wait()
        return row

    monkeypatch.setattr(house.store, "query_one", racing_query_one)

    results = []
    start = threading.Barrier(2)

    def worker(payload):
        start.wait()
        decision = sessions_mod.handle_session_request(
            house.store, house.identity, house.state, payload)
        results.append(decision)

    threads = [threading.Thread(target=worker, args=(p,)) for p in payloads]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
    monkeypatch.undo()

    assert not any(thread.is_alive() for thread in threads)  # no IntegrityError hang
    assert waited["count"] == 2                              # the race really happened
    assert len({d.ack_bytes for d in results}) == 1          # one immutable ACK
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM session_requests"
    )["c"] == 1
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM sessions")["c"] == 1      # one generation


# --- 2. idle inbox streams close without pending frames ----------------------


def _drive_inbox(house, monkeypatch_unused, token_is_v2, token, actor_id,
                 seed_dm_sender=None, act_between=None):
    """Drive stream_inbox_events directly: a seeded DM arrives first, then
    the stream goes idle while act_between changes authorization state; the
    generator must terminate without further frames or heartbeats."""
    streams_mod.POLL_SECONDS = 0.05
    streams_mod.HEARTBEAT_SECONDS = 600.0
    chunks = []

    async def run():
        generator = streams_mod.stream_inbox_events(
            house.store, house.identity, house.hub, house.state.origin,
            actor_id, token, token_is_v2, 0)
        index = 0
        async for chunk in generator:
            chunks.append(chunk)
            if act_between is not None and index == 0:
                act_between()
            index += 1
            if index > 400:  # heartbeat spam guard for the failure case
                break

    try:
        asyncio.run(run())
    finally:
        streams_mod.POLL_SECONDS = 0.5
        streams_mod.HEARTBEAT_SECONDS = 15.0
    return chunks


def test_idle_v2_stream_closes_on_leave_without_new_dm(house):
    from tests.interop.wire_helpers import make_dm as build_dm
    yun, luna = Actor("Yun"), Actor("Luna")
    ack = parse_ack(house.client.post(
        "/v1/house-session",
        content=session_request(luna, ENTER, 10)).content)
    token = ack.core.inbox_read_token
    house.client.post("/v1/push",
                      content=wrap_signed(build_dm(yun, luna, "seed"), yun))

    def leave():
        house.client.post("/v1/house-session",
                          content=session_request(luna, LEAVE, 11))

    chunks = _drive_inbox(house, None, True, token, luna.popclaw_id,
                          seed_dm_sender=yun, act_between=leave)
    # The generator TERMINATED (async for completed). After the leave no
    # further frame or heartbeat was produced while idle.
    assert len(chunks) == 1  # the seeded DM only
    assert "keepalive" not in "".join(chunks)


def test_idle_v2_stream_closes_on_expiry_without_new_dm(house):
    from tests.interop.wire_helpers import make_dm as build_dm
    yun, luna = Actor("Yun"), Actor("Luna")
    ack = parse_ack(house.client.post(
        "/v1/house-session",
        content=session_request(luna, ENTER, 10)).content)
    token = ack.core.inbox_read_token
    house.client.post("/v1/push",
                      content=wrap_signed(build_dm(yun, luna, "seed"), yun))

    def expire():
        house.store.execute(
            "UPDATE sessions SET lease_expires_at = ? WHERE session_id = ?",
            (int(time.time()) - 5, ack.core.session_id))

    chunks = _drive_inbox(house, None, True, token, luna.popclaw_id,
                          seed_dm_sender=yun, act_between=expire)
    assert len(chunks) == 1
    assert "keepalive" not in "".join(chunks)


# --- 3. rotation stop/join on a real suspended connection --------------------


def test_rotation_cancels_and_joins_real_stream(tmp_path):
    """Honest smoke only: a real uvicorn server, a real socket client that
    stops reading mid-stream (tiny frames, so this does NOT establish
    transport backpressure — the blocked-send/true-EOF proof lives in
    tests/interop/test_cutover_quiesce.py). The rotation cancels and joins
    the stream task and the server closes the suspended connection.

    What this test can and cannot pin. A rotation does two things: it
    invalidates the captured identity, and it cancels the stream task.
    Which one the generator meets first is a genuine race, so there are TWO
    legitimate terminal outcomes — the fence runs first and surfaces
    public_gap(log_incarnation_changed), or the cancellation lands first
    and the task exits having produced nothing further. Both close the
    connection and neither produces post-cutover data, so demanding the gap
    here would be asserting which side of a race won.

    The bytes read after the client resumes are also not "what was produced
    after the rotation": they include whatever was still sitting in the
    socket buffer from before it. So this test asserts what a real socket
    can actually witness — the join returns promptly, the server closes the
    connection, and nothing follows a gap once one appears. The gap path
    itself is pinned deterministically, without any cancellation, by
    tests/interop/test_fences_and_manifest.py."""
    import uvicorn

    from ranger_map.app import create_app
    from ranger_map.house import load_or_setup
    from ranger_map.keys import load_or_create_identity
    from ranger_map.store import Store

    data_dir = tmp_path / "d"
    store = Store.open(data_dir)
    identity = load_or_create_identity(data_dir)
    state = load_or_setup(store, identity, ORIGIN)
    hub = streams_mod.StreamHub(store)
    app = create_app(store, identity=identity, house_state=state, hub=hub)

    with socket.socket() as port_probe:
        port_probe.bind(("127.0.0.1", 0))
        port = port_probe.getsockname()[1]
    config = uvicorn.Config(app, host="127.0.0.1", port=port,
                            log_level="error", lifespan="off")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started and time.monotonic() < deadline:
            time.sleep(0.05)
        assert server.started

        yun = Actor("Yun")
        import urllib.request as urlrequest

        push = urlrequest.Request(f"{ORIGIN.replace('8787', str(port))}/v1/push",
                                  data=wrap_signed(make_post(yun, "one"), yun),
                                  method="POST")
        urlrequest.urlopen(push, timeout=5).read()

        # Open the stream on a raw socket and consume the first chunks.
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
        while b"public_frame" not in bytes(received):
            data = client.recv(4096)
            if not data:
                break
            received.extend(data)
        assert b"public_boundary" in bytes(received)
        assert b"public_frame" in bytes(received)

        # Suspend the client mid-stream (no further reads), then rotate
        # from this thread: cancel + bounded join must close the stream.
        rotate_started = time.monotonic()
        hub.rotate(identity, state)
        rotate_elapsed = time.monotonic() - rotate_started

        # The join returned promptly (bounded), and the server closed the
        # suspended connection: the next read hits EOF or a reset.
        client.settimeout(5)
        post_rotation = bytearray()
        # How the read ended is itself evidence, so record it rather than
        # swallowing every outcome alike. ConnectionResetError and
        # TimeoutError are both OSError subclasses, so they are caught
        # first.
        closed_by = None
        try:
            while True:
                data = client.recv(4096)
                if not data:
                    closed_by = "eof"
                    break
                post_rotation.extend(data)
        except ConnectionResetError:
            closed_by = "reset"
        except TimeoutError:
            closed_by = "timeout"
        except OSError as exc:
            # Only an explicit connection reset counts as the peer going
            # away. Every other socket error is a failure of this test's
            # own plumbing, not evidence about the server, so it is
            # recorded distinctly and fails below rather than being
            # relabelled as a close.
            closed_by = f"socket-error:{exc.errno}"
        client.close()

        # The bounded join returned, which is what proves cancel+join ran.
        assert rotate_elapsed < 10
        tail = bytes(post_rotation)

        # The response must be TERMINATED, and the two legitimate terminal
        # outcomes leave different evidence on a real socket:
        #   cancelled first — the ASGI app returns without completing, so
        #     uvicorn closes the connection and the client reads EOF (or a
        #     reset);
        #   fence first — the generator yields the gap and returns, so the
        #     chunked body is closed off with its terminator and the TCP
        #     connection may legitimately be kept alive for reuse, which
        #     means no EOF ever arrives.
        # A bare read timeout with neither witness is the absence of
        # evidence, not a weaker form of it, and must fail: it would mean
        # the server left the stream hanging open after the cutover. A
        # chunked terminator is a complete HTTP response and is accepted on
        # its own terms — TCP EOF is not required for the stream to have
        # ended.
        body_terminated = tail.endswith(b"0\r\n\r\n")
        assert closed_by in ("eof", "reset") or body_terminated, (
            f"no terminal evidence after the cutover (read ended by"
            f" {closed_by}, last bytes {tail[-40:]!r}): the stream was"
            f" neither closed nor properly ended")
        # Check-to-send semantics. A chunk that passed the fence BEFORE the
        # cutover may still be in the socket buffer and flush now, so its
        # presence here proves nothing either way. What must hold is that
        # once the terminal gap appears, the connection carries nothing
        # further — no data frame, and no second checkpoint.
        gap_index = tail.find(b"event: public_gap")
        if gap_index >= 0:
            after_gap = tail[gap_index + len(b"event: public_gap"):]
            assert b"event: public_frame" not in after_gap
            assert b"event: public_checkpoint" not in after_gap
        # Exactly one checkpoint at most: the pre-rotation replay one. A
        # second would mean the live loop certified coverage after the
        # cutover, which the fence exists to prevent.
        assert tail.count(b"event: public_checkpoint") <= 1
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        store.close()
