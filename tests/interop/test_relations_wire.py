"""Interop: relation originals never reach a public reader, and the
`.01.4` envelope limit at this server's real ingress.

A follow or unfollow is a personal event (RELATIONS.md §8): it is owed to
the two participants and to no public lane, and `FollowType.PUBLIC`
describes the relation's nature rather than granting a public-stream
right. This House admits valid relations privately and skips any row an
earlier build already numbered into the durable log on all three public
exits: replay, live and the legacy lane.

LIMITS.md — `L_ENVELOPE_MAX_BYTES` is 1.5 MiB since `.01.4`, and the
wrapper, SSE-frame and page ceilings are distinct consequences of it.
"""

from __future__ import annotations

import asyncio
import base64
import json

import pytest

from ranger_map import ingress as ingress_mod
from ranger_map import streams as streams_mod
from ranger_map import wire
from ranger_map.evidence import store_envelope

from tests.interop.wire_helpers import (
    Actor,
    build_envelope,
    make_house_event,
    make_post,
    signed_envelope_bytes,
    wrap_signed,
)


def push(client, payload: bytes):
    return client.post("/v1/push", content=payload)


def _follow(actor: Actor, followee: Actor, *, revoke: bool = False,
            private: bool = False, order=None) -> bytes:
    def set_body(envelope):
        body = envelope.follow_revoked if revoke else envelope.follow_declared
        body.followee_popclaw_id = followee.popclaw_id
        if private:
            body.follow_type = 1
        if order is not None:
            body.order.SetInParent()          # present even when empty
            for key, value in order.items():
                if key == "resolves":
                    body.order.resolves.extend(value)
                else:
                    setattr(body.order, key, value)

    return signed_envelope_bytes(build_envelope(actor, set_body), actor)


def _nothing_stored(house, payload: bytes) -> None:
    cid = wire.envelope_cid(payload)
    assert house.store.query_one(
        "SELECT event_id FROM accepted_envelopes WHERE event_id = ?", (cid,)
    ) is None
    assert house.store.public_log_high_water(house.state.log_incarnation) == 0


@pytest.mark.parametrize("revoke", [False, True], ids=["declared", "revoked"])
def test_legacy_follow_is_private_and_legal_before_ordered_evidence(house, revoke):
    # Two layers, and they answer different questions. The raw-wire guard
    # still decodes and structurally validates these bytes — the generic
    # wire capability is retained — while the sealed public predicate no
    # longer lists tags 20/21 at all since `.01.6`.
    actor, followee = Actor("Mira"), Actor("Ezra")
    payload = _follow(actor, followee, revoke=revoke)
    assert wire.guard_envelope(payload) == (21 if revoke else 20)
    with pytest.raises(wire.WireError, match="NOT_PUBLIC"):
        wire.guard_public_structure(payload)
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 200
    assert house.store.public_log_high_water(house.state.log_incarnation) == 0
    assert house.store.query_one('SELECT COUNT(*) n FROM personal_log')['n'] == 2


@pytest.mark.parametrize("revoke", [False, True], ids=["declared", "revoked"])
def test_ordered_follow_is_admitted_without_publication(house, revoke):
    actor, followee = Actor("Mira"), Actor("Ezra")
    payload = _follow(actor, followee, revoke=revoke,
                      order={"seq": 1, "house_key": house.identity.house_key_id})
    # Structurally legal bytes that the raw-wire guard still accepts: the
    # refusal must come from admission, and it must name the ordered case
    # rather than falling through to a generic public-eligibility verdict.
    assert wire.guard_envelope(payload) == (21 if revoke else 20)
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 200
    assert house.store.public_log_high_water(house.state.log_incarnation) == 0
    assert house.store.query_one('SELECT applied_seq FROM relation_edges')[0] == 1


def test_present_but_empty_order_is_still_ordered_mode(house):
    actor, followee = Actor("Mira"), Actor("Ezra")
    payload = _follow(actor, followee, order={})
    envelope = wire.EventEnvelope.FromString(payload)
    assert envelope.follow_declared.HasField("order")
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "RELATION_ORDER_INVALID"
    _nothing_stored(house, payload)


def test_private_follow_never_admitted_through_push(house):
    actor, followee = Actor("Mira"), Actor("Ezra")
    payload = _follow(actor, followee, private=True)
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 400
    # Refused as a relation before the privacy predicate is ever consulted:
    # a PRIVATE follow was already inadmissible, and now so is every other.
    assert response.json()["error"]["code"] == "RELATION_PRIVATE_UNSUPPORTED"
    _nothing_stored(house, payload)


