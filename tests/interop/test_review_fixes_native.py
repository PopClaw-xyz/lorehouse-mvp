"""Focused regressions for the native adapter review fixes (79cf4cf).

Findings 1-8 of ranger-map-native-review-fixes.md, each pinned to the exact
defect it guards against. Real-server cases reuse the live-server helper.
"""

from __future__ import annotations

import asyncio
import base64
import threading
import time
import urllib.error
import urllib.request

import pytest

from ranger_map import actions as actions_mod
from ranger_map import sessions as sessions_mod
from ranger_map import streams as streams_mod
from ranger_map import wire

from tests.interop.test_streams_live import LiveServer, SseReader
from tests.interop.wire_helpers import (
    Actor,
    check_in_intent,
    make_dm,
    make_post,
    parse_ack,
    session_request,
    wrap_signed,
)

ENTER, RENEW, LEAVE, STATUS = 1, 2, 3, 4


def open_inbox(url: str, token: str):
    request = urllib.request.Request(url)
    request.add_header("x-popclaw-inbox-token", token)
    return urllib.request.urlopen(request, timeout=5)


def post_session(house, payload: bytes):
    return house.client.post("/v1/house-session", content=payload)


def ack_of(house, response) -> wire.HouseSessionAck:
    return parse_ack(response.content)


# --- Finding 1: semantic (not byte-exact) request idempotency ---------------


def test_f1_retry_with_fresh_nonce_replays_stored_ack(house):
    actor = Actor("Yun")
    first = post_session(house, session_request(actor, ENTER, 10,
                                                request_id="req-sem-1"))
    # Same request_id/semantic operation, refreshed nonce and timestamps,
    # re-signed: a legal retry per house_session.proto, not a conflict.
    retry = post_session(house, session_request(actor, ENTER, 10,
                                                request_id="req-sem-1",
                                                nonce="fresh-nonce"))
    assert retry.status_code == 200
    assert retry.content == first.content  # immutable stored ACK replayed
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM sessions")["c"] == 1


def test_f1_retry_after_other_traffic_still_replays(house):
    actor = Actor("Yun")
    first = post_session(house, session_request(actor, ENTER, 10,
                                                request_id="req-sem-2"))
    # Unrelated traffic interleaves...
    post_session(house, session_request(Actor("Otto"), ENTER, 10))
    retry = post_session(house, session_request(actor, ENTER, 10,
                                                request_id="req-sem-2"))
    assert retry.content == first.content


def test_f1_retry_across_restart_replays(house, tmp_path):
    from ranger_map.house import load_or_setup
    from ranger_map.store import Store

    actor = Actor("Yun")
    first = post_session(house, session_request(actor, ENTER, 10,
                                                request_id="req-sem-3"))
    house.store.close()
    reopened = Store.open(tmp_path / "data")
    try:
        # A fresh process would re-sign with a fresh nonce; the durable
        # session_requests row still resolves the retry.
        decision = sessions_mod.handle_session_request(
            reopened, house.identity, house.state,
            session_request(actor, ENTER, 10, request_id="req-sem-3",
                            nonce="post-restart-nonce"))
        assert decision.ack_bytes == first.content
    finally:
        reopened.close()


def test_f1_concurrent_retries_single_ack(house):
    actor = Actor("Yun")
    payloads = [session_request(actor, ENTER, 10, request_id="req-sem-4",
                                nonce=f"n-{i}") for i in range(4)]
    results = []
    barrier = threading.Barrier(4)

    def worker(payload):
        barrier.wait()
        results.append(post_session(house, payload))

    threads = [threading.Thread(target=worker, args=(p,)) for p in payloads]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len({response.content for response in results}) == 1
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM sessions")["c"] == 1


def test_f1_semantic_change_is_conflict(house):
    actor = Actor("Yun")
    post_session(house, session_request(actor, ENTER, 10,
                                        request_id="req-sem-5"))
    changed = post_session(house, session_request(actor, ENTER, 11,
                                                  request_id="req-sem-5"))
    ack = ack_of(house, changed)
    assert ack.core.outcome == 7
    assert ack.core.error_code == sessions_mod.IDEMPOTENCY_CONFLICT


# --- Finding 2: actor-authoritative ACK revision -----------------------------


