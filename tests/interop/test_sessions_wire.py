"""Interop layer 3: the G0 session lifecycle over real signed requests."""

from __future__ import annotations

import time

import pytest

from ranger_map import sessions as sessions_mod
from ranger_map import wire

from tests.interop.wire_helpers import Actor, parse_ack, session_request

ENTER, RENEW, LEAVE, STATUS = 1, 2, 3, 4


def post_session(house, payload: bytes):
    return house.client.post("/v1/house-session", content=payload)


def verified_ack(house, response) -> wire.HouseSessionAck:
    """Parse the ACK and verify its signature + authority binding."""
    ack = parse_ack(response.content)
    assert wire.verify_ed25519(
        house.identity.public_key_bytes, bytes(ack.signature),
        wire.signing_input(wire.DOMAIN_SESSION_ACK,
                           wire.canonical_core(ack.core)))
    assert ack.signer_pubkey == house.identity.public_key_bytes
    return ack


def test_enter_renew_leave_status_full_cycle(house):
    actor = Actor("Yun")

    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 10)))
    assert ack.core.outcome == 1  # ENTERED
    session_id = ack.core.session_id
    assert session_id and ack.core.session_active
    assert ack.core.house_revision >= 1
    fence = ack.core.house_revision
    assert ack.core.inbox_read_token.startswith("itk-")

    ack = verified_ack(house, post_session(house, session_request(
        actor, RENEW, 10, target_session=session_id)))
    assert ack.core.outcome == 3  # RENEWED
    assert ack.core.lease_expires_at > int(time.time())

    ack = verified_ack(house, post_session(house, session_request(
        actor, STATUS, 10, target_session=session_id)))
    assert ack.core.outcome == 8  # REPORTED
    assert ack.core.status.session_id == session_id

    ack = verified_ack(house, post_session(house, session_request(
        actor, LEAVE, 11, target_session=session_id)))
    assert ack.core.outcome == 4  # CLOSED
    # The session id is never reusable.
    row = house.store.query_one(
        "SELECT active FROM sessions WHERE session_id = ?", (session_id,))
    assert row["active"] == 0


def test_enter_idempotency_same_request_replays_ack(house):
    actor = Actor("Yun")
    request = session_request(actor, ENTER, 10)
    first = post_session(house, request)
    second = post_session(house, request)
    assert first.content == second.content  # byte-identical stored ACK


def test_enter_request_id_reuse_with_different_core_conflicts(house):
    actor = Actor("Yun")
    request_id = "req-fixed-1"
    first = post_session(house, session_request(actor, ENTER, 10,
                                                request_id=request_id))
    ack = parse_ack(first.content)
    assert ack.core.outcome == 1
    second = post_session(house, session_request(actor, ENTER, 11,
                                                 request_id=request_id))
    ack = verified_ack(house, second)
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.IDEMPOTENCY_CONFLICT


def test_enter_op_seq_cas(house):
    actor = Actor("Yun")
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 5)))
    assert ack.core.outcome == 1
    first_session = ack.core.session_id

    # Equal op_seq reuses the generation.
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 5)))
    assert ack.core.outcome == 2  # ALREADY_ENTERED
    assert ack.core.session_id == first_session

    # Higher op_seq creates a new generation with a new fence.
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 6)))
    assert ack.core.outcome == 1
    assert ack.core.session_id != first_session
    assert ack.core.house_revision >= 2

    # Lower op_seq is stale.
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 4)))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.STALE_OPERATION


def test_second_installation_is_executor_busy(house):
    actor = Actor("Yun")  # one identity, two installations
    ack = verified_ack(house, post_session(house, session_request(
        actor, ENTER, 10, installation="install-A")))
    assert ack.core.outcome == 1
    ack = verified_ack(house, post_session(house, session_request(
        actor, ENTER, 10, installation="install-B")))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.EXECUTOR_BUSY


def test_leave_watermark_forbids_older_enters(house):
    actor = Actor("Yun")
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 10)))
    assert ack.core.outcome == 1
    ack = verified_ack(house, post_session(house, session_request(actor, LEAVE, 15)))
    assert ack.core.outcome == 4
    # An enter covered by the leave watermark is stale, not busy.
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 12)))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.STALE_OPERATION
    # A newer enter works again.
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 16)))
    assert ack.core.outcome == 1