def test_manifest_declares_runtime_relations_and_named_read_capabilities(house):
    # RELATIONS.md §1: the capability-bearing bytes are the proof's body.
    manifest = house.state.manifest_json
    assert manifest['relations'] == {'ordered': 1}
    assert manifest['read_auth'] == {'schemes': ['popclaw-identity-read-v2']}
    served = house.client.get("/v1/manifest").json()
    assert served['relations'] == {'ordered': 1}


def test_envelope_limit_is_the_01_4_bound(house):
    assert wire.L_ENVELOPE_MAX_BYTES == 1_572_864
    actor = Actor("Otto")
    # 1 MiB of opaque business bytes: refused under .01.3, admitted now.
    big = make_house_event(actor, "workshop.bulk", b"\x00" * (1024 * 1024))
    assert 262_144 < len(big) <= wire.L_ENVELOPE_MAX_BYTES
    response = push(house.client, wrap_signed(big, actor))
    assert response.status_code == 200, response.json()

    over = make_house_event(actor, "workshop.bulk",
                            b"\x00" * wire.L_ENVELOPE_MAX_BYTES)
    assert len(over) > wire.L_ENVELOPE_MAX_BYTES
    response = push(house.client, wrap_signed(over, actor))
    assert response.status_code == 413


# --- the three public exits --------------------------------------------------
#
# A relation original can no longer arrive through ingress, so these tests
# seed one the way an earlier `.01.3` build would have: numbered into the
# durable public log, between two ordinary public events. Its original bytes
# and CID are left exactly as they are and the log keeps its consecutive
# numbering, so the index-completeness check stays meaningful; the exits are
# what withhold it. Each exit must also keep reading past it.


def _seed_relation_row(house, actor, followee, *, corrupt_index=False) -> str:
    """Number a relation original into the public log directly."""
    payload = _follow(actor, followee)
    cid = wire.envelope_cid(payload)
    kind = "post" if corrupt_index else "follow_declared"
    with house.store.write_tx():
        store_envelope(house.store, cid, payload, actor.popclaw_id, 20,
                       kind, 1, [], house.store.clock_ms())
        house.store.public_log_append(house.state.log_incarnation, cid,
                                      payload, kind, json.dumps([]))
    return cid


def _seed_post(house, actor, text) -> str:
    payload = make_post(actor, text)
    response = push(house.client, wrap_signed(payload, actor))
    assert response.status_code == 200, response.json()
    return wire.envelope_cid(payload)


def _drive(generator, max_events: int, between=None):
    """Consume an SSE generator into [(event_name, decoded_bytes)]."""
    events = []

    async def run():
        index = 0
        async for chunk in generator:
            for line in chunk.split("\n"):
                if line.startswith("event: "):
                    events.append([line[7:], None])
                elif line.startswith("data: "):
                    if events and events[-1][1] is None:
                        events[-1][1] = base64.b64decode(line[6:])
                    else:
                        events.append(["message", base64.b64decode(line[6:])])
            if between is not None:
                between(index, events)
            index += 1
            if len(events) >= max_events:
                break

    asyncio.run(run())
    return [(name, data) for name, data in events]


def _selection(house, **overrides):
    params = {"mode": "public-v1", "cursors": "", "public_after": "0",
              "incarnation": house.state.log_incarnation}
    params.update(overrides)
    return streams_mod.parse_public_request(
        params, house.state.registered_scopes, house.state.log_incarnation)


def _frames(events):
    return [wire.WorldStreamFrame.FromString(data)
            for name, data in events if name == "public_frame"]


def test_replay_exit_withholds_a_relation_and_keeps_reading(house):
    yun, mira, ezra = Actor("Yun"), Actor("Mira"), Actor("Ezra")
    first = _seed_post(house, yun, "before the relation")
    hidden = _seed_relation_row(house, mira, ezra)
    later = _seed_post(house, yun, "after the relation")
    assert house.store.public_log_high_water(house.state.log_incarnation) == 3

    events = _drive(
        streams_mod.stream_public_events(house.hub, _selection(house),
                                         house.state.registered_scopes),
        max_events=4)
    names = [name for name, _ in events]
    assert names[0] == "public_boundary"
    assert "public_gap" not in names

    delivered = _frames(events)
    assert [frame.seq for frame in delivered] == [1, 3]
    assert {wire.envelope_cid(frame.envelope) for frame in delivered} == {
        first, later}
    assert hidden not in {wire.envelope_cid(f.envelope) for f in delivered}

    # The checkpoint still certifies coverage THROUGH the skipped row, so a
    # client resuming from it is not sent back and the cursor never stalls.
    checkpoint = [data for name, data in events if name == "public_checkpoint"]
    assert checkpoint, names
    parsed = wire.PublicStreamCheckpoint.FromString(checkpoint[0])
    assert parsed.public_through_seq == 3


