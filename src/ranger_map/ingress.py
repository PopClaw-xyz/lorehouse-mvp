"""Signed ingress: the ``POST /v1/push`` pipeline.

Order is fixed by IMPLEMENTERS.md: preserve the received envelope bytes, run
the bounded structural guard at every ingress, verify the SignedPayload
outer signature over the exact payload bytes BEFORE decoding anything else,
then canonicalise, check the CID, verify the inner signature and the
actor↔signer binding, and only then dispatch by body with per-body policy.
Nothing here repairs, re-encodes or strips unsupported wire input; a
structural rejection keeps the original bytes out of every projection.

Relation originals use their own verified admission engine and are delivered
only on the two participants' personal streams, never the public lane.
"""

from __future__ import annotations

import json

from . import actions as actions_mod
from . import relations
from . import wire
from .evidence import PushOutcome, store_envelope
from .keys import HouseIdentity

WRAPPER_MAX_BYTES = wire.L_ENVELOPE_MAX_BYTES + 128

# Tags we retain privately (validated structure, no public admission rule
# implemented for their typed semantics in this reference server).
RETAIN_PRIVATE_TAGS = {11, 12, 13, 14, 15, 16, 17, 18, 30, 31, 32}


def _reject(status: int, code: str, message: str) -> PushOutcome:
    return PushOutcome(http_status=status, code=code, message=message)


def handle_push(store, identity: HouseIdentity, state, body: bytes) -> PushOutcome:
    if len(body) > WRAPPER_MAX_BYTES:
        return _reject(413, "BODY_TOO_LARGE", "push body exceeds the envelope limit")

    try:
        wrapper = wire.SignedPayload.FromString(body)
    except Exception:
        return _reject(400, "MALFORMED_WRAPPER", "body is not a SignedPayload")

    payload = bytes(wrapper.payload)
    if not payload:
        return _reject(400, "MALFORMED_WRAPPER", "empty payload")
    if len(payload) > wire.L_ENVELOPE_MAX_BYTES:
        return _reject(413, "BODY_TOO_LARGE", "envelope exceeds the size limit")
    if len(wrapper.signer_pubkey) != 32:
        return _reject(400, "ACTOR_SIGNATURE_INVALID", "signer key must be 32 bytes")

    # Outer signature over the exact payload bytes, before any decode.
    if not wire.verify_ed25519(bytes(wrapper.signer_pubkey),
                               bytes(wrapper.signature), payload):
        return _reject(400, "ACTOR_SIGNATURE_INVALID", "outer signature invalid")

    try:
        tag = wire.guard_envelope(payload)
    except wire.WireError as exc:
        return _reject(400, f"WIRE_{exc}", "envelope failed the structural guard")

    envelope = wire.EventEnvelope.FromString(payload)
    canonical = wire.envelope_canonical_bytes(payload)
    cid = wire.envelope_cid(payload)
    if envelope.event_id != cid:
        return _reject(400, "ACTOR_SIGNATURE_INVALID",
                       "event_id does not match the canonical CID")
    if not wire.verify_ed25519(bytes(wrapper.signer_pubkey),
                               bytes(envelope.signature), canonical):
        return _reject(400, "ACTOR_SIGNATURE_INVALID", "inner signature invalid")
    try:
        actor_key = wire.key_bytes_from_popclaw_id(envelope.actor.popclaw_id)
    except ValueError:
        return _reject(400, "ACTOR_SIGNATURE_INVALID",
                       "actor.popclaw_id must decode to a 32-byte key")
    if actor_key != bytes(wrapper.signer_pubkey):
        return _reject(400, "ACTOR_SIGNATURE_INVALID",
                       "actor does not match the signer key")
    if tag not in wire.RELATION_TAGS and envelope.lorehouse not in ("", state.origin):
        return _reject(400, "INTENT_CONTEXT_MISMATCH",
                       "envelope targets another house")

    # A separate transactional replay lookup preserves the stored relation
    # verdict and refuses a corrupt/foreign index instead of returning a
    # historical public receipt for a personal original.
    if tag in wire.RELATION_TAGS:
        return relations.accept(store, identity, state, payload, envelope, cid, tag)

    # Idempotent replay of an already-accepted event: same bytes, same
    # outcome, never a second business effect.
    existing = store.query_one(
        "SELECT event_id, public_eligible FROM accepted_envelopes WHERE event_id = ?",
        (cid,),
    )
    if existing is not None:
        stored = actions_mod.stored_outcome_for(store, cid)
        if stored is not None:
            replay = actions_mod.replay_outcome(stored, cid)
            replay.public = bool(existing["public_eligible"])
            return replay
        return PushOutcome(http_status=200, code="OK", event_id=cid,
                           duplicate=True,
                           public=bool(existing["public_eligible"]))

    if tag == 35:
        return actions_mod.handle_intent_transactional(
            store, identity, state, payload, envelope, cid)

    return _dispatch_typed(store, identity, state, payload, envelope, cid, tag)


def _relation_order_present(envelope, tag: int) -> bool:
    body = envelope.follow_declared if tag == 20 else envelope.follow_revoked
    return body.HasField("order")


