"""Regression tests for the five reviewer corrections on fb71c48."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ranger_map.app import RequestBodyLimit  # noqa: E402
from ranger_map.check_in import TrustedCheckInContext, validate_check_in_params  # noqa: E402
from ranger_map.errors import InvalidInput, StorageUnavailable  # noqa: E402
from ranger_map.store import Store  # noqa: E402


# --- 1. replay_receive replays once, then forwards the live receive --------


def test_body_limit_replays_once_then_forwards_disconnect():
    seen_requests = []
    seen_after_replay = []

    async def downstream(scope, receive, send):
        first = await receive()
        seen_requests.append(first)
        second = await receive()  # must be the forwarded disconnect
        seen_after_replay.append(second)
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    feed = [
        {"type": "http.request", "body": b"hello ", "more_body": True},
        {"type": "http.request", "body": b"world", "more_body": False},
        {"type": "http.disconnect"},
    ]
    cursor = {"i": 0}

    async def scripted_receive():
        message = feed[cursor["i"]]
        cursor["i"] += 1
        return message

    sent = []
    scope = {
        "type": "http", "method": "POST", "path": "/",
        "headers": [(b"content-length", b"11")], "query_string": b"",
    }

    async def send(message):
        sent.append(message)

    middleware = RequestBodyLimit(downstream, max_bytes=64)
    asyncio.run(middleware(scope, scripted_receive, send))

    assert seen_requests == [
        {"type": "http.request", "body": b"hello world", "more_body": False}
    ]
    # The disconnect was forwarded, never swallowed or spun on.
    assert seen_after_replay == [{"type": "http.disconnect"}]
    assert cursor["i"] == 3  # no extra receive calls beyond the feed
    assert sent[0]["status"] == 200


def test_body_limit_forwards_messages_after_replay():
    """Post-replay request messages (e.g. a second read) reach the app."""
    received = []

    async def downstream(scope, receive, send):
        received.append(await receive())  # replayed body
        received.append(await receive())  # forwarded live message
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    feed = [
        {"type": "http.request", "body": b"x", "more_body": False},
        {"type": "http.request", "body": b"", "more_body": False},
    ]
    cursor = {"i": 0}

    async def scripted_receive():
        message = feed[cursor["i"]]
        cursor["i"] += 1
        return message

    middleware = RequestBodyLimit(downstream, max_bytes=16)

    async def send(message):
        pass

    asyncio.run(middleware({"type": "http", "method": "POST", "path": "/",
                            "headers": [], "query_string": b""},
                           scripted_receive, send))
    assert received[0]["body"] == b"x"
    assert received[1] == feed[1]
    assert cursor["i"] == 2


# --- 2. bounded-depth parse of hostile nesting ----------------------------


def test_deep_nesting_inside_4kib_is_rejected_deterministically():
    hostile = (b"{\"place\":" + b"[" * 2000 + b"]" * 2000 +
               b",\"latitude\":\"1\",\"longitude\":\"1\",\"status\":\"x\"}")
    assert len(hostile) < 4096
    with pytest.raises(InvalidInput):
        validate_check_in_params(hostile)


def test_deep_dict_nesting_is_rejected_deterministically():
    hostile = b'{"place":' + b'{"a":' * 1500 + b"1" + b"}" * 1500 + b"}"
    with pytest.raises(InvalidInput):
        validate_check_in_params(hostile)


def test_depth_just_under_limit_via_valid_shape_still_rejected():
    # Depth 9 through a wrong-typed field: still a defined rejection.
    body = b'{"place":{"a":{"b":{"c":{"d":{"e":{"f":{"g":1}}}}}}}}'
    with pytest.raises(InvalidInput):
        validate_check_in_params(body)


# --- 3. surrogate code points rejected before storage ----------------------


@pytest.mark.parametrize("raw_place", [
    b'{"place":"\\ud800Hangzhou","latitude":"1","longitude":"1","status":"x"}',
    b'{"place":"Bad\\udffftail","latitude":"1","longitude":"1","status":"x"}',
])
def test_escaped_surrogate_in_place_rejected(raw_place):
    with pytest.raises(InvalidInput, match="surrogate"):
        validate_check_in_params(raw_place)


def test_escaped_surrogate_in_status_rejected():
    raw = (b'{"place":"Hangzhou","latitude":"1","longitude":"1",'
           b'"status":"hi\\udcffthere"}')
    with pytest.raises(InvalidInput, match="surrogate"):
        validate_check_in_params(raw)


def test_surrogate_in_nickname_rejected():
    with pytest.raises(InvalidInput):
        TrustedCheckInContext(
            ranger_id="1A2b9CdefGhijkmnPqrsTuvwxYz",
            nickname="bad" + chr(0xD83D),
            source_event_id="ab" * 32,
        )


def test_normal_multibyte_place_still_accepted():
    raw = ('{"place":"杭州","latitude":"30.27","longitude":"120.15",'
           '"status":"你好"}').encode("utf-8")
    params = validate_check_in_params(raw)
    assert params.place == "杭州"


# --- 4. COMMIT failure recovery -------------------------------------------


class _FlakyConnection:
    """Proxy over a real connection whose COMMIT/ROLLBACK can be made to fail.

    sqlite3.Connection forbids instance-attribute monkeypatching, so tests
    swap the store's connection handle for this proxy instead.
    """

    def __init__(self, connection, fail_statements=()):
        self._connection = connection
        self._fail = tuple(s.upper() for s in fail_statements)

    def execute(self, sql, *args):
        if sql.strip().upper().startswith(self._fail):
            raise RuntimeError(f"injected failure: {sql.strip()}")
        return self._connection.execute(sql, *args)

    def __getattr__(self, name):
        return getattr(self._connection, name)


def test_commit_failure_rolls_back_and_recovers(tmp_path):
    store = Store.open(tmp_path / "d")
    real = store._connection
    store._connection = _FlakyConnection(real, fail_statements=("COMMIT",))

    with pytest.raises(RuntimeError):
        with store.write_tx():
            real.execute(
                "INSERT INTO events (event_id, raw_bytes, kind, received_at_ms)"
                " VALUES ('aa', x'00', 'test', 1)"
            )
    store._connection = real

    # The transaction was rolled back: nothing is visible.
    assert real.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0
    # The store recovered: a fresh transaction commits cleanly.
    with store.write_tx():
        store.insert_event("bb" * 32, b"x", "test")
    assert real.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1
    store.close()


def test_commit_and_rollback_failure_quarantines_connection(tmp_path):
    store = Store.open(tmp_path / "d")
    real = store._connection
    store._connection = _FlakyConnection(real, fail_statements=("COMMIT", "ROLLBACK"))

    with pytest.raises(RuntimeError):
        with store.write_tx():
            real.execute(
                "INSERT INTO events (event_id, raw_bytes, kind, received_at_ms)"
                " VALUES ('cc', x'00', 'test', 1)"
            )
    store._connection = real

    # Quarantined: reads refuse rather than expose uncommitted state.
    assert store._broken is True
    with pytest.raises(StorageUnavailable):
        store.max_seq()
    with pytest.raises(StorageUnavailable):
        with store.write_tx():
            pass
    store.close()

    # A fresh store on the same data root sees only committed data.
    fresh = Store.open(tmp_path / "d")
    assert fresh._connection.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0
    fresh.close()


# --- 5. Store.open cleans up lock/connection on failure --------------------


def test_store_open_failure_releases_lock(tmp_path, monkeypatch):
    def broken_migrate(self):
        raise RuntimeError("injected migration failure")

    monkeypatch.setattr(Store, "_migrate", broken_migrate)
    with pytest.raises(RuntimeError):
        Store.open(tmp_path / "d")

    # The failed open released its flock: a retry in the same process works.
    monkeypatch.undo()
    recovered = Store.open(tmp_path / "d")
    recovered.insert_event("dd" * 32, b"x", "test")
    with recovered.write_tx():
        pass
    recovered.close()
