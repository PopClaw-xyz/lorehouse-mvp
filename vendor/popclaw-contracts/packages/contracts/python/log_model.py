"""Executable protocol referee, NOT production storage, concurrency or trust code.

Transitions execute serially. Tests must not cite this model as database fencing,
server readiness, socket stop/join or session-maintenance evidence. Author/transport
signatures are assumed independently verified; raw admission uses the shared guard.
"""
from dataclasses import dataclass, field
from typing import Optional
from public_baseline import ENVELOPE_BASELINE, check_public_envelope_structure
from protocol import message_type


@dataclass(frozen=True)
class LogIdentity:
    log: str
    baseline: str


@dataclass
class Log:
    identity: LogIdentity
    rows: list = field(default_factory=list)
    ready: bool = False


class Referee:
    def __init__(self):
        self.logs = {}
        self.active = None
        self.connections = []
        self.retired = set()
        self.server_incarnation = 'server-1'
        self.server_key = 'unchanged-key'
        self.session = 'existing-session'
        self.policy = 'unchanged-policy'

    def create(self, name, baseline=ENVELOPE_BASELINE):
        if name in self.logs:
            raise ValueError('LOG_ID_REUSE')
        log = Log(LogIdentity(name,baseline))
        self.logs[name] = log
        return log

    def prepare(self, log):
        log.ready = False
        for raw in log.rows:
            if log.identity.baseline == ENVELOPE_BASELINE:
                check_public_envelope_structure(raw)
        log.ready = True

    def activate(self, log):
        if log.identity.log in self.retired:
            raise ValueError('LOG_ID_REUSE')
        if not log.ready:
            raise ValueError('PUBLIC_STREAM_UNAVAILABLE')
        # Serial referee cutover; real implementations need an emission fence
        # whose critical section covers both identity validation and emission.
        if self.active is not None and self.active.identity != log.identity:
            self.retired.add(self.active.identity.log)
            for connection in self.connections:
                connection.closed = True
        self.active = log

    def admit(self, raw):
        if self.active is None or not self.active.ready:
            raise ValueError('PUBLIC_STREAM_UNAVAILABLE')
        if self.active.identity.baseline == ENVELOPE_BASELINE:
            check_public_envelope_structure(raw)
        if raw in self.active.rows:
            return self.active.rows.index(raw)+1
        self.active.rows.append(bytes(raw))
        return len(self.active.rows)

    def select(self, identity, public_after=0, scopes=None, legacy=False):
        if self.active is None or not self.active.ready:
            raise ValueError('PUBLIC_STREAM_UNAVAILABLE')
        if identity != self.active.identity:
            raise ValueError('log_incarnation_changed')
        if identity.baseline != ENVELOPE_BASELINE and not legacy:
            raise ValueError('UNSUPPORTED_BASELINE')
        c = Connection(self,identity,public_after,dict(scopes or {}),legacy)
        self.connections.append(c)
        return c


class Connection:
    def __init__(self, house, identity, public_after, scopes, legacy):
        self.house, self.identity = house, identity
        self.public_after = public_after
        self.scopes = scopes
        self.legacy = legacy
        self.closed = False
        self.emitted = []
        self.checkpoints = []
        self.gap = None
        self.high_water = len(house.active.rows)
        inputs = list(scopes.values()) + ([] if public_after is None else [public_after])
        if not inputs:
            raise ValueError('EMPTY_SELECTION')
        if any(x < 0 or x > self.high_water for x in inputs):
            raise ValueError('cursor_ahead')
        self.scanned = min(inputs)

    def current(self):
        if self.closed:
            raise ValueError('SELECTION_FENCED')
        if self.house.active.identity != self.identity:
            self.closed = True
            raise ValueError('log_incarnation_changed')
        if not self.house.active.ready:
            self.closed = True
            raise ValueError('PUBLIC_STREAM_UNAVAILABLE')

    def fail(self, reason):
        self.closed = True
        self.gap = None if self.legacy else {'reason':reason,'lane':'public' if self.public_after is not None else 'connection'}

    def page(self, size=256):
        self.current()
        if size < 1 or size > 512:
            raise ValueError('PAGE_LIMIT')
        stop = min(self.scanned+size,self.high_water)
        pending = []
        for seq in range(self.scanned+1,stop+1):
            raw = self.house.active.rows[seq-1]
            try:
                # Every boundary, including explicit legacy, applies the guard.
                check_public_envelope_structure(raw)
            except ValueError:
                self.fail('public_log_invalid')
                return
            env = message_type('popclaw.event.EventEnvelope').FromString(raw)
            scopes = list(env.house_event.public_scopes) if env.HasField('house_event') else []
            full = self.public_after is not None and seq > self.public_after
            matching = [s for s in scopes if s in self.scopes and seq > self.scopes[s]]
            if full or matching:
                pending.append((seq,raw,full,matching))
        self.current()
        # The entire page has passed validation before any durable receive row.
        for seq,raw,full,matching in pending:
            self.emitted.append((seq,raw))
            if full:
                self.public_after=seq
            for s in matching:
                self.scopes[s]=seq
        self.scanned=stop

    def checkpoint(self):
        self.current()
        if self.scanned != self.high_water:
            raise ValueError('UNSCANNED_INTERVAL')
        # Fresh validation models the mandatory pre-checkpoint read. Production
        # must validate identity/readiness/retention under its actual lock/snapshot.
        for raw in self.house.active.rows[:self.high_water]:
            try:
                check_public_envelope_structure(raw)
            except ValueError:
                self.fail('public_log_invalid')
                return
        self.current()
        if self.public_after is not None:
            self.public_after=self.high_water
        self.scopes={s:self.high_water for s in self.scopes}
        self.checkpoints.append(self.high_water)
