"""HTTP surface: read-only map API, comic map page, and the native wire.

Business reads (unchanged from the reference candidate):

- ``GET /``                                       the map page
- ``GET /ranger-map/v1/map``                      snapshot pagination + ETag
- ``GET /ranger-map/v1/footprints``               history by seq descending
- ``GET /ranger-map/v1/footprints/by-event/{id}`` immutable original result
- ``GET /healthz``                                basic health

Native protocol (public-envelope-01.6):

- ``GET  /v1/manifest``                           pinned manifest + signed proof
- ``GET  /v1/guide.md``                           exact pinned guide bytes
- ``GET  /v1/profile/{popclaw_id}``               accepted profile projection
- ``POST /v1/push``                               signed ingress (SignedPayload)
- ``POST /v1/house-session``                      G0 session control (binary)
- ``POST /v1/world-actions/status``               signed status reads
- ``GET  /v1/world-stream[?mode=public-v1]``      public SSE (new + legacy lane)
- ``GET  /inbox/{popclaw_id}/stream``             private DM SSE

Guards: request bodies are capped (128 KiB default, the 1.5 MiB envelope
limit on push); query limits/cursors are strictly validated and never spliced into
SQL.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import sqlite3
from pathlib import Path

from google.protobuf.message import DecodeError
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import (
    FileResponse,
    JSONResponse,
    Response,
    StreamingResponse,
)
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from . import actions as actions_mod
from . import house as house_mod
from . import ingress as ingress_mod
from . import identity_read
from . import relation_reads
from . import sessions as sessions_mod
from . import streams as streams_mod
from . import wire
from .check_in import BASE58_PATTERN, EVENT_ID_PATTERN, RANGER_ID_MAX_LENGTH
from .errors import InvalidInput, NotFound, RangerMapError, StorageUnavailable

MAX_REQUEST_BODY_BYTES = 128 * 1024
PUSH_MAX_REQUEST_BODY_BYTES = ingress_mod.WRAPPER_MAX_BYTES

MAP_DEFAULT_LIMIT = 100
MAP_MAX_LIMIT = 200
HISTORY_DEFAULT_LIMIT = 20
HISTORY_MAX_LIMIT = 100
CURSOR_MAX_CHARS = 512


def error_response(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}},
                        status_code=status)


# ---------------------------------------------------------------------------
# Body cap middleware (pure ASGI; streams are accumulated with a limit)


class RequestBodyLimit:
    """Reject any request whose body exceeds the route's cap (413)."""

    def __init__(self, app, max_bytes: int = MAX_REQUEST_BODY_BYTES) -> None:
        self.app = app
        self.max_bytes = max_bytes

    def _limit_for(self, scope) -> int:
        path = scope.get("path", "")
        if path == "/v1/push":
            return PUSH_MAX_REQUEST_BODY_BYTES
        return self.max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        limit = self._limit_for(scope)

        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        declared = headers.get(b"content-length")
        if declared is not None:
            try:
                if int(declared) > limit:
                    response = error_response(
                        "invalid_input",
                        f"request body exceeds {limit} bytes",
                        413,
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass  # handled while reading the stream below

        body = bytearray()
        overflow = False
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] == "http.request":
                body.extend(message.get("body", b""))
                if len(body) > limit:
                    overflow = True
                    break
                if not message.get("more_body", False):
                    break
        if overflow:
            response = error_response(
                "invalid_input",
                f"request body exceeds {limit} bytes",
                413,
            )
            await response(scope, receive, send)
            return

        payload = bytes(body)
        replayed = False

        async def replay_receive():
            # Replay the buffered body exactly once, then forward the live
            # receive so disconnects and any further messages reach the app.
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": payload, "more_body": False}
            return await receive()

        await self.app(scope, replay_receive, send)


# ---------------------------------------------------------------------------
# Query helpers (strict; nothing is ever spliced into SQL)


