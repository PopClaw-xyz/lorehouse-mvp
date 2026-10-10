"""Consumption bridge over the vendored PopClaw contract bundle.

Loads the pinned descriptor and canonical/wire helpers from
``vendor/popclaw-contracts/packages/contracts/python`` exactly as shipped
(the bundle's Python bridge is the implementation basis; no alternative
canonical codec is hand-rolled here), and adds the small Ed25519 layer this
server needs on top of ``cryptography``.

All signing domains and canonical-byte rules come from the bundle's
``protocol/public-envelope-02/SIGNING.md``; the retained vectors pin them.
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR_PYTHON = (
    REPO_ROOT / "vendor" / "popclaw-contracts" / "packages" / "contracts" / "python"
)

_VENDORED_PATH = str(VENDOR_PYTHON)
if _VENDORED_PATH not in sys.path:
    sys.path.insert(0, _VENDORED_PATH)

# The vendored bridge modules (``protocol``/``public_baseline``) are imported
# by their own plain names from the vendor directory. This module is the only
# place that does so; the rest of ranger_map imports them from here.
import protocol as _vendor_protocol  # noqa: E402  (vendored bundle module)
import public_baseline as _vendor_baseline  # noqa: E402

message_type = _vendor_protocol.message_type
canonical_envelope = _vendor_protocol.canonical_envelope
signing_input = _vendor_protocol.signing_input
_ordered_message = _vendor_protocol._ordered_message
check_envelope_wire = _vendor_baseline.check_envelope_wire
check_public_envelope_structure = _vendor_baseline.check_public_envelope_structure
ENVELOPE_BASELINE = _vendor_baseline.ENVELOPE_BASELINE

# --- message constructors -------------------------------------------------

EventEnvelope = message_type("popclaw.event.EventEnvelope")
SignedPayload = message_type("popclaw.identity.SignedPayload")
ActorInfo = message_type("popclaw.identity.ActorInfo")
Recipient = message_type("popclaw.event.Recipient")
HouseEvent = message_type("popclaw.event.HouseEvent")
IntentPayload = message_type("popclaw.event.IntentPayload")
DirectMessageBody = message_type("popclaw.event.DirectMessage")
PostBody = message_type("popclaw.event.Post")
ProfileBody = message_type("popclaw.profile.Profile")
RequestCore = message_type("popclaw.housesession.RequestCore")
HouseSessionRequest = message_type("popclaw.housesession.HouseSessionRequest")
AckCore = message_type("popclaw.housesession.AckCore")
HouseSessionAck = message_type("popclaw.housesession.HouseSessionAck")
SessionInfo = message_type("popclaw.housesession.SessionInfo")
HouseBinding = message_type("popclaw.world.HouseBinding")
IntentContext = message_type("popclaw.world.IntentContext")
ManifestProof = message_type("popclaw.world.ManifestProof")
ActionResult = message_type("popclaw.world.ActionResult")
SignedActionResult = message_type("popclaw.world.SignedActionResult")
ActionStatusRequest = message_type("popclaw.world.ActionStatusRequest")
ActionStatusResponse = message_type("popclaw.world.ActionStatusResponse")
WorldStreamFrame = message_type("popclaw.event.WorldStreamFrame")
WorldStreamBoundary = message_type("popclaw.world.WorldStreamBoundary")
WorldStreamCheckpoint = message_type("popclaw.world.WorldStreamCheckpoint")
WorldStreamGap = message_type("popclaw.world.WorldStreamGap")
PublicStreamBoundary = message_type("popclaw.world.PublicStreamBoundary")
PublicStreamCheckpoint = message_type("popclaw.world.PublicStreamCheckpoint")
PublicStreamGap = message_type("popclaw.world.PublicStreamGap")
ScopeThrough = message_type("popclaw.world.ScopeThrough")

# --- signing domains (SIGNING.md) -----------------------------------------

DOMAIN_SESSION_REQUEST = "POPCLAW_HOUSE_SESSION_REQUEST_V1"
DOMAIN_SESSION_ACK = "POPCLAW_HOUSE_SESSION_ACK_V1"
DOMAIN_MANIFEST_PROOF = "POPCLAW_WORLD_MANIFEST_PROOF_V1"
DOMAIN_ACTION_RESULT = "POPCLAW_WORLD_ACTION_RESULT_V1"
DOMAIN_ACTION_STATUS_READ = "POPCLAW_WORLD_ACTION_STATUS_READ_V1"

# --- limits (LIMITS.md) ----------------------------------------------------

L_MANIFEST_MAX_BYTES = 262_144
L_GUIDE_MAX_BYTES = 524_288
L_PARAMS_MAX_BYTES = 16_384
L_RESULT_BODY_MAX_BYTES = 32_768
# 1572864 since .01.4 (LIMITS.md); the vendored guard is the single source.
L_ENVELOPE_MAX_BYTES = _vendor_baseline.L_ENVELOPE_MAX_BYTES

# Four DISTINCT ceilings, deliberately not one number. LIMITS.md bounds the
# raw EventEnvelope; everything below is a transport consequence of it, and
# none of them is a licence to treat the protocol limit as the ceiling for
# any particular business content (params, result bodies, the manifest and
# the guide keep their own much smaller limits above).
#
#   envelope  L_ENVELOPE_MAX_BYTES — raw EventEnvelope bytes.
#   wrapper   the SignedPayload carrying it: the envelope plus a 32-byte
#             signer key, a 64-byte signature and their field framing.
#   SSE frame base64 of the WHOLE WorldStreamFrame (4/3) plus the event
#             and data line framing — the envelope alone understates it,
#             see L_STREAM_FRAME_MAX_BYTES below.
#   page      up to L_STREAM_PAGE_MAX_EVENTS frames are validated and
#             buffered before any of a page is emitted, so a page's cost is
#             the frame ceiling times the requested limit.
L_SIGNED_PAYLOAD_MAX_BYTES = L_ENVELOPE_MAX_BYTES + 128

L_JSON_MAX_DEPTH = 8
L_SCOPES_MAX = 32
L_INITIAL_SCOPES_MAX = 8
L_STREAM_PAGE_MAX_EVENTS = 512
L_STATUS_QUERY_TTL_MAX_SECONDS = 300

# Public-stream membership limits the vendored predicate enforces, named
# here because the frame ceiling below is derived from them.
L_KIND_MAX_BYTES = 128
L_SCOPE_ID_MAX_BYTES = 64

# A delivered frame is NOT just the envelope: WorldStreamFrame also carries
# seq, the routing kind and the public scopes, and every one of those has
# its own worst case. Deriving the ceiling from the envelope alone
# understates it by the metadata — a 128-byte kind even takes a two-byte
# length varint, not one.
_FRAME_SEQ_MAX_BYTES = 1 + 10                       # tag + uint64 varint
_FRAME_ENVELOPE_MAX_BYTES = 1 + 3 + L_ENVELOPE_MAX_BYTES   # tag + len + bytes
_FRAME_KIND_MAX_BYTES = 1 + 2 + L_KIND_MAX_BYTES    # tag + len varint + utf-8
_FRAME_SCOPES_MAX_BYTES = L_SCOPES_MAX * (1 + 1 + L_SCOPE_ID_MAX_BYTES)
L_STREAM_FRAME_MAX_BYTES = (_FRAME_SEQ_MAX_BYTES + _FRAME_ENVELOPE_MAX_BYTES
                            + _FRAME_KIND_MAX_BYTES + _FRAME_SCOPES_MAX_BYTES)

# The largest `event: public_frame` chunk this server can put on the wire:
# the frame above, base64 (4/3 rounded up to a 4-byte group), inside the
# SSE event/data line framing.
_SSE_PUBLIC_FRAME_ENVELOPE = "event: public_frame\ndata: \n\n"
L_SSE_FRAME_MAX_BYTES = (((L_STREAM_FRAME_MAX_BYTES + 2) // 3) * 4
                         + len(_SSE_PUBLIC_FRAME_ENVELOPE))

# Session lease timing (G0 house-session contract).
SESSION_LEASE_SECONDS = 90
SESSION_RENEW_INTERVAL_SECONDS = 30
SESSION_REQUEST_WINDOW_SECONDS = 120
INBOX_TOKEN_TTL_SECONDS = 300
LEGACY_INBOX_WINDOW_SECONDS = 60


# --- canonical helpers -----------------------------------------------------


def canonical_core(message: Any) -> bytes:
    """Canonical protobuf core bytes for a map-free control/result message.

    Same recipe as the bridge's ``canonical_envelope`` minus the
    envelope-specific field clearing: deterministic serialization, then
    string-map entries reordered by UTF-8 key bytes (the retained golden
    vectors pin these exact bytes).
    """
    return _ordered_message(
        message.SerializeToString(deterministic=True), message.DESCRIPTOR
    )


def envelope_cid(envelope_bytes: bytes) -> str:
    """SHA-256 lowercase hex of the envelope's canonical core."""
    import hashlib

    envelope = EventEnvelope.FromString(envelope_bytes)
    core = canonical_envelope(envelope)
    return hashlib.sha256(core).hexdigest()


