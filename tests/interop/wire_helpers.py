"""Shared helpers for native wire tests: isolated keys and signed traffic.

Every identity here is generated fresh in-process (isolated test keys); no
real host, user identity or master key is ever touched. DM ciphertext uses
the identity-derived X25519/NaCl box convention via PyNaCl exactly as the
envelope schema describes.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import sys
import time
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(REPO_ROOT), str(REPO_ROOT / "src")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from ranger_map import wire  # noqa: E402


class Actor:
    """An isolated test identity."""

    def __init__(self, nickname: str = "Ranger"):
        self.private_key = Ed25519PrivateKey.from_private_bytes(
            secrets.token_bytes(32))
        self.public_key_bytes = self.private_key.public_key().public_bytes_raw()
        self.popclaw_id = wire.popclaw_id_from_key(self.public_key_bytes)
        self.nickname = nickname

    def sign(self, message: bytes) -> bytes:
        return self.private_key.sign(message)


ORIGIN = "http://127.0.0.1:8787"


def build_envelope(actor: Actor, body_setter, timestamp: int | None = None,
                   lorehouse: str = "", target=None) -> "wire.EventEnvelope":
    envelope = wire.EventEnvelope()
    envelope.actor.popclaw_id = actor.popclaw_id
    envelope.actor.nickname = actor.nickname
    envelope.timestamp = timestamp if timestamp is not None else int(time.time())
    if lorehouse:
        envelope.lorehouse = lorehouse
    if target is not None:
        envelope.target.CopyFrom(target)
    body_setter(envelope)
    return envelope


def signed_envelope_bytes(envelope, actor: Actor) -> bytes:
    """Compute the canonical core once (event_id/signature cleared), set the
    CID from it, sign that same core, and return the wire bytes."""
    envelope.ClearField("event_id")
    envelope.ClearField("signature")
    canonical = wire.canonical_envelope(envelope)
    envelope.event_id = hashlib.sha256(canonical).hexdigest()
    envelope.signature = actor.sign(canonical)
    return envelope.SerializeToString(deterministic=True)


def wrap_signed(envelope_bytes: bytes, actor: Actor) -> bytes:
    wrapper = wire.SignedPayload()
    wrapper.payload = envelope_bytes
    wrapper.signer_pubkey = actor.public_key_bytes
    wrapper.signature = actor.sign(envelope_bytes)
    return wrapper.SerializeToString(deterministic=True)


def make_post(actor: Actor, text: str = "Hello from the wire tests.") -> bytes:
    def set_body(envelope):
        block = envelope.post.blocks.add()
        block.block_type = 0
        block.content = text

    return signed_envelope_bytes(build_envelope(actor, set_body), actor)


def make_profile(actor: Actor, nickname: str, intro: str = "") -> bytes:
    def set_body(envelope):
        envelope.profile.nickname = nickname
        if intro:
            envelope.profile.one_line_intro = intro
        envelope.profile.declared_at = int(time.time())

    return signed_envelope_bytes(build_envelope(actor, set_body), actor)


def make_house_event(actor: Actor, kind: str, body: bytes,
                     scopes: list[str] | None = None) -> bytes:
    def set_body(envelope):
        envelope.house_event.kind = kind
        envelope.house_event.schema_version = 1
        envelope.house_event.body = body
        if scopes:
            envelope.house_event.public_scopes.extend(scopes)

    return signed_envelope_bytes(build_envelope(actor, set_body), actor)


def make_dm(sender: Actor, recipient: Actor, text: str) -> bytes:
    """Encrypted DM using the identity-derived X25519/NaCl box convention."""
    from nacl import bindings
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    recipient_ed = wire.key_bytes_from_popclaw_id(recipient.popclaw_id)
    ed_pub = Ed25519PublicKey.from_public_bytes(recipient_ed)
    raw = ed_pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
    curve = bindings.crypto_sign_ed25519_pk_to_curve25519(raw)

    nonce = secrets.token_bytes(24)
    ciphertext = bindings.crypto_box(text.encode("utf-8"), nonce, curve,
                                     _sender_sk(sender))
    def set_body(envelope):
        envelope.direct_message.from_popclaw_id = sender.popclaw_id
        envelope.direct_message.to_popclaw_id = recipient.popclaw_id
        envelope.direct_message.body = "(encrypted)"
        envelope.direct_message.ts = int(time.time())
        envelope.direct_message.ciphertext = ciphertext
        envelope.direct_message.nonce = nonce
        target = wire.Recipient()
        target.scope = 1  # PRIVATE
        target.target_ids.append(recipient.popclaw_id)
        envelope.target.CopyFrom(target)

    return signed_envelope_bytes(build_envelope(sender, set_body), sender)


def _sender_sk(sender: Actor) -> bytes:
    """NaCl box private key for the sender (fresh ephemeral for tests)."""
    from nacl.public import PrivateKey

    return bytes(PrivateKey.generate())


def session_request(actor: Actor, operation: int, op_seq: int, *,
                    installation: str = "install-test-1",
                    request_id: str | None = None,
                    target_session: str = "", origin: str = ORIGIN,
                    expected_revision: int = 0,
                    issued_at: int | None = None,
                    expires_at: int | None = None,
                    nonce: str | None = None) -> bytes:
    core = wire.RequestCore()
    core.operation = operation
    core.popclaw_id = actor.popclaw_id
    core.installation_id = installation
    core.op_seq = op_seq
    core.request_id = request_id or ("req-" + secrets.token_hex(8))
    core.house_origin = origin
    now = int(time.time())
    core.issued_at = issued_at if issued_at is not None else now - 5
    core.expires_at = expires_at if expires_at is not None else now + 60
    core.nonce = nonce or secrets.token_hex(8)
    core.expected_house_revision = expected_revision
    if target_session:
        core.target_session_id = target_session

    request = wire.HouseSessionRequest()
    request.core.CopyFrom(core)
    request.signer_pubkey = actor.public_key_bytes
    request.signature = actor.sign(
        wire.signing_input(wire.DOMAIN_SESSION_REQUEST, wire.canonical_core(core)))
    return request.SerializeToString(deterministic=True)


def parse_ack(response_bytes: bytes) -> "wire.HouseSessionAck":
    return wire.HouseSessionAck.FromString(response_bytes)


def check_in_intent(actor: Actor, *, session_id: str, fence: str,
                    capability_revision: str, schema_version: int = 1,
                    kind: str = "rangermap.check_in",
                    params: dict | None = None,
                    valid_until: int | None = None,
                    house_origin: str = ORIGIN,
                    house_key: str = "",
                    incarnation: str = "",
                    lorehouse: str = "") -> bytes:
    params = params if params is not None else {
        "place": "Hangzhou", "latitude": "30.27",
        "longitude": "120.15", "status": "Wire-test check-in.",
    }

    def set_body(envelope):
        envelope.intent.lorehouse = lorehouse
        envelope.intent.intent_kind = kind
        envelope.intent.params = json.dumps(
            params, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        envelope.intent.context.house_origin = house_origin
        envelope.intent.context.house_key = house_key
        envelope.intent.context.incarnation = incarnation
        envelope.intent.context.session_id = session_id
        envelope.intent.context.fence = fence
        envelope.intent.context.capability_revision = capability_revision
        envelope.intent.context.schema_version = schema_version
        envelope.intent.context.valid_until = (
            valid_until if valid_until is not None else int(time.time()) + 300)

    return signed_envelope_bytes(build_envelope(actor, set_body), actor)


def status_read(actor: Actor, request_id: str, *, house, nonce: str | None = None,
                issued_at: int | None = None,
                expires_at: int | None = None) -> bytes:
    core = wire.ActionStatusRequest()
    core.house.origin = house.origin
    core.house.house_key = house.house_key
    core.house.incarnation = house.incarnation
    core.actor_id = actor.popclaw_id
    core.request_id = request_id
    core.nonce = nonce or ("n-" + secrets.token_hex(8))
    now = int(time.time())
    core.issued_at = issued_at if issued_at is not None else now - 5
    core.expires_at = expires_at if expires_at is not None else now + 60
    core.signature = actor.sign(
        wire.signing_input(wire.DOMAIN_ACTION_STATUS_READ,
                           wire.canonical_core(core)))
    return core.SerializeToString(deterministic=True)
