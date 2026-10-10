"""Interop layer 1: the consumed contract bundle is the trusted pin, and the
shared vectors pass through THIS server's bridge import exactly as shipped."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

import pytest

from ranger_map import wire

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR = REPO_ROOT / "vendor" / "popclaw-contracts"
FIXTURES = VENDOR / "packages" / "contracts" / "fixtures"

NEW = json.loads((FIXTURES / "public-baseline.json").read_text())
OLD = json.loads((FIXTURES / "test-vectors.json").read_text())
GOLDEN = json.loads((FIXTURES / "retained-signing-golden.json").read_text())


def test_vendor_pin_matches_trusted_digest():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "vendor_verify_contracts.py")],
        capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert "273 files verified" in result.stdout
    assert wire.__file__  # bridge imported from the same vendored tree


def test_vendored_bridge_suite_passes_in_our_venv():
    """The bundle's own Python parity suite runs unchanged here (27 tests)."""
    runner = unittest.TextTestRunner(stream=open("/dev/null", "w"))
    loader = unittest.TestLoader()
    suite = loader.discover(str(VENDOR / "packages" / "contracts" / "python"),
                            pattern="test_*.py")
    result = runner.run(suite)
    assert result.testsRun == 27, result.testsRun
    assert len(result.failures) == 0 and len(result.errors) == 0


@pytest.mark.parametrize("row", NEW["wire"], ids=lambda row: row["name"])
def test_wire_matrix_through_server_guard(row):
    raw = bytes.fromhex(row["wire_hex"])
    if row["structural"]:
        wire.check_envelope_wire(raw)
    else:
        with pytest.raises(ValueError):
            wire.check_envelope_wire(raw)


def test_signed_vectors_cid_and_signatures():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    for row in NEW["signed"]:
        raw = bytes.fromhex(row["wire_hex"])
        envelope = wire.EventEnvelope.FromString(raw)
        canonical = wire.canonical_envelope(envelope)
        assert canonical.hex() == row["canonical_hex"]
        assert hashlib.sha256(canonical).hexdigest() == row["cid"]
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(row["public_key_hex"]))
        key.verify(envelope.signature, canonical)
        # The wrapper signature covers the exact payload bytes.
        wrapper = wire.SignedPayload.FromString(bytes.fromhex(row["signed_payload_hex"]))
        assert wrapper.payload == raw
        key.verify(wrapper.signature, wrapper.payload)


def test_session_cores_use_exact_domains():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    for group, ty, domain in [
        ("requests", "RequestCore", wire.DOMAIN_SESSION_REQUEST),
        ("acks", "AckCore", wire.DOMAIN_SESSION_ACK),
    ]:
        for row in OLD["house_session"][group]:
            raw = bytes.fromhex(row["canonical_bytes_hex"])
            message = getattr(
                wire, f"{'Request' if group == 'requests' else 'Ack'}Core"
            ).FromString(raw)
            assert message.SerializeToString(deterministic=True) == raw
            key = Ed25519PublicKey.from_public_bytes(
                bytes.fromhex(row["signer_pubkey_hex"]))
            signed = bytes.fromhex(row["signing_input_hex"])
            assert signed == domain.encode() + raw
            key.verify(bytes.fromhex(row["signature_hex"]), signed)


def test_retained_world_signing_domains():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    for row in GOLDEN["vectors"]:
        raw = bytes.fromhex(row["signed_core_bytes_hex"])
        message = wire.message_type("popclaw.world." + row["type"]).FromString(raw)
        assert message.SerializeToString(deterministic=True) == raw
        assert hashlib.sha256(raw).hexdigest() == row["sha256"]
        key = Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(row["signer_public_key_hex"]))
        key.verify(bytes.fromhex(row["signature_hex"]),
                   row["domain"].encode() + raw)


def test_canonical_core_matches_deterministic_for_mapless_messages():
    core = wire.AckCore()
    core.house_origin = "http://127.0.0.1:8787"
    core.popclaw_id = "1A2b9CdefGhijkmnPqrsTuvwxYz23456"
    core.op_seq = 7
    assert (wire.canonical_core(core)
            == core.SerializeToString(deterministic=True))
