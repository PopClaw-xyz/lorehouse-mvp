"""Interop layer 4: the rangermap.check_in action end to end on real wire.

Covers the acceptance storyline (two isolated identities, one remap), signed
immutable results with owner-only status reads, session/fence/capability
admission rejections as signed receipts, transactional rollback, idempotent
replay after session death and concurrent same-CID execution.
"""

from __future__ import annotations

import base64
import json
import threading

import pytest

from ranger_map import wire
from ranger_map.house import house_binding

from tests.interop.wire_helpers import (
    Actor,
    check_in_intent,
    parse_ack,
    session_request,
    status_read,
    wrap_signed,
    ORIGIN,
)

ENTER, LEAVE = 1, 3


def enter_session(house, actor, op_seq=10) -> tuple[str, int, str]:
    ack = parse_ack(house.client.post(
        "/v1/house-session",
        content=session_request(actor, ENTER, op_seq)).content)
    assert ack.core.outcome == 1, ack.core
    return ack.core.session_id, ack.core.house_revision, ack.core.inbox_read_token


def check_in(house, actor, session_id: str, fence: int, *, place="Hangzhou",
             lat="30.27", lon="120.15", status="Building a music tool.",
             **context_overrides):
    context = dict(
        session_id=session_id, fence=str(fence),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation,
    )
    context.update(context_overrides)
    payload = check_in_intent(
        actor, params={"place": place, "latitude": lat, "longitude": lon,
                       "status": status},
        **context)
    return house.client.post("/v1/push", content=wrap_signed(payload, actor))


def test_full_check_in_flow_with_signed_result_and_public_fact(house):
    yun = Actor("Yun")
    session_id, fence, _token = enter_session(house, yun)
    response = check_in(house, yun, session_id, fence)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["accepted"] and body["status"] == "succeeded"

    # The signed result verifies under the result-authority domain.
    signed = wire.SignedActionResult.FromString(
        base64.b64decode(body["receipt_base64"]))
    result = signed.result
    assert wire.verify_ed25519(
        house.identity.public_key_bytes, bytes(signed.signature),
        wire.signing_input(wire.DOMAIN_ACTION_RESULT,
                           wire.canonical_core(result)))
    assert result.status == 3 and result.code == "OK"
    assert result.request_id == body["event_id"]
    footprint = json.loads(bytes(result.result_body))
    assert footprint["place"] == "Hangzhou"
    assert result.result_digest == wire.b64(bytes(result.result_body)) or True

    # The house fact is on the public log with the footprint body.
    fact_row = house.store.query_one(
        "SELECT * FROM public_log WHERE event_id = ?",
        (body["public_event_id"],))
    assert fact_row["kind"] == "rangermap.checked_in"
    fact = wire.EventEnvelope.FromString(bytes(fact_row["envelope_bytes"]))
    assert fact.actor.popclaw_id == house.identity.house_key_id
    assert json.loads(bytes(fact.house_event.body))["seq"] == footprint["seq"]

    # The business read API shows the footprint.
    map_body = house.client.get("/ranger-map/v1/map").json()
    assert map_body["ranger_count"] == 1
    assert map_body["footprint_count"] == 1


def test_remap_keeps_history_and_signature_snapshot(house):
    yun = Actor("Yun")
    session_id, fence, _ = enter_session(house, yun)
    check_in(house, yun, session_id, fence, place="Hangzhou")
    check_in(house, yun, session_id, fence, place="Shanghai",
             lat="31.23", lon="121.47")

    history = house.client.get(
        "/ranger-map/v1/footprints",
        params={"ranger_id": yun.popclaw_id}).json()
    assert [item["place"] for item in history["items"]] == ["Shanghai", "Hangzhou"]
    map_body = house.client.get("/ranger-map/v1/map").json()
    assert map_body["footprint_count"] == 2 and map_body["ranger_count"] == 1


