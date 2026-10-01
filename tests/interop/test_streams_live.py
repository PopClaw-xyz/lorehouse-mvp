"""Interop layer 5b: LIVE lanes against a real server process.

The in-process transport only delivers a streaming response once it
completes, so never-ending lanes (live public stream, private DM stream)
are exercised here against a real uvicorn subprocess, reading SSE
incrementally over a blocking socket — closer to a real client anyway.
"""

from __future__ import annotations

import base64
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from ranger_map import wire  # noqa: E402

from tests.interop.wire_helpers import (  # noqa: E402
    Actor,
    check_in_intent,
    make_dm,
    make_post,
    session_request,
    wrap_signed,
)


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class LiveServer:
    def __init__(self, tmp_path: Path):
        self.port = free_port()
        self.origin = f"http://127.0.0.1:{self.port}"
        self.data_dir = tmp_path / "live"
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        self.process = subprocess.Popen(
            [sys.executable, "-m", "ranger_map",
             "--host", "127.0.0.1", "--port", str(self.port),
             "--data-dir", str(self.data_dir)],
            cwd=REPO_ROOT, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self._wait_healthy()

    def _wait_healthy(self, timeout=20.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(
                        f"{self.origin}/healthz", timeout=2) as response:
                    if response.status == 200:
                        return
            except Exception:
                time.sleep(0.2)
        raise AssertionError("live server did not start")

    def url(self, path: str) -> str:
        return f"{self.origin}{path}"

    def post_signed(self, payload: bytes, actor) -> dict:
        request = urllib.request.Request(
            self.url("/v1/push"), data=wrap_signed(payload, actor),
            method="POST")
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read())

    def session(self, actor, operation=1, op_seq=10, target=""):
        payload = session_request(actor, operation, op_seq,
                                  target_session=target, origin=self.origin)
        request = urllib.request.Request(
            self.url("/v1/house-session"), data=payload, method="POST")
        with urllib.request.urlopen(request, timeout=5) as response:
            return wire.HouseSessionAck.FromString(response.read())

    def stop(self):
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGINT)
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:  # pragma: no cover
                self.process.kill()


class SseReader:
    """Incremental SSE reader over a blocking socket."""

    def __init__(self, url: str, headers: dict | None = None,
                 idle_timeout: float = 12.0):
        request = urllib.request.Request(url)
        for key, value in (headers or {}).items():
            request.add_header(key, value)
        self.response = urllib.request.urlopen(request, timeout=idle_timeout)
        self.events: list[tuple[str, bytes]] = []

    def read_until(self, predicate, timeout: float = 15.0) -> list:
        deadline = time.monotonic() + timeout
        current = None
        while time.monotonic() < deadline:
            line = self.response.readline()
            if not line:
                break
            text = line.decode("utf-8").rstrip("\n")
            if text.startswith("event: "):
                current = text[7:]
            elif text.startswith("data: "):
                self.events.append((current or "message",
                                    base64.b64decode(text[6:])))
                if predicate(self.events):
                    return self.events
        return self.events

    def close(self):
        try:
            self.response.close()
        except Exception:
            pass


@pytest.fixture()
def server(tmp_path):
    live = LiveServer(tmp_path)
    yield live
    live.stop()


def get_manifest(server) -> dict:
    with urllib.request.urlopen(server.url("/v1/manifest"), timeout=5) as r:
        return json.loads(r.read())


