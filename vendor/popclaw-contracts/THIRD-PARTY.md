# Third-party components

This source candidate contains protocol definitions, project source, generated codecs, a binary schema descriptor, test vectors, tests, and documentation. It does not bundle node_modules, Cargo registry sources, a Python environment, or dependency wheels. Consumers obtain external dependencies using the supplied lockfiles and requirements. The project Apache-2.0 license does not replace third-party licenses.

## Runtime and generation dependencies

TypeScript codecs use protobufjs 7.6.6 (BSD-3-Clause), including its @protobufjs support packages and long 5.3.2 (Apache-2.0). Algorithms use @noble/hashes 1.8.0 (MIT). Rust codecs use prost 0.13.5 (Apache-2.0); Rust algorithms and vector generation also use sha2 0.10.9, hex 0.4.3, bs58 0.5.1, anyhow 1.0.104 and serde_json 1.0.151 (MIT/Apache alternatives), and ed25519-dalek 2.2.0 (BSD-3-Clause). Exact transitive resolution is recorded in Cargo.lock and pnpm-lock.yaml.

Bindings and the schema descriptor are generated with protobufjs-cli 1.1.3 (BSD-3-Clause), prost-build 0.13.5 (Apache-2.0), and protoc 34.1 (BSD-3-Clause). The protobufjs and protoc license texts state that generated code belongs to the owner of the input file, while support libraries retain their own licenses. Generated-file markers and generator versions preserve provenance; they do not independently establish input ownership.

Python tests dynamically consume the descriptor with protobuf 6.33.6 (BSD-3-Clause) and cryptography 46.0.5 (Apache-2.0 OR BSD-3-Clause). The inspected CPython 3.9 environment additionally used cffi 2.0.0 (MIT), pycparser 2.23 (BSD-3-Clause), and typing_extensions 4.16.0 (PSF-2.0). No generated Python binding files or wheels are bundled.

Schema validation tests use ajv 8.18.0 (MIT), with fast-deep-equal 3.1.3 (MIT), fast-uri 3.1.7 (BSD-3-Clause), json-schema-traverse 1.0.0 (MIT), and require-from-string 2.0.2 (MIT). Their complete installed license texts are archived below.

## Attribution archive

The accompanying archive preserves complete license texts for the named direct runtime dependencies and generation tools, available Rust transitive components, selected test tools, and selected upstream notices. File hashes below identify the exact copied texts. This is a source-candidate attribution aid, not a claim that the archive covers every optional platform or every embedded component of a future binary distribution.

Notable retained materials include TypeScript ThirdPartyNoticeText.txt, js2xmlparser and xmlcreate NOTICE files, and unicode-ident LICENSE-UNICODE. unicode-ident requires Unicode-3.0 in addition to its MIT/Apache alternative. Original alternative-license expressions are preserved without selecting or rewriting terms.

Before distributing bundled dependencies, executable packages, containers, or wheels, assemble the actual shipped dependency closure and retain its applicable license and notice texts. Native cryptography wheel components and uninstalled platform-specific optional dependencies have not been fully inventoried here. Installed test-tool metadata alone is not a substitute for those artifact-specific checks.

## Archived text index

Paths are relative to third-party-licenses/. Each row names an archived text, its associated package metadata license, and SHA-256.

