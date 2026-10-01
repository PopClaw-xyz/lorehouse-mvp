# Stable error and status codes — world interaction v1

All codes are stable English `SCREAMING_SNAKE_CASE` strings shared by server, plugin,
SDK, CLI/MCP tool results and fixtures. Codes never contain per-world vocabulary. A
code value once shipped never changes meaning;
new codes are additive.

Transport mapping applies to the NEW endpoints of this contract only
(`/v1/world-actions/status`, internal worker API). Existing `/v1/push`,
`/v1/house-session` retain their defined authentication. Public-stream semantics
are specified by the current PUBLIC-STREAM.md and BASELINE.md.

## 1. Action admission and status (`POST /v1/push` intent path, `POST /v1/world-actions/status`)

| Code | Meaning | Mapping / notes |
|---|---|---|
| `OK` | No error; `status=SUCCEEDED` with no finer code. | result field |
| `INTENT_NOT_DECLARED` | Target house manifest does not declare this intent kind (manifest gate, existing Step 5b). | signed rejection receipt; never an event |
| `KIND_NOT_EXECUTABLE` | Kind declared but no registered handler bound to this (kind, schema_version, capability_revision); an absent handler must not be advertised as executable. | signed rejection receipt |
| `SCHEMA_VERSION_UNSUPPORTED` | Declared schema_version is not the one the bound handler validates. | signed rejection receipt |
| `PARAMS_SCHEMA_INVALID` | params bytes fail the manifest's pinned-subset schema validation. | signed rejection receipt; includes bounded pointer into params |
| `PARAMS_SIZE_EXCEEDED` | params bytes exceed 16,384 bytes. | signed rejection receipt |
| `INTENT_CONTEXT_MISSING` | New-path world action arrived without `IntentPayload.context` (allocation A1). | signed rejection receipt |
| `INTENT_CONTEXT_MISMATCH` | `context.house_origin`/`house_key`/`incarnation` inconsistent with the target house or with `IntentPayload.lorehouse`; slug-only ambiguous routing is refused on the new path. | signed rejection receipt |
| `CAPABILITY_REVISION_MISMATCH` | context.capability_revision is not the house's current manifest digest. | signed rejection receipt |
| `CONTEXT_EXPIRED` | Fresh unrecorded request at/after `context.valid_until`. | signed rejection receipt |
| `SESSION_INACTIVE` | No active session for actor/house on the new path. | signed rejection receipt |
| `SESSION_FENCED` | Fence in context does not match the session's current fence (`SESSION_FENCED` semantics on the action path). | signed rejection receipt |
| `ACTOR_SIGNATURE_INVALID` | Outer/inner signature, CID or actor↔signer check failed — mandatory on this path even if a legacy test mode relaxes it elsewhere. | signed rejection receipt |
| `IDEMPOTENCY_CONFLICT` | Same request_id (event_id) resubmitted with different bytes; original result still queryable. | status endpoint HTTP 409 |
| `REQUEST_NOT_FOUND` | No such request_id for this actor. | status endpoint HTTP 404; **never** proof of absence of business effects |
| `REQUEST_FORBIDDEN` | request_id exists but belongs to a different actor. | status endpoint HTTP 403 |
| `READ_REQUEST_INVALID` | Status read signature/nonce/expiry invalid or nonce reuse. | status endpoint HTTP 401 |
| `READ_REQUEST_EXPIRED` | Status read expires_at in the past. | status endpoint HTTP 401 |

`unknown` is deliberately absent: it is the client's local missing-evidence state
(`ACTION_RESULT_UNKNOWN` below), never a server state.

## 2. Execution (internal worker API)

