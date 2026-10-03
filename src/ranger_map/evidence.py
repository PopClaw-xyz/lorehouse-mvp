"""Shared signed-wire evidence helpers for ingress and actions."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field


@dataclass
class PushOutcome:
    http_status: int
    code: str
    message: str = ""
    event_id: str | None = None
    duplicate: bool = False
    receipt_b64: str | None = None
    public: bool = False
    extra: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        body: dict = {"accepted": 200 <= self.http_status < 300 and self.code == "OK"}
        if self.event_id:
            body["event_id"] = self.event_id
        if self.duplicate:
            body["duplicate"] = True
        if self.receipt_b64:
            body["receipt_base64"] = self.receipt_b64
        if self.public:
            body["public"] = True
        body.update(self.extra)
        if self.code != "OK":
            error: dict = {"code": self.code}
            if self.message:
                error["message"] = self.message
            body["error"] = error
        return body


def blob(payload: bytes) -> sqlite3.Binary:
    return sqlite3.Binary(payload)


def store_envelope(store, cid: str, payload: bytes, actor_id: str, tag: int,
                   kind: str, public_eligible: int, scopes: list[str],
                   now_ms: int) -> None:
    """Record full signed-wire evidence for an accepted envelope."""
    store.execute(
        "INSERT INTO accepted_envelopes (event_id, envelope_bytes, actor_id,"
        " body_tag, kind, public_eligible, scopes, accepted_at_ms)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cid, blob(payload), actor_id, tag, kind, public_eligible,
         json.dumps(scopes), now_ms),
    )
    if tag not in (20, 21):
        # Relation insertion invokes this only after its edge index exists.
        # Nonrelation arrivals can prove a waiting recovery invalid now.
        from .relations import rejudge_referencing
        rejudge_referencing(store, cid)
