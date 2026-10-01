# Complete public facts with optional scope progress

Normative public-envelope-01 candidate. `public-v1` is the single revised first-release optional mode. The old unqualified endpoint retains its published wire format for existing clients. Original EventEnvelope bytes/CID/signature remain unchanged.

## 1. Negotiation and exact request

The authenticated block MUST declare `envelope_baseline=public-envelope-01`. The declaration covers the complete safe public set admitted under this baseline in this log incarnation, not every structure accepted by any historical implementation. Missing or different baseline is unsupported. See BASELINE.md for mandatory raw-wire checks and log transitions.

Select only from the valid, authenticated `world_interaction.public_stream` block specified in SPEC.md. A public-only block needs no actions, guide, session ACK, result key or worker. The existing trusted pin/HouseBinding and detached complete-manifest proof still apply. An independently selected safe ordinary legacy path may remain available, with the same client raw-wire checks at all boundaries; switching a resource first stops/joins its current sole receiver. Failure after selecting this mode is a failed selected subscription, not an automatic fallback or second socket.

```
GET /v1/world-stream?mode=public-v1&incarnation=<log>&public_after=<uint64>&cursors=<vector>&limit=256
```

`mode`, `incarnation`, `cursors` are required. `public_after` is optional: present means subscribe to **all safe public persistent facts**, absent means scope-only. Explicit `0` is not absence. `cursors` is the existing canonical ASCII comma-separated sorted vector `scopeA:0,scopeB:123`, empty allowed only when public_after is present. Labels match `[A-Za-z0-9_-]{4,64}`, maximum 32 unique scopes, strict ascending byte order. Decimal positions match `0|[1-9][0-9]*`, ≤2^64−1; no signs, spaces, leading zeros or JS number rounding. URL-encode once as a query value. `incarnation` matches the advertised `[A-Za-z0-9_-]{1,64}`. limit optional 1..512, default 256.

No credentials/cookies/Authorization, actor/session/participation/barrier/descriptor values, Last-Event-ID, after, kinds, scoped, repeated/unknown query parameters or extra ambiguous paths. SSE has no `id:`. No automatic user credential attachment on reconnect. Scope labels are public filters, not private group access or network anonymity.

Old endpoint calls have no mode and keep their old allowed parameter grammar. Old server rejection of mode is unsupported, never successful negotiation. A new server whose valid mode block cannot currently serve returns 409 `PUBLIC_STREAM_UNAVAILABLE`; malformed parameters return 400. Once SSE begins, gaps below are explicit and close the connection. New optional frames are never sent to an old unqualified request.

## 2. Membership: complete public set, not a typed complement

The complete public lane is not a pseudo-scope and does not mutate signed scopes. With public_after present, **every** eligible public fact after that lane's cursor is selected, even if it has scopes outside the requested set. Requested scopes add independent historical coverage; they do not narrow the full public lane. With public_after absent only matching scoped HouseEvents are selected.

Eligibility requires existing identity/body-specific admission, exact original CID/signature validation, understood unambiguous envelope structure, public privacy policy and durability. It never requires understanding a HouseEvent business body, a local projection/handler, JSON, or a positive business schema_version. In particular the older HouseEvent kind admission grammar (length ≤128, `^[a-z0-9-]+\.[a-z0-9_]+$`) remains legal; do not apply the narrower action-kind schema to public opaque transport. Existing valid zero/default scalar encodings retain their established signing semantics.

