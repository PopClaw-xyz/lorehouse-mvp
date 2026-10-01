"""Unit tests for the one business rule: rangermap.check_in application."""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tests.conftest import valid_params_bytes  # noqa: E402

from ranger_map.check_in import apply_check_in  # noqa: E402
from ranger_map.errors import InvalidInput  # noqa: E402

RANGER_A = "ArangerA1111111111111111111111111"
RANGER_B = "BrangerB2222222222222222222222222"


def ev(n: int) -> str:
    return f"{n:064x}"


def test_first_check_in_creates_footprint(store, ctx_factory):
    ctx = ctx_factory(ranger_id=RANGER_A, nickname="Yun", event_hex=ev(1))
    result = apply_check_in(store, ctx, valid_params_bytes())
    assert result.duplicate is False
    fp = result.footprint
    assert fp.seq == 1
    assert fp.ranger_id == RANGER_A
    assert fp.nickname == "Yun"
    assert fp.place == "Hangzhou"
    assert fp.latitude == "30.27"
    assert fp.longitude == "120.15"
    assert fp.status == "Building a little music tool."
    assert fp.source_event_id == ev(1)
    # accepted_at is a UTC ISO-8601 timestamp with milliseconds.
    assert fp.accepted_at.endswith("Z")
    assert len(fp.accepted_at) == len("2026-09-09T02:42:00.000Z")


def test_nickname_falls_back_to_short_identity(store, ctx_factory):
    ctx = ctx_factory(ranger_id=RANGER_A, nickname=None, event_hex=ev(1))
    result = apply_check_in(store, ctx, valid_params_bytes())
    assert result.footprint.nickname == RANGER_A[:8] + "…"


def test_second_event_same_ranger_new_footprint_latest_wins(store, ctx_factory):
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                   valid_params_bytes(place="Hangzhou"))
    result = apply_check_in(
        store, ctx_factory(RANGER_A, "Yun", ev(2)),
        valid_params_bytes(place="Shanghai", lat="31.23", lon="121.47",
                           status="The first version is ready."),
    )
    assert result.footprint.seq == 2
    assert result.footprint.place == "Shanghai"

    history = store.history_page(ranger_id=RANGER_A, limit=10)
    places = [fp.place for fp in history.items]
    assert places == ["Shanghai", "Hangzhou"]  # seq descending


def test_same_event_retry_is_idempotent(store, ctx_factory):
    first = apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                           valid_params_bytes())
    again = apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                           valid_params_bytes())
    assert again.duplicate is True
    assert again.footprint == first.footprint
    counts = store.map_snapshot_page(as_of_seq=None, after_ranger_id=None, limit=10)
    assert counts.footprint_count == 1
    assert counts.ranger_count == 1


def test_retry_after_remap_cannot_alter_original_result(store, ctx_factory):
    first = apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                           valid_params_bytes(place="Hangzhou"))
    # Even a differently-looking body under the same event CID returns the
    # original immutable result and stores nothing new.
    again = apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                           valid_params_bytes(place="Berlin"))
    assert again.duplicate is True
    assert again.footprint.place == "Hangzhou"
    assert first.footprint.place == "Hangzhou"
    assert store.map_snapshot_page(None, None, 10).footprint_count == 1


def test_new_event_same_content_is_new_footprint(store, ctx_factory):
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)), valid_params_bytes())
    result = apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(2)),
                            valid_params_bytes())
    assert result.duplicate is False
    assert result.footprint.seq == 2
    assert store.map_snapshot_page(None, None, 10).footprint_count == 2


def test_same_name_different_keys_are_two_rangers(store, ctx_factory):
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)), valid_params_bytes())
    apply_check_in(
        store, ctx_factory(RANGER_B, "Yun", ev(2)),
        valid_params_bytes(place="Berlin", lat="52.52", lon="13.40",
                           status="Hello from Berlin."),
    )
    snap = store.map_snapshot_page(None, None, 10)
    assert snap.ranger_count == 2
    assert len(snap.items) == 2
    assert {fp.ranger_id for fp in snap.items} == {RANGER_A, RANGER_B}


