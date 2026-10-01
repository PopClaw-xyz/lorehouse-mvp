"""Fixed public contract adapter — BOUND to public-envelope-01.6.

The native wire surface is implemented against the vendored trusted
contract bundle (``vendor/popclaw-contracts``, pinned SHA-256
``d01bd7a060cdaa2bb35937b67e5fb4dc64a350a646b30cf2fe5dd919701ea54b``):

- ``GET /v1/manifest`` + ``X-Popclaw-Manifest-Proof`` — pinned manifest
  bytes with a fresh house-signed proof over
  ``POPCLAW_WORLD_MANIFEST_PROOF_V1``.
- ``POST /v1/push`` — SignedPayload ingress: outer signature over the exact
  envelope bytes, bounded raw-wire guard (reserved EventEnvelope 29 /
  nested Profile 8 reject the whole event), canonical CID check, inner
  signature and actor↔signer binding, then per-body policy (public lane,
  private DM relay, opaque HouseEvent retention, intent actions). A Follow
  carrying a ``RelationOrder`` is refused, as is every other relation
  no ``relations.ordered`` capability and never degrades an ordered
  relation to the legacy rules.
- ``POST /v1/house-session`` — G0 enter/renew/leave/status with signed
  requests/ACKs, op-seq CAS, leave watermarks, fences and v2 inbox tokens.
- ``POST /v1/world-actions/status`` — signed, nonce-bound, owner-only
  terminal result reads (immutable replay).
- ``GET /v1/world-stream?mode=public-v1`` — the complete public lane with
  cursor/replay/checkpoint/gap semantics and check-to-send cutover fencing;
  the unqualified legacy lane keeps its old frame grammar.
- ``GET /inbox/:id/stream`` — recipient-isolated encrypted DM relay.

Domain unit tests may still construct ``TrustedCheckInContext`` directly;
that remains a test convenience, not an HTTP write path. See
docs/protocol-bindings.md for evidence and remaining boundaries (external
client interoperability is reported separately from server conformance).
"""

from __future__ import annotations

from ..check_in import TrustedCheckInContext

ADAPTER_BOUND = True
CONTRACT_BUNDLE_SHA256 = (
    "d01bd7a060cdaa2bb35937b67e5fb4dc64a350a646b30cf2fe5dd919701ea54b"
)
CONTRACT_VERSION = "0.1.0-public-envelope-01.6"

__all__ = [
    "ADAPTER_BOUND",
    "CONTRACT_BUNDLE_SHA256",
    "CONTRACT_VERSION",
    "TrustedCheckInContext",
]
