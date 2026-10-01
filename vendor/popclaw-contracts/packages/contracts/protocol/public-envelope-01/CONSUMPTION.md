# Fixed-version consumption

The public authority belongs at `popclaw/packages/contracts/`. Other repositories
consume a fixed candidate/release, not a private directory or a floating branch.
No additional protocol repository or public registry publication is required.

`CONTRACT-MANIFEST.json` at the source-bundle root records every allowed file's SHA-256
and one bundle digest. The digest is SHA-256 of the sorted concatenation of
`<file-sha256>  <relative-path>\n` entries. The manifest itself is excluded to avoid
self-reference. Generated files, build inputs, license notices and vectors are included;
local dependencies, build outputs, temporary evidence and the single exact filename
`.DS_Store` — which a desktop file browser writes without anyone editing the bundle —
are excluded. Nothing else is: any other unlisted file under the bundle root is a
membership mismatch, and that exclusion is one filename, not a hidden-file exemption.

1. Obtain the exact bundle from the approved distribution source. Record its digest
   through a trusted review/release channel; an untrusted manifest cannot authenticate
   its own replacement. No repository URL in a draft is evidence of publication.
2. Run `python3 scripts/verify-bundle.py --expected <trusted-bundle-digest>` before
   consuming it. This checks membership, hashes and the pinned digest. Do not silently
   update your expected digest to match a downloaded replacement.
3. Store a controlled copy under a dedicated vendor directory, preserving the bundle's
   relative layout and notices. Record the version/digest in your consuming repository.
   Do not overwrite existing root README, LICENSE or other repository-owned files.
4. The Python reference can use the fixed `proto/descriptor.pb`, Python consumption
   bridge, vectors and their notices within that controlled copy. The Rust server can
   use the fixed crates/proto with its own approved build integration. The client can
   build the TypeScript packages. Each consumer documents the exact subset if it
   intentionally extracts files; verify that subset against the full trusted manifest.
5. Update through an explicit new candidate, review its change log, regenerate and run
   required tests. Never hand-edit a second schema copy, auto-follow main, repin trust,
   switch logs or update live installations as part of a dependency refresh.

A protocol file-set digest, envelope baseline, public-log incarnation, HouseBinding
server incarnation and product version are separate identities. Fixing one does not
implicitly update the others. The bundle includes a serial model for conformance
only; production servers implement and test their own transactions/fences.
