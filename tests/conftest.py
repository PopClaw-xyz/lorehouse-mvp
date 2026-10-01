"""Shared test configuration: import path setup and store fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
for entry in (str(REPO_ROOT), str(SRC)):
    if entry not in sys.path:
        sys.path.insert(0, entry)


class FakeClock:
    """Controllable millisecond clock for ordering tests."""

    def __init__(self, start_ms: int = 1_800_000_000_000) -> None:
        self.now_ms = start_ms

    def __call__(self) -> int:
        return self.now_ms

    def advance(self, ms: int) -> None:
        self.now_ms += ms


@pytest.fixture()
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture()
def store(tmp_path, clock):
    from ranger_map.store import Store

    s = Store.open(tmp_path / "data", clock=clock)
    yield s
    s.close()


@pytest.fixture()
def ctx_factory():
    """Build trusted check-in contexts with synthetic isolated test identities."""

    from ranger_map.check_in import TrustedCheckInContext

    counter = {"n": 0}

    def make(ranger_id: str = "8rANGERtest111111111111111111111", nickname: str | None = "Yun",
             event_hex: str | None = None):
        counter["n"] += 1
        if event_hex is None:
            event_hex = f"{counter['n']:064x}"
        return TrustedCheckInContext(
            ranger_id=ranger_id, nickname=nickname, source_event_id=event_hex
        )

    return make


def valid_params_bytes(place="Hangzhou", lat="30.27", lon="120.15",
                       status="Building a little music tool.") -> bytes:
    import json

    return json.dumps(
        {"place": place, "latitude": lat, "longitude": lon, "status": status}
    ).encode("utf-8")
