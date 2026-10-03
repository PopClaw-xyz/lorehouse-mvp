# PopClaw public contracts

Protocol candidate **0.1.0-public-envelope-01.7**, envelope baseline
**public-envelope-01**. This is the common protocol source for PopClaw clients and
independent LoreHouse implementations. It is not a running server or a complete SDK.
Candidate conformance does not establish runtime integration or public release.

Start with [implementer guidance](protocol/public-envelope-01/IMPLEMENTERS.md),
then the normative [baseline](protocol/public-envelope-01/BASELINE.md),
[capability contract](protocol/public-envelope-01/SPEC.md),
[public stream](protocol/public-envelope-01/PUBLIC-STREAM.md),
[identity read authentication](protocol/public-envelope-01/READ-AUTH.md),
[receipts](protocol/public-envelope-01/RECEIPTS.md) and
[resource limits](protocol/public-envelope-01/LIMITS.md),
[signing recipes](protocol/public-envelope-01/SIGNING.md) and
[trust binding](protocol/public-envelope-01/TRUST.md).
[Compatibility changes](protocol/public-envelope-01/CHANGES.md) identify real wire
and coverage differences. [Runtime acceptance](protocol/public-envelope-01/RUNTIME.md)
separates protocol tests from required server/client evidence.

| Material | Path | Purpose |
| --- | --- | --- |
| Authoritative message definitions | `proto/` | Eight proto files and their generated descriptor |
| TypeScript codecs and algorithms | `ts/contracts/`, `ts/algorithms/` | Generated messages, canonical/CID/session helpers and original-wire guards |
| Rust codecs and algorithms | `crates/rust/`, `crates/algorithms/` | The same definitions and rules; no server source |
| Python consumption bridge | `python/` | Pinned descriptor messages, original-wire guards and parity tests |
| Shared machine vectors | `fixtures/` | Supported bytes, signatures, session cores and structural adversarial cases |
| JSON schema | `protocol/public-envelope-01/`, `protocol/retained/` | Capability and retained optional payload shapes |

The first-release runtime scope is one public world stream and one ordinary private
DM stream per House. Actions require separately authenticated capabilities and
bounded local authority. Optional structured private-message and execution-closure
shapes are retained for interoperability validation; their codecs do not promise
runtime availability. No generic multi-stream or complete SDK product is provided.

From the source bundle root, follow [BUILD.md](../../BUILD.md). The main commands are:

```sh
pnpm install --frozen-lockfile --ignore-scripts
pnpm build
pnpm test
cargo test --locked --workspace
.venv/bin/python -m unittest discover -s packages/contracts/python -v
node scripts/test-schemas.mjs
python3 scripts/check-generated.py
python3 scripts/verify-bundle.py
```

Generation and fixtures are reproducible from the included source and pinned build
inputs. Do not edit generated files. Pin the full bundle digest in
`CONTRACT-MANIFEST.json`; a baseline string alone does not identify all contract
files. [Fixed consumption](protocol/public-envelope-01/CONSUMPTION.md) describes
controlled copies without a registry-publishing requirement.

Protocol source and modifications use Apache-2.0; dependencies retain their own
licenses. Read [NOTICE](../../NOTICE) and [third-party information](../../THIRD-PARTY.md).
