# State transitions and invariants — world interaction v1

Retained action/authority invariants, subject to the current
[baseline](../public-envelope-01/BASELINE.md),
[stream](../public-envelope-01/PUBLIC-STREAM.md) and
[receipt](../public-envelope-01/RECEIPTS.md) rules. Optional execution and
participation definitions do not establish runtime availability.

## 1. Action lifecycle (server)

```
                 pre-admission invalid ──▶ signed rejection receipt (no ledger entry)
                         │ valid
                         ▼
                    ACCEPTED ──leave/closing before permit──▶ CANCELLED
                         │ claim (session authority lock held)
                         ▼
                    EXECUTING ──worker commit + complete──▶ SUCCEEDED
                         │                                   │
                         └──durable business rejection───────┴──▶ REJECTED
```

Invariants:

1. `request_id == signed envelope event_id`. Retry resubmits byte-identical
   SignedPayload; different bytes under the same id is `IDEMPOTENCY_CONFLICT`. A
   semantically corrected retry is a NEW action linked locally as replacement.
2. Terminal states (SUCCEEDED/REJECTED/CANCELLED) are immutable. A changing readiness
   view lives outside ActionResult (`SubscriptionReadiness`).
3. ACCEPTED is transport persistence; EXECUTING is a durable permit; only SUCCEEDED
   proves successful business execution. HTTP success, connection close, timeout,
   lease expiry or a missing worker record never substitute for a terminal result.
4. Pre-admission invalid input gets a signed rejection receipt, not a fabricated
   ledger entry; post-admission deterministic schema/version/deadline failures get
   durable results.
5. `unknown` is exclusively the client's missing-evidence state; it authorizes
   nothing. `ACTION_RESULT_UNKNOWN` sends keep their reservations until reconciled:
   never refund-and-duplicate.
6. Verified duplicate requests may return their already-stored result after session
   expiry; they cannot re-authorize execution. A fresh unrecorded expired/fenced
   request is refused.
7. Status revisions: each ledger transition bumps a monotonic `status_revision`
   (uint64, decimal string in JSON) within the house incarnation.
8. Per-session pending-admission cap (64): leave can
   terminalize the unpermitted set in a bounded transaction. Lock order is fixed
   session → action → execution/closure; no network I/O under the session
   transaction; complete can never reopen authority.

## 2. Execution closure (server, opt-in `execution_closure: 1`)

Session authority and closure obey the following invariants.

Covered-set construction (immutable, frozen at stop transaction time). The
predicate includes ALL same-incarnation historical sessions of the
actor/installation entered at or before the watermark — including sessions
already rotated out by a newer enter or expired, with their still-pending
permits — regardless of how they ended:

```
covered_sessions = { s | s.actor == actor
                      ∧ s.installation == installation
                      ∧ s.house_incarnation == binding.incarnation
                      ∧ s.entered_op_seq <= stop_through_op_seq }
```

- v1: `stop_through_op_seq == op_seq` of the identified LEAVE request (session rule:
  leave(op_seq=N) forbids every enter of this installation with op_seq ≤ N).
- example the referee must reproduce: ENTER10 (permits granted) → ENTER12
  rotates (session10 already stopped, still draining) → LEAVE13: covered =
  {session10, session12} — session10 qualifies through its entered_op_seq 10
  ≤ 13 even though it was stopped by the rotation, not by the leave; a later
  ENTER14 (14 > 13) is NOT covered and untouched by this closure.
- Authority-row mandate: the house keeps ONE persistent authority row per
  (actor, installation, house) even with no session; enter, rotate, leave,
  expiry, admission and first-claim all take that row's lock in a fixed
  order, and the watermark + frozen covered set persist inside the leave
  transaction itself. An empty SELECT FOR UPDATE result or a lost ACK is
  never zero-coverage evidence.
- Zero coverage (enter lost / ACK lost / no sessions): a signed `closed` with an
  explicit watermark and binding is valid; `CLOSURE_NOT_FOUND`, `CLOSURE_NOT_CREATED`,
  HTTP 404, or an old incarnation are NEVER zero-execution proof.

Aggregate phases:

```
phase=closing  (pending_count > 0 or unterminalized admitted requests exist)
   │ every covered request has a durable ClosureRecord
   │ (SUCCEEDED/REJECTED via accepted WorkerResult incl. permanent rejection
   │  tombstone; CANCELLED via the closing gate)
   ▼
phase=closed   (pending_count == 0; content and results_digest immutable)
```

Observation merge rules (client; `ClosureObservation`):

1. Validate the FULL outer binding first: house binding (origin/key/incarnation),
   actor, installation, closure_id, stop request identity and watermark, and that
   the observation answers THIS query's request_id/nonce.
