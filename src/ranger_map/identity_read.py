"""Current-client identity-read-v2 binding; independent of G0 ACK tokens.

The purpose is chosen by the route and the audience by trusted runtime state.
No claimed token field chooses either. See the version binding in docs.
"""

import base64
import re
import time

from . import wire
from . import sessions

SCHEME = 'popclaw-identity-read-v2'


def requester(token, identity, origin, purpose, now=None):
    if len(token) > 153 or not token.isascii():
        return None
    parts = token.split('.')
    if len(parts) != 4 or parts[0] != 'v2':
        return None
    _, actor, seconds, signature = parts
    if len(actor) > 44 or not re.fullmatch(r'(0|[1-9][0-9]{0,15})', seconds):
        return None
    ts = int(seconds)
    if ts > 2**53 - 1 or abs((int(time.time()) if now is None else now) - ts) > 60:
        return None
    if len(signature) != 88:
        return None
    try:
        key = wire.key_bytes_from_popclaw_id(actor)
        sig = wire.b64decode_strict(signature)
    except (ValueError, UnicodeError):
        return None
    if len(sig) != 64 or base64.b64encode(sig).decode('ascii') != signature:
        return None
    message = f'{SCHEME}:{purpose}:{actor}:{identity.house_key_id}:{seconds}:{origin}'.encode('ascii')
    return actor if wire.verify_ed25519(key, sig, message) else None


def inbox_status(store, token, identity, origin, recipient):
    """Identity-level reads cannot bypass this House's session-history policy."""
    if identity is None or not origin:
        return 503
    actor = requester(token, identity, origin, 'inbox-stream')
    if actor is None:
        return 401
    if actor != recipient or sessions.actor_has_session_state(store, actor):
        return 403
    return 200
