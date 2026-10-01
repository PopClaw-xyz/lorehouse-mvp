import { describe, it, expect } from 'vitest';
import { isHouseSessionBoard } from '../src/house-session.js';

const VALID = {
  version: 1,
  endpoint: '/v1/house-session',
  ack_pubkey: 'a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90',
  operations: ['enter', 'renew', 'leave', 'status', 'action'],
};

describe('isHouseSessionBoard (ADR-0049 board validation)', () => {
  it('accepts the canonical v1 board', () => {
    expect(isHouseSessionBoard(VALID)).toBe(true);
  });

  // Codex S0 review, fix 2: a startsWith('/') check accepts
  // protocol-relative and backslash paths that browsers resolve against a
  // DIFFERENT origin. v1 pins the endpoint to the exact protocol constant;
  // any other spelling is a malformed board, not a capability.

  it.each([
    '//other.invalid/v1/house-session', // protocol-relative → cross-origin
    '/\\other.invalid/v1/house-session', // backslash — browsers normalize to //
    '/v1/house-session?x=1', // query
    '/v1/house-session#frag', // fragment
    'https://demo.loreshow.com/v1/house-session', // absolute URL
    '/v1/house-session/', // trailing slash
    '/v1/house-session/../house-session', // dot segments
    'v1/house-session', // not root-relative at all
    '/v1/other-endpoint', // different path
  ])('rejects endpoint %s', (endpoint) => {
    expect(isHouseSessionBoard({ ...VALID, endpoint })).toBe(false);
  });

  it('rejects unknown version, bad pubkey, unknown operations, nonpositive lease', () => {
    expect(isHouseSessionBoard({ ...VALID, version: 2 })).toBe(false);
    expect(isHouseSessionBoard({ ...VALID, ack_pubkey: 'UPPERCASE' })).toBe(false);
    expect(isHouseSessionBoard({ ...VALID, operations: ['teleport'] })).toBe(false);
    expect(isHouseSessionBoard({ ...VALID, operations: [] })).toBe(false);
    expect(isHouseSessionBoard({ ...VALID, lease_seconds: 0 })).toBe(false);
    expect(isHouseSessionBoard(null)).toBe(false);
    expect(isHouseSessionBoard('nope')).toBe(false);
  });
});
