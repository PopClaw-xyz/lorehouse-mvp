"""Fixed public contract adapter — BOUND to public-envelope-02.0.

The native wire surface is implemented against the vendored trusted
contract bundle (``vendor/popclaw-contracts``, pinned SHA-256
``c530e69b51dcf8358b0e239b67d936dc9443ba7cad1f59b34b34520ad5e11337``):

- ``GET /v1/manifest`` + ``X-Popclaw-Manifest-Proof`` — pinned manifest
  bytes with a fresh house-signed proof over
  ``POPCLAW_WORLD_MANIFEST_PROOF_V1``.
- ``POST /v1/push`` — SignedPayload ingress: outer signature over the exact
  envelope bytes, bounded raw-wire guard (reserved EventEnvelope 29 /
  nested Profile 8 reject the whole event), canonical CID check, inner
  signature and actor↔signer binding, then per-body policy (public lane,
  private DM relay, opaque HouseEvent retention, intent actions). Relations
  have scoped ordered admission, persisted evidence and recovery adjudication;
  every original is delivered only to its two participants.
- ``POST /v1/house-session`` — G0 enter/renew/leave/status with signed
  requests/ACKs, op-seq CAS, leave watermarks, fences and v2 inbox tokens.
- ``POST /v1/world-actions/status`` — signed, nonce-bound, owner-only
  terminal result reads (immutable replay).
- ``GET /v1/world-stream?mode=public-v1`` — the complete public lane with
  cursor/replay/checkpoint/gap semantics and check-to-send cutover fencing;
  the unqualified legacy lane keeps its old frame grammar.
- ``GET /inbox/:id/stream`` — recipient-isolated DM and relation relay.
- Reconciliation reads use the sealed named identity-read-v2 scheme, with
  purpose/audience binding and independent session-token inbox authority;
  see docs/relations-client-binding.md for this House's eligibility policy.

Domain unit tests may still construct ``TrustedCheckInContext`` directly;
that remains a test convenience, not an HTTP write path. See
docs/protocol-bindings.md for evidence and remaining boundaries (external
client interoperability is reported separately from server conformance).
"""

from __future__ import annotations

from ..check_in import TrustedCheckInContext

ADAPTER_BOUND = True
CONTRACT_BUNDLE_SHA256 = (
    "c530e69b51dcf8358b0e239b67d936dc9443ba7cad1f59b34b34520ad5e11337"
)
CONTRACT_VERSION = "0.1.0-public-envelope-02.0"

__all__ = [
    "ADAPTER_BOUND",
    "CONTRACT_BUNDLE_SHA256",
    "CONTRACT_VERSION",
    "TrustedCheckInContext",
]