def test_live_exit_withholds_a_relation_and_keeps_reading(house):
    yun, mira, ezra = Actor("Yun"), Actor("Mira"), Actor("Ezra")
    _seed_post(house, yun, "replayed")
    injected = {}

    def after_checkpoint(index, events):
        names = [name for name, _ in events]
        if "public_checkpoint" in names and not injected:
            injected["relation"] = _seed_relation_row(house, mira, ezra)
            injected["post"] = _seed_post(house, yun, "live after relation")

    events = _drive(
        streams_mod.stream_public_events(house.hub, _selection(house),
                                         house.state.registered_scopes),
        max_events=5, between=after_checkpoint)
    assert injected, "the live phase was never reached"
    assert "public_gap" not in [name for name, _ in events]

    delivered = {wire.envelope_cid(frame.envelope) for frame in _frames(events)}
    assert injected["relation"] not in delivered
    assert injected["post"] in delivered


def test_legacy_exit_withholds_a_relation_and_keeps_reading(house):
    yun, mira, ezra = Actor("Yun"), Actor("Mira"), Actor("Ezra")
    first = _seed_post(house, yun, "legacy before")
    hidden = _seed_relation_row(house, mira, ezra)
    later = _seed_post(house, yun, "legacy after")

    events = _drive(streams_mod.stream_legacy_events(house.hub, 0),
                    max_events=2)
    frames = [wire.WorldStreamFrame.FromString(data) for _, data in events]
    assert [frame.seq for frame in frames] == [1, 3]
    cids = {wire.envelope_cid(frame.envelope) for frame in frames}
    assert cids == {first, later}
    assert hidden not in cids


def test_filtering_never_launders_a_corrupt_relation_row(house):
    # A relation row is withheld, but it is validated first: a row whose
    # durable index disagrees with its signed envelope still raises the
    # proper consistency gap instead of being quietly skipped.
    yun, mira, ezra = Actor("Yun"), Actor("Mira"), Actor("Ezra")
    _seed_post(house, yun, "before")
    _seed_relation_row(house, mira, ezra, corrupt_index=True)
    _seed_post(house, yun, "after")

    events = _drive(
        streams_mod.stream_public_events(house.hub, _selection(house),
                                         house.state.registered_scopes),
        max_events=4)
    names = [name for name, _ in events]
    assert "public_gap" in names, names
    gap = wire.PublicStreamGap.FromString(
        events[names.index("public_gap")][1])
    assert gap.reason == "publication_index_inconsistent"
    assert "public_checkpoint" not in names


# --- the four distinct ceilings ----------------------------------------------
#
# LIMITS.md bounds the raw envelope. The wrapper, the SSE frame and a page
# are consequences of it with their own sizes, and none of them licenses
# treating 1.5 MiB as the ceiling for any particular business content.


def _house_event_of_exact_size(actor: Actor, total: int) -> bytes:
    """A signed envelope whose wire length is exactly ``total`` bytes."""
    body = total - 512
    for _ in range(8):
        payload = make_house_event(actor, "workshop.bulk", b"\x00" * body)
        if len(payload) == total:
            return payload
        body += total - len(payload)
    raise AssertionError("could not land on the exact envelope size")


def test_envelope_ceiling_is_exact_at_the_boundary(house):
    actor = Actor("Otto")
    exact = _house_event_of_exact_size(actor, wire.L_ENVELOPE_MAX_BYTES)
    assert len(exact) == wire.L_ENVELOPE_MAX_BYTES
    assert push(house.client, wrap_signed(exact, actor)).status_code == 200

    over = _house_event_of_exact_size(actor, wire.L_ENVELOPE_MAX_BYTES + 1)
    assert len(over) == wire.L_ENVELOPE_MAX_BYTES + 1
    response = push(house.client, wrap_signed(over, actor))
    assert response.status_code == 413


def test_wrapper_ceiling_is_distinct_from_the_envelope_ceiling(house):
    # A maximal envelope does not fit in an envelope-sized wrapper: the
    # SignedPayload adds the signer key, the signature and their framing,
    # which is exactly why the two ceilings are separate numbers.
    actor = Actor("Otto")
    exact = _house_event_of_exact_size(actor, wire.L_ENVELOPE_MAX_BYTES)
    wrapper = wrap_signed(exact, actor)
    assert len(wrapper) > wire.L_ENVELOPE_MAX_BYTES
    assert len(wrapper) <= wire.L_SIGNED_PAYLOAD_MAX_BYTES
    assert wire.L_SIGNED_PAYLOAD_MAX_BYTES == ingress_mod.WRAPPER_MAX_BYTES


