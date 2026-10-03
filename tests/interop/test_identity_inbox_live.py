"""Actual HTTP and streaming authority, including A-leave/B-enter isolation."""

import json
import time
import urllib.error
import urllib.request
from types import SimpleNamespace

from ranger_map import wire
from tests.interop.test_relation_reads import credential
from tests.interop.test_streams_live import LiveServer, SseReader, get_manifest
from tests.interop.test_relations_wire import _follow
from tests.interop.wire_helpers import Actor, make_dm, session_request


def authority(server):
    return SimpleNamespace(identity=SimpleNamespace(house_key_id=get_manifest(server)['official_ids'][0]),
                           state=SimpleNamespace(origin=server.origin))


def session(server, actor, op, seq, install, target=''):
    raw = session_request(actor, op, seq, installation=install,
                          target_session=target, origin=server.origin)
    with urllib.request.urlopen(urllib.request.Request(server.url('/v1/house-session'), data=raw), timeout=5) as r:
        return wire.HouseSessionAck.FromString(r.read())


def refused(server, path, token, status):
    req = urllib.request.Request(server.url(path), headers={'x-popclaw-inbox-token': token})
    try:
        response = urllib.request.urlopen(req, timeout=3)
    except urllib.error.HTTPError as exc:
        assert exc.code == status
        return
    response.close()
    raise AssertionError(f'expected {status}')


def test_a_leave_b_enter_never_rescues_a_and_relation_reads_remain_independent(tmp_path):
    server = LiveServer(tmp_path)
    try:
        context = authority(server)
        actor, peer = Actor(), Actor()
        path = f'/inbox/{actor.popclaw_id}/stream'
        first = session(server, actor, 1, 1, 'installation-A')
        assert first.core.session_id
        session(server, actor, 3, 2, 'installation-A', first.core.session_id)
        second = session(server, actor, 1, 1, 'installation-B')
        assert second.core.session_id != first.core.session_id
        refused(server, path, first.core.inbox_read_token, 401)
        refused(server, path, credential(context, actor, 'inbox-stream'), 403)
        raw = make_dm(peer, actor, 'B may read; A may not')
        server.post_signed(raw, peer)
        reader = SseReader(server.url(path), headers={'x-popclaw-inbox-token': second.core.inbox_read_token})
        try:
            assert reader.read_until(lambda e: bool(e))[0][1] == raw
        finally:
            reader.close()
        session(server, actor, 3, 2, 'installation-B', second.core.session_id)
        refused(server, path, credential(context, actor, 'inbox-stream'), 403)
        refused(server, path, second.core.inbox_read_token, 401)
        original = _follow(actor, peer, order={'seq': 1, 'house_key': context.identity.house_key_id})
        cid = server.post_signed(original, actor)['event_id']
        for route, purpose in [('/v1/relation-snapshot','relation-snapshot'),
                               ('/v1/relation-evidence/'+cid,'relation-evidence')]:
            with urllib.request.urlopen(urllib.request.Request(server.url(route),
                    headers={'x-popclaw-inbox-token': credential(context, actor, purpose)}), timeout=3) as r:
                assert r.status == 200
                assert json.load(r)
    finally:
        server.stop()


def test_fresh_identity_flow_closes_on_first_enter_and_rejects_old_or_other_object(tmp_path):
    server = LiveServer(tmp_path)
    try:
        context = authority(server)
        sender, actor, outsider = Actor(), Actor(), Actor()
        path = f'/inbox/{actor.popclaw_id}/stream'
        token = credential(context, actor, 'inbox-stream')
        for bad in (token[3:], credential(context, actor, 'relation-snapshot'),
                    credential(context, actor, 'inbox-stream', ts=int(time.time())-61),
                    credential(context, actor, 'inbox-stream', origin='https://wrong.invalid'),
                    credential(context, actor, 'inbox-stream', key=outsider.popclaw_id)):
            refused(server, path, bad, 401)
        refused(server, path, credential(context, outsider, 'inbox-stream'), 403)
        raw = make_dm(sender, actor, 'identity lane before first session')
        server.post_signed(raw, sender)
        reader = SseReader(server.url(path), headers={'x-popclaw-inbox-token': token}, idle_timeout=3)
        try:
            assert reader.read_until(lambda e: bool(e))[0][1] == raw
            session(server, actor, 1, 1, 'first-installation')
            server.post_signed(make_dm(sender, actor, 'must not arrive on identity stream'), sender)
            reader.read_until(lambda e: len(e)>1, timeout=3)
            assert len(reader.events) == 1  # EOF, no second frame/heartbeat.
        finally:
            reader.close()
        refused(server, path, token, 403)
    finally:
        server.stop()


def test_relation_original_is_delivered_verbatim_only_to_both_participants(tmp_path):
    server = LiveServer(tmp_path)
    try:
        context = authority(server)
        a, b, outsider = Actor(), Actor(), Actor()
        original = _follow(a, b, order={'seq': 1, 'house_key': context.identity.house_key_id})
        server.post_signed(original, a)
        for actor in (a, b):
            reader = SseReader(server.url(f'/inbox/{actor.popclaw_id}/stream'),
                               headers={'x-popclaw-inbox-token': credential(context, actor, 'inbox-stream')})
            try:
                assert reader.read_until(lambda e: bool(e))[0] == ('envelope', original)
            finally:
                reader.close()
        own_dm = make_dm(a, outsider, 'only the outsider own DM')
        server.post_signed(own_dm, a)
        reader = SseReader(server.url(f'/inbox/{outsider.popclaw_id}/stream'),
                           headers={'x-popclaw-inbox-token': credential(context, outsider, 'inbox-stream')})
        try:
            assert reader.read_until(lambda e: bool(e))[0] == ('envelope', own_dm)
        finally:
            reader.close()
        for cursor, reason in (('bad', 'unreadable'), ('99.0', 'generation')):
            req = urllib.request.Request(server.url(f'/inbox/{a.popclaw_id}/stream'),
                    headers={'x-popclaw-inbox-token': credential(context, a, 'inbox-stream'), 'Last-Event-ID': cursor})
            with urllib.request.urlopen(req, timeout=3) as r:
                text = r.read().decode()
                assert text.startswith('event: cursor-reset\n') and 'id:' not in text
                assert json.loads(text.split('data: ')[1])['reason'] == reason
    finally:
        server.stop()