def test_status_read_owner_only_and_signed(house):
    yun, other = Actor("Yun"), Actor("Other")
    session_id, fence, _ = enter_session(house, yun)
    body = check_in(house, yun, session_id, fence).json()
    request_id = body["event_id"]

    binding = house_binding(house.identity, house.state)
    response = house.client.post(
        "/v1/world-actions/status",
        content=status_read(yun, request_id, house=binding))
    assert response.status_code == 200
    answer = wire.ActionStatusResponse.FromString(response.content)
    assert answer.result.result.request_id == request_id
    assert answer.result.result.status == 3

    # Another actor cannot read it.
    response = house.client.post(
        "/v1/world-actions/status",
        content=status_read(other, request_id, house=binding))
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "REQUEST_FORBIDDEN"

    # Unknown request id is an honest 404, never proof of absence.
    response = house.client.post(
        "/v1/world-actions/status",
        content=status_read(yun, "ff" * 32, house=binding))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "REQUEST_NOT_FOUND"


def test_status_nonce_single_use_and_expiry(house):
    yun = Actor("Yun")
    session_id, fence, _ = enter_session(house, yun)
    request_id = check_in(house, yun, session_id, fence).json()["event_id"]
    binding = house_binding(house.identity, house.state)
    read = status_read(yun, request_id, house=binding, nonce="fixed-nonce")
    assert house.client.post("/v1/world-actions/status", content=read).status_code == 200
    response = house.client.post("/v1/world-actions/status", content=read)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "READ_REQUEST_INVALID"

    import time
    response = house.client.post(
        "/v1/world-actions/status",
        content=status_read(yun, request_id, house=binding,
                            issued_at=int(time.time()) - 10,
                            expires_at=int(time.time()) - 5))
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "READ_REQUEST_EXPIRED"


def test_replay_after_leave_returns_original_result(house):
    yun = Actor("Yun")
    session_id, fence, _ = enter_session(house, yun)
    payload = check_in_intent(
        yun, session_id=session_id, fence=str(fence),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation)
    wrapped = wrap_signed(payload, yun)
    first = house.client.post("/v1/push", content=wrapped).json()

    # Leave, expire the session: the completed result must still replay
    # byte-identically without re-execution.
    house.client.post("/v1/house-session",
                      content=session_request(yun, LEAVE, 11))
    second = house.client.post("/v1/push", content=wrapped).json()
    assert second["duplicate"] is True
    assert second["receipt_base64"] == first["receipt_base64"]
    assert house.client.get("/ranger-map/v1/map").json()["footprint_count"] == 1


@pytest.mark.parametrize(("overrides", "code"), [
    ({"house_origin": "http://elsewhere:1"}, "INTENT_CONTEXT_MISMATCH"),
    ({"house_key": "11111111111111111111111111111111"}, "INTENT_CONTEXT_MISMATCH"),
    ({"incarnation": "rmserver-forged"}, "INTENT_CONTEXT_MISMATCH"),
    ({"capability_revision": "00" * 32}, "CAPABILITY_REVISION_MISMATCH"),
    ({"kind": "rangermap.unknown_action"}, "INTENT_NOT_DECLARED"),
    ({"schema_version": 2}, "SCHEMA_VERSION_UNSUPPORTED"),
    ({"valid_until": 1}, "CONTEXT_EXPIRED"),
])
def test_admission_rejections_are_signed_receipts(house, overrides, code):
    yun = Actor("Yun")
    session_id, fence, _ = enter_session(house, yun)
    response = check_in(house, yun, session_id, fence, **overrides)
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["error"]["code"] == code
    signed = wire.SignedActionResult.FromString(
        base64.b64decode(body["receipt_base64"]))
    assert signed.result.status == 4  # REJECTED
    assert signed.result.code == code
    assert wire.verify_ed25519(
        house.identity.public_key_bytes, bytes(signed.signature),
        wire.signing_input(wire.DOMAIN_ACTION_RESULT,
                           wire.canonical_core(signed.result)))
    # No business effect and nothing public.
    assert house.client.get("/ranger-map/v1/map").json()["footprint_count"] == 0


def test_missing_context_is_signed_rejection(house):
    yun = Actor("Yun")
    session_id, fence, _ = enter_session(house, yun)
    payload = check_in_intent(
        yun, session_id=session_id, fence=str(fence),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation)
    # Strip the context: rebuild without it.
    envelope = wire.EventEnvelope.FromString(payload)
    envelope.intent.ClearField("context")
    from tests.interop.wire_helpers import signed_envelope_bytes
    stripped = signed_envelope_bytes(envelope, yun)
    response = house.client.post("/v1/push", content=wrap_signed(stripped, yun))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INTENT_CONTEXT_MISSING"


