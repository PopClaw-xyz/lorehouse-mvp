"""The one business action over the native path: ``rangermap.check_in``.

Admission order (errors.md): context presence and binding, capability
revision, expiry, kind, schema version, session activity/fence, params size,
params schema — each failure produces a house-signed REJECTED ActionResult
receipt stored immutably under the request id. The accepted path commits
envelope evidence, business event + footprint, the house-signed public fact
and the terminal SUCCEEDED result in ONE SQLite transaction; the session
check runs again under that transaction's write lock so a concurrent leave
cannot authorize an interleaved action.

Replaying the exact original envelope returns the stored signed result
unchanged — even after the session has long expired — and never re-executes.
"""

from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass

from . import sessions as sessions_mod
from . import wire
from .check_in import TrustedCheckInContext, apply_check_in, validate_check_in_params
from .evidence import PushOutcome, blob, store_envelope
from .keys import HouseIdentity

ACTION_KIND = "rangermap.check_in"
SCHEMA_VERSION = 1
HOUSE_FACT_KIND = "rangermap.checked_in"
HOUSE_ACTOR_NICKNAME = "Ranger Map"

# ActionStatus proto values.
STATUS_ACCEPTED, STATUS_EXECUTING, STATUS_SUCCEEDED, STATUS_REJECTED = 1, 2, 3, 4


def _now() -> int:
    return int(time.time())


@dataclass
class StoredResult:
    actor_id: str
    request_digest: str
    status: str
    code: str
    kind: str
    signed_result_bytes: bytes


def stored_outcome_for(store, request_id: str) -> StoredResult | None:
    row = store.query_one(
        "SELECT * FROM action_results WHERE request_id = ?", (request_id,)
    )
    if row is None:
        return None
    return StoredResult(
        actor_id=row["actor_id"],
        request_digest=row["request_digest"],
        status=row["status"],
        code=row["code"],
        kind=row["kind"],
        signed_result_bytes=bytes(row["signed_result_bytes"]),
    )


def replay_outcome(stored: StoredResult, request_id: str) -> "PushOutcome":
    """Replay a terminal stored result with its ORIGINAL semantics.

    A stored SUCCEEDED result replays as an accepted duplicate; a stored
    REJECTED receipt replays with its original rejection code — a retry of
    a rejected request must never surface as accepted.
    """
    if stored.status == "rejected":
        return PushOutcome(
            http_status=422, code=stored.code,
            message="original rejection receipt replayed",
            event_id=request_id, duplicate=True,
            receipt_b64=wire.b64(stored.signed_result_bytes),
            extra={"status": stored.status},
        )
    return PushOutcome(
        http_status=200, code="OK", event_id=request_id, duplicate=True,
        receipt_b64=wire.b64(stored.signed_result_bytes),
        extra={"status": stored.status},
    )


def _build_result(identity: HouseIdentity, state, actor_id: str, request_id: str,
                  request_digest: str, status: int, code: str, kind: str,
                  result_body: bytes, execution_id: str) -> bytes:
    result = wire.ActionResult()
    result.house.origin = state.origin
    result.house.house_key = identity.house_key_id
    result.house.incarnation = state.server_incarnation
    result.actor_id = actor_id
    result.audience_id = actor_id
    result.request_id = request_id
    result.request_digest = request_digest
    result.execution_id = execution_id
    result.status = status
    result.status_revision = 1
    result.code = code
    result.kind = kind
    result.schema_version = SCHEMA_VERSION
    result.capability_revision = state.manifest_digest
    if result_body:
        result.result_body = result_body
        result.result_digest = _sha256_hex(result_body)
    result.committed_at = _now()

    signed = wire.SignedActionResult()
    signed.result.CopyFrom(result)
    signed.signature = identity.sign(
        wire.signing_input(wire.DOMAIN_ACTION_RESULT, wire.canonical_core(result))
    )
    return signed.SerializeToString(deterministic=True)


