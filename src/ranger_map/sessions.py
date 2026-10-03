"""G0 house-session lifecycle: enter / renew / leave / status.

Every handled outcome — including rejections — is a house-signed
``HouseSessionAck`` bound to the saved original request (origin, actor,
installation, request id, op seq, operation). Requests carry the actor's
Ed25519 signature over ``POPCLAW_HOUSE_SESSION_REQUEST_V1 || canonical core``;
ACKs use the ``..._ACK_V1`` domain under the house ACK authority (the same
32-byte authority key as HouseBinding.house_key).

Semantics per house_session.proto: ENTER compare-and-set on op_seq per
(identity, installation), a leave watermark forbidding older enters, lease
90 s / renew semantics, a monotonic house_revision fence allocated only on
new generations, never-reused session ids, and v2 inbox tokens tied to the
session that die with it.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass

from . import house as house_mod
from . import wire
from .keys import HouseIdentity

ENTER, RENEW, LEAVE, STATUS = 1, 2, 3, 4

# proto ErrorCode values.
INVALID_HOUSE = 1
EXECUTOR_BUSY = 4
STALE_OPERATION = 5
SESSION_FENCED = 6
LEASE_EXPIRED = 7
AUTH_INVALID = 8
AUDIENCE_MISMATCH = 9
IDEMPOTENCY_CONFLICT = 10

_REQUEST_MAX_WINDOW_SECONDS = 600
# Request timestamps come from the signing host's clock. Permit only a small
# bounded future issue time; expiry remains a strict server-clock deadline.
_REQUEST_CLOCK_SKEW_SECONDS = 30


@dataclass
class SessionDecision:
    ack_bytes: bytes
    outcome: int
    error_code: int
    session_id: str
    house_revision: int
    inbox_read_token: str


class SessionRejected(Exception):
    """Raised for structurally invalid requests that get no ACK at all."""

    def __init__(self, message: str, http_status: int = 400):
        super().__init__(message)
        self.http_status = http_status


def _canonical_core_hex(core) -> str:
    return wire.canonical_core(core).hex()


def _semantic_core_hex(core) -> str:
    """Semantic request identity: everything except refreshable nonce/times.

    house_session.proto permits retries to refresh nonce and timestamps while
    keeping the original request_id and semantic operation; byte-exact
    canonical comparison wrongly turns such retries into conflicts.
    """
    semantic = wire.RequestCore()
    semantic.CopyFrom(core)
    semantic.ClearField("issued_at")
    semantic.ClearField("expires_at")
    semantic.ClearField("nonce")
    return wire.canonical_core(semantic).hex()


def _row_semantic_hex(row) -> str:
    """Stored semantic identity; rows written before the semantic column
    existed are derived from their preserved canonical evidence."""
    stored = row["semantic_core_hex"] if "semantic_core_hex" in row.keys() else None
    if stored:
        return stored
    original = wire.RequestCore.FromString(bytes.fromhex(row["core_canonical_hex"]))
    return _semantic_core_hex(original)


def _now() -> int:
    return int(time.time())


def _new_session_id() -> str:
    return "sess-" + secrets.token_hex(16)


def _ack(identity: HouseIdentity, origin: str, request_core, outcome: int,
         error_code: int, house_revision: int, session_id: str,
         session_active: bool, lease_expires_at: int, detail: str,
         status_row=None, inbox_token: str = "") -> bytes:
    core = wire.AckCore()
    core.house_origin = origin
    core.popclaw_id = request_core.popclaw_id
    core.installation_id = request_core.installation_id
    core.request_id = request_core.request_id
    core.op_seq = request_core.op_seq
    core.operation = request_core.operation
    core.outcome = outcome
    if error_code:
        core.error_code = error_code
    core.house_revision = house_revision
    if session_id:
        core.session_id = session_id
    core.session_active = session_active
    if lease_expires_at:
        core.lease_expires_at = lease_expires_at
    core.server_committed_at = _now()
    if detail:
        core.detail = detail
    if status_row is not None:
        info = core.status
        info.session_id = status_row["session_id"]
        info.house_revision = status_row["house_revision"]
        info.lease_expires_at = status_row["lease_expires_at"]
        info.installation_id = status_row["installation_id"]
        info.entered_op_seq = status_row["entered_op_seq"]
    if inbox_token:
        core.inbox_read_token = inbox_token
    ack = wire.HouseSessionAck()
    ack.core.CopyFrom(core)
    ack.signer_pubkey = identity.public_key_bytes
    ack.signature = identity.sign(
        wire.signing_input(wire.DOMAIN_SESSION_ACK, wire.canonical_core(core))
    )
    return ack.SerializeToString(deterministic=True)


def _inbox_token_message(origin: str, token_id: str, actor_id: str,
                         session_id: str, house_revision: int,
                         expires_at: int) -> bytes:
    # The representation is house-internal and opaque on the wire (the .3
    # contract does not prescribe one); the signed binding covers the
    # canonical audience (origin), actor, session and revision as required
    # by house_session.proto's inbox_read_token field.
    return (f"inbox-token-v2:{token_id}:{origin}:{actor_id}:{session_id}:"
            f"{house_revision}:{expires_at}").encode("utf-8")


def _issue_inbox_token(store, identity: HouseIdentity, origin: str,
                       actor_id: str, session_row) -> str:
    token_id = "itk-" + secrets.token_hex(12)
    expires_at = _now() + wire.INBOX_TOKEN_TTL_SECONDS
    store.execute(
        "INSERT INTO inbox_tokens (token_id, actor_id, session_id,"
        " house_revision, expires_at, revoked) VALUES (?, ?, ?, ?, ?, 0)",
        (token_id, actor_id, session_row["session_id"],
         session_row["house_revision"], expires_at),
    )
    message = _inbox_token_message(origin, token_id, actor_id,
                                   session_row["session_id"],
                                   session_row["house_revision"], expires_at)
    signature = identity.sign(message)
    return f"{token_id}.{expires_at}.{wire.b64(signature)}"


def verify_inbox_token(store, identity: HouseIdentity, origin: str,
                       token: str, popclaw_id: str) -> bool:
    """Validate a house-issued v2 inbox token for a recipient stream."""
    parts = token.split(".")
    if len(parts) != 3:
        return False
    token_id, expires_text, signature_b64 = parts
    if not token_id or not expires_text.isdigit():
        return False
    expires_at = int(expires_text)
    row = store.query_one(
        "SELECT * FROM inbox_tokens WHERE token_id = ?", (token_id,)
    )
    if row is None or row["revoked"] or row["actor_id"] != popclaw_id:
        return False
    if expires_at != row["expires_at"] or _now() >= expires_at:
        return False
    session = store.query_one(
        "SELECT * FROM sessions WHERE session_id = ?", (row["session_id"],)
    )
    if session is None or not session["active"] or _now() >= session["lease_expires_at"]:
        return False
    if session["house_revision"] != row["house_revision"]:
        return False
    message = _inbox_token_message(origin, token_id, popclaw_id,
                                   row["session_id"], row["house_revision"],
                                   expires_at)
    try:
        signature = wire.b64decode_strict(signature_b64)
    except Exception:
        return False
    return identity.verify(signature, message)


def verify_legacy_inbox_token(token: str, popclaw_id: str) -> bool:
    """Legacy self-signed lane: ``<id>.<UTC-seconds>.<b64 sig>`` over
    ``inbox-read:<id>:<seconds>`` within a 60-second window."""
    try:
        key_bytes = wire.key_bytes_from_popclaw_id(popclaw_id)
    except ValueError:
        return False
    parts = token.split(".")
    if len(parts) != 3 or not parts[1].isdigit():
        return False
    issued = int(parts[1])
    now = _now()
    if abs(now - issued) > wire.LEGACY_INBOX_WINDOW_SECONDS:
        return False
    try:
        signature = wire.b64decode_strict(parts[2])
    except Exception:
        return False
    message = f"inbox-read:{popclaw_id}:{issued}".encode("utf-8")
    return wire.verify_ed25519(key_bytes, signature, message)


def active_session_row(store, actor_id: str, session_id: str):
    """The session row iff active, unexpired and owned by the actor."""
    row = store.query_one(
        "SELECT * FROM sessions WHERE session_id = ? AND actor_id = ?",
        (session_id, actor_id),
    )
    if row is None or not row["active"] or _now() >= row["lease_expires_at"]:
        return None
    return row


def handle_session_request(store, identity: HouseIdentity, state, body: bytes
                           ) -> SessionDecision:
    """Full request pipeline; every handled outcome returns a signed ACK."""
    try:
        request = wire.HouseSessionRequest.FromString(body)
    except Exception:
        raise SessionRejected("malformed HouseSessionRequest") from None
    core = request.core

    if core.operation not in (ENTER, RENEW, LEAVE, STATUS):
        # OPERATION_UNSPECIFIED/unsupported never reaches state mutation; a
        # signed rejection keeps the evidence trail.
        return _reject(store, identity, state, core, AUTH_INVALID,
                       "unsupported operation")
    try:
        actor_key = wire.key_bytes_from_popclaw_id(core.popclaw_id)
    except ValueError:
        return _reject(store, identity, state, core, AUTH_INVALID,
                       "popclaw_id must decode to a 32-byte key")
    if request.signer_pubkey != actor_key:
        return _reject(store, identity, state, core, AUTH_INVALID,
                       "signer key does not match popclaw_id")
    if not wire.verify_ed25519(
        request.signer_pubkey,
        request.signature,
        wire.signing_input(wire.DOMAIN_SESSION_REQUEST, wire.canonical_core(core)),
    ):
        return _reject(store, identity, state, core, AUTH_INVALID,
                       "request signature invalid")

    now = _now()
    if (core.issued_at > now + _REQUEST_CLOCK_SKEW_SECONDS
            or now >= core.expires_at
            or core.expires_at <= core.issued_at):
        return _reject(store, identity, state, core, AUTH_INVALID,
                       "request time window invalid")
    if core.expires_at - core.issued_at > _REQUEST_MAX_WINDOW_SECONDS:
        return _reject(store, identity, state, core, AUTH_INVALID,
                       "request window too long")
    if core.house_origin != state.origin:
        return _reject(store, identity, state, core, AUDIENCE_MISMATCH,
                       "request targets another house origin")

    # Request-id idempotency against the SAVED original request: equal
    # SEMANTIC cores (fresh nonce/times allowed) replay the immutable stored
    # ACK; a changed semantic operation is a conflict. Every attempt was
    # fully authenticated above regardless of the stored outcome.
    canonical_hex = _canonical_core_hex(core)
    semantic_hex = _semantic_core_hex(core)
    existing = store.query_one(
        "SELECT * FROM session_requests WHERE request_id = ?",
        (core.request_id,),
    )
    if existing is not None:
        if _row_semantic_hex(existing) != semantic_hex:
            return _reject(store, identity, state, core, IDEMPOTENCY_CONFLICT,
                           "request_id reused with a different semantic operation")
        return SessionDecision(
            ack_bytes=bytes(existing["ack_bytes"]),
            outcome=_outcome_of(bytes(existing["ack_bytes"])),
            error_code=0,
            session_id="",
            house_revision=0,
            inbox_read_token="",
        )

    # The decision and its idempotency record commit atomically: an ACK is
    # only returned once its session_requests row is durable. The semantic
    # idempotency lookup is REPEATED inside the write transaction: two
    # authenticated same-request_id first attempts that both missed the
    # outside lookup serialise here, the second replays the first's stored
    # ACK instead of racing the UNIQUE insert.
    with store.write_tx():
        raced = store.query_one(
            "SELECT * FROM session_requests WHERE request_id = ?",
            (core.request_id,),
        )
        if raced is not None:
            if _row_semantic_hex(raced) != semantic_hex:
                decision = _reject(store, identity, state, core,
                                   IDEMPOTENCY_CONFLICT,
                                   "request_id reused with a different"
                                   " semantic operation")
            else:
                decision = SessionDecision(
                    ack_bytes=bytes(raced["ack_bytes"]),
                    outcome=_outcome_of(bytes(raced["ack_bytes"])),
                    error_code=0,
                    session_id="",
                    house_revision=0,
                    inbox_read_token="",
                )
            return decision

        if core.operation == ENTER:
            decision = _enter(store, identity, state, core, now)
        elif core.operation == RENEW:
            decision = _renew(store, identity, state, core, now)
        elif core.operation == LEAVE:
            decision = _leave(store, identity, state, core, now)
        else:
            decision = _status(store, identity, state, core, now)

        store.execute(
            "INSERT INTO session_requests (request_id, actor_id, installation_id,"
            " core_canonical_hex, semantic_core_hex, ack_bytes, created_ms)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (core.request_id, core.popclaw_id, core.installation_id, canonical_hex,
             semantic_hex, decision.ack_bytes, store.clock_ms()),
        )
    return decision


def _outcome_of(ack_bytes: bytes) -> int:
    return wire.HouseSessionAck.FromString(ack_bytes).core.outcome


def actor_revision(store, actor_id: str) -> int:
    """The actor's authoritative session-generation fence.

    The global allocator only guarantees fence uniqueness; the ACK must
    report the generation THIS actor acts under, so a client's action fence
    keeps working while other identities enter and bump the global counter.
    """
    row = store.query_one(
        "SELECT COALESCE(MAX(house_revision), 0) AS r FROM sessions"
        " WHERE actor_id = ?",
        (actor_id,),
    )
    return int(row["r"])


def actor_has_session_state(store, actor_id: str) -> bool:
    """True once this identity has ANY session history in this house.

    Reference-server security policy (aligned with the official Rust
    implementation, not quoted public normative text): once an identity has
    used house sessions here, the self-signed legacy inbox lane is refused
    for it and only house-issued session tokens open its inbox.
    """
    row = store.query_one(
        "SELECT 1 FROM sessions WHERE actor_id = ? LIMIT 1", (actor_id,)
    )
    return row is not None


def _reject(store, identity, state, core, error_code: int, detail: str
            ) -> SessionDecision:
    ack = _ack(identity, state.origin, core,
               outcome=7,  # REJECTED
               error_code=error_code,
               house_revision=actor_revision(store, core.popclaw_id),
               session_id="", session_active=False, lease_expires_at=0,
               detail=detail)
    return SessionDecision(ack_bytes=ack, outcome=7, error_code=error_code,
                           session_id="", house_revision=0,
                           inbox_read_token="")


def _ensure_installation(store, actor_id: str, installation_id: str) -> None:
    store.execute(
        "INSERT OR IGNORE INTO installations (actor_id, installation_id,"
        " disabled_through_op_seq) VALUES (?, ?, 0)",
        (actor_id, installation_id),
    )


def _current_session(store, actor_id: str, installation_id: str):
    """The active, unexpired session of this installation, if any."""
    row = store.query_one(
        "SELECT * FROM sessions WHERE actor_id = ? AND installation_id = ?"
        " AND active = 1 ORDER BY entered_op_seq DESC LIMIT 1",
        (actor_id, installation_id),
    )
    if row is None:
        return None
    if _now() >= row["lease_expires_at"]:
        store.execute("UPDATE sessions SET active = 0, closed_ms = ?"
                      " WHERE session_id = ?", (store.clock_ms(), row["session_id"]))
        return None
    return row


def _enter(store, identity, state, core, now: int) -> SessionDecision:
    # Runs inside handle_session_request's write transaction.
        _ensure_installation(store, core.popclaw_id, core.installation_id)
        watermark_row = store.query_one(
            "SELECT disabled_through_op_seq AS d FROM installations"
            " WHERE actor_id = ? AND installation_id = ?",
            (core.popclaw_id, core.installation_id),
        )
        watermark = int(watermark_row["d"]) if watermark_row else 0
        if core.op_seq <= watermark:
            return _ack_decision(identity, state, core, outcome=7,
                                 error_code=STALE_OPERATION,
                                 detail="op_seq is covered by an earlier leave",
                                 store=store)

        current = _current_session(store, core.popclaw_id, core.installation_id)
        # The installation's LATEST generation, expired or not: op_seq
        # ordering must hold across expiry, so a delayed lower ENTER after
        # the lease lapsed is stale rather than a new generation.
        latest = store.query_one(
            "SELECT * FROM sessions WHERE actor_id = ? AND installation_id = ?"
            " ORDER BY entered_op_seq DESC, created_ms DESC LIMIT 1",
            (core.popclaw_id, core.installation_id),
        )

        if current is not None and current["entered_op_seq"] == core.op_seq:
            if (core.expected_house_revision
                    and core.expected_house_revision != current["house_revision"]):
                return _ack_decision(identity, state, core, outcome=7,
                                     error_code=SESSION_FENCED,
                                     detail="expected revision mismatch",
                                     store=store)
            lease = now + wire.SESSION_LEASE_SECONDS
            store.execute(
                "UPDATE sessions SET lease_expires_at = ? WHERE session_id = ?",
                (lease, current["session_id"]),
            )
            token = _issue_inbox_token(store, identity, state.origin, core.popclaw_id, current)
            return _ack_decision(identity, state, core, outcome=2,
                                 session=current, lease=lease, token=token,
                                 store=store, detail="generation reused")

        reference = current if current is not None else latest
        if reference is not None and reference["entered_op_seq"] > core.op_seq:
            return _ack_decision(identity, state, core, outcome=7,
                                 error_code=STALE_OPERATION,
                                 detail="op_seq below the current generation",
                                 store=store)

        # New-generation path (current expired/absent or higher op_seq):
        # an expected_house_revision CAS mismatch must never silently
        # overwrite a known generation, active or expired.
        expected_reference = (current["house_revision"] if current is not None
                              else actor_revision(store, core.popclaw_id))
        if (core.expected_house_revision
                and core.expected_house_revision != expected_reference):
            return _ack_decision(identity, state, core, outcome=7,
                                 error_code=SESSION_FENCED,
                                 detail="expected revision mismatch",
                                 store=store)

        # A valid lease held by another installation is EXECUTOR_BUSY.
        other = store.query_one(
            "SELECT * FROM sessions WHERE actor_id = ? AND active = 1"
            " AND installation_id != ? ORDER BY entered_op_seq DESC LIMIT 1",
            (core.popclaw_id, core.installation_id),
        )
        if other is not None and now < other["lease_expires_at"]:
            return _ack_decision(identity, state, core, outcome=7,
                                 error_code=EXECUTOR_BUSY,
                                 detail="another installation holds the lease",
                                 store=store)
        if other is not None:
            store.execute("UPDATE sessions SET active = 0, closed_ms = ?"
                          " WHERE session_id = ?",
                          (store.clock_ms(), other["session_id"]))

        if current is not None:
            # Rotation to a higher op_seq: close the previous generation.
            store.execute("UPDATE sessions SET active = 0, closed_ms = ?"
                          " WHERE session_id = ?",
                          (store.clock_ms(), current["session_id"]))

        revision = house_mod.next_house_revision(store, in_tx=True)
        session_id = _new_session_id()
        lease = now + wire.SESSION_LEASE_SECONDS
        store.execute(
            "INSERT INTO sessions (session_id, actor_id, installation_id,"
            " entered_op_seq, house_revision, lease_expires_at, active,"
            " created_ms, closed_ms) VALUES (?, ?, ?, ?, ?, ?, 1, ?, NULL)",
            (session_id, core.popclaw_id, core.installation_id, core.op_seq,
             revision, lease, store.clock_ms()),
        )
        row = store.query_one("SELECT * FROM sessions WHERE session_id = ?",
                              (session_id,))
        token = _issue_inbox_token(store, identity, state.origin, core.popclaw_id, row)
        return _ack_decision(identity, state, core, outcome=1, session=row,
                             lease=lease, token=token, store=store)


def _renew(store, identity, state, core, now: int) -> SessionDecision:
    # Runs inside handle_session_request's write transaction.
        row = store.query_one(
            "SELECT * FROM sessions WHERE session_id = ? AND actor_id = ?",
            (core.target_session_id, core.popclaw_id),
        )
        if row is None or row["installation_id"] != core.installation_id:
            return _ack_decision(identity, state, core, outcome=7,
                                 error_code=SESSION_FENCED,
                                 detail="unknown target session", store=store)
        if not row["active"] or now >= row["lease_expires_at"]:
            store.execute("UPDATE sessions SET active = 0, closed_ms = ?"
                          " WHERE session_id = ?",
                          (store.clock_ms(), row["session_id"]))
            return _ack_decision(identity, state, core, outcome=7,
                                 error_code=LEASE_EXPIRED,
                                 detail="lease expired; enter again", store=store)
        lease = now + wire.SESSION_LEASE_SECONDS
        store.execute("UPDATE sessions SET lease_expires_at = ? WHERE session_id = ?",
                      (lease, row["session_id"]))
        row = store.query_one("SELECT * FROM sessions WHERE session_id = ?",
                              (core.target_session_id,))
        token = _issue_inbox_token(store, identity, state.origin, core.popclaw_id, row)
        return _ack_decision(identity, state, core, outcome=3, session=row,
                             lease=lease, token=token, store=store)


def _leave(store, identity, state, core, now: int) -> SessionDecision:
    # Runs inside handle_session_request's write transaction.
        _ensure_installation(store, core.popclaw_id, core.installation_id)
        watermark_row = store.query_one(
            "SELECT disabled_through_op_seq AS d FROM installations"
            " WHERE actor_id = ? AND installation_id = ?",
            (core.popclaw_id, core.installation_id),
        )
        watermark = int(watermark_row["d"]) if watermark_row else 0
        if core.op_seq <= watermark:
            return _ack_decision(identity, state, core, outcome=5,
                                 detail="already closed through this op_seq",
                                 store=store)

        current = _current_session(store, core.popclaw_id, core.installation_id)
        closed_any = False
        superseded = False
        rows = store.query_all(
            "SELECT * FROM sessions WHERE actor_id = ? AND installation_id = ?"
            " AND active = 1",
            (core.popclaw_id, core.installation_id),
        )
        for row in rows:
            if row["entered_op_seq"] <= core.op_seq:
                store.execute(
                    "UPDATE sessions SET active = 0, closed_ms = ?"
                    " WHERE session_id = ?",
                    (store.clock_ms(), row["session_id"]),
                )
                store.execute(
                    "UPDATE inbox_tokens SET revoked = 1 WHERE session_id = ?",
                    (row["session_id"],),
                )
                closed_any = True
            else:
                superseded = True  # a late old leave never closes a newer enter

        store.execute(
            "UPDATE installations SET disabled_through_op_seq = ?"
            " WHERE actor_id = ? AND installation_id = ?",
            (core.op_seq, core.popclaw_id, core.installation_id),
        )
        if superseded and not closed_any:
            return _ack_decision(identity, state, core, outcome=6,
                                 detail="a newer generation stays open",
                                 store=store)
        if closed_any and current is not None and current["entered_op_seq"] > core.op_seq:
            return _ack_decision(identity, state, core, outcome=6,
                                 detail="newer generation unaffected", store=store)
        return _ack_decision(identity, state, core, outcome=4,
                             detail="session closed", store=store)


def _status(store, identity, state, core, now: int) -> SessionDecision:
    # Runs inside handle_session_request's write transaction.
        row = store.query_one(
            "SELECT * FROM sessions WHERE session_id = ? AND actor_id = ?",
            (core.target_session_id, core.popclaw_id),
        )
        if row is None or row["installation_id"] != core.installation_id:
            return _ack_decision(identity, state, core, outcome=7,
                                 error_code=SESSION_FENCED,
                                 detail="unknown target session", store=store)
        active = bool(row["active"]) and now < row["lease_expires_at"]
        if row["active"] and not active:
            store.execute("UPDATE sessions SET active = 0, closed_ms = ?"
                          " WHERE session_id = ?",
                          (store.clock_ms(), row["session_id"]))
        return _ack_decision(identity, state, core, outcome=8, session=row,
                             session_active=active, store=store)


def _ack_decision(identity, state, core, outcome: int, store,
                  session=None, lease: int = 0, token: str = "",
                  session_active: bool | None = None,
                  error_code: int = 0, detail: str = "") -> SessionDecision:
    # The ACK reports the ACTOR's authoritative generation fence (the
    # session's own revision when one is associated, else the actor's latest
    # generation), never the global allocator counter.
    if session is not None:
        house_revision = int(session["house_revision"])
    else:
        house_revision = actor_revision(store, core.popclaw_id)
    if session is not None and session_active is None:
        session_active = bool(session["active"])
    ack = _ack(
        identity, state.origin, core, outcome=outcome, error_code=error_code,
        house_revision=house_revision,
        session_id=session["session_id"] if session is not None else "",
        session_active=bool(session_active), lease_expires_at=lease,
        detail=detail, status_row=session if outcome == 8 else None,
        inbox_token=token,
    )
    return SessionDecision(ack_bytes=ack, outcome=outcome,
                           error_code=error_code,
                           session_id=session["session_id"] if session is not None else "",
                           house_revision=house_revision,
                           inbox_read_token=token)