| Tag/body | Complete public lane | With signed public_scopes absent | With signed public_scopes present |
| --- | --- | --- | --- |
| 11 InviteRequest; 12 QuestDispatch; 13 QuestResult; 14 InviteVerified | Admit only with existing author/House/assignee/evidence rules | Public lane | Not a field on these bodies; no synthetic scope |
| 15 RangerRegistration; 16 WatchDispatch; 18 WatchCancel | Admit legal durable public events | Public lane | Not applicable |
| 17 WatchHeartbeat | Existing liveness-only ingestion; no durable public publication | Neither | Not applicable |
| 20 FollowDeclared; 21 FollowRevoked | A relation original is a personal event owed to its two participants (RELATIONS.md §8); never a public fact, ordered or not, and never made one by `follow_type=PUBLIC(0)` | Neither | Cannot be made public by scope metadata |
| 25 Reply; 27 Post | Admit complete legal public body | Public lane | Not applicable |
| 26 DirectMessage | Never public, including ciphertext/placeholder/attachments | Neither | Cannot be made public by scope metadata |
| 28 Profile | Admit legal Layer 1 public Profile, including its defined public taste subset, with no raw occurrence of reserved field 8 | Public lane | Not applicable |
| 30 Mark; 31 MarkRevoked | Never expose original marker identity/event publicly | Neither | Cannot be made public by metadata |
| 32 PollDispatch | Existing transient dispatch, not this durable log | Neither | Not applicable |
| 33 PollReport | Admit legal public report | Public lane | Not applicable |
| 34 HouseEvent, locally known legal kind | Admit raw opaque fact | Public lane only | Public lane plus matching requested scope lanes |
| 34 HouseEvent, locally unknown legal kind/schema | Same raw persistence; interpretation unsupported, no business execution | Public lane only | Public lane plus matching requested scope lanes |
| 35 IntentPayload | Upstream command, not public bulletin; contextual action also private/control | Neither | No synthetic public event; the application may separately publish its signed HouseEvent |
| Missing/unknown/multiple oneof body | Unsafe/unsupported envelope structure, never “unknown business kind” | Reject/quarantine | Reject/quarantine |

WatchHeartbeat/Intent are excluded by the existing ingestion contract, and FollowDeclared/FollowRevoked by RELATIONS.md §8, although the generic publisher has tag mappings for all of them; a mapping alone is not a public obligation. Tighten the shared publication path accordingly in every implementation. This is different from removing already-legal unknown HouseEvent facts.

For all admitted rows: absent Recipient or BROADCAST(0)/GROUP(2) with existing valid public addressing is eligible. PRIVATE(1), CONDITIONAL(3), unknown enum, nonempty undefined filter_criteria or an invalid target rejects public membership. GROUP target_ids remain public execution addressees. A relation original is excluded by body type before any privacy field is consulted, so no `follow_type` or `taste_subscription_visibility` value can readmit one; when classifying any body, never rely on enum getters that replace unknown values with zero. Never redact private bits to create different public signed bytes.

Predecode wire checks reject repeated singular envelope/body/privacy fields, multiple body tags, unexpected wire types and unknown envelope/Recipient/Follow fields that prevent this version determining privacy. Repeated target_ids and repeated signed scopes retain their schema meaning; scopes must be unique/valid. Known nonprivacy business payload bytes remain opaque. Future envelope structure requires explicit supported semantics; a new business kind inside known HouseEvent does not.

This shared privacy predicate applies to publication, replay, live and baked projection exports, including the old public endpoint. Fixing only new-mode membership is insufficient: an implementation whose older publication policy, relation validator or replay path predates this rule reaches a different answer on the same bytes, and every such exit must be brought to this predicate. Do not make an old client's wire format change just to fix privacy; for unsafe historical rows the old SSE must close/error without delivering bytes or advancing its last delivered ID past that row. The new mode additionally emits a safe explicit gap. No old path may expose bytes rejected by the common privacy predicate.

## 3. DTOs and SSE events (new metadata only)

The following are exact proposed message field allocations in namespace popclaw.world, implemented by the accompanying proto. All data is canonical base64 protobuf, no SSE id. Unknown frame/control type, malformed supported field, repeated singular field or inconsistent selection fails the connection. Zero elision follows proto3; public_through uses unsigned optional presence to distinguish 0 from absent and is never part of an author signature.

| SSE event | Message and exact fields |
| --- | --- |
| `public_boundary` | `PublicStreamBoundary`: string log_incarnation=1; repeated string scopes=2; uint64 high_water_seq=3; bool full_public=4 |
| `public_frame` | Existing `popclaw.event.WorldStreamFrame` with seq=1, envelope=2, kind=3, projection=4, repeated scopes=5 as already allocated; no new signature/container |
| `public_checkpoint` | `PublicStreamCheckpoint`: string phase=1; repeated ScopeThrough scopes=2; optional uint64 public_through_seq=3 |
| `public_gap` | `PublicStreamGap`: string reason=1; string lane=2; string scope_id=3; PublicStreamBoundary boundary=4 |

