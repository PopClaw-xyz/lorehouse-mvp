"""Error taxonomy for PopClaw Ranger Map.

Business error categories are fixed by the design:

- ``invalid_input``      the submitted request does not satisfy the declared
                         schema of this application's resources.
- ``unsupported_action`` the action kind is known but not offered here.
- ``not_found``          the addressed resource does not exist.
- ``storage_unavailable``the local data root cannot serve the request right
                         now (locked, missing, or failing).

Messages must stay understandable but never leak internal paths, stack
traces, keys or the full original request.
"""

from __future__ import annotations


class RangerMapError(Exception):
    """Base class for errors mapped onto HTTP responses."""

    code = "invalid_input"
    http_status = 400


class InvalidInput(RangerMapError):
    code = "invalid_input"
    http_status = 400


class UnsupportedAction(RangerMapError):
    code = "unsupported_action"
    http_status = 400


class NotFound(RangerMapError):
    code = "not_found"
    http_status = 404


class StorageUnavailable(RangerMapError):
    code = "storage_unavailable"
    http_status = 503


class ProtocolAdapterPending(RangerMapError):
    """The PopClaw protocol adapter is not bound yet; writes fail closed.

    This is not a protocol error code from the shared contract. It is this
    reference server honestly reporting that its signed write entrances are
    disabled until the public contract publication closure lands
    (see docs/protocol-bindings.md). Reads keep working.
    """

    code = "protocol_adapter_pending"
    http_status = 503