def test_nickname_snapshot_not_rewritten_on_rename(store, ctx_factory):
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)), valid_params_bytes())
    apply_check_in(store, ctx_factory(RANGER_A, "Yun2", ev(2)),
                   valid_params_bytes(place="Shanghai"))
    history = store.history_page(ranger_id=RANGER_A, limit=10)
    by_place = {fp.place: fp.nickname for fp in history.items}
    assert by_place["Hangzhou"] == "Yun"     # history snapshot unchanged
    assert by_place["Shanghai"] == "Yun2"    # latest shows latest nickname


def test_invalid_params_rejected_before_storage(store, ctx_factory):
    with pytest.raises(InvalidInput):
        apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                       b'{"place":"","latitude":"1","longitude":"1","status":"x"}')
    assert store.map_snapshot_page(None, None, 10).footprint_count == 0


def test_failure_between_event_and_footprint_rolls_back(store, ctx_factory,
                                                        monkeypatch):
    original = store.insert_footprint

    def exploding(*args, **kwargs):
        raise RuntimeError("injected failure after event insert")

    monkeypatch.setattr(store, "insert_footprint", exploding)
    with pytest.raises(RuntimeError):
        apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                       valid_params_bytes())
    monkeypatch.setattr(store, "insert_footprint", original)

    # No half result: no event row, no footprint.
    events = store._connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    footprints = store._connection.execute(
        "SELECT COUNT(*) FROM footprints").fetchone()[0]
    assert (events, footprints) == (0, 0)

    # And the same CID can still be applied cleanly afterwards.
    result = apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                            valid_params_bytes())
    assert result.duplicate is False


def test_raw_bytes_stored_verbatim(store, ctx_factory):
    raw = valid_params_bytes(place="Café ☕")
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)), raw)
    blob = store._connection.execute(
        "SELECT raw_bytes FROM events WHERE event_id = ?", (ev(1),)).fetchone()[0]
    assert bytes(blob) == raw


def test_client_clock_skew_does_not_reorder_history(store, ctx_factory, clock):
    # accepted_at comes from the server-side clock inside the store; a later
    # check-in whose server clock goes *backwards* must still be "latest"
    # because ordering follows seq, not timestamps.
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                   valid_params_bytes(place="Hangzhou"))
    clock.advance(60_000)
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(2)),
                   valid_params_bytes(place="Shanghai"))
    clock.advance(-3600_000)  # clock jumps an hour backwards
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(3)),
                   valid_params_bytes(place="Tokyo"))
    snap = store.map_snapshot_page(None, None, 10)
    latest_a = next(fp for fp in snap.items if fp.ranger_id == RANGER_A)
    assert latest_a.place == "Tokyo"


def test_concurrent_same_cid_single_footprint(store, ctx_factory):
    results = []
    barrier = threading.Barrier(8)
    lock = threading.Lock()

    def worker():
        ctx = ctx_factory(RANGER_A, "Yun", ev(42))
        barrier.wait()
        r = apply_check_in(store, ctx, valid_params_bytes())
        with lock:
            results.append(r)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    footprints = {r.footprint.seq for r in results}
    assert len(footprints) == 1
    duplicates = [r.duplicate for r in results]
    assert duplicates.count(False) == 1
    assert store.map_snapshot_page(None, None, 10).footprint_count == 1


def test_concurrent_distinct_cids_all_land(store, ctx_factory):
    barrier = threading.Barrier(6)
    lock = threading.Lock()
    results = []

    def worker(n: int):
        ctx = ctx_factory(RANGER_A if n % 2 else RANGER_B, "Yun", ev(100 + n))
        barrier.wait()
        r = apply_check_in(store, ctx, valid_params_bytes(place=f"P{n}"))
        with lock:
            results.append(r)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 6
    seqs = sorted(r.footprint.seq for r in results)
    assert seqs == list(range(1, 7))
    snap = store.map_snapshot_page(None, None, 100)
    assert snap.footprint_count == 6
    assert snap.ranger_count == 2
