# Revised first-release interaction contract

Version: 0.1.0-public-envelope-02.0. Candidate for implementer review; not runtime acceptance or publication approval.

## 1. Scope

The normative set comprises this document, BASELINE.md, PUBLIC-STREAM.md,
RECEIPTS.md, RELATIONS.md, [READ-AUTH.md](READ-AUTH.md), LIMITS.md, the adjacent three schemas and the
retained definitions identified by relative references. BASELINE.md defines the explicit structural compatibility
change and takes precedence over historical blanket body-retention wording.
Supported fields retain their numeric allocation and original CID/signing rules.
No runtime storage schema is prescribed. Each House has one public receiver
resource owner and a separate ordinary private DM stream.

Optional structured private-message and execution-closure shapes are retained
for validation compatibility; their presence here does not promise a first-release
runtime implementation. Only exact authenticated declarations and actual
implementation enable a capability. A login is never action authorization.

## 2. Exactly one optional board, three usable blocks

`manifest.world_interaction` is absent on an ordinary House. When present its first-release version is `1` under `board.schema.json`. Blocks are concrete capabilities, not a plugin registry or user-selected named profile framework:

| Block | Provides | Required dependencies | Does not require |
| --- | --- | --- | --- |
| `public_stream` | Complete safe public facts and optional signed-scope selection/progress on `public-v1` | Existing trusted House pin/binding; exact manifest proof; actual retained public log, index, public policy and receiver | `actions`, guide fetch, result key, session ACK board, worker or model |
| `actions` | Explicit listed kinds of original-authority signed actions and base signed receipts | Trusted binding/proof, session protocol for these requests, result authority, exact guide and selected bounded schemas; real per-kind execution implementation | Public scope receiver unless a selected kind promises subscription; participation, private application messages or model |
| `private_messages` | Explicit listed structured kinds inside the existing encrypted DM channel | Trusted sending House/official producer and receiving binding; exact guide and bounded listed schemas; authentic decrypted bytes | Action result key, actions service, scope receiver or model for plain structured conversation/state |
| `execution_closure` | Strong remote execution closure for actions | `actions`, session authority and complete permit/closure implementation on all admissions covered by the declaration | Local logout waiting for remote success; worker/model in a basic relay |

`guide` is shared immutable interpretation metadata, required when actions or private_messages is present, optional and not fetched for public_stream-only use. Server knowledge does not authorize action. The board has no `features`, global `supportsWorld`, mandatory `world_actions`, mandatory `private_message_version` or global `initial_public_scopes`. Old internal board fields are not additional fallback modes.

`actions.attachments` is the exact set the server supports emitting, from snapshot/subscription/participation. Empty is valid. It does not force a receiving client to enable installers. `private_messages.participation=false` forbids a descriptor in those wrappers; true permits it with the unchanged descriptor validation and local authorization rules. This flag is needed because private descriptor interpretation has a different dependency from ordinary private body interpretation; it does not enable automatic model work.

Public scope labels come from `public_stream.initial_public_scopes` and an actual registered-scope authority. A scope-only House can configure/register public labels without installing the actions worker API. This candidate requires a real server-side registration provider but adds no public registration endpoint or worker-auth bypass. The exact provider wiring is a later fixed implementation seam.

### Semantic activation rules