def parse_limit(request: Request, default: int, maximum: int) -> int:
    raw = request.query_params.get("limit")
    if raw is None or raw == "":
        return default
    if not re.fullmatch(r"[0-9]{1,9}", raw):
        raise InvalidInput(f"limit must be an integer between 1 and {maximum}")
    value = int(raw)
    if not 1 <= value <= maximum:
        raise InvalidInput(f"limit must be an integer between 1 and {maximum}")
    return value


def parse_before(request: Request) -> int | None:
    raw = request.query_params.get("before")
    if raw is None or raw == "":
        return None
    if not re.fullmatch(r"[0-9]{1,18}", raw) or int(raw) < 1:
        raise InvalidInput("before must be a positive integer seq (exclusive)")
    return int(raw)


def parse_ranger_id(request: Request) -> str | None:
    raw = request.query_params.get("ranger_id")
    if raw is None or raw == "":
        return None
    if len(raw) > RANGER_ID_MAX_LENGTH or not BASE58_PATTERN.match(raw):
        raise InvalidInput("ranger_id must be a base58 public identity")
    return raw


def encode_cursor(as_of_seq: int, after_ranger_id: str) -> str:
    payload = json.dumps(
        {"v": 1, "as_of_seq": as_of_seq, "after_ranger_id": after_ranger_id},
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")


def decode_cursor(token: str) -> tuple[int, str]:
    if not 1 <= len(token) <= CURSOR_MAX_CHARS:
        raise InvalidInput("cursor is malformed")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise InvalidInput("cursor is malformed")
    padded = token + "=" * (-len(token) % 4)
    try:
        payload = base64.b64decode(padded, altchars=b"-_", validate=True)
        document = json.loads(payload.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, ValueError):
        raise InvalidInput("cursor is malformed") from None
    if not isinstance(document, dict) or set(document) != {
        "v", "as_of_seq", "after_ranger_id"
    }:
        raise InvalidInput("cursor is malformed")
    as_of_seq = document["as_of_seq"]
    after = document["after_ranger_id"]
    if document["v"] != 1 or isinstance(as_of_seq, bool) or not isinstance(as_of_seq, int):
        raise InvalidInput("cursor is malformed")
    if not 1 <= as_of_seq:
        raise InvalidInput("cursor is malformed")
    if (
        not isinstance(after, str)
        or not 1 <= len(after) <= RANGER_ID_MAX_LENGTH
        or not BASE58_PATTERN.match(after)
    ):
        raise InvalidInput("cursor is malformed")
    return as_of_seq, after


def snapshot_etag(as_of_seq: int, query_string: bytes) -> str:
    digest = hashlib.sha256(
        b"ranger-map/v1/map|" + str(as_of_seq).encode() + b"|" + query_string
    ).hexdigest()[:24]
    return f'"map1-{digest}"'


# ---------------------------------------------------------------------------
# Business read endpoints (reference candidate, unchanged)


async def homepage(request: Request) -> Response:
    index = Path(request.app.state.static_root) / "index.html"
    return FileResponse(index, media_type="text/html")


async def map_endpoint(request: Request) -> Response:
    store = request.app.state.store
    limit = parse_limit(request, MAP_DEFAULT_LIMIT, MAP_MAX_LIMIT)
    cursor_token = request.query_params.get("cursor") or None
    if cursor_token is not None:
        as_of_seq, after_ranger_id = decode_cursor(cursor_token)
        if as_of_seq > store.max_seq():
            raise InvalidInput("cursor refers to a snapshot that does not exist")
    else:
        as_of_seq, after_ranger_id = None, None

    page = store.map_snapshot_page(as_of_seq, after_ranger_id, limit)

    etag = snapshot_etag(page.as_of_seq, request.scope.get("query_string", b""))
    if_none_match = request.headers.get("if-none-match")
    headers = {"ETag": etag, "Cache-Control": "no-cache"}
    if if_none_match and etag in (candidate.strip() for candidate in if_none_match.split(",")):
        return Response(status_code=304, headers=headers)

    next_cursor = None
    if page.has_more and page.items:
        next_cursor = encode_cursor(page.as_of_seq, page.items[-1].ranger_id)
    return JSONResponse(
        {
            "as_of_seq": str(page.as_of_seq),
            "ranger_count": page.ranger_count,
            "footprint_count": page.footprint_count,
            "items": [fp.to_json_dict() for fp in page.items],
            "next_cursor": next_cursor,
        },
        headers=headers,
    )


async def footprints_endpoint(request: Request) -> Response:
    store = request.app.state.store
    limit = parse_limit(request, HISTORY_DEFAULT_LIMIT, HISTORY_MAX_LIMIT)
    before = parse_before(request)
    ranger_id = parse_ranger_id(request)
    page = store.history_page(before=before, ranger_id=ranger_id, limit=limit)
    return JSONResponse(
        {
            "items": [fp.to_json_dict() for fp in page.items],
            "next_before": str(page.next_before) if page.next_before is not None else None,
        }
    )


async def by_event_endpoint(request: Request) -> Response:
    store = request.app.state.store
    event_id = request.path_params["event_id"]
    if not isinstance(event_id, str) or not EVENT_ID_PATTERN.match(event_id):
        raise InvalidInput("event_id must be 64 lowercase hex characters")
    footprint = store.footprint_by_event(event_id)
    if footprint is None:
        raise NotFound("no accepted check-in exists for this event_id")
    return JSONResponse(footprint.to_json_dict())


async def healthz(request: Request) -> Response:
    store = request.app.state.store
    try:
        version = store.schema_version()
        with store._guard:  # basic readability probe
            store._connection.execute("SELECT 1").fetchone()
    except StorageUnavailable:
        raise
    except Exception as exc:
        raise StorageUnavailable("the local database is not readable") from exc
    return JSONResponse(
        {"status": "ok", "database": "ok", "schema_version": version}
    )


# ---------------------------------------------------------------------------
# Native protocol endpoints


def _require_house(request: Request):
    identity = getattr(request.app.state, "identity", None)
    state = getattr(request.app.state, "house_state", None)
    if identity is None or state is None:
        raise StorageUnavailable("the house protocol layer is not initialised")
    return identity, state


async def manifest_endpoint(request: Request) -> Response:
    identity, state = _require_house(request)
    proof = house_mod.manifest_proof_bytes(identity, state)
    return Response(
        content=state.manifest_bytes,
        media_type="application/json",
        headers={
            "X-Popclaw-Manifest-Proof": wire.b64(proof),
            "Cache-Control": "no-cache",
        },
    )


async def guide_endpoint(request: Request) -> Response:
    _identity, state = _require_house(request)
    return Response(content=state.guide_bytes, media_type="text/markdown")


def _profile_sigil(popclaw_id: str, length: int = 8) -> str:
    """Existing public algorithm: first eight lowercase Crockford SHA256 digits."""
    alphabet = "0123456789abcdefghjkmnpqrstvwxyz"
    digest = hashlib.sha256(popclaw_id.encode("utf-8")).digest()
    prefix = int.from_bytes(digest, "big")
    return "".join(alphabet[(prefix >> (256 - 5 * (i + 1))) & 31] for i in range(length))


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate stored card field")
        result[key] = value
    return result


def _profile_card(card_json: str) -> dict:
    """Translate the complete stored projection; never synthesize empty fields.

    Reject unrepresentable rows rather than discarding unknown/future content
    or making a partial row look safe for a client's whole-row rename.
    Identity and event metadata belong to the row, never to this card.
    """
    strings = {"nickname", "one_line_intro", "role_persona", "location_hint",
               "avatar_uri"}
    try:
        card = json.loads(card_json, object_pairs_hook=_unique_json_object)
        if not isinstance(card, dict) or set(card) != strings | {"taste_tags", "declared_at"}:
            raise ValueError("incomplete or unknown stored card vocabulary")
        if any(not isinstance(card[key], str) for key in strings):
            raise ValueError("wrong stored string type")
        tags = card["taste_tags"]
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            raise ValueError("wrong stored tag type")
        seconds = card["declared_at"]
        # JSON numbers must retain the exact integer in the JS client. Reject
        # out-of-range milliseconds, bools, floats and numeric strings.
        if type(seconds) is not int or abs(seconds * 1000) > 2**53 - 1:
            raise ValueError("stored timestamp is not exactly representable")
    except (TypeError, ValueError) as exc:
        raise StorageUnavailable("the stored profile card cannot be represented") from exc
    card.pop("declared_at")
    card["declared_at_ms"] = seconds * 1000
    # This build rejects reserved Profile field 8 at admission. An unexpected
    # stored payout field is rejected above, never replaced by this empty list.
    card["payout_addresses"] = []
    return card


def _profile_counts(store, popclaw_id: str) -> tuple[int, int]:
    """House-local, CID-deduplicated Post and received Reply envelope counts.

    Replies are attributed by the signed in_reply_to.author_popclaw_id, not
    by the sender or inferred from text. No external-post resolution is added.
    The actor index serves posts; replies require a local scan and decode.
    """
    posts = store.query_one(
        "SELECT COUNT(*) AS count FROM accepted_envelopes"
        " WHERE actor_id = ? AND body_tag = 27 AND public_eligible = 1",
        (popclaw_id,),
    )["count"]
    replies = 0
    for row in store.query_all(
        "SELECT envelope_bytes FROM accepted_envelopes"
        " WHERE body_tag = 25 AND public_eligible = 1"
    ):
        envelope = wire.EventEnvelope.FromString(row["envelope_bytes"])
        if envelope.WhichOneof("body") != "reply":
            raise StorageUnavailable("the stored reply index cannot be represented")
        if envelope.reply.in_reply_to.author_popclaw_id == popclaw_id:
            replies += 1
    return posts, replies


async def profile_endpoint(request: Request) -> Response:
    popclaw_id = request.path_params["popclaw_id"]
    store = request.app.state.store
    try:
        wire.key_bytes_from_popclaw_id(popclaw_id)
    except ValueError:
        raise InvalidInput("popclaw_id must decode to a 32-byte key") from None
    try:
        row = store.query_one(
            "SELECT card_json FROM profiles WHERE ranger_id = ?", (popclaw_id,)
        )
        card = _profile_card(row["card_json"]) if row is not None else None
        posts, replies = _profile_counts(store, popclaw_id)
    except (sqlite3.Error, DecodeError) as exc:
        raise StorageUnavailable("the local profile database is not readable") from exc
    # Absence is an explicit answer inside a complete HTTP wrapper. Only a
    # genuinely absent row omits card; invalid IDs and unreadable rows fail.
    identity = getattr(request.app.state, 'identity', None)
    try:
        followers = store.query_one('SELECT COUNT(*) n FROM relation_edges '
                                    'WHERE house_key=? AND followee=? AND state=\'active\'',
                                    (identity.house_key_id, popclaw_id))['n'] if identity else 0
    except sqlite3.Error as exc:
        raise StorageUnavailable('the local relation projection is not readable') from exc
    body = {"popclaw_id": popclaw_id, "sigil": _profile_sigil(popclaw_id),
            "profiles": [], "house_follower_count": followers,
            "house_post_count": posts, "house_reply_received_count": replies}
    if card is not None:
        body["card"] = card
    return JSONResponse(body)


async def resolve_endpoint(request: Request) -> Response:
    """Current-client directory binding over actual public Profile rows.

    No session, follow or name string manufactures a verified account. Read
    errors remain failures rather than an apparently successful empty roster.
    """
    sigil = request.query_params.get("sigil", "").strip().lower()
    name = request.query_params.get("name", "").strip()
    if sigil:
        sigil = sigil.translate(str.maketrans({"o": "0", "i": "1", "l": "1"}))
        if not 6 <= len(sigil) <= 12 or any(c not in "0123456789abcdefghjkmnpqrstvwxyz" for c in sigil):
            raise InvalidInput("sigil must be 6..12 Crockford digits")
    elif not name:
        raise InvalidInput("provide sigil or name")
    candidates = []
    try:
        with request.app.state.store.read_tx():
            rows = request.app.state.store.query_all(
                "SELECT ranger_id, card_json FROM profiles ORDER BY ranger_id")
            for row in rows:
                card = _profile_card(row["card_json"])
                try:
                    wire.key_bytes_from_popclaw_id(row["ranger_id"])
                except ValueError as exc:
                    raise StorageUnavailable("the stored profile identity is invalid") from exc
                short = _profile_sigil(row["ranger_id"])
                if sigil:
                    # Match the requested prefix length; display eight digits.
                    matches = _profile_sigil(row["ranger_id"], max(8, len(sigil))).startswith(sigil)
                else:
                    matches = name.casefold() in card["nickname"].casefold()
                if matches:
                    candidates.append({"popclaw_id": row["ranger_id"],
                                       "nickname": card["nickname"],
                                       "sigil": short, "profiles": []})
    except sqlite3.Error as exc:
        raise StorageUnavailable("the local profile directory is not readable") from exc
    candidates.sort(key=lambda c: (c["nickname"].casefold() != name.casefold(),
                                   c["nickname"].casefold(), c["popclaw_id"]))
    return JSONResponse({"candidates": candidates[:256]})


async def push_endpoint(request: Request) -> Response:
    identity, state = _require_house(request)
    body = await request.body()
    outcome = ingress_mod.handle_push(request.app.state.store, identity, state, body)
    return JSONResponse(outcome.to_json(), status_code=outcome.http_status)


async def house_session_endpoint(request: Request) -> Response:
    identity, state = _require_house(request)
    body = await request.body()
    try:
        decision = sessions_mod.handle_session_request(
            request.app.state.store, identity, state, body
        )
    except sessions_mod.SessionRejected as exc:
        return error_response("invalid_input", str(exc), exc.http_status)
    return Response(content=decision.ack_bytes,
                    media_type="application/x-protobuf")


async def action_status_endpoint(request: Request) -> Response:
    identity, state = _require_house(request)
    body = await request.body()
    status, payload = actions_mod.handle_status(
        request.app.state.store, identity, state, body
    )
    media = "application/x-protobuf" if status == 200 else "application/json"
    return Response(content=payload, media_type=media, status_code=status)


async def world_stream_endpoint(request: Request) -> Response:
    hub: streams_mod.StreamHub = request.app.state.hub
    if "mode" in request.query_params:
        try:
            selection = streams_mod.parse_public_request(
                request.query_params,
                request.app.state.house_state.registered_scopes,
                hub.captured_identity()[1],
            )
        except streams_mod.StreamRequestError as exc:
            return error_response("invalid_input", exc.message, 400)
        generator = streams_mod.stream_public_events(
            hub, selection, request.app.state.house_state.registered_scopes)
    else:
        try:
            last_id = int(request.headers.get("last-event-id") or "0")
        except ValueError:
            return error_response("invalid_input", "Last-Event-ID malformed", 400)
        generator = streams_mod.stream_legacy_events(hub, last_id)

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def inbox_stream_endpoint(request: Request) -> Response:
    identity = getattr(request.app.state, 'identity', None)
    _state = getattr(request.app.state, 'house_state', None)
    if identity is None or _state is None or not _state.origin:
        return error_response('read_authority_unavailable', 'the read audience is unavailable', 503)
    hub: streams_mod.StreamHub = request.app.state.hub
    popclaw_id = request.path_params["popclaw_id"]
    try:
        wire.key_bytes_from_popclaw_id(popclaw_id)
    except ValueError:
        raise InvalidInput("popclaw_id must decode to a 32-byte key") from None
    token = request.headers.get("x-popclaw-inbox-token", "")
    if not token:
        return error_response(
            "invalid_input",
            "an x-popclaw-inbox-token header is required", 401)
    token_is_session = token.startswith("itk-")
    # Authenticate before the stream starts; the generator revalidates
    # before EVERY frame (leave/revocation/expiry stop delivery mid-stream).
    if token_is_session:
        if not sessions_mod.verify_inbox_token(request.app.state.store,
                                               identity, _state.origin, token,
                                               popclaw_id):
            return error_response("invalid_input",
                                  "inbox token is not valid for this recipient", 401)
    else:
        status = identity_read.inbox_status(request.app.state.store, token, identity,
                                           _state.origin, popclaw_id)
        if status != 200:
            return error_response('invalid_input', 'identity inbox read refused', status)
    last_id = request.headers.get("last-event-id") or ""

    generator = streams_mod.stream_inbox_events(
        request.app.state.store, identity, hub, _state.origin, popclaw_id,
        token, token_is_session, last_id,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def protocol_unsupported(request: Request) -> Response:
    return error_response(
        "unsupported_action",
        "this optional protocol capability is not implemented by this house",
        404,
    )


# ---------------------------------------------------------------------------
# App factory


def create_app(store, static_root: Path | str | None = None,
               identity=None, house_state=None, hub=None) -> Starlette:
    if static_root is None:
        static_root = Path(__file__).parent / "static"
    static_root = Path(static_root)

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app):
        yield
        store.close()  # release the data-root lock on clean shutdown

    app = Starlette(
        lifespan=lifespan,
        routes=[
            Route("/", homepage, methods=["GET"]),
            Mount("/static", StaticFiles(directory=str(static_root)), name="static"),
            Route("/ranger-map/v1/map", map_endpoint, methods=["GET"]),
            Route("/ranger-map/v1/footprints", footprints_endpoint, methods=["GET"]),
            Route("/ranger-map/v1/footprints/by-event/{event_id}", by_event_endpoint,
                  methods=["GET"]),
            Route("/healthz", healthz, methods=["GET"]),
            Route("/v1/manifest", manifest_endpoint, methods=["GET"]),
            Route("/v1/guide.md", guide_endpoint, methods=["GET"]),
            Route("/v1/profile/{popclaw_id}", profile_endpoint, methods=["GET"]),
            Route("/v1/resolve", resolve_endpoint, methods=["GET"]),
            Route("/v1/relation-snapshot", relation_reads.snapshot, methods=["GET"]),
            Route("/v1/relation-evidence/{event_id}", relation_reads.evidence, methods=["GET"]),
            Route("/followers/{popclaw_id}", relation_reads.relation_list, methods=["GET"]),
            Route("/follows/{popclaw_id}", relation_reads.relation_list, methods=["GET"]),
            Route("/v1/push", push_endpoint, methods=["POST"]),
            Route("/v1/house-session", house_session_endpoint, methods=["POST"]),
            Route("/v1/world-actions/status", action_status_endpoint, methods=["POST"]),
            Route("/v1/world-stream", world_stream_endpoint, methods=["GET"]),
            Route("/inbox/{popclaw_id}/stream", inbox_stream_endpoint, methods=["GET"]),
        ],
        middleware=[Middleware(RequestBodyLimit)],
        exception_handlers={
            RangerMapError: _ranger_map_error,
            HTTPException: _http_exception,
            Exception: _unhandled_error,
        },
    )
    app.state.store = store
    app.state.static_root = static_root
    app.state.identity = identity
    app.state.house_state = house_state
    app.state.hub = hub or streams_mod.StreamHub(store)
    return app


async def _ranger_map_error(request: Request, exc: RangerMapError) -> JSONResponse:
    return error_response(exc.code, str(exc), exc.http_status)


async def _http_exception(request: Request, exc: HTTPException) -> Response:
    path = request.url.path
    if path.startswith("/ranger-map/") or path.startswith("/v1/") or path == "/healthz":
        code = "not_found" if exc.status_code == 404 else "invalid_input"
        if exc.status_code == 405:
            code = "unsupported_action"
        return error_response(code, exc.detail or "request is not supported",
                              exc.status_code)
    return Response(content=exc.detail or "", status_code=exc.status_code)


async def _unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    # Never leak internals; the server log keeps the real traceback.
    return error_response("storage_unavailable",
                          "the server could not complete the request", 503)
