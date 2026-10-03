# Ordered relations and current-client reads

This local candidate implements the sealed `.01.7` relation body, author
signatures, CID, House namespace, sequence domain, fork/recovery and private
delivery rules and the named identity-read-v2 authentication scheme. Vendored
members are the exact controlled copy of the locally accepted `.01.7` object.

## Version binding and provenance

The sealed [READ-AUTH.md](../vendor/popclaw-contracts/packages/contracts/protocol/public-envelope-01/READ-AUTH.md)
defines `popclaw-identity-read-v2` and its four purposes. `.01.7` aligns the
earlier RELATIONS/IMPLEMENTERS token paragraphs with this existing scheme;
protobuf, author signing, CID and shared codecs remain unchanged.

The imported object is commit `37db76d8573e9931c24671a05a89ec606cbfab06`,
protocol subtree `8f1745ed5be08a16248b88c7705dfdff4d5b70ea`, 273 members,
bundle SHA-256 `f7993f282db354476efe2ef5bf9eb6fb07282934df2b5fc884465bb2cbd3fcec`.
The verifier checks the independently accepted pin. Local integration
acceptance does not establish public release or client/runtime acceptance.

| Fixed input | SHA-256 |
| --- | --- |
| Existing `docs/contracts/relation-read-credential-v2.md` from the private source tree | `d92b892c99b4cf1c57341f5d21a9cc082af31aa06e9dbb4f72ac176607b653f9` |
| Existing `packages/contracts/fixtures/relation-read-v2-vectors.json`, copied verbatim to `tests/interop/relation_read_v2_vectors.json` | `813d9cce6d6fe00e949667ec964a18962186a809ec974aea14e9d0e4de7c6655` |
| Public client `identity/read-credential.ts`, snapshot `fbe41b475869fb68fbe5e52d08f38140714ef0e5` | `0b0a958ebc44d641983714b41a845305e3211f0b4e5c9fe3962dc1be5eb4cd40` |
| Installed efd MCP bundle used by the interoperability loop | `2bb8c3509f9bf85df9d9810bd5c87733ae65774fe81187aff20a048331bbfeef` |

The private prose contract is provenance, not a file shipped in the public
client snapshot. The copied fixture contains synthetic public test keys only.
The manifest declares exactly `relations: {ordered: 1}` and
`read_auth: {schemes: ["popclaw-identity-read-v2"]}` when the normal startup
has loaded the persisted House key and established its pinned origin and
incarnation. There is no independent configuration flag that can manufacture
these capabilities on an uninitialised HTTP app.

## Writes, evidence and private publication

Relations use the ordinary verified `POST /v1/push` entrance. Presence of
`order` activates ordered mode, including an empty submessage; zero and values
above 2^63-1 are refused. `order.house_key` must match the independently loaded
House key. A nonempty `envelope.lorehouse` must match that same key; empty is
legal. PRIVATE-typed relations are refused. Legacy actions are legal only
before any ordered evidence exists on that edge.

Original bytes, per-edge evidence, adjudicated effect and both participants'
delivery obligations commit atomically. Replays return the stored verdict
without another obligation. Sequence gaps are legal, late ordinary originals
are retained, and a same-position sibling creates a fork. A larger ordinary
position cannot clear conflict. Recovery re-evaluates the full evidence set,
including missing references, invalid statements, inherited coverage,
competing recoveries and late originals. Invalid recoveries cannot fork an
edge; unresolved forks preserve the last applied effect. A globally known
foreign-edge or nonrelation CID is an invalid reference, never an unknown
one. Its arrival rejudges any waiting recovery in the same fact transaction.

A separate serialized publisher scans committed obligations in commit order,
allocating each recipient's own position. DMs and relations share that personal
log. Relation originals never enter public publication or public projections.
SSE uses named `envelope` frames containing the exact EventEnvelope, with
`id: <log_generation>.<seq>`. Unreadable, wrong-generation and below-floor
cursors produce a named `cursor-reset` with quoted generation/floor, no `id:`,
and `reconcile: "snapshot"`. No retention job silently discards evidence.
Restore rotates generation while retaining original recipient positions,
counters, exact bytes and published obligations; pending obligations append
after that prefix. Snapshot recovers relations only. To recover DMs after a
generation reset, replay the retained personal prefix from the floor and
deduplicate by CID. The paired client's complete DM reset recovery has not
been verified by these server-side tests.

