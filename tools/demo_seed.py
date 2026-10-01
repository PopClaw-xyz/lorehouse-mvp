#!/usr/bin/env python3
"""Development-only demo seeder for PopClaw Ranger Map.

This tool exists so a developer can see the inhabited comic map locally
BEFORE the signed PopClaw protocol adapter is bound. It writes through the
same internal trusted-context API used by domain tests - never through an
unsigned HTTP endpoint - with clearly synthetic identities ("demo" ids that
could never be mistaken for real public keys). It is not part of the server,
never runs automatically, and leaves a marker event so seeded data is easy
to recognise.

Usage:
    python tools/demo_seed.py --data-dir ./.ranger-map

Idempotence follows the business rule: re-running with the same event CIDs
produces no new footprints. The server must NOT be running on the same data
root (the single-instance lock will refuse one of the two).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ranger_map.check_in import TrustedCheckInContext, apply_check_in  # noqa: E402
from ranger_map.store import Store  # noqa: E402

# Synthetic demo identities. The "demo" substring keeps them unmistakable
# from real base58 public identities in a screenshot or a database dump.
DEMOS = [
    # (ranger_id, nickname, event suffix, place, lat, lon, status)
    ("demoYunA1111111111111111111111111A", "Yun", "d001", "Hangzhou", "30.27", "120.15",
     "My first music tool finally sings."),
    ("demoottoB2222222222222222222222B", "Otto", "d002", "Berlin", "52.52", "13.40",
     "Coffee refilled, one chapter read."),
    ("demoLunaC3333333333333333333333C", "Luna", "d003", "Rio de Janeiro", "-22.91", "-43.17",
     "Found a whole afternoon by the sea."),
    ("demoKikiD4444444444444444444444D", "Kiki", "d004", "Cape Town", "-33.92", "18.42",
     "The wind on the mountain is huge."),
    ("demoPipE5555555555555555555555E", "Pip", "d005", "Sydney", "-33.87", "151.21",
     "Just finished a strange little poem."),
    ("demoMomoF6666666666666666666666F", "Momo", "d006", "San Francisco", "37.77", "-122.42",
     "Cooking up new ideas again today."),
]

# Yun moves on: second event for the same identity (Shanghai), like the
# acceptance storyline - the map shows Shanghai, the trail keeps Hangzhou.
DEMOS.append(
    ("demoYunA1111111111111111111111111A", "Yun", "d007", "Shanghai", "31.23", "121.47",
     "Version one is ready. Onwards!")
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="./.ranger-map", type=Path)
    args = parser.parse_args()

    store = Store.open(args.data_dir)
    try:
        created = 0
        for ranger_id, nickname, suffix, place, lat, lon, status in DEMOS:
            event_id = ("de" + suffix.ljust(62, "0"))[:64]
            import json

            raw = json.dumps(
                {"place": place, "latitude": lat, "longitude": lon, "status": status}
            ).encode("utf-8")
            result = apply_check_in(
                store,
                TrustedCheckInContext(ranger_id=ranger_id, nickname=nickname,
                                      source_event_id=event_id),
                raw,
            )
            created += 0 if result.duplicate else 1
        snap = store.map_snapshot_page(None, None, 200)
        print(f"demo seed complete: {created} new footprints "
              f"({snap.ranger_count} rangers, {snap.footprint_count} footprints total)")
        print("synthetic identities only - do not ship this data anywhere.")
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
