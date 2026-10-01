"""SQLite storage: transactions, migrations and read models.

One process, one SQLite file (WAL). All database operations are synchronous
and guarded by a re-entrant lock so no ``await`` can ever straddle an open
write transaction; Starlette runs sync endpoints in its threadpool and every
call below is short-lived. Writes use ``BEGIN IMMEDIATE`` so concurrent
threads serialise on the single writer. ``synchronous=FULL`` keeps committed
state across power loss; ``foreign_keys=ON`` keeps projections honest.

A flock on ``<data-dir>/server.lock`` refuses a second server process on the
same data root instead of silently becoming an unverified multi-instance
service.
"""

from __future__ import annotations

import fcntl
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from .check_in import CheckInParams, Footprint
from .errors import StorageUnavailable

DB_FILENAME = "ranger_map.sqlite3"
LOCK_FILENAME = "server.lock"
BUSY_TIMEOUT_MS = 5000

MIGRATIONS: tuple[tuple[int, str], ...] = (
    (
        1,
        """
        CREATE TABLE profiles (
            ranger_id     TEXT PRIMARY KEY,
            display_name  TEXT,
            card_json     TEXT,
            updated_at_ms INTEGER NOT NULL
        );

        CREATE TABLE events (
            event_id       TEXT PRIMARY KEY,
            raw_bytes      BLOB NOT NULL,
            kind           TEXT NOT NULL,
            received_at_ms INTEGER NOT NULL
        );

        CREATE TABLE footprints (
            seq               INTEGER PRIMARY KEY AUTOINCREMENT,
            source_event_id   TEXT NOT NULL UNIQUE REFERENCES events (event_id),
            ranger_id         TEXT NOT NULL,
            nickname_snapshot TEXT NOT NULL,
            place             TEXT NOT NULL,
            latitude          TEXT NOT NULL,
            longitude         TEXT NOT NULL,
            status            TEXT NOT NULL,
            accepted_at_ms    INTEGER NOT NULL
        );

        CREATE INDEX idx_footprints_ranger_seq
            ON footprints (ranger_id, seq DESC);
        """,
    ),
    (
        2,
        """
        CREATE TABLE house_meta (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        -- Full signed-wire evidence of every accepted envelope (distinct from
        -- events.raw_bytes, which keeps the original business params bytes).
        CREATE TABLE accepted_envelopes (
            event_id        TEXT PRIMARY KEY,
            envelope_bytes  BLOB NOT NULL,
            actor_id        TEXT NOT NULL,
            body_tag        INTEGER NOT NULL,
            kind            TEXT NOT NULL,
            public_eligible INTEGER NOT NULL,
            scopes          TEXT NOT NULL DEFAULT '[]',
            accepted_at_ms  INTEGER NOT NULL
        );

        CREATE INDEX idx_accepted_actor
            ON accepted_envelopes (actor_id, accepted_at_ms);

        -- The public event log: one incarnation never reuses seqs or event ids.
        CREATE TABLE public_log (
            log_incarnation TEXT NOT NULL,
            seq             INTEGER NOT NULL,
            event_id        TEXT NOT NULL,
            envelope_bytes  BLOB NOT NULL,
            kind            TEXT NOT NULL,
            scopes          TEXT NOT NULL DEFAULT '[]',
            PRIMARY KEY (log_incarnation, seq)
        );

        CREATE UNIQUE INDEX idx_public_log_event
            ON public_log (log_incarnation, event_id);

        -- Private DM relay log (recipient-scoped, never public).
        CREATE TABLE dm_log (
            seq             INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id        TEXT NOT NULL UNIQUE,
            recipient_id    TEXT NOT NULL,
            envelope_bytes  BLOB NOT NULL,
            delivered_at_ms INTEGER NOT NULL
        );

        CREATE INDEX idx_dm_recipient ON dm_log (recipient_id, seq);

        -- G0 house sessions: request idempotency + authority rows.
        CREATE TABLE session_requests (
            request_id          TEXT PRIMARY KEY,
            actor_id            TEXT NOT NULL,
            installation_id     TEXT NOT NULL,
            core_canonical_hex  TEXT NOT NULL,
            ack_bytes           BLOB NOT NULL,
            created_ms          INTEGER NOT NULL
        );

        CREATE TABLE installations (
            actor_id                 TEXT NOT NULL,
            installation_id          TEXT NOT NULL,
            disabled_through_op_seq  INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (actor_id, installation_id)
        );

        CREATE TABLE sessions (
            session_id       TEXT PRIMARY KEY,
            actor_id         TEXT NOT NULL,
            installation_id  TEXT NOT NULL,
            entered_op_seq   INTEGER NOT NULL,
            house_revision   INTEGER NOT NULL,
            lease_expires_at INTEGER NOT NULL,
            active           INTEGER NOT NULL,
            created_ms       INTEGER NOT NULL,
            closed_ms        INTEGER
        );

        CREATE INDEX idx_sessions_actor
            ON sessions (actor_id, installation_id);

        CREATE TABLE inbox_tokens (
            token_id        TEXT PRIMARY KEY,
            actor_id        TEXT NOT NULL,
            session_id      TEXT NOT NULL,
            house_revision  INTEGER NOT NULL,
            expires_at      INTEGER NOT NULL,
            revoked         INTEGER NOT NULL DEFAULT 0
        );

        -- Terminal action results (immutable, replayable by request_id).
        CREATE TABLE action_results (
            request_id           TEXT PRIMARY KEY,
            actor_id             TEXT NOT NULL,
            request_digest       TEXT NOT NULL,
            status               TEXT NOT NULL,
            code                 TEXT NOT NULL,
            kind                 TEXT NOT NULL,
            signed_result_bytes  BLOB NOT NULL,
            created_ms           INTEGER NOT NULL
        );

        -- Single-use nonces for signed status reads.
        CREATE TABLE used_nonces (
            actor_id   TEXT NOT NULL,
            nonce      TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            PRIMARY KEY (actor_id, nonce)
        );

        ALTER TABLE profiles ADD COLUMN event_id TEXT;
        ALTER TABLE profiles ADD COLUMN one_line_intro TEXT;
        ALTER TABLE profiles ADD COLUMN declared_at INTEGER NOT NULL DEFAULT 0;
        """,
    ),
    (
        3,
        """
        -- Semantic idempotency for session requests: retries may refresh
        -- nonce/times while keeping the semantic operation (house_session.proto).
        ALTER TABLE session_requests ADD COLUMN semantic_core_hex TEXT;
        """,
    ),
)

