import { describe, it, expect } from 'vitest';
import { popclaw } from '@popclaw/contracts';
import descriptor from '@popclaw/contracts/descriptor';
import protobuf from 'protobufjs';
import { canonicalizeEnvelope } from '../src/canonical.js';

const root = protobuf.Root.fromJSON(descriptor as protobuf.INamespace);
const hex = (b: Uint8Array) => Buffer.from(b).toString('hex');

describe('frozen world contract allocations', () => {
  it('reserves A1–A3 at their approved tags and exports world messages', () => {
    expect(root.lookupType('popclaw.event.IntentPayload').fields.context.id).toBe(4);
    expect(root.lookupType('popclaw.event.HouseEvent').fields.publicScopes.id).toBe(4);
    expect(root.lookupType('popclaw.event.WorldStreamFrame').fields.scopes.id).toBe(5);
    expect(popclaw.world.IntentContext).toBeDefined();
  });

  it('context contributes to the envelope CID while absent context preserves old bytes', () => {
    const old = { intent: { intentKind: 'example.act' } };
    const context = { houseOrigin: 'https://a.invalid', sessionId: 's', validUntil: 99 };
    expect(hex(canonicalizeEnvelope(old))).toBe('9a020d120b6578616d706c652e616374');
    expect(hex(canonicalizeEnvelope({ intent: { ...old.intent, context } })))
      .toBe('9a0227120b6578616d706c652e61637422180a1168747470733a2f2f612e696e76616c69642201734063');
    expect(canonicalizeEnvelope({ intent: { ...old.intent, context } }))
      .not.toEqual(canonicalizeEnvelope(old));
  });

  it('context elides explicit scalar defaults, preserves empty-message presence and exact int64', () => {
    const encode = (context: popclaw.world.IIntentContext) => canonicalizeEnvelope({ intent: { context } });
    expect(hex(encode({}))).toBe('9a02022200');
    expect(encode({ houseOrigin: '', schemaVersion: 0, validUntil: 0 })).toEqual(encode({}));
    const zero = popclaw.world.IntentContext.decode(new Uint8Array([64, 0]));
    expect(encode(zero)).toEqual(encode({}));
    const large = popclaw.world.IntentContext.fromObject({ validUntil: '9007199254740993' });
    expect(hex(encode(large))).toBe('9a020b2209408180808080808010');
  });

  it('signed public scopes change the CID; relay scopes do not change envelope bytes', () => {
    const old = { houseEvent: { kind: 'example.notice' } };
    const scoped = { houseEvent: { ...old.houseEvent, publicScopes: ['scope-a'] } };
    expect(canonicalizeEnvelope(scoped)).not.toEqual(canonicalizeEnvelope(old));
    const envelope = canonicalizeEnvelope(scoped);
    const frame = popclaw.event.WorldStreamFrame.decode(popclaw.event.WorldStreamFrame.encode({ envelope, scopes: ['relay-only'] }).finish());
    expect(frame.scopes).toEqual(['relay-only']);
    expect(frame.envelope).toEqual(envelope);
  });
});
