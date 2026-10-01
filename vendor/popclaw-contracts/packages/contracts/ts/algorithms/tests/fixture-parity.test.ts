import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import nacl from 'tweetnacl';
import { cidFromCanonical } from '../src/cid.js';
import { sigil } from '../src/sigil.js';

const FIXTURES_PATH = resolve(__dirname, '../../../fixtures/test-vectors.json');

type Vectors = {
  canonical_serialization: Array<{
    name: string;
    canonical_bytes_hex: string;
    cid: string;
  }>;
  sigil: Array<{
    popclaw_id: string;
    length: number;
    expected: string;
  }>;
  signature_roundtrip: Array<{
    name: string;
    master_private_key_hex: string;
    master_public_key_hex: string;
    canonical_bytes_hex: string;
    signature_hex: string;
  }>;
};

function fromHex(hex: string): Uint8Array {
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.substr(i * 2, 2), 16);
  return out;
}

function toHex(bytes: Uint8Array): string {
  let s = '';
  for (const b of bytes) s += b.toString(16).padStart(2, '0');
  return s;
}

const vectors: Vectors = JSON.parse(readFileSync(FIXTURES_PATH, 'utf-8'));

describe('fixture parity', () => {
  describe('cid_from_canonical', () => {
    for (const v of vectors.canonical_serialization) {
      it(`cid matches for ${v.name}`, () => {
        const canonical = fromHex(v.canonical_bytes_hex);
        expect(cidFromCanonical(canonical)).toBe(v.cid);
      });
    }
  });

  describe('sigil', () => {
    for (const v of vectors.sigil) {
      it(`sigil(${v.popclaw_id}, ${v.length}) = ${v.expected}`, () => {
        expect(sigil(v.popclaw_id, v.length)).toBe(v.expected);
      });
    }
  });

  describe('signature roundtrip', () => {
    for (const v of vectors.signature_roundtrip) {
      it(`verifies signature for ${v.name}`, () => {
        const seed = fromHex(v.master_private_key_hex);
        const kp = nacl.sign.keyPair.fromSeed(seed);
        expect(toHex(kp.publicKey)).toBe(v.master_public_key_hex);

        const canonical = fromHex(v.canonical_bytes_hex);
        const sig = fromHex(v.signature_hex);
        const ok = nacl.sign.detached.verify(canonical, sig, kp.publicKey);
        expect(ok).toBe(true);

        // Also: re-sign and expect byte-identical output (tweetnacl is deterministic).
        const ourSig = nacl.sign.detached(canonical, kp.secretKey);
        expect(toHex(ourSig)).toBe(v.signature_hex);
      });
    }
  });
});
