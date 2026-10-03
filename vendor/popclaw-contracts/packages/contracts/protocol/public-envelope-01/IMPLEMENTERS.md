# Implementing the first public baseline

Read the normative documents linked in the contracts README. The following is a
navigation guide, not a substitute for complete authentication or runtime tests.

## Endpoint and evidence map

All paths resolve at the selected canonical House origin. Reject ambiguous,
cross-origin, credential-bearing or protocol-relative redirect destinations.
Never infer a House from a slug when a request is bound to an exact origin/key.

| Operation | Endpoint | Evidence and boundary |
| --- | --- | --- |
| Discovery | `GET /v1/manifest` | Exact UTF-8 body; `X-Popclaw-Manifest-Proof` is base64 ManifestProof |
| Declared interpretation guide | `GET /v1/guide.md` | Exact bytes must match the authenticated declaration; not needed for public-only operation |
| Session control | `POST /v1/house-session` | Binary HouseSessionRequest; signed HouseSessionAck bound to the original request |
| Event/action submission | `POST /v1/push` | Binary SignedPayload, outer signature over original EventEnvelope bytes; inner canonical signature and CID |
| Public event reception | `GET /v1/world-stream?mode=public-v1` | Anonymous, exact selection grammar in PUBLIC-STREAM.md; no credentials or Last-Event-ID |
| Explicit ordinary legacy reception | `GET /v1/world-stream` | Existing legacy grammar; independent raw-wire guard; no complete-baseline claim without negotiation |
| Ordinary private DM reception | `GET /inbox/:popclaw_id/stream` | Positively selected House session or identity-v2 authentication; named SSE `envelope` with base64 full signed EventEnvelope |
| Declared action status | `POST /v1/world-actions/status` | Signed ActionStatusRequest; exact original request/authority context and authentic results |
| Relation reconciliation baseline | `GET /v1/relation-snapshot` | Identity-v2 `relation-snapshot`; frozen checkpoint, decimal-string 64-bit fields, House hints only |
| Relation original bytes | `GET /v1/relation-evidence/:event_id` | Identity-v2 `relation-evidence`; verbatim stored envelope to an edge participant; uniform empty 404 |

The two relation routes are specified in RELATIONS.md, with authentication in
[READ-AUTH.md](READ-AUTH.md); this candidate fixes their
contract and ships no server for them.

Additional optional endpoint constants are in board.schema.json and the proto;
advertising them requires their actual implementation. An endpoint table is not a
claim that any particular server has enabled these capabilities.

## Identity, trust and sessions

A `popclaw_id` is the Bitcoin-base58 encoding of exactly 32 Ed25519 public-key bytes.
Check the decoded key length, not merely a string regex. A display nickname conveys
no authority. Keep the same identity key and retained personal evidence across
ordinary reconnects and upgrades.

The manifest proof covers the SHA-256 hex digest of the **entire exact served body**.
Its signing bytes are ASCII `POPCLAW_WORLD_MANIFEST_PROOF_V1` followed directly by
the canonical ManifestProof core with `authority_signature` absent. Verify origin,
House key and server incarnation against the existing trusted binding before using
any declared capability. Optional block failure never bypasses an invalid base
proof. A new key or incarnation is not automatically trusted or repinned.

Session request and ACK domains are distinct ASCII prefixes:
`POPCLAW_HOUSE_SESSION_REQUEST_V1` and `POPCLAW_HOUSE_SESSION_ACK_V1`, each immediately
followed by its canonical core bytes, with no extra separator. Requests match the
requesting actor key. ACK signer keys match the trusted House ACK authority;
AckCore.popclaw_id names the requester, not the ACK signer.

Validate ACK origin, requester, installation, request ID, op_seq, operation and
outcome against the **saved original request**, not current mutable UI/session
state. The manifest `house_session.ack_pubkey` is lowercase 64-character hex.
ENTER/RENEW/LEAVE/STATUS are control operations. The retained ACTION enum is a
restricted fixture operation, not a general application endpoint promise.

Request IDs provide semantic idempotency: session retries may refresh nonce/times
and re-sign while keeping the original semantic operation. Allocate op_seq durably
per identity/House, keep installation watermarks, and enforce generation fences at
actual effect commit. A late old leave cannot close a newer enter. Local logout
fences local work independently of a remote ACK; an unknown outcome is not confirmed
remote closure. Ordinary process restart does not rotate the House incarnation.
A public-log baseline change and a server/session restore are distinct boundaries.

## Event bytes and signatures

1. Preserve the received EventEnvelope bytes before decoding. Apply the bounded
   structural guard at every ingress, including legacy/cache/projection boundaries.
2. Where receiving SignedPayload, verify its outer signature over its exact payload
   using the supplied key before treating decoded contents as authenticated.
3. For the inner signed core, remove event_id and signature, encode canonical proto3
   fields, compute SHA-256 lowercase hex, and compare the event_id. Verify Ed25519
   signature over those canonical bytes and check actor/signer identity consistency.
4. Apply body-specific validity/authority and the appropriate public/private policy.
   Only then may a server commit admission and allocate a visible sequence.

Passing `checkEnvelopeWire` establishes supported structure only.
`checkPublicEnvelopeStructure` additionally excludes known private/transient bodies,
invalid public Recipient forms and nonpublic Follow values. Neither verifies an
author's identity/signature or a Quest/Invite/application authority. Never expose
raw failed evidence through a public projection or diagnostic.

