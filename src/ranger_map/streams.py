"""Public world stream, legacy lane and private DM inbox streams.

Fencing model (BASELINE.md "check-to-send"): the public log incarnation and
a monotonic stream epoch live in ``house_meta``; every emission first
re-validates the captured (epoch, log) identity under the hub's cutover
lock, and a rotation — which only the explicit restore path performs, and
only while the server is stopped (the data-root flock enforces that) —
bumps both before old connections can send another frame or checkpoint.
Historical unsupported rows are re-guarded on every scan page; a violation
produces ``public_log_invalid`` and closes WITHOUT emitting the page or any
checkpoint across it: sequence N never disappears behind filtering and N+1
is never delivered past it.
"""

from __future__ import annotations

import asyncio
import json
import re
import threading
import time
from dataclasses import dataclass

from . import house as house_mod
from . import sessions as sessions_mod
from . import wire
from .keys import HouseIdentity

HEARTBEAT_SECONDS = 15.0
POLL_SECONDS = 0.5

_SCOPE_LABEL = re.compile(r"[A-Za-z0-9_-]{4,64}")
_POSITION = re.compile(r"0|[1-9][0-9]*")
_INCARNATION = re.compile(r"[A-Za-z0-9_-]{1,64}")
_UINT64_MAX = 2**64 - 1


