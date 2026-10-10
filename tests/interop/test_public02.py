"""First-release public02 wire and immutable actual-log binding regressions."""
import json
from pathlib import Path

import pytest

from ranger_map import wire
from ranger_map.house import HouseStateError, load_or_setup
from ranger_map.streams import _validate_public_row
from tests.interop.wire_helpers import Actor, make_post, make_profile, wrap_signed
from tests.interop.test_relations_wire import _seed_relation_row


def test_fresh_log_declares_public02_and_persists_immutable_binding(house):
    assert wire.ENVELOPE_BASELINE == "public-envelope-02"
    assert house.state.manifest_json["world_interaction"]["public_stream"]["envelope_baseline"] == wire.ENVELOPE_BASELINE
    assert house.store.get_meta("public_log_baselines") == json.dumps(
        {house.state.log_incarnation: wire.ENVELOPE_BASELINE}, sort_keys=True)


@pytest.mark.parametrize("raw", [
    bytes.fromhex("5a024001"),  # InviteRequest.verification_mode=WAIT_NEW_POST
    bytes.fromhex("5a034a0178"),  # InviteRequest.cancel_task_id
    bytes.fromhex("620452023001"),  # QuestDispatch.verify_invite.verification_mode
    bytes.fromhex("6a0450025801"),  # QuestResult READY/revision
])
def test_public02_additive_fields_are_supported(raw):
    wire.guard_envelope(raw)
    wire.guard_public_structure(raw)


@pytest.mark.parametrize("raw", [
    bytes.fromhex("5a0440014001"),
    bytes.fromhex("5a064a01784a0179"),
    bytes.fromhex("6a0450025002"),
    bytes.fromhex("6a0458015801"),
])
def test_duplicate_public02_singular_fields_fail_original_wire(raw):
    with pytest.raises(wire.WireError):
        wire.guard_envelope(raw)


@pytest.mark.parametrize("raw", [bytes.fromhex("5a024002"), bytes.fromhex("6a025004")])
def test_unknown_public02_enum_is_structural_but_not_public(raw):
    wire.guard_envelope(raw)
    with pytest.raises(wire.WireError, match="INVALID_ENUM"):
        wire.guard_public_structure(raw)


def test_manifest_edit_cannot_rebind_actual_log(house):
    manifest = house.state.manifest_json
    manifest["world_interaction"]["public_stream"]["envelope_baseline"] = "public-envelope-01"
    house.store.set_meta("manifest_bytes", json.dumps(manifest))
    with pytest.raises(HouseStateError, match="baseline"):
        load_or_setup(house.store, house.identity, house.state.origin)


def test_unsupported_relation_is_invalid_actual_public_log(house):
    _seed_relation_row(house, Actor("sender"), Actor("recipient"))
    row = house.store.query_one("SELECT * FROM public_log")
    with pytest.raises(wire.WireError, match="NOT_PUBLIC"):
        _validate_public_row(row)
    with pytest.raises(HouseStateError, match="public log"):
        load_or_setup(house.store, house.identity, house.state.origin)


def test_restart_validates_retained_original_and_keeps_log_identity(house):
    raw = make_post(Actor("fresh"))
    house.store.public_log_append(house.state.log_incarnation, wire.envelope_cid(raw), raw, "post", "[]")
    restarted = load_or_setup(house.store, house.identity, house.state.origin)
    assert restarted.log_incarnation == house.state.log_incarnation
    house.store.execute("UPDATE public_log SET kind='profile'")
    with pytest.raises(HouseStateError, match="public log"):
        load_or_setup(house.store, house.identity, house.state.origin)


def test_runtime_baseline_mismatch_refuses_selected_mode(house):
    house.store.set_meta("public_log_baselines", json.dumps({house.state.log_incarnation: "public-envelope-01"}))
    response = house.client.get(
        f"/v1/world-stream?mode=public-v1&incarnation={house.state.log_incarnation}&cursors=&public_after=99")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PUBLIC_STREAM_UNAVAILABLE"


