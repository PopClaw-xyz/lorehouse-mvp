import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import nacl from 'tweetnacl';
import bs58 from 'bs58';
import { popclaw } from '@popclaw/contracts';
import {
  REQUEST_DOMAIN,
  ACK_DOMAIN,
  canonicalRequestCore,
  canonicalAckCore,
  requestSigningInput,
  ackSigningInput,
} from '../src/house-session.js';
import { cidFromCanonical } from '../src/cid.js';

const FIXTURES_PATH = resolve(__dirname, '../../../fixtures/test-vectors.json');

type RequestCoreFixture = {
  name: string;
  core: Record<string, unknown>;
  canonical_bytes_hex: string;
  cid: string;
  signer_seed_hex: string;
  signer_pubkey_hex: string;
  signing_input_hex: string;
  signature_hex: string;
  explicit_defaults?: boolean;
  expect_signer_match?: boolean;
};

type AckCoreFixture = RequestCoreFixture;

type SequenceFixture = {
  name: string;
  description: string;
  steps: Array<{
    op: string;
    op_seq: number;
    request_id: string;
    installation_id: string;
    delivery: 'first' | 'replay';
    expected_outcome: string;
    expected_error_code?: string;
  }>;
};

type Vectors = {
  house_session: {
    requests: RequestCoreFixture[];
    acks: AckCoreFixture[];
    sequences: SequenceFixture[];
  };
};

const vectors: Vectors = JSON.parse(readFileSync(FIXTURES_PATH, 'utf-8'));

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

const ns = (popclaw as unknown as {
  housesession: {
    Operation: Record<string, number>;
    Outcome: Record<string, number>;
    ErrorCode: Record<string, number>;
    RequestCore: {
      decode(bytes: Uint8Array): Record<string, unknown>;
      fromObject(value: Record<string, unknown>): Record<string, unknown>;
    };
    AckCore: {
      decode(bytes: Uint8Array): Record<string, unknown>;
      fromObject(value: Record<string, unknown>): Record<string, unknown>;
    };
  };
}).housesession;

/**
 * Map fixture wire names (snake_case) and enum names to protobufjs objects.
 */
function toRequestObject(fixtureCore: Record<string, unknown>): Record<string, unknown> {
  return {
    operation: ns.Operation[fixtureCore.operation as string],
    popclawId: fixtureCore.popclaw_id,
    installationId: fixtureCore.installation_id,
    opSeq: fixtureCore.op_seq,
    requestId: fixtureCore.request_id,
    houseOrigin: fixtureCore.house_origin,
    issuedAt: fixtureCore.issued_at,
    expiresAt: fixtureCore.expires_at,
    nonce: fixtureCore.nonce,
    expectedHouseRevision: fixtureCore.expected_house_revision ?? 0,
    targetSessionId: fixtureCore.target_session_id ?? '',
  };
}

function toAckObject(fixtureCore: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {
    houseOrigin: fixtureCore.house_origin,
    popclawId: fixtureCore.popclaw_id,
    installationId: fixtureCore.installation_id,
    requestId: fixtureCore.request_id,
    opSeq: fixtureCore.op_seq,
    operation: ns.Operation[fixtureCore.operation as string],
    outcome: ns.Outcome[fixtureCore.outcome as string],
    errorCode: fixtureCore.error_code ? ns.ErrorCode[fixtureCore.error_code as string] : 0,
    houseRevision: fixtureCore.house_revision,
    sessionId: fixtureCore.session_id ?? '',
    sessionActive: fixtureCore.session_active ?? false,
    leaseExpiresAt: fixtureCore.lease_expires_at ?? 0,
    serverCommittedAt: fixtureCore.server_committed_at ?? 0,
    status: undefined,
    detail: fixtureCore.detail ?? '',
  };
  if (fixtureCore.status) {
    const s = fixtureCore.status as Record<string, unknown>;
    out.status = {
      sessionId: s.session_id,
      houseRevision: s.house_revision,
      leaseExpiresAt: s.lease_expires_at,
      installationId: s.installation_id,
      enteredOpSeq: s.entered_op_seq,
    };
  }
  return out;
}

