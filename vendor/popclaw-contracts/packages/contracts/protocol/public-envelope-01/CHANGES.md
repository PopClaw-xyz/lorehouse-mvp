# Compatibility changes

`0.1.0-public-envelope-01.6` settles where a relation original may be delivered,
and what a client may do after refusing one that reached it on a public channel
anyway. It is a normative revision, not an editorial one: the shared
public-eligibility predicate changes in all three languages, so a consumer that
vendors the predicate changes behaviour on bytes it already accepts.

- **A `FollowDeclared` or `FollowRevoked` original is never publicly eligible,
  whether its `order` is absent, present, or present but entirely default.**
  Tags 20 and 21 leave the public membership set in
  `checkPublicEnvelopeStructure` / `check_public_envelope_structure`, which now
  answers `NOT_PUBLIC` for a relation original. `.5` stated this rule in
  RELATIONS.md §8 while PUBLIC-STREAM.md's membership table still listed both
  tags on the public lane and the predicate still admitted them; this version
  removes the contradiction in favour of RELATIONS.md. The follow-specific
  privacy refusals inside that predicate are now unreachable and are removed
  with it; the body type alone decides, so no privacy field can readmit one.
- **Relation capability is unchanged, and this is not a write guard.** The
  generic wire and codec layer, canonical bytes, CID, author signature
  verification, `/v1/push` admission of a relation original and personal-stream
  delivery are all untouched. No canonical byte, CID, signature or field number
  moves. Public eligibility is one question asked of a public exit; a House that
  supports relations goes on accepting originals through its ordinary verified
  write entrance, and a House keeps its own delivery filters as defence in depth.
- A House that published such originals under an earlier version must stop
  serving them on every public exit — publication, live path, history window,
  cursored replay and baked projection. A filtered page still advances the scan
  position, so the exclusion never costs a later legitimate post.
- **A client that receives a violating public frame refuses it, admits it to no
  relation state, and may release only its transport resume position** — and
  only after the raw bytes, their true byte hash, the refusal reason, the
  trusted connection source and that position have been durably retained in the
  same atomic step. A failed evidence write moves nothing. That release asserts
  nothing about signature verification, business completion, relation ordering
  or recovery completeness; public eligibility is answered before the CID and
  signature are checked, so a refused frame's claimed author is not a verified
  identity. A refusal never occupies a verified event's deduplication identity,
  and a position that also asserts complete reception — a PUBLIC-STREAM.md lane
  cursor or checkpoint — is never moved by one. Stopping instead, with the
  binding declared unavailable, stays conforming. This obligation binds the
  receiving client only: a House that filters relation rows out of its own log
  after full verification and checkpoints as already specified gains no
  sender-side refusal ledger and keeps its originals (RELATIONS.md §8).
- **This version supersedes an earlier `0.1.0-public-envelope-01.6` candidate**,
  bundle `f06e8a24e28aec2da74d2787b67ddda955f8c48f284c6aade41e8351981d4fc9`,
  271 files. That candidate required the refusal to advance no cursor at all,
  which left a client facing a non-conforming House with no bounded exit; the
  rule above replaces it with the transport resume position and the evidence
  that must precede its release. The superseded digest was never adopted — no
  vendored copy, consumer or pin ever referenced it — so the version string is
  reused rather than burned, and the earlier candidate is not a released
  version.
- The source-bundle membership rule now ignores the exact filename `.DS_Store`,
  which a desktop file browser creates without anyone editing the bundle. Any
  other unlisted file under the bundle root is still a membership mismatch; the
  rule is a single filename, not a hidden-file exemption.
- The manifest jurisdiction statement in SPEC.md and LIMITS.md is made exact:
  which bounds are raw-wire, which are business JSON, and which top-level rows
  the `world_interaction` block draws under the public profile. No bound moves.

`0.1.0-public-envelope-01.5` adds author-signed ordering to relation actions and
changes nothing else. It is an additive superset of `.4`: no existing canonical
byte, CID or signature moves.

- `RelationOrder` is a new nested message carrying `seq` (uint64), `house_key`
  (string) and `resolves` (repeated string). `FollowDeclared` gains `order = 5`
  and `FollowRevoked` gains `order = 3`. proto3 message fields have explicit
  presence, so an absent `order` elides and every event signed before this field
  existed keeps a byte-identical CID. All 29 previously retained canonical
  vectors are unchanged, and four new vectors pin the new shape.
