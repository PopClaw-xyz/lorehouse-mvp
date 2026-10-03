"""The current public client's person query reads real Profile evidence only."""

import sqlite3

from tests.interop.test_profile_http import publish, seed, clean_card
from tests.interop.wire_helpers import Actor
from ranger_map.app import _profile_sigil


def test_absent_person_is_successfully_empty_not_offline(house):
    actor = Actor()
    r = house.client.get('/v1/resolve', params={'sigil': _profile_sigil(actor.popclaw_id)})
    assert r.status_code == 200
    assert r.json() == {'candidates': []}


def test_signed_profile_resolves_by_sigil_and_name_without_private_fields(house):
    actor = Actor()
    def card(e):
        e.profile.nickname = 'Mira Scout'
        e.profile.one_line_intro = 'not a resolve field'
        e.profile.declared_at = 1790705946
    publish(house, actor, card)
    expected = {'popclaw_id': actor.popclaw_id, 'nickname': 'Mira Scout',
                'sigil': _profile_sigil(actor.popclaw_id), 'profiles': []}
    for query in ({'sigil': expected['sigil'][:6].upper()}, {'name': 'SCOUT'}):
        r = house.client.get('/v1/resolve', params=query)
        assert r.status_code == 200
        assert r.json() == {'candidates': [expected]}
    assert house.client.get('/v1/resolve', params={'sigil': 'zzzzzzzz'}).json() == {'candidates': []}


def test_ambiguity_is_preserved_and_name_never_creates_verified_accounts(house):
    a, b = Actor(), Actor()
    seed(house, a, clean_card('Scout'))
    seed(house, b, clean_card('scout'))
    r = house.client.get('/v1/resolve', params={'name': 'scout'})
    assert {c['popclaw_id'] for c in r.json()['candidates']} == {a.popclaw_id, b.popclaw_id}
    assert all(c['profiles'] == [] for c in r.json()['candidates'])


def test_bad_query_and_broken_projection_are_not_empty_success(house, monkeypatch):
    for q in ({}, {'sigil': 'short'}, {'sigil': 'u12345'}):
        assert house.client.get('/v1/resolve', params=q).status_code == 400
    seed(house, Actor(), '{}')
    assert house.client.get('/v1/resolve', params={'name': 'Mira'}).status_code == 503
    def broken(*args):
        raise sqlite3.OperationalError('injected')
    monkeypatch.setattr(house.store, 'query_all', broken)
    assert house.client.get('/v1/resolve', params={'name': 'Mira'}).status_code == 503