describe('house_session contract vectors', () => {
  it('domain separators are fixed-length and distinct', () => {
    expect(REQUEST_DOMAIN).toBe('POPCLAW_HOUSE_SESSION_REQUEST_V1');
    expect(ACK_DOMAIN).toBe('POPCLAW_HOUSE_SESSION_ACK_V1');
    expect(REQUEST_DOMAIN).not.toBe(ACK_DOMAIN);
  });

  // --- decoded-message canonicalization (Codex S0 review, fix 1) ---
  // pbjs decode assigns an explicit on-wire zero as a Long instance, not a
  // JS number; a canonicalizer that treats Long as a nested message keeps
  // junk keys and emits bytes prost never would. These regressions pin the
  // decoded path against exactly that.

  it('explicit zero varint field (Long(0)) elides from canonical bytes', () => {
    const decoded = ns.RequestCore.decode(new Uint8Array([0x50, 0x00]));
    expect(toHex(canonicalRequestCore(decoded as Record<string, unknown>))).toBe('');
  });

  it('AckCore with an explicit zero revision inside status stays an empty message', () => {
    const decoded = ns.AckCore.decode(new Uint8Array([0x72, 0x02, 0x10, 0x00]));
    expect(toHex(canonicalAckCore(decoded as Record<string, unknown>))).toBe('7200');
  });

  it('empty status message presence survives decode→canonicalize', () => {
    const decoded = ns.AckCore.decode(new Uint8Array([0x72, 0x00]));
    expect(toHex(canonicalAckCore(decoded as Record<string, unknown>))).toBe('7200');
  });

  it('non-zero 64-bit value > 2^53 survives decode→canonicalize without precision loss', () => {
    // op_seq = 2^60 = 1152921504606846976: tag 0x20 + varint (0x80 ×8, 0x10).
    const wire = new Uint8Array([
      0x20, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x10,
    ]);
    const decoded = ns.RequestCore.decode(wire);
    expect((decoded as Record<string, unknown>).opSeq).toBeTruthy();
    expect(toHex(canonicalRequestCore(decoded as Record<string, unknown>))).toBe(toHex(wire));
    // And re-decoding the canonical output yields the same exact value.
    const round = ns.RequestCore.decode(
      canonicalRequestCore(decoded as Record<string, unknown>)
    );
    expect((round as unknown as { opSeq: { toString(): string } }).opSeq.toString()).toBe(
      '1152921504606846976'
    );
  });

  it('fromObject with a Long-shaped op_seq encodes exactly (no number round-trip)', () => {
    const fromObj = ns.RequestCore.fromObject({
      operation: 1,
      opSeq: { low: 0, high: 268435456, unsigned: true }, // 2^60
    });
    // operation(1) emits tag 0x08 0x01; op_seq emits tag 0x20 + 2^60 varint.
    expect(toHex(canonicalRequestCore(fromObj))).toBe('080120808080808080808010');
  });

  describe('requests', () => {
    for (const v of vectors.house_session.requests) {
      it(`canonical bytes + signing input + signature hold for ${v.name}`, () => {
        const core = toRequestObject(v.core);
        const canonical = canonicalRequestCore(core);
        expect(toHex(canonical)).toBe(v.canonical_bytes_hex);

        const input = requestSigningInput(core);
        expect(toHex(input)).toBe(v.signing_input_hex);
        const domainBytes = new TextEncoder().encode(REQUEST_DOMAIN);
        expect(Array.from(input.slice(0, domainBytes.length))).toEqual(
          Array.from(domainBytes)
        );
        expect(input.length).toBe(domainBytes.length + canonical.length);

        expect(cidFromCanonical(canonical)).toBe(v.cid);

        const seed = fromHex(v.signer_seed_hex);
        const kp = nacl.sign.keyPair.fromSeed(seed);
        expect(toHex(kp.publicKey)).toBe(v.signer_pubkey_hex);

        // Identity binding: except for explicit negative vectors, the actor must be the
        // base58 encoding of the signer public key.
        const signerB58 = bs58.encode(kp.publicKey);
        if (v.expect_signer_match === false) {
          expect(v.name).toBe('signer_mismatch_rejected');
          expect(v.core.popclaw_id).not.toBe(signerB58);
        } else {
          expect(v.core.popclaw_id, `${v.name} actor must equal signer key`).toBe(
            signerB58
          );
        }

        const sig = fromHex(v.signature_hex);
        expect(nacl.sign.detached.verify(input, sig, kp.publicKey)).toBe(true);
        expect(toHex(nacl.sign.detached(input, kp.secretKey))).toBe(v.signature_hex);
      });
    }

    it('explicit proto3 defaults still elide (default_boundaries vector)', () => {
      const boundaries = vectors.house_session.requests.find(
        (r) => r.name === 'default_boundaries'
      );
      const minimal = vectors.house_session.requests.find((r) => r.name === 'enter_minimal');
      expect(boundaries).toBeDefined();
      expect(minimal).toBeDefined();
      expect(boundaries!.explicit_defaults).toBe(true);
      // The mapper above passes explicit 0 / '' through — canonicalRequestCore
      // must still drop them to match prost.
      expect(boundaries!.canonical_bytes_hex).toBe(minimal!.canonical_bytes_hex);
    });
  });

  describe('acks', () => {
    for (const v of vectors.house_session.acks) {
      it(`canonical bytes + signing input + signature hold for ${v.name}`, () => {
        const core = toAckObject(v.core);
        const canonical = canonicalAckCore(core);
        expect(toHex(canonical)).toBe(v.canonical_bytes_hex);

        const input = ackSigningInput(core);
        expect(toHex(input)).toBe(v.signing_input_hex);
        const domainBytes = new TextEncoder().encode(ACK_DOMAIN);
        expect(Array.from(input.slice(0, domainBytes.length))).toEqual(
          Array.from(domainBytes)
        );
        expect(input.length).toBe(domainBytes.length + canonical.length);

        expect(cidFromCanonical(canonical)).toBe(v.cid);

        const seed = fromHex(v.signer_seed_hex);
        const kp = nacl.sign.keyPair.fromSeed(seed);
        expect(toHex(kp.publicKey)).toBe(v.signer_pubkey_hex);
        const sig = fromHex(v.signature_hex);
        expect(nacl.sign.detached.verify(input, sig, kp.publicKey)).toBe(true);
      });
    }
  });

  describe('sequences', () => {
    const legalOutcomes: Record<string, string[]> = {
      ENTER: ['ENTERED', 'ALREADY_ENTERED', 'REJECTED'],
      RENEW: ['RENEWED', 'REJECTED'],
      LEAVE: ['CLOSED', 'ALREADY_CLOSED', 'SUPERSEDED', 'REJECTED'],
      STATUS: ['REPORTED', 'REJECTED'],
    };

    it('every step pairs a legal outcome with its operation', () => {
      for (const seq of vectors.house_session.sequences) {
        for (const [i, step] of seq.steps.entries()) {
          expect(legalOutcomes[step.op], `${seq.name} step ${i} op`).toContain(
            step.expected_outcome
          );
          if (step.expected_outcome === 'REJECTED') {
            expect(step.expected_error_code, `${seq.name} step ${i} error_code`).toBeTruthy();
          } else {
            expect(step.expected_error_code, `${seq.name} step ${i} no error_code`).toBeUndefined();
          }
        }
      }
    });

    it('delivery semantics are consistent (first vs replay)', () => {
      for (const seq of vectors.house_session.sequences) {
        const seenFirst: string[] = [];
        for (const [i, step] of seq.steps.entries()) {
          if (step.delivery === 'first') {
            expect(
              seenFirst.includes(step.request_id),
              `${seq.name} step ${i}: request delivered first twice`
            ).toBe(false);
            seenFirst.push(step.request_id);
          } else {
            expect(
              seenFirst.includes(step.request_id),
              `${seq.name} step ${i}: replay of a never-delivered request`
            ).toBe(true);
            expect(
              step.expected_outcome.startsWith('ALREADY'),
              `${seq.name} step ${i}: replay outcome must be ALREADY_*`
            ).toBe(true);
          }
          if (step.expected_outcome === 'SUPERSEDED') {
            expect(
              step.delivery,
              `${seq.name} step ${i}: SUPERSEDED must be a first delivery`
            ).toBe('first');
          }
        }
      }
    });

    it('mandated race examples are pinned', () => {
      const names = vectors.house_session.sequences.map((s) => s.name);
      for (const required of [
        'enter_rotated_enter_late_leave',
        'leave_before_enter_commit',
        'leave_ack_lost_retry',
      ]) {
        expect(names, `missing mandated example ${required}`).toContain(required);
      }
    });

    it('late leave example: rotation then first-delivery SUPERSEDED, new session alive', () => {
      const seq = vectors.house_session.sequences.find(
        (s) => s.name === 'enter_rotated_enter_late_leave'
      )!;
      const steps = seq.steps;
      expect(steps[1].expected_outcome).toBe('ENTERED'); // rotation, not reuse
      const last = steps[steps.length - 1];
      expect(last.op).toBe('LEAVE');
      expect(last.delivery).toBe('first');
      expect(last.expected_outcome).toBe('SUPERSEDED');
      expect(seq.description).toContain('session_active');
      expect(seq.description).toContain('rotation');
    });
  });
});
