# Ordered relations

`RelationOrder` makes a relation action comparable without the receiver holding
anything between two events. This document fixes the external contract: the
capability declaration, what the author signs, admission, conflict and recovery,
the two reconciliation endpoints and where an admitted original is delivered.
Relation events add no signing domain or baseline; their read requests use the
separate identity credential specified in [READ-AUTH.md](READ-AUTH.md). Wire changes
are recorded in CHANGES.md.

## 1. Capability `relations.ordered`

The declaration is a top-level `relations` member of the exact authenticated
manifest body — the same bytes the ManifestProof digest covers and the same
trust path as every other capability (TRUST.md). It is not part of
`world_interaction`, is never read from a cache, a second endpoint or a handle
from an earlier fetch, and is parsed only after the proof and the current
authorization have been confirmed.

| Served manifest | Reader verdict |
| --- | --- |
| `relations` absent | unsupported |
| `relations` an object whose `ordered` is the integer `1` | supported |
| `relations` present but not an object | capability-unknown |
| `relations` present, `ordered` absent | capability-unknown |
| `ordered` any other value — `0`, a negative, `1.5`, `"1"`, a higher level | capability-unknown |
| body is not valid JSON, or not a JSON object | capability-unknown |

JSON writes the same number more than one way. `1.0` and `1e0` parse to the
integer `1` and are therefore `supported`; the contract is the parsed numeric
value, not its spelling, and no implementation should carry a second parser to
tell the spellings apart. A publisher emits the integer `1`.

capability-unknown is **not** unsupported and is **not** auto-downgraded to the
legacy rules. There is no "at most the highest level I know" compatibility: what
a level this build does not know means is not this build's to guess. Extra
unrelated members inside `relations` do not change the reading — the contract
names `ordered` and only it — but a publisher declares exactly `{"ordered": 1}`
and nothing else.

A House may declare it only when its runtime genuinely has the capability: a
persisted signing key, a configured origin and incarnation, and a successfully
claimed binding. Missing any of them, it serves **no** `relations` member at all
and refuses to start on a source document that declares one on its behalf.
`{"ordered": 0}` is not how a House says no; absence is. The member is merged
before the body is serialized, so the digest, the validator and the proof are
each computed once over the capability-bearing bytes — never sign a body and
then add the field.

A verified binding proves identity, not capability. A `supported` answer is the
House's own signed statement, not a promise that it executes honestly or holds
complete history, and a push receipt is transport acceptance and nothing more.

## 2. What the author signs

`order` sits inside `FollowDeclared` / `FollowRevoked`, so it is covered by the
ordinary EventEnvelope inner signature and by the CID, under the unchanged rules
in SIGNING.md. The author's signature therefore covers the action (declare or
revoke), `followee_popclaw_id`, and `order.seq`, `order.house_key` and
`order.resolves` together.

The receiver verifies the **author's** signature independently, before any
effect. A House signature, a manifest proof, a relay position or an accepted
push never substitutes for it, and a House's summary of an event is never
storable as the event.

`order` absent elides entirely. `order` present but entirely default still emits
its tag and a zero length, and those two forms are byte-distinct: presence is
what activates ordered mode, so a canonicalizer that drops empty sub-messages
would make the two modes indistinguishable. `seq` crosses every JSON boundary as
a decimal string; a JavaScript Number stops being able to represent its own
successor above 2^53.

## 3. Admission

Applied by every receiving end — server and client — in this order. The order is
load-bearing: unresolved conflict is judged **before** magnitude.

| Check | Rule on failure |
| --- | --- |
| `order` absent | Legacy mode. Legal only while this edge has no ordered evidence |
| `order` present | Ordered mode, unconditionally. A malformed ordered event is illegal new format, refused, never downgraded to the legacy rules |
| `seq` = 0 | Refuse. 0 is the proto3 default and cannot be told apart from unset inside a present `order` |
| `seq` > 2^63−1 | Refuse. The effective domain is 1..=2^63−1, narrower than the wire type |
| `house_key` empty | Refuse. It is required once `order` is present |
| `house_key` not this receiver's independently established House key | Refuse. An event scoped to another House is not applied to a local edge |
| `lorehouse` non-empty and different from `order.house_key` | Refuse (section 4) |
| `resolves` non-empty | Recovery statement (section 5), never an ordinary action |