def test_a_maximal_event_really_reads_back_through_the_public_lane(house):
    # Not just admitted: a reader has to receive the whole thing, base64
    # framed, byte-identical to what was signed.
    actor = Actor("Otto")
    exact = _house_event_of_exact_size(actor, wire.L_ENVELOPE_MAX_BYTES)
    assert push(house.client, wrap_signed(exact, actor)).status_code == 200

    events = _drive(
        streams_mod.stream_public_events(house.hub, _selection(house),
                                         house.state.registered_scopes),
        max_events=3)
    delivered = _frames(events)
    assert len(delivered) == 1
    assert bytes(delivered[0].envelope) == exact

    # No tolerance: the real chunk this server emitted must fit the stated
    # ceiling exactly as stated.
    emitted = streams_mod._sse_event("public_frame",
                                     streams_mod._frame_bytes(
                                         {"seq": 1, "envelope_bytes": exact,
                                          "kind": "workshop.bulk",
                                          "scopes": "[]"}))
    assert len(emitted) <= wire.L_SSE_FRAME_MAX_BYTES


def test_the_sealed_predicate_and_this_house_both_exclude_relations(house):
    """Two layers now say no, and this server must not depend on either.

    Since `.01.6` the sealed public predicate omits tags 20/21 outright, so
    a relation original is no longer publicly eligible at the contract
    layer either. This server decides relation-ness from the structural
    decode instead, which is what keeps a stored relation original a
    withheld row rather than an "invalid public row" that would close every
    reader's connection — the exit tests above cover that against the real
    sealed guard, with no simulation.
    """
    mira, ezra = Actor("Mira"), Actor("Ezra")
    for revoke in (False, True):
        payload = _follow(mira, ezra, revoke=revoke)
        # The sealed predicate refuses it outright...
        with pytest.raises(wire.WireError, match="NOT_PUBLIC"):
            wire.guard_public_structure(payload)
        # ...while the generic wire capability is retained: the bytes still
        # decode and still carry a verifiable author signature.
        assert wire.guard_envelope(payload) == (21 if revoke else 20)
        envelope = wire.EventEnvelope.FromString(payload)
        assert wire.envelope_cid(payload) == envelope.event_id

    # Relation tags are excluded from this house's delivery policy
    # independently of what the sealed whitelist happens to list.
    assert wire.RELATION_TAGS == {20, 21}
    assert not wire.PUBLIC_ELIGIBLE_TAGS & wire.RELATION_TAGS


def test_the_frame_ceiling_covers_maximal_metadata_not_just_the_envelope(house):
    """The ceiling is for the whole frame, so build the worst frame there is.

    A delivered frame carries seq, the routing kind and the public scopes
    besides the envelope. Deriving the ceiling from the envelope alone
    understated it by the metadata — a 128-byte kind takes a two-byte
    length varint on its own — so the bound is checked against a frame that
    maxes out every component at once, with no tolerance.
    """
    frame = wire.WorldStreamFrame()
    frame.seq = 2 ** 64 - 1
    frame.envelope = b"\x00" * wire.L_ENVELOPE_MAX_BYTES
    frame.kind = "k" * wire.L_KIND_MAX_BYTES
    for index in range(wire.L_SCOPES_MAX):
        frame.scopes.append(
            ("s%02d" % index) + "x" * (wire.L_SCOPE_ID_MAX_BYTES - 3))
    raw = frame.SerializeToString(deterministic=True)
    assert len(raw) <= wire.L_STREAM_FRAME_MAX_BYTES

    chunk = streams_mod._sse_event("public_frame", raw)
    assert len(chunk) <= wire.L_SSE_FRAME_MAX_BYTES
    # And it really is bigger than the envelope-only arithmetic, which is
    # the miscalculation this pins.
    assert len(chunk) > ((wire.L_ENVELOPE_MAX_BYTES + 2) // 3) * 4 + 64


def test_a_legacy_stored_relation_is_still_refused_not_replayed_as_public(
        house):
    """The replay branch must not answer for a relation original.

    A data root written by an earlier build can still hold one in
    accepted_envelopes. The idempotent-replay lookup used to run first and
    would answer 200 with `public: true` for it — telling a client its
    relation sits on a public lane that now withholds it, and making "every
    relation original is refused" untrue in exactly the case that matters.
    """
    mira, ezra = Actor("Mira"), Actor("Ezra")
    payload = _follow(mira, ezra)
    cid = wire.envelope_cid(payload)
    with house.store.write_tx():
        store_envelope(house.store, cid, payload, mira.popclaw_id, 20,
                       "follow_declared", 1, [], house.store.clock_ms())
        house.store.public_log_append(house.state.log_incarnation, cid,
                                      payload, "follow_declared",
                                      json.dumps([]))
    assert house.store.query_one(
        "SELECT event_id FROM accepted_envelopes WHERE event_id = ?", (cid,))

    response = push(house.client, wrap_signed(payload, mira))
    assert response.status_code == 400, response.json()
    body = response.json()
    assert body["error"]["code"] == "RELATION_INDEX_INVALID"
    assert body.get("public") is not True
    assert body.get("duplicate") is not True
