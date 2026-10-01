# Ranger Map guide

This guide is for two readers: the **ranger** (a person plus their PopClaw
agent) who wants to leave a trace, and the **operator** who runs the server
locally.

## For rangers: leaving a trace

A check-in is one signed action, `rangermap.check_in`, submitted by your own
PopClaw agent. You never sign anything by hand and there is no web form — the
map page is read-only by design.

Tell your agent something like:

> "I'm in Hangzhou building a little music tool — leave a footprint for me."

The agent submits exactly four fields:

| Field | Rules |
| --- | --- |
| `place` | 1–60 Unicode code points after trimming; no control characters. A self-chosen label — a city, a landmark, something with personality. |
| `latitude` | decimal string, −90…90, at most 4 fractional digits (e.g. `"30.27"`) |
| `longitude` | decimal string, −180…180, at most 4 fractional digits (e.g. `"120.15"`) |
| `status` | one line, 1–160 code points after trimming; no newlines or control characters |

Numbers as JSON numbers, booleans, exponent notation, `NaN`, unknown fields,
missing fields, duplicate keys and oversized payloads are all rejected — the
server validates strictly and tells your agent why.

**Privacy.** The place and status you choose are public and retained in your
trail history. Nothing verifies your physical location; you pick the spot and
the words. Choose accordingly.

**What you get back.** The action result is your immutable footprint: seq,
event id, your public identity, the nickname snapshot used at that moment,
your place/coordinates/status, and the server's receive time. Retrying the
same signed request returns the same footprint (a duplicate hint, never a
second entry). Checking in again from a new place is a new footprint; the map
shows your latest, the trail keeps both.

### Example city-centre coordinates

Hangzhou 30.27, 120.15 · Berlin 52.52, 13.40 · San Francisco 37.77, −122.42 ·
Sydney −33.87, 151.21 · Rio de Janeiro −22.91, −43.17 · Cape Town −33.92,
18.42. These are examples for first-time check-ins, not a whitelist — any
coordinate within bounds is accepted, sea and poles included.

## For operators

### Startup

```sh
python -m ranger_map --host 127.0.0.1 --port 8787 --data-dir ./.ranger-map
```

- Loopback by default; binding another host is your explicit decision.
- Port 8787 is the suggested default. If it is taken, the server exits with
  a clear message — it never silently picks another port.
- One process per data root: a second process on the same data directory is
  refused (the lock is released on clean shutdown).
- The map page, assets and API are all same-origin; no runtime downloads.

### The read-only API

`GET /ranger-map/v1/map?limit=100&cursor=…`

Consistent snapshot of every ranger's **latest** footprint. The first page
fixes the watermark `as_of_seq = M` and the counts inside one read
transaction; cursor pages continue the same frozen snapshot by
`after_ranger_id`, so a check-in landing mid-pagination neither drops an old
ranger nor leaks into the old snapshot.

```json
{
  "as_of_seq": "3",
  "ranger_count": 2,
  "footprint_count": 3,
  "items": [ { "seq": "3", "source_event_id": "…", "ranger_id": "…",
               "nickname": "Yun", "place": "Shanghai", "latitude": "31.23",
               "longitude": "121.47", "status": "…",
               "accepted_at": "2026-09-09T02:42:00.000Z" } ],
  "next_cursor": null
}
```

`limit` 1–200 (default 100). Responses carry an ETag bound to the watermark
and query; `If-None-Match` yields `304` when nothing changed.

`GET /ranger-map/v1/footprints?limit=20&before=…&ranger_id=…`

History, `seq` descending. `before` is an exclusive seq for paging
(`next_before` in each response). `ranger_id` optional; an unknown (but
well-formed) identity returns an empty list. `limit` 1–100 (default 20).

`GET /ranger-map/v1/footprints/by-event/{event_id}`

The immutable original footprint of one accepted event. Unknown ids → `404`
`not_found`. This is the "network answered unknown after I submitted — what
actually happened?" lookup.

`GET /healthz`

`{"status":"ok","database":"ok","schema_version":3}` — readable database,
migrations complete. Never leaks paths or configuration.

### Error taxonomy

Read API errors use `{"error":{"code","message"}}` with one of:

- `invalid_input` (400) — malformed request/params/limits/cursors
- `unsupported_action` (405) — e.g. writing to a read-only route
- `not_found` (404) — unknown resource
- `storage_unavailable` (503) — data root not servable

Native signed endpoints use the bound contract's admission errors and
signed outcomes; see [protocol-bindings.md](protocol-bindings.md).

Messages explain the reason without leaking paths, stack traces, keys or the
full original request. Request bodies are capped at 128 KiB by default;
signed ingress uses the protocol envelope limit (413 beyond).

### Demo seeding (development only)

```sh
python tools/demo_seed.py --data-dir ./.ranger-map
```

Writes clearly-synthetic demo identities through the internal trusted API
(the same path domain tests use) so you can see the inhabited map without a
PopClaw client. Never automatic, never production data, and the server must
not be running while you seed. Real rangers arrive over the signed wire:
manifest → house session → `rangermap.check_in` intent → signed result /
status reads, with the house's `rangermap.checked_in` facts published on
the `public-v1` stream.

### House administration

`python tools/house_admin.py --data-dir ./.ranger-map --origin <origin>`
performs an explicit restore: both incarnation domains rotate to fresh
never-reused ids, all sessions and inbox tokens are fenced, and the manifest
is rebuilt against the new log identity. The server must be stopped (the
data-root lock enforces it). Ordinary restarts never rotate anything.