def _sha256_hex(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def _receipt_outcome(store, identity, state, actor_id, request_id,
                     request_digest, code: str, message: str,
                     http_status: int) -> PushOutcome:
    """Store an immutable signed rejection receipt under the request id.

    A concurrent attempt may have inserted a terminal result under the same
    request_id first (same envelope racing validation, or a same-id/different-
    bytes conflict): the ORIGINAL stored result always stands — it is
    returned untouched (with IDEMPOTENCY_CONFLICT when the stored digest
    differs), never overwritten and never duplicated.
    """
    with store.write_tx():
        existing = stored_outcome_for(store, request_id)
        if existing is not None:
            signed = existing.signed_result_bytes
            if existing.request_digest != request_digest:
                code, message, http_status = (
                    "IDEMPOTENCY_CONFLICT",
                    "request_id reused with different bytes; original result"
                    " remains queryable",
                    409,
                )
        else:
            signed = _build_result(identity, state, actor_id, request_id,
                                   request_digest, STATUS_REJECTED, code,
                                   ACTION_KIND, b"", "")
            _store_action_result(store, request_id, actor_id, request_digest,
                                 "rejected", code, signed)
    return PushOutcome(http_status=http_status, code=code, message=message,
                       event_id=request_id, receipt_b64=wire.b64(signed))


def _store_action_result(store, request_id: str, actor_id: str,
                         request_digest: str, status: str, code: str,
                         signed: bytes) -> None:
    store.execute(
        "INSERT OR IGNORE INTO action_results (request_id, actor_id,"
        " request_digest, status, code, kind, signed_result_bytes, created_ms)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (request_id, actor_id, request_digest, status, code, ACTION_KIND,
         blob(signed), store.clock_ms()),
    )


def _resolve_nickname(store, envelope) -> str | None:
    profile = store.query_one(
        "SELECT display_name FROM profiles WHERE ranger_id = ?",
        (envelope.actor.popclaw_id,),
    )
    if profile is not None and profile["display_name"]:
        return profile["display_name"]
    nickname = envelope.actor.nickname
    if nickname and not any(0xD800 <= ord(ch) <= 0xDFFF for ch in nickname):
        return nickname
    return None


