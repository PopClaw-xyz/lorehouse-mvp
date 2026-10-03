"""House state: pinned manifest, guide, incarnations and restore.

The manifest is built once at first boot of a data root and pinned verbatim
in ``house_meta``: its bytes are the ``capability_revision`` every signed
action context must quote, and its ``guide.sha256`` binds the exact guide
bytes served from ``/v1/guide.md`` (the guide is pinned alongside it, so a
later edit of the on-disk file never desynchronises the proof).

The data root is also bound to its canonical origin at first boot. Booting
the same data root under a different origin is refused: cross-origin replay
of old signed requests must fail closed rather than be silently reinterpreted.

An explicit restore rotates BOTH incarnation domains (server + public log),
retiring ids that must never be reused, rebuilding the manifest against the
new log identity and fencing every session and inbox token. Ordinary process
restarts change neither.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from . import wire
from .keys import HouseIdentity, digest_bytes, new_incarnation

GUIDE_RESOURCE = Path(__file__).parent / "static" / "house-guide.md"
GUIDE_REVISION = "rangermap-guide-2"
INITIAL_PUBLIC_SCOPES = ["rangermap"]
SLUG = "rangermap"
NAME = "PopClaw Ranger Map"

_PROFILE = "https://popclaw.example/world-interaction/schema-profile/v1"
_COORDINATE_PATTERN = "^-?(0|[1-9][0-9]{0,2})(\\.[0-9]{1,4})?$"
_NO_CONTROL_PATTERN = "^[^\\u0000-\\u001F\\u007F]*$"

# The unique action-kind declaration selected by world_interaction.actions.kinds
# (SPEC.md §2 rule 4). The schemas mirror the real business validation in
# check_in.py and the real Footprint projection exactly; the server enforces
# them authoritatively, the manifest states them for clients.
CHECK_IN_PARAMS_SCHEMA = {
    "$schema": _PROFILE,
    "title": "rangermap.check_in parameters v1",
    "description": (
        "One check-in: a self-chosen place, decimal-string coordinates and a"
        " one-line status. Strings are trimmed server-side; control characters"
        " and surrogate code points are rejected. latitude is within ±90 and"
        " longitude within ±180 (the server range-checks with Decimal); at"
        " most four fractional digits, no exponent notation, no leading"
        " zeros. Stored coordinates are normalised (trailing zeros, -0)."
    ),
    "type": "object",
    "properties": {
        "place": {
            "type": "string",
            "minLength": 1,
            "maxLength": 60,
            "pattern": _NO_CONTROL_PATTERN,
        },
        "latitude": {
            "type": "string",
            "minLength": 1,
            "maxLength": 9,
            "pattern": _COORDINATE_PATTERN,
        },
        "longitude": {
            "type": "string",
            "minLength": 1,
            "maxLength": 9,
            "pattern": _COORDINATE_PATTERN,
        },
        "status": {
            "type": "string",
            "minLength": 1,
            "maxLength": 160,
            "pattern": _NO_CONTROL_PATTERN,
        },
    },
    "required": ["place", "latitude", "longitude", "status"],
    "additionalProperties": False,
}

CHECK_IN_RESULT_SCHEMA = {
    "$schema": _PROFILE,
    "title": "rangermap.check_in result (Footprint) v1",
    "description": (
        "Immutable accepted check-in. seq is the house-local monotonic"
        " footprint sequence; source_event_id is the verified event CID;"
        " ranger_id is the signing ranger's base58 public identity;"
        " accepted_at is the server receive time, UTC ISO-8601 with"
        " milliseconds. Wide counters travel as decimal strings."
    ),
    "type": "object",
    "properties": {
        "seq": {"type": "string", "pattern": "^[1-9][0-9]*$"},
        "source_event_id": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "ranger_id": {
            "type": "string",
            "minLength": 32,
            "maxLength": 128,
            "pattern": "^[1-9A-HJ-NP-Za-km-z]+$",
        },
        "nickname": {"type": "string", "minLength": 1, "maxLength": 60},
        "place": {"type": "string", "minLength": 1, "maxLength": 60},
        "latitude": {
            "type": "string",
            "minLength": 1,
            "maxLength": 9,
            "pattern": _COORDINATE_PATTERN,
        },
        "longitude": {
            "type": "string",
            "minLength": 1,
            "maxLength": 9,
            "pattern": _COORDINATE_PATTERN,
        },
        "status": {"type": "string", "minLength": 1, "maxLength": 160},
        "accepted_at": {
            "type": "string",
            "pattern":
                "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
                "\\.[0-9]{3}Z$",
        },
    },
    "required": [
        "seq", "source_event_id", "ranger_id", "nickname", "place",
        "latitude", "longitude", "status", "accepted_at",
    ],
    "additionalProperties": False,
}

CHECK_IN_KIND_ROW = {
    "kind": "rangermap.check_in",
    "schema_version": 1,
    "transport": "house",
    "signer": "user",
    "description": (
        "Leave a footprint: submit a chosen place, bounded decimal-string"
        " coordinates and a one-line status. The map keeps one latest pin"
        " per signed identity and an immutable trail; the house commits a"
        " signed rangermap.checked_in public fact carrying the Footprint"
        " result and returns an immutable signed ActionResult."
    ),
    "params_schema": CHECK_IN_PARAMS_SCHEMA,
    "result_schema": CHECK_IN_RESULT_SCHEMA,
    "result_attachments": {"allowed": [], "required_on_success": []},
    "consistency": "none",
}

_META_ORIGIN = "origin"
_META_SERVER_INCARNATION = "server_incarnation"
_META_LOG_INCARNATION = "public_log_incarnation"
_META_RETIRED_SERVER = "retired_server_incarnations"
_META_RETIRED_LOGS = "retired_log_incarnations"
_META_HOUSE_REVISION = "house_revision"
_META_MANIFEST = "manifest_bytes"
_META_GUIDE = "guide_bytes"


class HouseStateError(Exception):
    """Refusable house-state condition (origin mismatch, corrupt pinning)."""


@dataclass
class HouseState:
    origin: str
    server_incarnation: str
    log_incarnation: str
    manifest_bytes: bytes
    guide_bytes: bytes
    house_revision: int

    @property
    def manifest_digest(self) -> str:
        return digest_bytes(self.manifest_bytes)

    @property
    def manifest_json(self) -> dict:
        return json.loads(self.manifest_bytes.decode("utf-8"))

    @property
    def registered_scopes(self) -> list[str]:
        return list(
            self.manifest_json["world_interaction"]["public_stream"][
                "initial_public_scopes"
            ]
        )


def _build_manifest(identity: HouseIdentity, log_incarnation: str,
                    guide_digest: str, guide_revision: str = GUIDE_REVISION) -> bytes:
    declared_kinds = [row["kind"] for row in [CHECK_IN_KIND_ROW]]
    manifest = {
        "name": NAME,
        "slug": SLUG,
        "official_ids": [identity.house_key_id],
        "guide_url": "/v1/guide.md",
        "intent_kinds": [CHECK_IN_KIND_ROW],
        "relations": {"ordered": 1},
        "read_auth": {"schemes": ["popclaw-identity-read-v2"]},
        "house_session": {
            "endpoint": "/v1/house-session",
            "version": 1,
            "operations": ["enter", "renew", "leave", "status"],
            "lease_seconds": wire.SESSION_LEASE_SECONDS,
            "renew_interval_seconds": wire.SESSION_RENEW_INTERVAL_SECONDS,
            "ack_pubkey": identity.ack_pubkey_hex,
        },
        "world_interaction": {
            "version": 1,
            "public_stream": {
                "endpoint": "/v1/world-stream",
                "mode": "public-v1",
                "log_incarnation": log_incarnation,
                "initial_public_scopes": INITIAL_PUBLIC_SCOPES,
                "envelope_baseline": wire.ENVELOPE_BASELINE,
            },
            "actions": {
                "status_endpoint": "/v1/world-actions/status",
                "result_authority_pubkey": identity.house_key_id,
                "kinds": declared_kinds,
                "attachments": [],
            },
            "guide": {
                "path": "/v1/guide.md",
                "sha256": guide_digest,
                "revision": guide_revision,
            },
        },
    }
    return json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


_ACTION_KIND_PATTERN = re.compile(r"^[a-z0-9]{1,24}(\.[a-z0-9_]{1,24}){1,2}$")

_RESTORE_MIGRATION = (
    "this data root's pinned manifest predates the intent_kinds declaration"
    " (SPEC.md section 2 rule 4: every actions.kinds entry must uniquely"
    " select a manifest.intent_kinds row). The pin is deliberately NOT"
    " silently mutated. Run `python tools/house_admin.py --restore"
    " --data-dir <dir> --origin <origin>` with the server stopped to rebuild"
    " the manifest (an explicit house restore rotates both incarnations per"
    " the public contract), or start a fresh data root."
)


def validate_action_declarations(manifest: dict) -> None:
    """Every world_interaction.actions.kinds entry must uniquely select a
    structurally valid manifest.intent_kinds row (action-kind.schema.json
    shape; SPEC.md section 2 rule 4). The server never serves a manifest
    advertising a capability it cannot back with a declared row."""
    board = manifest.get("world_interaction") or {}
    actions = board.get("actions")
    if not actions:
        return
    kinds = actions.get("kinds") or []
    rows = manifest.get("intent_kinds") or []
    for kind in kinds:
        if not isinstance(kind, str) or not _ACTION_KIND_PATTERN.fullmatch(kind):
            raise HouseStateError(f"actions.kinds entry is invalid: {kind!r}")
        selected = [row for row in rows if row.get("kind") == kind]
        if len(selected) != 1:
            raise HouseStateError(
                f"actions kind {kind!r} does not uniquely select a"
                f" manifest.intent_kinds row. {_RESTORE_MIGRATION}"
            )
        row = selected[0]
        required = {
            "kind", "schema_version", "transport", "signer", "description",
            "params_schema", "result_schema", "result_attachments",
            "consistency",
        }
        if set(row) != required:
            raise HouseStateError(
                f"intent_kinds row for {kind!r} does not match"
                f" action-kind.schema.json (additionalProperties=false)."
                f" {_RESTORE_MIGRATION}"
            )
        if row["schema_version"] != 1 or not isinstance(row["schema_version"], int):
            raise HouseStateError(
                f"intent_kinds row for {kind!r} has an unsupported"
                f" schema_version. {_RESTORE_MIGRATION}"
            )
        if row["transport"] != "house" or row["signer"] != "user":
            raise HouseStateError(
                f"intent_kinds row for {kind!r} declares an unimplemented"
                f" transport/signer. {_RESTORE_MIGRATION}"
            )
        attachments = row["result_attachments"]
        if (not isinstance(attachments, dict)
                or set(attachments) != {"allowed", "required_on_success"}
                or attachments["allowed"] != []
                or attachments["required_on_success"] != []):
            raise HouseStateError(
                f"intent_kinds row for {kind!r} declares attachments this"
                f" house does not implement. {_RESTORE_MIGRATION}"
            )
        if row["consistency"] != "none":
            raise HouseStateError(
                f"intent_kinds row for {kind!r} declares a consistency"
                f" promise this house does not implement. {_RESTORE_MIGRATION}"
            )


def load_or_setup(store, identity: HouseIdentity, origin: str) -> HouseState:
    """Load the pinned house state, initialising it on a fresh data root."""
    pinned_origin = store.get_meta(_META_ORIGIN)
    if pinned_origin is not None and pinned_origin != origin:
        raise HouseStateError(
            f"this data root is bound to origin {pinned_origin!r}; refusing to "
            f"serve as {origin!r}. Restart on the original origin or use a "
            "fresh data directory."
        )

    server_incarnation = store.get_meta(_META_SERVER_INCARNATION)
    if server_incarnation is None:
        guide_bytes = GUIDE_RESOURCE.read_bytes()
        if len(guide_bytes) > wire.L_GUIDE_MAX_BYTES:
            raise HouseStateError("bundled guide exceeds the guide size limit")
        log_incarnation = new_incarnation("rmlog")
        with store.write_tx():
            # Re-check under the write lock so concurrent first boots cannot
            # pin two different states.
            if store.get_meta(_META_SERVER_INCARNATION) is None:
                store.set_meta(_META_ORIGIN, origin)
                store.set_meta(_META_SERVER_INCARNATION, new_incarnation("rmserver"))
                store.set_meta(_META_LOG_INCARNATION, log_incarnation)
                store.set_meta(_META_RETIRED_SERVER, json.dumps([]))
                store.set_meta(_META_RETIRED_LOGS, json.dumps([]))
                store.set_meta(_META_HOUSE_REVISION, "0")
                store.set_meta(
                    _META_MANIFEST,
                    _build_manifest(identity, log_incarnation,
                                    digest_bytes(guide_bytes)).decode("utf-8"),
                )
                store.set_meta(_META_GUIDE, guide_bytes.decode("utf-8"))
            server_incarnation = store.get_meta(_META_SERVER_INCARNATION)

    manifest_bytes = store.get_meta(_META_MANIFEST).encode("utf-8")
    if len(manifest_bytes) > wire.L_MANIFEST_MAX_BYTES:
        raise HouseStateError("pinned manifest exceeds the manifest size limit")
    guide_bytes = store.get_meta(_META_GUIDE).encode("utf-8")
    parsed = json.loads(manifest_bytes)
    if digest_bytes(guide_bytes) != parsed["world_interaction"]["guide"]["sha256"]:
        raise HouseStateError(
            "pinned guide bytes do not match the pinned manifest digest"
        )
    # SPEC.md section 2 rule 4: an advertised actions kind without a unique,
    # structurally valid intent_kinds row is an unbacked capability — refuse
    # to serve it rather than weakening the board the client validates.
    validate_action_declarations(parsed)

    return HouseState(
        origin=origin,
        server_incarnation=server_incarnation,
        log_incarnation=store.get_meta(_META_LOG_INCARNATION),
        manifest_bytes=manifest_bytes,
        guide_bytes=guide_bytes,
        house_revision=int(store.get_meta(_META_HOUSE_REVISION) or "0"),
    )


def bundled_guide() -> bytes:
    """Validate the fixed package guide before any maintenance mutation."""
    try:
        content = GUIDE_RESOURCE.read_bytes()
        text = content.decode('utf-8')
    except (OSError, UnicodeError) as exc:
        raise HouseStateError('bundled guide is unreadable or not UTF-8') from exc
    if not text.strip() or '\0' in text or len(content) > wire.L_GUIDE_MAX_BYTES:
        raise HouseStateError('bundled guide is empty, invalid or exceeds the guide size limit')
    return content


def restore(store, identity: HouseIdentity, state: HouseState, *,
            refresh_guide: bool = False) -> HouseState:
    """Explicit house restore/rebuild: rotate both incarnations, fence all
    sessions and inbox tokens, retire ids forever, rebuild the manifest.

    Never invoked automatically (no HTTP route): an operator runs this via
    ``tools/house_admin.py --restore`` with the server stopped.
    """
    guide_bytes = bundled_guide() if refresh_guide else state.guide_bytes
    guide_revision = (GUIDE_REVISION if refresh_guide else
                      state.manifest_json['world_interaction']['guide']['revision'])
    with store.write_tx():
        retired_server = json.loads(store.get_meta(_META_RETIRED_SERVER) or "[]")
        retired_logs = json.loads(store.get_meta(_META_RETIRED_LOGS) or "[]")
        retired_server.append(store.get_meta(_META_SERVER_INCARNATION))
        retired_logs.append(store.get_meta(_META_LOG_INCARNATION))
        new_server = new_incarnation("rmserver")
        new_log = new_incarnation("rmlog")
        manifest = _build_manifest(identity, new_log, digest_bytes(guide_bytes), guide_revision)
        if len(manifest) > wire.L_MANIFEST_MAX_BYTES:
            raise HouseStateError('rebuilt manifest exceeds the manifest size limit')
        validate_action_declarations(json.loads(manifest))
        store.set_meta(_META_RETIRED_SERVER, json.dumps(retired_server))
        store.set_meta(_META_RETIRED_LOGS, json.dumps(retired_logs))
        store.set_meta(_META_SERVER_INCARNATION, new_server)
        store.set_meta(_META_LOG_INCARNATION, new_log)
        store.set_meta(
            _META_MANIFEST,
            manifest.decode("utf-8"),
        )
        store.set_meta(_META_GUIDE, guide_bytes.decode('utf-8'))
        # Fence every live session; the house_revision counter stays monotonic
        # (fences are never reused, even across restore).
        store.execute("UPDATE sessions SET active = 0, closed_ms = ?"
                      " WHERE active = 1", (store.clock_ms(),))
        store.execute("UPDATE inbox_tokens SET revoked = 1 WHERE revoked = 0")
        generation = int(store.get_meta("personal_generation")) + 1
        store.set_meta("personal_generation", str(generation))
        # Retain exact originals, recipient positions and counters. Published
        # obligations must stay reachable; relation snapshots do not recover
        # DMs. Pending obligations append after this preserved committed prefix.
        store.execute("UPDATE personal_log SET generation=?", (generation,))
    return load_or_setup(store, identity, state.origin)


def manifest_proof_bytes(identity: HouseIdentity, state: HouseState) -> bytes:
    """Fresh signed ManifestProof for the pinned manifest (response metadata)."""
    proof = wire.ManifestProof()
    proof.house.origin = state.origin
    proof.house.house_key = identity.house_key_id
    proof.house.incarnation = state.server_incarnation
    proof.manifest_digest = state.manifest_digest
    proof.signed_at = int(time.time())
    core = wire.canonical_core(proof)
    proof.authority_signature = identity.sign(
        wire.signing_input(wire.DOMAIN_MANIFEST_PROOF, core)
    )
    return proof.SerializeToString(deterministic=True)


def house_binding(identity: HouseIdentity, state: HouseState) -> wire.HouseBinding:
    binding = wire.HouseBinding()
    binding.origin = state.origin
    binding.house_key = identity.house_key_id
    binding.incarnation = state.server_incarnation
    return binding


def next_house_revision(store, in_tx: bool = False) -> int:
    """Allocate the next session-generation fence (monotonic, never reused).

    ``in_tx=True`` runs inside the caller's already-open write transaction.
    """
    if in_tx:
        current = int(store.get_meta(_META_HOUSE_REVISION) or "0")
        nxt = current + 1
        store.set_meta(_META_HOUSE_REVISION, str(nxt))
        return nxt
    with store.write_tx():
        current = int(store.get_meta(_META_HOUSE_REVISION) or "0")
        nxt = current + 1
        store.set_meta(_META_HOUSE_REVISION, str(nxt))
    return nxt


def retired_log_incarnations(store) -> list[str]:
    return json.loads(store.get_meta(_META_RETIRED_LOGS) or "[]")
