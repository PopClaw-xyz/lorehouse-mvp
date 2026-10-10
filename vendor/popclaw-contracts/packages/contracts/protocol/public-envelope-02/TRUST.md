# Trust binding

Keep one persistent trust record per canonical origin. A configured or persisted
pin has priority. A conflicting configured/persisted key, changed manifest key or
proof under another key stops new execution; retain the original pin and unresolved
records. Never silently fall back to first-contact trust or replace a pin from a
House response.

With no pin, explicit user/host login to the exact origin may establish first
binding from a certificate-chain and hostname-verified HTTPS manifest fetch, with
redirects and cross-origin fallback forbidden. Validate the declaration/key and
transactionally insert-if-absent the origin/key with its transport provenance.
Concurrent different keys conflict; a lost ENTER ACK must not lose the pin needed
for later exit/reconciliation. The HTTPS transport is the first-contact trust
source. A key's self-signature in the same untrusted response is not independent
trust. Background discovery, events, DMs and guides cannot create or replace pins.

Verify the manifest proof against that pin, the exact complete response-body digest
and full HouseBinding. The session ACK key (hex) and HouseBinding.house_key (base58)
identify the same 32-byte authority key; compare decoded bytes. A separately declared
result authority is limited signing delegation, never a replacement bootstrap pin.
A first server incarnation is established by the pin-verified proof; a later changed
incarnation pauses new execution even if the key is the same. Reconciliation and
explicit local trust rebuilding remain separate from stream selection.

Explicit local loopback fixtures may use plaintext HTTP with recorded fixture
provenance, never labeled HTTPS-verified or generalized to remote deployment.
No fixture in this bundle authorizes network login or contacts its example origin.

A public-log cutover does not itself change HouseBinding, trust, session or local
policy. See BASELINE.md for the distinct public-log incarnation and delivery fence.
