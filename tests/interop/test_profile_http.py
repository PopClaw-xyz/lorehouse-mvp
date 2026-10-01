"""Public-client HTTP binding, distinct from the sealed signed wire."""

import json
import sqlite3
from pathlib import Path

import pytest

from ranger_map import wire
from ranger_map.errors import StorageUnavailable
from tests.interop.wire_helpers import (
    Actor, build_envelope, make_post, signed_envelope_bytes, wrap_signed,
)


def publish(house, actor, setter):
    raw = signed_envelope_bytes(build_envelope(actor, setter), actor)
    response = house.client.post('/v1/push', content=wrap_signed(raw, actor))
    assert response.status_code == 200, response.text
    return response.json()['event_id']


def profile(house, actor):
    return house.client.get(f'/v1/profile/{actor.popclaw_id}')


def clean_card(name='Mira', seconds=1790705946):
    return dict(nickname=name, one_line_intro='', taste_tags=[], role_persona='',
                location_hint='', avatar_uri='', declared_at=seconds)


def seed(house, actor, card):
    house.store.execute(
        'INSERT INTO profiles (ranger_id, card_json, updated_at_ms) VALUES (?, ?, 0)',
        (actor.popclaw_id, card if isinstance(card, str) else json.dumps(card)))


def test_absence_is_complete_wrapper(house):
    actor = Actor()
    body = profile(house, actor).json()
    assert body == dict(popclaw_id=actor.popclaw_id, sigil=body['sigil'],
                        profiles=[], house_follower_count=0, house_post_count=0,
                        house_reply_received_count=0)
    assert len(body['sigil']) == 8


def test_signed_first_card_readback_and_clean_rename(house):
    actor = Actor()
    for name, seconds in [('Mira', 1790705946), ('Nova', 1790705947)]:
        card = clean_card(name, seconds)
        def setter(e):
            e.profile.nickname = name
            e.profile.declared_at = seconds
        publish(house, actor, setter)
        expected = {k: v for k, v in card.items() if k != 'declared_at'}
        expected.update(declared_at_ms=seconds * 1000, payout_addresses=[])
        assert profile(house, actor).json()['card'] == expected


def test_all_nonempty_fields_are_preserved(house):
    actor = Actor()
    def setter(e):
        e.profile.nickname = 'Mira'
        e.profile.declared_at = 1790705946
        e.profile.one_line_intro = 'first card'
        e.profile.taste_tags.extend(['maps', 'tea'])
        e.profile.role_persona = 'Ranger'
        e.profile.location_hint = 'Hangzhou'
        e.profile.avatar_uri = 'https://example.invalid/avatar.png'
    publish(house, actor, setter)
    card = profile(house, actor).json()['card']
    assert card == dict(nickname='Mira', one_line_intro='first card',
                        taste_tags=['maps', 'tea'], role_persona='Ranger',
                        location_hint='Hangzhou',
                        avatar_uri='https://example.invalid/avatar.png',
                        declared_at_ms=1790705946000, payout_addresses=[])


@pytest.mark.parametrize('bad', [
    'null', '[]', '{', '{}',
    '{"nickname":"Mira","nickname":"Nova"}',
    {**clean_card(), 'one_line_intro': None},
    {**clean_card(), 'taste_tags': ['tea', 3]},
    {**clean_card(), 'declared_at': True},
    {**clean_card(), 'declared_at': 1.5},
    {**clean_card(), 'declared_at': 9007199254741},
    {**clean_card(), 'unknown_future_field': ''},
    {**clean_card(), 'payout_addresses': []},
    {k: v for k, v in clean_card().items() if k != 'avatar_uri'},
])
def test_bad_stored_card_never_becomes_safe_or_absent(house, bad):
    actor = Actor()
    seed(house, actor, bad)
    response = profile(house, actor)
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'storage_unavailable'


def test_legacy_row_with_no_card_is_not_absence(house):
    actor = Actor()
    house.store.execute(
        'INSERT INTO profiles (ranger_id, updated_at_ms) VALUES (?, 0)',
        (actor.popclaw_id,))
    assert profile(house, actor).status_code == 503


def test_storage_error_and_invalid_id_are_not_absence(house, monkeypatch):
    actor = Actor()
    assert house.client.get('/v1/profile/not-a-valid-key').status_code == 400
    def broken(*args):
        raise StorageUnavailable('injected read failure')
    monkeypatch.setattr(house.store, 'query_one', broken)
    assert profile(house, actor).status_code == 503


def test_sqlite_error_is_an_explicit_unreadable_response(house, monkeypatch):
    def broken(*args):
        raise sqlite3.OperationalError('injected sqlite failure')
    monkeypatch.setattr(house.store, 'query_one', broken)
    assert profile(house, Actor()).status_code == 503


def test_local_counts_nonzero_replay_and_author_boundary(house):
    author, replier, stranger = Actor(), Actor(), Actor()
    raw = make_post(author)
    response = house.client.post('/v1/push', content=wrap_signed(raw, author))
    assert response.status_code == 200
    root = response.json()['event_id']
    assert house.client.post('/v1/push', content=wrap_signed(raw, author)).status_code == 200
    def reply(e):
        e.reply.in_reply_to.platform = 'popclaw'
        e.reply.in_reply_to.platform_post_id = root
        e.reply.in_reply_to.author_popclaw_id = author.popclaw_id
        e.reply.body = 'reply'
    reply_id = publish(house, replier, reply)
    # Replay the exact accepted Reply; it still counts only once.
    raw_reply = house.store.query_one(
        'SELECT envelope_bytes FROM accepted_envelopes WHERE event_id = ?',
        (reply_id,))['envelope_bytes']
    assert house.client.post('/v1/push', content=wrap_signed(raw_reply, replier)).status_code == 200
    counts = profile(house, author).json()
    assert counts['house_post_count'] == 1
    assert counts['house_reply_received_count'] == 1
    assert profile(house, replier).json()['house_post_count'] == 0
    assert profile(house, stranger).json()['house_reply_received_count'] == 0


def test_corrupt_reply_count_source_is_not_reported_as_zero(house):
    house.store.execute(
        "INSERT INTO accepted_envelopes (event_id, envelope_bytes, actor_id, body_tag,"
        " kind, public_eligible, accepted_at_ms) VALUES (?, ?, ?, 25, 'reply', 1, 0)",
        ('a' * 64, b'\xff', Actor().popclaw_id))
    assert profile(house, Actor()).status_code == 503


def test_sigil_public_vector():
    from ranger_map.app import _profile_sigil
    assert _profile_sigil('BlackFeather') == 'gdx8rgtp'


def test_documented_http_fixtures_match_actual_projection(house):
    fixtures = json.loads(Path(__file__).with_name('profile_http_fixtures.json').read_text())
    actor = Actor()
    # The fixture uses a canonical synthetic 32-byte all-zero public key;
    # no signing claims are attached to these response-only examples.
    actor.popclaw_id = '1' * 32
    assert profile(house, actor).json() == fixtures['no_card']
    seed(house, actor, clean_card())
    assert profile(house, actor).json() == fixtures['clean_card']