def test_f2_ack_reports_actor_generation_not_global_counter(house):
    a, b = Actor("A"), Actor("B")
    ack_a1 = ack_of(house, post_session(house, session_request(a, ENTER, 10)))
    ack_b = ack_of(house, post_session(house, session_request(b, ENTER, 10)))
    revision_a = ack_a1.core.house_revision
    revision_b = ack_b.core.house_revision
    assert revision_b > revision_a  # the global allocator grew...

    # ...but A's renew/status/leave all report A's OWN generation.
    ack_renew = ack_of(house, post_session(house, session_request(
        a, RENEW, 10, target_session=ack_a1.core.session_id)))
    assert ack_renew.core.house_revision == revision_a
    ack_status = ack_of(house, post_session(house, session_request(
        a, STATUS, 10, target_session=ack_a1.core.session_id)))
    assert ack_status.core.house_revision == revision_a
    ack_leave = ack_of(house, post_session(house, session_request(a, LEAVE, 11)))
    assert ack_leave.core.house_revision == revision_a

    # B still reports its own generation after A acted.
    ack_b_renew = ack_of(house, post_session(house, session_request(
        b, RENEW, 10, target_session=ack_b.core.session_id)))
    assert ack_b_renew.core.house_revision == revision_b


def test_f2_action_fence_survives_another_identity_entering(house):
    a, b = Actor("A"), Actor("B")
    ack_a = ack_of(house, post_session(house, session_request(a, ENTER, 10)))
    post_session(house, session_request(b, ENTER, 10))  # bumps the global

    payload = check_in_intent(
        a, session_id=ack_a.core.session_id,
        fence=str(ack_a.core.house_revision),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation)
    response = house.client.post("/v1/push", content=wrap_signed(payload, a))
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "succeeded"


# --- Finding 4: op_seq ordering and CAS across lease expiry ------------------


def _expire_sessions(store):
    store.execute("UPDATE sessions SET lease_expires_at = ?",
                  (int(time.time()) - 5,))


def test_f4_delayed_lower_enter_after_expiry_is_stale(house):
    actor = Actor("Yun")
    ack = ack_of(house, post_session(house, session_request(actor, ENTER, 10)))
    assert ack.core.outcome == 1
    _expire_sessions(house.store)
    # A delayed op_seq 9 request, still inside its signing window.
    delayed = ack_of(house, post_session(house, session_request(actor, ENTER, 9)))
    assert delayed.core.outcome == 7
    assert delayed.core.error_code == sessions_mod.STALE_OPERATION
    # No new generation was created for the stale op.
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM sessions")["c"] == 1


def test_f4_expected_revision_must_match_after_expiry(house):
    actor = Actor("Yun")
    ack = ack_of(house, post_session(house, session_request(actor, ENTER, 10)))
    revision = ack.core.house_revision
    _expire_sessions(house.store)
    mismatch = ack_of(house, post_session(house, session_request(
        actor, ENTER, 11, expected_revision=revision + 999)))
    assert mismatch.core.outcome == 7
    assert mismatch.core.error_code == sessions_mod.SESSION_FENCED
    # The matching CAS value re-enters cleanly after expiry.
    reentered = ack_of(house, post_session(house, session_request(
        actor, ENTER, 11, expected_revision=revision)))
    assert reentered.core.outcome == 1


def test_f4_watermark_persists_across_restart(house, tmp_path):
    from ranger_map.house import load_or_setup
    from ranger_map.store import Store

    actor = Actor("Yun")
    post_session(house, session_request(actor, ENTER, 10))
    post_session(house, session_request(actor, LEAVE, 15))
    house.store.close()
    reopened = Store.open(tmp_path / "data")
    try:
        state = load_or_setup(reopened, house.identity, house.state.origin)
        decision = sessions_mod.handle_session_request(
            reopened, house.identity, state,
            session_request(actor, ENTER, 12))
        ack = parse_ack(decision.ack_bytes)
        assert ack.core.outcome == 7
        assert ack.core.error_code == sessions_mod.STALE_OPERATION
    finally:
        reopened.close()


# --- Finding 5: sends are fenced (no data/checkpoint after a rotation) -------


