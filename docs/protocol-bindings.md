# Protocol bindings & current status

PopClaw Ranger Map speaks the shared PopClaw public contract natively. This
document records what is bound, the trusted inputs it consumes, and what
remains outside this build's scope.

## Status: adapter BOUND to public-envelope-01.6

The signed wire surface is implemented against the controlled copy of the
contract source bundle vendored under `vendor/popclaw-contracts/`:

| Artifact | Identity |
| --- | --- |
| Contract bundle | `0.1.0-public-envelope-01.6` (envelope baseline `public-envelope-01`) |
| Trusted bundle SHA-256 | `d01bd7a060cdaa2bb35937b67e5fb4dc64a350a646b30cf2fe5dd919701ea54b` |
| Seal commit | `f42bf5db` (`PopClaw-xyz/popclaw`; bundle, pin and generated artifacts in one commit) |
| Vendored from | candidate head `3f985f47` of `merge/candidate-0.1.0`, whose `protocol/` files are identical to the seal |
| Receipt commit | pending — the architect signed this object for the re-seal scope, which is not a whole-package release acceptance |

`tools/vendor_verify_contracts.py` re-verifies all 271 files and the bundle
digest against that pin (never re-pinned to downloaded content). The
vendored Python bridge, pinned descriptor and shared vectors are the
implementation basis; no alternative canonical codec is hand-rolled, and the
bundle's serial referee (`log_model.py`) is used only by its own conformance
tests, never as production storage.

Earlier pins were `0.1.0-public-envelope-01.5` (bundle
`7956e0d9aebd7f9031193047c30322c1e5fb22a8e3788a78f3d503ad67f03bef`) and
`0.1.0-public-envelope-01.3` (bundle
`3bc796e3aa4b69d0f957b2c3e71698f73c874527738f0a4c170f27b4d8e0d170`, candidate
commit `654a63a3f995d3f1b390541fb1de5233680dc7cd`, receipt commit
`4d0dc64a13bd011e3f2298b1df7db6fbd0e51b96`). A superseded `.01.6` candidate
digest `f06e8a24` was never adopted here. The external client
interoperability run recorded in [interop-verification.md](interop-verification.md)
was made against the `.01.3` pin and is not re-claimed for `.01.6`.

## HTTP Profile binding for the public 0.1.0 client

`GET /v1/profile/{popclaw_id}` implements the minimal read binding consumed
by the public 0.1.0 client's namecard write guard. This is a version-specific
client HTTP adapter, **not** an amendment to the sealed `.01.6` signed-wire
contract or a promise that every Rust house endpoint is a permanent federation
standard. The vendor bundle, Profile signing bytes, CID, timestamp storage
unit and ingress semantics are unchanged.

For a valid identity with no stored profile row, HTTP 200 is a complete
response, with the `card` member omitted (never `null` or `{}`):

```json
{
  "popclaw_id": "11111111111111111111111111111111",
  "sigil": "ha1pcqsq",
  "profiles": [],
  "house_follower_count": 0,
  "house_post_count": 0,
  "house_reply_received_count": 0
}
```

When a stored card exists, all eight members are returned under `card`:

```json
{
  "nickname": "Mira",
  "one_line_intro": "",
  "taste_tags": [],
  "role_persona": "",
  "location_hint": "",
  "avatar_uri": "",
  "declared_at_ms": 1790705946000,
  "payout_addresses": []
}
```

- Strings and tag arrays are mapped without dropping content. Identity and
  event metadata are not card fields. `declared_at_ms` is exactly the stored
  integer `declared_at` in seconds multiplied by 1000. Milliseconds outside
  JavaScript's exact integer range (±(2^53−1)) return 503 rather than being
  rounded into a different declaration time.
- `payout_addresses: []` reflects this reference server's rejection of reserved
  Profile field 8 at admission. It does not add wallet support. An unexpected
  payout member in storage, even an empty one, is rejected rather than hidden.
- A present row with missing, duplicate, unknown or wrongly typed card fields,
  invalid JSON, or no card JSON returns HTTP 503 `storage_unavailable`. No
  field is defaulted to empty and no unknown member is selectively discarded.
  Only an absent row means no card. Invalid identity encoding returns 400;
  database/read failures return 503, never an empty-card answer.