1. Parse the whole served manifest with the bounded base checks before any optional block is interpreted: at most 262,144 bytes (`L_MANIFEST_MAX_BYTES`), strict UTF-8, one complete JSON document, duplicate keys rejected, and a finite raw nesting depth (`L_MANIFEST_MAX_RAW_DEPTH`, 64). Retain the exact body bytes. The manifest digest/proof covers the whole original, so no implementation may drop, rename or normalise a member and verify the remainder, and an unbounded bare parse that stops at "there is no `world_interaction` block" is not this check. Source manifest activation prepares actual log identity/readiness before digest/signing. Log restore/rebuild changes log incarnation; process restart does not.
2. Verify the unchanged ManifestProof domain against the existing trusted House pin and complete HouseBinding. The public-only proof path does not require `house_session.ack_pubkey` to exist; when that board is present its decoded key must match the pinned authority under the base session rules. Actions and closure retain required session/ACK checks. An anonymous boundary never bootstraps a pin or resolves a changed binding.
3. Schema-validation failure in one known block disables that block and dependents only. Interpret the board in two stages: validate its envelope/version/known top-level keys, then independently validate each child against its `$defs` schema. A child failure is not permission to skip its checks. Bad envelope/version/unknown top-level key disables the optional board; ordinary valid social traffic remains. An invalid base identity/session proof retains its existing rejection effect, not an optional fallback.
4. `actions.kinds` uniquely selects existing manifest.intent_kinds rows governed by action-kind.schema.json. Do not apply the new action schema or worker registration requirements to unrelated legacy typed/opaque intent rows. Each selected kind requires one unambiguous row and a registered real execution provider with the matching schema version/purpose. A snapshot-purpose provider remains read-only. Provider choice is server configuration, not a mandatory remote worker deployment shape.
5. For each selected kind, `required_on_success ⊆ allowed ⊆ actions.attachments`. The sets are order-insensitive, no duplicates. Both sets are explicitly required, including `[]`. `consistency=none` forbids subscription in allowed. `stream` requires subscription in required_on_success and a public_stream block. `snapshot_barrier` requires snapshot and subscription in required_on_success, a public_stream block and a real complete barrier publisher. These are fixed per-kind promises, not server-selected weakened interpretations after a request.
6. At server publication, `actions.attachments` must equal the union of all selected rows' allowed sets, avoiding unused claims. At client interpretation, a malformed row or an allowed set outside the declared attachment set disables that kind and dependents only. If a row is unparseable, record union validation as unverifiable; do not treat its unknown set as empty and invalidate unrelated base kinds. If all rows parse but declared attachments include unsupported extras, disable those unsubstantiated attachment capabilities and report the mismatch; independently valid allowed=[] kinds remain usable. A shared result authority/status failure disables actions. A declared subscription promise requires public_stream operational before that kind's first request. A temporarily failed stream blocks only dependent invocation/install/readiness, not unrelated action kinds or base receipt retention. Report outcomes alongside the exact saved manifest, never edit it to hide invalid rows.
7. `private_messages.kinds` uniquely selects interpreted-event-kind.schema.json rows in event_kinds. Ordinary typed event rows remain unchanged. Body-schema validation is for interpretation, never a prerequisite to retain a legal unknown HouseEvent's original bytes. An unavailable/unimplemented schema is unsupported interpretation, not malformed federation transport.
8. A participation descriptor does not require subscription. For every nonempty referenced intent kind, the manifest must declare it; execution through this actions contract additionally requires it in `actions.kinds`. A private descriptor with no executable selected action can still be retained and can constrain direct_message channels permitted by existing fields and local grants; an unsupported intent channel stays unavailable. Do not fabricate dummy actions, delete descriptor kinds, or infer that a direct_message permission authorizes an intent. If the descriptor's existing schema cannot express the requested channel arrangement, reject that interpretation; this revision does not weaken its shape to manufacture a DM-only runtime.
9. `execution_closure` is legal only with actions. All selected action admission paths must enforce the existing permit/closure guarantee. Endpoint merely present in configuration is insufficient. Unsupported remote closure remains distinct from temporary inability to obtain proof. Local logout completes its local fence independently.
10. Guide digest must match exact UTF-8 bytes, at most 524,288 bytes. Each embedded schema at most 32,768 bytes, total interpreted schema count at most 64, validated against the unchanged pinned schema-profile whitelist and resource limits. Existing bounded worker validation has no unbounded fallback. Business JSON remains depth ≤8 and bytes within existing bounds (params 16,384; result body 32,768; snapshot body 65,536). Snapshot validation requires the saved declared schema_kind/schema_version, not a current unrelated manifest row.
11. Endpoint values are the exact same-origin relative constants in the schemas. HTTP rejects cross-origin/ambiguous redirects, protocol-relative paths, URL-embedded credentials or alternate URLs. Public-stream requests are anonymous as specified separately; actions/status/closure retain their required original authentication. Ordinary unfiltered legacy `/v1/world-stream` remains separately selectable; optional-mode failure never silently changes a live connection's requested semantics.
12. New requests capture exact original manifest, guide/schema context, result authority, session/fence and local authority reference. New manifest bytes change capability_revision. Old saved requests/results continue under the old bytes/key; their validity does not imply current grants, current schemas or permission to replay. No automatic historical grant/notification reactivation follows a later module installation or relogin.

### Manifest jurisdiction

The bounded base parse in rule 1 governs the whole manifest. The public profile
governs the `world_interaction` block and, through it, exactly the top-level
declarations that block selects: `actions.kinds` selects `manifest.intent_kinds`
rows (rule 4) and `private_messages.kinds` selects `manifest.event_kinds` rows
(rule 7). A selected row is validated against the adjacent public action-kind or
interpreted-event-kind schema, under the member names those schemas define —
`params_schema`, `result_schema`, `body_schema`. There is no `schema` alias: a
row carrying its payload under another name is an invalid selected row under
rules 3 and 6, never a row to be renamed into shape before validation.