def test_f5_rotation_between_page_frames_stops_delivery(tmp_path):
    from ranger_map.app import create_app
    from ranger_map.house import load_or_setup
    from ranger_map.keys import load_or_create_identity
    from ranger_map.store import Store
    from starlette.testclient import TestClient

    store = Store.open(tmp_path / "d")
    identity = load_or_create_identity(tmp_path / "d")
    state = load_or_setup(store, identity, "http://127.0.0.1:8787")
    hub = streams_mod.StreamHub(store)
    client = TestClient(create_app(store, identity=identity, house_state=state,
                                   hub=hub))
    yun = Actor("Yun")
    for text in ("one", "two", "three"):
        client.post("/v1/push", content=wrap_signed(make_post(yun, text), yun))

    selection = streams_mod.parse_public_request(
        {"mode": "public-v1", "cursors": "", "public_after": "0",
         "incarnation": state.log_incarnation},
        state.registered_scopes, state.log_incarnation)

    events = []
    post_rotation = {"chunks": []}
    rotation_index = {"n": None}
    rotate_error = {}
    rotate_done = threading.Event()

    def run_rotate():
        try:
            hub.rotate(identity, state)
        except Exception as exc:  # noqa: BLE001 - surfaced below
            rotate_error["exc"] = exc
        finally:
            rotate_done.set()

    async def run():
        generator = streams_mod.stream_public_events(
            hub, selection, state.registered_scopes)
        index = 0
        async for chunk in generator:
            if rotation_index["n"] is None and index >= 2:
                # Boundary + first frame consumed: rotate NOW, between the
                # remaining page frames and the checkpoint. Sync rotate
                # refuses the stream's own loop thread (it would join
                # itself), so it runs on its OWN thread and this loop stays
                # free to receive the cancellation.
                rotation_index["n"] = index
                threading.Thread(target=run_rotate, daemon=True).start()
            if rotation_index["n"] is not None and index > rotation_index["n"]:
                post_rotation["chunks"].append(chunk)
            for line in chunk.split("\n"):
                if line.startswith("data: "):
                    events.append(base64.b64decode(line[6:]))
            index += 1
            if len(post_rotation["chunks"]) >= 3:
                break

    try:
        asyncio.run(run())
    except asyncio.CancelledError:
        pass  # cancelled in-flight stream: the stop/join fence

    assert rotate_done.wait(timeout=10)
    assert "exc" not in rotate_error, rotate_error.get("exc")

    # Whatever arrived after the rotation, it must contain NO data frame
    # and NO checkpoint of the retired log.
    for chunk in post_rotation["chunks"]:
        if chunk.startswith("event: public_frame") or \
           chunk.startswith("event: public_checkpoint"):
            pytest.fail(f"old-log chunk leaked after rotation: {chunk[:60]!r}")


# --- Finding 6: valid_until enforced at transactional admission --------------


def test_f6_expiry_while_waiting_for_the_lock_is_rejected(house, monkeypatch):
    yun = Actor("Yun")
    ack = ack_of(house, post_session(house, session_request(yun, ENTER, 10)))
    calls = {"n": 0}
    real_now = actions_mod._now

    def advancing_clock():
        calls["n"] += 1
        # First call (pre-lock check) sees the real time; every later call
        # (the transactional admission and beyond) is far past valid_until.
        return real_now() if calls["n"] == 1 else real_now() + 10_000

    monkeypatch.setattr(actions_mod, "_now", advancing_clock)
    payload = check_in_intent(
        yun, session_id=ack.core.session_id,
        fence=str(ack.core.house_revision),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation,
        valid_until=real_now() + 300)  # valid at the pre-check
    response = house.client.post("/v1/push", content=wrap_signed(payload, yun))
    monkeypatch.undo()

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "CONTEXT_EXPIRED"
    # No business effect and no public fact survived the deadline.
    assert house.client.get("/ranger-map/v1/map").json()["footprint_count"] == 0
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM public_log")["c"] == 0
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM action_results")["c"] == 1  # the receipt


# --- Finding 7: durable index association validated before emission ----------


def _open_stream(house, query: str):
    url = (f"/v1/world-stream?mode=public-v1"
           f"&incarnation={house.state.log_incarnation}&{query}")
    events = []

    def read():
        with house.client.stream("GET", url, timeout=10) as response:
            current = None
            for line in response.iter_lines():
                if line.startswith("event: "):
                    current = line[7:]
                elif line.startswith("data: "):
                    events.append((current or "message",
                                   base64.b64decode(line[6:])))

    read()
    return events


def test_f7_kind_corruption_is_index_gap(house):
    yun = Actor("Yun")
    house.client.post("/v1/push", content=wrap_signed(make_post(yun), yun))
    house.store.execute("UPDATE public_log SET kind = 'wrong' WHERE seq = 1")
    events = _open_stream(house, "cursors=&public_after=0")
    names = [name for name, _ in events]
    assert names[0] == "public_boundary"
    gap = wire.PublicStreamGap.FromString(events[1][1])
    assert gap.reason == "publication_index_inconsistent"
    assert "public_checkpoint" not in names


