"""Explicit maintenance arguments, guide pins, rejection before mutation."""

import json
from contextlib import closing

import pytest

from ranger_map import house as house_mod, wire
from ranger_map.keys import digest_bytes, load_or_create_identity
from ranger_map.store import Store
from tests.interop.wire_helpers import ORIGIN
from tools import house_admin


def run(monkeypatch, data, *args):
    monkeypatch.setattr('sys.argv', ['house-admin', '--data-dir', str(data), '--origin', ORIGIN, *args])
    return house_admin.main()


@pytest.mark.parametrize('args', [(), ('--refresh-guide',), ('--restore', '--unknown')])
def test_bad_arguments_refuse_before_creating_root(tmp_path, monkeypatch, args):
    data = tmp_path / 'never-created'
    with pytest.raises(SystemExit) as error:
        run(monkeypatch, data, *args)
    assert error.value.code == 2 and not data.exists()


@pytest.mark.parametrize('content', [b'\xff', b' ', b'x' * (wire.L_GUIDE_MAX_BYTES + 1)])
def test_invalid_refresh_guide_refuses_before_creating_root(tmp_path, monkeypatch, capsys, content):
    guide = tmp_path / 'invalid-guide.md'
    guide.write_bytes(content)
    monkeypatch.setattr(house_mod, 'GUIDE_RESOURCE', guide)
    data = tmp_path / 'never-created'
    assert run(monkeypatch, data, '--restore', '--refresh-guide') == 1
    assert not data.exists()
    assert 'bundled guide' in capsys.readouterr().err


def test_restore_refuses_mistyped_nonexistent_root(tmp_path, monkeypatch):
    data = tmp_path / 'wrong-root'
    assert run(monkeypatch, data, '--restore') == 1
    assert not data.exists()


def test_explicit_refresh_changes_guide_and_capability_with_same_key_and_origin(tmp_path, monkeypatch, capsys):
    data = tmp_path / 'existing'
    old_bytes, old_revision = b'# Previously pinned guide\n', 'rangermap-guide-1'
    with closing(Store.open(data)) as store:
        identity = load_or_create_identity(data)
        state = house_mod.load_or_setup(store, identity, ORIGIN)
        old_manifest = state.manifest_json
        old_manifest.pop('relations')
        old_manifest.pop('read_auth')
        old_manifest['world_interaction']['guide'].update(sha256=digest_bytes(old_bytes), revision=old_revision)
        with store.write_tx():
            store.set_meta('manifest_bytes', json.dumps(old_manifest))
            store.set_meta('guide_bytes', old_bytes.decode())
        old_state = house_mod.load_or_setup(store, identity, ORIGIN)
        # A source update and ordinary boot preserve the prior pins.
        assert old_state.guide_bytes == old_bytes
        assert 'relations' not in old_state.manifest_json
        ordinary = house_mod.restore(store, identity, old_state)
        assert ordinary.guide_bytes == old_bytes
        assert ordinary.manifest_json['world_interaction']['guide']['revision'] == old_revision
        prior_cap = ordinary.manifest_digest
        prior_log = ordinary.log_incarnation
        prior_server = ordinary.server_incarnation
        # Same-root single-instance lock prevents actual maintenance.
        assert run(monkeypatch, data, '--restore', '--refresh-guide') == 1
        assert house_mod.load_or_setup(store, identity, ORIGIN).manifest_digest == prior_cap
    assert run(monkeypatch, data, '--restore', '--refresh-guide') == 0
    output = capsys.readouterr().out
    with closing(Store.open(data)) as store:
        refreshed_identity = load_or_create_identity(data)
        refreshed = house_mod.load_or_setup(store, refreshed_identity, ORIGIN)
        assert refreshed_identity.house_key_id == identity.house_key_id
        assert refreshed.origin == ORIGIN
        assert refreshed.server_incarnation != prior_server and refreshed.log_incarnation != prior_log
        assert refreshed.manifest_digest != prior_cap
        assert refreshed.manifest_digest in output
        assert refreshed.guide_bytes == house_mod.GUIDE_RESOURCE.read_bytes()
        assert refreshed.manifest_json['world_interaction']['guide'] == {
            'path': '/v1/guide.md', 'sha256': digest_bytes(refreshed.guide_bytes),
            'revision': house_mod.GUIDE_REVISION}
        assert refreshed.manifest_json['relations'] == {'ordered': 1}
        assert refreshed.manifest_json['read_auth'] == {'schemes': ['popclaw-identity-read-v2']}


def test_refresh_pin_failure_rolls_back_entire_restore(house, monkeypatch):
    old_meta = [tuple(r) for r in house.store.query_all('SELECT * FROM house_meta ORDER BY key')]
    set_meta = house.store.set_meta
    def fail_guide(key, value):
        if key == 'guide_bytes':
            raise house_mod.HouseStateError('injected guide pin failure')
        set_meta(key, value)
    monkeypatch.setattr(house.store, 'set_meta', fail_guide)
    with pytest.raises(house_mod.HouseStateError, match='injected'):
        house_mod.restore(house.store, house.identity, house.state, refresh_guide=True)
    assert [tuple(r) for r in house.store.query_all('SELECT * FROM house_meta ORDER BY key')] == old_meta