def handle_intent(store, identity: HouseIdentity, state, payload: bytes,
                  envelope, cid: str) -> PushOutcome:
    intent = envelope.intent
    actor_id = envelope.actor.popclaw_id
    request_digest = _sha256_hex(payload)

    # Idempotency against the terminal result (checked again in-tx below).
    stored = stored_outcome_for(store, cid)
    if stored is not None:
        if stored.request_digest != request_digest:
            # The original immutable result stands; report the conflict
            # WITHOUT inserting a second receipt under the same request_id.
            return PushOutcome(
                http_status=409, code="IDEMPOTENCY_CONFLICT",
                message="request_id reused with different bytes; the original"
                        " result remains queryable",
                event_id=cid, receipt_b64=wire.b64(stored.signed_result_bytes),
            )
        return replay_outcome(stored, cid)

    if not intent.HasField("context"):
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "INTENT_CONTEXT_MISSING",
                                "world actions require a full IntentContext", 422)
    context = intent.context
    if (context.house_origin != state.origin
            or context.house_key != identity.house_key_id
            or context.incarnation != state.server_incarnation
            or intent.lorehouse not in ("", state.origin)):
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "INTENT_CONTEXT_MISMATCH",
                                "context does not bind to this house", 422)
    if context.capability_revision != state.manifest_digest:
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "CAPABILITY_REVISION_MISMATCH",
                                "context quotes a different manifest", 422)
    if intent.intent_kind != ACTION_KIND:
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "INTENT_NOT_DECLARED",
                                "this house declares only rangermap.check_in", 422)
    if context.schema_version != SCHEMA_VERSION:
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "SCHEMA_VERSION_UNSUPPORTED",
                                "only schema version 1 is served", 422)
    if _now() >= context.valid_until:
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "CONTEXT_EXPIRED",
                                "request valid_until has passed", 422)

    params = bytes(intent.params)
    if len(params) > wire.L_PARAMS_MAX_BYTES:
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "PARAMS_SIZE_EXCEEDED",
                                "params exceed the size limit", 422)
    try:
        validate_check_in_params(params)
    except Exception:
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "PARAMS_SCHEMA_INVALID",
                                "params fail the declared schema", 422)

    session = sessions_mod.active_session_row(store, actor_id, context.session_id)
    if session is None:
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "SESSION_INACTIVE",
                                "no active session for this actor", 422)
    if str(session["house_revision"]) != context.fence:
        return _receipt_outcome(store, identity, state, actor_id, cid,
                                request_digest, "SESSION_FENCED",
                                "session fence does not match the context", 422)

    # ---- the authoritative transaction ---------------------------------
    execution_id = "exec-" + secrets.token_hex(12)
    with store.write_tx():
        stored = stored_outcome_for(store, cid)
        if stored is not None:
            if stored.request_digest != request_digest:
                raise _InTxConflict("IDEMPOTENCY_CONFLICT")
            raise _InTxReplay(stored)

        # Session may have been fenced/closed and the request window may
        # have lapsed between the outer check and this transaction; BOTH are
        # re-validated at transactional admission under the write lock, so a
        # request that expired while waiting never produces effects.
        if _now() >= context.valid_until:
            raise _InTxReject("CONTEXT_EXPIRED",
                              "request valid_until passed before admission")
        session = sessions_mod.active_session_row(store, actor_id,
                                                  context.session_id)
        if session is None:
            raise _InTxReject("SESSION_INACTIVE", "session no longer active")
        if str(session["house_revision"]) != context.fence:
            raise _InTxReject("SESSION_FENCED", "session fenced at commit")

        # 1. Signed-wire evidence for the accepted intent envelope.
        store_envelope(store, cid, payload, actor_id, 35, ACTION_KIND, 0, [],
                       store.clock_ms())
        # 2. Business event (params bytes) + footprint projection.
        context_obj = TrustedCheckInContext(
            ranger_id=actor_id,
            nickname=_resolve_nickname(store, envelope),
            source_event_id=cid,
        )
        result = apply_check_in(store, context_obj, params, in_tx=True)
        footprint = result.footprint
        # 3. House-signed public fact carrying the footprint body.
        fact_bytes = _build_house_fact(store, identity, state, footprint)
        fact = wire.EventEnvelope.FromString(fact_bytes)
        fact_cid = wire.envelope_cid(fact_bytes)
        store_envelope(store, fact_cid, fact_bytes, identity.house_key_id, 34,
                       HOUSE_FACT_KIND, 1,
                       list(fact.house_event.public_scopes), store.clock_ms())
        public_seq = store.public_log_append(
            state.log_incarnation, fact_cid, fact_bytes, HOUSE_FACT_KIND,
            json.dumps(list(fact.house_event.public_scopes)))
        # 4. Terminal signed result.
        result_body = json.dumps(
            footprint.to_json_dict(), separators=(",", ":"),
            ensure_ascii=False).encode("utf-8")
        signed = _build_result(identity, state, actor_id, cid, request_digest,
                               STATUS_SUCCEEDED, "OK", ACTION_KIND,
                               result_body, execution_id)
        _store_action_result(store, cid, actor_id, request_digest, "succeeded",
                             "OK", signed)

    return PushOutcome(
        http_status=200, code="OK", event_id=cid, public=True,
        receipt_b64=wire.b64(signed),
        extra={
            "status": "succeeded",
            "footprint_seq": footprint.seq,
            "public_event_id": fact_cid,
            "public_seq": str(public_seq),
        },
    )


class _InTxReplay(Exception):
    def __init__(self, stored: StoredResult):
        super().__init__("replay")
        self.stored = stored


