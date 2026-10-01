"""Interop layer 2: real signed traffic through the live /v1/push ingress.

Tamper/actor/CID/strict-structure cases use isolated generated keys; the
reserved-field vectors exercise whole-event rejection on original wire bytes
(valid inner signature included — stripping is never repair).
"""

from __future__ import annotations

import hashlib

import pytest

from ranger_map import wire

from tests.interop.wire_helpers import (
    Actor,
    build_envelope,
    make_dm,
    make_house_event,
    make_post,
    make_profile,
    signed_envelope_bytes,
    wrap_signed,
    ORIGIN,
)

RESERVED_ENVELOPE_29 = b"\xea\x01\x00"     # field 29, len-delimited, empty
RESERVED_PROFILE_8 = b"\x42\x00"           # field 8, len-delimited, empty


def push(client, payload: bytes):
    return client.post("/v1/push", content=payload)


def test_post_is_accepted_and_published(house):
    actor = Actor("Yun")
    response = push(house.client, wrap_signed(make_post(actor), actor))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["accepted"] is True and body["public"] is True
    row = house.store.query_one(
        "SELECT * FROM public_log WHERE log_incarnation = ?",
        (house.state.log_incarnation,))
    assert row is not None and row["kind"] == "post"
    # The published bytes are the exact signed envelope.
    envelope = wire.EventEnvelope.FromString(bytes(row["envelope_bytes"]))
    assert envelope.event_id == body["event_id"]


def test_idempotent_replay_returns_same_outcome(house):
    actor = Actor("Yun")
    payload = wrap_signed(make_post(actor), actor)
    first = push(house.client, payload).json()
    second = push(house.client, payload).json()
    assert second["duplicate"] is True
    assert second["event_id"] == first["event_id"]
    count = house.store.query_one(
        "SELECT COUNT(*) AS c FROM public_log")["c"]
    assert count == 1


def test_profile_updates_projection_and_public_lane(house):
    actor = Actor("Momo")
    response = push(house.client, wrap_signed(make_profile(actor, "Momo"), actor))
    assert response.status_code == 200
    profile = house.client.get(f"/v1/profile/{actor.popclaw_id}")
    assert profile.status_code == 200
    card = profile.json()["card"]
    assert card["nickname"] == "Momo"
    row = house.store.query_one("SELECT event_id FROM profiles WHERE ranger_id = ?",
                                (actor.popclaw_id,))
    assert row["event_id"] == response.json()["event_id"]
    assert "event_id" not in card