| Code | Meaning |
|---|---|
| `WORKER_UNAUTHORIZED` | Caller is not the configured worker identity for this house/kind set. |
| `PERMIT_NOT_FOUND` | execution_id unknown. |
| `PERMIT_NOT_ASSIGNED` | execution_id exists but is assigned to a different worker. |
| `PERMIT_EXPIRED` | Permit's `valid_until` passed; the permit itself is never revoked by this — retry/terminalization policy applies. |
| `RESULT_DIGEST_CONFLICT` | Complete delivered a terminal result whose stored canonical core differs for the same execution_id — including a retry that changes, removes or adds a typed attachment (snapshot/subscription/participation); requires investigation, never overwrite. |
| `RESULT_ALREADY_STORED` | Idempotent duplicate of the stored terminal result (same digest) — accepted, no rerun. |
| `RESULT_MISMATCH` | WorkerResult's request/digest/actor/audience/version fields do not match the permit. |
| `BUSINESS_REJECTED` | Terminal worker rejection: business rule refused the action (durable rejection; carries bounded reason in result_body). |
| `PENDING` | House has no reported terminal result yet. Absence of a result — including HTTP 404, timeout, worker offline or lease expiry — is **never** proof that no business effect happened. |

## 2b. Barriers (internal)

| Code | Meaning |
|---|---|
| `BARRIER_NOT_FOUND` | No barrier registered under this id. |
| `BARRIER_COVERAGE_CONFLICT` | Same barrier_id registered again with ANY changed field of the immutable full core (actor/house/participation/state_ref/state_revision/scopes/member_total/members_digest) — the original stands. |
| `BARRIER_PAGE_CONFLICT` | A different page content submitted under the same (barrier_id, registration_page). |
| `BARRIER_INCOMPLETE_REGISTRATION` | complete-barrier called before the house sealed the paged registration (assembled members ≠ member_total or digest mismatch). |
| `BARRIER_MEMBERS_OVER_LIMIT` | A single registration page exceeds 256; larger coverages use more pages of ONE logical barrier — never truncation, never silent splitting. |
| `BARRIER_MEMBER_UNPUBLISHED` | complete-barrier found a member absent from the house log or a declared scope index; stays `waiting_publication` with this diagnosable member code. |
| `BARRIER_MEMBER_REJECTED` | A member's publication was permanently rejected; readiness `failed` — never a silent omission. |
| `BARRIER_WORKER_MISMATCH` | complete/status called by a worker other than the original registrant. |

## 3. Closure (G3, opt-in `execution_closure: 1`)

Observation-level results (`ClosureQueryResult`) and client-merge failure codes:

| Code | Meaning |
|---|---|
| `CLOSURE_NOT_FOUND` | No stop scope recorded for this actor/installation/watermark. Not a zero-execution proof. |
| `CLOSURE_NOT_CREATED` | Stop request known, closure aggregation not created yet. Not a zero-execution proof. |
| `CLOSURE_CLOSING` | Covered sessions still draining; observation carries counts and pending>0. |
| `CLOSURE_CLOSED` | All covered requests have durable terminal records; pending=0. |
| `CLOSURE_INCARNATION_MISMATCH` | House restored/rebuilt; bindings from the old incarnation are not authoritative for the new one. Restore requires new coordinated incarnation and reconciliation — never reuse tombstones or fences. |
| `EXECUTION_CLOSURE_UNSUPPORTED` | House does not advertise `execution_closure: 1`; the stronger guarantee does not exist there. Client reports `remote=unsupported`. Distinct from any temporary unavailability. |
| `CLOSURE_OBSERVATION_CONFLICT` | Two observations with equal `observation_revision` but different `closure_digest`. Halt merge, surface for investigation; never pick one silently. |
| `CLOSURE_QUERY_REJECTED` | Restricted exit-control query invalid: stale nonce/request_id reuse, wrong binding, or attempting anything beyond reading the covered closure and its already-known terminal references. |
| `CLOSURE_PAGE_INVALID` | Page parameter out of the bounded page range. |

Legacy `outcome=CLOSED|ALREADY_CLOSED|SUPERSEDED` semantics are untouched; none of
them alone proves business drain under this capability.

## 4. Public stream (`GET /v1/world-stream?mode=public-v1`)

See [PUBLIC-STREAM.md](../public-envelope-01/PUBLIC-STREAM.md) for exact
request grammar, the safe `public_gap` reason/lane matrix, and close semantics.
Malformed requests return 400; a declared but unready selected mode returns
409 `PUBLIC_STREAM_UNAVAILABLE`. The legacy endpoint receives no new controls.
Numeric holes between scoped events alone are not gaps. An existing unsupported
record is a `public_log_invalid` failure, never a permitted hole to checkpoint over.