class _InTxReject(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(code)
        self.code = code
        self.message = message


class _InTxConflict(Exception):
    pass


def handle_intent_transactional(store, identity, state, payload, envelope, cid):
    """Wrapper that converts in-transaction outcomes into push responses."""
    try:
        return handle_intent(store, identity, state, payload, envelope, cid)
    except _InTxReplay as replay:
        return replay_outcome(replay.stored, cid)
    except _InTxReject as reject:
        return _receipt_outcome(store, identity, state,
                                envelope.actor.popclaw_id, cid,
                                _sha256_hex(payload), reject.code,
                                reject.message, 422)
    except _InTxConflict:
        return _receipt_outcome(store, identity, state,
                                envelope.actor.popclaw_id, cid,
                                _sha256_hex(payload), "IDEMPOTENCY_CONFLICT",
                                "request_id reused with different bytes", 409)


def _build_house_fact(store, identity: HouseIdentity, state, footprint) -> bytes:
    body = json.dumps(footprint.to_json_dict(), separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    envelope = wire.EventEnvelope()
    envelope.actor.popclaw_id = identity.house_key_id
    envelope.actor.nickname = HOUSE_ACTOR_NICKNAME
    envelope.timestamp = _now()
    envelope.house_event.kind = HOUSE_FACT_KIND
    envelope.house_event.schema_version = SCHEMA_VERSION
    envelope.house_event.body = body
    envelope.house_event.public_scopes.extend(state.registered_scopes)
    canonical = wire.canonical_envelope(envelope)
    envelope.event_id = _sha256_hex(canonical)
    envelope.signature = identity.sign(canonical)
    return envelope.SerializeToString(deterministic=True)


# --- signed status reads ---------------------------------------------------


def handle_status(store, identity: HouseIdentity, state, body: bytes):
    """``POST /v1/world-actions/status``. Returns (status, payload bytes)."""
    try:
        request = wire.ActionStatusRequest.FromString(body)
    except Exception:
        return 400, b'{"error":{"code":"READ_REQUEST_INVALID","message":"malformed ActionStatusRequest"}}'
    try:
        actor_key = wire.key_bytes_from_popclaw_id(request.actor_id)
    except ValueError:
        return 401, _json_error("READ_REQUEST_INVALID", "actor_id invalid")

    core = wire.ActionStatusRequest()
    core.house.origin = request.house.origin
    core.house.house_key = request.house.house_key
    core.house.incarnation = request.house.incarnation
    core.actor_id = request.actor_id
    core.request_id = request.request_id
    core.nonce = request.nonce
    core.issued_at = request.issued_at
    core.expires_at = request.expires_at
    if not wire.verify_ed25519(
        actor_key, bytes(request.signature),
        wire.signing_input(wire.DOMAIN_ACTION_STATUS_READ, wire.canonical_core(core)),
    ):
        return 401, _json_error("READ_REQUEST_INVALID", "status read signature invalid")
    now = _now()
    if request.issued_at > now or now >= request.expires_at:
        return 401, _json_error("READ_REQUEST_EXPIRED", "status read window invalid")
    if request.expires_at - request.issued_at > wire.L_STATUS_QUERY_TTL_MAX_SECONDS:
        return 401, _json_error("READ_REQUEST_INVALID", "status read TTL too long")
    if (request.house.origin != state.origin
            or request.house.house_key != identity.house_key_id
            or request.house.incarnation != state.server_incarnation):
        return 401, _json_error("READ_REQUEST_INVALID",
                                "status read bound to another house")

    with store.write_tx():
        existing = store.query_one(
            "SELECT 1 FROM used_nonces WHERE actor_id = ? AND nonce = ?",
            (request.actor_id, request.nonce),
        )
        if existing is not None:
            return 401, _json_error("READ_REQUEST_INVALID", "nonce already used")
        store.execute(
            "INSERT INTO used_nonces (actor_id, nonce, expires_at)"
            " VALUES (?, ?, ?)",
            (request.actor_id, request.nonce, request.expires_at),
        )
        store.execute("DELETE FROM used_nonces WHERE expires_at < ?", (now,))

    row = store.query_one(
        "SELECT * FROM action_results WHERE request_id = ?",
        (request.request_id,),
    )
    if row is None:
        return 404, _json_error("REQUEST_NOT_FOUND",
                                "no result for this request id (never proof of "
                                "absence of business effects)")
    if row["actor_id"] != request.actor_id:
        return 403, _json_error("REQUEST_FORBIDDEN",
                                "this request id belongs to another actor")

    response = wire.ActionStatusResponse()
    response.result.CopyFrom(
        wire.SignedActionResult.FromString(bytes(row["signed_result_bytes"]))
    )
    return 200, response.SerializeToString(deterministic=True)


def _json_error(code: str, message: str) -> bytes:
    return json.dumps({"error": {"code": code, "message": message}}).encode("utf-8")
