# Runtime acceptance boundary

The candidate provides algorithms, generated codecs, shared wire/signature vectors,
schema checks and an executable serial log referee. It does **not** provide evidence
that a running House or installed client already consumes this baseline.

| Requirement | Candidate evidence | Required runtime owner/evidence |
| --- | --- | --- |
| Exact supported bytes/CID/signatures, defaults, optional presence, wide counters, map order | TS/Rust/Python shared vectors | Each adapter invokes the same fixed rules on actual ingress |
| Numeric reserved occurrence, nested Profile and malformed/ambiguous wire | Three-language raw-wire matrix; valid-signature unsupported case | Client ingress/migration/cache/projection paths; both servers' admission/publication/backfill paths |
| Unknown legal HouseEvent retained without business interpretation | Shared opaque/signed vectors | Actual persistence/replay and any signed-scope associations |
| Exact authenticated baseline declaration | Schema negotiation matrix and signed manifest fixture | Actual trusted manifest verifier, preparer and metadata agreement |
| Immutable baseline metadata and fresh IDs for both cutover directions | Serial referee | Authoritative DB metadata, never-reused IDs and restart/restore evidence |
| Old selection/checkpoint fencing | Serial referee | Actual concurrent transaction/socket race test, including check-to-send window |
| Unsupported historical N; no N+1/checkpoint across N | Buffered-page/referee cases | Real DB replay/live/projection, injected historical/race violation |
| Scope-only unclassifiable N | Conservative connection gap in referee | Actual full log/index consistency, not a filtered query which hides N |
| Same-baseline reconnect and durable prior cursor | Referee and wire fixtures | Client durable journal and real receiver reconnect/stop/join |
| Legacy without new declaration | Client-side raw-wire model and no new legacy control | Every old endpoint and local cache/import/export boundary |
| Reverse rollback/cache-old-manifest | Fresh identity/referee and manifest digest tests | Runtime cutover, no old ID reuse, trusted explicit reselection |
| Public-log versus server/session incarnation | Proto and model distinction | Session owner validates actual lifecycle/restore; no implicit repin/grant/session claim |
| Session requests/ACKs | Retained requests/ACK bytes/signatures and sequence examples | Real session DB idempotency, races, lease/restart and original-request ACK binding |
| Ordinary DM | Codec/signature fixtures | Actual encryption, recipient isolation, token lifecycle and receive journal |
| Actions and receipts | Retained signatures, schemas and normative rules | Real authority, business commit, status/idempotency and per-attachment transactions |
| Clean regeneration and fixed consumption | Local standalone build/drift checks | Each consuming repository records exact bundle digest and runs required suites |

The Python `log_model.py` is a serial **protocol referee**, not an installable
persistence implementation. Its `admit` assumes separately verified identity and
signatures, and its in-memory cutover is not proof of a lock, transaction, database
isolation level or live connection fence. Do not import it as production storage.

Neither the candidate tests nor a handoff establishes end-to-end acceptance,
deployment, installation, public availability or permission to replace an existing
test baseline. Application-specific Map/MUD/newspaper behavior is outside this bundle.

Consumers should append their actual version, command, database/runtime and observed
results to their own integration record. Unsupported or untested cases remain explicit;
matching a manifest string alone is never a compatibility certificate.
