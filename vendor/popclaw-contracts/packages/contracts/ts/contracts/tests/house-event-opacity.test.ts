/**
 * Federation spec (2026-07-26) — Layer 2 extension slots.
 *
 * HouseEvent.body / IntentPayload.params are opaque bytes: contracts never
 * looks inside them, so the wire format cannot be perturbed by whatever the
 * house encodes in there. These tests pin that property, plus the proto3
 * default-elision rule that CID parity with prost depends on.
 *
 * Cross-language byte parity lives in the fixture suite (gen_fixtures.rs +
 * ts/algorithms/tests/canonical-parity.test.ts); these are the local
 * pbjs-side invariants.
 */
import { describe, expect, it } from 'vitest';
import { popclaw } from '../src/generated/index.js';

function containsSequence(buf: Uint8Array, seq: readonly number[]): boolean {
  for (let i = 0; i <= buf.length - seq.length; i++) {
    if (seq.every((b, j) => buf[i + j] === b)) return true;
  }
  return false;
}

const outer = {
  actor: { popclawId: 'x', nickname: 'n' },
  lorehouse: 'popclaw',
  timestamp: 1,
} as const;

function roundTrip(body: Record<string, unknown>): popclaw.event.EventEnvelope {
  const env = popclaw.event.EventEnvelope.create({ ...outer, ...body });
  return popclaw.event.EventEnvelope.decode(popclaw.event.EventEnvelope.encode(env).finish());
}

describe('HouseEvent opacity', () => {
  it.each<{ label: string; bytes: Uint8Array }>([
    { label: 'NUL + high bytes', bytes: new Uint8Array([0x00, 0xff, 0x7b, 0x00, 0x1a, 0x80]) },
    { label: 'all zero bytes', bytes: new Uint8Array([0, 0, 0, 0]) },
    { label: 'single NUL', bytes: new Uint8Array([0]) },
    { label: '1 KiB of 0x00..0xff cycling', bytes: Uint8Array.from({ length: 1024 }, (_, i) => i % 256) },
  ])('round-trips body byte-for-byte: $label', ({ bytes }) => {
    const dec = roundTrip({ houseEvent: { kind: 'world.postcard', schemaVersion: 3, body: bytes } });
    expect(dec.houseEvent?.kind).toBe('world.postcard');
    expect(dec.houseEvent?.schemaVersion).toBe(3);
    expect(Array.from(dec.houseEvent!.body!)).toEqual(Array.from(bytes));
  });

  it('encoding is deterministic for identical input', () => {
    const build = () =>
      popclaw.event.EventEnvelope.encode(
        popclaw.event.EventEnvelope.create({
          ...outer,
          houseEvent: {
            kind: 'world.trip',
            schemaVersion: 2,
            body: new Uint8Array([0x00, 0x01, 0xfe, 0xff]),
          },
        }),
      ).finish();
    expect(Array.from(build())).toEqual(Array.from(build()));
  });

  it('an empty body decodes as empty, not as a missing HouseEvent', () => {
    // `houseEvent: {}` is a present-but-all-default message: tag 34 + len 0.
    const dec = roundTrip({ houseEvent: {} });
    expect(dec.body).toBe('houseEvent');
    expect(dec.houseEvent?.kind).toBe('');
    expect(dec.houseEvent?.schemaVersion).toBe(0);
    expect(dec.houseEvent?.body?.length ?? 0).toBe(0);
  });

  it('proto3 defaults elide when omitted, and leak onto the wire when set explicitly', () => {
    // This is applied to HouseEvent: prost elides defaults,
    // pbjs emits them if the property is present on the object. A producer that
    // writes `schemaVersion: 0` or `body: new Uint8Array(0)` ships bytes prost
    // would never produce → the server recomputes a different CID → cid_mismatch.
    const HE = popclaw.event.HouseEvent;
    const omitted = HE.encode(HE.create({ kind: 'world.encounter' })).finish();
    const explicit = HE.encode(
      HE.create({ kind: 'world.encounter', schemaVersion: 0, body: new Uint8Array(0) }),
    ).finish();

    const schemaVersionTag = [0x10]; // field 2, varint
    const bodyTag = [0x1a]; // field 3, LEN
    expect(containsSequence(omitted, schemaVersionTag)).toBe(false);
    expect(containsSequence(omitted, bodyTag)).toBe(false);
    expect(containsSequence(explicit, schemaVersionTag)).toBe(true);
    expect(containsSequence(explicit, bodyTag)).toBe(true);
    expect(explicit.length).toBeGreaterThan(omitted.length);
  });

  it('an unknown kind still decodes — clients ignore by kind, not by parse failure', () => {
    // additive superset: a house we have never heard of must not
    // produce a decode error, only an unrecognised `kind` string.
    const dec = roundTrip({
      houseEvent: { kind: 'somefuturehouse.some_verb', schemaVersion: 99, body: new Uint8Array([9]) },
    });
    expect(dec.body).toBe('houseEvent');
    expect(dec.houseEvent?.kind).toBe('somefuturehouse.some_verb');
  });
});

describe('IntentPayload opacity', () => {
  it('round-trips params byte-for-byte incl. NUL', () => {
    const params = new Uint8Array([0x7b, 0x00, 0xff, 0x7d]);
    const dec = roundTrip({
      intent: { lorehouse: 'world', intentKind: 'world.pack_and_travel', params },
    });
    expect(dec.intent?.lorehouse).toBe('world');
    expect(dec.intent?.intentKind).toBe('world.pack_and_travel');
    expect(Array.from(dec.intent!.params!)).toEqual(Array.from(params));
  });

  it('proto3 defaults elide when omitted', () => {
    const IP = popclaw.event.IntentPayload;
    const omitted = IP.encode(IP.create({ intentKind: 'world.look_around' })).finish();
    const explicit = IP.encode(
      IP.create({ lorehouse: '', intentKind: 'world.look_around', params: new Uint8Array(0) }),
    ).finish();
    expect(containsSequence(omitted, [0x0a])).toBe(false); // field 1, LEN
    expect(containsSequence(omitted, [0x1a])).toBe(false); // field 3, LEN
    expect(explicit.length).toBeGreaterThan(omitted.length);
  });
});
