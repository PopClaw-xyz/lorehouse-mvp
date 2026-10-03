"""Signed admission, transactional evidence and recovery under the sealed rules."""

from concurrent.futures import ThreadPoolExecutor
from itertools import permutations

import pytest

from ranger_map import ingress, relations, wire
from tests.interop.test_relations_wire import _follow
from tests.interop.wire_helpers import Actor, build_envelope, make_post, signed_envelope_bytes, wrap_signed


def push(house, actor, peer, seq, *, revoke=False, resolves=(), lorehouse=''):
    def body(e):
        e.lorehouse = lorehouse
        b = e.follow_revoked if revoke else e.follow_declared
        b.followee_popclaw_id = peer.popclaw_id
        b.order.seq = seq
        b.order.house_key = house.identity.house_key_id
        b.order.resolves.extend(resolves)
    raw = signed_envelope_bytes(build_envelope(actor, body), actor)
    r = house.client.post('/v1/push', content=wrap_signed(raw, actor))
    return r, wire.envelope_cid(raw), raw


def edge(house):
    return house.store.query_one('SELECT * FROM relation_edges')


def test_apply_stale_gap_revoke_replay_and_private_delivery(house):
    a, b = Actor(), Actor()
    r, one, raw = push(house, a, b, 2)
    assert r.status_code == 200
    assert r.json().get('public') is not True
    assert edge(house)['state'] == 'active'
    assert push(house, a, b, 1, revoke=True)[0].status_code == 200
    assert edge(house)['applied_seq'] == 2
    assert push(house, a, b, 8, revoke=True)[0].status_code == 200
    assert edge(house)['state'] == 'revoked'
    replay = house.client.post('/v1/push', content=wrap_signed(raw, a))
    assert replay.json()['duplicate'] is True
    rows = house.store.query_all('SELECT recipient,seq FROM personal_log ORDER BY recipient,seq')
    assert len(rows) == 6
    assert {row['recipient'] for row in rows} == {a.popclaw_id, b.popclaw_id}
    assert house.store.public_log_high_water(house.state.log_incarnation) == 0
    assert house.store.query_one('SELECT COUNT(*) n FROM accepted_envelopes')['n'] == 3


@pytest.mark.parametrize('seq', [0, 2**63, 2**64-1])
def test_seq_domain_refused_without_effect(house, seq):
    a, b = Actor(), Actor()
    assert push(house, a, b, seq)[0].status_code == 400
    assert edge(house) is None


def test_author_house_lorehouse_and_downgrade_guards(house):
    a, b = Actor(), Actor()
    assert push(house, a, b, 1, lorehouse=house.identity.house_key_id)[0].status_code == 200
    assert push(house, a, b, 2, lorehouse=house.state.origin)[0].status_code == 400
    raw = _follow(a, b, order={'seq': 2, 'house_key': Actor().popclaw_id})
    assert house.client.post('/v1/push', content=wrap_signed(raw, a)).status_code == 400
    raw = _follow(a, b)
    assert house.client.post('/v1/push', content=wrap_signed(raw, a)).json()['error']['code'] == 'RELATION_DOWNGRADE'
    assert house.client.post('/v1/push', content=wrap_signed(raw, b)).status_code == 400


def test_fork_larger_blocked_recovery_and_transitive_succession(house):
    a, b = Actor(), Actor()
    _, first, _ = push(house, a, b, 1)
    _, fork, _ = push(house, a, b, 1, revoke=True)
    assert edge(house)['conflicted'] == 1
    assert edge(house)['state'] == 'active'  # Last applied effect stands.
    push(house, a, b, 10, revoke=True)
    assert edge(house)['applied_seq'] == 1
    _, recovery, _ = push(house, a, b, 2, resolves=[first, fork])
    assert edge(house)['conflicted'] == 0
    assert edge(house)['applied_seq'] == 10
    _, next_recovery, _ = push(house, a, b, 11, resolves=[recovery])
    assert edge(house)['applied_event_id'] == next_recovery
    assert edge(house)['conflicted'] == 0


