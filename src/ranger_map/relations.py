"""Ordered relation evidence and adjudication (sealed RELATIONS sections 3–5).

Facts, effects and delivery obligations commit together. Publication allocates
personal positions in a separate transaction, scanning obligations in commit
order. Neither a transport receipt nor a House hint replaces author evidence.
"""

from __future__ import annotations

import json

from . import wire
from .evidence import PushOutcome, store_envelope

MAX_SEQ = 2**63 - 1


def adjudicate(events, previous=None, known_ineligible=()):
    """Re-evaluate every recovery against the entire edge evidence set.

    A still-unresolved fork preserves the last applied effect. Recoveries never
    inherit from awaiting/invalid statements and cannot reach forward in time.
    """
    by_id = {e['event_id']: e for e in events}
    standing, coverage = {}, {}
    for e in sorted(events, key=lambda e: (e['seq'] or 0, e['event_id'])):
        cid, refs, seq = e['event_id'], e['resolves'], e['seq']
        if not refs:
            standing[cid] = 'ordinary'
            continue
        if (any(r in known_ineligible for r in refs)
                or any(r in by_id and (by_id[r]['seq'] or 0) >= seq for r in refs)):
            standing[cid] = 'invalid'
        elif any(r not in by_id for r in refs):
            standing[cid] = 'awaiting_reference'
        else:
            standing[cid] = 'valid'
            inherited = set(refs)
            for r in refs:
                if standing.get(r) == 'valid':
                    inherited.update(coverage[r])
            coverage[cid] = inherited

    groups = {}
    for e in events:
        if e['seq'] is not None and standing[e['event_id']] != 'invalid':
            groups.setdefault(e['seq'], []).append(e['event_id'])
    conflicts = {cid for siblings in groups.values() if len(siblings) > 1 for cid in siblings}
    recoveries = list(coverage)
    for i, a in enumerate(recoveries):
        for b in recoveries[i + 1:]:
            if (set(by_id[a]['resolves']) & set(by_id[b]['resolves'])
                    and a not in coverage[b] and b not in coverage[a]):
                conflicts.update((a, b))
    sufficient = [r for r in recoveries if conflicts - {r} <= coverage[r]]
    sufficient = [r for r in sufficient if not any(r in coverage[s] for s in sufficient if s != r)]
    winner = sufficient[0] if len(sufficient) == 1 else None
    conflicted = bool(conflicts) and winner is None
    head = previous['applied_event_id'] if previous else None
    head_seq = previous['applied_seq'] if previous else None
    applied_now = set()
    if not conflicted:
        choices = [e for e in events if standing[e['event_id']] == 'ordinary']
        if winner:
            choices = [e for e in choices if (e['seq'] or 0) > by_id[winner]['seq']]
            choices.append(by_id[winner])
        elif recoveries:
            # Valid succession can apply even when there was no fork.
            choices.extend(by_id[r] for r in sufficient)
        for selected in sorted(choices, key=lambda e: (e['seq'] or 0, e['timestamp'], e['event_id'])):
            if (head_seq is None or (selected['seq'] or 0) > head_seq
                    or (selected['seq'] is None and selected['event_id'] != head)):
                head, head_seq = selected['event_id'], selected['seq']
                applied_now.add(head)
    applied = by_id.get(head)
    state = applied['action'] if applied else 'undecided'
    return {'state': state, 'applied_seq': head_seq, 'applied_event_id': head,
            'conflicted': int(conflicted),
            'revoked_at': applied['timestamp'] if applied and state == 'revoked' else None,
            'standing': standing, 'conflicts': conflicts, 'applied_now': applied_now}


def _events(store, key, follower, followee):
    return [{**dict(row), 'resolves': json.loads(row['resolves'])} for row in store.query_all(
        'SELECT * FROM relation_originals WHERE house_key=? AND follower=? AND followee=?',
        (key, follower, followee))]


def _rejudge(store, key, follower, followee):
    """Caller owns the fact transaction, including newly arrived references."""
    events = _events(store, key, follower, followee)
    local_ids = {e['event_id'] for e in events}
    references = {r for e in events for r in e['resolves']}
    # Global verified originals distinguish impossible references from missing
    # same-edge evidence. A known CID cannot later become another original.
    known_ineligible = {r for r in references - local_ids if store.query_one(
        'SELECT event_id FROM accepted_envelopes WHERE event_id=?', (r,))}
    previous = store.query_one('SELECT * FROM relation_edges WHERE house_key=? AND follower=? AND followee=?',
                               (key, follower, followee))
    result = adjudicate(events, previous, known_ineligible)
    store.execute('INSERT INTO relation_edges VALUES (?,?,?,?,?,?,?,?) '
                  'ON CONFLICT(house_key,follower,followee) DO UPDATE SET '
                  'state=excluded.state, applied_seq=excluded.applied_seq, '
                  'applied_event_id=excluded.applied_event_id, conflicted=excluded.conflicted, '
                  'revoked_at=excluded.revoked_at',
                  (key, follower, followee, result['state'], result['applied_seq'],
                   result['applied_event_id'], result['conflicted'], result['revoked_at']))
    for e in events:
        if e['event_status'] not in ('pending', 'awaiting_reference'):
            continue  # A terminal verdict is not re-classified on replay.
        standing = result['standing'][e['event_id']]
        status = ('invalid' if standing == 'invalid' else
                  'awaiting_reference' if standing == 'awaiting_reference' else
                  'fork_branch' if e['event_id'] in result['conflicts'] else
                  'pending' if result['conflicted'] else
                  'applied' if e['event_id'] in result['applied_now'] else 'stale')
        store.execute('UPDATE relation_originals SET event_status=? WHERE event_id=?', (status, e['event_id']))