The `seq` bound is a deliberate narrowing, stated because a silent one is the
failure it prevents. A store with no unsigned 64-bit integer records a larger
value as a negative number, after which comparison runs backwards in both
directions — a stale event reads as newer and a current one as stale. Both ends
refuse at admission rather than cast and hope. A per-edge counter never
legitimately approaches the bound.

Per-edge state is namespaced by `(house_key, author, followee)`. What the
contract requires of any store is that isolation: evidence signed under one
House key is never written into, nor reinterpreted as, another's.

It does **not** require a store to hold one House. An implementation whose
projection is keyed by `(follower, followee)` alone cannot represent two
namespaces at once, and such a store must refuse ordered mode on an edge that
already holds evidence under a different House key rather than run on top of
it, leaving the old rows untouched. That is a property of that storage shape,
not of this contract. A client is expected to aggregate the edges it holds
across every House it participates in — the complete picture exists only
locally — and nothing here forbids it.

| Arrival | Outcome |
| --- | --- |
| Same `event_id` already judged terminally on this edge | Return the stored verdict; a terminal verdict is never re-classified |
| Same `seq`, different `event_id` | Fork (section 5). Never treated as a duplicate — dedup is by `event_id`, never by position |
| `seq` above the edge's applied position, edge not conflicted | Apply. This is also how a legacy edge adopts ordered mode |
| `seq` below the edge's applied position | Stale: recorded, no effect, and deliberately not an error — a late old event is ordinary |
| Any ordinary event on a conflicted edge | Blocked and pending. Magnitude never clears a fork |
| `order` absent on an edge with ordered evidence | A visible refusal, never a silent application — applying it quietly is the downgrade path |

Gaps are legal. A crash may skip a number; nothing may reuse one. Arrival is not
required to be `current + 1`, and contiguity is never a condition of applying.

## 4. `lorehouse` and `order.house_key`

`envelope.lorehouse` keeps its proto3 default meaning: empty is "the House you
are talking to". The rule is conditional and must be written as such —

> only when `envelope.lorehouse` is non-empty must it equal `order.house_key`.

An empty `lorehouse` with a present `order` is well-formed and ordinary. Do not
promote this to an unconditional equality: that silently tightens a defined rule
through documentation and refuses events the format allows.

Two author-written fields agreeing proves only that the author was internally
consistent. Both are inside the same signature, so an author who lies lies in
both. Cross-House forgery resistance comes from one comparison and only one:
`order.house_key` against a House key the receiver established trust in
**independently** — the pin under TRUST.md, or the verified delivery source of
the frame. A receiver that checks `order.house_key` against `envelope.lorehouse`
has checked nothing.

## 5. Conflict and recovery

A fork is two different `event_id`s at the same `(edge, seq)`. The edge is
marked conflicted; the last applied effect stands and only the reported
confidence drops. An ordinary event never resolves a fork, whatever its `seq`:
a larger number proves the author saw one branch, not that they abandoned the
other.

A recovery names in `resolves` the `event_id`s it settles. Three standings,
deliberately not two:

- **Valid** — every named id is a real event on this edge and the recovery's own
  `seq` is strictly above every named one's. A statement cannot settle something
  it does not come after.
- **Awaiting reference** — something it names has not arrived. Not invalid:
  deciding it invalid on sight would let any relay void a recovery by
  withholding one event it names. It is re-judged when the missing original
  arrives.
- **Invalid** — it claims to settle something at or above its own position, so
  it can never become valid. Its original is kept as evidence, but keeping an
  original is not granting it effect, and it must not be able to fork an edge.

Coverage is **transitive**, and `resolves` is not defined solely by "every
branch": a valid recovery inherits the coverage of a valid recovery it names, so
a chain the author deliberately extended does not have to re-enumerate every
ancestor. Inheritance flows only from a Valid statement — an Invalid one carries
nothing ever, an Awaiting one carries nothing yet.