def test_invalid_recovery_cannot_fork_and_missing_reference_rejudged(house):
    a, b = Actor(), Actor()
    _, high, _ = push(house, a, b, 5)
    _, invalid, _ = push(house, a, b, 5, revoke=True, resolves=[high])
    assert edge(house)['conflicted'] == 0
    assert house.store.query_one('SELECT event_status FROM relation_originals WHERE event_id=?', (invalid,))[0] == 'invalid'
    late = _follow(a, b, order={'seq': 1, 'house_key': house.identity.house_key_id})
    late_id = wire.envelope_cid(late)
    _, waiting, _ = push(house, a, b, 9, resolves=[late_id])
    assert edge(house)['applied_seq'] == 5
    assert house.client.post('/v1/push', content=wrap_signed(late, a)).status_code == 200
    assert edge(house)['applied_event_id'] == waiting


@pytest.mark.parametrize('kind', ['foreign_edge', 'nonrelation'])
@pytest.mark.parametrize('arrives_first', [True, False])
def test_known_ineligible_reference_is_invalid_and_cannot_fork(house, kind, arrives_first):
    a, b, x, y = Actor(), Actor(), Actor(), Actor()
    push(house, a, b, 1)
    original = (_follow(x, y, order={'seq': 1, 'house_key': house.identity.house_key_id})
                if kind == 'foreign_edge' else make_post(x))
    foreign_cid = wire.envelope_cid(original)
    if arrives_first:
        assert house.client.post('/v1/push', content=wrap_signed(original, x)).status_code == 200
    _, ordinary, _ = push(house, a, b, 2)
    _, recovery, raw = push(house, a, b, 2, revoke=True, resolves=[foreign_cid])
    if not arrives_first:
        assert house.store.query_one('SELECT event_status FROM relation_originals WHERE event_id=?',
                                     (recovery,))[0] == 'awaiting_reference'
        assert edge(house)['conflicted'] == 1
        assert house.client.post('/v1/push', content=wrap_signed(original, x)).status_code == 200
    current = house.store.query_one('SELECT * FROM relation_edges WHERE follower=? AND followee=?',
                                    (a.popclaw_id, b.popclaw_id))
    assert (current['conflicted'], current['applied_seq'], current['applied_event_id']) == (0, 2, ordinary)
    replay = house.client.post('/v1/push', content=wrap_signed(raw, a))
    assert replay.json()['duplicate'] and replay.json()['relation_status'] == 'invalid'
    push(house, a, b, 3, revoke=True)
    current = house.store.query_one('SELECT * FROM relation_edges WHERE follower=? AND followee=?',
                                    (a.popclaw_id, b.popclaw_id))
    assert (current['conflicted'], current['applied_seq'], current['state']) == (0, 3, 'revoked')


def test_two_overlapping_recoveries_conflict_until_successor(house):
    a, b = Actor(), Actor()
    _, one, _ = push(house, a, b, 1)
    _, two, _ = push(house, a, b, 1, revoke=True)
    _, x, _ = push(house, a, b, 2, resolves=[one, two])
    _, y, _ = push(house, a, b, 3, resolves=[one, two], revoke=True)
    assert edge(house)['conflicted'] == 1
    _, z, _ = push(house, a, b, 4, resolves=[x, y])
    assert edge(house)['conflicted'] == 0
    assert edge(house)['applied_event_id'] == z


def test_late_reference_rejudgment_rolls_back_with_original_acceptance(house, monkeypatch):
    from ranger_map.errors import StorageUnavailable
    a, b, outsider = Actor(), Actor(), Actor()
    push(house, a, b, 1)
    original = make_post(outsider)
    cid = wire.envelope_cid(original)
    _, waiting, _ = push(house, a, b, 1, revoke=True, resolves=[cid])
    append = house.store.public_log_append
    def unavailable(*args):
        raise StorageUnavailable('injected public append failure after rejudgment')
    monkeypatch.setattr(house.store, 'public_log_append', unavailable)
    assert house.client.post('/v1/push', content=wrap_signed(original, outsider)).status_code == 503
    assert not house.store.query_one('SELECT event_id FROM accepted_envelopes WHERE event_id=?', (cid,))
    assert house.store.query_one('SELECT event_status FROM relation_originals WHERE event_id=?', (waiting,))[0] == 'awaiting_reference'
    assert edge(house)['conflicted'] == 1
    monkeypatch.setattr(house.store, 'public_log_append', append)
    assert house.client.post('/v1/push', content=wrap_signed(original, outsider)).status_code == 200
    assert house.store.query_one('SELECT event_status FROM relation_originals WHERE event_id=?', (waiting,))[0] == 'invalid'
    assert edge(house)['conflicted'] == 0


