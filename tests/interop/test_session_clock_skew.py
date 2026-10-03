"""Bounded request clock skew without weakening expiry or session authority."""
import pytest

from ranger_map import sessions, wire
from tests.interop.wire_helpers import Actor, session_request

NOW = 1791048000


def verified(house, payload):
    response = house.client.post('/v1/house-session', content=payload)
    assert response.status_code == 200
    ack = wire.HouseSessionAck.FromString(response.content)
    assert ack.signer_pubkey == house.identity.public_key_bytes
    assert wire.verify_ed25519(ack.signer_pubkey, ack.signature,
        wire.signing_input(wire.DOMAIN_SESSION_ACK, wire.canonical_core(ack.core)))
    return ack.core


def entered(house, monkeypatch):
    monkeypatch.setattr(sessions, '_now', lambda: NOW)
    actor = Actor()
    ack = verified(house, session_request(actor, sessions.ENTER, 10,
        issued_at=NOW, expires_at=NOW + 60))
    assert ack.outcome == 1
    # This clock belongs to the isolated server fixture, not the OS clock.
    monkeypatch.setattr(sessions, '_now', lambda: NOW + 30)
    return actor, ack


def renewal(actor, initial, issued, expires):
    return session_request(actor, sessions.RENEW, 10,
        target_session=initial.session_id,
        expected_revision=initial.house_revision,
        issued_at=issued, expires_at=expires)


@pytest.mark.parametrize('ahead,window', [(0, 60), (1, 60), (2, 60), (30, 60), (30, 600)])
def test_natural_renewal_window_tolerates_bounded_client_clock(house, monkeypatch, ahead, window):
    actor, initial = entered(house, monkeypatch)
    now = NOW + 30
    ack = verified(house, renewal(actor, initial, now + ahead, now + ahead + window))
    assert ack.outcome == 3 and ack.error_code == 0
    assert ack.session_id == initial.session_id
    assert ack.house_revision == initial.house_revision
    assert ack.session_active
    assert ack.lease_expires_at == now + wire.SESSION_LEASE_SECONDS
    assert ack.lease_expires_at > initial.lease_expires_at
    assert house.store.query_one('SELECT COUNT(*) AS c FROM sessions')['c'] == 1


@pytest.mark.parametrize('issued_offset,expiry_offset', [
    (31, 91),       # excessive future issue time
    (-60, 0),      # expiry is a strict deadline, even at exact equality
    (-61, -1),     # already expired
    (20, 19),      # reversed signed window that is otherwise within skew
    (20, 20),      # empty signed window
    (0, 601),      # excessive authority lifetime
    (30, 631),     # skew never exempts the 600-second window cap
])
def test_invalid_renewal_times_preserve_current_session(house, monkeypatch, issued_offset, expiry_offset):
    actor, initial = entered(house, monkeypatch)
    before = dict(house.store.query_one('SELECT * FROM sessions'))
    now = NOW + 30
    ack = verified(house, renewal(actor, initial, now + issued_offset, now + expiry_offset))
    assert ack.outcome == 7 and ack.error_code == sessions.AUTH_INVALID
    assert dict(house.store.query_one('SELECT * FROM sessions')) == before


@pytest.mark.parametrize('fault', ['signature', 'identity', 'audience', 'target', 'installation', 'expired_lease'])
def test_clock_tolerance_does_not_bypass_other_renewal_guards(house, monkeypatch, fault):
    actor, initial = entered(house, monkeypatch)
    now = NOW + 30
    request = wire.HouseSessionRequest.FromString(renewal(actor, initial, now + 2, now + 62))
    expected = sessions.AUTH_INVALID
    if fault == 'signature':
        request.signature = b'\x00' * 64
    elif fault == 'identity':
        request.signer_pubkey = Actor().public_key_bytes
    else:
        if fault == 'audience':
            request.core.house_origin = 'http://127.0.0.1:9999'
            expected = sessions.AUDIENCE_MISMATCH
        elif fault == 'target':
            request.core.target_session_id = 'unknown-session'
            expected = sessions.SESSION_FENCED
        elif fault == 'installation':
            request.core.installation_id = 'other-installation'
            expected = sessions.SESSION_FENCED
        elif fault == 'expired_lease':
            house.store.execute('UPDATE sessions SET lease_expires_at = ?', (now,))
            expected = sessions.LEASE_EXPIRED
        request.signature = actor.sign(wire.signing_input(
            wire.DOMAIN_SESSION_REQUEST, wire.canonical_core(request.core)))
    before = dict(house.store.query_one('SELECT * FROM sessions'))
    ack = verified(house, request.SerializeToString(deterministic=True))
    assert ack.outcome == 7 and ack.error_code == expected
    after = dict(house.store.query_one('SELECT * FROM sessions'))
    if fault == 'expired_lease':
        assert after['active'] == 0
        assert after['lease_expires_at'] == before['lease_expires_at']
    else:
        assert after == before


@pytest.mark.parametrize('fault', ['future', 'expired', 'signature', 'semantic'])
def test_renew_replay_still_authenticates_every_attempt(house, monkeypatch, fault):
    actor, initial = entered(house, monkeypatch)
    now = NOW + 30
    raw = renewal(actor, initial, now + 2, now + 62)
    request = wire.HouseSessionRequest.FromString(raw)
    ack = verified(house, raw)
    assert ack.outcome == 3
    before = dict(house.store.query_one('SELECT * FROM sessions'))
    if fault == 'future':
        request.core.issued_at = now + 31
        request.core.expires_at = now + 91
    elif fault == 'expired':
        request.core.issued_at = now - 60
        request.core.expires_at = now
    elif fault == 'semantic':
        request.core.target_session_id = 'changed-semantic-target'
    request.signature = actor.sign(wire.signing_input(
        wire.DOMAIN_SESSION_REQUEST, wire.canonical_core(request.core)))
    if fault == 'signature':
        request.signature = b'\x00' * 64
    rejected = verified(house, request.SerializeToString(deterministic=True))
    assert rejected.outcome == 7
    assert rejected.error_code == (sessions.IDEMPOTENCY_CONFLICT if fault == 'semantic' else sessions.AUTH_INVALID)
    assert dict(house.store.query_one('SELECT * FROM sessions')) == before
    assert verified(house, raw) == ack
    assert house.store.query_one('SELECT COUNT(*) AS c FROM session_requests')['c'] == 2
