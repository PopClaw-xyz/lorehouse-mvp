"""Real route credentials, immutable pages, participant privacy and watermarks."""

import asyncio
import base64
import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ranger_map import identity_read, relations, streams, wire
from tests.interop.test_ordered_relations import push
from tests.interop.wire_helpers import Actor, make_post, wrap_signed


def credential(house, actor, purpose, ts=None, origin=None, key=None):
    ts = int(time.time()) if ts is None else ts
    message = f'{identity_read.SCHEME}:{purpose}:{actor.popclaw_id}:{key or house.identity.house_key_id}:{ts}:{origin or house.state.origin}'
    return f'v2.{actor.popclaw_id}.{ts}.{wire.b64(actor.sign(message.encode()))}'


def headers(house, actor, purpose):
    return {'x-popclaw-inbox-token': credential(house, actor, purpose)}


def test_snapshot_empty_and_auth_is_never_relaxed(house):
    a = Actor()
    route = '/v1/relation-snapshot'
    assert house.client.get(route).status_code == 401
    h = headers(house, a, 'relation-snapshot')
    r = house.client.get(route, headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body['entries'] == [] and body['complete'] is True
    assert (body['log_generation'], body['floor'], body['watermark']) == ('1', '1', '0')
    for token in (credential(house, a, 'relation-evidence'), credential(house, a, 'relation-snapshot', ts=int(time.time())-61),
                  credential(house, a, 'relation-snapshot', origin='https://elsewhere.invalid'),
                  credential(house, a, 'relation-snapshot', key=Actor().popclaw_id),
                  h['x-popclaw-inbox-token'][3:]):
        assert house.client.get(route, headers={'x-popclaw-inbox-token': token}).status_code == 401


def test_pagination_is_frozen_and_never_reinterprets_cursor(house):
    a, b, c = Actor(), Actor(), Actor()
    push(house, a, b, 1)
    push(house, a, c, 1, revoke=True)
    h = headers(house, a, 'relation-snapshot')
    first = house.client.get('/v1/relation-snapshot?limit=1', headers=h).json()
    assert first['complete'] is False and first['watermark'] == '2'
    push(house, a, b, 2, revoke=True)
    second = house.client.get('/v1/relation-snapshot', params={'cursor': first['next_cursor']}, headers=h).json()
    assert second['complete'] is True
    for k in ('checkpoint_id', 'watermark', 'floor', 'log_generation'):
        assert second[k] == first[k]
    assert sum(e['state'] == 'revoked' for e in first['entries']+second['entries']) == 1
    assert house.client.get('/v1/relation-snapshot?cursor=unreadable', headers=h).status_code == 400
    assert house.client.get('/v1/relation-snapshot', params={'cursor': first['next_cursor']},
                            headers=headers(house, b, 'relation-snapshot')).status_code == 400
    house.store.execute('UPDATE relation_checkpoints SET expires_at_ms=0')
    assert house.client.get('/v1/relation-snapshot', params={'cursor': first['next_cursor']}, headers=h).status_code == 410


def test_evidence_is_verbatim_participants_only_and_empty_404(house):
    a, b, outsider = Actor(), Actor(), Actor()
    _, cid, raw = push(house, a, b, 2**53+1)
    path = '/v1/relation-evidence/' + cid
    for actor in (a, b):
        r = house.client.get(path, headers=headers(house, actor, 'relation-evidence'))
        assert r.status_code == 200
        assert base64.b64decode(r.json()['envelope_b64']) == raw
        assert r.json()['hints']['seq'] == str(2**53+1)
    assert house.client.get(path, headers=headers(house, a, 'relation-snapshot')).status_code == 401
    raw_post = make_post(a)
    post_id = house.client.post('/v1/push', content=wrap_signed(raw_post, a)).json()['event_id']
    responses = [house.client.get('/v1/relation-evidence/'+event,
                 headers=headers(house, outsider, 'relation-evidence')) for event in (cid, '0'*64, post_id)]
    assert all(r.status_code == 404 and r.content == b'' for r in responses)


def test_snapshot_flushes_committed_obligations_before_watermark(house, monkeypatch):
    a, b = Actor(), Actor()
    monkeypatch.setattr(relations, 'publish', lambda _: None)
    push(house, a, b, 1)
    assert house.store.query_one('SELECT COUNT(*) n FROM personal_log')['n'] == 0
    r = house.client.get('/v1/relation-snapshot', headers=headers(house, a, 'relation-snapshot')).json()
    assert r['watermark'] == '1' and len(r['entries']) == 1
    assert house.store.query_one('SELECT COUNT(*) n FROM personal_log')['n'] == 2


def test_personal_cursor_reset_carries_no_position(house):
    a, b = Actor(), Actor()
    push(house, a, b, 1)
    for cursor, reason in [('bad', 'unreadable'), ('2.1', 'generation'), ('1.9', 'unreadable')]:
        text = streams._personal_reset(reason, 1, 1)
        assert 'id:' not in text and json.loads(text.split('data: ')[1])['reconcile'] == 'snapshot'
        assert streams.personal_cursor(cursor, 1, 1, 1)[1] == reason
    assert streams.personal_cursor('1.0', 1, 3, 5)[1] == 'below_floor'
    assert streams.personal_cursor('1.9007199254740993', 1, 1, 9007199254740993) == (9007199254740993, None)


@pytest.mark.parametrize('path', [Path(__file__).with_name('relation_read_v2_vectors.json'),
    Path(__file__).resolve().parents[2] / 'vendor/popclaw-contracts/packages/contracts/fixtures/relation-read-v2-vectors.json'])
def test_fixed_golden_vectors_recomputed_and_verified(path):
    v = json.loads(path.read_text())
    secret = Ed25519PrivateKey.from_private_bytes(v['seeds']['requester'].encode().ljust(32, b'\0'))
    actor = wire.popclaw_id_from_key(secret.public_key().public_bytes_raw())
    assert actor == v['requester_popclaw_id']
    for case in v['positive']:
        assert wire.b64(secret.sign(case['message'].encode())) == case['signature_b64']
        audience = SimpleNamespace(house_key_id=case['audience']['house_key'])
        assert identity_read.requester(case['token'], audience, case['audience']['origin'], case['purpose'],
                                      now=v['verify_now_utc_seconds']) == actor
    for case in v['negative']:
        audience = case.get('presented_to', {'house_key': v['house_a_key'], 'origin': 'https://house.example'})
        assert identity_read.requester(case['token'], SimpleNamespace(house_key_id=audience['house_key']),
                                      audience['origin'], 'relation-snapshot' if case['name']=='wrong-purpose' else 'relation-list',
                                      now=v['verify_now_utc_seconds']) is None


def test_real_list_routes_select_purpose_and_object_after_authentication(house):
    a, b, other = Actor(), Actor(), Actor()
    push(house, a, b, 1)
    for actor, path, peer in ((a, '/follows/'+a.popclaw_id, b), (b, '/followers/'+b.popclaw_id, a)):
        r = house.client.get(path, headers=headers(house, actor, 'relation-list'))
        assert r.json() == [{'popclaw_id': peer.popclaw_id}]
        assert house.client.get(path, headers=headers(house, other, 'relation-list')).status_code == 403
        assert house.client.get(path, headers=headers(house, actor, 'relation-snapshot')).status_code == 401
    assert house.client.get('/v1/profile/'+b.popclaw_id).json()['house_follower_count'] == 1
    push(house, a, b, 2, revoke=True)
    assert house.client.get('/v1/profile/'+b.popclaw_id).json()['house_follower_count'] == 0


def test_missing_read_audience_is_503_not_bad_user_credential(house):
    house.client.app.state.identity = None
    for path in ('/v1/relation-snapshot', '/v1/relation-evidence/'+'0'*64,
                 '/followers/'+Actor().popclaw_id, '/inbox/'+Actor().popclaw_id+'/stream'):
        r = house.client.get(path)
        assert r.status_code == 503
        assert r.json()['error']['code'] == 'read_authority_unavailable'


def test_checkpoint_budget_and_database_fault_never_claim_a_baseline(house, monkeypatch):
    from ranger_map import relation_reads
    a = Actor()
    monkeypatch.setattr(relation_reads, 'CHECKPOINT_BUDGET_SECONDS', -1)
    r = house.client.get('/v1/relation-snapshot', headers=headers(house, a, 'relation-snapshot'))
    assert r.status_code == 503 and r.headers['retry-after'] == '1'
    assert house.store.query_one('SELECT COUNT(*) n FROM relation_checkpoints')['n'] == 0
    monkeypatch.setattr(relation_reads, 'CHECKPOINT_BUDGET_SECONDS', 1)
    def broken(*args):
        from ranger_map.errors import StorageUnavailable
        raise StorageUnavailable('injected unavailable database')
    monkeypatch.setattr(house.store, 'query_all', broken)
    r = house.client.get('/v1/relation-snapshot', headers=headers(house, a, 'relation-snapshot'))
    assert r.status_code == 503 and r.headers['retry-after'] == '1'


def test_generation_change_expires_continuation_and_resets_live_cursor(house):
    from ranger_map.house import restore
    a, b, c = Actor(), Actor(), Actor()
    push(house, a, b, 1)
    push(house, a, c, 1)
    h = headers(house, a, 'relation-snapshot')
    page = house.client.get('/v1/relation-snapshot?limit=1', headers=h).json()
    house.client.app.state.house_state = restore(house.store, house.identity, house.state)
    r = house.client.get('/v1/relation-snapshot', params={'cursor': page['next_cursor']}, headers=h)
    assert r.status_code == 410
    token = credential(house, a, 'inbox-stream')
    async def reset():
        return [chunk async for chunk in streams.stream_inbox_events(
            house.store, house.identity, house.hub, house.state.origin, a.popclaw_id, token, False, '1.0')]
    chunks = asyncio.run(reset())
    assert len(chunks) == 1 and '"reason":"generation"' in chunks[0]
    assert 'id:' not in chunks[0]
