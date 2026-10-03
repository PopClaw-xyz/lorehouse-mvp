# Public envelope baseline 01

Version: `0.1.0-public-envelope-01.7`. Baseline: `public-envelope-01`.
This document defines normative changes to the earlier envelope coverage promise.
It is not an assertion of compatibility with a wider historical body set.

## Declaration and supported bytes

A receiver selects this baseline only from the exact, authenticated manifest body
whose `world_interaction.public_stream.envelope_baseline` is `public-envelope-01`.
The discriminator is required by `board.schema.json` and participates in the
manifest proof and capability revision. Missing/different values are unsupported.
The outer board version remains 1; the transport remains `mode=public-v1`.
An older strict block parser rejects the added field. Independently valid base
blocks remain subject to their existing dependencies: an action requiring a
subscription cannot run with an unsupported public stream.

The public proto reserves only the numbers EventEnvelope 29 and Profile 8 at
message scope. No field-name reservation, number reuse, replacement carrier or
named excluded product type is introduced. **Any raw occurrence** of either
number is unsupported, including zero, empty, default, reordered or duplicate
encodings. Profile 8 is checked within every original Profile occurrence,
including an occurrence a lossy decoder would merge or discard. Reject the whole
event; never strip a field and verify or forward the resulting object as the
original signed event. This does not assert the private author's signature was
cryptographically invalid.

Check bounded original wire structure before lossy decode/re-encode. Malformed,
ambiguous, duplicate singular/oneof, unsupported envelope or privacy structure
continues to fail. Decoders' unknown-field skipping is not admission. This change
does not grant blanket unknown-structure passthrough. A valid HouseEvent with a
legal kind (`^[a-z0-9-]+\.[a-z0-9_]+$`, at most 128 characters) retains exact
original bytes even if its business kind/schema is unknown. Its opaque body is
not parsed for product semantics, JSON or a narrower action-kind grammar. The
baseline is structural, not content classification of arbitrary application data.

Supported events keep exact original wire bytes, canonical signed bytes, CID and
signature. Ordinary identity, signature, body-specific validity, public addressing
and privacy checks remain mandatory in addition to structural validation. Ordinary
DM and signed control messages are not made public by passing a structural check.

## One immutable baseline per actual log

The baseline is immutable authoritative metadata of a public log incarnation.
Manifest configuration cannot change it. Before advertising readiness, validate
the actual entire retained log, public membership/index consistency and every
entry path against the same baseline and privacy predicate. The signed declaration
must agree with that metadata. An unready selected mode returns
`409 PUBLIC_STREAM_UNAVAILABLE`.

Apply the predicate to source admission, federation/backfill into this log,
publication, replay, live delivery, public projections and exports. Rejected source
events obtain no visible public sequence. A subsequent independently accepted event
obtains the ordinary next sequence; rejecting an unadmitted event fabricates no gap.
Private original records may remain in restricted storage outside this public log.
No such storage creates a publication or projection bypass.

A new empty House creates a real new baseline log before signing a ready manifest.
An existing log which was never declared under a wider baseline may be prepared
by validating all retained data and indices without rewriting bytes or sequences.
A process restart alone preserves the baseline and log identity.

## Historical violations and legacy boundaries

At an existing unsupported sequence N, preparation refuses readiness. A runtime
read/race which encounters N emits safe `public_log_invalid` and closes. Choose a
lane only from safely established selection; otherwise use connection. Send no
unsafe bytes or diagnostic, N, later frame or checkpoint certifying coverage over N.
Validate and fully buffer each page before emitting any of it; a failed page may
withhold its earlier rows. Prior durable input/positions remain intact. Scope-only
scans conservatively gap if unsupported structure prevents proving irrelevance.
Index filtering, retries, cursor manipulation or checkpoints never erase a violation.
Reconnecting to the same identity repeats the failure while N remains.

The same House predicate applies to the unqualified legacy endpoint and projection
exports. Preserve legacy parameter/frame grammar: close/error at N, no new public_gap
control for an old request, no N+1 and no last-delivered identity crossing N.
A wider House may retain its separate old domain but cannot claim this baseline.

The public client independently checks original reserved occurrences at **every**
ingress, explicitly selected ordinary legacy path, legacy migration, cached display,
and projection import/export boundary. Server claims or lossy decoders do not
replace this guard. Stop an unsupported delivery without crossing its cursor or
manufacturing success. A safe independently selected ordinary path may be usable
without a new declaration, but cannot claim complete public-envelope-01 sync.
Failure after new-mode selection never triggers automatic fallback.

## Bidirectional cutover and recovery

Any baseline change, forward **or reverse**, requires a new, never-reused public
log incarnation, even if every retained event fits both baselines. Never reactivate
a former log ID for rollback. Persist used IDs/immutable bindings with the log's
storage history. A changed document or mode string does not establish a transition.

Before activating a switch invalidate old selections and fence delivery work.
Every page and pre-checkpoint check compares the authoritative baseline/log identity
captured at selection. An in-flight old connection must never certify a cycle across
the switch. Runtime implementations must coordinate this check and emission with
cutover so that a check-then-send race cannot leak a successful old checkpoint.
A cached old manifest/request cannot authenticate a replacement log.

Stop/join the sole receiver, obtain and validate the changed manifest through
existing trust, then explicitly select the new log with fresh positions. Preserve
old journals/provenance. Never copy old `(log,seq,CID)` bindings or cursors to the new
identity. Real replay creates new associations; content dedup may avoid repeating
a business effect while reception records are separately committed. An incarnation
mismatch gap carries only an untrusted hint: close and perform trusted discovery;
never auto reset, repin, grant policy or create a second socket.

An unsupported retained history is unavailable until an explicitly planned
reconstruction, or may remain unavailable. Deleting an offending record does not
make the old coverage promise ready. Reconstruction preserves the old log as
restricted provenance and uses a fresh identity with new sequence associations.
Only supported original events may be imported, without CID/signature rewriting.
The omitted wider history is explicitly outside the new log's coverage; retain
honest floors/gaps and do not pretend its checkpoints certify the old history.
This candidate performs no reconstruction or deployment.

## Two incarnation domains

`public_stream.log_incarnation` identifies a public log; `HouseBinding.incarnation`
identifies the server. A log/baseline switch alone does not imply a server/key
rotation, new trust pin, new session or grant/reactivation of local authority.
Actual House restore/rebuild follows the existing server/session lifecycle.
Stop/join, trusted manifest refresh and any required session maintenance need
separate runtime evidence. Log-level tests do not establish zero session impact.