def test_concurrent_duplicate_commits_one_fact_two_obligations(house):
    a, b = Actor(), Actor()
    raw = _follow(a, b, order={'seq': 1, 'house_key': house.identity.house_key_id})
    wrapped = wrap_signed(raw, a)
    def send(_):
        return ingress.handle_push(house.store, house.identity, house.state, wrapped)
    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(send, range(8)))
    assert all(o.http_status == 200 for o in outcomes)
    assert sum(o.duplicate for o in outcomes) == 7
    assert house.store.query_one('SELECT COUNT(*) n FROM relation_originals')['n'] == 1
    assert house.store.query_one('SELECT COUNT(*) n FROM personal_outbox')['n'] == 2


@pytest.mark.parametrize('arrival', list(permutations(range(3))))
def test_recovery_reaches_same_head_in_all_arrival_orders(house, arrival):
    a, b = Actor(), Actor()
    key = house.identity.house_key_id
    first = _follow(a, b, order={'seq': 1, 'house_key': key})
    fork = _follow(a, b, revoke=True, order={'seq': 1, 'house_key': key})
    recovery = _follow(a, b, order={'seq': 2, 'house_key': key,
                                   'resolves': [wire.envelope_cid(first), wire.envelope_cid(fork)]})
    originals = [first, fork, recovery]
    for i in arrival:
        assert house.client.post('/v1/push', content=wrap_signed(originals[i], a)).status_code == 200
    assert edge(house)['applied_event_id'] == wire.envelope_cid(recovery)
    assert edge(house)['conflicted'] == 0


def test_late_original_reopens_a_previously_settled_edge(house):
    a, b = Actor(), Actor()
    _, one, _ = push(house, a, b, 1)
    _, two, _ = push(house, a, b, 1, revoke=True)
    _, recovery, _ = push(house, a, b, 2, resolves=[one, two])
    push(house, a, b, 10)
    _, late, _ = push(house, a, b, 2, revoke=True)
    assert edge(house)['conflicted'] == 1 and edge(house)['applied_seq'] == 10
    push(house, a, b, 11, resolves=[recovery, late])
    assert edge(house)['conflicted'] == 0 and edge(house)['applied_seq'] == 11


def test_evidence_and_both_obligations_rollback_together(house, monkeypatch):
    from ranger_map.errors import StorageUnavailable
    a, b = Actor(), Actor()
    enqueue = relations.enqueue
    calls = 0
    def fail_second(store, actor, cid):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise StorageUnavailable('injected second obligation failure')
        enqueue(store, actor, cid)
    monkeypatch.setattr(relations, 'enqueue', fail_second)
    assert push(house, a, b, 1)[0].status_code == 503
    for table in ('accepted_envelopes', 'relation_originals', 'relation_edges', 'personal_outbox'):
        assert house.store.query_one(f'SELECT COUNT(*) n FROM {table}')['n'] == 0


def test_post_commit_failure_replays_original_without_duplicate_delivery(house, monkeypatch):
    from ranger_map.errors import StorageUnavailable
    a, b = Actor(), Actor()
    publisher = relations.publish
    def unavailable(_):
        raise StorageUnavailable('injected publication outage after fact commit')
    monkeypatch.setattr(relations, 'publish', unavailable)
    r, cid, raw = push(house, a, b, 1)
    assert r.status_code == 503
    assert edge(house)['applied_seq'] == 1
    monkeypatch.setattr(relations, 'publish', publisher)
    r = house.client.post('/v1/push', content=wrap_signed(raw, a))
    assert r.status_code == 200 and r.json()['duplicate'] is True
    assert house.store.query_one('SELECT COUNT(*) n FROM personal_log')['n'] == 2