class StreamRequestError(Exception):
    """Malformed request grammar -> HTTP 400 before any SSE output."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass
class PublicSelection:
    log_incarnation: str
    scopes: list[str]           # exact sorted requested set
    scope_inputs: dict[str, int]
    public_after: int | None    # None = scope-only
    limit: int


def parse_public_request(query_params, registered_scopes: list[str],
                         current_log: str) -> PublicSelection:
    mode = query_params.get("mode")
    if mode != "public-v1":
        raise StreamRequestError("mode=public-v1 is required on this lane")
    incarnation = query_params.get("incarnation", "")
    if not _INCARNATION.fullmatch(incarnation):
        raise StreamRequestError("incarnation is malformed")
    cursors_raw = query_params.get("cursors")
    if cursors_raw is None:
        raise StreamRequestError("cursors is required")
    public_after_raw = query_params.get("public_after")
    if public_after_raw is not None and not _POSITION.fullmatch(public_after_raw):
        raise StreamRequestError("public_after must be a non-negative integer")
    if public_after_raw is not None and int(public_after_raw) > _UINT64_MAX:
        raise StreamRequestError("public_after exceeds uint64")
    public_after = int(public_after_raw) if public_after_raw is not None else None
    if cursors_raw == "" and public_after is None:
        raise StreamRequestError("empty cursors are only legal with public_after")

    scope_inputs: dict[str, int] = {}
    if cursors_raw:
        parts = cursors_raw.split(",")
        if len(parts) > wire.L_SCOPES_MAX:
            raise StreamRequestError("too many scopes")
        previous = ""
        for part in parts:
            if ":" not in part:
                raise StreamRequestError("cursor entries need scope:position")
            scope, _, position = part.rpartition(":")
            if not _SCOPE_LABEL.fullmatch(scope):
                raise StreamRequestError("scope label is malformed")
            if not _POSITION.fullmatch(position) or int(position) > _UINT64_MAX:
                raise StreamRequestError("cursor position is malformed")
            if scope in scope_inputs:
                raise StreamRequestError("duplicate scope in the vector")
            if scope.encode("utf-8") <= previous.encode("utf-8"):
                raise StreamRequestError("cursors must be strictly ascending")
            previous = scope
            scope_inputs[scope] = int(position)
    limit_raw = query_params.get("limit")
    limit = 256
    if limit_raw is not None:
        if not limit_raw.isdigit() or not 1 <= int(limit_raw) <= wire.L_STREAM_PAGE_MAX_EVENTS:
            raise StreamRequestError("limit must be between 1 and 512")
        limit = int(limit_raw)
    return PublicSelection(log_incarnation=incarnation,
                           scopes=sorted(scope_inputs),
                           scope_inputs=scope_inputs,
                           public_after=public_after,
                           limit=limit)


class CutoverQuiesceTimeout(Exception):
    """The cutover COMMITTED but a registered live stream task did not exit.

    The old-generation gate is already closed (epoch/log switched under the
    cutover lock; any resumed stream fails its next identity check and
    gaps), so this is a recoverable post-cutover state, not a half-done
    rotation: re-run ``rotate`` after the wedged task exits (or after the
    operator clears it) to re-attempt quiesce. ``pending`` carries the
    (loop, task) pairs that had not exited.
    """

    def __init__(self, message: str, pending: list):
        super().__init__(message)
        self.pending = pending


class StreamHub:
    """Owns the cutover lock shared by rotation and every SSE emission.

    Send fencing has two coordinated layers: (1) every data/checkpoint
    chunk re-validates the captured (epoch, log) identity under this lock
    immediately before it is yielded, and (2) rotation commits the epoch/
    log switch under the lock, then — with the lock RELEASED so cancelled
    streams can still take it — cancels every registered live stream task
    on its own event loop and JOINS it (bounded wait for actual task exit),
    which is the stop/join semantics: a chunk already suspended in a socket
    write is aborted by the cancellation, and the connection is closed by
    the server. Neither layer holds a SQL transaction across network IO.
    """

    def __init__(self, store):
        self._store = store
        self._cutover_lock = threading.RLock()
        self._tasks: dict = {}  # task -> (loop, thread_ident)
        self._tasks_guard = threading.Lock()

    def captured_identity(self) -> tuple[int, str]:
        epoch = int(self._store.get_meta("stream_epoch") or "0")
        log = self._store.get_meta("public_log_incarnation") or ""
        return epoch, log

    def identity_valid(self, captured: tuple[int, str]) -> bool:
        with self._cutover_lock:
            return self.captured_identity() == captured

    def register_stream(self) -> None:
        """Register the current async task for cancellation on rotation."""
        import asyncio

        task = asyncio.current_task()
        loop = asyncio.get_running_loop()
        with self._tasks_guard:
            self._tasks[task] = (loop, threading.get_ident())

    def unregister_stream(self) -> None:
        import asyncio

        task = asyncio.current_task()
        with self._tasks_guard:
            self._tasks.pop(task, None)

    def _live_snapshot(self) -> list:
        with self._tasks_guard:
            return [(loop, task) for task, (loop, _ident)
                    in self._tasks.items()]

    def rotate(self, identity: HouseIdentity, state, join_timeout: float = 5.0):
        """In-process rotation (tests/admin): bump epoch + switch log under
        the cutover lock, then cancel and JOIN the registered live streams.

        Semantics (verified against a real suspended uvicorn connection in
        tests/interop/test_followup_fixes.py): a chunk that already passed
        the send fence BEFORE the cutover may be flushed by the transport
        as the connection aborts, and no frame or checkpoint is PRODUCED
        after the cutover. There are two legitimate terminal outcomes and
        which one a given stream reaches is a race between the two things
        this method does: the stream's own fence may observe the identity
        change and surface the incarnation gap, or the cancellation may
        land first and the task exits having produced nothing further.
        Both close the connection; neither leaks old-generation bytes. A NORMAL return PROVES every captured
        stream task actually exited; if any task fails to exit within the
        join budget this raises CutoverQuiesceTimeout — successful
        quiescence is never advertised on a timeout. The old-generation
        gate is already closed at that point (recoverable post-cutover
        state; re-run rotate after the task exits).
        """
        with self._cutover_lock:
            # A synchronous rotate on a registered stream's own event-loop
            # thread would join a task that is blocked waiting for THIS
            # call to return: refuse it up front instead of deadlocking.
            with self._tasks_guard:
                self_threads = {ident for _loop, ident in self._tasks.values()}
            if threading.get_ident() in self_threads:
                raise RuntimeError(
                    "sync rotate() must not run on a registered stream's"
                    " event-loop thread — the join would wait on the"
                    " calling stream itself. Invoke it from another thread"
                    " (e.g. await asyncio.to_thread(hub.rotate, ...))"
                )
            with self._store.write_tx():
                epoch = int(self._store.get_meta("stream_epoch") or "0")
                self._store.set_meta("stream_epoch", str(epoch + 1))
            live = self._live_snapshot()
            restored = house_mod.restore(self._store, identity, state)
        # Cancellation and joining happen OUTSIDE the cutover lock: the
        # fence is already committed, and a cancelled stream taking the
        # lock for its final identity check must not deadlock the join.
        joins = []
        for loop, task in live:
            done = threading.Event()
            try:
                task.add_done_callback(lambda _task, event=done: event.set())
                loop.call_soon_threadsafe(task.cancel)
            except RuntimeError:  # pragma: no cover - loop already closed
                pass  # the join below reports the stuck task explicitly
            joins.append((loop, task, done))
        deadline = time.monotonic() + join_timeout
        pending: list = []
        for loop, task, done in joins:
            remaining = deadline - time.monotonic()
            if remaining > 0:
                done.wait(remaining)
            # The Event is only a notification channel (its callback runs on
            # the task's loop, which may have stopped); ACTUAL task exit is
            # the proof, and a normal return asserts it for every capture.
            if not task.done():
                pending.append((loop, task))
        if pending:
            raise CutoverQuiesceTimeout(
                f"cutover committed (old-generation gate closed, log rotated"
                f" to {restored.log_incarnation}) but {len(pending)} live"
                f" stream task(s) did not exit within {join_timeout}s;"
                f" re-run rotate after the task exits to re-attempt"
                f" quiesce", pending)
        return restored


def _publicly_deliverable(tag: int) -> bool:
    """House delivery policy, applied AFTER a row has been validated.

    A relation original is a personal event (RELATIONS.md §8): it is owed
    to the two participants and to no public lane. This house refuses one
    at ingress, so no new row can appear; a row numbered into the durable
    log by an earlier build stays exactly where it is — originals and CIDs
    are never rewritten and the log keeps its consecutive numbering — and
    is skipped on every public exit instead.

    Order matters. Validation runs first and unchanged, so genuinely bad
    bytes or a broken index association still raise and still produce the
    proper gap or close: filtering must never launder real corruption into
    a clean-looking stream. A skipped row still advances the scan position,
    so a filtered row never stalls a cursor and never costs a later
    legitimate post its delivery.
    """
    return tag not in wire.RELATION_TAGS


def _validate_public_row(row) -> int:
    """Authoritative row validation before any emission: raw-wire guard AND
    index-association consistency against the signed envelope (CID, routing
    kind, public scopes), then the public privacy predicate. A mismatch is
    an index/consistency failure, never silently skipped by a filtered
    query.

    The raw-wire guard runs first and the privacy predicate last, because
    the two answer different questions. Bad bytes and a broken index
    association are corruption and must raise whatever the row carries.
    Public eligibility is a membership verdict, and for a relation original
    that verdict is permanently "never" — so it is withheld by
    ``_publicly_deliverable`` rather than routed through a predicate that
    would report it as an invalid public row. Consulting the predicate for
    a relation would make a stored relation original close every reader's
    connection the moment the sealed whitelist stops listing tags 20/21,
    which is a permanently stalled cursor rather than a withheld row.
    """
    raw = bytes(row["envelope_bytes"])
    tag = wire.guard_envelope(raw)
    envelope = wire.EventEnvelope.FromString(raw)
    cid = wire.envelope_cid(raw)
    if cid != row["event_id"]:
        raise IndexInconsistent("event_id does not match the envelope CID")
    expected_kind = (envelope.house_event.kind if tag == 34
                     else wire.BODY_TAGS.get(tag, "unknown"))
    if expected_kind != row["kind"]:
        raise IndexInconsistent("kind does not match the envelope body")
    signed_scopes = (list(envelope.house_event.public_scopes) if tag == 34
                     else [])
    if signed_scopes != json.loads(row["scopes"]):
        raise IndexInconsistent("scope association does not match the"
                                " signed envelope")
    if _publicly_deliverable(tag):
        wire.guard_public_structure(raw)
    return tag


class IndexInconsistent(Exception):
    """Durable index row disagrees with the signed envelope it indexes."""



def _sse_event(name: str, payload: bytes) -> str:
    return f"event: {name}\ndata: {wire.b64(payload)}\n\n"


def _sse_frame_with_id(seq: int, payload: bytes) -> str:
    return f"id: {seq}\ndata: {wire.b64(payload)}\n\n"


def _sse_named_with_id(name: str, seq: int, payload: bytes) -> str:
    return f"event: {name}\nid: {seq}\ndata: {wire.b64(payload)}\n\n"


def _build_boundary(log: str, scopes: list[str], high_water: int,
                    full_public: bool) -> bytes:
    boundary = wire.PublicStreamBoundary()
    boundary.log_incarnation = log
    boundary.scopes.extend(scopes)
    boundary.high_water_seq = high_water
    boundary.full_public = full_public
    return boundary.SerializeToString(deterministic=True)


def _build_checkpoint(phase: str, scopes: list[tuple[str, int]],
                      public_through: int | None) -> bytes:
    checkpoint = wire.PublicStreamCheckpoint()
    checkpoint.phase = phase
    for scope, through in scopes:
        entry = checkpoint.scopes.add()
        entry.scope_id = scope
        entry.through_seq = through
    if public_through is not None:
        checkpoint.public_through_seq = public_through
    return checkpoint.SerializeToString(deterministic=True)


def _build_gap(reason: str, lane: str, scope_id: str,
               boundary_bytes: bytes | None) -> bytes:
    gap = wire.PublicStreamGap()
    gap.reason = reason
    gap.lane = lane
    if scope_id:
        gap.scope_id = scope_id
    if boundary_bytes is not None:
        gap.boundary.ParseFromString(boundary_bytes)
    return gap.SerializeToString(deterministic=True)


def _frame_bytes(row) -> bytes:
    frame = wire.WorldStreamFrame()
    frame.seq = int(row["seq"])
    frame.envelope = bytes(row["envelope_bytes"])
    frame.kind = row["kind"]
    frame.scopes.extend(json.loads(row["scopes"]))
    return frame.SerializeToString(deterministic=True)


def _row_selected(row, selection: PublicSelection) -> bool:
    """Union selection: full-public lane OR matching requested scope lane."""
    if selection.public_after is not None and int(row["seq"]) > selection.public_after:
        return True
    scopes = json.loads(row["scopes"])
    for scope in scopes:
        if scope in selection.scope_inputs and int(row["seq"]) > selection.scope_inputs[scope]:
            return True
    return False


def _identify_violation_lane(row, selection: PublicSelection) -> tuple[str, str]:
    """(lane, scope_id) for a violation gap over a specific row.

    The lane is identified from the SIGNED envelope's own scopes (the
    durable index row may itself be the corrupted part).
    """
    try:
        envelope = wire.EventEnvelope.FromString(bytes(row["envelope_bytes"]))
        signed_scopes = list(envelope.house_event.public_scopes)
    except Exception:
        signed_scopes = json.loads(row["scopes"])
    for scope in signed_scopes:
        if scope in selection.scope_inputs:
            return "scope", scope
    if selection.public_after is not None:
        return "public", ""
    return "connection", ""


def _gap_incarnation(hub: StreamHub, selection: PublicSelection) -> str:
    current = hub._store.get_meta("public_log_incarnation") or ""
    high = hub._store.public_log_high_water(current)
    return _sse_event(
        "public_gap",
        _build_gap("log_incarnation_changed", "connection", "",
                   _build_boundary(current, selection.scopes, high, False)),
    )


async def stream_public_events(hub: StreamHub, selection: PublicSelection,
                               registered_scopes: list[str]):
    """Async SSE generator for mode=public-v1. Yields text chunks.

    Every emitted data chunk and checkpoint is fenced immediately before
    the yield (check-to-send against the captured log identity), and this
    generator's task is registered with the hub so a rotation cancels it
    outright (stop/join). Historical rows are re-validated per page — raw
    wire AND durable index association — with the page fully buffered
    before any of it is emitted.
    """
    hub.register_stream()
    try:
        captured = hub.captured_identity()
        current_log = captured[1]

        # The sole exceptional startup gap: requested log differs from actual.
        if selection.log_incarnation != current_log:
            high = hub._store.public_log_high_water(current_log)
            yield _sse_event(
                "public_gap",
                _build_gap("log_incarnation_changed", "connection", "",
                           _build_boundary(current_log, selection.scopes, high,
                                           False)),
            )
            return

        unknown = [s for s in selection.scopes if s not in registered_scopes]
        high_water = hub._store.public_log_high_water(current_log)
        full_public = selection.public_after is not None

        yield _sse_event(
            "public_boundary",
            _build_boundary(current_log, selection.scopes, high_water,
                            full_public),
        )
        if unknown:
            # unknown_scope: boundary first, then the gap; no checkpoint.
            yield _sse_event(
                "public_gap",
                _build_gap("unknown_scope", "scope", unknown[0],
                           _build_boundary(current_log, selection.scopes,
                                           high_water, full_public)),
            )
            return

        floor = hub._store.public_log_floor(current_log)
        # A cursor inside the pruned region (cursor+1 < floor) means
        # retained history no longer covers the requested resume point; a
        # cursor of floor-1 or below-zero simply means "from the beginning".
        if selection.public_after is not None and selection.public_after + 1 < floor:
            yield _sse_event(
                "public_gap",
                _build_gap("history_pruned", "public", "",
                           _build_boundary(current_log, selection.scopes,
                                           high_water, full_public)),
            )
            return
        for scope, position in selection.scope_inputs.items():
            if position > high_water:
                yield _sse_event(
                    "public_gap",
                    _build_gap("cursor_ahead", "scope", scope,
                               _build_boundary(current_log, selection.scopes,
                                               high_water, full_public)),
                )
                return
            if position + 1 < floor:
                yield _sse_event(
                    "public_gap",
                    _build_gap("history_pruned", "scope", scope,
                               _build_boundary(current_log, selection.scopes,
                                               high_water, full_public)),
                )
                return
        if selection.public_after is not None and selection.public_after > high_water:
            yield _sse_event(
                "public_gap",
                _build_gap("cursor_ahead", "public", "",
                           _build_boundary(current_log, selection.scopes,
                                           high_water, full_public)),
            )
            return

        # Index completeness: seqs are allocated consecutively, so a row
        # count below the high water means history was deleted out of the
        # durable log — a consistency gap, never silently skipped.
        count_row = hub._store.query_one(
            "SELECT COUNT(*) AS c FROM public_log WHERE log_incarnation = ?",
            (current_log,),
        )
        if int(count_row["c"]) != high_water:
            yield _sse_event(
                "public_gap",
                _build_gap("publication_index_inconsistent", "connection", "",
                           None),
            )
            return

        # ---------------- replay ---------------------------------------------
        emitted = set()
        outcome: list[int | None] = [None]
        async for chunk in _drain_replay(hub, captured, selection, current_log,
                                         high_water, emitted, outcome):
            yield chunk
        checkpoint_h = outcome[0]
        if checkpoint_h is None:
            return

        # Pre-checkpoint check-to-send: a checkpoint must never certify
        # coverage of a log identity that a completed cutover retired.
        if not hub.identity_valid(captured):
            yield _gap_incarnation(hub, selection)
            return

        yield _sse_event(
            "public_checkpoint",
            _build_checkpoint(
                "replay",
                [(scope, checkpoint_h) for scope in selection.scopes],
                checkpoint_h if full_public else None,
            ),
        )

        # ---------------- live -------------------------------------------------
        last_sent = checkpoint_h
        last_checkpoint_h = checkpoint_h
        last_heartbeat = time.monotonic()
        while True:
            if not hub.identity_valid(captured):
                yield _gap_incarnation(hub, selection)
                return
            rows = hub._store.public_log_page(current_log, last_sent,
                                              selection.limit)
            if rows:
                expected = last_sent + 1
                buffered = []
                failure = None
                for row in rows:
                    if int(row["seq"]) != expected:
                        failure = ("publication_index_inconsistent",
                                   "connection", "")
                        break
                    expected += 1
                    try:
                        tag = _validate_public_row(row)
                    except wire.WireError:
                        lane, scope_id = _identify_violation_lane(row, selection)
                        failure = ("public_log_invalid", lane, scope_id)
                        break
                    except IndexInconsistent:
                        lane, scope_id = _identify_violation_lane(row, selection)
                        failure = ("publication_index_inconsistent",
                                   lane, scope_id)
                        break
                    buffered.append((row, tag))
                if failure is not None:
                    yield _sse_event("public_gap",
                                     _build_gap(*failure, None))
                    return
                # Page fully validated: emit under the send fence.
                for row, tag in buffered:
                    if not hub.identity_valid(captured):
                        yield _gap_incarnation(hub, selection)
                        return
                    if (_publicly_deliverable(tag)
                            and _row_selected(row, selection)
                            and row["event_id"] not in emitted):
                        emitted.add(row["event_id"])
                        yield _sse_event("public_frame", _frame_bytes(row))
                    last_sent = max(last_sent, int(row["seq"]))
            live_high = hub._store.public_log_high_water(current_log)
            if live_high > last_checkpoint_h and last_sent >= live_high:
                # All selected lanes drained to the live high-water mark.
                if not hub.identity_valid(captured):
                    yield _gap_incarnation(hub, selection)
                    return
                last_checkpoint_h = live_high
                yield _sse_event(
                    "public_checkpoint",
                    _build_checkpoint(
                        "live",
                        [(scope, live_high) for scope in selection.scopes],
                        live_high if full_public else None,
                    ),
                )
            if time.monotonic() - last_heartbeat >= HEARTBEAT_SECONDS:
                last_heartbeat = time.monotonic()
                yield ": keepalive\n\n"
            await asyncio.sleep(POLL_SECONDS)
    finally:
        hub.unregister_stream()


async def _drain_replay(hub: StreamHub, captured, selection: PublicSelection,
                        log: str, high_water: int, emitted: set,
                        outcome: list):
    """Emit buffered replay pages up to the captured high-water mark.

    Each page is fetched, checked for seq continuity, and every row is
    validated (raw wire + index association) BEFORE any of it is emitted;
    a failed page withholds its earlier rows (BASELINE.md allowance). On
    success ``outcome[0]`` is the checkpoint position; it stays ``None``
    after a terminal gap.
    """
    floor = hub._store.public_log_floor(log)
    # Replay scans from the LOWEST input position of any selected lane: an
    # older scope lane must still see its history even when the public lane
    # cursor is far ahead (PUBLIC-STREAM.md §4 overlap example).
    inputs = list(selection.scope_inputs.values())
    if selection.public_after is not None:
        inputs.append(selection.public_after)
    start = min(inputs) if inputs else max(floor - 1, 0)
    last = start - 1 if start > 0 else 0
    while last < high_water:
        if not hub.identity_valid(captured):
            yield _gap_incarnation(hub, selection)
            return
        rows = hub._store.public_log_page(log, last, selection.limit)
        if not rows:
            break
        expected = last + 1
        buffered = []
        failure = None
        for row in rows:
            if int(row["seq"]) > high_water:
                break
            if int(row["seq"]) != expected:
                failure = ("publication_index_inconsistent", "connection", "")
                break
            expected += 1
            # Original-wire guard + index association on EVERY retained row
            # before emission.
            try:
                tag = _validate_public_row(row)
            except wire.WireError:
                lane, scope_id = _identify_violation_lane(row, selection)
                failure = ("public_log_invalid", lane, scope_id)
                break
            except IndexInconsistent:
                lane, scope_id = _identify_violation_lane(row, selection)
                failure = ("publication_index_inconsistent", lane, scope_id)
                break
            buffered.append((row, tag))
        if failure is not None:
            yield _sse_event("public_gap", _build_gap(*failure, None))
            return
        # Page fully validated before any of it is emitted; each chunk is
        # fenced immediately before its yield.
        for row, tag in buffered:
            if not hub.identity_valid(captured):
                yield _gap_incarnation(hub, selection)
                return
            if (_publicly_deliverable(tag)
                    and _row_selected(row, selection)
                    and row["event_id"] not in emitted):
                emitted.add(row["event_id"])
                yield _sse_event("public_frame", _frame_bytes(row))
            last = max(last, int(row["seq"]))
        if len(rows) < selection.limit:
            break
    outcome[0] = high_water


async def stream_legacy_events(hub: StreamHub, last_event_id: int):
    """Unqualified legacy lane: old frame grammar, no new control events.

    Applies the same privacy predicate, index validation and original-wire
    guard; an unsafe historical row closes the connection without
    delivering bytes past it.
    """
    hub.register_stream()
    try:
        captured = hub.captured_identity()
        log = captured[1]
        last = int(last_event_id or 0)
        last_heartbeat = time.monotonic()
        while True:
            if not hub.identity_valid(captured):
                return
            rows = hub._store.public_log_page(log, last, 256)
            if rows:
                expected = last + 1
                buffered = []
                unsafe = False
                for row in rows:
                    if int(row["seq"]) != expected:
                        unsafe = True
                        break
                    expected += 1
                    try:
                        tag = _validate_public_row(row)
                    except (wire.WireError, IndexInconsistent):
                        unsafe = True
                        break
                    buffered.append((row, tag))
                if unsafe:
                    return  # legacy grammar: close, no gap event
                for row, tag in buffered:
                    if not hub.identity_valid(captured):
                        return
                    last = int(row["seq"])
                    if not _publicly_deliverable(tag):
                        continue
                    yield _sse_frame_with_id(int(row["seq"]), _frame_bytes(row))
            if time.monotonic() - last_heartbeat >= HEARTBEAT_SECONDS:
                last_heartbeat = time.monotonic()
                yield ": keepalive\n\n"
            await asyncio.sleep(POLL_SECONDS)
    finally:
        hub.unregister_stream()


async def stream_inbox_events(store, identity: HouseIdentity, hub: StreamHub,
                              origin: str, popclaw_id: str, token: str,
                              token_is_v2: bool, last_event_id: int):
    """Private DM stream: named ``envelope`` frames, recipient-isolated.

    Authorization is revalidated before EVERY frame (not per batch): a v2
    token dies with its session/revision (leave, revocation, fence change,
    expiry), and the legacy self-signed lane is only eligible while the
    actor has never used house sessions here (reference security policy)
    and its 60-second window still holds. Invalidation stops delivery and
    closes the stream.
    """
    hub.register_stream()
    try:
        def authorized() -> bool:
            if token_is_v2:
                return sessions_mod.verify_inbox_token(
                    store, identity, origin, token, popclaw_id)
            if sessions_mod.actor_has_session_state(store, popclaw_id):
                return False
            return sessions_mod.verify_legacy_inbox_token(token, popclaw_id)

        if not authorized():
            return

        last = int(last_event_id or 0)
        last_heartbeat = time.monotonic()
        while True:
            # Revalidate authorization EVERY tick, not only when frames are
            # pending: an idle stream whose session was left or whose token
            # expired closes on the next poll instead of heartbeating on.
            if not authorized():
                return
            rows = store.dm_page(popclaw_id, last, 64)
            for row in rows:
                if not authorized():  # per-frame check-to-send
                    return
                last = int(row["seq"])
                yield _sse_named_with_id("envelope", int(row["seq"]),
                                         bytes(row["envelope_bytes"]))
            if time.monotonic() - last_heartbeat >= HEARTBEAT_SECONDS:
                if not authorized():
                    return
                last_heartbeat = time.monotonic()
                yield ": keepalive\n\n"
            await asyncio.sleep(POLL_SECONDS)
    finally:
        hub.unregister_stream()
