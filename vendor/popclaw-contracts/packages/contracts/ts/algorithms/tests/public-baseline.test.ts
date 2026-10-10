import { describe, it, expect } from 'vitest';
import { checkEnvelopeWire } from '../src/public-baseline.js';

describe('original wire public baseline guard', () => {
  it.each(['ea0100','e80100','e201024200','e201024000'])('rejects reserved occurrence %s', hex => {
    expect(() => checkEnvelopeWire(Buffer.from(hex, 'hex'))).toThrow();
  });
  it('keeps unknown legal business bytes opaque', () => {
    const body = Buffer.from('0a0961622e666f6f5f30301a03ea0100', 'hex');
    const raw = Buffer.concat([Buffer.from([0x92, 2, body.length]),body]);
    expect(checkEnvelopeWire(raw)).toBe(34);
  });
  it.each(['920200920200','e20100e20100','0a8000','00','92020180'])('rejects ambiguous or malformed %s', hex => {
    expect(() => checkEnvelopeWire(Buffer.from(hex, 'hex'))).toThrow();
  });
});

import { readFileSync } from 'node:fs';
import { checkPublicEnvelopeStructure } from '../src/public-baseline.js';
import { canonicalizeEnvelope } from '../src/canonical.js';
import { cidFromCanonical } from '../src/cid.js';
import { popclaw } from '@popclaw/contracts';
import nacl from 'tweetnacl';
const vectors = JSON.parse(readFileSync(new URL('../../../fixtures/public-baseline.json', import.meta.url),'utf8'));
const oldVectors = JSON.parse(readFileSync(new URL('../../../fixtures/test-vectors.json', import.meta.url),'utf8'));

describe('shared cross-language public baseline vectors', () => {
  for (const v of vectors.wire) it(v.name, () => {
    const raw = Buffer.from(v.wire_hex,'hex');
    for (const [fn, expected] of [[checkEnvelopeWire,v.structural],[checkPublicEnvelopeStructure,v.public]] as const) {
      if (expected) expect(() => fn(raw)).not.toThrow();
      else expect(() => fn(raw)).toThrow();
    }
  });
  it.each([
    'invite_wait_duplicate_mode',
    'invite_wait_duplicate_cancel_task',
    'invite_wait_duplicate_dispatch_mode',
    'invite_wait_duplicate_progress',
    'invite_wait_duplicate_progress_revision',
  ])('classifies %s as a duplicate singular field', name => {
    const v = vectors.wire.find(row => row.name === name);
    expect(v, `missing vector ${name}`).toBeDefined();
    expect(() => checkEnvelopeWire(Buffer.from(v!.wire_hex,'hex'))).toThrow('DUPLICATE_FIELD');
  });
  for (const v of vectors.signed) it(v.name, () => {
    const raw = Buffer.from(v.wire_hex,'hex');
    expect(() => checkEnvelopeWire(raw)).not.toThrow();
    const env = popclaw.event.EventEnvelope.decode(raw);
    const core = canonicalizeEnvelope(env);
    expect(Buffer.from(core).toString('hex')).toBe(v.canonical_hex);
    expect(cidFromCanonical(core)).toBe(v.cid);
    const pk = Buffer.from(v.public_key_hex,'hex');
    const sig = Buffer.from(v.signature_hex,'hex');
    expect(nacl.sign.detached.verify(core,sig,pk)).toBe(true);
    const changed = new Uint8Array(core); changed[changed.length-1] ^= 1;
    expect(nacl.sign.detached.verify(changed,sig,pk)).toBe(false);
    const wrapped = popclaw.identity.SignedPayload.decode(Buffer.from(v.signed_payload_hex,'hex'));
    expect(Buffer.from(wrapped.payload).equals(raw)).toBe(true);
    expect(nacl.sign.detached.verify(wrapped.payload,wrapped.signature,wrapped.signerPubkey)).toBe(true);
  });
  for (const v of oldVectors.canonical_serialization) it(`retained wire ${v.name}`, () => {
    const raw = Buffer.from(v.canonical_bytes_hex,'hex');
    if (v.name === 'verified_platform_with_account_id') {
      const value = popclaw.event.VerifiedPlatform.decode(raw);
      expect(Buffer.from(popclaw.event.VerifiedPlatform.encode(value).finish()).toString('hex')).toBe(v.canonical_bytes_hex);
    } else {
      expect(() => checkEnvelopeWire(raw)).not.toThrow();
      expect(Buffer.from(canonicalizeEnvelope(popclaw.event.EventEnvelope.decode(raw))).toString('hex')).toBe(v.canonical_bytes_hex);
    }
  });
});