A recovery settles the edge when it is Valid and covers every event currently in
conflict other than itself. Candidates are searched among all events on the
edge, not only the conflicting ones: a recovery is usually nobody's sibling. A
candidate that another candidate covers is succession, not a tie. Exactly one
sufficient candidate settles the edge; zero or more than one leaves it
conflicted. Two recoveries conflict when both are Valid, their `resolves` sets
overlap and neither names the other. Same `seq` with different ids is a fork
whatever either event claims — a `resolves` list does not excuse it.

Re-judgement is a pure function of the full evidence set. Nothing is filtered
out for being superseded, and a late original re-opens a settled edge; delaying
one delivery is otherwise exactly how a relay buries a conflict. A settling
recovery does not reach forward in time: if an ordinary event has since applied
above its position, the edge stays where it is. Ordinary events the fork had
blocked then become decidable and advance in `seq` order above the resulting
head, so the same set of originals reaches the same end state whatever order
they arrived in.

A client that does not adjudicate recovery keeps the edge **pending** and
records the original and every delivery attempt intact. It must not drop
`resolves` and apply the event as an ordinary Follow or Unfollow.

## 6. `GET /v1/relation-snapshot`

The frozen reconciliation baseline: what a House believes a requester's
relations already are, as of one identified instant, for a client that has been
away or fell below the retention floor.

Authentication is `popclaw-identity-read-v2` in `x-popclaw-inbox-token`, with
purpose `relation-snapshot`, under [READ-AUTH.md](READ-AUTH.md). Verify the exact
purpose/audience-bound ASCII message, canonical four-segment header and inclusive
60-second window before object access. The authenticated requester identifies
whose relations are being asked for; there is no unauthenticated or relaxed mode.
A House-issued inbox session token is not snapshot authentication, and the obsolete
three-segment self-signed form is refused.

Request: `cursor` (opaque continuation, valid only for the build that issued it)
and `limit` (default 100, clamped to 1..500). One entry is always served whole.

Response: `checkpoint_id`, `log_generation`, `floor`, `watermark`, `entries`,
`next_cursor`, `complete`. Every 64-bit value — `log_generation`, `floor`,
`watermark`, and each entry's `applied_seq` — is a decimal **string**. The same
quantities appear as text in the stream's `id:` line, so a numeric field here
would make one quantity disagree with itself depending on where it was read.

Each entry carries `follower_popclaw_id`, `followee_popclaw_id`, `state`
(`active`, `revoked` or `undecided`), `revoked_at`, `applied_seq`,
`applied_event_id`, `conflicted`, `evidence_event_ids`, `state_event_id` and
`state_proof` (`applied_event`, `source_event` or `unknown`).

- A checkpoint is materialised once and never updated in place. Every page of
  one snapshot carries the same `checkpoint_id`.
- `watermark` is the strict published prefix: the highest delivery `seq`
  published to this recipient when the baseline was taken. There is exactly one
  watermark semantic — no lower-bound variant that may contain unpublished
  facts.
- A client may adopt the watermark **only** after a complete pagination of that
  same checkpoint ending in `complete: true`. `complete: false` means unknown,
  never "fully synced".
- An absent entry is **not** an unfollow. A revocation is carried as an explicit
  tombstone (`state: "revoked"`). Only verified author evidence adds an edge and
  only a verified revoke retires one, so a partial or hostile snapshot adds
  nothing and deletes nothing.
- `state`, `applied_seq`, `applied_event_id`, `conflicted` and the timestamps
  are House **hints**. The client re-derives them from the originals named in
  `evidence_event_ids`, which is every original the House holds on that edge,
  not only the ones it considers unsettled. `state_proof: "unknown"` is an
  honest answer; it must not be replaced by inferring a proof from the state and
  the timestamps. `state_proof` says where to look for the original that
  settles an edge — it is never permission to skip verifying that original, and
  a value the client does not recognise leaves the edge unverified rather than
  assumed.
- A House never serves a checkpoint whose content reaches past its own
  watermark. When it cannot take a consistent one it answers `503` and a retry,
  never an incomplete baseline under a watermark.
- Honest limit: relations predating the delivery index carry no delivery number
  and can never be repeated on the stream. They appear as baseline-only state.

