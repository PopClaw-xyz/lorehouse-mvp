"""Restore retains committed personal originals, positions and CID deduplication."""

import asyncio
from contextlib import closing

from ranger_map import house as house_mod, ingress, relations, streams, wire
from ranger_map.keys import load_or_create_identity
from ranger_map.store import Store
from ranger_map.streams import StreamHub
from tests.interop.test_relation_reads import credential
from tests.interop.wire_helpers import Actor, ORIGIN, make_dm, wrap_signed


def test_restore_restart_reset_and_replay_preserve_unread_dm(tmp_path, monkeypatch):
    data = tmp_path / 'personal-data'
    sender, recipient = Actor(), Actor()
    first = make_dm(sender, recipient, 'committed unread before restore')
    second = make_dm(sender, recipient, 'committed but not published')
    with closing(Store.open(data)) as store:
        identity = load_or_create_identity(data)
        state = house_mod.load_or_setup(store, identity, ORIGIN)
        assert ingress.handle_push(store, identity, state, wrap_signed(first, sender)).http_status == 200
        publisher = relations.publish
        monkeypatch.setattr(relations, 'publish', lambda _: None)
        assert ingress.handle_push(store, identity, state, wrap_signed(second, sender)).http_status == 200
        monkeypatch.setattr(relations, 'publish', publisher)
        assert store.query_one('SELECT COUNT(*) n FROM personal_log')[0] == 1
        house_mod.restore(store, identity, state)
        assert store.query_one('SELECT COUNT(*) n FROM personal_log')[0] == 1
    with closing(Store.open(data)) as store:
        identity = load_or_create_identity(data)
        state = house_mod.load_or_setup(store, identity, ORIGIN)
        hub = StreamHub(store)
        for original in (first, second):
            replay = ingress.handle_push(store, identity, state, wrap_signed(original, sender))
            assert replay.http_status == 200 and replay.duplicate
        from types import SimpleNamespace
        token = credential(SimpleNamespace(identity=identity, state=state), recipient, 'inbox-stream')

        async def read():
            reset = streams.stream_inbox_events(store, identity, hub, ORIGIN,
                                                recipient.popclaw_id, token, False, '1.0')
            assert [chunk async for chunk in reset] == [streams._personal_reset('generation', 2, 1)]
            # A reset has no resume id; relation snapshots cannot recover DMs.
            # Start at the retained floor and let the recipient deduplicate CIDs.
            replay = streams.stream_inbox_events(store, identity, hub, ORIGIN,
                                                 recipient.popclaw_id, token, False, '')
            try:
                chunks = [await anext(replay), await anext(replay)]
            finally:
                await replay.aclose()
            assert chunks == [streams._sse_named_with_id('envelope', f'2.{seq}', raw)
                              for seq, raw in enumerate((first, second), 1)]
        asyncio.run(read())
        assert store.query_one('SELECT COUNT(*) n FROM dm_log')[0] == 2
        assert store.query_one('SELECT COUNT(*) n FROM personal_log')[0] == 2
        assert store.query_one('SELECT high_water FROM personal_counters')[0] == 2
        assert store.query_one('SELECT COUNT(*) n FROM personal_outbox')[0] == 2
        assert store.query_one('SELECT COUNT(*) n FROM personal_outbox WHERE published=0')[0] == 0
        assert {r['event_id'] for r in store.query_all('SELECT event_id FROM personal_log')} == {
            wire.envelope_cid(first), wire.envelope_cid(second)}