def test_f7_deleted_row_is_index_gap(house):
    yun = Actor("Yun")
    for text in ("one", "two", "three"):
        house.client.post("/v1/push",
                          content=wrap_signed(make_post(yun, text), yun))
    house.store.execute("DELETE FROM public_log WHERE seq = 2")
    events = _open_stream(house, "cursors=&public_after=0")
    gap = wire.PublicStreamGap.FromString(events[1][1])
    assert gap.reason == "publication_index_inconsistent"
    assert gap.lane == "connection"


def test_f7_scope_association_corruption_is_scope_gap(house):
    otto = Actor("Otto")
    ack = ack_of(house, post_session(house, session_request(otto, ENTER, 10)))
    payload = check_in_intent(
        otto, session_id=ack.core.session_id,
        fence=str(ack.core.house_revision),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation)
    response = house.client.post("/v1/push", content=wrap_signed(payload, otto))
    assert response.status_code == 200
    # Drop the signed scope association from the durable index row.
    house.store.execute("UPDATE public_log SET scopes = '[]' WHERE seq = 1")
    events = _open_stream(house, "cursors=rangermap:0")
    gap = wire.PublicStreamGap.FromString(
        [d for n, d in events if n == "public_gap"][0])
    assert gap.reason == "publication_index_inconsistent"
    assert gap.lane == "scope" and gap.scope_id == "rangermap"


def test_f7_unsafe_later_page_withholds_only_from_that_page(house):
    yun = Actor("Yun")
    for text in ("one", "two", "three"):
        house.client.post("/v1/push",
                          content=wrap_signed(make_post(yun, text), yun))
    # seq 3 becomes unsafe wire while pages 1 (seq 1-2, limit=2) is clean.
    house.store.execute(
        "UPDATE public_log SET envelope_bytes = ? WHERE seq = 3",
        (sqlite_blob(b"\x0a\x03abc" + b"\xea\x01\x00"),))
    events = _open_stream(house, "cursors=&public_after=0&limit=2")
    names = [name for name, _ in events]
    frames = [wire.WorldStreamFrame.FromString(d)
              for n, d in events if n == "public_frame"]
    assert [f.seq for f in frames] == [1, 2]  # first page delivered
    gap = wire.PublicStreamGap.FromString(
        [d for n, d in events if n == "public_gap"][0])
    assert gap.reason == "public_log_invalid"
    assert "public_checkpoint" not in names  # never certified across it


def sqlite_blob(payload: bytes):
    import sqlite3

    return sqlite3.Binary(payload)


# --- Finding 8: receipt races preserve the original immutable result ---------


def test_f8_concurrent_rejected_admissions_share_one_receipt(house):
    yun = Actor("Yun")
    ack = ack_of(house, post_session(house, session_request(yun, ENTER, 10)))
    context = dict(
        session_id=ack.core.session_id,
        fence=str(ack.core.house_revision),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation,
    )
    payload = check_in_intent(yun, params={"place": "", "latitude": "1",
                                           "longitude": "1", "status": "x"},
                              **context)
    wrapped = wrap_signed(payload, yun)
    responses = []
    barrier = threading.Barrier(4)

    def worker():
        barrier.wait()
        responses.append(house.client.post("/v1/push", content=wrapped))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert all(response.status_code == 422 for response in responses)
    receipts = {response.json()["receipt_base64"] for response in responses}
    assert len(receipts) == 1  # the original immutable receipt, no 500s
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM action_results")["c"] == 1


def _reordered_wire(payload: bytes) -> bytes:
    """Same message, different top-level field order on the wire: an equal
    canonical core (same CID) with different exact bytes."""
    chunks = []
    pos = 0

    def varint(pos):
        n, shift = 0, 0
        while True:
            byte = payload[pos]
            pos += 1
            n |= (byte & 127) << shift
            if not byte & 128:
                return n, pos
            shift += 7

    while pos < len(payload):
        start = pos
        key, pos = varint(pos)
        wire_type = key & 7
        if wire_type == 0:
            _, pos = varint(pos)
        elif wire_type == 2:
            length, pos = varint(pos)
            pos += length
        elif wire_type == 1:
            pos += 8
        elif wire_type == 5:
            pos += 4
        chunks.append(payload[start:pos])
    return b"".join(reversed(chunks))