| Condition | Status |
| --- | --- |
| Missing, malformed, stale, unsupported or invalid identity credential | `401` |
| Server cannot establish ReadAudience | `503 read_authority_unavailable` |
| Authenticated requester refused by object policy | `403` |
| A cursor this House cannot read | `400` — refused, never reinterpreted |
| Continuation whose checkpoint is unknown, aged out, or from another log generation | `410` — start a fresh snapshot; restarting is always safe |
| No consistent checkpoint could be taken within the request's budget | `503` and retry |
| Storage unavailable | `503` |

## 7. `GET /v1/relation-evidence/<event_id>`

One relation event's signed original, to a participant of its edge. Authentication
uses `popclaw-identity-read-v2` with purpose `relation-evidence`, under
[READ-AUTH.md](READ-AUTH.md); a snapshot-purpose credential cannot open this route.
There is no relaxed mode. Credential failures receive `401`; unavailable server
ReadAudience receives `503 read_authority_unavailable`. Object lookup follows
successful authentication and preserves the empty-`404` rules below.

Response: `event_id`, `payload_type` (`follow_declared` or `follow_revoked`),
`envelope_b64` — base64 of the **verbatim stored envelope bytes**, never
re-encoded, because a re-encode drops any field the serving House's schema does
not know and that is precisely how a newer author's event stops verifying — and
`hints` (`event_status`, `seq`, `edge_applied_seq`, `edge_applied_event_id`,
`edge_conflicted`). `seq` and `edge_applied_seq` are decimal strings or null.

Three constraints:

1. **Relation payload types only**, checked on the type tag before anything else
   in the record is read. A read keyed by `event_id` over every stored payload
   would leak DM metadata to anyone who could guess or harvest an id.
2. **Participants only.** The requester must be the edge's follower or followee,
   both taken from what the House verified at ingest — never from the request.
3. **Hints, not facts.** Everything the House computed is reported under `hints`
   and nowhere else. The client re-verifies the returned bytes through its
   ordinary ingress — signature, CID, per-type authorization — before anything
   takes effect.

Every object refusal after authentication is the same empty `404`, byte for byte:
unknown event, an event of
another type, or a relation event the requester is not on. A `403` would confirm
the event exists and a distinct "not a relation event" would confirm that some
other event carries that id. Existence is itself the secret, so the refusals are
indistinguishable. A `404` on one item during a reconciliation run skips that
item; it is evidence of nothing and must not fail the run.

## 8. Delivery

An admitted relation original is owed to **both** participants — the author and
the followee — on their personal streams. It is owed for every legitimately
admitted original, not only for those that moved a projection: gating delivery
on "it applied" hides exactly the fork evidence a recipient needs most, leaving
them believing one branch is the whole story with no way to detect the fork.
The delivery obligation commits in the same transaction as the fact.

Per-recipient delivery numbers are assigned after commit, under that recipient's
own counter, so for one recipient allocation order is commit order — the only
order a per-recipient cursor reads. Transport is the ordinary private stream
`GET /inbox/:popclaw_id/stream`: named SSE `envelope` frames carrying the
complete signed EventEnvelope, with `id: <log_generation>.<seq>`.

A cursor that cannot be honoured is announced as a named `cursor-reset` event
carrying `{"reason", "log_generation", "floor", "reconcile": "snapshot"}`, with
`log_generation` and `floor` quoted and no `id:` line — so it cannot move a
cursor by arriving and is invisible to a client that does not listen for it.
Reasons are `unreadable` (a cursor the House cannot parse), `generation` (a log
rebuild) and `below_floor` (retention). Everything resolves downward, towards
re-delivering what the client may already hold and never towards skipping what
it may not; the client pays the debt through sections 6 and 7.

`FollowDeclared` and `FollowRevoked` are **silent**: they raise no notification
on the receiving side, ordered or not. Notification is a separate downstream
step, not a missing optimisation.