@pytest.mark.parametrize("name", ["invite_wait_request_house_helper", "invite_wait_cancel_signed",
    "invite_wait_dispatch_signed", "invite_wait_ready_progress_signed"])
def test_signed_public02_vectors_ingress_preserves_private_evidence(house, name):
    vectors = json.loads((Path(__file__).resolve().parents[2] / "vendor/popclaw-contracts/packages/contracts/fixtures/public-baseline.json").read_text())
    row = next(row for row in vectors["signed"] if row["name"] == name)
    raw = bytes.fromhex(row["wire_hex"])
    wire.guard_public_structure(raw)
    response = house.client.post("/v1/push", content=bytes.fromhex(row["signed_payload_hex"]))
    assert response.status_code == 200, response.text
    assert response.json()["retained"] == "private"  # no new game admission rules
    stored = house.store.query_one("SELECT * FROM accepted_envelopes WHERE event_id=?", (row["cid"],))
    assert bytes(stored["envelope_bytes"]) == raw
    assert wire.envelope_cid(raw) == row["cid"]
    assert house.store.public_log_high_water(house.state.log_incarnation) == 0


def test_public_row_signature_is_verified_before_delivery_and_readiness(house):
    raw = make_post(Actor("signed"))
    envelope = wire.EventEnvelope.FromString(raw)
    envelope.signature = b"\0" * 64
    tampered = envelope.SerializeToString(deterministic=True)
    house.store.public_log_append(house.state.log_incarnation, wire.envelope_cid(raw), tampered, "post", "[]")
    row = house.store.query_one("SELECT * FROM public_log")
    with pytest.raises(wire.WireError, match="SIGNATURE"):
        _validate_public_row(row)
    with pytest.raises(HouseStateError, match="public log"):
        load_or_setup(house.store, house.identity, house.state.origin)


@pytest.mark.parametrize("body", ["profile", "post"])
def test_profile_public_projection_rechecks_original_reserved_structure(house, body):
    actor = Actor("projection")
    raw = (make_profile(actor, "Visible only with a valid original") if body == "profile" else make_post(actor))
    assert house.client.post("/v1/push", content=wrap_signed(raw, actor)).status_code == 200
    # A storage bypass must not turn a previously decoded card into safe output.
    house.store.execute("UPDATE accepted_envelopes SET envelope_bytes=? WHERE event_id=?",
                        (raw + bytes.fromhex("ea0100"), wire.envelope_cid(raw)))
    response = house.client.get(f"/v1/profile/{actor.popclaw_id}")
    assert response.status_code == 503
    assert "card" not in response.json()


def test_resolve_public_projection_rechecks_profile_original(house):
    actor = Actor("directory")
    raw = make_profile(actor, "ReviewReservedProfile")
    assert house.client.post("/v1/push", content=wrap_signed(raw, actor)).status_code == 200
    before = house.client.get("/v1/resolve?name=ReviewReservedProfile")
    assert before.status_code == 200 and before.json()["candidates"][0]["popclaw_id"] == actor.popclaw_id
    house.store.execute("UPDATE accepted_envelopes SET envelope_bytes=? WHERE event_id=?",
                        (raw + bytes.fromhex("ea0100"), wire.envelope_cid(raw)))
    response = house.client.get("/v1/resolve?name=ReviewReservedProfile")
    assert response.status_code == 503
    assert "candidates" not in response.json()


def test_public_row_rejects_embedded_event_id_not_equal_to_canonical_cid(house):
    raw = make_post(Actor("embedded CID"))
    envelope = wire.EventEnvelope.FromString(raw)
    envelope.event_id = "0" * 64
    tampered = envelope.SerializeToString(deterministic=True)
    assert wire.envelope_cid(tampered) == wire.envelope_cid(raw)
    house.store.public_log_append(house.state.log_incarnation, wire.envelope_cid(raw), tampered, "post", "[]")
    with pytest.raises(wire.WireError, match="CID"):
        _validate_public_row(house.store.query_one("SELECT * FROM public_log"))
    with pytest.raises(HouseStateError, match="public log"):
        load_or_setup(house.store, house.identity, house.state.origin)
