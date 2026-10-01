"""Interop layer 5c: cutover fences (driving the generators directly) and
the manifest proof binding."""

from __future__ import annotations

import asyncio
import base64
import json
import threading

from ranger_map import house as house_mod
from ranger_map import streams as streams_mod
from ranger_map import wire

from tests.interop.wire_helpers import Actor, make_post, wrap_signed


def _drive(generator, max_events=50, between=None):
    """Run an async SSE generator, collecting (event_name, decoded_data)."""
    events = []

    async def run():
        index = 0
        async for chunk in generator:
            current = None
            for line in chunk.split("\n"):
                if line.startswith("event: "):
                    current = line[7:]
                elif line.startswith("data: "):
                    events.append((current or "message",
                                   base64.b64decode(line[6:])))
            if between is not None:
                between(index, events)
            index += 1
            if len(events) >= max_events:
                break

    asyncio.run(run())
    return events


def test_cutover_mid_stream_fences_and_gaps(house):
    yun = Actor("Yun")
    house.client.post("/v1/push",
                      content=wrap_signed(make_post(yun, "before"), yun))
    selection = streams_mod.parse_public_request(
        {"mode": "public-v1", "cursors": "", "public_after": "0",
         "incarnation": house.state.log_incarnation},
        house.state.registered_scopes, house.state.log_incarnation)

    rotated = {"done": False}
    rotate_error = {}
    rotate_done = threading.Event()

    def maybe_rotate(index, events):
        # Rotate once the boundary + replay frame are in hand. The rotation
        # runs on its OWN thread and this callback must NOT block the loop:
        # the consumer task has to stay free to receive its cancellation.
        if not rotated["done"] and len(events) >= 2:
            rotated["done"] = True
            rotated["at"] = len(events)

            def run_rotate():
                try:
                    house.hub.rotate(house.identity, house.state)
                except Exception as exc:  # noqa: BLE001 - surfaced below
                    rotate_error["exc"] = exc
                finally:
                    rotate_done.set()

            threading.Thread(target=run_rotate, daemon=True).start()

    events = []
    try:
        events = _drive(
            streams_mod.stream_public_events(
                house.hub, selection, house.state.registered_scopes),
            max_events=8, between=maybe_rotate)
    except asyncio.CancelledError:
        pass  # stop/join cancels the consuming stream task: the airtight
        # fence — nothing further can be produced for the retired log.

    assert rotated["done"]
    rotate_done.wait(timeout=10)
    assert "exc" not in rotate_error, rotate_error.get("exc")
    names = [name for name, _ in events]
    assert names[0] == "public_boundary"
    boundary = wire.PublicStreamBoundary.FromString(events[0][1])
    assert boundary.log_incarnation == house.state.log_incarnation

    # The rotation fenced the in-flight connection: NO checkpoint and NO
    # data frame were produced after the rotation point (either an explicit
    # incarnation gap arrived and closed the stream, or stop/join cancelled
    # the consuming task outright).
    post = names[rotated["at"]:]
    assert "public_checkpoint" not in post
    if "public_gap" in post:
        gap_index = post.index("public_gap")
        gap = wire.PublicStreamGap.FromString(
            events[rotated["at"] + gap_index][1])
        assert gap.reason == "log_incarnation_changed"
        assert "public_frame" not in post[gap_index:]

    # Retired log id never returns; the new identity serves.
    old_log = house.state.log_incarnation
    new_log = house.store.get_meta("public_log_incarnation")
    assert new_log != old_log
    assert old_log in json.loads(
        house.store.get_meta("retired_log_incarnations"))
    assert house.store.public_log_high_water(new_log) == 0


def test_restore_rotates_both_incarnations_and_fences_sessions(house, tmp_path):
    from ranger_map.keys import load_or_create_identity

    yun = Actor("Yun")
    ack_wire = house.client.post(
        "/v1/house-session",
        content=__import__("tests.interop.wire_helpers", fromlist=["x"])
        .session_request(yun, 1, 10))
    old_session = wire.HouseSessionAck.FromString(ack_wire.content).core.session_id
    old_server = house.state.server_incarnation
    old_log = house.state.log_incarnation

    new_state = house_mod.restore(house.store, house.identity, house.state)
    assert new_state.server_incarnation != old_server
    assert new_state.log_incarnation != old_log
    assert house.store.query_one(
        "SELECT active FROM sessions WHERE session_id = ?",
        (old_session,))["active"] == 0
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM inbox_tokens WHERE revoked = 0")["c"] == 0
    # The manifest was rebuilt against the new log identity.
    manifest = json.loads(new_state.manifest_bytes)
    assert manifest["world_interaction"]["public_stream"][
        "log_incarnation"] == new_state.log_incarnation
    assert new_state.manifest_digest != house.state.manifest_digest