def envelope_canonical_bytes(envelope_bytes: bytes) -> bytes:
    envelope = EventEnvelope.FromString(envelope_bytes)
    return canonical_envelope(envelope)


# --- base58 identity --------------------------------------------------------

_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BASE58_INDEX = {char: index for index, char in enumerate(_BASE58_ALPHABET)}


def base58_encode(raw: bytes) -> str:
    number = int.from_bytes(raw, "big")
    encoded = ""
    while number > 0:
        number, remainder = divmod(number, 58)
        encoded = _BASE58_ALPHABET[remainder] + encoded
    for byte in raw:
        if byte == 0:
            encoded = "1" + encoded
        else:
            break
    return encoded or "1"


def base58_decode(text: str) -> bytes:
    number = 0
    for char in text:
        if char not in _BASE58_INDEX:
            raise ValueError("invalid base58 character")
        number = number * 58 + _BASE58_INDEX[char]
    raw = number.to_bytes((number.bit_length() + 7) // 8, "big") if number else b""
    leading = 0
    for char in text:
        if char == "1":
            leading += 1
        else:
            break
    return b"\x00" * leading + raw


def popclaw_id_from_key(public_key_bytes: bytes) -> str:
    """A popclaw_id is Bitcoin-base58 of exactly 32 Ed25519 public-key bytes."""
    if len(public_key_bytes) != 32:
        raise ValueError("public key must be exactly 32 bytes")
    return base58_encode(public_key_bytes)


def key_bytes_from_popclaw_id(popclaw_id: str) -> bytes:
    """Decode a popclaw_id, enforcing the exact 32-byte key length."""
    raw = base58_decode(popclaw_id)
    if len(raw) != 32:
        raise ValueError("popclaw_id must decode to exactly 32 bytes")
    return raw


# --- Ed25519 helpers --------------------------------------------------------


def verify_ed25519(public_key_bytes: bytes, signature: bytes, message: bytes) -> bool:
    if len(public_key_bytes) != 32:
        return False
    try:
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(signature, message)
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False


def sign_ed25519(private_key: Ed25519PrivateKey, message: bytes) -> bytes:
    return private_key.sign(message)


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64decode_strict(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"), validate=True)


# --- envelope body routing ---------------------------------------------------

BODY_TAGS = {
    11: "invite_request",
    12: "quest_dispatch",
    13: "quest_result",
    14: "invite_verified",
    15: "ranger_registration",
    16: "watch_dispatch",
    17: "watch_heartbeat",
    18: "watch_cancel",
    20: "follow_declared",
    21: "follow_revoked",
    25: "reply",
    26: "direct_message",
    27: "post",
    28: "profile",
    30: "mark",
    31: "mark_revoked",
    32: "poll_dispatch",
    33: "poll_report",
    34: "house_event",
    35: "intent",
}

# PUBLIC-STREAM.md membership table: tags never eligible for the public log.
NEVER_PUBLIC_TAGS = {26, 30, 31, 32, 17, 35}
# Mirrors the sealed bundle's public-eligibility predicate. Tags 20/21 left
# this set in `.01.6`: a relation original is never a public fact. Keeping
# the mirror honest matters because eligibility and delivery are separate
# decisions; see RELATION_TAGS.
PUBLIC_ELIGIBLE_TAGS = {11, 12, 13, 14, 15, 16, 18, 25, 27, 28, 33, 34}

# Relation originals. A follow or unfollow is a PERSONAL event: RELATIONS.md
# section 8 owes it to the two participants' personal streams and to no
# public lane, and FollowType.PUBLIC describes the relation's nature rather
# than conferring a public-stream right. Relation admission and personal
# delivery are implemented separately from every public exit. The two
# now agree — `.01.6` dropped these tags from the sealed predicate too —
# but they answer different questions, and this server must not depend on
# the sealed answer: a stored relation original has to stay a WITHHELD row
# rather than become an invalid public row that closes every reader's
# connection. The vendored guard still decodes and structurally validates
# these envelopes, so the generic wire capability is retained.
RELATION_TAGS = {20, 21}


class WireError(ValueError):
    """Structural wire rejection (guarded before any lossy decode)."""


def guard_envelope(envelope_bytes: bytes) -> int:
    """Bounded structural guard; returns the envelope body tag."""
    try:
        return check_envelope_wire(envelope_bytes)
    except ValueError as exc:
        raise WireError(str(exc)) from None


def guard_public_structure(envelope_bytes: bytes) -> int:
    """Structural + public privacy predicate; returns the body tag."""
    try:
        return check_public_envelope_structure(envelope_bytes)
    except ValueError as exc:
        raise WireError(str(exc)) from None
