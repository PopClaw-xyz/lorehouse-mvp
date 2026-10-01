import { describe, it, expect } from 'vitest';
import { popclaw } from '../src/index.js';
const hex = (bytes: Uint8Array) => Buffer.from(bytes).toString('hex');
describe('public-v1 relay metadata parity', () => {
  it('preserves exact uint64 values above the JS safe integer range', () => {
    const value = popclaw.world.PublicStreamBoundary.fromObject({logIncarnation: 'log1', scopes: ['scopeA'], highWaterSeq: '9007199254740993', fullPublic: true});
    const bytes = popclaw.world.PublicStreamBoundary.encode(value).finish();
    expect(hex(bytes)).toBe('0a046c6f6731120673636f7065411881808080808080102001');
    expect(popclaw.world.PublicStreamBoundary.decode(bytes).highWaterSeq.toString()).toBe('9007199254740993');
  });
  it('distinguishes scope-only absence from explicit public zero and preserves uint64 max', () => {
    const encode = (value: Record<string, unknown>) => popclaw.world.PublicStreamCheckpoint.encode(popclaw.world.PublicStreamCheckpoint.fromObject(value)).finish();
    expect(hex(encode({phase: 'replay'}))).toBe('0a067265706c6179');
    const zero = encode({phase: 'replay', publicThroughSeq: '0'});
    expect(hex(zero)).toBe('0a067265706c61791800');
    expect(Object.hasOwn(popclaw.world.PublicStreamCheckpoint.decode(zero), 'publicThroughSeq')).toBe(true);
    expect(Object.hasOwn(popclaw.world.PublicStreamCheckpoint.decode(encode({phase: 'replay'})), 'publicThroughSeq')).toBe(false);
    const maximum = encode({phase: 'live', publicThroughSeq: '18446744073709551615'});
    expect(hex(maximum)).toBe('0a046c69766518ffffffffffffffffff01');
    expect(popclaw.world.PublicStreamCheckpoint.decode(maximum).publicThroughSeq!.toString()).toBe('18446744073709551615');
  });
  it('keeps gap selection in its own relay metadata container', () => {
    const value = popclaw.world.PublicStreamGap.fromObject({reason:'history_pruned',lane:'scope',scopeId:'scopeA', boundary:{logIncarnation:'log1',scopes:['scopeA'],highWaterSeq:'9007199254740993',fullPublic:true}});
    expect(hex(popclaw.world.PublicStreamGap.encode(value).finish())).toBe('0a0e686973746f72795f7072756e6564120573636f70651a0673636f70654122190a046c6f6731120673636f7065411881808080808080102001');
  });
});
