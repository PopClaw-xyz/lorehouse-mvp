import { describe, it, expect } from 'vitest';
import { popclaw } from '../src/generated/index.js';

describe('WorldFeedItem quoted_* fields (this plan)', () => {
  it('exposes quotedEventId / quotedAuthorPopclawId / quotedAuthorHandle / quotedTextPreview', () => {
    const item = popclaw.event.WorldFeedItem.create({
      platform: 'popclaw',
      platformPostId: 'abc',
      quotedEventId: 'a'.repeat(64),
      quotedAuthorPopclawId: 'BlackFeather',
      quotedAuthorHandle: 'blackfeather',
      quotedTextPreview: '城西西瓜很便宜',
    });
    expect(item.quotedEventId).toBe('a'.repeat(64));
    expect(item.quotedAuthorPopclawId).toBe('BlackFeather');
    expect(item.quotedAuthorHandle).toBe('blackfeather');
    expect(item.quotedTextPreview).toBe('城西西瓜很便宜');
  });

  it('omits empty quoted_* on wire (proto3 default elision)', () => {
    // Encode a message with quoted_* populated — must be longer than without.
    const withQuoted = popclaw.event.WorldFeedItem.create({
      platform: 'x',
      quotedEventId: 'deadbeef',
      quotedAuthorPopclawId: 'BlackFeather',
      quotedAuthorHandle: 'blackfeather',
      quotedTextPreview: 'hello',
    });
    const withoutQuoted = popclaw.event.WorldFeedItem.create({
      platform: 'x',
    });

    const bytesWithQuoted = popclaw.event.WorldFeedItem.encode(withQuoted).finish();
    const bytesWithoutQuoted = popclaw.event.WorldFeedItem.encode(withoutQuoted).finish();

    // When quoted_* are empty, the encoding must be strictly shorter.
    expect(bytesWithoutQuoted.length).toBeLessThan(bytesWithQuoted.length);

    // Verify the without-quoted encoding does NOT contain any of the
    // field-11..14 tag bytes (0x5a, 0x62, 0x6a, 0x72) when the platform
    // field value itself doesn't contain those bytes.
    // platform='x' (0x78) avoids collision with tag bytes 0x5a/0x62/0x6a/0x72.
    // Field 1 tag = 0x0a, length = 0x01, value = 0x78 ('x') — no tag collision.
    const tag11 = (11 << 3) | 2; // 0x5a
    const tag12 = (12 << 3) | 2; // 0x62
    const tag13 = (13 << 3) | 2; // 0x6a
    const tag14 = (14 << 3) | 2; // 0x72
    const tags = new Set([tag11, tag12, tag13, tag14]);
    for (const b of bytesWithoutQuoted) {
      expect(tags.has(b)).toBe(false);
    }
  });
});
