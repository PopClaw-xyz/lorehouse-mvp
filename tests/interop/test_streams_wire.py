"""Interop layer 5a: SSE endpoints through the in-process client.

Covers every stream outcome that CLOSES the connection quickly (negotiation
errors, gaps, unsafe-history closes). Never-ending live lanes are covered by
tests/interop/test_streams_live.py against a real server, because the
in-process transport delivers a streaming response only once it completes.
"""

from __future__ import annotations

import base64

from ranger_map import wire

from tests.interop.wire_helpers import Actor, make_post, wrap_signed


def push_post(house, actor, text="hello"):
    response = house.client.post(
        "/v1/push", content=wrap_signed(make_post(actor, text), actor))
    assert response.status_code == 200, response.text
    return response.json()


def stream_until_close(house, url, timeout=10.0):
    """Consume a short-lived SSE stream fully; returns [(event, data)]."""
    events = []

    def read():
        with house.client.stream("GET", url, timeout=timeout) as response:
            current = None
            for line in response.iter_lines():
                if line.startswith("event: "):
                    current = line[7:]
                elif line.startswith("data: "):
                    events.append((current or "message", line[6:]))

    read()
    return events


def test_unknown_scope_gaps_after_boundary(house):
    url = (f"/v1/world-stream?mode=public-v1"
           f"&incarnation={house.state.log_incarnation}"
           f"&cursors=unknownscope:0")
    events = stream_until_close(house, url)
    names = [name for name, _ in events]
    assert names[:2] == ["public_boundary", "public_gap"]
    gap = wire.PublicStreamGap.FromString(base64.b64decode(events[1][1]))
    assert gap.reason == "unknown_scope" and gap.scope_id == "unknownscope"
    assert "public_checkpoint" not in names


def test_incarnation_mismatch_gaps_and_closes(house):
    url = ("/v1/world-stream?mode=public-v1"
           f"&incarnation=rmlog-forged&cursors=&public_after=0")
    events = stream_until_close(house, url)
    assert events[0][0] == "public_gap"
    gap = wire.PublicStreamGap.FromString(base64.b64decode(events[0][1]))
    assert gap.reason == "log_incarnation_changed" and gap.lane == "connection"


def test_cursor_ahead_gaps(house):
    push_post(house, Actor("Yun"), "one")
    url = (f"/v1/world-stream?mode=public-v1"
           f"&incarnation={house.state.log_incarnation}"
           f"&cursors=&public_after=99")
    events = stream_until_close(house, url)
    gap = wire.PublicStreamGap.FromString(base64.b64decode(events[1][1]))
    assert gap.reason == "cursor_ahead" and gap.lane == "public"


def test_scope_cursor_ahead_gaps(house):
    push_post(house, Actor("Yun"), "one")
    url = (f"/v1/world-stream?mode=public-v1"
           f"&incarnation={house.state.log_incarnation}"
           f"&cursors=rangermap:42")
    events = stream_until_close(house, url)
    gap = wire.PublicStreamGap.FromString(base64.b64decode(events[1][1]))
    assert gap.reason == "cursor_ahead" and gap.lane == "scope"
    assert gap.scope_id == "rangermap"


def test_malformed_stream_requests_are_400(house):
    base = f"/v1/world-stream?incarnation={house.state.log_incarnation}"
    for url in [
        base + "&mode=public-v1",                     # cursors required
        base + "&mode=public-v1&cursors=&public_after=abc",
        base + "&mode=public-v1&cursors=x:0",  # label too short
        base + "&mode=public-v1&cursors=&public_after=0&limit=999",
        base + "&mode=public-v1&cursors=a:0,b:0&public_after=0",  # unsorted
        "/v1/world-stream?mode=public-v1&cursors=",   # incarnation required
    ]:
        response = house.client.get(url)
        assert response.status_code == 400, url


def _inject_unsafe_row(house):
    """Insert a reserved-wire row directly into the retained log."""
    house.store.public_log_append(
        house.state.log_incarnation, "ff" * 32,
        b"\x0a\x03abc" + b"\xea\x01\x00", "post", "[]")


def test_unsupported_historical_row_blocks_without_crossing(house):
    push_post(house, Actor("Yun"), "safe")
    _inject_unsafe_row(house)  # seq 2: reserved occurrence
    house.store.public_log_append(  # seq 3 must never be delivered past N
        house.state.log_incarnation, "ee" * 32,
        make_post(Actor("Zed"), "after the violation"), "post", "[]")

    url = (f"/v1/world-stream?mode=public-v1"
           f"&incarnation={house.state.log_incarnation}"
           f"&cursors=&public_after=0")
    events = stream_until_close(house, url)
    names = [name for name, _ in events]
    assert "public_gap" in names
    gap = wire.PublicStreamGap.FromString(
        base64.b64decode([d for n, d in events if n == "public_gap"][0]))
    assert gap.reason == "public_log_invalid"
    frames = [wire.WorldStreamFrame.FromString(base64.b64decode(d))
              for n, d in events if n == "public_frame"]
    # A failed page MAY withhold its earlier rows (BASELINE.md); what is
    # forbidden is delivering seq >= N or any checkpoint across it.
    assert all(f.seq < 2 for f in frames)
    assert "public_checkpoint" not in names
    assert names[-1] == "public_gap"  # closed on it: no N+1


def test_legacy_lane_closes_silently_at_unsafe_row(house):
    push_post(house, Actor("Yun"), "safe")
    _inject_unsafe_row(house)
    url = "/v1/world-stream"  # unqualified legacy grammar
    events = stream_until_close(house, url)
    # Old grammar: plain frames, no public_* controls, close at N. A failed
    # page may withhold its earlier safe rows (BASELINE allowance); what is
    # forbidden is delivering seq >= N or anything past it.
    assert all(name == "message" for name, _ in events)
    frames = [wire.WorldStreamFrame.FromString(base64.b64decode(d))
              for _, d in events]
    assert all(f.seq < 2 for f in frames)