def test_profile_without_card_is_200_with_nothing_in_it(house):
    # Absence is an answer: a stranger is not an error, and a 404 here would
    # be indistinguishable from a moved route at the client that has to read
    # this before publishing its first profile.
    actor = Actor("Nobody")
    response = house.client.get(f"/v1/profile/{actor.popclaw_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["popclaw_id"] == actor.popclaw_id
    assert "nickname" not in body, "nothing declared, nothing reported"
    assert "event_id" not in body
    assert "card" not in body


def test_profile_malformed_id_is_still_400(house):
    # The two genuine failures stay distinguishable from absence, or the
    # answer above would mean nothing.
    response = house.client.get("/v1/profile/not-a-valid-key")
    assert response.status_code == 400


def test_unknown_legal_house_event_relays_opaquely(house):
    actor = Actor("Otto")
    payload = make_house_event(actor, "workshop.tea_ceremony",
                               b'{"opaque":true}')
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 200
    assert response.json()["public"] is True
    row = house.store.query_one(
        "SELECT * FROM public_log WHERE kind = ?", ("workshop.tea_ceremony",))
    assert bytes(row["envelope_bytes"]) == payload


def test_illegal_house_event_kind_rejected(house):
    actor = Actor("Otto")
    payload = make_house_event(actor, "Not A Kind!", b"{}")
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400
    assert "WIRE_" in response.json()["error"]["code"]


def test_encrypted_dm_relayed_privately(house):
    sender, recipient = Actor("Yun"), Actor("Luna")
    payload = make_dm(sender, recipient, "psst")
    response = push(house.client, wrap_signed(payload, sender))
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert "inbox_seq" in body          # private relay, no public lane entry
    # DMs never enter the public log.
    assert house.store.public_log_high_water(house.state.log_incarnation) == 0
    row = house.store.query_one(
        "SELECT * FROM dm_log WHERE recipient_id = ?", (recipient.popclaw_id,))
    assert bytes(row["envelope_bytes"]) == payload


def test_dm_with_bad_targeting_rejected(house):
    sender, recipient = Actor("Yun"), Actor("Luna")

    def set_body(envelope):
        envelope.direct_message.from_popclaw_id = sender.popclaw_id
        envelope.direct_message.to_popclaw_id = recipient.popclaw_id
        envelope.direct_message.body = "no target envelope"

    payload = signed_envelope_bytes(build_envelope(sender, set_body), sender)
    response = push(house.client, wrap_signed(payload, sender))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TARGET"


# --- tamper / strictness ----------------------------------------------------


def test_outer_signature_tamper_rejected(house):
    actor = Actor("Yun")
    wrapper = wire.SignedPayload.FromString(wrap_signed(make_post(actor), actor))
    wrapper.signature = bytes(wrapper.signature)[:-1] + bytes(
        [wrapper.signature[-1] ^ 1])
    response = push(house.client, wrapper.SerializeToString(deterministic=True))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ACTOR_SIGNATURE_INVALID"


def test_inner_signature_tamper_rejected(house):
    actor = Actor("Yun")
    envelope = wire.EventEnvelope.FromString(make_post(actor))
    envelope.signature = bytes(envelope.signature)[:-1] + bytes(
        [envelope.signature[-1] ^ 1])
    response = push(house.client, wrap_signed(
        envelope.SerializeToString(deterministic=True), actor))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ACTOR_SIGNATURE_INVALID"


def test_cid_mismatch_rejected(house):
    actor = Actor("Yun")
    envelope = wire.EventEnvelope.FromString(make_post(actor))
    envelope.event_id = "ff" * 32
    response = push(house.client, wrap_signed(
        envelope.SerializeToString(deterministic=True), actor))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ACTOR_SIGNATURE_INVALID"


def test_actor_signer_mismatch_rejected(house):
    signer, impersonated = Actor("A"), Actor("B")
    payload = make_post(impersonated)  # inner sig by impersonated
    # Outer signature by the wrong key entirely.
    response = push(house.client, wrap_signed(payload, signer))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ACTOR_SIGNATURE_INVALID"


def test_foreign_house_envelope_rejected(house):
    actor = Actor("Yun")

    def set_body(envelope):
        block = envelope.post.blocks.add()
        block.content = "wrong house"

    payload = signed_envelope_bytes(
        build_envelope(actor, set_body, lorehouse="http://elsewhere:1"), actor)
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INTENT_CONTEXT_MISMATCH"


def _with_reserved_envelope_29(actor: Actor) -> bytes:
    """A structurally-reserved envelope whose own signatures are VALID."""
    clean = make_post(actor)
    polluted = clean + RESERVED_ENVELOPE_29
    envelope = wire.EventEnvelope.FromString(polluted)
    envelope.ClearField("event_id")
    envelope.ClearField("signature")
    canonical = wire.canonical_envelope(envelope)
    envelope.event_id = hashlib.sha256(canonical).hexdigest()
    envelope.signature = actor.sign(canonical)
    return envelope.SerializeToString(deterministic=True)


def test_reserved_envelope_field29_rejects_whole_event(house):
    actor = Actor("Yun")
    payload = _with_reserved_envelope_29(actor)
    # The inner signature itself is valid over a core that still carries
    # the reserved bytes; the raw-wire guard still rejects the whole event.
    envelope = wire.EventEnvelope.FromString(payload)
    canonical = wire.canonical_envelope(
        wire.EventEnvelope.FromString(
            payload[:0] + payload))  # recompute with cleared id/sig
    assert wire.verify_ed25519(actor.public_key_bytes,
                               bytes(envelope.signature), canonical)
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "WIRE_RESERVED_OCCURRENCE"
    assert house.store.query_one(
        "SELECT COUNT(*) AS c FROM accepted_envelopes")["c"] == 0


def test_reserved_nested_profile_field8_rejects_whole_event(house):
    actor = Actor("Momo")

    def set_body(envelope):
        profile = wire.ProfileBody()
        profile.nickname = "Momo"
        profile.declared_at = 1
        raw = profile.SerializeToString(deterministic=True) + RESERVED_PROFILE_8
        envelope.profile.ParseFromString(raw)

    payload = signed_envelope_bytes(build_envelope(actor, set_body), actor)
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "WIRE_RESERVED_OCCURRENCE"


def test_duplicate_field_rejected(house):
    actor = Actor("Yun")
    payload = make_post(actor)
    # Append a second actor message (field 2) — duplicate singular field.
    polluted = payload + b"\x12\x00"
    response = push(house.client, wrap_signed(polluted, actor))
    assert response.status_code == 400
    assert "WIRE_" in response.json()["error"]["code"]


def test_truncated_envelope_rejected(house):
    actor = Actor("Yun")
    payload = make_post(actor)[:-3]
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400


def test_unknown_envelope_field_rejected(house):
    actor = Actor("Yun")
    # Field 40 is not allocated on EventEnvelope.
    payload = make_post(actor) + b"\xc0\x02\x00"
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "WIRE_UNSUPPORTED_FIELD"


def test_private_target_post_not_publicly_admitted(house):
    actor = Actor("Yun")
    target = wire.Recipient()
    target.scope = 1  # PRIVATE
    target.target_ids.append(actor.popclaw_id)

    def set_body(envelope):
        block = envelope.post.blocks.add()
        block.content = "secret"

    payload = signed_envelope_bytes(
        build_envelope(actor, set_body, target=target), actor)
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400
    assert response.json()["error"]["code"].startswith("WIRE_")