- **The compatibility direction is asymmetric, and it is a rejection rather than
  a degradation.** A `.5` reader accepts every `.4` byte *at the encoding and
  structural layer* — this says nothing about whether a relation an end has
  already seen ordered may go on being applied under the legacy rules; it may
  not. An event that actually carries `order` is refused by a `.4` reader, and a
  conforming implementation must not treat it as a valid unordered event.
  Refusal has two independent layers. WIRE: a conforming `.4` reader rejects it
  at the predecode wire check, because an unknown Follow field prevents that
  version determining privacy (`UNSUPPORTED_FIELD`); a decoder that instead
  discards unknown fields re-encodes a different canonical form and fails the
  CID. But a decoder that *retains* unknown fields can re-encode identical bytes
  and pass the CID, so the wire layer is not by itself the guard. ADMISSION: an
  end that has not declared `relations.ordered` refuses the event on the version
  check regardless of how its decoder treated the field. Both ends that consume
  an ordered relation must support `.5`. Events without `order` remain readable
  by `.4`.
- `order` **present but entirely default** is distinct from `order` absent: the
  sub-message still emits its tag and zero length. Presence is what activates
  ordered mode, so a canonicalizer that drops empty sub-messages would make
  ordered and legacy modes indistinguishable. A vector pins this.
- `seq` has an effective domain of 1..=2^63-1, narrower than the wire type, and
  a vector pins 2^53+1 — the first value a JavaScript Number cannot hold — so an
  implementation that silently rounds the counter fails parity rather than
  corrupting ordering.
- `FollowType.PUBLIC` keeps its meaning: the relation is public in nature. It is
  not an instruction to broadcast and confers no public-stream right.

`0.1.0-public-envelope-01.4` raises one fixed resource limit and changes nothing else.

- `L_ENVELOPE_MAX_BYTES` is 1572864 (1.5 MiB), up from 262144. A raw envelope between
  the two bounds that a `.3` reader rejected with `WIRE_LIMIT` is accepted by a `.4`
  reader; every other check, every canonical byte, CID and signature is unchanged. A
  direct message carrying a 1 MiB sealed attachment now fits. Houses may still bound
  what they relay on their public streams below this.

`0.1.0-public-envelope-01.3` is a separately versioned successor. It does not reuse
an earlier bundle digest or claim that these changes are only editorial.

- Public admission removes envelope field 29 and Profile field 8, retaining numeric
  reservations only. Original-wire occurrence is rejected even when a generated
  decoder could discard it. Three excluded product vectors/types are absent.
- The authenticated public_stream declaration requires
  `envelope_baseline=public-envelope-01`. Strict old block parsers reject the added
  field; new parsers reject the old missing declaration. There is no automatic fallback.
- The declared baseline is immutable actual-log metadata. Forward and reverse
  changes use new, never-reused log incarnations and fence old delivery work.
- All public, legacy and projection boundaries apply the same admission/privacy
  checks. Existing unsupported N produces no crossing frame/checkpoint; legacy
  retains its old control grammar and closes/errors.
- The generated TypeScript map encoder now sorts UTF-8 key bytes directly. This
  fixes a demonstrated mismatch for Unicode and integer-like string map keys.
  Python canonicalization also orders prefix keys by UTF-8 bytes; its protobuf
  deterministic mode alone does not provide this ordering. TypeScript canonicalization
  elides all implicit scalar defaults while preserving optional/oneof presence.
  Empty string map keys/values omit their entry fields to match prost, retaining
  the map entry itself. Literal keys such as `__proto__` survive TS cloning; old affected bytes are never silently rewritten or re-signed. The 29
  retained canonical vectors keep their original bytes/CIDs, including the one
  standalone VerifiedPlatform vector.
- Known supported identity, DM, nonpayment Quest, session and world signature domains
  retain their signing rules. Legal unknown HouseEvent bodies remain opaque.
- Public log incarnation and HouseBinding server incarnation remain distinct. A log
  cutover conveys no new session, trust pin or local grant.

Eight retained world-signing vectors are byte-regression evidence only, not active
manifest declarations or current authority. Session sequence fixtures are contract
examples, not proof of database races, restart recovery or running server support.