2. Merge by monotonic `observation_revision` within (house, actor, installation,
   closure_id). Timestamps never substitute for it.
3. Equal revision + different `closure_digest` → `CLOSURE_OBSERVATION_CONFLICT`;
   halt and surface, never silently pick.
4. A lower revision never rolls back a `closed` observation; the final closed
   content/digest is immutable.
5. Each status query carries a fresh request_id+nonce; a repeated leave key must
   never be answered with a cached first `closing` observation. The original
   leave AckCore stays immutable and is never reinterpreted.
6. Closure does not undo completed actions and does not wait for committed outbox
   delivery, DM reads, notifications, or later scheduled world consequences of a
   submitted action. Those are not new business executions.
7. Restore: a new coordinated incarnation invalidates old bindings for BOTH permits
   and observations (`CLOSURE_INCARNATION_MISMATCH`); recovery requires
   reconciliation, never reusing lost tombstones/fences/execution identities.

Strong-guarantee reporting: user-visible `remote=confirmed` requires a matching
signed `phase=closed` observation for the house advertising the capability. Legacy
outcome (CLOSED/ALREADY_CLOSED/SUPERSEDED) or `remote=unsupported` is reported as
exactly that.

## 3. Publication readiness and client readiness (two ledgers, never merged)

SERVER side (house-provable facts only):

```
waiting_publication ──▶ published   (house re-verified EVERY registered member
        │                          against its OWN log + declared scope indexes)
        └── member permanently rejected ──▶ failed (diagnosable, never silent omission)
```

1. Barrier B covers the exact committed public outbox membership visible through
   business revision R for the selected scopes; explicit immutable set — never
   `MAX(outbox_id)` or `created_at <= now()`. Identity + full core (incl.
   `member_total` and the full-set `members_digest`) are frozen in the worker's
   business snapshot transaction, then registered in bounded pages of ONE logical
   barrier (every page repeats the full core; full-core idempotency; the house
   seals only when assembled members = member_total and the sorted set hashes to
   members_digest — the final member can never be silently omitted).
2. A member is satisfied only by presence in `world_stream_log` AND every declared
   scope index (stable event_id/seq/incarnation), verified by the house against its
   own database — worker receipts are advisory input. `/v1/push`
   accepted/duplicate is insufficient.
3. The server NEVER claims client replay state. Progress reads return a signed
   `SubscriptionObservation` (publication_state + house log facts + query
   binding); the changing observation is signed separately from the immutable
   terminal ActionResult.

CLIENT side (local facts, computed from the plugin's own durable cursors plus the
latest observation):

```
replaying ──▶ ready        (all scopes replayed through a sealed H AND a valid
   │                        current snapshot after catch-up)
   └── gap ──▶ explicit recovery ──▶ replaying
```

4. Join remains `SUCCEEDED` while publication is `waiting_publication`; readiness
   is a separate monotonic resource and never rewrites the immutable ActionResult
   nor blocks settled business execution or exit confirmation. The anonymous
   stream never carries identity or per-actor progress.

## 4. Participation control state (plugin, durable across restart)

Authority order (each dominates the ones below): owner whole-participation manual →
group takeover (window or explicit) → local grant ∩ descriptor groups → budget
availability → opportunity validity.

| Control state | Scope | Release |
|---|---|---|
| `PARTICIPATION_MANUAL` | whole participation, all windows/revisions/restarts | explicit owner resume only |
| Group takeover `control_reset=window` | (group, original window) | a GENUINELY new window; old tombstone retained to block late plans |
| Group takeover `control_reset=explicit` | group, across windows | explicit owner resume |
| No takeover | per local grant | n/a |

Invariants:

1. Takeover is committed BEFORE submitting the owner's replacement action;
   a server rejection of the owner's request does NOT silently restore agent
   authority.
2. Higher descriptor revision never resets budget/dedupe/takeover state. Changed
   group→kind mapping cannot route a previously controlled kind around its local
   restriction; new kinds need their own local grant.
3. Existing permitted autonomous requests may still complete; world CAS/version
   checks prevent stale overwrite of the owner's replacement.
4. Resume cannot replay expired jobs.
5. Expiry of the current window, an untrusted descriptor, or a stream gap stops
   autonomous actions (reading continues) until a current trusted state is fetched;
   never guess a window from guide prose.

## 5. Opportunity and budget gate (plugin; per autonomous invocation)

Exactly two trigger forms: time eligibility, or validated source arrival plus time
eligibility. `not_before` inclusive, `expires_at` exclusive, both within the named
current window. Per invocation, ALL of:

