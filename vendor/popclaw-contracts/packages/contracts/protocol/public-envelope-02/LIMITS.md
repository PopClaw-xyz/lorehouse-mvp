# Fixed protocol resource limits

These are fixed limits, not manifest-negotiated capabilities. Runtime implementations
apply them before expensive processing. A resource-limit rejection is not proof of
cryptographic invalidity.

| Limit | Value |
| --- | --- |
| `L_MANIFEST_MAX_BYTES` | 262144 (256 KiB) |
| `L_MANIFEST_MAX_RAW_DEPTH` | 64 (manifest base parse only; not the business JSON depth) |
| `L_GUIDE_MAX_BYTES` | 524288 (512 KiB) |
| `L_SCHEMA_DOC_MAX_BYTES` | 32768 per schema |
| `L_MANIFEST_MAX_SCHEMAS` | 64 |
| `L_PARAMS_MAX_BYTES` | 16384 |
| `L_RESULT_BODY_MAX_BYTES` | 32768 |
| `L_SNAPSHOT_BODY_MAX_BYTES` | 65536 |
| `L_ENVELOPE_MAX_BYTES` | 1572864 (1.5 MiB; a direct message carrying a 1 MiB sealed attachment fits) |
| `L_JSON_MAX_DEPTH` | 8 |
| `L_SCOPES_MAX` | 32 per subscription/request vector |
| `L_INITIAL_SCOPES_MAX` | 8 |
| `L_SCOPE_ID_MAX_CHARS` | 64 |
| `L_ACTION_GROUPS_MAX` | 16 |
| `L_OPPORTUNITIES_MAX` | 64 |
| `L_BUDGETS_MAX` | 16 |
| `L_DESCRIPTOR_MAX_BYTES` | 65536 |
| `L_PRIVATE_MESSAGE_MAX_BYTES` | 65536 (wrapper JSON inside DM ciphertext) |
| `L_SUMMARY_MAX_CHARS` | 280 |
| `L_DEDUPE_KEY_MAX_CHARS` | 128 |
| `L_CLAIM_BATCH_MAX` | 16 |
| `L_COMPLETE_BATCH_MAX` | 16 |
| `L_PUBLICATION_STATUS_BATCH_MAX` | 64 |
| `L_PENDING_ACTIONS_PER_SESSION_MAX` | 64 |
| `L_STATUS_QUERY_TTL_MAX_SECONDS` | 300 |
| `L_CLOSURE_RECORDS_PAGE_MAX` | 128 |
| `L_BARRIER_MEMBERS_MAX` | 256 |
| `L_STREAM_PAGE_MAX_EVENTS` | 512 client request / 256 server page |
| `L_BUDGET_SUGGESTED_LIMIT_MAX` | 1000 |

The 65,536-field traversal budget and depth 32 bound the shared **raw-wire**
guards over protobuf EventEnvelope bytes — `checkEnvelopeWire` and its Rust and
Python equivalents — and nothing else. They are not guarantees of any JSON
parser: no JSON limit in this contract counts fields, and JSON nesting is bounded
separately by `L_MANIFEST_MAX_RAW_DEPTH` for the manifest's base parse and by
`L_JSON_MAX_DEPTH` for business JSON. `L_ENVELOPE_MAX_BYTES` was 262144 in
`0.1.0-public-envelope-01.3`; a house may
still apply a smaller bound to what it relays on its public stream (the reference
lore-house keeps 256 KiB there), which is house policy, not a protocol limit. Business byte payloads remain opaque; JSON limits apply only where a specific
interface requires JSON, and `L_JSON_MAX_DEPTH` binds business JSON, not manifest
rows this contract does not select (SPEC.md, "Manifest jurisdiction").