import { canonicalWorld, signingInput } from '../src/world/canonical.js';
const golden = JSON.parse(readFileSync(new URL('../../../fixtures/retained-signing-golden.json', import.meta.url),'utf8'));
describe('retained world signing rules', () => {
  for (const v of golden.vectors) it(v.type, () => {
    const codec = (popclaw.world as unknown as Record<string,{decode(b:Uint8Array):object;encode(m:object):{finish():Uint8Array};getTypeUrl():string}>)[v.type]!;
    const core = canonicalWorld(codec,codec.decode(Buffer.from(v.signed_core_bytes_hex,'hex')));
    expect(Buffer.from(core).toString('hex')).toBe(v.signed_core_bytes_hex);
    expect(cidFromCanonical(core)).toBe(v.sha256);
    const msg = signingInput(v.domain,core);
    expect(nacl.sign.detached.verify(msg,Buffer.from(v.signature_hex,'hex'),Buffer.from(v.signer_public_key_hex,'hex'))).toBe(true);
    expect(nacl.sign.detached.verify(signingInput(v.domain+'X',core),Buffer.from(v.signature_hex,'hex'),Buffer.from(v.signer_public_key_hex,'hex'))).toBe(false);
  });
});

describe('exact baseline declaration is covered by manifest proof', () => {
  it('binds the baseline and log identity to the exact signed manifest bytes', () => {
    const v=vectors.manifest;
    const raw=new TextEncoder().encode(v.manifest_utf8);
    const proof=popclaw.world.ManifestProof.decode(Buffer.from(v.proof_hex,'hex'));
    const signature=proof.authoritySignature;
    delete (proof as {authoritySignature?:Uint8Array}).authoritySignature;
    const core=canonicalWorld(popclaw.world.ManifestProof,proof);
    expect(cidFromCanonical(raw)).toBe(proof.manifestDigest);
    expect(Buffer.from(core).toString('hex')).toBe(v.core_hex);
    expect(nacl.sign.detached.verify(signingInput('POPCLAW_WORLD_MANIFEST_PROOF_V1',core),signature,Buffer.from(v.public_key_hex,'hex'))).toBe(true);
    const changed=JSON.parse(v.manifest_utf8);
    changed.world_interaction.public_stream.envelope_baseline='another-baseline';
    expect(cidFromCanonical(new TextEncoder().encode(JSON.stringify(changed)))).not.toBe(proof.manifestDigest);
    changed.world_interaction.public_stream.envelope_baseline='public-envelope-02';
    changed.world_interaction.public_stream.log_incarnation='replacement-log';
    expect(cidFromCanonical(new TextEncoder().encode(JSON.stringify(changed)))).not.toBe(proof.manifestDigest);
    expect(cidFromCanonical(new TextEncoder().encode(v.manifest_utf8+'\n'))).not.toBe(proof.manifestDigest);
  });
});

it('unsupported structure can have a valid signature; stripping is not repair', () => {
  const v=vectors.signed_reserved;
  const canonical=Buffer.from(v.canonical_hex,'hex'),raw=Buffer.from(v.wire_hex,'hex');
  const sig=Buffer.from(v.signature_hex,'hex'),key=Buffer.from(v.public_key_hex,'hex');
  expect(nacl.sign.detached.verify(canonical,sig,key)).toBe(true);
  expect(() => checkEnvelopeWire(raw)).toThrow('RESERVED_OCCURRENCE');
  const stripped=canonicalizeEnvelope(popclaw.event.EventEnvelope.decode(raw));
  expect(cidFromCanonical(stripped)).not.toBe(v.cid);
  expect(nacl.sign.detached.verify(stripped,sig,key)).toBe(false);
});
