#!/usr/bin/env python3
"""Operator tool for explicit house maintenance.

``--restore`` rotates BOTH incarnation domains (server + public log) into
fresh, never-reused identities, retires the old ids, fences every session
and inbox token, and rebuilds the manifest against the new log identity.
Ordinary restarts never do this; reconstruction is a deliberate operator
action (BASELINE.md "Bidirectional cutover and recovery").

``--refresh-guide`` additionally pins the current package guide and its
revision/hash with the rebuilt manifest. Without it, restore retains the
existing guide bytes and revision. House key, origin and accepted data stay.

The server must NOT be running on the same data root: the data-root lock
enforces single-instance access, so restore fails loudly if it is.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ranger_map import house as house_mod  # noqa: E402
from ranger_map.keys import KEY_FILENAME, load_or_create_identity  # noqa: E402
from ranger_map.store import DB_FILENAME, Store  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="./.ranger-map", type=Path)
    parser.add_argument("--origin", required=True,
                        help="canonical origin the data root is pinned to")
    parser.add_argument('--restore', action='store_true', required=True,
                        help='explicitly rotate incarnations and fence sessions')
    parser.add_argument('--refresh-guide', action='store_true',
                        help='with restore, pin the current fixed package guide')
    args = parser.parse_args()

    if args.refresh_guide:
        try:
            house_mod.bundled_guide()
        except house_mod.HouseStateError as exc:
            print(f'house-admin: {exc}', file=sys.stderr)
            return 1

    if not all((args.data_dir / name).is_file() for name in (KEY_FILENAME, DB_FILENAME)):
        print('house-admin: restore requires the existing data root with its House key and database',
              file=sys.stderr)
        return 1

    try:
        store = Store.open(args.data_dir)
    except Exception as exc:
        print(f"house-admin: {exc}", file=sys.stderr)
        return 1
    try:
        identity = load_or_create_identity(args.data_dir)
        state = house_mod.load_or_setup(store, identity, args.origin)
        old_log = state.log_incarnation
        new_state = house_mod.restore(store, identity, state,
                                      refresh_guide=args.refresh_guide)
        print("restore complete:")
        print(f"  retired log incarnation : {old_log}")
        print(f"  new server incarnation  : {new_state.server_incarnation}")
        print(f"  new public log          : {new_state.log_incarnation}")
        print(f"  new capability revision : {new_state.manifest_digest}")
        print("sessions fenced, inbox tokens revoked, old ids retired forever")
        return 0
    except Exception as exc:
        print(f'house-admin: {exc}', file=sys.stderr)
        return 1
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
