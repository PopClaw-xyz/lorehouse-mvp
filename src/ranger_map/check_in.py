"""The one business rule: ``rangermap.check_in`` (leave a footprint).

This module owns parameter validation and the accepted-footprint projection.
It is deliberately protocol-agnostic: the trusted context (verified identity,
event CID) is produced by the protocol adapter, or constructed directly by
domain unit tests. It is never exposed as an unsigned HTTP write.

Field rules (schema_version 1, additionalProperties=false):

- ``place``     UTF-8 string, 1-60 code points after trimming, no control
                characters.
- ``latitude``  decimal string in [-90, 90], at most four fractional digits.
- ``longitude`` decimal string in [-180, 180], at most four fractional digits.
- ``status``    UTF-8 string, 1-160 code points after trimming, no newlines
                or control characters.

The pinned action-kind schema profile supports integers but not floating
point numbers or negative numeric bounds, so coordinates are bounded decimal
strings; the server validates ranges with ``Decimal`` and normalises
trailing zeros and ``-0`` for the stored projection without ever touching the
original signed bytes. Longitude 180 renders at the same spot as -180 on the
map; the stored value keeps what was signed.

Raw business JSON is at most 4 KiB with nesting depth at most 8. Rejected:
malformed UTF-8, NaN/Infinity, duplicate JSON keys, non-objects, missing
fields, wrong types, unknown keys (an ``actor_id`` cannot smuggle in another
identity: author identity comes only from the verified context).
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from .errors import InvalidInput

ACTION_KIND = "rangermap.check_in"
SCHEMA_VERSION = 1

MAX_PARAMS_BYTES = 4096
MAX_JSON_DEPTH = 8

PLACE_MAX_CODEPOINTS = 60
STATUS_MAX_CODEPOINTS = 160

COORDINATE_PATTERN = re.compile(r"^-?(0|[1-9][0-9]{0,2})(\.[0-9]{1,4})?$")
COORDINATE_MAX_LENGTH = 9

# Bitcoin-alphabet base58: what a public PopClaw identity looks like on the
# wire. The protocol layer guarantees this for verified events; the business
# core re-checks so domain tests cannot smuggle impossible identities.
BASE58_PATTERN = re.compile(r"^[1-9A-HJ-NP-Za-km-z]+$")
RANGER_ID_MAX_LENGTH = 128
NICKNAME_MAX_CODEPOINTS = 60

EVENT_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_FIELDS = ("place", "latitude", "longitude", "status")


# ---------------------------------------------------------------------------
# Value objects


@dataclass(frozen=True)
class CheckInParams:
    """Validated, normalised business parameters of one check-in."""

    place: str
    latitude: str
    longitude: str
    status: str


@dataclass(frozen=True)
class TrustedCheckInContext:
    """Facts a verified protocol adapter (or a domain test) asserts.

    ``ranger_id``      base58 public identity of the signing ranger.
    ``nickname``       display-name snapshot available for this request, or
                       ``None`` to fall back to a short identity label.
    ``source_event_id`` verified event CID (SHA-256, lowercase hex); the
                       idempotency key of the business effect.
    """

    ranger_id: str
    nickname: str | None
    source_event_id: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.ranger_id, str)
            or not 1 <= len(self.ranger_id) <= RANGER_ID_MAX_LENGTH
            or not BASE58_PATTERN.match(self.ranger_id)
        ):
            raise InvalidInput("ranger_id must be a base58 public identity")
        if (
            not isinstance(self.source_event_id, str)
            or not EVENT_ID_PATTERN.match(self.source_event_id)
        ):
            raise InvalidInput("source_event_id must be 64 lowercase hex characters")
        if self.nickname is not None:
            if (
                not isinstance(self.nickname, str)
                or not 1 <= len(self.nickname) <= NICKNAME_MAX_CODEPOINTS
                or _has_surrogate(self.nickname)
                or _has_control_character(self.nickname)
            ):
                raise InvalidInput("nickname must be 1-60 code points without control characters")

    @property
    def display_nickname(self) -> str:
        if self.nickname:
            return self.nickname
        return short_identity(self.ranger_id)


@dataclass(frozen=True)
class Footprint:
    """An immutable accepted check-in as exposed by the read models."""

    seq: int
    source_event_id: str
    ranger_id: str
    nickname: str
    place: str
    latitude: str
    longitude: str
    status: str
    accepted_at_ms: int

    @property
    def accepted_at(self) -> str:
        return format_iso_utc_ms(self.accepted_at_ms)

    def to_json_dict(self) -> dict:
        return {
            "seq": str(self.seq),
            "source_event_id": self.source_event_id,
            "ranger_id": self.ranger_id,
            "nickname": self.nickname,
            "place": self.place,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "accepted_at": self.accepted_at,
        }


@dataclass(frozen=True)
class ApplyResult:
    footprint: Footprint
    duplicate: bool


# ---------------------------------------------------------------------------
# Validation


def short_identity(ranger_id: str) -> str:
    """Stable short label distinguishing same-name rangers."""
    return ranger_id[:8] + "…"


def format_iso_utc_ms(accepted_at_ms: int) -> str:
    seconds, millis = divmod(int(accepted_at_ms), 1000)
    from datetime import datetime, timezone

    moment = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%S") + f".{millis:03d}Z"


def _has_control_character(text: str) -> bool:
    return any(unicodedata.category(ch) in ("Cc", "Cf") or ord(ch) < 0x20 or ord(ch) == 0x7F
               for ch in text)


def _has_surrogate(text: str) -> bool:
    """Lone surrogates decode from valid UTF-8 JSON escapes but cannot be
    encoded back to UTF-8 for storage; reject them with a defined error."""
    return any(0xD800 <= ord(ch) <= 0xDFFF for ch in text)


def _reject_constant(token: str):  # pragma: no cover - defensive
    raise InvalidInput(f"non-finite numbers are not valid parameters: {token}")


def _object_pairs(pairs):
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise InvalidInput(f"duplicate JSON key: {key}")
        seen.add(key)
    return dict(pairs)


def _measure_depth(value) -> int:
    """Iterative depth measurement: no recursion on hostile nesting."""
    max_depth = 0
    stack = [(value, 1)]
    while stack:
        current, depth = stack.pop()
        max_depth = max(max_depth, depth)
        if isinstance(current, dict):
            stack.extend((v, depth + 1) for v in current.values())
        elif isinstance(current, list):
            stack.extend((v, depth + 1) for v in current)
    return max_depth


def _validate_text_field(raw, field: str, max_codepoints: int) -> str:
    if not isinstance(raw, str):
        raise InvalidInput(f"{field} must be a string")
    if _has_surrogate(raw):
        raise InvalidInput(f"{field} must not contain surrogate code points")
    if _has_control_character(raw):
        raise InvalidInput(f"{field} must not contain control characters")
    trimmed = raw.strip()
    if not 1 <= len(trimmed) <= max_codepoints:
        raise InvalidInput(
            f"{field} must be 1-{max_codepoints} code points after trimming"
        )
    return trimmed


def _normalise_coordinate(raw, field: str, low: Decimal, high: Decimal) -> str:
    if not isinstance(raw, str):
        raise InvalidInput(f"{field} must be a decimal string")
    if len(raw) > COORDINATE_MAX_LENGTH or not COORDINATE_PATTERN.match(raw):
        raise InvalidInput(
            f"{field} must be a decimal string with at most four fractional digits"
        )
    try:
        value = Decimal(raw)
    except InvalidOperation:  # pragma: no cover - regex already excludes this
        raise InvalidInput(f"{field} is not a valid decimal number") from None
    if not low <= value <= high:
        raise InvalidInput(f"{field} must be between {low} and {high}")
    normalised = value.normalize()
    if normalised == 0:
        normalised = Decimal(0)  # collapses -0 and 0.0000
    text = format(normalised, "f")
    if text.startswith("-0") and Decimal(text) == 0:  # pragma: no cover - defensive
        text = text[1:]
    return text


def validate_check_in_params(raw: bytes) -> CheckInParams:
    """Strictly validate raw check-in parameter bytes (schema_version 1)."""
    if not isinstance(raw, (bytes, bytearray)):
        raise InvalidInput("check-in parameters must be raw bytes")
    if len(raw) > MAX_PARAMS_BYTES:
        raise InvalidInput(f"check-in parameters exceed {MAX_PARAMS_BYTES} bytes")
    try:
        text = bytes(raw).decode("utf-8")
    except UnicodeDecodeError:
        raise InvalidInput("check-in parameters must be valid UTF-8") from None
    try:
        document = json.loads(
            text,
            object_pairs_hook=_object_pairs,
            parse_constant=_reject_constant,
        )
    except InvalidInput:
        raise
    except RecursionError:
        # Deeply nested hostile input inside the 4 KiB budget must fail
        # deterministically as invalid input, never as an internal error.
        raise InvalidInput("check-in parameters nest too deeply") from None
    except ValueError:
        raise InvalidInput("check-in parameters must be a single JSON object") from None
    if not isinstance(document, dict):
        raise InvalidInput("check-in parameters must be a JSON object")
    if _measure_depth(document) > MAX_JSON_DEPTH:
        raise InvalidInput(f"check-in parameters nest deeper than {MAX_JSON_DEPTH}")
    unknown = set(document) - set(REQUIRED_FIELDS)
    if unknown:
        raise InvalidInput(
            "unknown check-in fields are rejected: " + ", ".join(sorted(unknown))
        )
    missing = [field for field in REQUIRED_FIELDS if field not in document]
    if missing:
        raise InvalidInput("missing required fields: " + ", ".join(missing))
    return CheckInParams(
        place=_validate_text_field(document["place"], "place", PLACE_MAX_CODEPOINTS),
        latitude=_normalise_coordinate(document["latitude"], "latitude", Decimal(-90), Decimal(90)),
        longitude=_normalise_coordinate(document["longitude"], "longitude", Decimal(-180), Decimal(180)),
        status=_validate_text_field(document["status"], "status", STATUS_MAX_CODEPOINTS),
    )


# ---------------------------------------------------------------------------
# Application (the business transaction)


def apply_check_in(store, context: TrustedCheckInContext, raw_params: bytes,
                   *, in_tx: bool = False) -> ApplyResult:
    """Apply one verified ``rangermap.check_in`` atomically.

    The event row and the footprint projection land in one SQLite
    transaction. Retrying a completed request returns the original immutable
    footprint with ``duplicate=True`` and changes nothing. A new event CID is
    a new trace, even with identical content.

    ``in_tx=True`` runs inside the caller's already-open write transaction
    (the protocol action path commits envelope evidence, footprint, public
    fact and signed result together); the domain default owns its own
    transaction.
    """
    existing = store.footprint_by_event(context.source_event_id)
    if existing is not None:
        return ApplyResult(footprint=existing, duplicate=True)

    params = validate_check_in_params(raw_params)

    def _work() -> ApplyResult:
        # Re-check under the write lock so a concurrent same-CID apply
        # cannot slip through the read check above.
        existing = store.footprint_by_event(context.source_event_id)
        if existing is not None:
            return ApplyResult(footprint=existing, duplicate=True)
        store.insert_event(
            event_id=context.source_event_id,
            raw_bytes=bytes(raw_params),
            kind=ACTION_KIND,
        )
        footprint = store.insert_footprint(
            source_event_id=context.source_event_id,
            ranger_id=context.ranger_id,
            nickname_snapshot=context.display_nickname,
            params=params,
        )
        return ApplyResult(footprint=footprint, duplicate=False)

    if in_tx:
        return _work()
    with store.write_tx():
        return _work()