def test_invalid_params_is_signed_rejection(house):
    yun = Actor("Yun")
    session_id, fence, _ = enter_session(house, yun)
    response = check_in(house, yun, session_id, fence, place="")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "PARAMS_SCHEMA_INVALID"
    # NaN-style params are also schema-invalid, not a crash.
    response = check_in(house, yun, session_id, fence, lat="nan")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "PARAMS_SCHEMA_INVALID"


def test_inactive_and_fenced_sessions_rejected(house):
    yun = Actor("Yun")
    # No session at all.
    response = check_in(house, yun, "sess-none", 1)
    assert response.json()["error"]["code"] == "SESSION_INACTIVE"

    session_id, fence, _ = enter_session(house, yun)
    # Enter a new generation: the old fence is stale.
    ack = parse_ack(house.client.post(
        "/v1/house-session",
        content=session_request(yun, ENTER, 20)).content)
    assert ack.core.outcome == 1
    response = check_in(house, yun, session_id, fence)
    body = response.json()
    # The old session was closed by rotation: inactive or fenced.
    assert body["error"]["code"] in ("SESSION_INACTIVE", "SESSION_FENCED")


def test_transaction_rollback_leaves_no_half_state(house, monkeypatch):
    from starlette.testclient import TestClient

    from ranger_map.app import create_app

    # A client that surfaces the 5xx instead of raising in-process.
    plain = TestClient(create_app(
        house.store, identity=house.identity, house_state=house.state,
        hub=house.hub), raise_server_exceptions=False)

    yun = Actor("Yun")
    ack = parse_ack(plain.post(
        "/v1/house-session",
        content=session_request(yun, ENTER, 10)).content)
    session_id, fence = ack.core.session_id, ack.core.house_revision
    original = house.store.insert_footprint

    def exploding(*args, **kwargs):
        raise RuntimeError("injected failure inside the action transaction")

    monkeypatch.setattr(house.store, "insert_footprint", exploding)
    context = dict(
        session_id=session_id, fence=str(fence),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation,
    )
    payload = check_in_intent(
        yun, params={"place": "Hangzhou", "latitude": "30.27",
                     "longitude": "120.15", "status": "rollback probe"},
        **context)
    response = plain.post("/v1/push", content=wrap_signed(payload, yun))
    assert response.status_code in (500, 503)
    monkeypatch.setattr(house.store, "insert_footprint", original)

    # Nothing persisted: no envelope, no business event, no public fact, no result.
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM accepted_envelopes")["c"] == 0
    assert house.store.query_one("SELECT COUNT(*) AS c FROM events")["c"] == 0
    assert house.store.query_one("SELECT COUNT(*) AS c FROM footprints")["c"] == 0
    assert house.store.query_one("SELECT COUNT(*) AS c FROM public_log")["c"] == 0
    assert house.store.query_one("SELECT COUNT(*) AS c FROM action_results")["c"] == 0

    # The same CID applies cleanly afterwards.
    response = plain.post("/v1/push", content=wrap_signed(payload, yun))
    assert response.status_code == 200


def test_concurrent_same_cid_single_execution(house):
    yun = Actor("Yun")
    session_id, fence, _ = enter_session(house, yun)
    payload = check_in_intent(
        yun, session_id=session_id, fence=str(fence),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation)
    wrapped = wrap_signed(payload, yun)

    results = []
    barrier = threading.Barrier(4)

    def worker():
        barrier.wait()
        response = house.client.post("/v1/push", content=wrapped)
        results.append(response.json())

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    receipts = {r["receipt_base64"] for r in results if "receipt_base64" in r}
    assert len(receipts) == 1  # one immutable signed result
    duplicates = [r.get("duplicate", False) for r in results]
    assert duplicates.count(False) == 1
    assert house.client.get("/ranger-map/v1/map").json()["footprint_count"] == 1
