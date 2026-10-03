"""Frozen, participant-only reconciliation over verbatim verified originals."""

import json
import secrets
import sqlite3
import time

from starlette.responses import JSONResponse, Response

from . import identity_read, relations, wire
from .errors import StorageUnavailable

CHECKPOINT_TTL_MS = 300_000
CHECKPOINT_BUDGET_SECONDS = 1.0


def _authority(request, purpose):
    identity = getattr(request.app.state, 'identity', None)
    state = getattr(request.app.state, 'house_state', None)
    if identity is None or state is None or not state.origin:
        return None, None, JSONResponse({'error': {'code': 'read_authority_unavailable'}}, status_code=503)
    actor = identity_read.requester(request.headers.get('x-popclaw-inbox-token', ''),
                                    identity, state.origin, purpose)
    if actor is None:
        return None, None, Response(status_code=401)
    return actor, identity, None


def _entry(store, row):
    originals = store.query_all('SELECT event_id FROM relation_originals '
                               'WHERE house_key=? AND follower=? AND followee=? ORDER BY event_id',
                               (row['house_key'], row['follower'], row['followee']))
    applied = row['applied_event_id']
    return {'follower_popclaw_id': row['follower'], 'followee_popclaw_id': row['followee'],
            'state': row['state'], 'revoked_at': row['revoked_at'],
            'applied_seq': str(row['applied_seq']) if row['applied_seq'] is not None else None,
            'applied_event_id': applied, 'conflicted': bool(row['conflicted']),
            'evidence_event_ids': [e['event_id'] for e in originals],
            'state_event_id': applied, 'state_proof': 'applied_event' if applied else 'unknown'}


async def snapshot(request):
    deadline = time.monotonic() + CHECKPOINT_BUDGET_SECONDS
    actor, identity, refusal = _authority(request, 'relation-snapshot')
    if refusal is not None:
        return refusal
    store = request.app.state.store
    try:
        limit = max(1, min(500, int(request.query_params.get('limit', '100'))))
    except ValueError:
        return Response(status_code=400)
    cursor = request.query_params.get('cursor')
    try:
        with store.write_tx():
            generation = int(store.get_meta('personal_generation'))
            if cursor is not None:
                continuation = store.query_one('SELECT * FROM relation_continuations WHERE cursor=?', (cursor,))
                if continuation is None:
                    return Response(status_code=400)
                cp = store.query_one('SELECT * FROM relation_checkpoints WHERE checkpoint=?',
                                     (continuation['checkpoint'],))
                if (cp is None or cp['generation'] != generation
                        or cp['expires_at_ms'] <= store.clock_ms()):
                    return Response(status_code=410)
                if cp['requester'] != actor:
                    return Response(status_code=400)
                offset = continuation['offset']
            else:
                # Every queued fact predates this transaction. Publish the
                # complete committed prefix before freezing any projections.
                relations.publish_pending(store)
                counter = store.query_one('SELECT * FROM personal_counters WHERE recipient=?', (actor,))
                entries = [_entry(store, row) for row in store.query_all(
                    'SELECT * FROM relation_edges WHERE house_key=? AND (follower=? OR followee=?) '
                    'ORDER BY follower,followee', (identity.house_key_id, actor, actor))]
                if time.monotonic() > deadline:
                    return Response(status_code=503, headers={'Retry-After': '1'})
                cp = {'checkpoint': secrets.token_hex(16), 'generation': generation,
                      'floor': counter['floor'] if counter else 1,
                      'watermark': counter['high_water'] if counter else 0,
                      'entries_json': json.dumps(entries)}
                store.execute('INSERT INTO relation_checkpoints VALUES (?,?,?,?,?,?,?)',
                              (cp['checkpoint'], actor, generation, cp['floor'], cp['watermark'],
                               cp['entries_json'], store.clock_ms() + CHECKPOINT_TTL_MS))
                offset = 0
            entries = json.loads(cp['entries_json'])
            page = entries[offset:offset + limit]
            complete = offset + len(page) >= len(entries)
            next_cursor = None
            if not complete:
                next_cursor = secrets.token_urlsafe(24)
                store.execute('INSERT INTO relation_continuations VALUES (?,?,?)',
                              (next_cursor, cp['checkpoint'], offset + len(page)))
            result = {'checkpoint_id': cp['checkpoint'], 'log_generation': str(cp['generation']),
                      'floor': str(cp['floor']), 'watermark': str(cp['watermark']),
                      'entries': page, 'next_cursor': next_cursor, 'complete': complete}
    except (sqlite3.Error, StorageUnavailable):
        return JSONResponse({'error': {'code': 'storage_unavailable'}}, status_code=503,
                            headers={'Retry-After': '1'})
    return JSONResponse(result)


async def evidence(request):
    actor, identity, refusal = _authority(request, 'relation-evidence')
    if refusal is not None:
        return refusal
    store = request.app.state.store
    cid = request.path_params['event_id']
    try:
        with store.read_tx():
            row = store.query_one('SELECT body_tag FROM accepted_envelopes WHERE event_id=?', (cid,))
            # Do not even inspect metadata of a non-relation payload.
            if row is None or row['body_tag'] not in wire.RELATION_TAGS:
                return Response(status_code=404)
            row = store.query_one('SELECT r.*,a.envelope_bytes,a.body_tag FROM relation_originals r '
                                  'JOIN accepted_envelopes a USING(event_id) WHERE event_id=?', (cid,))
            if row is None or actor not in (row['follower'], row['followee']):
                return Response(status_code=404)
            edge = store.query_one('SELECT * FROM relation_edges WHERE house_key=? AND follower=? AND followee=?',
                                   (row['house_key'], row['follower'], row['followee']))
            hints = {'event_status': row['event_status'],
                     'seq': str(row['seq']) if row['seq'] is not None else None,
                     'edge_applied_seq': str(edge['applied_seq']) if edge['applied_seq'] is not None else None,
                     'edge_applied_event_id': edge['applied_event_id'], 'edge_conflicted': bool(edge['conflicted'])}
            result = {'event_id': cid, 'payload_type': wire.BODY_TAGS[row['body_tag']],
                      'envelope_b64': wire.b64(bytes(row['envelope_bytes'])), 'hints': hints}
    except sqlite3.Error as exc:
        raise StorageUnavailable('relation evidence storage is unavailable') from exc
    return JSONResponse(result)


async def relation_list(request):
    """Current-client list binding; a list is a hint, never author proof."""
    actor, identity, refusal = _authority(request, 'relation-list')
    if refusal is not None:
        return refusal
    if actor != request.path_params['popclaw_id']:
        return Response(status_code=403)
    incoming = request.url.path.startswith('/followers/')
    own, peer = ('followee', 'follower') if incoming else ('follower', 'followee')
    try:
        with request.app.state.store.read_tx():
            rows = request.app.state.store.query_all(
                f'SELECT {peer} AS popclaw_id FROM relation_edges '
                f'WHERE house_key=? AND {own}=? AND state=\'active\' ORDER BY {peer}',
                (identity.house_key_id, actor))
            result = [{'popclaw_id': row['popclaw_id']} for row in rows]
    except sqlite3.Error as exc:
        raise StorageUnavailable('relation list storage is unavailable') from exc
    return JSONResponse(result)
