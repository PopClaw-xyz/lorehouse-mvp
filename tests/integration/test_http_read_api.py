"""Integration tests: read-only HTTP API over a seeded local store."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tests.conftest import valid_params_bytes  # noqa: E402

from ranger_map.app import create_app  # noqa: E402
from ranger_map.check_in import TrustedCheckInContext, apply_check_in  # noqa: E402
from ranger_map.store import Store  # noqa: E402

RANGER_A = "ArangerA1111111111111111111111111"
RANGER_B = "BrangerB2222222222222222222222222"
RANGER_C = "CrangerC3333333333333333333333333"


def ev(n: int) -> str:
    return f"{n:064x}"


def make_client(tmp_path, seed=True):
    """Client plus its store so tests can seed via the trusted path."""
    from starlette.testclient import TestClient

    from ranger_map.house import load_or_setup
    from ranger_map.keys import load_or_create_identity
    from ranger_map.streams import StreamHub

    store = Store.open(tmp_path / "data")
    identity = load_or_create_identity(tmp_path / "data")
    state = load_or_setup(store, identity, "http://127.0.0.1:8787")
    if seed:
        apply_check_in(store, TrustedCheckInContext(RANGER_A, "Yun", ev(1)),
                       valid_params_bytes(place="Hangzhou"))
        apply_check_in(
            store, TrustedCheckInContext(RANGER_B, "Otto", ev(2)),
            valid_params_bytes(place="Berlin", lat="52.52", lon="13.40",
                               status="Hello from Berlin."),
        )
        apply_check_in(
            store, TrustedCheckInContext(RANGER_A, "Yun", ev(3)),
            valid_params_bytes(place="Shanghai", lat="31.23", lon="121.47",
                               status="The first version is ready."),
        )
    app = create_app(store, identity=identity, house_state=state,
                     hub=StreamHub(store))
    return TestClient(app), store


def test_healthz_ok(tmp_path):
    client, _store = make_client(tmp_path, seed=False)
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert isinstance(body["schema_version"], int)


def test_map_empty_state_is_real_zero(tmp_path):
    client, _store = make_client(tmp_path, seed=False)
    response = client.get("/ranger-map/v1/map")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "as_of_seq": "0",
        "ranger_count": 0,
        "footprint_count": 0,
        "items": [],
        "next_cursor": None,
    }


def test_map_full_snapshot(tmp_path):
    client, _store = make_client(tmp_path)
    body = client.get("/ranger-map/v1/map").json()
    assert body["as_of_seq"] == "3"
    assert body["ranger_count"] == 2
    assert body["footprint_count"] == 3
    assert len(body["items"]) == 2
    a = next(item for item in body["items"] if item["ranger_id"] == RANGER_A)
    assert a["place"] == "Shanghai"
    assert a["seq"] == "3"
    assert a["latitude"] == "31.23"
    assert a["accepted_at"].endswith("Z")
    assert set(a) == {
        "seq", "source_event_id", "ranger_id", "nickname", "place",
        "latitude", "longitude", "status", "accepted_at",
    }


def test_map_pagination_cursor_roundtrip(tmp_path):
    client, _store = make_client(tmp_path)
    page1 = client.get("/ranger-map/v1/map?limit=1").json()
    assert [item["ranger_id"] for item in page1["items"]] == [RANGER_A]
    assert page1["next_cursor"]
    page2 = client.get(
        "/ranger-map/v1/map",
        params={"limit": 1, "cursor": page1["next_cursor"]},
    ).json()
    assert [item["ranger_id"] for item in page2["items"]] == [RANGER_B]
    assert page2["next_cursor"] is None
    # Same frozen snapshot on both pages.
    assert page2["as_of_seq"] == page1["as_of_seq"]


def test_map_cursor_rejects_garbage(tmp_path):
    client, _store = make_client(tmp_path)
    bad_cursors = [
        "not-a-cursor!",
        "<<<<",
        base64.urlsafe_b64encode(b"{}").rstrip(b"=").decode(),          # wrong keys
        base64.urlsafe_b64encode(b'{"v":2,"as_of_seq":1,"after_ranger_id":"a"}')
        .rstrip(b"=").decode(),                                        # wrong version
        base64.urlsafe_b64encode(
            json.dumps({"v": 1, "as_of_seq": 999, "after_ranger_id": RANGER_A})
            .encode()).rstrip(b"=").decode(),                          # future snapshot
        base64.urlsafe_b64encode(
            json.dumps({"v": 1, "as_of_seq": 1, "after_ranger_id": "0bad"})
            .encode()).rstrip(b"=").decode(),                          # bad identity
        "a" * 600,
    ]
    for cursor in bad_cursors:
        response = client.get("/ranger-map/v1/map", params={"cursor": cursor})
        assert response.status_code == 400, cursor
        assert response.json()["error"]["code"] == "invalid_input"


@pytest.mark.parametrize("limit", ["0", "201", "-1", "abc", "1.5"])
def test_map_limit_validation(tmp_path, limit):
    client, _store = make_client(tmp_path)
    response = client.get("/ranger-map/v1/map", params={"limit": limit})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_input"


def test_map_etag_and_304(tmp_path):
    client, store = make_client(tmp_path)
    first = client.get("/ranger-map/v1/map")
    etag = first.headers["ETag"]
    assert first.status_code == 200
    fresh = client.get("/ranger-map/v1/map", headers={"If-None-Match": etag})
    assert fresh.status_code == 304
    # A new accepted check-in changes the watermark and therefore the ETag.
    apply_check_in(
        store, TrustedCheckInContext(RANGER_C, "Luna", ev(4)),
        valid_params_bytes(place="Rio", lat="-22.91", lon="-43.17",
                           status="Beach day."),
    )
    changed = client.get("/ranger-map/v1/map", headers={"If-None-Match": etag})
    assert changed.status_code == 200
    assert changed.headers["ETag"] != etag


def test_history_defaults_filter_and_paging(tmp_path):
    client, _store = make_client(tmp_path)
    body = client.get("/ranger-map/v1/footprints").json()
    assert [item["seq"] for item in body["items"]] == ["3", "2", "1"]
    assert body["next_before"] is None

    a_only = client.get("/ranger-map/v1/footprints",
                        params={"ranger_id": RANGER_A}).json()
    assert [item["place"] for item in a_only["items"]] == ["Shanghai", "Hangzhou"]

    page = client.get("/ranger-map/v1/footprints", params={"limit": 2}).json()
    assert [item["seq"] for item in page["items"]] == ["3", "2"]
    assert page["next_before"] == "2"
    rest = client.get("/ranger-map/v1/footprints",
                      params={"limit": 2, "before": page["next_before"]}).json()
    assert [item["seq"] for item in rest["items"]] == ["1"]
    assert rest["next_before"] is None

    unknown = client.get("/ranger-map/v1/footprints",
                         params={"ranger_id": "Zzzzzz9999999999999999999999999"})
    assert unknown.json() == {"items": [], "next_before": None}


@pytest.mark.parametrize("before", ["0", "-3", "xyz", "1.5"])
def test_history_before_validation(tmp_path, before):
    client, _store = make_client(tmp_path)
    response = client.get("/ranger-map/v1/footprints", params={"before": before})
    assert response.status_code == 400


@pytest.mark.parametrize("ranger_id", ["0bad", "l", "I", "x" * 129, "has space"])
def test_history_ranger_id_validation(tmp_path, ranger_id):
    client, _store = make_client(tmp_path)
    response = client.get("/ranger-map/v1/footprints",
                          params={"ranger_id": ranger_id})
    assert response.status_code == 400


def test_by_event_returns_immutable_result(tmp_path):
    client, _store = make_client(tmp_path)
    found = client.get(f"/ranger-map/v1/footprints/by-event/{ev(1)}")
    assert found.status_code == 200
    assert found.json()["place"] == "Hangzhou"
    assert found.json()["seq"] == "1"


def test_by_event_unknown_and_malformed(tmp_path):
    client, _store = make_client(tmp_path)
    unknown = client.get("/ranger-map/v1/footprints/by-event/" + "ff" * 32)
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "not_found"
    malformed = client.get("/ranger-map/v1/footprints/by-event/not-hex")
    assert malformed.status_code == 400
    assert malformed.json()["error"]["code"] == "invalid_input"


def test_unknown_api_route_is_json_404(tmp_path):
    client, _store = make_client(tmp_path)
    response = client.get("/ranger-map/v1/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_write_method_on_read_api_rejected(tmp_path):
    client, _store = make_client(tmp_path)
    response = client.post("/ranger-map/v1/map", json={"any": "thing"})
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "unsupported_action"


def test_protocol_entrances_are_real_now(tmp_path):
    """The adapter is bound: the wire entrances answer natively.

    (Full signed traffic is covered by tests/interop; here we pin the
    honest error surface for unsigned/garbage requests.)
    """
    client, _store = make_client(tmp_path)
    for path, payload in [
        ("/v1/push", b"\x00\x01proto-bytes"),
        ("/v1/world-actions/status", b"{}"),
        ("/v1/house-session", b"{}"),
    ]:
        response = client.post(path, content=payload)
        assert response.status_code == 400, path
        assert response.json()["error"]["code"] in {
            "MALFORMED_WRAPPER", "invalid_input", "READ_REQUEST_INVALID",
        }, (path, response.json())


def test_body_limit_413(tmp_path):
    client, _store = make_client(tmp_path, seed=False)
    # Default cap (128 KiB) applies to non-push routes.
    huge = b"x" * (128 * 1024 + 1)
    response = client.post("/v1/house-session", content=huge)
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "invalid_input"
    # Push carries the envelope-sized cap (1.5 MiB since .01.4); beyond it
    # still 413.
    enormous = b"x" * (1536 * 1024 + 129)
    response = client.post("/v1/push", content=enormous)
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "invalid_input"


def test_errors_do_not_leak_paths(tmp_path):
    client, _store = make_client(tmp_path)
    responses = [
        client.get("/ranger-map/v1/map", params={"cursor": "!!!"}),
        client.get("/ranger-map/v1/footprints/by-event/zz"),
        client.get("/ranger-map/v1/nope"),
    ]
    for response in responses:
        text = response.text
        assert "/Users/" not in text
        assert "Traceback" not in text
        assert ".sqlite3" not in text