def _routing_kind(tag: int, envelope) -> str:
    if tag == 34:
        return envelope.house_event.kind
    return wire.BODY_TAGS.get(tag, "unknown")


def _dispatch_typed(store, identity: HouseIdentity, state, payload: bytes,
                    envelope, cid: str, tag: int) -> PushOutcome:
    kind = _routing_kind(tag, envelope)
    now_ms = store.clock_ms()

    if tag == 26:
        return _accept_direct_message(store, payload, envelope, cid, now_ms)

    # Public lane: apply the privacy predicate before any publication.
    if tag in wire.PUBLIC_ELIGIBLE_TAGS and tag not in RETAIN_PRIVATE_TAGS:
        try:
            wire.guard_public_structure(payload)
        except wire.WireError as exc:
            return _reject(400, f"WIRE_{exc}",
                           "envelope is not admissible as a public event")
        scopes = (
            list(envelope.house_event.public_scopes) if tag == 34 else []
        )
        with store.write_tx():
            store_envelope(store, cid, payload, envelope.actor.popclaw_id, tag,
                            kind, 1, scopes, now_ms)
            seq = store.public_log_append(state.log_incarnation, cid, payload,
                                          kind, json.dumps(scopes))
            if tag == 28:
                _upsert_profile(store, envelope, cid, now_ms)
        return PushOutcome(http_status=200, code="OK", event_id=cid, public=True,
                           extra={"public_seq": str(seq)})

    # Retained privately: legal typed traffic this reference server has no
    # admission rules for (quests/invites/watch/marks/transients).
    with store.write_tx():
        store_envelope(store, cid, payload, envelope.actor.popclaw_id, tag,
                        kind, 0, [], now_ms)
    return PushOutcome(http_status=200, code="OK", event_id=cid, public=False,
                       extra={"retained": "private"})


def _upsert_profile(store, envelope, cid: str, now_ms: int) -> None:
    profile = envelope.profile
    if not profile.nickname:
        return
    store.execute(
        "INSERT INTO profiles (ranger_id, display_name, card_json, updated_at_ms,"
        " event_id, one_line_intro, declared_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
        " ON CONFLICT(ranger_id) DO UPDATE SET"
        "   display_name = excluded.display_name,"
        "   card_json = excluded.card_json,"
        "   updated_at_ms = excluded.updated_at_ms,"
        "   event_id = excluded.event_id,"
        "   one_line_intro = excluded.one_line_intro,"
        "   declared_at = excluded.declared_at"
        " WHERE excluded.declared_at >= profiles.declared_at",
        (
            envelope.actor.popclaw_id,
            profile.nickname,
            json.dumps(
                {
                    "nickname": profile.nickname,
                    "one_line_intro": profile.one_line_intro,
                    "taste_tags": list(profile.taste_tags),
                    "role_persona": profile.role_persona,
                    "location_hint": profile.location_hint,
                    "avatar_uri": profile.avatar_uri,
                    "declared_at": profile.declared_at,
                }
            ),
            now_ms,
            cid,
            profile.one_line_intro,
            profile.declared_at,
        ),
    )


def _accept_direct_message(store, payload: bytes, envelope, cid: str,
                           now_ms: int) -> PushOutcome:
    dm = envelope.direct_message
    recipient = dm.to_popclaw_id
    try:
        wire.key_bytes_from_popclaw_id(recipient)
    except ValueError:
        return _reject(400, "INVALID_TARGET", "DM recipient must be a valid identity")
    if dm.from_popclaw_id != envelope.actor.popclaw_id:
        return _reject(400, "INVALID_TARGET",
                       "DM from_popclaw_id must match the signing actor")
    if not envelope.HasField("target") or envelope.target.scope != 1:
        return _reject(400, "INVALID_TARGET",
                       "DM envelopes must use PRIVATE recipient targeting")
    if recipient not in list(envelope.target.target_ids):
        return _reject(400, "INVALID_TARGET",
                       "DM recipient missing from the envelope target ids")
    if bool(dm.ciphertext) != bool(dm.nonce):
        return _reject(400, "INVALID_DM",
                       "ciphertext and nonce must be set together")
    if dm.ciphertext and len(dm.nonce) != 24:
        return _reject(400, "INVALID_DM", "nonce must be 24 bytes")
    if bool(dm.media_ciphertext) != bool(dm.media_nonce):
        return _reject(400, "INVALID_DM",
                       "media ciphertext and nonce must be set together")
    if not dm.body and not dm.ciphertext:
        return _reject(400, "INVALID_DM", "DM needs a body or ciphertext")

    with store.write_tx():
        store_envelope(store, cid, payload, envelope.actor.popclaw_id, 26,
                        "direct_message", 0, [], now_ms)
        seq = store.dm_append(cid, recipient, payload)
        relations.enqueue(store, recipient, cid)
    relations.publish(store)
    return PushOutcome(http_status=200, code="OK", event_id=cid, public=False,
                       extra={"inbox_seq": str(seq)})