```
1. currently valid descriptor (revision/window) for the reserved opportunity
2. opportunity reserved by THIS job; KIND_NOT_IN_GROUP else
3. group takeover gate (§4)
4. local grant present
5. expiry re-check (opportunity AND Intent.context.valid_until bound to it)
6. expected capability revision match
7. declared budget group has units AND local rolling/aggregate ceilings have units
```

Batching rule: one host turn may batch several currently eligible opportunities;
each actual invocation independently passes 1–7 for its own kind. One turn charge
per batch; a non-message decision consumes ZERO message units; each outbound
message/DM consumes message budget at its own attempt. A speech opportunity never
authorizes a decision. Direct autonomous DM goes through the protocol-reserved
`direct_message` egress binding (the egress rules below): the same gate sequence
with the group's AND the opportunity's `channels` both including
`direct_message` (effective egress = intersection; the per-opportunity check
runs AFTER the budget/aggregate checks so egress mis-qualification never
masks an exhausted ceiling), spending one turn charge plus the same shared
outbound budget. Response slot per the descriptor's OPTIONAL
`dm_response_slot_key`: declared → every DM-qualified opportunity of the
window (installed or added later) carries exactly that one-use key (a single
shared reply slot for intent replies and DM replies alike; the declaration
is immutable for the window — removal, replacement or new-ID bypass is
RESPONSE_SLOT_IMMUTABLE); absent → distinct per-opportunity keys are allowed
under the same shared budgets and local ceilings (neutral multi-thread
worlds). New message/window/group ids still cannot mint extra budget or
bypass local ceilings in either mode.
A host turn deciding not to act fabricates no succeeded action.

Reservation rule: reserve dedupe/turn/message/notice budgets transactionally before
side effects; crashed unknown sends retain reservations; successful owner messages
reduce the remaining autonomous allowance per configured shared policy; server
business quota is separately authoritative.

## 6. Public stream cursor lifecycle

Use [PUBLIC-STREAM.md](../public-envelope-01/PUBLIC-STREAM.md) exclusively:
`mode=public-v1`, public_boundary/public_frame/public_checkpoint/public_gap,
independent full-public and signed-scope progress, exact raw-byte admission and
immutable baseline/log binding. Earlier scoped transport generations are not
additional modes. Publication is serialized before visible sequence allocation;
rollback may leave numeric holes but never a later-visible lower sequence.

## 7. Snapshot replacement (plugin)

Only complete snapshots of the SAME `state_ref` supersede one another by
`state_revision`; every event is retained by event_id regardless of revision
sharing/order; no plugin reducer, no revision-threshold event dropping. Until a
post-catch-up refresh returns, report the last snapshot's `as_of` as stale — never
fabricated current state. Snapshot refresh is bounded housekeeping under a local
read-state grant (enabled/session gates apply); its handler registers read-only
and can never mutate inventory/decisions/speech. `purpose` labels are routing
hints, never authority.

## 8. Normative authority examples

The same generic behavior applies regardless of application vocabulary:

| # | Input | Required result |
|---|---|---|
| T1 | Valid descriptor, no local grant | Persist facts; zero jobs; suggested budgets grant nothing |
| T2 | Grant + eligible opportunity + remaining budgets | Atomically reserve dedupe+turn budget; at most one candidate turn; message/notice budgets separate |
| T3 | Owner takes over one window group | Cancel that group's unsent work for that window, retain tombstone; other groups unchanged |
| T4 | Speech-triggered turn attempts a controlled decision | Invocation rejected under decision-group gate; no speech-group bypass |
| T5 | Batched decision + comment opportunities | One turn reservation; decision costs zero message units; comment consumes its own message budget |
| T6 | Owner takes over whole participation | All autonomous actions paused; logged-in reading continues; explicit resume only |
| T7 | Higher revision, same window | No reset of budget/dedupe/takeover; mapping changes cannot extend grants |
| T8 | Higher revision, new window | New window budgets; old opportunities expire; participation-manual and explicit-group control persist |
| T9 | Duplicate source / replay / restart | Recover durable reservations/results; no extra job; no unknown-request refund; replay never dispatches directly |
| T10 | Expired window / gap / untrusted descriptor | Stop autonomous actions; obtain current trusted state; no guessed window |
| T11 | Message allowance exhausted, decision opportunity remains | Non-message decision remains eligible within turn grant/ceiling; no forced statement |
| T12 | Gift/item arrives after turns used | Store fact and opportunity; mint no turns; owner may act explicitly |
| T13 | Same item/result re-emitted under new revision/transport id | Stable consumed/reserved key preserved; not rerun |
| T14 | Owner locks decision group but speech wakes host | Speech cannot authorize vote; scene/item follow their own gates |