def test_manifest_served_with_valid_proof(house):
    response = house.client.get("/v1/manifest")
    assert response.status_code == 200
    body = response.content
    manifest = json.loads(body)
    assert manifest["slug"] == "rangermap"
    assert manifest["house_session"]["ack_pubkey"] == \
        house.identity.ack_pubkey_hex
    assert manifest["house_session"]["lease_seconds"] == 90
    board = manifest["world_interaction"]
    assert board["version"] == 1
    assert board["public_stream"]["envelope_baseline"] == "public-envelope-01"
    assert board["public_stream"]["mode"] == "public-v1"
    assert board["actions"]["kinds"] == ["rangermap.check_in"]
    assert board["actions"]["attachments"] == []
    assert board["guide"]["path"] == "/v1/guide.md"

    proof = wire.ManifestProof.FromString(
        base64.b64decode(response.headers["X-Popclaw-Manifest-Proof"]))
    assert proof.house.origin == house.state.origin
    assert proof.house.house_key == house.identity.house_key_id
    assert proof.house.incarnation == house.state.server_incarnation
    assert proof.manifest_digest == house.state.manifest_digest
    # The signature covers POPCLAW_WORLD_MANIFEST_PROOF_V1 + core with the
    # authority_signature field absent.
    core = wire.ManifestProof()
    core.house.CopyFrom(proof.house)
    core.manifest_digest = proof.manifest_digest
    core.signed_at = proof.signed_at
    assert wire.verify_ed25519(
        house.identity.public_key_bytes, bytes(proof.authority_signature),
        wire.signing_input(wire.DOMAIN_MANIFEST_PROOF,
                           wire.canonical_core(core)))


def test_guide_bytes_match_manifest_digest(house):
    import hashlib

    guide = house.client.get("/v1/guide.md")
    assert guide.status_code == 200
    manifest = json.loads(house.client.get("/v1/manifest").content)
    digest = manifest["world_interaction"]["guide"]["sha256"]
    assert hashlib.sha256(guide.content).hexdigest() == digest


def test_manifest_is_pinned_across_restart(house, tmp_path):
    from ranger_map.house import load_or_setup
    from ranger_map.store import Store

    before_digest = house.state.manifest_digest
    before_log = house.state.log_incarnation
    house.store.close()

    store = Store.open(tmp_path / "data")
    state2 = load_or_setup(store, house.identity, house.state.origin)
    assert state2.manifest_digest == before_digest
    assert state2.log_incarnation == before_log
    # Reopen for fixture teardown.
    store.close()
    from ranger_map.keys import load_or_create_identity
    house.store = Store.open(tmp_path / "data")
    house.identity = load_or_create_identity(tmp_path / "data")


def test_data_root_refuses_foreign_origin(house):
    import pytest
    from ranger_map.house import HouseStateError, load_or_setup

    with pytest.raises(HouseStateError):
        load_or_setup(house.store, house.identity, "http://127.0.0.1:9999")


def test_live_fence_surfaces_the_gap_without_any_cancellation(house):
    """Deterministic counterpart to the real-socket rotation smoke.

    A real rotation both invalidates the captured identity AND cancels the
    stream task, and which one the generator meets first is a race — so
    that test cannot pin the gap without asserting which side won. Here
    only the identity changes and nothing is cancelled, so the live loop's
    own fence is the only thing that can end the stream: it must surface
    public_gap(log_incarnation_changed) and stop, with nothing after it.
    """
    yun = Actor("Yun")
    house.client.post("/v1/push",
                      content=wrap_signed(make_post(yun, "before"), yun))
    selection = streams_mod.parse_public_request(
        {"mode": "public-v1", "cursors": "", "public_after": "0",
         "incarnation": house.state.log_incarnation},
        house.state.registered_scopes, house.state.log_incarnation)

    invalidated = {}

    def invalidate_after_checkpoint(index, events):
        names = [name for name, _ in events]
        if "public_checkpoint" in names and not invalidated:
            # Exactly what a cutover commits, and nothing else: no task is
            # cancelled, so only the fence can terminate this stream.
            with house.store.write_tx():
                epoch = int(house.store.get_meta("stream_epoch") or "0")
                house.store.set_meta("stream_epoch", str(epoch + 1))
            invalidated["epoch"] = epoch + 1

    # Bounded by wall clock, not by an event count: the generator must END
    # on its own, and a fence that never fires has to FAIL here rather than
    # poll forever.
    events = []

    async def run():
        async for chunk in streams_mod.stream_public_events(
                house.hub, selection, house.state.registered_scopes):
            for line in chunk.split("\n"):
                if line.startswith("event: "):
                    events.append([line[7:], None])
                elif line.startswith("data: ") and events:
                    events[-1][1] = base64.b64decode(line[6:])
            invalidate_after_checkpoint(len(events), events)

    asyncio.run(asyncio.wait_for(run(), timeout=15))

    assert invalidated, "the live phase was never reached"
    names = [name for name, _ in events]
    assert names[-1] == "public_gap", names
    gap = wire.PublicStreamGap.FromString(events[-1][1])
    assert gap.reason == "log_incarnation_changed"
    assert gap.lane == "connection"
    # Terminal: the loop above ended because the generator ended, not
    # because a driver cut it off.
