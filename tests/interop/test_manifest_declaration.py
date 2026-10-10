"""Focused regressions: the manifest's unique rangermap.check_in declaration.

SPEC.md section 2 rule 4 — every world_interaction.actions.kinds entry must
uniquely select a manifest.intent_kinds row governed by
action-kind.schema.json. The schemas must mirror the real business
validation and the real Footprint result; the pinned manifest/proof/
capability revision must cover the declaration; restart pinning is
deliberate and legacy roots migrate explicitly via house restore.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

import pytest

from ranger_map import house as house_mod
from ranger_map import wire
from ranger_map.check_in import validate_check_in_params
from ranger_map.house import HouseStateError

from tests.interop.wire_helpers import (
    Actor,
    check_in_intent,
    parse_ack,
    session_request,
    wrap_signed,
)

VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "popclaw-contracts"
ACTION_KIND_SCHEMA = json.loads(
    (VENDOR / "packages" / "contracts" / "protocol" / "public-envelope-02"
     / "action-kind.schema.json").read_text()
)

# --- declaration present and exactly right -----------------------------------


def test_manifest_declares_unique_intent_kinds_row(house):
    manifest = house.state.manifest_json
    rows = manifest["intent_kinds"]
    assert len(rows) == 1
    row = rows[0]
    assert row["kind"] == "rangermap.check_in"
    assert row["schema_version"] == 1
    assert row["transport"] == "house"
    assert row["signer"] == "user"
    assert isinstance(row["description"], str) and row["description"]
    assert row["result_attachments"] == {"allowed": [],
                                         "required_on_success": []}
    assert row["consistency"] == "none"
    # The actions board selects exactly the declared row.
    assert manifest["world_interaction"]["actions"]["kinds"] == [
        row["kind"] for row in rows
    ]


def test_row_matches_action_kind_schema_shape():
    row = house_mod.CHECK_IN_KIND_ROW
    properties = set(ACTION_KIND_SCHEMA["properties"])
    required = set(ACTION_KIND_SCHEMA["required"])
    # The schema allows exactly its declared properties and this row uses
    # exactly the required set (additionalProperties=false, no optionals).
    assert set(row) == required
    assert required <= properties
    assert re.fullmatch(
        ACTION_KIND_SCHEMA["properties"]["kind"]["pattern"], row["kind"])
    assert 1 <= row["schema_version"] <= 4294967295
    assert len(row["description"]) <= 2048


# --- embedded schemas conform to the pinned schema profile -------------------

_ALLOWED_KEYWORDS = {
    "title", "description", "$comment", "$schema", "type", "properties",
    "required", "additionalProperties", "items", "minItems", "maxItems",
    "uniqueItems", "maxProperties", "enum", "const", "minimum", "maximum",
    "exclusiveMinimum", "exclusiveMaximum", "minLength", "maxLength",
    "pattern", "allOf", "anyOf", "oneOf", "$ref", "$defs",
}
_ALLOWED_TYPES = {"object", "array", "string", "boolean", "integer"}


def _check_profile_node(node):
    assert set(node) <= _ALLOWED_KEYWORDS, set(node) - _ALLOWED_KEYWORDS
    if "type" in node:
        assert node["type"] in _ALLOWED_TYPES
    for name, sub in (node.get("properties") or {}).items():
        assert re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", name), name
        _check_profile_node(sub)
    for keyword in ("allOf", "anyOf", "oneOf"):
        for sub in node.get(keyword, []):
            _check_profile_node(sub)
    if "items" in node:
        _check_profile_node(node["items"])
    for sub in (node.get("$defs") or {}).values():
        _check_profile_node(sub)
    if "pattern" in node:
        assert 1 <= len(node["pattern"]) <= 256


@pytest.mark.parametrize("schema_name", ["params_schema", "result_schema"])
def test_embedded_schemas_fit_pinned_profile(schema_name):
    _check_profile_node(house_mod.CHECK_IN_KIND_ROW[schema_name])


# --- schemas mirror the real validation and result ----------------------------


def test_params_schema_matches_real_validation():
    good = {"place": "Hangzhou", "latitude": "30.27", "longitude": "120.15",
            "status": "Building a little music tool."}
    assert validate_check_in_params(
        json.dumps(good).encode()) .place == "Hangzhou"

    properties = house_mod.CHECK_IN_PARAMS_SCHEMA["properties"]
    # Cases the schema's own patterns reject must be rejected by the server.
    import copy

    bad_cases = [
        ("latitude", "1e5"), ("latitude", "030.1"), ("latitude", "30."),
        ("longitude", ".5"), ("longitude", "1234.0"),
        ("place", "line\nbreak"), ("status", "be\x07ll"),
    ]
    for field, value in bad_cases:
        assert not re.fullmatch(
            properties[field]["pattern"], value), (field, value)
        body = dict(good)
        body[field] = value
        with pytest.raises(Exception):
            validate_check_in_params(json.dumps(body).encode())

    # additionalProperties=false / required mirror unknown+missing rejects.
    with_unknown = dict(good, actor_id="8imposter")
    with pytest.raises(Exception):
        validate_check_in_params(json.dumps(with_unknown).encode())
    missing = {k: v for k, v in good.items() if k != "place"}
    with pytest.raises(Exception):
        validate_check_in_params(json.dumps(missing).encode())


def _matches(node, value) -> bool:
    if node.get("type") == "string" and not isinstance(value, str):
        return False
    if "pattern" in node and re.fullmatch(node["pattern"], value) is None:
        return False
    if "minLength" in node and len(value) < node["minLength"]:
        return False
    if "maxLength" in node and len(value) > node["maxLength"]:
        return False
    return True


def test_result_schema_matches_real_footprint(house):
    yun = Actor("Yun")
    ack = parse_ack(house.client.post(
        "/v1/house-session",
        content=session_request(yun, 1, 10)).content)
    payload = check_in_intent(
        yun, session_id=ack.core.session_id,
        fence=str(ack.core.house_revision),
        capability_revision=house.state.manifest_digest,
        house_key=house.identity.house_key_id,
        incarnation=house.state.server_incarnation)
    response = house.client.post("/v1/push", content=wrap_signed(payload, yun))
    assert response.status_code == 200, response.text
    signed = wire.SignedActionResult.FromString(
        base64.b64decode(response.json()["receipt_base64"]))
    footprint = json.loads(bytes(signed.result.result_body))

    schema = house_mod.CHECK_IN_RESULT_SCHEMA
    assert set(footprint) == set(schema["required"])  # no extra/missing keys
    for field, node in schema["properties"].items():
        assert _matches(node, footprint[field]), (field, footprint[field])


# --- proof / capability revision cover the declaration ------------------------


def test_manifest_proof_and_capability_revision_cover_declaration(house):
    response = house.client.get("/v1/manifest")
    body = response.content
    manifest = json.loads(body)
    assert "intent_kinds" in manifest

    digest = hashlib.sha256(body).hexdigest()
    assert digest == house.state.manifest_digest

    proof = wire.ManifestProof.FromString(
        base64.b64decode(response.headers["X-Popclaw-Manifest-Proof"]))
    assert proof.manifest_digest == digest
    core = wire.ManifestProof()
    core.house.CopyFrom(proof.house)
    core.manifest_digest = proof.manifest_digest
    core.signed_at = proof.signed_at
    assert wire.verify_ed25519(
        house.identity.public_key_bytes, bytes(proof.authority_signature),
        wire.signing_input(wire.DOMAIN_MANIFEST_PROOF,
                           wire.canonical_core(core)))

    # An IntentContext quoting this exact capability revision is admitted
    # end to end (covered fully above; here the digest equality is the link).
    assert manifest["world_interaction"]["actions"]["kinds"] == [
        "rangermap.check_in"]


def test_manifest_pinned_across_restart_with_declaration(house, tmp_path):
    from ranger_map.house import load_or_setup
    from ranger_map.store import Store

    before = house.state.manifest_bytes
    house.store.close()
    store = Store.open(tmp_path / "data")
    state2 = load_or_setup(store, house.identity, house.state.origin)
    assert state2.manifest_bytes == before  # deliberately restart-pinned
    assert "intent_kinds" in state2.manifest_json
    store.close()
    from ranger_map.keys import load_or_create_identity
    house.store = Store.open(tmp_path / "data")
    house.identity = load_or_create_identity(tmp_path / "data")


# --- legacy data roots migrate explicitly, never silently ---------------------


def _pin_legacy_manifest(store, identity, state):
    """Rewrite the pinned manifest without intent_kinds (pre-declaration)."""
    manifest = json.loads(state.manifest_bytes)
    manifest.pop("intent_kinds")
    with store.write_tx():
        store.set_meta("manifest_bytes", json.dumps(
            manifest, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False))


def test_legacy_manifest_fails_loudly_and_restores(house, tmp_path):
    from ranger_map.house import load_or_setup
    from ranger_map.store import Store

    _pin_legacy_manifest(house.store, house.identity, house.state)
    house.store.close()

    store = Store.open(tmp_path / "data")
    with pytest.raises(HouseStateError) as exc:
        load_or_setup(store, house.identity, house.state.origin)
    assert "house_admin.py --restore" in str(exc.value)

    # The documented migration: an explicit restore rebuilds the manifest
    # with the declaration (rotating both incarnations per the contract).
    restored = house_mod.restore(store, house.identity, house.state)
    assert "intent_kinds" in restored.manifest_json
    assert restored.manifest_digest != house.state.manifest_digest
    assert restored.log_incarnation != house.state.log_incarnation
    store.close()
    from ranger_map.keys import load_or_create_identity
    house.store = Store.open(tmp_path / "data")
    house.identity = load_or_create_identity(tmp_path / "data")


def test_duplicate_or_mismatched_rows_are_refused(house):
    manifest = house.state.manifest_json
    with pytest.raises(HouseStateError):
        doubled = json.loads(json.dumps(manifest))
        doubled["intent_kinds"].append(doubled["intent_kinds"][0])
        house_mod.validate_action_declarations(doubled)
    with pytest.raises(HouseStateError):
        unbacked = json.loads(json.dumps(manifest))
        unbacked["world_interaction"]["actions"]["kinds"].append(
            "rangermap.other")
        house_mod.validate_action_declarations(unbacked)
    with pytest.raises(HouseStateError):
        bad_attachments = json.loads(json.dumps(manifest))
        bad_attachments["intent_kinds"][0]["result_attachments"] = {
            "allowed": ["snapshot"], "required_on_success": []}
        house_mod.validate_action_declarations(bad_attachments)
