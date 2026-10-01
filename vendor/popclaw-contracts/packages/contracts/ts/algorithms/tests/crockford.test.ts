import { describe, it, expect } from 'vitest';
import { sha256 } from '@noble/hashes/sha256';
import { crockford32Lower, normalizeSigilInput } from '../src/crockford.js';

describe('crockford32Lower', () => {
  it('encodes the full sha256 digest of "BlackFeather"', () => {
    // Known-answer oracle: python crockford32 over sha256("BlackFeather")
    // (see task report for the derivation). Must match the Rust twin.
    const digest = sha256(new TextEncoder().encode('BlackFeather'));
    expect(crockford32Lower(digest)).toBe(
      'gdx8rgtpj9xsrkm2rmeh48pycejzzwhdnj0htzrmgyzcpkgsjdd0'
    );
  });

  it('encodes empty input to empty string', () => {
    expect(crockford32Lower(new Uint8Array(0))).toBe('');
  });

  it('pads the final partial group on the right', () => {
    // 0xff = 11111111 -> groups of 5 MSB-first: 11111 1110(0) -> "z" "w"
    expect(crockford32Lower(new Uint8Array([0xff]))).toBe('zw');
  });
});

describe('normalizeSigilInput', () => {
  it('trims and lowercases', () => {
    expect(normalizeSigilInput('  2FF697AB  ')).toBe('2ff697ab');
  });

  it('folds confusable chars (o->0, i->1, l->1)', () => {
    expect(normalizeSigilInput('O0Il')).toBe('0011');
  });

  it('rejects u and other out-of-alphabet chars', () => {
    expect(normalizeSigilInput('abcu1234')).toBeNull();
  });
});