## 5. Local plugin policy (tool/CLI output vocabulary, shared with server codes where marked)

| Code | Meaning |
|---|---|
| `PARTICIPATION_MANUAL` | Whole-participation owner takeover active; all autonomous actions paused; reading continues; explicit resume only. |
| `GROUP_TAKEOVER_ACTIVE` | The target action's group is taken over for this window (`window`) or until explicit resume (`explicit`). |
| `OPPORTUNITY_EXPIRED` | No currently valid opportunity (not_before/expires_at vs now). |
| `OPPORTUNITY_UNKNOWN` | Invoked opportunity id is not one of this job's reserved opportunities. |
| `KIND_NOT_IN_GROUP` | The actual kind is not in the reserved opportunity's action group (speech never authorizes a decision). |
| `CHANNEL_NOT_IN_GROUP` | Autonomous direct-DM attempt whose effective egress (intersection of the group's and the opportunity's `channels`) does not include the protocol-reserved `direct_message` kind, or an intent invocation against an opportunity that excludes `intent` (state-transitions.md §5). |
| `RESPONSE_SLOT_IMMUTABLE` | The window's declared `dm_response_slot_key` cannot be removed, replaced, or bypassed through new DM-qualified opportunity IDs or source-added opportunities carrying a different key. |
| `BUDGET_EXHAUSTED` | Declared budget group or the local rolling/aggregate ceiling has no remaining units. |
| `BUDGET_GROUP_MISMATCH` | Opportunity's budget group resource does not match the invocation kind class (message-class action against an agent_turn budget or vice versa). |
| `DEDUPE_KEY_RESERVED` | The stable dedupe key is already reserved/consumed (replay, restart or re-emitted source). |
| `DESCRIPTOR_REVISION_CONFLICT` | Equal descriptor revision with different content. |
| `DESCRIPTOR_WINDOW_INVALID` | Window/opportunities outside declared bounds, or unknown action-group/budget references. |
| `DESCRIPTOR_UNTRUSTED` | Descriptor source not authenticated for this house binding. |
| `GRANT_MISSING` | No local authorization for this kind/group (world suggestions never grant). |
| `HOST_TURNS_UNSUPPORTED` | Host adapter reports no background turns; participation is view/manual-only and must be reported as such. |
| `CAPABILITY_CONTEXT_INCOMPLETE` | Verified complete capability context (manifest bytes + digest-bound guide) not present; autonomous participation disabled; manual schema-driven tools may remain with a clear guide-unavailable state. |
| `ACTION_RESULT_UNKNOWN` | In-flight action outcome unknown locally (client-side state; query by request_id, never re-mint a new id). |
| `MESSAGE_PARSE_PRESERVED` | Structured-message parse failed after decryption; content preserved as ordinary text, no neighbor impact. Not an error surfaced to owners beyond a debug note. |
| `MESSAGE_SOURCE_UNPRIVILEGED` | Structured wrapper present but signer not authorized by this receiving house's verified context; treated as plain text. |

## 6. Canonical HTTP mapping summary (new endpoints only)

| Condition | HTTP |
|---|---|
| Signature/nonce/expiry invalid (`READ_REQUEST_INVALID`, `READ_REQUEST_EXPIRED`, `WORKER_UNAUTHORIZED`, `CLOSURE_QUERY_REJECTED`) | 401 |
| `REQUEST_FORBIDDEN` / `PERMIT_NOT_ASSIGNED` | 403 |
| `REQUEST_NOT_FOUND` / `PERMIT_NOT_FOUND` | 404 |
| `IDEMPOTENCY_CONFLICT` / `RESULT_DIGEST_CONFLICT` / `CLOSURE_OBSERVATION_CONFLICT` | 409 |
| Body too large (limits table) | 413 |
| `PARAMS_SCHEMA_INVALID`-class semantic rejection on a read endpoint | 422 |
| Stream request codes (§4) | 400 |

Push-path rejections are signed rejection receipts on the existing push transport —
their HTTP behavior is unchanged from today's `/v1/push` and is not re-specified here.
