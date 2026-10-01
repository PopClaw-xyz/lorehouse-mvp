// Optional house_session manifest declaration for per-house login/logout control. A
// missing declaration identifies a legacy house: new login reports
// HOUSE_LIFECYCLE_UNSUPPORTED and must not claim remote session guarantees. JSON keys
// use snake_case consistently with other manifest fields and the Rust representation.

/**
 * Session-control capabilities advertised in the house manifest.
 */
export interface HouseSessionBoard {
  /**
 * Structure version, currently 1. Treat unknown versions as unsupported; do not guess
 * field semantics.
 */
  version: number;
  /**
 * Control endpoint at the fixed house origin: /v1/house-session.
 */
  endpoint: string;
  /**
 * Ed25519 server acknowledgement public key, encoded as 64 lowercase hex characters; used
 * to verify ACKs.
 */
  ack_pubkey: string;
  /**
 * Supported operations: enter, renew, leave, status, and the restricted fixture action.
 */
  operations: readonly string[];
  /**
 * Lease duration in seconds; when absent, the client uses its default (90 seconds
 * recommended).
 */
  lease_seconds?: number;
  /**
 * Suggested renewal interval in seconds; when absent, the client uses its default (30
 * seconds recommended).
 */
  renew_interval_seconds?: number;
}

const KNOWN_OPERATIONS = ['enter', 'renew', 'leave', 'status', 'action'] as const;

/**
 * The v1 control endpoint is this exact path. Merely requiring a leading slash permits
 * dangerous protocol-relative or backslash variants; query and fragment variants are also
 * rejected. Changing the endpoint requires a new manifest structure version, rather than
 * negotiation within v1.
 */
export const HOUSE_SESSION_ENDPOINT_V1 = '/v1/house-session';

/**
 * Validate the entire declaration. Any invalid field returns false; callers report
 * HOUSE_LIFECYCLE_UNSUPPORTED rather than inferring capabilities from a partial
 * declaration.
 */
export function isHouseSessionBoard(value: unknown): value is HouseSessionBoard {
  if (typeof value !== 'object' || value === null) return false;
  const board = value as Record<string, unknown>;
  if (board.version !== 1) return false;
  if (board.endpoint !== HOUSE_SESSION_ENDPOINT_V1) return false;
  if (typeof board.ack_pubkey !== 'string' || !/^[0-9a-f]{64}$/.test(board.ack_pubkey)) {
    return false;
  }
  if (!Array.isArray(board.operations) || board.operations.length === 0) return false;
  for (const op of board.operations) {
    if (typeof op !== 'string' || !(KNOWN_OPERATIONS as readonly string[]).includes(op)) {
      return false;
    }
  }
  for (const key of ['lease_seconds', 'renew_interval_seconds'] as const) {
    const v = board[key];
    if (v !== undefined && (typeof v !== 'number' || !Number.isInteger(v) || v <= 0)) {
      return false;
    }
  }
  return true;
}