def test_f8_same_cid_different_bytes_conflicts_without_overwrite(house):
    yun = Actor("Yun")
    ack = ack_of(house, post_session(house, session_request(yun, ENTER, 10)))
    context = dict(
        session_id=ack.core.session_id,
        fence=str(ack.core.house_revision),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation,
    )
    payload = check_in_intent(yun, params={"place": "", "latitude": "1",
                                           "longitude": "1", "status": "x"},
                              **context)
    variant = _reordered_wire(payload)
    assert variant != payload
    assert wire.envelope_cid(variant) == wire.envelope_cid(payload)

    first = house.client.post("/v1/push", content=wrap_signed(payload, yun))
    assert first.status_code == 422
    original_receipt = first.json()["receipt_base64"]

    second = house.client.post("/v1/push", content=wrap_signed(variant, yun))
    assert second.status_code == 409
    body = second.json()
    assert body["error"]["code"] == "IDEMPOTENCY_CONFLICT"
    # The ORIGINAL receipt stands untouched, still the only stored result.
    assert body["receipt_base64"] == original_receipt
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM action_results")["c"] == 1


# --- Finding 3: live inbox authorization (real server) ------------------------


def test_f3_legacy_lane_for_never_sessioned_actor(tmp_path):
    server = LiveServer(tmp_path)
    try:
        sender, recipient = Actor("Yun"), Actor("Ghost")
        dm = make_dm(sender, recipient, "legacy lane")
        server.post_signed(dm, sender)

        now = int(time.time())
        message = f"inbox-read:{recipient.popclaw_id}:{now}".encode()
        legacy = (f"{recipient.popclaw_id}.{now}."
                  f"{base64.b64encode(recipient.sign(message)).decode()}")
        reader = SseReader(
            server.url(f"/inbox/{recipient.popclaw_id}/stream"),
            headers={"x-popclaw-inbox-token": legacy})
        try:
            events = reader.read_until(lambda ev: len(ev) >= 1)
            assert events and events[0][1] == dm
        finally:
            reader.close()
    finally:
        server.stop()


def test_f3_legacy_refused_after_session_history(tmp_path):
    server = LiveServer(tmp_path)
    try:
        actor = Actor("Yun")
        server.session(actor, operation=ENTER, op_seq=10)
        server.session(actor, operation=LEAVE, op_seq=11)

        now = int(time.time())
        message = f"inbox-read:{actor.popclaw_id}:{now}".encode()
        legacy = (f"{actor.popclaw_id}.{now}."
                  f"{base64.b64encode(actor.sign(message)).decode()}")
        try:
            open_inbox(server.url(f"/inbox/{actor.popclaw_id}/stream"), legacy)
            raise AssertionError("legacy lane must be refused post-session")
        except urllib.error.HTTPError as exc:
            assert exc.code == 401
    finally:
        server.stop()


def test_f3_leave_stops_live_v2_delivery_mid_stream(tmp_path):
    server = LiveServer(tmp_path)
    try:
        sender, luna = Actor("Yun"), Actor("Luna")
        ack = server.session(luna, operation=ENTER, op_seq=10)
        token = ack.core.inbox_read_token

        reader = SseReader(
            server.url(f"/inbox/{luna.popclaw_id}/stream"),
            headers={"x-popclaw-inbox-token": token})
        try:
            dm1 = make_dm(sender, luna, "before leave")
            server.post_signed(dm1, sender)
            events = reader.read_until(lambda ev: len(ev) >= 1)
            assert events and events[0][1] == dm1

            # Logout revokes the session lane; the open stream must stop
            # delivering, with no legacy bypass available afterwards.
            server.session(luna, operation=LEAVE, op_seq=11,
                           target=ack.core.session_id)
            dm2 = make_dm(sender, luna, "after leave")
            server.post_signed(dm2, sender)
            baseline = len(reader.events)
            reader.read_until(lambda ev: len(ev) > baseline, timeout=8)
            # The revoked stream delivered nothing more after the leave.
            assert len(reader.events) == baseline
        finally:
            reader.close()

        # And a fresh legacy attempt for the now-sessioned actor is refused.
        now = int(time.time())
        message = f"inbox-read:{luna.popclaw_id}:{now}".encode()
        legacy = (f"{luna.popclaw_id}.{now}."
                  f"{base64.b64encode(luna.sign(message)).decode()}")
        try:
            open_inbox(server.url(f"/inbox/{luna.popclaw_id}/stream"), legacy)
            raise AssertionError("legacy bypass after leave")
        except urllib.error.HTTPError as exc:
            assert exc.code == 401
    finally:
        server.stop()