For a successful connection, boundary comes first exactly once. scopes equals the exact sorted requested scope set, full_public equals public_after presence, log_incarnation matches authenticated negotiation, H is a fixed replay high-water mark. No data/checkpoint before boundary. The sole exceptional startup sequence is `public_gap(reason=log_incarnation_changed,lane=connection)` followed by close when the requested authenticated log differs from the actual server log. Its embedded current boundary is an untrusted recovery hint only, not a normal accepted boundary; there is no data/checkpoint and no automatic repin/reset/cursor migration. Fetch and validate the current manifest through the existing trust path before selecting another log. Never pair the old incarnation with the new log's H.

The replay checkpoint occurs once, then zero or more live checkpoints. Each checkpoint has phase replay/live and the exact requested scope set; all marks and public_through (iff full_public) equal that cycle's H. Live H values are monotonic. The complete checkpoint supplies that next cycle's H; no second boundary can silently reset the connection. Every checkpoint H is at least the highest frame seq durably received in its cycle; data alone never sets caught-up.

frame.envelope is exact original bytes. frame.kind agrees with the decoded body: typed snake_case or the exact HouseEvent.kind. frame.scopes is exactly the original HouseEvent.public_scopes, otherwise empty, not just the requested intersection. A public-only typed fact never gains scope evidence. Preserve all signed scope positions; query vectors are sorted independently. Projection is optional and may never replace original envelope bytes or be synthesized from missing cached content. Its own CID/body binding is checked as in the existing projection path. Missing projection does not discard a valid public fact.

Every frame must be full-public eligible and either full_public selected or intersect requested signed scopes. Sequence/order is ascending for newly drained union rows within each cycle; replaying an older original event to fill an independently older lane is valid. Its CID/seq/log association must be immutable. A duplicate original event is not another business delivery. Unknown legal HouseEvent kind persists even when an interpreted schema rejects/is unavailable; it gives no source-arrived/ready effect to a policy whose interpretation requirements failed.

Gap reason/lane combinations are fixed below. scope_id is nonempty **iff** lane=scope, matches a scope from this connection's original requested vector, and is empty otherwise. lane=public is legal only if public_after was present. Embedded boundary uses the exact originally requested selection; unknown_scope does not silently remove the requested scope. Invalid historical bytes, private IDs/content and raw diagnostics never appear. All gaps close with no checkpoint for the failed interval. Transport/database failure can close without fabricating a gap/checkpoint; client retains last durable positions and marks connection unavailable.

| Reason | Legal lane | Additional rule |
| --- | --- | --- |
| unknown_scope | scope | Original requested scope not registered; normal boundary then gap, no checkpoint |
| cursor_ahead | public or scope | The identified selected lane's input exceeds actual H/storage ceiling |
| history_pruned | public or scope | Identified selected lane's input is below retained floor |
| log_incarnation_changed | connection | All log evidence stale; exceptional first-frame gap permitted as above |
| public_log_invalid | public, scope or connection | Identify only a safely known affected selected lane; otherwise connection, disclose no unsafe record |
| publication_index_inconsistent | scope or connection | Scope only if known to be an originally selected scope; otherwise connection |

## 4. Exhaustive progress and overlap

At each cycle capture H from the authoritative committed log and the starting input cursor of every selected lane. Selection is the OR of `full_public && seq>public_input` and each `signed_scope∈requested && seq>that_scope_input`, bounded by H. Emit the union in global sequence order once per CID. Scope-only scans must not depend on an index omission that can silently hide a signed member: a correct minimal implementation scans bounded authoritative log pages and checks derived membership/index consistency. An optimized query may replace it only with equivalent complete-index evidence.

For each scan page use one read-only REPEATABLE READ transaction to validate incarnation/index readiness/retention floor and fetch a bounded committed page through H. Validate against that page's input positions, not already advanced output values. Check original envelope/public predicate before emission. Unsafe historical row or missing/corrupt membership association produces a safe gap; never SQL-filter it away then checkpoint across it. For scope-only, unclassifiable corrupt rows can conservatively cause a connection gap. Fully buffer the page, commit successfully, then emit. Repeat checks at the next page and a fresh check against the last page's input before checkpoint. Rotation/pruning between pages or before checkpoint cannot silently certify a missing interval. No long SQL transaction held over network writes.

