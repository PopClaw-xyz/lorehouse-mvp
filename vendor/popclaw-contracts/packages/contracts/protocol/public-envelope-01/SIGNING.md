# Signing domains and digest recipes

Prefixes below are exact ASCII bytes followed immediately by canonical protobuf
core bytes. There is no separator, length prefix or implicit JSON conversion.
Signatures are Ed25519. SHA-256 digests are lowercase hexadecimal (64 characters).
The generated core must preserve optional presence and wide integers as defined in
the proto. Unknown signed fields which cannot be faithfully verified are unsupported;
lossy unknown-field skipping never proves verification.

| Domain | Authority | Core | Excluded field |
| --- | --- | --- | --- |
| `POPCLAW_HOUSE_SESSION_REQUEST_V1` | Requesting actor | RequestCore | Signature is in HouseSessionRequest |
| `POPCLAW_HOUSE_SESSION_ACK_V1` | Pinned House ACK authority | AckCore | Signature is in HouseSessionAck |
| `POPCLAW_WORLD_MANIFEST_PROOF_V1` | Pinned House authority | ManifestProof 1–3 | authority_signature 4 |
| `POPCLAW_WORLD_ACTION_RESULT_V1` | Verified manifest's result authority | ActionResult 1–18, including all attachments | Signature is in SignedActionResult |
| `POPCLAW_WORLD_SUBSCRIPTION_OBSERVATION_V1` | Result authority | SubscriptionObservation 1–14 | signature 15 |
| `POPCLAW_WORLD_ACTION_STATUS_READ_V1` | Actor | ActionStatusRequest 1–6 | signature 7 |
| `POPCLAW_WORLD_EXECUTION_PERMIT_V1` | House | ExecutionPermit 1–15 | Signature is in SignedExecutionPermit |
| `POPCLAW_WORLD_WORKER_RESULT_V1` | Configured worker | WorkerResult 1–14, including attachments 12–14 | Signature is in SignedWorkerResult |
| `POPCLAW_WORLD_CLOSURE_QUERY_V1` | Actor | ClosureQueryRequest 1–10 | signature 11 |
| `POPCLAW_WORLD_CLOSURE_OBSERVATION_V1` | House session authority | ClosureObservation 1–16, including page index and page contents | signature 17 |

The ordinary EventEnvelope inner signature signs its canonical core **without a
prefix**; SignedPayload signs the exact envelope bytes **without a prefix**.
Do not substitute a world/session domain into those established algorithms.
A digest or valid signature alone is not request/actor/audience/House binding or
current authorization. Every verifier checks the saved original context.

## Canonical protobuf core

Encode fields in ascending field-number order. Omit implicit proto3 scalar defaults
(zero, false, empty string and empty bytes); retain explicitly present optional or
oneof defaults and present empty nested messages. Preserve repeated element order.
Encode string-map entries in ascending UTF-8 key-byte order, with shorter prefix
keys first. Within each entry omit empty string key/value fields, but retain the
entry even when both are empty. These rules match the pinned Rust/prost encoder;
protobuf runtime flags named `deterministic` alone are not a cross-language contract.
Use the provided canonical helpers and shared vectors, not a generic codec's raw
`encode` as a signing API. Clear EventEnvelope event_id and signature for its core;
its event_id is SHA-256 of that core. Never normalize an unsupported received wire
into a new event or rewrite the original SignedPayload bytes.

## Exact digests

- `capability_revision` and `manifest_digest`: exact final served manifest bytes.
- `request_digest`: exact accepted EventEnvelope bytes, not a reconstructed object.
- `result_digest`: exact result_body bytes.
- `covered_digest`: canonical JSON array of objects with exactly
  `{"entered_op_seq":"<decimal>","fence":"<string>","session_id":"<string>"}`,
  array ordered by session_id byte order.
- `results_digest`: canonical JSON array with exactly
  `{"execution_id":"<string>","request_id":"<string>","result_digest":"<hex64>","session_id":"<string>","status":"<string>"}`,
  array ordered by request_id byte order.
- `members_digest`: canonical JSON array of
  `{"event_id":"<hex64>","kind":"<string>","scopes":["<string>",...]}`,
  array ordered by event_id, covering the complete membership across registration
  pages. Fix member_total before registration; never omit the final page/member.
- `closure_digest`: canonical ExecutionClosure bytes with its own closure_digest
  absent, all other fields (including results_digest) retained.

Canonical JSON uses UTF-8, integer-only values, no insignificant whitespace, and
object keys sorted by UTF-16 code-unit order. This is distinct from protobuf map
key ordering by UTF-8 bytes. Empty arrays hash the exact bytes `[]`. Reject duplicate
JSON keys before schema interpretation. Do not coerce wide counters to JSON numbers;
their canonical decimal-string form is part of the signed meaning.

The retained world-signing fixtures test unchanged byte/domain rules. They do not
activate the recorded historical manifest, guide, key or capability in a runtime.