CURRENT_SCHEMA_VERSION = MIGRATIONS[-1][0]


def current_schema_version() -> int:
    return CURRENT_SCHEMA_VERSION


@dataclass(frozen=True)
class MapSnapshotPage:
    as_of_seq: int
    ranger_count: int
    footprint_count: int
    items: list[Footprint]
    has_more: bool


@dataclass(frozen=True)
class HistoryPage:
    items: list[Footprint]
    has_more: bool
    next_before: int | None


def _default_clock_ms() -> int:
    return time.time_ns() // 1_000_000


class Store:
    """Owns the SQLite connection, the migrations and the read queries."""

    def __init__(self, connection: sqlite3.Connection, lock_fd, clock) -> None:
        self._connection = connection
        self._lock_fd = lock_fd
        self._clock = clock
        self._guard = threading.RLock()
        self._broken = False

    # -- lifecycle ---------------------------------------------------------

    @classmethod
    def open(cls, data_dir: Path | str, clock=None) -> "Store":
        data_dir = Path(data_dir)
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageUnavailable(
                "cannot create the data directory"
            ) from exc

        lock_path = data_dir / LOCK_FILENAME
        lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(lock_fd)
            raise StorageUnavailable(
                "another server process is already using this data directory"
            ) from None

        db_path = data_dir / DB_FILENAME
        connection = sqlite3.connect(
            db_path, check_same_thread=False, isolation_level=None, timeout=BUSY_TIMEOUT_MS / 1000
        )
        connection.row_factory = sqlite3.Row
        store = cls(connection, lock_fd, clock or _default_clock_ms)
        try:
            store._apply_pragmas()
            store._migrate()
        except BaseException:
            # Never leak the lock or an unusable connection on a failed open:
            # close both before re-raising so a retry in this process works.
            store.close()
            raise
        return store

    def close(self) -> None:
        with self._guard:
            try:
                self._connection.close()
            finally:
                if self._lock_fd is not None:
                    try:
                        fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                    finally:
                        os.close(self._lock_fd)
                        self._lock_fd = None

    def _apply_pragmas(self) -> None:
        with self._guard:
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.execute("PRAGMA synchronous=FULL")
            self._connection.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")

    def _migrate(self) -> None:
        with self._guard:
            with self.write_tx():
                self._connection.execute(
                    "CREATE TABLE IF NOT EXISTS schema_migrations ("
                    " version INTEGER PRIMARY KEY, applied_at_ms INTEGER NOT NULL)"
                )
                row = self._connection.execute(
                    "SELECT MAX(version) FROM schema_migrations"
                ).fetchone()
                current = row[0] or 0
                for version, script in MIGRATIONS:
                    if version <= current:
                        continue
                    # executescript() would COMMIT behind our back; run the
                    # statements individually so the migration stays in one
                    # transaction (the scripts contain no semicolons except
                    # statement separators).
                    for statement in script.split(";"):
                        if statement.strip():
                            self._connection.execute(statement)
                    self._connection.execute(
                        "INSERT INTO schema_migrations (version, applied_at_ms)"
                        " VALUES (?, ?)",
                        (version, self._clock()),
                    )

    def schema_version(self) -> int:
        with self._guard:
            row = self._connection.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()
            return row[0] or 0

    # -- transactions ------------------------------------------------------

    def _ensure_usable(self) -> None:
        if self._broken:
            raise StorageUnavailable(
                "the database connection was quarantined after a failed "
                "transaction and must be reopened"
            )

    @contextmanager
    def write_tx(self):
        """Serialised ``BEGIN IMMEDIATE`` transaction; rollback on error.

        COMMIT itself is inside the protected region: if it fails, the
        transaction is rolled back; if even the rollback fails, the
        connection is quarantined so no later read can observe uncommitted
        writes and no later BEGIN hits a leftover transaction.
        """
        with self._guard:
            self._ensure_usable()
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                yield
                self._connection.execute("COMMIT")
            except BaseException:
                try:
                    self._connection.execute("ROLLBACK")
                except Exception:
                    # Rollback failed: the connection's transaction state is
                    # unknowable. Quarantine it rather than risk exposing
                    # uncommitted writes through later reads.
                    self._broken = True
                raise

    @contextmanager
    def read_tx(self):
        """One consistent read snapshot (WAL readers never block writers)."""
        with self._guard:
            self._ensure_usable()
            self._connection.execute("BEGIN DEFERRED")
            try:
                yield
            finally:
                self._connection.execute("COMMIT")

    def clock_ms(self) -> int:
        return self._clock()

    # -- guarded generic access for protocol modules -----------------------
    # All access to the single connection goes through the guard; domain
    # modules compose their own SQL but never touch the connection directly.

    def query_all(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self._guard:
            self._ensure_usable()
            return self._connection.execute(sql, params).fetchall()

    def query_one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        with self._guard:
            self._ensure_usable()
            return self._connection.execute(sql, params).fetchone()

    def execute(self, sql: str, params: tuple = ()) -> None:
        """Run one statement; use inside write_tx for transactional work."""
        with self._guard:
            self._ensure_usable()
            self._connection.execute(sql, params)

    # -- house meta ---------------------------------------------------------

    def get_meta(self, key: str) -> str | None:
        row = self.query_one("SELECT value FROM house_meta WHERE key = ?", (key,))
        return None if row is None else row["value"]

    def set_meta(self, key: str, value: str) -> None:
        self.execute(
            "INSERT INTO house_meta (key, value) VALUES (?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    # -- public log ----------------------------------------------------------

    def public_log_append(self, log_incarnation: str, event_id: str,
                          envelope_bytes: bytes, kind: str, scopes_json: str) -> int:
        row = self.query_one(
            "SELECT COALESCE(MAX(seq), 0) AS m FROM public_log"
            " WHERE log_incarnation = ?",
            (log_incarnation,),
        )
        seq = int(row["m"]) + 1
        self.execute(
            "INSERT INTO public_log (log_incarnation, seq, event_id,"
            " envelope_bytes, kind, scopes) VALUES (?, ?, ?, ?, ?, ?)",
            (log_incarnation, seq, event_id, sqlite3.Binary(envelope_bytes),
             kind, scopes_json),
        )
        return seq

    def public_log_high_water(self, log_incarnation: str) -> int:
        row = self.query_one(
            "SELECT COALESCE(MAX(seq), 0) AS m FROM public_log"
            " WHERE log_incarnation = ?",
            (log_incarnation,),
        )
        return int(row["m"])

    def public_log_floor(self, log_incarnation: str) -> int:
        row = self.query_one(
            "SELECT COALESCE(MIN(seq), 0) AS m FROM public_log"
            " WHERE log_incarnation = ?",
            (log_incarnation,),
        )
        return int(row["m"])

    def public_log_page(self, log_incarnation: str, after_seq: int,
                        limit: int) -> list[sqlite3.Row]:
        return self.query_all(
            "SELECT seq, event_id, envelope_bytes, kind, scopes FROM public_log"
            " WHERE log_incarnation = ? AND seq > ? AND seq <= ?"
            " ORDER BY seq ASC LIMIT ?",
            # upper bound parameter comes from callers via high water; here we
            # pass a literal maximum and let callers cap rows themselves.
            (log_incarnation, after_seq, 2**63 - 1, limit),
        )

    # -- private DM relay -----------------------------------------------------

    def dm_append(self, event_id: str, recipient_id: str,
                  envelope_bytes: bytes) -> int:
        cursor = self._connection.execute(
            "INSERT INTO dm_log (event_id, recipient_id, envelope_bytes,"
            " delivered_at_ms) VALUES (?, ?, ?, ?)",
            (event_id, recipient_id, sqlite3.Binary(envelope_bytes), self._clock()),
        )
        return int(cursor.lastrowid)

    def dm_page(self, recipient_id: str, after_seq: int, limit: int):
        return self.query_all(
            "SELECT seq, event_id, envelope_bytes FROM dm_log"
            " WHERE recipient_id = ? AND seq > ? ORDER BY seq ASC LIMIT ?",
            (recipient_id, after_seq, limit),
        )

    # -- writes ------------------------------------------------------------

    def insert_event(self, event_id: str, raw_bytes: bytes, kind: str) -> None:
        self._connection.execute(
            "INSERT INTO events (event_id, raw_bytes, kind, received_at_ms)"
            " VALUES (?, ?, ?, ?)",
            (event_id, sqlite3.Binary(raw_bytes), kind, self._clock()),
        )

    def insert_footprint(self, source_event_id: str, ranger_id: str,
                         nickname_snapshot: str, params: CheckInParams) -> Footprint:
        accepted_at_ms = self._clock()
        cursor = self._connection.execute(
            "INSERT INTO footprints (source_event_id, ranger_id, nickname_snapshot,"
            " place, latitude, longitude, status, accepted_at_ms)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                source_event_id,
                ranger_id,
                nickname_snapshot,
                params.place,
                params.latitude,
                params.longitude,
                params.status,
                accepted_at_ms,
            ),
        )
        return self._footprint_from_row(self._row_by_seq(cursor.lastrowid))

    # -- reads -------------------------------------------------------------

    def _row_by_seq(self, seq: int) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT * FROM footprints WHERE seq = ?", (seq,)
        ).fetchone()
        if row is None:  # pragma: no cover - only right after INSERT
            raise StorageUnavailable("footprint row vanished inside its transaction")
        return row

    @staticmethod
    def _footprint_from_row(row: sqlite3.Row) -> Footprint:
        return Footprint(
            seq=row["seq"],
            source_event_id=row["source_event_id"],
            ranger_id=row["ranger_id"],
            nickname=row["nickname_snapshot"],
            place=row["place"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            status=row["status"],
            accepted_at_ms=row["accepted_at_ms"],
        )

    _FOOTPRINT_COLUMNS = (
        "seq, source_event_id, ranger_id, nickname_snapshot, place,"
        " latitude, longitude, status, accepted_at_ms"
    )
    _FOOTPRINT_COLUMNS_F = (
        "f.seq, f.source_event_id, f.ranger_id, f.nickname_snapshot, f.place,"
        " f.latitude, f.longitude, f.status, f.accepted_at_ms"
    )

    def footprint_by_event(self, event_id: str) -> Footprint | None:
        with self._guard:
            self._ensure_usable()
            row = self._connection.execute(
                f"SELECT {self._FOOTPRINT_COLUMNS} FROM footprints"
                " WHERE source_event_id = ?",
                (event_id,),
            ).fetchone()
        return None if row is None else self._footprint_from_row(row)

    def max_seq(self) -> int:
        with self._guard:
            self._ensure_usable()
            row = self._connection.execute(
                "SELECT COALESCE(MAX(seq), 0) FROM footprints"
            ).fetchone()
        return int(row[0])

    def map_snapshot_page(self, as_of_seq: int | None, after_ranger_id: str | None,
                          limit: int) -> MapSnapshotPage:
        """One consistent snapshot page of each ranger's latest footprint.

        With ``as_of_seq=None`` the watermark M = MAX(seq) is fixed first, in
        the same read transaction as the counts and the page rows. Cursor
        pages re-pass M so pagination stays on one frozen snapshot.
        Items are ordered by ``ranger_id`` (stable), continuing after
        ``after_ranger_id`` when given.
        """
        with self._guard:
            with self.read_tx():
                if as_of_seq is None:
                    as_of_seq = self.max_seq()
                count_row = self._connection.execute(
                    "SELECT COUNT(DISTINCT ranger_id), COUNT(*) FROM footprints"
                    " WHERE seq <= ?",
                    (as_of_seq,),
                ).fetchone()
                ranger_count, footprint_count = int(count_row[0]), int(count_row[1])
                sql = (
                    f"SELECT {self._FOOTPRINT_COLUMNS_F} FROM footprints f"
                    " JOIN (SELECT ranger_id, MAX(seq) AS mseq FROM footprints"
                    "       WHERE seq <= ? GROUP BY ranger_id) latest"
                    "   ON f.seq = latest.mseq"
                    " WHERE (? IS NULL OR f.ranger_id > ?)"
                    " ORDER BY f.ranger_id ASC"
                    " LIMIT ?"
                )
                rows = self._connection.execute(
                    sql, (as_of_seq, after_ranger_id, after_ranger_id, limit + 1)
                ).fetchall()
        has_more = len(rows) > limit
        items = [self._footprint_from_row(row) for row in rows[:limit]]
        return MapSnapshotPage(
            as_of_seq=as_of_seq,
            ranger_count=ranger_count,
            footprint_count=footprint_count,
            items=items,
            has_more=has_more,
        )

    def history_page(self, before: int | None = None, ranger_id: str | None = None,
                     limit: int = 20) -> HistoryPage:
        """Footprint history by seq descending; ``before`` is exclusive."""
        with self._guard:
            with self.read_tx():
                sql = (
                    f"SELECT {self._FOOTPRINT_COLUMNS} FROM footprints"
                    " WHERE (? IS NULL OR seq < ?)"
                    "   AND (? IS NULL OR ranger_id = ?)"
                    " ORDER BY seq DESC"
                    " LIMIT ?"
                )
                rows = self._connection.execute(
                    sql, (before, before, ranger_id, ranger_id, limit + 1)
                ).fetchall()
        has_more = len(rows) > limit
        items = [self._footprint_from_row(row) for row in rows[:limit]]
        next_before = items[-1].seq if has_more and items else None
        return HistoryPage(items=items, has_more=has_more, next_before=next_before)
