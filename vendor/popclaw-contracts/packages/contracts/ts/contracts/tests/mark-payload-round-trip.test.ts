import { describe, expect, it } from 'vitest';
import { popclaw } from '../src/generated/index.js';

describe('MarkPayload round-trip', () => {
  it('encodes and decodes mark + markRevoked', () => {
    const id = 'a'.repeat(64);
    for (const payload of [{ mark: { markedEventId: id } }, { markRevoked: { markedEventId: id } }] as const) {
      const env = popclaw.event.EventEnvelope.create({
        actor: { popclawId: 'x', nickname: 'n' },
        platform: 'popclaw',
        timestamp: 1,
        ...payload,
      });
      const dec = popclaw.event.EventEnvelope.decode(
        popclaw.event.EventEnvelope.encode(env).finish(),
      );
      const got = 'mark' in payload ? dec.mark?.markedEventId : dec.markRevoked?.markedEventId;
      expect(got).toBe(id);
    }
  });

  it('WorldFeedItem carries event_id and mark_count fields', () => {
    const item = popclaw.event.WorldFeedItem.create({
      platform: 'popclaw',
      platformPostId: 'abc',
      eventId: 'a'.repeat(64),
      markCount: 42,
    });
    const dec = popclaw.event.WorldFeedItem.decode(
      popclaw.event.WorldFeedItem.encode(item).finish(),
    );
    expect(dec.eventId).toBe('a'.repeat(64));
    // int64 fields are decoded as Long objects by protobufjs — compare via toNumber().
    expect(Number(dec.markCount)).toBe(42);
  });

  it('proto3 default elision: empty event_id and 0 mark_count NOT on wire when omitted', () => {
    // prost (Rust) elides proto3 defaults; protobufjs (TS)
    // emits them if you explicitly set the field. NEVER explicitly set event_id='' or
    // mark_count=0 in TS producers — omit the field entirely so the wire is compact and
    // round-trips correctly on both sides.
    const item = popclaw.event.WorldFeedItem.create({
      platform: 'x',
      platformPostId: 'p1',
      // event_id and mark_count intentionally omitted (proto3 defaults: '' and 0)
    });
    const bytes = item instanceof Uint8Array
      ? item
      : popclaw.event.WorldFeedItem.encode(item).finish();

    // field 19 = event_id (string LEN): tag byte sequence 0x9a 0x01
    // field 20 = mark_count (int64 VARINT): tag byte sequence 0xa0 0x01
    // These must NOT appear in the encoded bytes when the fields are omitted.
    const field19Tag = [0x9a, 0x01];
    const field20Tag = [0xa0, 0x01];

    function containsSequence(buf: Uint8Array, seq: number[]): boolean {
      for (let i = 0; i <= buf.length - seq.length; i++) {
        if (seq.every((b, j) => buf[i + j] === b)) return true;
      }
      return false;
    }

    expect(containsSequence(bytes, field19Tag)).toBe(false);
    expect(containsSequence(bytes, field20Tag)).toBe(false);

    // Sanity: with fields populated, the tag bytes DO appear.
    const withFields = popclaw.event.WorldFeedItem.create({
      platform: 'x',
      platformPostId: 'p1',
      eventId: 'a'.repeat(64),
      markCount: 5,
    });
    const withBytes = popclaw.event.WorldFeedItem.encode(withFields).finish();
    expect(containsSequence(withBytes, field19Tag)).toBe(true);
    expect(containsSequence(withBytes, field20Tag)).toBe(true);
  });
});