An unselected row is outside that jurisdiction. It is not held to the business
JSON depth limit (`L_JSON_MAX_DEPTH`, 8); it does not consume the interpreted
schema count (`L_MANIFEST_MAX_SCHEMAS`, 64) or the per-schema byte bound
(`L_SCHEMA_DOC_MAX_BYTES`, 32,768); and it confers no exemption on a selected
row. A manifest may carry rows this contract does not interpret without those
rows either paying or escaping these quotas. Every other bound is unchanged:
business `params`, `result_body`, snapshot body and private-wrapper bytes, the
selected-schema size, the interpreted-schema count, the pinned schema-profile
whitelist and the bounded worker limits all apply exactly as rule 10 states.

Absence is not failure. A manifest with no `world_interaction` block is an
ordinary House that does not support these capabilities. An invalid optional
sub-block, or an invalid selected kind, disables that block or kind and its
dependents locally under rule 3, leaving ordinary social traffic working. Only a
genuine base identity or proof failure refuses the manifest: an interpretation
error inside the optional board is never promoted to an authentication failure,
and a real trust failure is never absorbed into one.

### Exact useful combinations

| Selected functionality | Board blocks and row promises |
| --- | --- |
| Ordinary social and Ranger | Board absent; existing public/private paths |
| Scope-only or reliable complete public relay | public_stream only, initial_public_scopes may be [] |
| Manual appointment/action receipt | actions + guide; per-kind allowed=[], required=[], consistency=none |
| Historical snapshot returned by action | actions + guide; allowed includes snapshot, subscription absent, consistency=none |
| Stream subscription result | actions + guide + public_stream; consistency=stream |
| Snapshot/barrier action | actions + guide + public_stream; consistency=snapshot_barrier; participation separately allowed if needed |
| Private structured conversation without actions | private_messages + guide; participation=false |
| Private descriptor without public subscription | private_messages + guide, participation=true; referenced kinds/channel execution checked by rule 8 |
| Automatic action | Any applicable action combination + separately available local owner delegation/model port; no new remote model feature |

This list describes concrete combinations, not extra profile names on the wire. Application names/rules never enter the capability enum.

## 3. Precise retained and changed schema boundaries

Retain supported EventEnvelope/IntentPayload/HouseEvent definitions and original signing rules subject to BASELINE.md numeric reservations. The internal candidate additions IntentPayload.context=4 and HouseEvent.public_scopes=4 remain the revised first-release fields; absence preserves published old bytes. Existing ActionResult fields 1–18, SignedActionResult, WorldSnapshot, SubscriptionDescriptor, ParticipationDescriptor and signed mutable SubscriptionObservation retain their field numbers/types and signing domains. No opaque attachment envelope or movement into result_body is introduced.

Retain participation/private-wrapper schema shapes in ../retained/, with the capability-dependent availability rules above. No business vocabulary, runtime SQL table, model API or grant authority becomes a wire field. private_messages schema rows may omit public_scope_declaration; publishing a scoped HouseEvent additionally requires the authenticated publishing authority's configured scope declaration and actual registration. A retained, legal old unscoped HouseEvent does not become invalid merely because it has no new row/field.

Structured private messages still use the existing authenticated-decryption/official-producer boundary. Untrusted or unsupported wrapper text gains no metadata authority; retain the original content under existing inbox rules. This revision adds no owner summary, notification presentation or native command; owner_notice remains held, and private receipts do not create a second delivery channel.

The adjacent schemas define the board and selected action rows. PUBLIC-STREAM.md
defines the single public-v1 transport; RECEIPTS.md separates local receipt and
installation status. Stream DTOs are unsigned relay metadata, never a replacement
for signed author bytes. Generated codecs do not establish runtime integration.

## 4. Fixed acceptance scope, not test claims

After implementation authorization, verify: all useful combinations above; absent/broken optional guide/model leaving ordinary social working; each selected-kind dependency violation; trusted proof with no session board for public-only use; invalid base proof still rejected; genuine non-game manual interaction; all PUBLIC-STREAM.md rows and adversarial sequences; all eight RECEIPTS.md combinations and crash/unsupported/ACK transitions; old original manifest and signatures; one actual connection; original-generation logout/final egress. Reuse unchanged budget/atomicity/host tests. This candidate has only document/schema structural inspection, not those runtime results.