| Component | Version | License expression | Text | SHA-256 |
|---|---|---|---|---|
| python: cffi | 2.0.0 | MIT | [python/cffi-2.0.0/AUTHORS](third-party-licenses/python/cffi-2.0.0/AUTHORS) | `2a67a60bbfb33759d67d645ff131b8e6d6bc4cafc232d751fcac3eda4d314cc8` |
| python: cffi | 2.0.0 | MIT | [python/cffi-2.0.0/LICENSE](third-party-licenses/python/cffi-2.0.0/LICENSE) | `5ba24ddc57067f9249add644c3afc41a5d6dc37e23433ef759d95df370b0af63` |
| python: cryptography | 46.0.5 | Apache-2.0 OR BSD-3-Clause | [python/cryptography-46.0.5/LICENSE](third-party-licenses/python/cryptography-46.0.5/LICENSE) | `3e0c7c091a948b82533ba98fd7cbb40432d6f1a9acbf85f5922d2f99a93ae6bb` |
| python: cryptography | 46.0.5 | Apache-2.0 OR BSD-3-Clause | [python/cryptography-46.0.5/LICENSE.APACHE](third-party-licenses/python/cryptography-46.0.5/LICENSE.APACHE) | `aac73b3148f6d1d7111dbca32099f68d26c644c6813ae1e4f05f6579aa2663fe` |
| python: cryptography | 46.0.5 | Apache-2.0 OR BSD-3-Clause | [python/cryptography-46.0.5/LICENSE.BSD](third-party-licenses/python/cryptography-46.0.5/LICENSE.BSD) | `602c4c7482de6479dd2e9793cda275e5e63d773dacd1eca689232ab7008fb4fb` |
| python: protobuf | 6.33.6 | 3-Clause BSD License | [python/protobuf-6.33.6/LICENSE](third-party-licenses/python/protobuf-6.33.6/LICENSE) | `6e5e117324afd944dcf67f36cf329843bc1a92229a8cd9bb573d7a83130fea7d` |
| python: pycparser | 2.23 | BSD-3-Clause | [python/pycparser-2.23/LICENSE](third-party-licenses/python/pycparser-2.23/LICENSE) | `0c846399369ea76ddd7b5c44fe6d16497415fcf015f5cbb508c24bf98b81c5b1` |
| python: typing_extensions | 4.16.0 | PSF-2.0 | [python/typing_extensions-4.16.0/LICENSE](third-party-licenses/python/typing_extensions-4.16.0/LICENSE) | `3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf` |
| rust: aho-corasick | 1.1.5 | Unlicense OR MIT | [rust/aho-corasick-1.1.5/LICENSE-MIT](third-party-licenses/rust/aho-corasick-1.1.5/LICENSE-MIT) | `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f` |
| rust: aho-corasick | 1.1.5 | Unlicense OR MIT | [rust/aho-corasick-1.1.5/UNLICENSE](third-party-licenses/rust/aho-corasick-1.1.5/UNLICENSE) | `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c` |
| rust: anyhow | 1.0.104 | MIT OR Apache-2.0 | [rust/anyhow-1.0.104/LICENSE-APACHE](third-party-licenses/rust/anyhow-1.0.104/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: anyhow | 1.0.104 | MIT OR Apache-2.0 | [rust/anyhow-1.0.104/LICENSE-MIT](third-party-licenses/rust/anyhow-1.0.104/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: base64ct | 1.8.3 | Apache-2.0 OR MIT | [rust/base64ct-1.8.3/LICENSE-APACHE](third-party-licenses/rust/base64ct-1.8.3/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: base64ct | 1.8.3 | Apache-2.0 OR MIT | [rust/base64ct-1.8.3/LICENSE-MIT](third-party-licenses/rust/base64ct-1.8.3/LICENSE-MIT) | `2d1c57bff28344b9e698f51063bc8509799cc4c99a4e0cf2aa3f7e7c3e1f9a9d` |
| rust: bitflags | 2.13.1 | MIT OR Apache-2.0 | [rust/bitflags-2.13.1/LICENSE-APACHE](third-party-licenses/rust/bitflags-2.13.1/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: bitflags | 2.13.1 | MIT OR Apache-2.0 | [rust/bitflags-2.13.1/LICENSE-MIT](third-party-licenses/rust/bitflags-2.13.1/LICENSE-MIT) | `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` |
| rust: block-buffer | 0.10.4 | MIT OR Apache-2.0 | [rust/block-buffer-0.10.4/LICENSE-APACHE](third-party-licenses/rust/block-buffer-0.10.4/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: block-buffer | 0.10.4 | MIT OR Apache-2.0 | [rust/block-buffer-0.10.4/LICENSE-MIT](third-party-licenses/rust/block-buffer-0.10.4/LICENSE-MIT) | `d5c22aa3118d240e877ad41c5d9fa232f9c77d757d4aac0c2f943afc0a95e0ef` |
| rust: bs58 | 0.5.1 | MIT/Apache-2.0 | [rust/bs58-0.5.1/LICENSE-APACHE](third-party-licenses/rust/bs58-0.5.1/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: bs58 | 0.5.1 | MIT/Apache-2.0 | [rust/bs58-0.5.1/LICENSE-MIT](third-party-licenses/rust/bs58-0.5.1/LICENSE-MIT) | `42d3bf7e7d4d49d72c0555d14ed99c3ee7ce9ce3cbffbc38bbafe8c103f50969` |
| rust: bytes | 1.12.1 | MIT | [rust/bytes-1.12.1/LICENSE](third-party-licenses/rust/bytes-1.12.1/LICENSE) | `45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42` |
| rust: cfg-if | 1.0.4 | MIT OR Apache-2.0 | [rust/cfg-if-1.0.4/LICENSE-APACHE](third-party-licenses/rust/cfg-if-1.0.4/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: cfg-if | 1.0.4 | MIT OR Apache-2.0 | [rust/cfg-if-1.0.4/LICENSE-MIT](third-party-licenses/rust/cfg-if-1.0.4/LICENSE-MIT) | `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397` |
| rust: const-oid | 0.9.6 | Apache-2.0 OR MIT | [rust/const-oid-0.9.6/LICENSE-APACHE](third-party-licenses/rust/const-oid-0.9.6/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: const-oid | 0.9.6 | Apache-2.0 OR MIT | [rust/const-oid-0.9.6/LICENSE-MIT](third-party-licenses/rust/const-oid-0.9.6/LICENSE-MIT) | `bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682` |
| rust: cpufeatures | 0.2.17 | MIT OR Apache-2.0 | [rust/cpufeatures-0.2.17/LICENSE-APACHE](third-party-licenses/rust/cpufeatures-0.2.17/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: cpufeatures | 0.2.17 | MIT OR Apache-2.0 | [rust/cpufeatures-0.2.17/LICENSE-MIT](third-party-licenses/rust/cpufeatures-0.2.17/LICENSE-MIT) | `ae9baa7beea910273c2f384c2a6b721fb7bd02bda3436074a1072e4ee689f985` |
| rust: crypto-common | 0.1.7 | MIT OR Apache-2.0 | [rust/crypto-common-0.1.7/LICENSE-APACHE](third-party-licenses/rust/crypto-common-0.1.7/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: crypto-common | 0.1.7 | MIT OR Apache-2.0 | [rust/crypto-common-0.1.7/LICENSE-MIT](third-party-licenses/rust/crypto-common-0.1.7/LICENSE-MIT) | `3521672491a3479422d5fe1aca6645dd2984090f85da6e5205abfb18fb7a6897` |
| rust: curve25519-dalek | 4.1.3 | BSD-3-Clause | [rust/curve25519-dalek-4.1.3/LICENSE](third-party-licenses/rust/curve25519-dalek-4.1.3/LICENSE) | `cca0bd3c4fcdba74145ef9d49c62337e2c9fbf9368288f11d0547f1b0273219f` |
| rust: der | 0.7.10 | Apache-2.0 OR MIT | [rust/der-0.7.10/LICENSE-APACHE](third-party-licenses/rust/der-0.7.10/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: der | 0.7.10 | Apache-2.0 OR MIT | [rust/der-0.7.10/LICENSE-MIT](third-party-licenses/rust/der-0.7.10/LICENSE-MIT) | `ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d` |
| rust: digest | 0.10.7 | MIT OR Apache-2.0 | [rust/digest-0.10.7/LICENSE-APACHE](third-party-licenses/rust/digest-0.10.7/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: digest | 0.10.7 | MIT OR Apache-2.0 | [rust/digest-0.10.7/LICENSE-MIT](third-party-licenses/rust/digest-0.10.7/LICENSE-MIT) | `9e0dfd2dd4173a530e238cb6adb37aa78c34c6bc7444e0e10c1ab5d8881f63ba` |
| rust: ed25519 | 2.2.3 | Apache-2.0 OR MIT | [rust/ed25519-2.2.3/LICENSE-APACHE](third-party-licenses/rust/ed25519-2.2.3/LICENSE-APACHE) | `78779d420019e6b4630376af8e86b6b335ee8a2f89ede6e0411e0469a326aaa4` |
| rust: ed25519 | 2.2.3 | Apache-2.0 OR MIT | [rust/ed25519-2.2.3/LICENSE-MIT](third-party-licenses/rust/ed25519-2.2.3/LICENSE-MIT) | `b3470648aff02beb36d7a53240fc9260ed80ed93bd43bace6b67d7ef7336ee33` |
| rust: ed25519-dalek | 2.2.0 | BSD-3-Clause | [rust/ed25519-dalek-2.2.0/LICENSE](third-party-licenses/rust/ed25519-dalek-2.2.0/LICENSE) | `7a313964a6e050794d2ad57f4863c11f6bbe055c0ae6ce2cf3b9fc45150bada3` |
| rust: either | 1.18.0 | MIT OR Apache-2.0 | [rust/either-1.18.0/LICENSE-APACHE](third-party-licenses/rust/either-1.18.0/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: either | 1.18.0 | MIT OR Apache-2.0 | [rust/either-1.18.0/LICENSE-MIT](third-party-licenses/rust/either-1.18.0/LICENSE-MIT) | `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545` |
| rust: equivalent | 1.0.2 | Apache-2.0 OR MIT | [rust/equivalent-1.0.2/LICENSE-APACHE](third-party-licenses/rust/equivalent-1.0.2/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: equivalent | 1.0.2 | Apache-2.0 OR MIT | [rust/equivalent-1.0.2/LICENSE-MIT](third-party-licenses/rust/equivalent-1.0.2/LICENSE-MIT) | `7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349` |
| rust: errno | 0.3.14 | MIT OR Apache-2.0 | [rust/errno-0.3.14/LICENSE-APACHE](third-party-licenses/rust/errno-0.3.14/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: errno | 0.3.14 | MIT OR Apache-2.0 | [rust/errno-0.3.14/LICENSE-MIT](third-party-licenses/rust/errno-0.3.14/LICENSE-MIT) | `8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2` |
| rust: fastrand | 2.5.0 | Apache-2.0 OR MIT | [rust/fastrand-2.5.0/LICENSE-APACHE](third-party-licenses/rust/fastrand-2.5.0/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: fastrand | 2.5.0 | Apache-2.0 OR MIT | [rust/fastrand-2.5.0/LICENSE-MIT](third-party-licenses/rust/fastrand-2.5.0/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: fixedbitset | 0.5.7 | MIT OR Apache-2.0 | [rust/fixedbitset-0.5.7/LICENSE-APACHE](third-party-licenses/rust/fixedbitset-0.5.7/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: fixedbitset | 0.5.7 | MIT OR Apache-2.0 | [rust/fixedbitset-0.5.7/LICENSE-MIT](third-party-licenses/rust/fixedbitset-0.5.7/LICENSE-MIT) | `ce592787ff2321feab698a4c612237f4378cc658ebb1d472913e5802cc47afb4` |
| rust: generic-array | 0.14.7 | MIT | [rust/generic-array-0.14.7/LICENSE](third-party-licenses/rust/generic-array-0.14.7/LICENSE) | `c09aae9d3c77b531f56351a9947bc7446511d6b025b3255312d3e3442a9a7583` |
| rust: getrandom | 0.2.17 | MIT OR Apache-2.0 | [rust/getrandom-0.2.17/LICENSE-APACHE](third-party-licenses/rust/getrandom-0.2.17/LICENSE-APACHE) | `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf` |
| rust: getrandom | 0.2.17 | MIT OR Apache-2.0 | [rust/getrandom-0.2.17/LICENSE-MIT](third-party-licenses/rust/getrandom-0.2.17/LICENSE-MIT) | `42fa16951ce7f24b5a467a40e5b449a1d41e662f97ca779864f053f39e097737` |
| rust: getrandom | 0.4.3 | MIT OR Apache-2.0 | [rust/getrandom-0.4.3/LICENSE-APACHE](third-party-licenses/rust/getrandom-0.4.3/LICENSE-APACHE) | `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf` |
| rust: getrandom | 0.4.3 | MIT OR Apache-2.0 | [rust/getrandom-0.4.3/LICENSE-MIT](third-party-licenses/rust/getrandom-0.4.3/LICENSE-MIT) | `523a42c25d245dde9c015f882cec7f4555aad883382a6cf19b4b7d9b2cd5419b` |
| rust: hashbrown | 0.17.1 | MIT OR Apache-2.0 | [rust/hashbrown-0.17.1/LICENSE-APACHE](third-party-licenses/rust/hashbrown-0.17.1/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: hashbrown | 0.17.1 | MIT OR Apache-2.0 | [rust/hashbrown-0.17.1/LICENSE-MIT](third-party-licenses/rust/hashbrown-0.17.1/LICENSE-MIT) | `ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2` |
| rust: heck | 0.5.0 | MIT OR Apache-2.0 | [rust/heck-0.5.0/LICENSE-APACHE](third-party-licenses/rust/heck-0.5.0/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: heck | 0.5.0 | MIT OR Apache-2.0 | [rust/heck-0.5.0/LICENSE-MIT](third-party-licenses/rust/heck-0.5.0/LICENSE-MIT) | `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0` |
| rust: hex | 0.4.3 | MIT OR Apache-2.0 | [rust/hex-0.4.3/LICENSE-APACHE](third-party-licenses/rust/hex-0.4.3/LICENSE-APACHE) | `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08` |
| rust: hex | 0.4.3 | MIT OR Apache-2.0 | [rust/hex-0.4.3/LICENSE-MIT](third-party-licenses/rust/hex-0.4.3/LICENSE-MIT) | `f7bdb3426d045cd50efd4953026e3eb5a83d0199f458a075602611b9344da5b9` |
| rust: indexmap | 2.14.2 | Apache-2.0 OR MIT | [rust/indexmap-2.14.2/LICENSE-APACHE](third-party-licenses/rust/indexmap-2.14.2/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: indexmap | 2.14.2 | Apache-2.0 OR MIT | [rust/indexmap-2.14.2/LICENSE-MIT](third-party-licenses/rust/indexmap-2.14.2/LICENSE-MIT) | `ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055` |
| rust: itertools | 0.14.0 | MIT OR Apache-2.0 | [rust/itertools-0.14.0/LICENSE-APACHE](third-party-licenses/rust/itertools-0.14.0/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: itertools | 0.14.0 | MIT OR Apache-2.0 | [rust/itertools-0.14.0/LICENSE-MIT](third-party-licenses/rust/itertools-0.14.0/LICENSE-MIT) | `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545` |
| rust: itoa | 1.0.18 | MIT OR Apache-2.0 | [rust/itoa-1.0.18/LICENSE-APACHE](third-party-licenses/rust/itoa-1.0.18/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: itoa | 1.0.18 | MIT OR Apache-2.0 | [rust/itoa-1.0.18/LICENSE-MIT](third-party-licenses/rust/itoa-1.0.18/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: libc | 0.2.189 | MIT OR Apache-2.0 | [rust/libc-0.2.189/LICENSE-APACHE](third-party-licenses/rust/libc-0.2.189/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: libc | 0.2.189 | MIT OR Apache-2.0 | [rust/libc-0.2.189/LICENSE-MIT](third-party-licenses/rust/libc-0.2.189/LICENSE-MIT) | `123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e` |
| rust: log | 0.4.34 | MIT OR Apache-2.0 | [rust/log-0.4.34/LICENSE-APACHE](third-party-licenses/rust/log-0.4.34/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: log | 0.4.34 | MIT OR Apache-2.0 | [rust/log-0.4.34/LICENSE-MIT](third-party-licenses/rust/log-0.4.34/LICENSE-MIT) | `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` |
| rust: memchr | 2.8.3 | Unlicense OR MIT | [rust/memchr-2.8.3/LICENSE-MIT](third-party-licenses/rust/memchr-2.8.3/LICENSE-MIT) | `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f` |
| rust: memchr | 2.8.3 | Unlicense OR MIT | [rust/memchr-2.8.3/UNLICENSE](third-party-licenses/rust/memchr-2.8.3/UNLICENSE) | `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c` |
| rust: multimap | 0.10.1 | MIT OR Apache-2.0 | [rust/multimap-0.10.1/LICENSE-APACHE](third-party-licenses/rust/multimap-0.10.1/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: multimap | 0.10.1 | MIT OR Apache-2.0 | [rust/multimap-0.10.1/LICENSE-MIT](third-party-licenses/rust/multimap-0.10.1/LICENSE-MIT) | `23ce717d2face34a1ae9af6a8c8fbbf488875afee16374d7a10ce79d41e22f37` |
| rust: once_cell | 1.21.4 | MIT OR Apache-2.0 | [rust/once_cell-1.21.4/LICENSE-APACHE](third-party-licenses/rust/once_cell-1.21.4/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: once_cell | 1.21.4 | MIT OR Apache-2.0 | [rust/once_cell-1.21.4/LICENSE-MIT](third-party-licenses/rust/once_cell-1.21.4/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: petgraph | 0.7.1 | MIT OR Apache-2.0 | [rust/petgraph-0.7.1/LICENSE-APACHE](third-party-licenses/rust/petgraph-0.7.1/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: petgraph | 0.7.1 | MIT OR Apache-2.0 | [rust/petgraph-0.7.1/LICENSE-MIT](third-party-licenses/rust/petgraph-0.7.1/LICENSE-MIT) | `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545` |
| rust: pkcs8 | 0.10.2 | Apache-2.0 OR MIT | [rust/pkcs8-0.10.2/LICENSE-APACHE](third-party-licenses/rust/pkcs8-0.10.2/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: pkcs8 | 0.10.2 | Apache-2.0 OR MIT | [rust/pkcs8-0.10.2/LICENSE-MIT](third-party-licenses/rust/pkcs8-0.10.2/LICENSE-MIT) | `ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d` |
| rust: prettyplease | 0.2.37 | MIT OR Apache-2.0 | [rust/prettyplease-0.2.37/LICENSE-APACHE](third-party-licenses/rust/prettyplease-0.2.37/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: prettyplease | 0.2.37 | MIT OR Apache-2.0 | [rust/prettyplease-0.2.37/LICENSE-MIT](third-party-licenses/rust/prettyplease-0.2.37/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: proc-macro2 | 1.0.107 | MIT OR Apache-2.0 | [rust/proc-macro2-1.0.107/LICENSE-APACHE](third-party-licenses/rust/proc-macro2-1.0.107/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: proc-macro2 | 1.0.107 | MIT OR Apache-2.0 | [rust/proc-macro2-1.0.107/LICENSE-MIT](third-party-licenses/rust/proc-macro2-1.0.107/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: prost | 0.13.5 | Apache-2.0 | [rust/prost-0.13.5/LICENSE](third-party-licenses/rust/prost-0.13.5/LICENSE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: prost-build | 0.13.5 | Apache-2.0 | [rust/prost-build-0.13.5/LICENSE](third-party-licenses/rust/prost-build-0.13.5/LICENSE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: prost-derive | 0.13.5 | Apache-2.0 | [rust/prost-derive-0.13.5/LICENSE](third-party-licenses/rust/prost-derive-0.13.5/LICENSE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: prost-types | 0.13.5 | Apache-2.0 | [rust/prost-types-0.13.5/LICENSE](third-party-licenses/rust/prost-types-0.13.5/LICENSE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: quote | 1.0.47 | MIT OR Apache-2.0 | [rust/quote-1.0.47/LICENSE-APACHE](third-party-licenses/rust/quote-1.0.47/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: quote | 1.0.47 | MIT OR Apache-2.0 | [rust/quote-1.0.47/LICENSE-MIT](third-party-licenses/rust/quote-1.0.47/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: rand_core | 0.6.4 | MIT OR Apache-2.0 | [rust/rand_core-0.6.4/LICENSE-APACHE](third-party-licenses/rust/rand_core-0.6.4/LICENSE-APACHE) | `6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51` |
| rust: rand_core | 0.6.4 | MIT OR Apache-2.0 | [rust/rand_core-0.6.4/LICENSE-MIT](third-party-licenses/rust/rand_core-0.6.4/LICENSE-MIT) | `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b` |
| rust: regex | 1.13.1 | MIT OR Apache-2.0 | [rust/regex-1.13.1/LICENSE-APACHE](third-party-licenses/rust/regex-1.13.1/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: regex | 1.13.1 | MIT OR Apache-2.0 | [rust/regex-1.13.1/LICENSE-MIT](third-party-licenses/rust/regex-1.13.1/LICENSE-MIT) | `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` |
| rust: regex-automata | 0.4.18 | MIT OR Apache-2.0 | [rust/regex-automata-0.4.18/LICENSE-APACHE](third-party-licenses/rust/regex-automata-0.4.18/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: regex-automata | 0.4.18 | MIT OR Apache-2.0 | [rust/regex-automata-0.4.18/LICENSE-MIT](third-party-licenses/rust/regex-automata-0.4.18/LICENSE-MIT) | `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` |
| rust: regex-syntax | 0.8.11 | MIT OR Apache-2.0 | [rust/regex-syntax-0.8.11/LICENSE-APACHE](third-party-licenses/rust/regex-syntax-0.8.11/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: regex-syntax | 0.8.11 | MIT OR Apache-2.0 | [rust/regex-syntax-0.8.11/LICENSE-MIT](third-party-licenses/rust/regex-syntax-0.8.11/LICENSE-MIT) | `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` |
| rust: rustc_version | 0.4.1 | MIT OR Apache-2.0 | [rust/rustc_version-0.4.1/LICENSE-APACHE](third-party-licenses/rust/rustc_version-0.4.1/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: rustc_version | 0.4.1 | MIT OR Apache-2.0 | [rust/rustc_version-0.4.1/LICENSE-MIT](third-party-licenses/rust/rustc_version-0.4.1/LICENSE-MIT) | `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5` |
| rust: rustix | 1.1.4 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT | [rust/rustix-1.1.4/LICENSE-APACHE](third-party-licenses/rust/rustix-1.1.4/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: rustix | 1.1.4 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT | [rust/rustix-1.1.4/LICENSE-Apache-2.0_WITH_LLVM-exception](third-party-licenses/rust/rustix-1.1.4/LICENSE-Apache-2.0_WITH_LLVM-exception) | `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5` |
| rust: rustix | 1.1.4 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT | [rust/rustix-1.1.4/LICENSE-MIT](third-party-licenses/rust/rustix-1.1.4/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: semver | 1.0.28 | MIT OR Apache-2.0 | [rust/semver-1.0.28/LICENSE-APACHE](third-party-licenses/rust/semver-1.0.28/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: semver | 1.0.28 | MIT OR Apache-2.0 | [rust/semver-1.0.28/LICENSE-MIT](third-party-licenses/rust/semver-1.0.28/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: serde | 1.0.229 | MIT OR Apache-2.0 | [rust/serde-1.0.229/LICENSE-APACHE](third-party-licenses/rust/serde-1.0.229/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: serde | 1.0.229 | MIT OR Apache-2.0 | [rust/serde-1.0.229/LICENSE-MIT](third-party-licenses/rust/serde-1.0.229/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: serde_core | 1.0.229 | MIT OR Apache-2.0 | [rust/serde_core-1.0.229/LICENSE-APACHE](third-party-licenses/rust/serde_core-1.0.229/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: serde_core | 1.0.229 | MIT OR Apache-2.0 | [rust/serde_core-1.0.229/LICENSE-MIT](third-party-licenses/rust/serde_core-1.0.229/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: serde_derive | 1.0.229 | MIT OR Apache-2.0 | [rust/serde_derive-1.0.229/LICENSE-APACHE](third-party-licenses/rust/serde_derive-1.0.229/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: serde_derive | 1.0.229 | MIT OR Apache-2.0 | [rust/serde_derive-1.0.229/LICENSE-MIT](third-party-licenses/rust/serde_derive-1.0.229/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: serde_json | 1.0.151 | MIT OR Apache-2.0 | [rust/serde_json-1.0.151/LICENSE-APACHE](third-party-licenses/rust/serde_json-1.0.151/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: serde_json | 1.0.151 | MIT OR Apache-2.0 | [rust/serde_json-1.0.151/LICENSE-MIT](third-party-licenses/rust/serde_json-1.0.151/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: sha2 | 0.10.9 | MIT OR Apache-2.0 | [rust/sha2-0.10.9/LICENSE-APACHE](third-party-licenses/rust/sha2-0.10.9/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: sha2 | 0.10.9 | MIT OR Apache-2.0 | [rust/sha2-0.10.9/LICENSE-MIT](third-party-licenses/rust/sha2-0.10.9/LICENSE-MIT) | `b4eb00df6e2a4d22518fcaa6a2b4646f249b3a3c9814509b22bd2091f1392ff1` |
| rust: signature | 2.2.0 | Apache-2.0 OR MIT | [rust/signature-2.2.0/LICENSE-APACHE](third-party-licenses/rust/signature-2.2.0/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: signature | 2.2.0 | Apache-2.0 OR MIT | [rust/signature-2.2.0/LICENSE-MIT](third-party-licenses/rust/signature-2.2.0/LICENSE-MIT) | `b3470648aff02beb36d7a53240fc9260ed80ed93bd43bace6b67d7ef7336ee33` |
| rust: spki | 0.7.3 | Apache-2.0 OR MIT | [rust/spki-0.7.3/LICENSE-APACHE](third-party-licenses/rust/spki-0.7.3/LICENSE-APACHE) | `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5` |
| rust: spki | 0.7.3 | Apache-2.0 OR MIT | [rust/spki-0.7.3/LICENSE-MIT](third-party-licenses/rust/spki-0.7.3/LICENSE-MIT) | `c995204cc6bad2ed67dd41f7d89bb9f1a9d48e0edd745732b30640d7912089a4` |
| rust: subtle | 2.6.1 | BSD-3-Clause | [rust/subtle-2.6.1/LICENSE](third-party-licenses/rust/subtle-2.6.1/LICENSE) | `d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b` |
| rust: syn | 2.0.119 | MIT OR Apache-2.0 | [rust/syn-2.0.119/LICENSE-APACHE](third-party-licenses/rust/syn-2.0.119/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: syn | 2.0.119 | MIT OR Apache-2.0 | [rust/syn-2.0.119/LICENSE-MIT](third-party-licenses/rust/syn-2.0.119/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: syn | 3.0.5 | MIT OR Apache-2.0 | [rust/syn-3.0.5/LICENSE-APACHE](third-party-licenses/rust/syn-3.0.5/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: syn | 3.0.5 | MIT OR Apache-2.0 | [rust/syn-3.0.5/LICENSE-MIT](third-party-licenses/rust/syn-3.0.5/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: tempfile | 3.27.0 | MIT OR Apache-2.0 | [rust/tempfile-3.27.0/LICENSE-APACHE](third-party-licenses/rust/tempfile-3.27.0/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: tempfile | 3.27.0 | MIT OR Apache-2.0 | [rust/tempfile-3.27.0/LICENSE-MIT](third-party-licenses/rust/tempfile-3.27.0/LICENSE-MIT) | `8b427f5bc501764575e52ba4f9d95673cf8f6d80a86d0d06599852e1a9a20a36` |
| rust: tinyvec | 1.13.2 | Zlib OR Apache-2.0 OR MIT | [rust/tinyvec-1.13.2/LICENSE-APACHE.md](third-party-licenses/rust/tinyvec-1.13.2/LICENSE-APACHE.md) | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| rust: tinyvec | 1.13.2 | Zlib OR Apache-2.0 OR MIT | [rust/tinyvec-1.13.2/LICENSE-MIT.md](third-party-licenses/rust/tinyvec-1.13.2/LICENSE-MIT.md) | `fd80a26fbb3f644af1fa994134446702932968519797227e07a1368dea80f0bc` |
| rust: tinyvec | 1.13.2 | Zlib OR Apache-2.0 OR MIT | [rust/tinyvec-1.13.2/LICENSE-ZLIB.md](third-party-licenses/rust/tinyvec-1.13.2/LICENSE-ZLIB.md) | `84b34dd7608f7fb9b17bd588a6bf392bf7de504e2716f024a77d89f1b145a151` |
| rust: tinyvec_macros | 0.1.1 | MIT OR Apache-2.0 OR Zlib | [rust/tinyvec_macros-0.1.1/LICENSE-APACHE.md](third-party-licenses/rust/tinyvec_macros-0.1.1/LICENSE-APACHE.md) | `4f44572785f35152c1fd2eadf565b7e079c0f300b4324f0af653419f9d76b735` |
| rust: tinyvec_macros | 0.1.1 | MIT OR Apache-2.0 OR Zlib | [rust/tinyvec_macros-0.1.1/LICENSE-MIT.md](third-party-licenses/rust/tinyvec_macros-0.1.1/LICENSE-MIT.md) | `1dd8eca0f83669e75fa119e34fb9e1be9d16e3e9b6368962b8019db6e8ae5f7b` |
| rust: tinyvec_macros | 0.1.1 | MIT OR Apache-2.0 OR Zlib | [rust/tinyvec_macros-0.1.1/LICENSE-ZLIB.md](third-party-licenses/rust/tinyvec_macros-0.1.1/LICENSE-ZLIB.md) | `41ace205715d9f19a3214218cc1c01d57c533e02cd0fef7c8e51a49a7fce5ac5` |
| rust: typenum | 1.20.1 | MIT OR Apache-2.0 | [rust/typenum-1.20.1/LICENSE](third-party-licenses/rust/typenum-1.20.1/LICENSE) | `db11fec9946737df39ca3898d9cd8c10ec6f6c3a884a6802b0ad0b81b4e8f23a` |
| rust: typenum | 1.20.1 | MIT OR Apache-2.0 | [rust/typenum-1.20.1/LICENSE-APACHE](third-party-licenses/rust/typenum-1.20.1/LICENSE-APACHE) | `516b24e051bf5630880ebbd55c40a25ce9552ebaf8970a53e8976eb70e522406` |
| rust: typenum | 1.20.1 | MIT OR Apache-2.0 | [rust/typenum-1.20.1/LICENSE-MIT](third-party-licenses/rust/typenum-1.20.1/LICENSE-MIT) | `a825bd853ab71619a4923d7b4311221427848070ff44d990da39b0b274c1683f` |
| rust: unicode-ident | 1.0.24 | (MIT OR Apache-2.0) AND Unicode-3.0 | [rust/unicode-ident-1.0.24/LICENSE-APACHE](third-party-licenses/rust/unicode-ident-1.0.24/LICENSE-APACHE) | `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` |
| rust: unicode-ident | 1.0.24 | (MIT OR Apache-2.0) AND Unicode-3.0 | [rust/unicode-ident-1.0.24/LICENSE-MIT](third-party-licenses/rust/unicode-ident-1.0.24/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| rust: unicode-ident | 1.0.24 | (MIT OR Apache-2.0) AND Unicode-3.0 | [rust/unicode-ident-1.0.24/LICENSE-UNICODE](third-party-licenses/rust/unicode-ident-1.0.24/LICENSE-UNICODE) | `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1` |
| rust: version_check | 0.9.5 | MIT/Apache-2.0 | [rust/version_check-0.9.5/LICENSE-APACHE](third-party-licenses/rust/version_check-0.9.5/LICENSE-APACHE) | `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` |
| rust: version_check | 0.9.5 | MIT/Apache-2.0 | [rust/version_check-0.9.5/LICENSE-MIT](third-party-licenses/rust/version_check-0.9.5/LICENSE-MIT) | `b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e` |
| rust: zeroize | 1.9.0 | Apache-2.0 OR MIT | [rust/zeroize-1.9.0/LICENSE-APACHE](third-party-licenses/rust/zeroize-1.9.0/LICENSE-APACHE) | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| rust: zeroize | 1.9.0 | Apache-2.0 OR MIT | [rust/zeroize-1.9.0/LICENSE-MIT](third-party-licenses/rust/zeroize-1.9.0/LICENSE-MIT) | `8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b` |
| rust: zmij | 1.0.23 | MIT | [rust/zmij-1.0.23/LICENSE-MIT](third-party-licenses/rust/zmij-1.0.23/LICENSE-MIT) | `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` |
| tools: protoc | 34.1 | BSD-3-Clause | [tools/protoc-34.1/LICENSE](third-party-licenses/tools/protoc-34.1/LICENSE) | `6e5e117324afd944dcf67f36cf329843bc1a92229a8cd9bb573d7a83130fea7d` |
| javascript: ajv | 8.18.0 | MIT | [javascript/ajv-8.18.0/LICENSE](third-party-licenses/javascript/ajv-8.18.0/LICENSE) | `a05350a88e318e4f5f2c2a1ff1e2e88daa4dd38e6e78b71cccae422bdc762cc3` |
| javascript: fast-deep-equal | 3.1.3 | MIT | [javascript/fast-deep-equal-3.1.3/LICENSE](third-party-licenses/javascript/fast-deep-equal-3.1.3/LICENSE) | `7bf9b2de73a6b356761c948d0e9eeb4be6c1270bd04c79cd489c1e400ffdfc1a` |
| javascript: fast-uri | 3.1.7 | BSD-3-Clause | [javascript/fast-uri-3.1.7/LICENSE](third-party-licenses/javascript/fast-uri-3.1.7/LICENSE) | `b010b0dfdfdb23d7396e03b82cd4621fc9bb8f95d6b0aea70b9c24e12074c786` |
| javascript: json-schema-traverse | 1.0.0 | MIT | [javascript/json-schema-traverse-1.0.0/LICENSE](third-party-licenses/javascript/json-schema-traverse-1.0.0/LICENSE) | `7bf9b2de73a6b356761c948d0e9eeb4be6c1270bd04c79cd489c1e400ffdfc1a` |
| javascript: require-from-string | 2.0.2 | MIT | [javascript/require-from-string-2.0.2/license](third-party-licenses/javascript/require-from-string-2.0.2/license) | `6ee0feb1f6ef996ff5a68600f8cf98909cf412d39ef3cdceaefd87d636fa1b7f` |
