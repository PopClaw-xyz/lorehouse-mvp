# Build and verify the protocol source bundle

Work from this bundle's root. It is independently buildable; it does not require a
private monorepo, server source, sibling project, maintainer path or registry release.
The root build files are standalone-candidate inputs. When incorporating them into
an existing repository, merge the needed entries and preserve that repository's
README, license, package identity and unrelated build configuration.

## Toolchain and dependencies

Exact locally tested versions and generator pins are in TOOLCHAIN.json. Install
Node 25.9.0, pnpm 9.12.0, Rust 1.88.0, Python 3.9 or newer, and protoc 34.1. The
[official protoc release](https://github.com/protocolbuffers/protobuf/releases/tag/v34.1)
provides platform binaries. The Linux CI download is fixed by its upstream SHA-256;
other platforms must supply the same compiler version. No compiler binary is bundled.

```sh
pnpm install --frozen-lockfile --ignore-scripts
python3 -m venv .venv
.venv/bin/pip install -r packages/contracts/python/requirements.txt
pnpm build
```

Cargo.lock, pnpm-lock.yaml and exact Python requirements fix the dependency versions.
The source bundle includes license notices, not installed dependencies. The Python
bridge loads the included descriptor; it avoids a protoc-version-specific Python
source generator/runtime coupling. Its cryptography dependency is used for test
signatures and fixture generation, not a promise of a complete client crypto SDK.

## Checks

```sh
pnpm test
cargo test --locked --workspace
.venv/bin/python -m unittest discover -s packages/contracts/python -v
node scripts/test-schemas.mjs
python3 scripts/check-generated.py
python3 scripts/verify-bundle.py
```

`pnpm test` builds first, then runs both TypeScript packages and schema/negotiation
checks. Python includes byte/signature parity and a **serial protocol model**, not
DB/runtime tests. Rust tests include the same original-wire/signature vectors.
No tests log in to a real House or install/update a client. The protocol-only GitHub
workflow is provided; local command success is not a claim of a completed hosted CI run.

The suites cover 29 retained canonical vectors (28 EventEnvelopes and one standalone
VerifiedPlatform), session request/ACK fixtures, eight retained world-signing rules,
new signed envelopes and malicious wire cases. Retained fixture URLs and keys are
fixed test bytes, never instructions to contact a service or trust those identities.

## Regeneration

```sh
bash scripts/gen-proto.sh
cargo run --locked -p popclaw-algorithms --bin gen-fixtures
.venv/bin/python scripts/gen-baseline-fixtures.py
```

Proto is the authority. The script verifies generator versions, regenerates Rust
and TypeScript codecs, applies the checked-in deterministic TS map-encoding transform,
and emits proto/descriptor.pb. No generated output is hand-edited. `check-generated.py`
snapshots all generated outputs, reruns these steps, and fails on any changed or
missing output without relying on Git history. Generated outputs may change only
with an explicit new reviewed candidate and updated manifest.

After an intentional reviewed change, `python3 scripts/write-manifest.py` freezes
the new file set. Consumers verify a separately trusted expected digest using
`verify-bundle.py --expected <digest>`; they do not regenerate the pin themselves.
Source-build success does not prove runtime readiness, log cutover, session safety,
end-to-end interoperability or permission to publish.
