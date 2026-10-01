import { describe, it, expect } from 'vitest';
import { cidFromCanonical } from '../src/cid.js';

describe('cidFromCanonical', () => {
  it('SHA-256("") = e3b0c442...', () => {
    expect(cidFromCanonical(new Uint8Array(0))).toBe(
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    );
  });

  it('lowercase hex 64 chars', () => {
    const cid = cidFromCanonical(new TextEncoder().encode('hello'));
    expect(cid).toHaveLength(64);
    expect(cid).toMatch(/^[0-9a-f]{64}$/);
  });
});