Implicit proto3 defaults are omitted from canonical encoding. Explicit optional
presence remains, including present-empty ActorInfo fields and present-zero
public_through_seq. Wide counters remain uint64/Long values; JSON renders them as
canonical decimal strings. Do not round through JavaScript Number. Map keys encode
in ascending UTF-8 byte order, including Unicode and integer-like string keys.
Generated TS map encoding applies that ordering directly; sorting object insertion
order alone is insufficient.

Do not repair a received record by decoding away reserved or unsupported fields.
An unknown legal HouseEvent business kind still carries opaque bytes and may be
retained/relayed without interpretation, projection or model execution. Opaque data
which resembles field tags is not a nested envelope to inspect.

## Ordinary DM

DirectMessage remains in the known envelope schema but is never public. The
recipient stream carries complete signed envelopes, not bare DirectMessage payloads;
reject an incompatible unnamed frame rather than guessing its type. Verify the
signed sender, recipient targeting and message bytes before interpretation.

A session lane uses its verified House-issued inbox `itk` token and current
lifecycle fence, positively selected through the trusted `house_session` declaration.
When both schemes are declared and a current authorized session exists, inbox
reading selects that session lane first. Missing token, expiry or a rejected token
cannot fall back to identity signing. A residual session ID alone does not authorize
that lane, especially on an identity-only House.

An independently selected identity lane uses `popclaw-identity-read-v2`, purpose
`inbox-stream`, and the canonical four-segment `x-popclaw-inbox-token` header in
[READ-AUTH.md](READ-AUTH.md). It requires the current verified `read_auth` declaration,
trusted binding and caller lifecycle gate. Old three-segment self-signing is refused;
authentication failure never triggers anonymous access or scheme traversal. Issue
on every reconnect, recheck authority after async work, and use bounded retry/backoff.
Identity authentication alone has no installation/session fence; the House's route
policy still applies. The minimal reference House requires session authentication
for an actor with any sessions-row history. This House policy is not a federation
rule and does not restrict independent snapshot/evidence identity purposes.
The inclusive 60-second identity window provides no single-use replay exclusion.

Existing encrypted DM uses the identity-derived X25519/NaCl box convention, with
fresh nonces. Ciphertext and nonce are covered by the envelope signature. Empty
implicit bytes and absent bytes have the canonical default treatment; explicit
optional fields elsewhere must not be erased. The ordinary DM interface does not
promise forward secrecy or metadata privacy. This contract bundle verifies encoded
DM fields and signatures; it is not an encryption library or a complete DM runtime.

## Ordered relations

RELATIONS.md is normative for `RelationOrder`. A House declares `relations`
exactly as `{"ordered": 1}` in the authenticated manifest body, and only when
its runtime genuinely has the capability; absence means unsupported, and any
other value is capability-unknown rather than a downgrade to the legacy rules.
`order` rides the ordinary envelope signature and CID, so the author's own
signature is what a receiver verifies — a House signature never substitutes.
`seq` has an effective domain of 1..=2^63-1 and crosses every JSON boundary as
a decimal string. `envelope.lorehouse` must equal `order.house_key` only when
it is non-empty; empty keeps its proto3 default meaning. Two author-written
fields agreeing proves internal consistency only, so compare `order.house_key`
against a House key established independently through TRUST.md.

Gaps in `seq` are legal and arrival need not be contiguous. Same position with
a different `event_id` is a fork, never a duplicate, and an ordinary larger
`seq` never clears one. A client that does not adjudicate `resolves` keeps the
edge pending; it must not drop the field and apply the event anyway. A snapshot
watermark may be adopted only after a complete pagination of one checkpoint,
an absent entry is not an unfollow, and every House-supplied state or hint is
rechecked against the originals.

A relation original is delivered to its two participants' personal streams and
to no public lane. It is not publicly eligible, ordered or not: the shared
predicate answers `NOT_PUBLIC` on the body type, and a House applies the same
answer at publication, on the live path, in the history window, in a cursored
replay and in any projection baked out of the log. Receiving one on a public
channel is evidence that the sender is not conforming, not permission to consume
it. The only position the refusal may release is the transport resume position,
and only once the raw bytes, their true byte hash, the refusal reason, the
trusted connection source and that position have been durably retained in the
same atomic step; a failed evidence write moves nothing. Releasing it asserts
nothing about signature verification, business completion, relation ordering or
recovery completeness, and it never occupies a verified event's deduplication
identity, so the same original arriving later on a personal stream is still
processed. A position that also asserts complete reception is never moved by a
refusal. Stopping instead, with the binding declared unavailable, is equally
conforming. See RELATIONS.md §8.

## Actions, authority and recovery

Login/subscription does not authorize a business write. A declared action captures
the exact manifest, guide/schema, House result authority, session/fence and bounded
local policy. The action's required/allowed attachments and consistency promise
must be met; unrelated valid base actions do not require a broken optional stream.
Status polling, timeout or HTTP success cannot substitute for a signed terminal
business result. Retry an action's exact original SignedPayload/request identity;
an unknown execution is reconciled, not resent under a new ID.

Retain the base receipt, each attachment validation result, installation disposition
and pending recovery work separately. A valid business result can coexist with an
unsupported attachment. Installation does not grant policy, schedule a model or
make a stream caught up. See RECEIPTS.md and retained/state-transitions.md.

At a log gap, preserve durable positions and original evidence, close, and report
unavailable readiness. Do not checkpoint across unsupported N, manufacture scope
progress from unrelated events or auto-switch to legacy. An incarnation mismatch
is an untrusted discovery hint; validate the current manifest before explicit new
selection. Real replay creates new log associations; historical content dedup may
avoid repeated business effects but never invents receive evidence.
