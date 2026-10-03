# Third-party notices and asset sources

This file records the licenses of bundled dependencies and the provenance of
every non-source asset shipped in this repository. The project code itself is
Apache-2.0 (see `LICENSE`); this file does not change that.

## Runtime Python dependencies (installed via `requirements.lock`)

| Package | Version | License | Source |
| --- | --- | --- | --- |
| starlette | 1.6.0 | BSD-3-Clause | https://github.com/encode/starlette |
| uvicorn | 0.52.4 | BSD-3-Clause | https://github.com/encode/uvicorn |
| anyio | 4.15.1 | MIT | https://github.com/agronholm/anyio |
| click | 8.5.0 | BSD-3-Clause | https://github.com/pallets/click |
| h11 | 0.16.0 | MIT | https://github.com/python-hyper/h11 |
| idna | 3.19 | BSD-3-Clause | https://github.com/kjd/idna |
| typing_extensions | 4.16.0 | PSF-2.4 | https://github.com/python/typing_extensions |
| protobuf | 6.33.6 | BSD-3-Clause | https://github.com/protocolbuffers/protobuf |
| cryptography | 46.0.5 | Apache-2.0 OR BSD-3-Clause | https://github.com/pyca/cryptography |
| cffi | 2.1.1 | MIT | https://github.com/python-cffi/cffi |
| pycparser | 3.0 | BSD-3-Clause | https://github.com/eliben/pycparser |

## Vendored protocol bundle: `vendor/popclaw-contracts/`

A controlled copy of the PopClaw public contract source bundle
**0.1.0-public-envelope-01.7** (envelope baseline `public-envelope-01`), taken
from the locally accepted commit `37db76d8573e9931c24671a05a89ec606cbfab06`,
protocol subtree `8f1745ed5be08a16248b88c7705dfdff4d5b70ea`.
This acceptance covers local integration, not a public release. Bundle pin:
`f7993f282db354476efe2ef5bf9eb6fb07282934df2b5fc884465bb2cbd3fcec`.
`tools/vendor_verify_contracts.py` re-verifies the 273-file copy against that
pin; it is never re-pinned to downloaded content. The bundle keeps its own
`LICENSE`, `NOTICE`, `SOURCE-PROVENANCE.json` and `THIRD-PARTY.md` inside the
vendor directory and is Apache-2.0 like this repository.

Each package carries its own license text in its distribution; the lock file
pins the exact versions above.

## Development-only dependencies (`requirements-dev.lock`)

| Package | Version | License |
| --- | --- | --- |
| pytest | 9.1.1 | MIT |
| httpx | 0.28.1 | BSD-3-Clause |
| httpcore | 1.0.9 | BSD-3-Clause |
| certifi | 2026.7.22 | MPL-2.0 |
| idna | 3.19 | BSD-3-Clause |
| PyNaCl | 1.6.0 | Apache-2.0 |
| iniconfig | 2.3.0 | MIT |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pluggy | 1.6.0 | MIT |
| Pygments | 2.21.0 | BSD-3-Clause |

## Map asset: world land outline

- Asset: `src/ranger_map/static/assets/world-land.svg`
- Built by: `tools/build_land_svg.py` (development-time tool, pure stdlib)
- Source data: Natural Earth `ne_110m_land.geojson`, from the
  [natural-earth-vector](https://github.com/nvkelso/natural-earth-vector)
  repository, release tag **v5.1.2**
- Source URL: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_110m_land.geojson
- Vendored input copy: `tools/vendor_ne_110m_land.geojson`
- SHA-256 of the vendored input:
  `9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9`
- License: **Public Domain**. Natural Earth data is free for use in any form
  with attribution assumed (https://www.naturalearthdata.com/about/terms-of-use/).
- The SVG is an equirectangular (plate carree) projection of the 110m land
  polygons. It carries no political boundaries. The build is deterministic:
  the same input file always yields the same SVG, and the SVG embeds the
  source URL, version tag and input SHA-256 in a comment.

## Brand assets

The README's approved horizontal SVG assets and their bundled font license
are recorded in [docs/brand/README.md](docs/brand/README.md). The application
wordmarks below are retained separately.

- `src/ranger_map/static/assets/brand/popclaw-large-wordmark-positive@2x.png`
- `src/ranger_map/static/assets/brand/popclaw-large-wordmark-reverse@2x.png`

These are the approved PopClaw wordmarks provided by the PopClaw brand owner
on 2026-09-09. They are brand assets, kept separately from the Apache-2.0
source code: the copyright and trademark in the wordmarks remains with their
owner. Nothing in `LICENSE` grants rights in these marks; the repository
license covers the source code and documentation only.
