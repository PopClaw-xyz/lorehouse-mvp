# Identity read authentication

The named scheme `popclaw-identity-read-v2` authenticates a read request with the
requester's Ed25519 identity key. It is distinct from the House-issued, session-bound
inbox token in `house_session.proto`, including that protocol's token version 2.
The `v2.` segment below identifies the identity credential format only; it is not
an instruction to select any scheme whose name contains "v2".

This contract fixes existing identity read authentication. It changes no protobuf
field, descriptor, codec, EventEnvelope, CID or event-signing recipe. The obsolete
three-segment self-signed credential and its `inbox-read` signing domain are refused.
They are not an additional supported lane.

## 1. Trusted audience and declaration

`ReadAudience = { origin, house_key }` is a projection of already trusted House
identity. A server derives one immutable value from its verified startup identity
and configuration. A client copies the values from its verified HouseBinding.
It is not a separate trust store and is not supplied by the read request.
Incarnation, relation database claims, ordered-relation capability, installation,
session ID and participation state are not fields of this credential.

The origin is the WHATWG origin ASCII serialization: lowercase scheme and host,
HTTP/HTTPS default port omitted, non-default port retained, IPv6 brackets retained,
no path, query, fragment or userinfo. The House authors this canonical value in its
binding. A client copies the verified binding's origin and House key verbatim;
it does not normalize them again or sign the address originally entered by a user.
The House key is Bitcoin-base58 encoding of exactly 32 Ed25519 public-key bytes.

A House with a usable ReadAudience declares this top-level member in the exact
served manifest body covered by the verified ManifestProof:

```json
"read_auth": { "schemes": ["popclaw-identity-read-v2"] }
```

The runtime authors the declaration before serialization, digest and signing.
A source manifest may agree with that runtime declaration or omit it; a conflicting
source declaration is refused. Without ReadAudience the runtime omits `read_auth`
and identity-authenticated private routes return `503 read_authority_unavailable`.
Failing startup preflight is preferable to advertising an unusable read service.
Identity reading does not require `relations.ordered` or `world_interaction`.

Clients select identity reading only from the exact scheme name in the same
currently verified manifest and binding. An absent declaration, malformed block,
empty scheme list or a list without the exact supported name grants no identity
read authority. Unknown names grant nothing and must not be guessed from their
spelling. Do not read a separate unverified advertisement, probe old self-signing,
try anonymous private reading, use a domain whitelist or turn a refusal into an
empty relation list or successful recovery.

## 2. Purposes and routes

The caller selects the purpose explicitly. The verifier obtains the expected
purpose from the actual route, never from a caller-controlled claim.

| Purpose | Route |
| --- | --- |
| `relation-list` | `GET /follows/:id`, `GET /followers/:id` |
| `inbox-stream` | `GET /inbox/:id/stream` |
| `relation-snapshot` | `GET /v1/relation-snapshot` |
| `relation-evidence` | `GET /v1/relation-evidence/:event_id` |

A snapshot credential does not authorize evidence or inbox reading. The two list
routes share one purpose. Authentication establishes the requester only; each route
then applies its own object policy (section 5).

## 3. Exact signing bytes and header

Ed25519 signs these exact ASCII bytes, with no trailing newline, NUL, protobuf core,
JSON conversion, length prefix or additional separator:

```text
popclaw-identity-read-v2:<purpose>:<requester>:<house_key>:<seconds>:<origin>
```

The field order is fixed. `purpose` is one of section 2's four strings; requester
and House key are base58; seconds is canonical decimal. None can contain `:`.
Only the final origin may contain colons, including a port or IPv6 address. These
field grammars and the final origin position make the concatenation unambiguous.
The message is output, not a data source: build it from the held purpose, identity,
audience and timestamp; never split it to recover those values.

```text
x-popclaw-inbox-token: v2.<requester>.<seconds>.<standard-base64-signature>
```

The header has exactly four dot-separated segments. Count all segments; a bounded
split that folds extra segments into the signature is not sufficient. Purpose,
origin and House key are not transmitted in this header. The server reconstructs
the message from the actual route, its trusted audience and the validated requester
and timestamp. All old three-segment self-signed forms are rejected; no dual
acceptance or failure-triggered scheme traversal is permitted.

## 4. Syntax, freshness and verification

| Value | Rule |
| --- | --- |
| Whole token | ASCII only, at most 153 characters, exact `v2` first segment |
| Requester | Bitcoin-base58, at most 44 characters, strict decoding to exactly 32 bytes; shorter valid encodings are allowed |
| Seconds | Unix epoch **seconds**, nonnegative canonical decimal (`0` or a nonzero digit followed by digits); no sign, whitespace or redundant leading zero; at most 16 characters and at most `9007199254740991` (`2^53-1`) |
| Signature | Canonical padded standard base64, exactly 88 characters decoding to 64 bytes; strict decoding and canonical re-encoding must agree, not base64url or an unpadded variant |
| Freshness | Absolute difference from the server's current Unix epoch seconds is at most 60; both `-60` and `+60` are accepted, both `-61` and `+61` refused |

