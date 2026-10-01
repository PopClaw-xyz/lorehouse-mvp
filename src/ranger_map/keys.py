"""House identity: the persistent key and incarnations of this LoreHouse.

The house authority key is created once per data root and stored with mode
0600 under ``<data-dir>/house_key.seed``. It is the HouseBinding.house_key,
the session ACK authority (``house_session.ack_pubkey``) and the action
result authority (``actions.result_authority_pubkey``) — per TRUST.md these
identify the same 32-byte key. The key never enters logs, tests reports, the
repository or served pages, and is never read from the network.

Two distinct incarnation domains (BASELINE.md):
- the **server incarnation** (HouseBinding.incarnation): stable across
  ordinary restarts, changed only by an explicit restore/rebuild;
- the **public log incarnation**: identity of the public event log, also
  stable across restarts, rotated to a never-reused new id on restore or any
  baseline switch in either direction.
"""

from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from . import wire

KEY_FILENAME = "house_key.seed"


class HouseIdentityError(Exception):
    pass


@dataclass(frozen=True)
class HouseIdentity:
    """The loaded authority key plus derived public identifiers."""

    private_key: Ed25519PrivateKey
    public_key_bytes: bytes

    @property
    def house_key_id(self) -> str:
        """base58 popclaw_id form of the authority key."""
        return wire.popclaw_id_from_key(self.public_key_bytes)

    @property
    def ack_pubkey_hex(self) -> str:
        return self.public_key_bytes.hex()

    def sign(self, message: bytes) -> bytes:
        return wire.sign_ed25519(self.private_key, message)

    def verify(self, signature: bytes, message: bytes) -> bool:
        return wire.verify_ed25519(self.public_key_bytes, signature, message)


def load_or_create_identity(data_dir: Path) -> HouseIdentity:
    """Load the persistent house key, creating it once on a fresh data root.

    An existing key is never replaced silently: a corrupt or wrong-length
    seed file is a hard error so a damaged identity cannot quietly fork this
    house's identity.
    """
    key_path = data_dir / KEY_FILENAME
    if key_path.exists():
        seed = key_path.read_bytes()
        if len(seed) != 32:
            raise HouseIdentityError(
                f"{KEY_FILENAME} is corrupt (expected 32 bytes); refusing to "
                "replace the house identity - restore it from backup or use a "
                "fresh data directory"
            )
    else:
        seed = secrets.token_bytes(32)
        try:
            fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(fd, seed)
            finally:
                os.close(fd)
        except FileExistsError:  # pragma: no cover - concurrent first boot
            seed = key_path.read_bytes()
    return HouseIdentity(
        private_key=Ed25519PrivateKey.from_private_bytes(seed),
        public_key_bytes=Ed25519PrivateKey.from_private_bytes(seed)
        .public_key()
        .public_bytes_raw(),
    )


def new_incarnation(prefix: str) -> str:
    """Fresh, never-reused incarnation id matching [A-Za-z0-9_-]{1,64}."""
    return f"{prefix}-{secrets.token_hex(12)}"


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
