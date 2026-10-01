"""Unit tests for SQLite storage: opening, pragmas, raw bytes, instance lock."""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ranger_map.errors import StorageUnavailable  # noqa: E402
from ranger_map.store import Store, current_schema_version  # noqa: E402


def test_open_creates_data_dir_and_db(tmp_path):
    data_dir = tmp_path / "nested" / "data"
    store = Store.open(data_dir)
    try:
        assert (data_dir / "ranger_map.sqlite3").exists()
    finally:
        store.close()


def test_pragmas_active(store):
    journal = store._connection.execute("PRAGMA journal_mode").fetchone()[0]
    fk = store._connection.execute("PRAGMA foreign_keys").fetchone()[0]
    sync = store._connection.execute("PRAGMA synchronous").fetchone()[0]
    busy = store._connection.execute("PRAGMA busy_timeout").fetchone()[0]
    assert journal.lower() == "wal"
    assert fk == 1
    assert sync == 2  # FULL
    assert busy >= 5000


def test_migrations_idempotent_on_reopen(tmp_path):
    store = Store.open(tmp_path / "d")
    store.close()
    store2 = Store.open(tmp_path / "d")
    try:
        assert store2.schema_version() == current_schema_version()
    finally:
        store2.close()


def test_second_process_lock_rejected(tmp_path):
    first = Store.open(tmp_path / "d")
    try:
        with pytest.raises(StorageUnavailable) as exc:
            Store.open(tmp_path / "d")
        assert "another" in str(exc.value).lower() or "already" in str(exc.value).lower()
    finally:
        first.close()
    # Lock is released on close: reopening must work.
    second = Store.open(tmp_path / "d")
    second.close()


def test_write_tx_rolls_back_on_error(store):
    from ranger_map.errors import StorageUnavailable

    with pytest.raises(RuntimeError):
        with store.write_tx():
            store._connection.execute(
                "INSERT INTO events (event_id, raw_bytes, kind, received_at_ms)"
                " VALUES ('aa', x'00', 'test', 1)"
            )
            raise RuntimeError("injected failure")
    row = store._connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert row == 0


def test_concurrent_writes_serialize(store):
    # The store guards a single connection with a lock; hammer it from
    # several threads and confirm every unit of work commits exactly once.
    errors: list[Exception] = []

    def worker(n: int) -> None:
        try:
            with store.write_tx():
                store._connection.execute(
                    "INSERT INTO events (event_id, raw_bytes, kind, received_at_ms)"
                    " VALUES (?, x'00', 'test', ?)",
                    (f"{n:064x}", n),
                )
        except Exception as exc:  # pragma: no cover - surfaced via assertion
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    count = store._connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert count == 8
