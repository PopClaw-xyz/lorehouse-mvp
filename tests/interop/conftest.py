"""Fixtures for native wire tests: a fully wired in-process house."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(REPO_ROOT), str(REPO_ROOT / "src")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from ranger_map.app import create_app  # noqa: E402
from ranger_map.house import load_or_setup  # noqa: E402
from ranger_map.keys import load_or_create_identity  # noqa: E402
from ranger_map.store import Store  # noqa: E402
from ranger_map.streams import StreamHub  # noqa: E402

from tests.interop.wire_helpers import ORIGIN  # noqa: E402


@pytest.fixture()
def house(tmp_path):
    """(client, store, identity, state, hub) wired like a real boot."""
    from starlette.testclient import TestClient

    data_dir = tmp_path / "data"
    store = Store.open(data_dir)
    identity = load_or_create_identity(data_dir)
    state = load_or_setup(store, identity, ORIGIN)
    hub = StreamHub(store)
    app = create_app(store, identity=identity, house_state=state, hub=hub)
    client = TestClient(app)
    yield SimpleNamespace(client=client, store=store, identity=identity,
                          state=state, hub=hub)
    store.close()