def test_live_public_stream_replay_then_live_delivery(server):
    yun = Actor("Yun")
    server.post_signed(make_post(yun, "first"), yun)
    server.post_signed(make_post(yun, "second"), yun)
    manifest = get_manifest(server)
    log = manifest["world_interaction"]["public_stream"]["log_incarnation"]

    reader = SseReader(server.url(
        f"/v1/world-stream?mode=public-v1&incarnation={log}"
        f"&cursors=&public_after=0"))
    try:
        events = reader.read_until(
            lambda ev: any(name == "public_checkpoint" for name, _ in ev))
        names = [name for name, _ in events]
        assert names[0] == "public_boundary"
        frames = [wire.WorldStreamFrame.FromString(data)
                  for name, data in events if name == "public_frame"]
        assert [f.seq for f in frames] == [1, 2]
        checkpoint = wire.PublicStreamCheckpoint.FromString(
            [d for n, d in events if n == "public_checkpoint"][0])
        assert checkpoint.phase == "replay"

        # LIVE: a fresh accepted event arrives while the stream is open.
        server.post_signed(make_post(yun, "third"), yun)
        events = reader.read_until(
            lambda ev: any(name == "public_checkpoint" and
                           wire.PublicStreamCheckpoint.FromString(data).phase
                           == "live"
                           for name, data in ev))
        live_frames = [wire.WorldStreamFrame.FromString(d)
                       for n, d in events if n == "public_frame"]
        assert any(f.seq == 3 for f in live_frames)
        live_checkpoint = [wire.PublicStreamCheckpoint.FromString(d)
                           for n, d in events if n == "public_checkpoint"
                           and wire.PublicStreamCheckpoint.FromString(d).phase
                           == "live"]
        assert live_checkpoint and live_checkpoint[0].scopes == []
        assert live_checkpoint[0].public_through_seq == 3
    finally:
        reader.close()


def test_dm_live_delivery_and_revocation(server):
    yun, luna = Actor("Yun"), Actor("Luna")
    ack = server.session(luna, operation=1, op_seq=10)
    token = ack.core.inbox_read_token

    reader = SseReader(
        server.url(f"/inbox/{luna.popclaw_id}/stream"),
        headers={"x-popclaw-inbox-token": token})
    try:
        dm = make_dm(yun, luna, "live secret")
        server.post_signed(dm, yun)
        events = reader.read_until(lambda ev: len(ev) >= 1)
        assert events[0][0] == "envelope"
        assert events[0][1] == dm  # exact signed envelope bytes
    finally:
        reader.close()

    # Leaving revokes the token: a reconnect is refused outright.
    server.session(luna, operation=3, op_seq=11,
                   target=ack.core.session_id)
    request = urllib.request.Request(
        server.url(f"/inbox/{luna.popclaw_id}/stream"))
    request.add_header("x-popclaw-inbox-token", token)
    try:
        urllib.request.urlopen(request, timeout=5)
        raise AssertionError("revoked token must not open a stream")
    except urllib.error.HTTPError as exc:
        assert exc.code == 401


def test_check_in_fact_streamed_into_scope_lane(server):
    otto = Actor("Otto")
    ack = server.session(otto, operation=1, op_seq=10)
    payload = check_in_intent(
        otto, session_id=ack.core.session_id,
        fence=str(ack.core.house_revision),
        capability_revision=_capability_revision(server),
        house_key=_house_key(server), incarnation=_server_incarnation(server),
        house_origin=server.origin, lorehouse=server.origin)
    body = server.post_signed(payload, otto)
    assert body["status"] == "succeeded"

    reader = SseReader(server.url(
        f"/v1/world-stream?mode=public-v1&incarnation={_log(server)}"
        f"&cursors=rangermap:0"))
    try:
        events = reader.read_until(
            lambda ev: any(n == "public_checkpoint" for n, _ in ev))
        frames = [wire.WorldStreamFrame.FromString(d)
                  for n, d in events if n == "public_frame"]
        kinds = [f.kind for f in frames]
        assert kinds == ["rangermap.checked_in"]
        assert list(frames[0].scopes) == ["rangermap"]
    finally:
        reader.close()


def _manifest(server) -> dict:
    return get_manifest(server)


def _capability_revision(server) -> str:
    import hashlib

    with urllib.request.urlopen(server.url("/v1/manifest"), timeout=5) as r:
        return hashlib.sha256(r.read()).hexdigest()


def _house_key(server) -> str:
    return _manifest(server)["official_ids"][0]


def _server_incarnation(server) -> str:
    # The server incarnation is carried by the signed manifest proof.
    with urllib.request.urlopen(server.url("/v1/manifest"), timeout=5) as r:
        proof_b64 = r.headers["X-Popclaw-Manifest-Proof"]
    proof = wire.ManifestProof.FromString(base64.b64decode(proof_b64))
    return proof.house.incarnation


def _log(server) -> str:
    return _manifest(server)["world_interaction"]["public_stream"][
        "log_incarnation"]