**A `FollowDeclared` or `FollowRevoked` original is never published on a public
stream, whether or not it carries `order`.** Its delivery is the two personal
streams and nothing else. A conforming House does not stage one into a public
outbox, does not serve one on a public stream's live path, and does not serve
one from that stream's history window, from a cursored replay of it or from a
projection baked out of it — a filtered page still advances the scan
position, so filtering never costs a later legitimate post. A client that
receives one on a public channel treats it as a channel it must not be consumed
on: it refuses the frame as business-inadmissible, admits it to no relation
state, and derives no relation, notification or authorization from it. The
refusal never swallows a signature error. Public eligibility is answered before
the CID and the author signature are checked, so a cheap early refusal is
allowed and the claimed author and CID of a refused frame are not a verified
identity: such a refusal is recorded as unverified, and a signature failure
already found on a publicly eligible body keeps its own reason.

The only position a refusal may release is the **transport resume position** —
the position a client keeps solely to know where to continue reading a
connection. Releasing it is not evidence that a signature verified, that any
business completed, that a relation was ordered, or that recovery is complete.
It may move only after the raw bytes, their true byte hash, the refusal reason,
the trusted connection source and the corresponding transport position have all
been durably retained, in the same atomic step that moves it; if that evidence
is not written, the position does not move. A refusal never occupies a verified
event's deduplication identity, so the same legitimate original arriving
afterwards on a personal stream is still processed in full. A position that is
also used to assert that a stream has been completely received — the public and
scope lane cursors and the checkpoints of PUBLIC-STREAM.md — is not a transport
resume position and is never moved by a refusal. A consumer may be stricter and
stop instead: refusing the frame, leaving its position where it is and declaring
its binding unavailable is conforming, and nothing here obliges a consumer to
skip. None of this relaxes the reserved-occurrence stop rule of BASELINE.md,
which answers a baseline violation, not a business refusal.

This obligation binds the receiving client only. A House that, after full
verification, keeps relation rows out of its own public log and emits its
checkpoints exactly as PUBLIC-STREAM.md specifies owes no refusal ledger of its
own, and retains its originals.

`FollowType.PUBLIC` describes the relation's nature — the relation may be
looked up, and is not secret. It is not an instruction to broadcast and confers
no public-stream right. A House that broadcasts these originals anyway is not
conforming to this version; nothing here can stop it, but a client must not
read its behaviour as permission.

PRIVATE-typed `FollowDeclared` / `FollowRevoked` are never admitted through
`/v1/push`.

## 9. Implementation status

The external contract above is fixed now and complete enough to implement
against. This bundle ships the message definitions, the canonical bytes and the
structural guards only. This table says what a conforming runtime owes; whether
any particular deployment has met it is recorded in that deployment's own
conformance record, against a pinned repository, commit and test run, and never
asserted here.

| Surface | In this bundle | Required elsewhere |
| --- | --- | --- |
| `RelationOrder` bytes, presence, CID, `seq` domain | Proto, codecs and vectors | Each adapter applies the same rules at actual ingress |
| Capability declaration and reading | Contract fixed here | Real manifest assembly, proof and current-authorization check |
| Ordered admission and the per-edge namespace | Contract fixed here | Not delivered — no admission engine in this bundle |
| Conflict, recovery adjudication and re-judgement | Contract fixed here | Not delivered — no adjudicator in this bundle |
| `/v1/relation-snapshot`, `/v1/relation-evidence/<event_id>` | Contract fixed here | Not delivered — no server in this bundle |
| Personal delivery and `cursor-reset` | Contract fixed here | Not delivered — real per-recipient log, retention and fences |
| Public-stream exclusion of relation originals | Contract fixed here, and enforced by the shared public-eligibility predicate: a relation original is answered `NOT_PUBLIC`, ordered or not | No relation original may appear on a public stream's publication, live path, history window, cursored replay or baked projection. This is a source bundle, not a deployed service, so it carries the rule and the predicate rather than a public exit that could violate one; a House applies the rule at every public exit it actually operates. A House that supports relations still accepts originals through its ordinary verified write entrance and still owes personal delivery |

A runtime without a complete business implementation of a surface declares the
capability **absent** rather than accepting an ordered event and degrading it.
Accepting an ordered relation and applying it under the legacy rules is the
downgrade the whole mode exists to make impossible, and it is worse than
refusing the event: the author has burned a position they can never reuse.