def rejudge_referencing(store, cid):
    """Reclassify waiting references when their verified original arrives.

    Run after a relation's edge index is written, or immediately after a
    nonrelation original is stored, within the same acceptance transaction.
    """
    edges = {(r['house_key'], r['follower'], r['followee']) for r in store.query_all(
        "SELECT house_key,follower,followee,resolves FROM relation_originals WHERE event_status='awaiting_reference'")
        if cid in json.loads(r['resolves'])}
    for key, follower, followee in sorted(edges):
        _rejudge(store, key, follower, followee)


def accept(store, identity, state, payload, envelope, cid, tag):
    body = envelope.follow_declared if tag == 20 else envelope.follow_revoked
    follower, followee, key = envelope.actor.popclaw_id, body.followee_popclaw_id, identity.house_key_id
    def refuse(code, message):
        return PushOutcome(http_status=400, code=code, message=message)
    try:
        wire.key_bytes_from_popclaw_id(followee)
    except ValueError:
        return refuse('INVALID_TARGET', 'followee must be a valid identity')
    if body.follow_type != 0:
        return refuse('RELATION_PRIVATE_UNSUPPORTED', 'private-typed relations are not admitted')
    ordered = body.HasField('order')
    if not ordered and envelope.lorehouse not in ('', state.origin):
        return refuse('RELATION_HOUSE_MISMATCH', 'legacy envelope targets another house')
    if ordered:
        if not 1 <= body.order.seq <= MAX_SEQ:
            return refuse('RELATION_ORDER_INVALID', 'seq must be in 1..2^63-1')
        if body.order.house_key != key:
            return refuse('RELATION_HOUSE_MISMATCH', 'order is not scoped to this house')
        if envelope.lorehouse and envelope.lorehouse != key:
            return refuse('RELATION_HOUSE_MISMATCH', 'lorehouse disagrees with order.house_key')
    with store.write_tx():
        existing = store.query_one('SELECT event_status FROM relation_originals WHERE event_id=?', (cid,))
        if existing:
            outcome = PushOutcome(http_status=200, code='OK', event_id=cid, duplicate=True,
                                  public=False, extra={'relation_status': existing['event_status']})
        else:
            events = _events(store, key, follower, followee)
            if not ordered and any(e['seq'] is not None for e in events):
                return refuse('RELATION_DOWNGRADE', 'edge already has ordered evidence')
            if store.query_one('SELECT event_id FROM accepted_envelopes WHERE event_id=?', (cid,)):
                return refuse('RELATION_INDEX_INVALID', 'original has no relation index')
            store_envelope(store, cid, payload, follower, tag, wire.BODY_TAGS[tag], 0, [], store.clock_ms())
            refs = list(body.order.resolves) if ordered else []
            timestamp = envelope.timestamp
            store.execute('INSERT INTO relation_originals VALUES (?,?,?,?,?,?,?,?,?)',
                          (cid, key, follower, followee, body.order.seq if ordered else None,
                           json.dumps(refs), 'active' if tag == 20 else 'revoked', 'pending', timestamp))
            _rejudge(store, key, follower, followee)
            rejudge_referencing(store, cid)
            for recipient in sorted({follower, followee}):
                enqueue(store, recipient, cid)
            status = store.query_one('SELECT event_status FROM relation_originals WHERE event_id=?', (cid,))['event_status']
            outcome = PushOutcome(http_status=200, code='OK', event_id=cid, public=False,
                                  extra={'relation_status': status})
    publish(store)
    return outcome


def enqueue(store, recipient, cid):
    store.execute('INSERT INTO personal_outbox(recipient,event_id) VALUES (?,?)', (recipient, cid))


def publish_pending(store):
    """Caller holds a write transaction; every obligation was already committed."""
    generation = int(store.get_meta('personal_generation'))
    for row in store.query_all('SELECT * FROM personal_outbox WHERE published=0 ORDER BY obligation'):
        recipient = row['recipient']
        counter = store.query_one('SELECT high_water FROM personal_counters WHERE recipient=?', (recipient,))
        seq = counter['high_water'] + 1 if counter else 1
        if seq > MAX_SEQ:
            raise OverflowError('personal delivery position exhausted')
        store.execute('INSERT INTO personal_log VALUES (?,?,?,?)', (generation, recipient, seq, row['event_id']))
        store.execute('INSERT INTO personal_counters(recipient,high_water) VALUES (?,?) '
                      'ON CONFLICT(recipient) DO UPDATE SET high_water=excluded.high_water', (recipient, seq))
        store.execute('UPDATE personal_outbox SET published=1 WHERE obligation=?', (row['obligation'],))


def publish(store):
    with store.write_tx():
        publish_pending(store)
