"""Unit tests for read models: consistent map snapshots and history paging."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tests.conftest import valid_params_bytes  # noqa: E402

from ranger_map.check_in import apply_check_in  # noqa: E402

RANGER_A = "ArangerA1111111111111111111111111"
RANGER_B = "BrangerB2222222222222222222222222"
RANGER_C = "CrangerC3333333333333333333333333"


def ev(n: int) -> str:
    return f"{n:064x}"


def check_in(store, ranger, nickname, n, place):
    return apply_check_in(store, _ctx(ranger, nickname, ev(n)),
                          valid_params_bytes(place=place))


def _ctx(ranger, nickname, event_hex):
    from ranger_map.check_in import TrustedCheckInContext

    return TrustedCheckInContext(ranger_id=ranger, nickname=nickname,
                                 source_event_id=event_hex)


def seed_three(store):
    """A checks in at Hangzhou, B at Berlin, A again in Shanghai."""
    check_in(store, RANGER_A, "Yun", 1, "Hangzhou")
    check_in(store, RANGER_B, "Otto", 2, "Berlin")
    check_in(store, RANGER_A, "Yun", 3, "Shanghai")


def test_map_snapshot_latest_per_ranger(store):
    seed_three(store)
    snap = store.map_snapshot_page(as_of_seq=None, after_ranger_id=None, limit=100)
    assert snap.as_of_seq == 3
    assert snap.ranger_count == 2
    assert snap.footprint_count == 3
    assert [fp.ranger_id for fp in snap.items] == [RANGER_A, RANGER_B]
    assert next(fp for fp in snap.items
                if fp.ranger_id == RANGER_A).place == "Shanghai"


def test_map_snapshot_honours_historical_watermark(store):
    seed_three(store)
    snap = store.map_snapshot_page(as_of_seq=2, after_ranger_id=None, limit=100)
    assert snap.as_of_seq == 2
    assert snap.footprint_count == 2
    a = next(fp for fp in snap.items if fp.ranger_id == RANGER_A)
    assert a.place == "Hangzhou"  # seq=3 not visible under M=2


def test_map_pagination_stable_order_and_counts(store):
    seed_three(store)
    page1 = store.map_snapshot_page(None, None, limit=1)
    assert [fp.ranger_id for fp in page1.items] == [RANGER_A]
    assert page1.has_more is True
    page2 = store.map_snapshot_page(page1.as_of_seq, RANGER_A, limit=1)
    assert [fp.ranger_id for fp in page2.items] == [RANGER_B]
    assert page2.has_more is False
    # Counts are consistent across pages of one snapshot.
    assert (page2.ranger_count, page2.footprint_count) == (
        page1.ranger_count, page1.footprint_count) == (2, 3)


def test_new_write_during_pagination_does_not_distort_snapshot(store):
    seed_three(store)
    page1 = store.map_snapshot_page(None, None, limit=1)
    # A fourth ranger checks in mid-pagination.
    check_in(store, RANGER_C, "Luna", 4, "Rio")
    # The cursor's snapshot stays frozen: no C, same watermark and counts.
    page2 = store.map_snapshot_page(page1.as_of_seq, RANGER_A, limit=10)
    assert page2.as_of_seq == 3
    assert page2.ranger_count == 2
    assert {fp.ranger_id for fp in page2.items} == {RANGER_B}
    # The next full refresh sees the new snapshot including everyone.
    fresh = store.map_snapshot_page(None, None, limit=10)
    assert fresh.as_of_seq == 4
    assert fresh.ranger_count == 3
    assert {fp.ranger_id for fp in fresh.items} == {RANGER_A, RANGER_B, RANGER_C}


def test_history_order_and_exclusive_before(store):
    seed_three(store)
    page = store.history_page(limit=2)
    assert [fp.seq for fp in page.items] == [3, 2]
    assert page.has_more is True
    next_page = store.history_page(before=page.items[-1].seq, limit=2)
    assert [fp.seq for fp in next_page.items] == [1]
    assert next_page.has_more is False


def test_history_ranger_filter_and_unknown_ranger(store):
    seed_three(store)
    page = store.history_page(ranger_id=RANGER_A, limit=10)
    assert [fp.place for fp in page.items] == ["Shanghai", "Hangzhou"]
    unknown = store.history_page(ranger_id="Zzzzzz9999999999999999999999999",
                                 limit=10)
    assert unknown.items == []
    assert unknown.has_more is False


def test_history_count_caps_at_limit(store, ctx_factory):
    for n in range(1, 6):
        check_in(store, RANGER_A, "Yun", n, f"P{n}")
    page = store.history_page(limit=3)
    assert len(page.items) == 3
    assert page.has_more is True


def test_by_event_returns_immutable_original(store):
    first = check_in(store, RANGER_A, "Yun", 1, "Hangzhou")
    check_in(store, RANGER_A, "Yun", 2, "Shanghai")
    found = store.footprint_by_event(first.footprint.source_event_id)
    assert found is not None
    assert found.place == "Hangzhou"
    assert found.seq == 1


def test_by_event_unknown_is_none(store):
    seed_three(store)
    assert store.footprint_by_event("ff" * 32) is None


def test_restart_preserves_all_facts(tmp_path, ctx_factory):
    from ranger_map.store import Store

    data_dir = tmp_path / "d"
    store = Store.open(data_dir)
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(1)),
                   valid_params_bytes(place="Hangzhou"))
    apply_check_in(
        store, ctx_factory(RANGER_B, "Otto", ev(2)),
        valid_params_bytes(place="Berlin", lat="52.52", lon="13.40",
                           status="Hello from Berlin."),
    )
    apply_check_in(store, ctx_factory(RANGER_A, "Yun", ev(3)),
                   valid_params_bytes(place="Shanghai", lat="31.23",
                                      lon="121.47", status="Ready."))
    raw_first = store.footprint_by_event(ev(1))
    store.close()

    reopened = Store.open(data_dir)
    try:
        snap = reopened.map_snapshot_page(None, None, 100)
        assert (snap.ranger_count, snap.footprint_count) == (2, 3)
        a = next(fp for fp in snap.items if fp.ranger_id == RANGER_A)
        assert a.place == "Shanghai"
        assert reopened.footprint_by_event(ev(1)) == raw_first
        # Idempotency survives restart: the same CID is still a duplicate.
        again = apply_check_in(reopened, ctx_factory(RANGER_A, "Yun", ev(1)),
                               valid_params_bytes(place="Hangzhou"))
        assert again.duplicate is True
        assert reopened.map_snapshot_page(None, None, 100).footprint_count == 3
    finally:
        reopened.close()
