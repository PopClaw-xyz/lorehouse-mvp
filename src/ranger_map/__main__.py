"""Entry point: ``python -m ranger_map [--host H] [--port P] [--data-dir D]``.

Defaults are loopback ``127.0.0.1:8787`` with ``./.ranger-map`` as the data
root. The process stays in the foreground; Ctrl-C shuts down cleanly. A
second process on the same data root, an occupied port, or a data root
pinned to a different origin are all refused with clear diagnostics.
"""

from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

from . import __version__, protocol
from .app import create_app
from .errors import StorageUnavailable
from .house import HouseStateError, load_or_setup
from .keys import HouseIdentityError, load_or_create_identity
from .store import Store
from .streams import StreamHub


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m ranger_map",
        description="PopClaw Ranger Map - local LoreHouse reference server",
    )
    parser.add_argument("--host", default="127.0.0.1",
                        help="bind address (default: 127.0.0.1, loopback only)")
    parser.add_argument("--port", type=int, default=8787,
                        help="port (default: 8787; exits if occupied)")
    parser.add_argument("--data-dir", default="./.ranger-map", type=Path,
                        help="data root holding the SQLite database (default: ./.ranger-map)")
    return parser.parse_args(argv)


def ensure_port_free(host: str, port: int) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind((host, port))
    except OSError as exc:
        raise SystemExit(
            f"ranger-map: cannot bind {host}:{port} - {exc}. "
            "Choose another port with --port or stop the process using it; "
            "the server does not silently switch ports."
        ) from exc


def canonical_origin(host: str, port: int) -> str:
    return f"http://{host.lower()}:{port}"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data_dir = Path(args.data_dir)
    origin = canonical_origin(args.host, args.port)

    try:
        store = Store.open(data_dir)
    except StorageUnavailable as exc:
        print(f"ranger-map: {exc}", file=sys.stderr)
        return 1

    try:
        identity = load_or_create_identity(data_dir)
        state = load_or_setup(store, identity, origin)
    except (HouseIdentityError, HouseStateError) as exc:
        print(f"ranger-map: {exc}", file=sys.stderr)
        store.close()
        return 1

    ensure_port_free(args.host, args.port)
    hub = StreamHub(store)
    app = create_app(store, identity=identity, house_state=state, hub=hub)

    print(f"PopClaw Ranger Map {__version__}")
    print(f"  Map page      : http://{args.host}:{args.port}/")
    print(f"  Origin        : {origin} (bound to this data root)")
    print(f"  Data directory: {data_dir.resolve()}")
    print(f"  Database      : schema v{store.schema_version()} "
          f"({store.max_seq()} footprints so far)")
    print(f"  Protocol      : {protocol.CONTRACT_VERSION} adapter bound "
          f"(bundle {protocol.CONTRACT_BUNDLE_SHA256[:16]}…)")
    print(f"  House identity: {identity.house_key_id[:16]}… "
          f"(incarnation {state.server_incarnation[:16]}…)")
    print("  Press Ctrl-C to stop.")

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
