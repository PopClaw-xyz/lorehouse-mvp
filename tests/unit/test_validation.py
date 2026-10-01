"""Unit tests for strict raw check-in parameter validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ranger_map.check_in import (  # noqa: E402
    CheckInParams,
    TrustedCheckInContext,
    validate_check_in_params,
)
from ranger_map.errors import InvalidInput  # noqa: E402


def raw(obj) -> bytes:
    if isinstance(obj, bytes):
        return obj
    return json.dumps(obj).encode("utf-8")


VALID = {
    "place": "Hangzhou",
    "latitude": "30.27",
    "longitude": "120.15",
    "status": "Building a little music tool.",
}


# --- happy path -----------------------------------------------------------


def test_valid_params_round_trip():
    p = validate_check_in_params(raw(VALID))
    assert isinstance(p, CheckInParams)
    assert p.place == "Hangzhou"
    assert p.latitude == "30.27"
    assert p.longitude == "120.15"
    assert p.status == "Building a little music tool."


@pytest.mark.parametrize(
    ("raw_value", "normalized"),
    [
        ("30.2700", "30.27"),
        ("30.0", "30"),
        ("-0", "0"),
        ("-0.0", "0"),
        ("0.0000", "0"),
        ("0.0001", "0.0001"),
        ("90", "90"),
        ("-90", "-90"),
        ("90.0000", "90"),
        ("89.9999", "89.9999"),
    ],
)
def test_latitude_normalization(raw_value, normalized):
    body = dict(VALID, latitude=raw_value)
    assert validate_check_in_params(raw(body)).latitude == normalized


@pytest.mark.parametrize(
    ("raw_value", "normalized"),
    [
        ("120.1500", "120.15"),
        ("180", "180"),
        ("-180.0000", "-180"),
        ("0", "0"),
        ("-74.0060", "-74.006"),
    ],
)
def test_longitude_normalization(raw_value, normalized):
    body = dict(VALID, longitude=raw_value)
    assert validate_check_in_params(raw(body)).longitude == normalized


def test_place_and_status_are_trimmed():
    # Trimming applies to ordinary whitespace. Control characters such as
    # tabs are rejected outright (see rejection tests below).
    body = dict(VALID, place="  Hangzhou  ", status=" Hi there ")
    p = validate_check_in_params(raw(body))
    assert p.place == "Hangzhou"
    assert p.status == "Hi there"


def test_longest_valid_place_and_status():
    body = dict(VALID, place="字" * 60, status="a" * 160)
    p = validate_check_in_params(raw(body))
    assert len(p.place) == 60
    assert len(p.status) == 160


def test_multibyte_counts_code_points_not_bytes():
    # 60 code points of a 3-byte character is still valid.
    body = dict(VALID, place="あ" * 60)
    assert len(validate_check_in_params(raw(body)).place) == 60


# --- shape and JSON-level rejection --------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        b"[]",
        b'"string"',
        b"42",
        b"null",
        b"true",
        b"",
        b"not json at all",
        b"\xff\xfe{bad utf-8}",
        b'{"place":"Hangzhou"',
    ],
)
def test_non_object_or_malformed_rejected(payload):
    with pytest.raises(InvalidInput):
        validate_check_in_params(payload)


def test_missing_required_field_rejected():
    for field in VALID:
        body = {k: v for k, v in VALID.items() if k != field}
        with pytest.raises(InvalidInput):
            validate_check_in_params(raw(body))


def test_unknown_field_rejected():
    body = dict(VALID, actor_id="8someoneElse")
    with pytest.raises(InvalidInput):
        validate_check_in_params(raw(body))


def test_duplicate_json_key_rejected():
    text = (
        '{"place":"Hangzhou","place":"Berlin",'
        '"latitude":"30.27","longitude":"120.15","status":"x"}'
    )
    with pytest.raises(InvalidInput):
        validate_check_in_params(text.encode("utf-8"))


@pytest.mark.parametrize("literal", [b"NaN", b"Infinity", b"-Infinity"])
def test_non_finite_literals_rejected(literal):
    text = (
        b'{"place":"Hangzhou","latitude":' + literal
        + b',"longitude":"120.15","status":"x"}'
    )
    with pytest.raises(InvalidInput):
        validate_check_in_params(text)


def test_params_over_4kib_rejected():
    body = dict(VALID, status="a" * 5000)
    with pytest.raises(InvalidInput):
        validate_check_in_params(raw(body))


def test_nesting_depth_over_8_rejected():
    deep = "x"
    for _ in range(10):
        deep = {"n": deep}
    body = dict(VALID, place=deep)
    with pytest.raises(InvalidInput):
        validate_check_in_params(raw(body))


# --- field-level rejection ------------------------------------------------


@pytest.mark.parametrize(
    "place",
    [
        "",
        "   ",
        "a" * 61,
        "line\nbreak",
        "bell",
        "nul\x00",
        "del\x7f",
        123,
        True,
        None,
        ["Hangzhou"],
    ],
)
def test_invalid_place_rejected(place):
    body = dict(VALID, place=place)
    with pytest.raises(InvalidInput):
        validate_check_in_params(raw(body))


@pytest.mark.parametrize(
    "status",
    [
        "",
        "  ",
        "a" * 161,
        "two\nlines",
        "tab\tchar",
        7,
        False,
        None,
    ],
)
def test_invalid_status_rejected(status):
    body = dict(VALID, status=status)
    with pytest.raises(InvalidInput):
        validate_check_in_params(raw(body))


@pytest.mark.parametrize(
    "lat",
    [
        30.27,          # numbers are not accepted, only decimal strings
        True,
        None,
        "91",
        "-90.0001",
        "90.00001",
        "1e1",
        "+30.27",
        ".5",
        "30.",
        "030.27",
        "30.27000",
        "30,27",
        " 30.27",
        "nan",
        "inf",
        "-91",
        "900",
        "1000.0",
    ],
)
def test_invalid_latitude_rejected(lat):
    body = dict(VALID, latitude=lat)
    with pytest.raises(InvalidInput):
        validate_check_in_params(raw(body))


@pytest.mark.parametrize(
    "lon",
    [
        120.15,
        "181",
        "-180.0001",
        "180.00001",
        "200",
        "1000",
        "120.",
        ".15",
        "0120.15",
        "1e2",
        None,
        False,
    ],
)
def test_invalid_longitude_rejected(lon):
    body = dict(VALID, longitude=lon)
    with pytest.raises(InvalidInput):
        validate_check_in_params(raw(body))


# --- trusted context validation ------------------------------------------


def test_trusted_context_accepts_base58_and_hex():
    ctx = TrustedCheckInContext(
        ranger_id="1A2b9CdefGhijkmnPqrsTuvwxYz234567",
        nickname="Yun",
        source_event_id="ab" * 32,
    )
    assert ctx.ranger_id.startswith("1A2")


@pytest.mark.parametrize(
    "ranger_id",
    ["", "0", "I", "O", "l", "has space", "ümlaut", "x" * 129, 123, None],
)
def test_trusted_context_rejects_bad_ranger_id(ranger_id):
    with pytest.raises(InvalidInput):
        TrustedCheckInContext(
            ranger_id=ranger_id, nickname="Yun", source_event_id="ab" * 32
        )


@pytest.mark.parametrize(
    "event_id",
    [
        "",
        "ab",
        "AB" * 32,          # uppercase hex rejected
        "g" * 64,           # not hex
        "a" * 63,
        "a" * 65,
        "a" * 62 + "\n",
        123,
        None,
    ],
)
def test_trusted_context_rejects_bad_event_id(event_id):
    with pytest.raises(InvalidInput):
        TrustedCheckInContext(
            ranger_id="1A2b9CdefGhijklmNOpqrsTuvwxYz", nickname="Yun",
            source_event_id=event_id,
        )


def test_trusted_context_allows_missing_nickname():
    TrustedCheckInContext(
        ranger_id="1A2b9CdefGhijkmnPqrsTuvwxYz",
        nickname=None,
        source_event_id="ab" * 32,
    )


@pytest.mark.parametrize("nickname", ["", "a" * 61, "bad\nnick", "bad\x07nick", 5])
def test_trusted_context_rejects_bad_nickname(nickname):
    with pytest.raises(InvalidInput):
        TrustedCheckInContext(
            ranger_id="1A2b9CdefGhijkmnPqrsTuvwxYz",
            nickname=nickname,
            source_event_id="ab" * 32,
        )