Publication and every derived scope association commit under the existing publication lock before allocating visible sequence; retries preserve exact CID/bytes. Bootstrap/backfill proves readiness for the actual retained log and privacy/index predicate before advertising the block. Historical unsafe records require explicit operator repair/reconstruction, not rewrite/redaction or a success checkpoint. Restoration rotates log identity and preserves explicit history-floor/gap obligations. A conservative common retained_after floor may gap a lane even if its lost interval happened to be empty; it may not conceal actual loss.

Client ingress commits original frame/envelope, immutable (HouseBinding,log,CID,seq) binding, selected lane associations and only their monotonic cursors in one real transaction before consuming data. Full-public selection permits public cursor advancement; signed requested membership permits that scope's advancement. A high seq unrelated to a scope does not advance it. Checkpoints atomically advance the exact selected lanes only after all preceding frames have been durably ingested. Business consumer completion is separately durable and does not control reception completeness; it does control application effects/readiness as required by that consumer. These lane cursors and checkpoints assert reception completeness, so a refused frame never moves one; only a transport resume position may be released that way, under the conditions in RELATIONS.md section 8.

Example: public input=100, scope A input=0, H=120. Event 50/A must replay for A even if already consumed via public history. Event 110/B does not advance A. Event 120/A is emitted once and adds both lane associations. Reused CID suppresses duplicate consumers, not the missing scope association transaction. Empty A still needs its own checkpoint to H; public checkpoint and heartbeat cannot substitute. New scope starts at 0 and gaps if history unavailable. Wire uint64 exceeds JS safe integer; PostgreSQL's signed bigint storage ceiling produces cursor_ahead, never wraparound.

If the connection fails, affected scope-dependent readiness is unavailable until actual matching scope replay evidence returns. Other valid lane cursors stay saved; public traffic alone cannot restore a failed scope. A full-public-only boundary/checkpoint creates no scoped anchor/barrier proof.

## 5. Migration and old/new compatibility matrix

| Manifest / selected client mode | Result |
| --- | --- |
| Old manifest, old client | Published unqualified public wire path, shared privacy policy |
| New board absent/unsupported, new client | Old sole receiver if selected; optional profile unsupported, no silent scoped claims |
| Valid public_stream, old client | Unqualified old wire path continues; no new controls sent |
| Valid public_stream, new client selecting full public only | One public-v1 connection; all table-eligible facts, including Profile/unknown/unscoped HouseEvent |
| Valid public_stream, new client selecting scopes only | One public-v1 connection; matching signed scoped HouseEvents only; explicit filtered view |
| Valid public_stream, new client selecting full public + scopes | One union connection; complete public coverage plus independent requested scope progress |
| Declared block invalid/unready | New mode disabled/409; no weaker fake high-assurance capability; ordinary path remains separately usable if safe |
| Failure after new mode selected | Retain durable positions/error, stop connection; no automatic legacy fallback or parallel socket |

Before migrating stop/join the sole old receiver. Import original safe publicly eligible envelopes/CIDs and separate old content_done/task_done states into the durable shared receive journal; preserve pending vs completed. Unknown legal HouseEvent and Profile are included. The old scalar cursor and old row seq lack authenticated new log identity and MUST NOT initialize new public/scope positions or current-log CID/seq bindings. Historical projections remain marked historical; do not fabricate a complete new-mode frame. Start selected new lanes at 0. Actual replay supplies the current association, even if content was already consumed. Preserve old source records and migration receipt. Unsafe old rows remain restricted audit evidence, never republished or displayed as a repaired public projection.

Migration must be atomic, restart-idempotent and binding-specific without overwriting completion that occurred after the first import. A CID at old seq17 can reappear at new seq5, while new seq17 can belong to another CID; no invented old association is allowed. Frame and per-consumer flags remain durable personal receive evidence under the receiver's storage ownership. This document does not change its physical tables or enable a migration.

## 6. Required runtime evidence

Use a real Rust server/PostgreSQL and actual receiver/SQLite, observing one connection: all table bodies and forbidden forms; Profile; known/unknown opaque HouseEvent with no scope/matching scope/nonmatching scope and legacy kind grammar; unknown Recipient/Follow enums, duplicate privacy/body tags and private projections; scope-only with no actions/guide/ACK/model; overlap example above; late-added scopes; empty-lane checkpoint; interrupted emission/transaction failure; pagination prune/rotate races and malformed historical row; old/new client negotiation; old-CID migration conflict examples; logout stop/join and post-restore interlock. Retain exact source/binary/evidence bounds. The candidate ran none of these runtime tests.