def test_late_leave_supersedes_without_closing_newer_generation(house):
    actor = Actor("Yun")
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 10)))
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 20)))
    assert ack.core.outcome == 1
    newer_session = ack.core.session_id
    # A late LEAVE at the old op_seq must not close the new generation.
    ack = verified_ack(house, post_session(house, session_request(actor, LEAVE, 12)))
    assert ack.core.outcome == 6  # SUPERSEDED
    row = house.store.query_one(
        "SELECT active FROM sessions WHERE session_id = ?", (newer_session,))
    assert row["active"] == 1


def test_leave_twice_is_already_closed(house):
    actor = Actor("Yun")
    post_session(house, session_request(actor, ENTER, 10))
    ack = verified_ack(house, post_session(house, session_request(actor, LEAVE, 12)))
    assert ack.core.outcome == 4
    ack = verified_ack(house, post_session(house, session_request(actor, LEAVE, 13)))
    # watermark 13 > 12 closes nothing new; the tombstone stands.
    assert ack.core.outcome == 4


def test_leave_before_any_enter_records_tombstone(house):
    actor = Actor("Ghost")
    ack = verified_ack(house, post_session(house, session_request(actor, LEAVE, 9)))
    assert ack.core.outcome == 4  # CLOSED tombstone for an unobserved enter
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 8)))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.STALE_OPERATION


def test_renew_unknown_session_is_fenced(house):
    actor = Actor("Yun")
    ack = verified_ack(house, post_session(house, session_request(
        actor, RENEW, 10, target_session="sess-does-not-exist")))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.SESSION_FENCED


def test_expired_lease_renew_requires_new_enter(house):
    actor = Actor("Yun")
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 10)))
    session_id = ack.core.session_id
    house.store.execute(
        "UPDATE sessions SET lease_expires_at = ? WHERE session_id = ?",
        (int(time.time()) - 5, session_id))
    ack = verified_ack(house, post_session(house, session_request(
        actor, RENEW, 10, target_session=session_id)))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.LEASE_EXPIRED


def test_audience_mismatch_rejected(house):
    actor = Actor("Yun")
    ack = verified_ack(house, post_session(house, session_request(
        actor, ENTER, 10, origin="http://other-house:9000")))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.AUDIENCE_MISMATCH


def test_bad_signature_rejected(house):
    actor = Actor("Yun")
    request = wire.HouseSessionRequest.FromString(session_request(actor, ENTER, 10))
    request.signature = bytes(request.signature)[:-1] + bytes(
        [request.signature[-1] ^ 1])
    ack = verified_ack(house, post_session(
        house, request.SerializeToString(deterministic=True)))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.AUTH_INVALID


def test_expired_window_rejected(house):
    actor = Actor("Yun")
    now = int(time.time())
    ack = verified_ack(house, post_session(house, session_request(
        actor, ENTER, 10, issued_at=now - 3600, expires_at=now - 3000)))
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.AUTH_INVALID


def test_signer_must_match_popclaw_id(house):
    real, fake = Actor("Yun"), Actor("Imposter")
    request = wire.HouseSessionRequest.FromString(session_request(real, ENTER, 10))
    request.signer_pubkey = fake.public_key_bytes
    # The signature is by `real` over the original core; the key now claims
    # someone else, so verification fails before any state change.
    response = post_session(
        house, request.SerializeToString(deterministic=True))
    ack = parse_ack(response.content)
    assert ack.core.outcome == 7 and ack.core.error_code == sessions_mod.AUTH_INVALID


def test_malformed_binary_request_is_plain_400(house):
    response = post_session(house, b"\xff\xff\xff")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_input"


def test_inbox_token_dies_with_leave(house):
    actor = Actor("Yun")
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 10)))
    token = ack.core.inbox_read_token
    assert sessions_mod.verify_inbox_token(
        house.store, house.identity, house.state.origin, token, actor.popclaw_id)
    post_session(house, session_request(actor, LEAVE, 11))
    assert not sessions_mod.verify_inbox_token(
        house.store, house.identity, house.state.origin, token, actor.popclaw_id)


def test_inbox_token_is_audience_bound(house):
    actor = Actor("Yun")
    ack = verified_ack(house, post_session(house, session_request(actor, ENTER, 10)))
    token = ack.core.inbox_read_token
    # The signed binding covers the canonical audience (origin): presenting
    # the same token material under another origin must not verify.
    assert not sessions_mod.verify_inbox_token(
        house.store, house.identity, "http://127.0.0.1:9999", token,
        actor.popclaw_id)