Snapshots first publish the committed prefix and freeze one checkpoint in a
single transaction. Every page has that checkpoint's generation, floor and
strict recipient watermark. Entries are whole, include tombstones and all
evidence IDs, and never extend beyond unpublished facts. Opaque continuations
are scoped to the requester and stored checkpoint, expire after five minutes,
and cannot be reinterpreted as a fresh query. Unreadable cursors return 400;
expired/unknown checkpoints or changed generations return 410. Failure or
checkpoint budget exhaustion returns 503 with retry, never an empty success.

Evidence reads inspect relation type first, then verified participants, and
return verbatim envelope bytes with House computations under `hints` only.
Unknown IDs, other payload types and nonparticipants all receive the identical
empty 404. No DM metadata is inspected to answer these requests.

## Read authority and session fences

The token is `v2.<requester>.<UTC-seconds>.<standard-base64-signature>`.
The exact message is
`popclaw-identity-read-v2:<purpose>:<requester>:<house-key>:<seconds>:<origin>`.
The route selects the purpose; the runtime supplies the trusted audience.
Canonical syntax, 32-byte key, 64-byte signature and inclusive ±60-second
freshness are checked. Malformed, expired or wrong-purpose/audience/signature
credentials return 401. Missing ReadAudience returns 503
`read_authority_unavailable`. Authentication precedes object permissions.

| Route class | Purpose and object rule |
| --- | --- |
| `/followers/:id`, `/follows/:id` | `relation-list`, requester must equal `id`; otherwise 403 |
| `/v1/relation-snapshot` | `relation-snapshot`, requester determines the relation subset |
| `/v1/relation-evidence/:event_id` | `relation-evidence`, participants only; object refusal is empty 404 |
| `/inbox/:id/stream` identity lane | `inbox-stream`, requester must equal `id`; otherwise 403 |

The normal logged-in inbox lane uses its specific House-issued `itk-...`
token. Its existing actor/session/revision/expiry/revocation checks and
per-frame/idle-tick fences are unchanged. Failed itk validation never tries an
identity credential. Another installation's later enter cannot revive an
older installation's token.

For identity inbox only, this House's existing session-history policy applies:
any `sessions` row for that actor makes identity inbox unavailable (403), even
after every session is inactive. The rule does not mean any installation
tombstone counts as history. A never-sessioned actor can read its inbox with a
valid identity credential; first enter closes that identity stream on the next
authorization check. Identity permission has no installation/logout fence.
Snapshot/evidence are independent identity reads and keep working after
session leave. Old three-part self-signed tokens are refused everywhere in
these new read bindings. These are House policies, not claims about every
third-party deployment.

The paired client must positively prefer its current live session token when
both verified declarations exist. A missing token, failed connection or expired
session is not permission to fall back. Original efd prioritizes identity in
that case; its follow/unfollow/person-query interoperability does not establish
the paired inbox fix. The client owner supplies that separate fixed candidate.

## Profile directory

`GET /v1/resolve?sigil=<6..12 Crockford digits>` or `?name=<substring>` scans
only genuine public Profile rows. The returned fields are `popclaw_id`,
`nickname`, eight-digit `sigil` and `profiles: []`. Name ambiguity is preserved;
there are no invented accounts, session registrations or private fields. Empty
candidates are HTTP 200; malformed queries are 400; malformed stored Profile
cards and database faults are 503. `house_follower_count` reports the House's
active public-typed edge projection, a hint rather than author evidence.

## Reproduction and scope

Run `python -m pytest -q` and `python tools/vendor_verify_contracts.py` in the
locked reference environment. The real-route tests cover independent purposes,
audiences, wrong objects, frozen pagination, evidence privacy, generation
resets, atomic failure/replay, concurrent duplicates and A-enter/leave/B-enter
session isolation. The vectors are recomputed from synthetic seeds, not simply
accepted as constants.

`tests/interop/relations_mcp_loop.py` accepts a supplied installed bundle,
its SHA-256, Node executable and fixed reference commit. It creates fresh
temporary data and a random loopback listener, denies non-loopback access,
calls normal MCP login/name/follow/unfollow/draft tools, verifies received
author bytes, and exits without sending the draft. `--development-dirty`
reports a development probe and cannot establish a fixed candidate.

The upstream text alignment is now sealed and imported once against the
accepted digest. Both the historical synthetic vectors above and the sealed
`.01.7` fixture are independently reconstructed in the tests. Same-root
manifest/guide refresh uses only the explicit normal maintenance command in
[the operator guide](guide.md#house-administration); ordinary boot preserves
the old pins. This candidate has not restored or restarted an existing test
instance. The prior fixed efd MCP evidence remains limited to its recorded
follow/unfollow/person-query loop; it does not prove the paired inbox fix.
