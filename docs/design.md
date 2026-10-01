# Ranger Map design notes

This document records the design decisions behind the reference server so a
future maintainer can tell intent from accident. Product-level narrative
lives in the README; the agent/operator handbook is `guide.md`.

## Product shape

One business action — `rangermap.check_in`, "leave a footprint" — with four
self-chosen fields (place, latitude, longitude, status). Four facts the map
proves: **someone** (signed identities), **an action** (explicit check-ins,
not passive views), **a trail** (immutable history), **state** (one latest
pin per identity that others read). Fun comes from real participants filling
the map. Deliberately absent: scores, tasks, feeds, admin panels, anonymous
writes, location tracking, external map APIs, default seed people.

## Business core

`src/ranger_map/check_in.py` owns everything about the rule:

- **Strict validation on raw bytes** before anything else: ≤4 KiB, valid
  UTF-8, single JSON object, no duplicate keys (via `object_pairs_hook`), no
  `NaN`/`Infinity` (via `parse_constant`), nesting depth ≤8, exactly the four
  known fields (`additionalProperties=false` semantically), correct types.
- **Coordinates are decimal strings**, not numbers: the pinned action-kind
  schema profile supports integers only (no floats, no negative bounds), so
  coordinates are bounded human-readable strings matched against
  `^-?(0|[1-9][0-9]{0,2})(\.[0-9]{1,4})?$` plus a `Decimal` range check
  (±90 / ±180). The stored projection normalises trailing zeros and `-0`
  (`"30.2700" → "30.27"`, `"-0.0" → "0"`); the original signed bytes are
  kept verbatim in the events table. Longitude 180 projects to the same map
  position as −180 in the frontend; stored data is untouched.
- **Identity comes only from the trusted context** — a verified public
  (base58) identity, a display-name snapshot (or `None` → short-identity
  fallback), and the verified event CID (64 lowercase hex). An `actor_id`
  inside the JSON body is an unknown field and rejected; nobody can sign as
  someone else through payload fields.
- **Idempotency by event CID**: `apply_check_in` re-checks the CID under the
  write lock (double-checked after a pre-check for the fast path). A retry
  returns the original immutable footprint with `duplicate=true` and writes
  nothing. A new CID is a new trace even with identical text — no content
  hashing, no silent dedup.

## Storage

One SQLite file (WAL, `foreign_keys=ON`, `synchronous=FULL`,
`busy_timeout=5s`), one process, one connection guarded by an `RLock`; all
transactions are `BEGIN IMMEDIATE` writes or `BEGIN DEFERRED` snapshot reads,
and never span an `await` (every DB call is synchronous). A `flock` on
`server.lock` refuses a second server process on the same data root, and is
released on clean shutdown.

Tables: `events` (CID PK, raw bytes, kind, received time), `footprints`
(`seq INTEGER PRIMARY KEY AUTOINCREMENT`, `source_event_id UNIQUE` FK,
ranger, nickname snapshot, place/lat/lon/status, `accepted_at_ms`, index
`(ranger_id, seq DESC)`), `profiles` (provisional — fields will follow the
final public Profile contract), `schema_migrations`.

Invariants worth knowing:

- `accepted_at` is server receive time (ISO-8601 UTC, ms) — never claimed to
  be arrival time; "latest" is decided by `seq`, so client clock skew cannot
  reorder history (tested with a backwards-jumping clock).
- Nickname snapshots are frozen per footprint; renames change future rows
  only (tested).
- There is no separate "latest" table: the map is a projection
  (`MAX(seq) per ranger WHERE seq<=M`) computed in the reader — no drift
  between two copies of the truth.

## Snapshot pagination

`GET /ranger-map/v1/map` fixes the watermark `M = MAX(seq)` and both counts
in one read transaction, then pages latest-per-ranger ordered by `ranger_id`
(stable) via an opaque cursor `{v, as_of_seq, after_ranger_id}`
(version-tagged base64url JSON, strictly validated: alphabet, size, keys,
types, `as_of_seq ≤ MAX(seq)`). A check-in committed mid-pagination is
invisible to the open snapshot and appears on the next full refresh —
neither rangers nor counts drift inside one snapshot (tested). ETags bind
watermark + query params; `If-None-Match` → 304.