Use safe integer arithmetic for freshness (for example unsigned `abs_diff`);
do not parse a signed integer then take an overflowing absolute value. The
16-character decimal bound does not make milliseconds into seconds.

Reject segment/version and length errors first, then timestamp syntax/range and
freshness, then base58/base64 syntax and decoded lengths. Verify Ed25519 against
the decoded requester key over section 3's reconstructed message. Only after a
valid signature may the route decide whether that requester has object access.
An unverified claimed identity must never cause a `403` response.

## 5. Object policy and failure semantics

| Condition | Response |
| --- | --- |
| Server cannot establish ReadAudience | `503` with stable code `read_authority_unavailable` |
| Missing, malformed, unsupported, stale or cryptographically invalid identity credential | `401` |
| Authenticated requester lacks object access, except evidence concealment below | `403` |
| Unknown evidence ID, non-relation evidence type, or requester not an edge participant | The same empty `404`, byte for byte |

List access is checked after authentication under the route's self/administrator
policy. Administrator list access grants no authority over another identity's inbox
or evidence. Inbox identity requests must target the requester itself. Snapshot
requests read that requester's relations; evidence requests require the requester
to be the follower or followee taken from verified ingest. Evidence type and
participation refusals preserve RELATIONS.md section 7's hidden-existence policy;
they do not become `403`. Invalid credentials still receive `401` before an object
lookup. Other snapshot cursor/checkpoint/storage errors remain in RELATIONS.md.

A House may apply additional route policy. In particular, the minimal reference
House refuses identity inbox reading with `403` once that actor has any row in its
`sessions` history, including inactive sessions; it requires the specific session's
House-issued inbox token instead. This is that House's inbox policy, not a federation
requirement or an installation fence inherent in identity-v2. The history predicate
is sessions-row existence, not arbitrary installation history or a leave-only
tombstone. It is not extended to snapshot/evidence authentication.

Keep failures observable and retry with bounded backoff. A `403` does not trigger
repinning, anonymous access or a different scheme; a `401` may permit bounded fresh
credentials within the selected lane, never traversal to another lane. Logs may
classify observable facts such as malformed, not fresh, signature invalid, forbidden
or unavailable authority; signature failure alone cannot distinguish wrong origin,
wrong purpose and forgery. Never log the complete credential.

## 6. Session lane selection and lifecycle

House-issued inbox authentication remains an independent positively declared lane.
Its trusted `house_session` declaration, current session, specific ACK token and
lifecycle fence are required; a nonempty local session ID or a token labeled v2
alone is not selection authority.

When both identity-v2 and session reading are positively declared at the current
trusted origin and the caller has a current authorized session, inbox reading
selects that session's House-issued `itk` token first. Missing token, token/session
expiry, revocation or a `401` in that selected lane is a failure, not permission to
switch to identity reading. A later active session does not authorize an earlier
session's token. An identity-only declaration must not cause a residual session ID
to send an `itk` token. Selection must precede any unnecessary identity signing.

Without a selected session lane, identity inbox reading requires its own positive
verified declaration and current local authorization. An untrusted/blocked pin or
closed lifecycle gate permits no inbox request. Recheck current binding,
declaration and lifecycle after asynchronous work; a logout, renewal or generation
change while signing must not send a request using stale authority. Snapshot and
evidence use their own identity purposes and object policies independently of inbox
session selection.

Identity credentials contain no installation/session/revision fence and do not
invalidate the identity private key on logout. Local logout closes local work;
server-confirmed session closure, revocation or expiry invalidates the corresponding
House-issued token. Do not claim remote identity-key revocation, instant cancellation
of bytes already sent, or complete logout safety from identity signatures alone.

## 7. Per-request issuance and conformance evidence

Issue a fresh credential for each list/snapshot/evidence request and each inbox
reconnect, with that call's explicit purpose and current clock. Do not reuse one
fixed header across a long reconciliation sweep. Check caller ownership/lifecycle
before and after an awaited signature. Identical inputs in the same second normally
produce the same token; this contract provides purpose/audience binding and freshness,
not a nonce or single-use replay exclusion within that House.

The shared [synthetic vectors](../../fixtures/relation-read-v2-vectors.json) retain
seven positive and ten negative cases. Their seeds are test-only and must never
become runtime identities. Recompute the exact message, Ed25519 signature and token
with each implementation's actual constructor, including default-port omission,
non-default ports and loopback IPv6. The vectors do not establish runtime readiness.

A conforming runtime additionally tests all five actual route chains with successful
objects for each purpose, wrong-purpose refusals, independent wrong-origin and
wrong-House-key cases, old three-segment rejection, timestamp/length/encoding bounds,
and inclusive 60-second/exclusive 61-second boundaries. Include an actual successful
evidence read and its indistinguishable empty-404 refusals. Test lifecycle races and
selected-session failure without fallback; a helper testing itself cannot establish
route wiring or session safety. These are conformance requirements, not claims that
this source bundle ships a server or has run those runtime tests.