- `sigil` is the existing public algorithm: SHA-256 of the exact identity's
  UTF-8 bytes, lowercase Crockford base32 (`0123456789abcdefghjkmnpqrstvwxyz`),
  first eight characters. The shared check is `BlackFeather` → `gdx8rgtp`.
- `profiles: []` reflects the absence of platform-account verification in
  this build. `house_follower_count: 0` reflects its refusal of all relations.

The other counts are genuine **house-local envelope counts**, not global
influence scores or a complete Rust feed implementation:

| Member | Local definition |
| --- | --- |
| `house_post_count` | Distinct accepted, publicly eligible Post envelopes (tag 27) whose envelope actor is the queried identity. This includes accepted mirrored Posts; no external post-ID deduplication is implied. |
| `house_reply_received_count` | Distinct accepted, publicly eligible Reply envelopes (tag 25) whose signed `in_reply_to.author_popclaw_id` equals the queried identity. The sender does not determine this count. A referenced post need not be stored here; empty/unknown author references count for nobody. No author is inferred or looked up on an external platform. |

Exact CID replay counts once because `accepted_envelopes.event_id` is the
primary key. A valid stranger can have nonzero counts without a card. Post
counting uses the existing actor index (scanning that actor's accepted rows).
Reply counting filters the accepted-envelope table, then decodes the local
Reply rows: O(N) table scan plus O(total Reply bytes) decoding per GET, with
O(total Reply bytes) temporary memory from `query_all`. There is no new index,
statistics service, background write, or cross-house query. This deliberate
small-reference-server tradeoff may need an indexed projection at larger
scale; zero is not substituted for the scan. Unreadable Reply bytes return
503 rather than a fabricated zero.

Response fixtures for no card, clean card, and a protected card with nonzero
counts are in [profile_http_fixtures.json](../tests/interop/profile_http_fixtures.json).
The synthetic all-zero public-key identity in the response examples is not a
signing identity. [test_profile_http.py](../tests/interop/test_profile_http.py)
checks exact mappings, full signed ingress/readback, nonzero counts, duplicate
Post/Reply replays, and invalid-ID/storage/corruption negatives.

The public client can reissue only nickname/time. Therefore the old example
`one_line_intro: "first card"` is **protected**, not a successful rename case:
its normal command must issue no new Profile and preserve the row. A separate
nickname/time-only card provides the rename positive control.

### Re-running the actual MCP loop

With the reference Python dependencies and the selected client's existing
Node/tsx dependencies already present, run from this reference checkout:

```sh
python tests/interop/profile_http_loop.py \
  --client-root /absolute/path/to/fixed-client-checkout \
  --expected-client-sha FULL_40_CHARACTER_CLIENT_SHA
```

The script reads the supplied client checkout without writing it, verifies
its HEAD, and refuses dirty reference/client trees by default. It prints
both SHAs and the Node version in its JSON evidence. It creates a real
temporary reference HTTP server on a random `127.0.0.1` port and spawns the
real client `src/mcp.ts`. Isolated data, HOME, configuration and synthetic
identity live only in a temporary directory; the client network preload
rejects and records non-loopback attempts. It never addresses port 8113.
Only its own child/server handles are stopped at completion.

It exercises normal `popclaw_house_login` and `popclaw_set_name` calls:
no card → actual first signed issue → GET readback → clean rename, with the
command's pre-write GET and accepted Profile attributed by name and call
window. Separate intro/avatar fixtures must produce zero Profile POSTs,
zero accepted declarations and unchanged HTTP projections.

The final `direct_ingress_probe` is explicitly **outside the user chain**:
it bypasses the client guard and submits signed nickname/time-only Profile
fixtures directly over HTTP. An older declaration preserves the protected
row; a newer declaration demonstrates the existing whole-row overwrite by
clearing the protected avatar. Before/after projections, request bytes and
accepted event IDs are emitted for independent inspection. This probe does
not change ingress; it establishes the loss that the normal guard prevents.

`--allow-dirty` is available only for development probes. Such output reports
`fixed_joint_candidate: false` and cannot be cited as acceptance of fixed
client/server candidates. Running this loop does not by itself accept a
release, install a package, or publish an artifact.

## Upgrade record: `.01.5` → `.01.6`

Two substantive changes, both of which this server had already anticipated.

| # | Change | Disposition | What this server does |
| --- | --- | --- | --- |
| A | Tags 20/21 leave the sealed public-eligibility predicate in all three language baselines; the follow privacy fields are no longer consulted there, because the body type alone decides. Generic structure, codec, CID and author signatures are untouched, and relation originals are still admitted through a House's ordinary verified write entrance | **Mirror synced; no behaviour change** | `wire.PUBLIC_ELIGIBLE_TAGS` mirrors the sealed list and drops the two tags with it. Nothing else moves: relation-ness has been decided from the structural decode since the exits were written, precisely so that the sealed predicate refusing these tags turns a stored relation original into a withheld row rather than an invalid public row. Reverting that decoupling against this pin now breaks all three exits and the corruption test, which is the evidence that it was load-bearing rather than defensive. |
| B | `RELATIONS.md` §8 gains the transport-resume-position clause: a refusal may release only the position a client keeps to know where to continue reading, and only after the raw bytes, their true hash, the reason, the trusted source and the position have been durably retained in the same atomic step. A public or scope lane cursor, and a `PUBLIC-STREAM.md` checkpoint, are explicitly **not** transport resume positions | Not applicable | The clause binds the receiving client only, and says so: a House that keeps relation rows out of its own public log after full verification and emits its checkpoints exactly as `PUBLIC-STREAM.md` specifies owes no refusal ledger and retains its originals. That is what this server does, so it carries no ledger and its checkpoints are unaffected. |

The `PUBLIC-STREAM.md` / `RELATIONS.md` conflict recorded in the `.01.5` table
below is resolved by this re-seal, in the direction this server already
implemented.

## Upgrade record: `.01.3` → `.01.5`

Every change the bundle's `CHANGES.md` lists between the two versions, with
this reference server's disposition. Only `LIMITS.md`, `SPEC.md`/`BASELINE.md`
(version lines), `IMPLEMENTERS.md`, the new `RELATIONS.md`, `event.proto`, the
regenerated descriptor/codecs, the vector file and the bundle tooling differ;
`board.schema.json`, `action-kind.schema.json`, `SIGNING.md`, `RECEIPTS.md`,
`PUBLIC-STREAM.md`, `TRUST.md`, `RUNTIME.md`, `CONSUMPTION.md`,
`examples.json`, `interpreted-event-kind.schema.json` and everything under
`protocol/retained/` are byte-identical.

| # | Change (version) | Disposition | What this server does |
| --- | --- | --- | --- |
| 1 | `L_ENVELOPE_MAX_BYTES` 262144 → 1572864 (`.01.4`; `LIMITS.md`, `public_baseline.py` and the TS/Rust guards) | **Changed** | `wire.L_ENVELOPE_MAX_BYTES` is taken from the vendored bridge; the push body cap, the wrapper/payload checks and the guard re-run on historical rows all follow it. A house may bound what it relays on its public stream below the protocol limit (the Rust lore-house keeps 256 KiB there); that is house policy and this reference server sets no such lower bound. The protocol limit bounds the raw envelope only; the wrapper, SSE-frame and page ceilings are distinct consequences of it and none of them is the ceiling for any particular business content (params, result bodies, the manifest and the guide keep their own far smaller limits). The frame ceiling is derived from every component a `WorldStreamFrame` carries — seq, envelope, routing kind and public scopes — because deriving it from the envelope alone understates it by the metadata. |
| 2 | New nested `RelationOrder {seq, house_key, resolves}`; `FollowDeclared.order = 5`, `FollowRevoked.order = 3`; descriptor and generated codecs regenerated (`.01.5`) | **Changed** | Re-vendored. The bridge's structural guard is descriptor-driven, so an order-bearing Follow now passes the wire check instead of failing `UNSUPPORTED_FIELD`; admission below is what keeps it out of the legacy public lane. |
| 3 | Capability `relations` = `{"ordered": 1}` as a top-level authenticated-manifest member (`RELATIONS.md` §1, `IMPLEMENTERS.md`) | **Changed (declared absent)** | This server has no ordered-relation engine, so it serves **no** `relations` member; a regression asserts the pinned manifest never carries one. `board.schema.json` is unchanged and `relations` sits beside `intent_kinds` outside `world_interaction`, so the board validation is unaffected. |
| 4 | Ordered admission (`RELATIONS.md` §3): `order` present activates ordered mode unconditionally; an end that has not declared `relations.ordered` refuses the event rather than applying it under the legacy rules | **Changed** | `POST /v1/push` refuses **every** `FollowDeclared`/`FollowRevoked` after the signatures and CID have verified, storing nothing. A present `order` — including present-but-empty — is refused with 400 `RELATION_ORDER_UNSUPPORTED` under the contract's own rule; every other relation original is refused with 400 `RELATION_UNSUPPORTED` under this house's policy (row 10). Both codes are house-local HTTP rejections and are deliberately not added to `retained/errors.md`, which defines signed Intent action and status receipts. |
| 5 | `seq` domain 1..=2^63−1, 2^53+1 vector, `seq = 0` refusal | Not applicable | Never reached: every order-bearing event is refused at admission (#4). |
| 6 | `envelope.lorehouse` vs `order.house_key` rule (`RELATIONS.md` §4) | Not applicable | Same as #5. |
| 7 | Fork / recovery adjudication, `resolves` standings (`RELATIONS.md` §5) | Not applicable | No adjudicator; capability declared absent (#3). |
| 8 | `GET /v1/relation-snapshot`, `GET /v1/relation-evidence/:event_id` (`RELATIONS.md` §6–7, `IMPLEMENTERS.md` table) | Not applicable | Not advertised, not served. The bundle ships no server for them either. |
| 9 | Delivery of admitted relation originals to both participants' personal streams; `cursor-reset` (`RELATIONS.md` §8) | Not applicable | Only ordered originals are covered and none are admitted (#4). |
| 10 | `RELATIONS.md` §8: a relation original is not published on a public stream | **Changed** | A follow or unfollow is a personal event, so no relation original is carried publicly here — not only the ordered kind. Ranger Map implements no relation engine, so it refuses every relation original at ingress (row 4) and withholds one on all three public exits (replay, live and the legacy lane). The `PUBLIC-STREAM.md` text that read the other way was unified by the `.01.6` re-seal. See "Relation originals" below. |
| 11 | PRIVATE-typed Follows are never admitted through `/v1/push` (`RELATIONS.md` §8) | Unchanged in effect | Already refused by the shared privacy predicate; now refused one step earlier as a relation original, so the outcome no longer depends on the privacy predicate at all. A regression pins it. |
| 12 | `FollowType.PUBLIC` keeps its meaning; no broadcast instruction | Not applicable | No behaviour depends on it beyond the privacy predicate. |
| 13 | Four new canonical vectors (`house_event_minimal`, `house_event_default_boundaries`, `intent_minimal`, `intent_default_boundaries`); 29 retained vectors byte-unchanged | Covered by the bundle suite | The vendored parity suite (18 tests) and `tests/interop/test_vendor_bridge.py` run through this server's bridge import unchanged. |
| 14 | Version lines in `SPEC.md`/`BASELINE.md`; `IMPLEMENTERS.md` capability table and "Ordered relations" section | Docs only | This document, `README.md`, `THIRD-PARTY-NOTICES.md`, the verifier pin and the adapter constants now name `.01.5`. |
| 15 | Bundle tooling (`TOOLCHAIN.json`, `write-manifest.py`, `package.json`, Rust/TS test sources) | Not applicable | Part of the sealed bundle; covered by the digest pin only. |

## Implemented surface

- **`GET /v1/manifest`** — the manifest is built once at a data root's first
  boot and pinned verbatim (its digest is the `capability_revision`); every
  response carries a fresh house-signed `X-Popclaw-Manifest-Proof`
  (`POPCLAW_WORLD_MANIFEST_PROOF_V1` over the canonical core with
  `authority_signature` absent), binding origin, house key and server
  incarnation to the exact served bytes. `GET /v1/guide.md` serves the exact
  pinned guide bytes whose digest the manifest quotes. The data root is
  bound to its canonical origin at first boot; serving under a different
  origin is refused.
- **`GET /v1/profile/:popclaw_id`** — the accepted profile projection for
  one identity. Three outcomes, never four: 400 when the id does not decode
  to a 32-byte key, 503 when the data root cannot serve, and 200 for
  everything else.
  An identity this house has never heard of is not a 404 — it gets a 200
  carrying only the `popclaw_id` it was asked about. A client that reads
  before it writes must fail closed on an unreadable answer, and a 404 is
  indistinguishable from a route that moved; answering at all is how the
  house says the route is alive and the identity is new.
- **`POST /v1/push`** — SignedPayload ingress: outer signature over the
  exact envelope bytes verified before any decode; the bounded raw-wire
  guard rejects any occurrence of reserved EventEnvelope field 29 or nested
  Profile field 8 (whole event, never stripped-and-repaired), duplicate
  singular fields, unknown envelope fields and malformed structure;
  canonical CID check; inner signature; `Base58Decode(actor.popclaw_id)`
  must equal the 32-byte signer key. Every `FollowDeclared`/`FollowRevoked`
  is refused (`RELATION_ORDER_UNSUPPORTED` when the `.01.5` `order`
  sub-message is present at all, `RELATION_UNSUPPORTED` otherwise); see
  "Relation originals" below. Body policy: public lane for
  Post/Reply/Profile/legal HouseEvents (privacy predicate
  applied before publication), private relay for encrypted DirectMessages
  (recipient targeting validated, ciphertext/nonce pairing enforced, never
  public), opaque retention of other legal typed traffic, and the intent
  path below. Exact replay of an accepted event returns the original
  outcome (`duplicate: true`) with no second effect.
- **`POST /v1/house-session`** — G0 enter/renew/leave/status with signed
  requests/ACKs (`POPCLAW_HOUSE_SESSION_REQUEST_V1` /
  `..._ACK_V1`), op_seq compare-and-set per (identity, installation),
  leave watermarks (a late old leave never closes a newer generation;
  SUPERSEDED/ALREADY_CLOSED/CLOSED-tombstone outcomes), lease 90 s,
  EXECUTOR_BUSY across installations, a monotonic never-reused
  house_revision fence, and short-lived v2 inbox tokens that die with the
  session. Every handled outcome — rejections included — is a signed ACK
  bound to the saved original request; request retries are idempotent by
  request_id with IDEMPOTENCY_CONFLICT on changed contents.
- **Intent actions (`rangermap.check_in`)** — the one business action over
  `POST /v1/push` with a full `IntentContext` (origin/house key/incarnation,
  session + fence, capability revision = current manifest digest, schema
  version, validity window). Admission failures produce house-signed
  REJECTED ActionResult receipts (stable errors.md codes) stored immutably
  under the request id. The accepted path commits envelope evidence,
  business event + footprint, the house-signed `rangermap.checked_in`
  public fact and the terminal SUCCEEDED
  `SignedActionResult`(`POPCLAW_WORLD_ACTION_RESULT_V1`, immutable
  `result_body` = Footprint) in ONE transaction, re-validating the session
  under the write lock. Replays return the original signed result
  byte-identically — including after the session expired or left.
- **`POST /v1/world-actions/status`** — signed, nonce-single-use, owner-only
  reads (`POPCLAW_WORLD_ACTION_STATUS_READ_V1`, TTL ≤ 300 s); unknown →
  404 `REQUEST_NOT_FOUND` (never proof of absence), foreign actor → 403.
- **`GET /v1/world-stream?mode=public-v1`** — the anonymous public lane:
  strict request grammar (required `incarnation` + sorted `cursors` vector,
  optional `public_after`, limit 1–512), `public_boundary` → replayed
  `public_frame`s (exact original envelope bytes) → `public_checkpoint`,
  then live delivery with monotonic checkpoints; explicit `public_gap`
  matrix (unknown_scope, cursor_ahead, history_pruned,
  log_incarnation_changed, public_log_invalid). Historical unsupported
  rows re-fail the guard on every scan page and close the connection
  without emitting N or anything past it; a failed page may withhold its
  earlier rows (BASELINE.md). The unqualified legacy lane keeps the old
  id/data frame grammar, applies the same privacy predicate and closes
  silently at unsafe rows.
- **`GET /inbox/:id/stream`** — recipient-isolated DM SSE (named
  `envelope` frames with the full signed envelope): house-issued v2 tokens
  (re-validated every tick; leave/revocation closes the stream) or the
  legacy self-signed `x-popclaw-inbox-token` lane with its 60-second
  window. `Last-Event-ID` resumes from the durable per-recipient log.

### Log and incarnation semantics

The public log's incarnation and the server incarnation are distinct and
both persisted; ordinary restarts preserve both. An explicit restore
(`tools/house_admin.py --restore`, refused while the server holds the data
root) rotates both into fresh never-reused ids, records the retired ids,
fences every session and inbox token, and rebuilds the manifest against the
new log identity. Live emission uses check-to-send fencing: every page,
frame batch and checkpoint re-validates the captured (epoch, log) identity
under the hub's cutover lock before sending, so an in-flight connection can
never certify coverage across a switch — it receives
`public_gap(log_incarnation_changed)` and closes. An in-process rotation
commits the epoch/log switch under the lock, then cancels and JOINS the
registered stream tasks: a normal return proves every captured task
actually exited, and a wedged task (e.g. one blocked inside its own
cancellation cleanup) raises `CutoverQuiesceTimeout` instead of
advertising successful quiescence — a recoverable post-cutover state, since
the old-generation gate is already closed; re-running the rotation after
the task exits re-attempts the join. Regressions cover the deterministic
cleanup wedge and a real transport-backpressure case (blocked ASGI send,
true EOF observed by the client, never a socket timeout mistaken for
connection close).

## Action-kind declaration and legacy data roots

The manifest carries a top-level `intent_kinds` array whose single row
uniquely declares `rangermap.check_in` (selected by
`world_interaction.actions.kinds`, SPEC.md §2 rule 4) under the pinned
action-kind schema: `schema_version=1`, `transport=house`, `signer=user`,
`result_attachments {allowed:[], required_on_success:[]}`, `consistency=none`,
with `params_schema`/`result_schema` that mirror the real business
validation and the real Footprint projection (validated in
`tests/interop/test_manifest_declaration.py`, including pinned-schema-profile
conformance of both embedded schemas). The load-time validator refuses to
serve any manifest advertising an action kind without a unique, structurally
valid row — the client's capability checks are never weakened by an unbacked
board entry.

Manifests are pinned per data root at first boot by design. A data root
pinned before this declaration existed (no `intent_kinds`) fails startup
loudly with the migration instruction — the pin is never silently mutated
and identities are never silently rotated. The documented migration is an
explicit house restore:

```sh
python tools/house_admin.py --data-dir <dir> --origin <origin>
```

The restore rotates both incarnation domains to fresh never-reused ids per
the public contract and rebuilds the manifest with the declaration (a new
`capability_revision`; previously issued action results stay queryable
under the old revision they were signed against).

## Evidence

- `tests/interop/test_vendor_bridge.py` — the trusted pin verifies; the
  vendored bundle's own 18-test parity suite passes in this venv; the wire
  matrix, signed-envelope/CID vectors, session request/ACK domains and the
  eight retained world-signing domains all pass through this server's
  bridge import.
- `tests/interop/test_relations_wire.py` — relation originals and the size
  ceilings. Ingress: every Follow form (declared/revoked, ordered/plain/
  present-but-empty `order`, PUBLIC/PRIVATE) is refused under its own code
  with nothing stored, and the manifest declares no `relations` member.
  Exits: a relation original seeded into the durable log between two
  ordinary public events is withheld on replay, on the live lane and on the
  legacy lane, while both ordinary events still read and the checkpoint
  still certifies coverage through the skipped position — a filtered row
  never stalls a cursor. A relation row whose index association is corrupt
  still raises `publication_index_inconsistent` rather than being quietly
  skipped, so filtering cannot launder real corruption. Ceilings: an
  envelope of exactly `L_ENVELOPE_MAX_BYTES` is admitted and one byte more
  is refused, the wrapper ceiling is proven distinct from the envelope
  ceiling, and a maximal event is read back byte-identically through the
  public lane.
- `tests/interop/test_ingress_wire.py` — real generated-key traffic and the
  tamper matrix (outer/inner signature, CID, actor↔signer, foreign house,
  reserved 29 / nested Profile 8 with valid inner signatures, duplicate and
  unknown fields, truncation, private-target publication, DM targeting).
- `tests/interop/test_sessions_wire.py` — the full G0 lifecycle including
  op_seq CAS, watermarks, SUPERSEDED, lease expiry, audience mismatch,
  idempotent ACK replay and token death.
- `tests/interop/test_action_wire.py` — end-to-end check_in with signed
  results, the admission-rejection receipt matrix, owner-only status reads
  with nonce/expiry rules, rollback atomicity and concurrent same-CID
  single execution.
- `tests/interop/test_streams_wire.py` / `test_streams_live.py` /
  `test_fences_and_manifest.py` — negotiation/gap matrix, unsafe-history
  closes (both lanes), REAL-server live replay→live delivery, live scoped
  lanes, DM live delivery + revocation, mid-stream cutover fencing,
  restart-pinned manifest/log identity and the manifest proof binding.
- The 192 business/UI tests of the original candidate remain green
  (the two placeholder assertions that encoded the old adapter-pending
  state were replaced with real-protocol expectations).

**External client interoperability: PASSED (two real runtime phases).**
The G0 TypeScript client candidate
`11fbca5861542280c86078a8a93753a641866701` passed both phases against this
server at `f17c8940f66636f901f0f475fec6acdcf1a03d2c` — real login,
authenticated capability/guide preparation, two `rangermap.check_in`
submissions with verified signed receipts, byte-identical exact-request
replay before leave / after leave / after an ordinary server restart,
public full-lane + scope-lane reception, durable encrypted-DM delivery and
settlement, and non-recipient inbox rejection. Independent read-only
verification of the archived bytes passed in full (request CIDs with
inner/outer signatures; receipt signatures, all request/House/context
bindings, the exact inner-envelope digest domain and distinct wrapper
bytes; public-fact CIDs/signatures with bodies exactly equal to the signed
`result_body`; identical receipt hashes before and after restart). The
manifest/proof/guide view carried by the capture is byte-identical to the
successful run's capability revision, with the pin signature, declared
result authority, guide hash, intent schema row and log incarnation
independently verified; that provenance is recorded explicitly. The full
verification record with exact SHAs is
[docs/interop-verification.md](interop-verification.md) (G0 evidence
commit `e75380b6daf07d416485a2a753d5660e7f661ef2`). Scope: an ordinary
process restart between phases — not a restore/cutover test; deployment
and other platforms are not inferred. The trace ran at `f17c894…`; the
subsequent code change through `d69f783…` covers cutover quiescence with its
own targeted regressions. Later documentation and source-distribution
changes are not part of that original trace. Server-side conformance
suites above remain distinct evidence, and
a Python self-client is never counted as client acceptance.

DM admission policy: this reference server applies its explicit PRIVATE
recipient-target requirement to **all DM submissions it receives** — the
tested client's new DM authoring now complies. That is this server's
admission policy, not a public-wire mandate over DM envelopes generally
(historical no-target envelopes stay byte-unchanged and remain accepted by
the ordinary recipient verifier; reposting them to this server is
unsupported).

## Inbox token representation and the legacy lane (G0 clarification)

The `0.1.0-public-envelope-01` public contract (unchanged through `.01.5`) treats
`AckCore.inbox_read_token` as an **opaque string** (house_session.proto
specifies only: short-lived, house-signed, bound to canonical audience,
session and revision, invalid after leave/revocation; IMPLEMENTERS.md forbids
a selected session lane from falling back to a self-signed token on
failure). This house therefore keeps its three-segment internal
representation (`itk-<id>.<exp>.<b64 sig>`), whose signature covers
`inbox-token-v2:<id>:<origin>:<actor>:<session>:<revision>:<exp>` — audience,
session, revision, expiry and revocation are all bound and revalidated
before EVERY delivered frame; leave/revocation/fence-change/expiry stop
delivery and close the stream. No six-part format is imitated.

The self-signed **legacy** lane (`x-popclaw-inbox-token`,
`inbox-read:<id>:<seconds>`, 60-second window) is refused for any identity
with house-session history in this house. That eligibility rule and the
per-frame recheck are this reference server's security policy — aligned
with the official Rust implementation's behavior, but **not** quoted public
normative text (the public bundle does not prescribe a migration rule);
clients that never enter sessions keep the legacy lane available.

## Relation originals

A follow or unfollow is a personal event. `RELATIONS.md` §8 owes an admitted
relation original to the two participants' personal streams and to no public
lane, and `FollowType.PUBLIC` describes the relation's nature rather than
conferring any public-stream right. Ranger Map is a check-in map: it
implements no relation engine, no ordered-relation adjudicator and neither
reconciliation route, so it does not carry relation events at all.

- **Ingress refuses every relation original.** Structural validity and
  delivery policy are separate questions: the vendored guard still decodes
  and validates these envelopes (generic wire capability is retained), and
  the refusal is this house's own. Nothing is stored and nothing is
  published.
- **All three public exits withhold one.** A row an earlier build numbered
  into the durable public log is never delivered on replay, on the live lane
  or on the legacy lane. Its original bytes and CID are left untouched and
  the log keeps its consecutive numbering, so nothing is rewritten and the
  index-completeness check stays meaningful.
- **Withholding still advances the scan position.** A skipped row never
  stalls a cursor and never costs a later legitimate event its delivery, and
  the checkpoint still certifies coverage through the skipped position.
- **Withholding never launders corruption.** Row validation — raw-wire guard
  and index association — runs first and unchanged, so genuinely bad bytes
  or a broken association still produce the proper gap or close instead of
  disappearing into a clean-looking stream.
- **The refusal precedes the replay lookup.** A data root written by an
  earlier build can still hold a relation original in `accepted_envelopes`,
  and the idempotent-replay branch would otherwise answer 200 with
  `public: true` for it — telling a client its relation sits on a public
  lane that now withholds it. Refusing first is what makes "every relation
  original is refused" true without qualification.
- **Withholding does not depend on the sealed whitelist.** Relation-ness is
  decided from the structural decode, which keeps the field whatever the
  baseline's public predicate lists. The `.01.6` re-seal did drop tags 20/21
  from that predicate, and a server that asked it whether a stored relation
  original is publicly eligible would now read the answer as an invalid
  public row and close every reader's connection — a permanently stalled
  cursor on any data root still holding one. Restoring that coupling against
  the current pin breaks all three exits and the corruption test, which is
  what makes this decoupling load-bearing rather than defensive.

`PUBLIC-STREAM.md` rows 20/21 and `CHANGES.md` still describe PUBLIC Follows
as public-lane traffic. That conflict is the contract's own; the protocol
owner is unifying the texts and will re-seal the bundle, and this server
re-vendors once against the re-sealed pin rather than editing sealed text
locally.

## Known limits of this build

- Invite/Quest/Watch/Poll/Mark typed bodies are structurally retained
  (with signatures verified) but have no house-side admission rules, so
  they are not published to the public lane; only the tags this house
  actively validates (posts/replies/follows/profiles/HouseEvents plus its
  own signed facts) are admitted publicly.
- `actions.attachments` is `[]` and `consistency=none`: no snapshot or
  subscription attachments, no execution-closure capability, no structured
  private-message interpretation (ordinary encrypted DMs only).
- The legacy `/v1/world-stream` lane implements the published frame grammar
  with `Last-Event-ID` resume; older query parameters of the historical
  relay are not emulated beyond that.
- Single process per data root by design; no multi-instance service, no
  deployment tooling, no push. External client interoperability is
  verified (see Evidence); hosted availability and other platforms remain
  outside the record.