History paging is exclusive-`before` on `seq` with `next_before` in the
response. Unknown-but-valid ranger ids return an honest empty list; anything
malformed is `400 invalid_input`. Nothing from the query string ever reaches
SQL except as bound parameters.

## HTTP surface & failure posture

- Request bodies are capped at 128 KiB by default (with the protocol's
  envelope limit on signed ingress) by a pure-ASGI middleware that
  buffers with a hard limit (Content-Length pre-check + streamed
  accumulation) and answers `413 invalid_input`.
- Read API errors use `invalid_input` / `unsupported_action` / `not_found` /
  `storage_unavailable`. Native signed endpoints use the bound public
  contract's admission errors and signed outcomes; see
  [protocol-bindings.md](protocol-bindings.md). Messages never leak paths,
  stacks, keys or raw payloads (tested).
- Unknown routes under the API prefixes return JSON errors; writes to
  read-only routes are `405 unsupported_action`.

## The comic map page

Vanilla HTML/CSS/JS, no build step, no external requests (CSP:
`default-src 'self'`, no inline script/style). The first screen is the
inhabited world: compact branded header (approved PopClaw wordmark, light
and dark variants), the land map as the main scene, and every ranger
directly on the map at their true submitted coordinate — deterministic
illustrated portrait, name + short identity, chosen-place tag, and their
latest accepted status in a speech bubble (with "last check-in" time, not a
presence indicator).

- **Presentation vs geography**: the anchor dot sits at the exact projected
  coordinate; when markers collide, the portrait box moves (spiral search,
  fully clamped inside the canvas) and a dashed leader line ties it back to
  the anchor. Saved coordinates are never adjusted. Dense spots fan out;
  everyone stays reachable through the "All rangers" drawer and keyboard
  navigation (Tab/Arrows, `aria-pressed` selection, Esc closes drawers).
- **Portraits** are deterministic per identity (FNV-1a hash → palette, eyes,
  mouth, headwear) — locally generated SVG, no avatar fetching. Real
  signed-profile avatars arrive with the protocol adapter's asset policy;
  until then this fallback is explicit, never one-letter pins.
- **Refresh**: 5-second conditional polling while the page is visible
  (paused when hidden, immediate refresh on return), first page via
  `If-None-Match` (304 → no DOM churn), cursor pages assembled fully before
  the map is replaced, in-flight rounds aborted when a new one starts, and
  per-ranger pop-in animation only for genuinely new/moved markers,
  respecting `prefers-reduced-motion`.
- **States**: real zero state ("Be the first ranger…"), error banner with
  last-good time + retry, per-page loading progress. No fabricated visitors,
  no fake conversations, no online dots.
- **Pan/zoom**: pointer drag, wheel zoom toward cursor, pinch, buttons,
  bounded so the canvas always covers the viewport; keyboard selection works
  without a pointer.

Brand: China red `#ED2925`, charcoal `#2B2B2B`, white — the approved PopClaw
palette; paper `#F7F6F2` and sea/land tones are presentation choices, with a
full dark variant via `prefers-color-scheme` (ink flips to light cream so
outlines and text stay legible on dark surfaces).

## Map asset

`tools/build_land_svg.py` converts the vendored Natural Earth 110m Land
GeoJSON (public domain, release v5.1.2, SHA-256 in the SVG header and
`THIRD-PARTY-NOTICES.md`) into two equirectangular SVGs (light/dark) on a
1000×500 viewBox — the same projection the page uses for markers, so
coordinates and coastlines always align. No political boundaries; no runtime
downloads; the build is deterministic and pure-stdlib.

## Testing philosophy

Domain invariants over mirror tests: input rejection matrices, double-checked
idempotency under real thread concurrency, rollback on injected failure
between event and footprint insert (with a clean re-apply afterwards), frozen
snapshot pagination across a mid-pagination write, restart persistence,
duplicate-retry across restart, process lifecycle (clean start, occupied
port, second data-root process), HTTP limits/cursors/ETag/404/405/413, and
static-page security posture (CSP present, no inline handlers, no external
URLs, no server data baked into the HTML). Business unit tests construct
internal trusted contexts directly — that is explicitly not an HTTP write
path and not interoperability evidence; `tests/interop` arrives with the
protocol adapter and skips are never counted as passes.
