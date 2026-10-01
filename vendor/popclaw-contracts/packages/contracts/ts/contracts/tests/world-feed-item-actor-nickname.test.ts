import { describe, it, expect } from 'vitest';
import { popclaw } from '../src/generated/index.js';

describe('WorldFeedItem actor_nickname + quoted_actor_nickname (CLI polish plan)', () => {
  it('exposes actorNickname + quotedActorNickname accessors', () => {
    const item = popclaw.event.WorldFeedItem.create({
      platform: 'popclaw',
      platformPostId: 'abc',
      actorNickname: '青鸾',   // CJK nickname — validates UTF-8 round-trip
      quotedActorNickname: 'Scout',
    });
    expect(item.actorNickname).toBe('青鸾');
    expect(item.quotedActorNickname).toBe('Scout');
  });

  it('proto3 default elision: empty actor_nickname not on wire', () => {
    const item = popclaw.event.WorldFeedItem.create({
      platform: 'x',  // 'x' = 0x78 to avoid collision with tag bytes
      platformPostId: 'p1',
    });
    const bytes = popclaw.event.WorldFeedItem.encode(item).finish();
    // Field 15 tag = (15 << 3) | 2 = 0x7a (1-byte form).
    // Field 16 tag = 0x82 0x01 (2-byte varint form, since 130 > 127).
    // Neither tag byte should appear in encoded bytes when fields are absent.
    expect([...bytes].includes(0x7a)).toBe(false);
    expect([...bytes].includes(0x82)).toBe(false);
    // Compare sizes — message with the 2 fields set should be longer.
    const withFields = popclaw.event.WorldFeedItem.create({
      platform: 'x',
      platformPostId: 'p1',
      actorNickname: 'foo',
      quotedActorNickname: 'bar',
    });
    const withBytes = popclaw.event.WorldFeedItem.encode(withFields).finish();
    expect(withBytes.length).toBeGreaterThan(bytes.length);
  });
});
