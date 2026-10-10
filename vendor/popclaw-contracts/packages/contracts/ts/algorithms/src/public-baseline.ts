import protobuf from 'protobufjs';
import descriptor from '@popclaw/contracts/descriptor';

export const ENVELOPE_BASELINE = 'public-envelope-02';
const schema = protobuf.Root.fromJSON(descriptor as protobuf.INamespace).resolveAll();
const utf8 = new TextDecoder('utf-8', { fatal: true });
const varints = new Set(['int32','uint32','sint32','int64','uint64','sint64','bool']);

/** `L_ENVELOPE_MAX_BYTES` (LIMITS.md): the largest raw EventEnvelope any
 * conforming reader must accept. Sized so a direct message carrying a 1 MiB
 * sealed attachment plus its sealed text fits with margin. */
export const L_ENVELOPE_MAX_BYTES = 1572864;

/** Structural predecode guard only. Identity, signatures, body validity and
 * public membership MUST additionally pass before allocation or forwarding.
 * The caller retains the exact input; this function never repairs/re-encodes it.
 */
export function checkEnvelopeWire(raw: Uint8Array): number {
  if (raw.length > L_ENVELOPE_MAX_BYTES) throw new Error('WIRE_LIMIT');
  let budget = 65536;
  let body = 0;
  function scan(bytes: Uint8Array, type: protobuf.Type, depth: number): void {
    if (depth > 32) throw new Error('WIRE_DEPTH');
    let pos = 0;
    const seen = new Set<number>();
    const oneofs = new Set<string>();
    function vint(): bigint {
      let n = 0n;
      for (let i = 0; i < 10; i++) {
        const b = bytes[pos++];
        if (b === undefined || (i === 9 && b > 1)) throw new Error('WIRE_VARINT');
        n |= BigInt(b & 127) << BigInt(7*i);
        if (!(b & 128)) {
          return n;
        }
      }
      throw new Error('WIRE_VARINT');
    }
    while (pos < bytes.length) {
      if (--budget < 0) throw new Error('WIRE_LIMIT');
      const key = vint();
      const tag = Number(key >> 3n), wire = Number(key & 7n);
      if (tag < 1 || tag > 536870911) throw new Error('WIRE_TAG');
      if ((type.fullName === '.popclaw.event.EventEnvelope' && tag === 29) ||
          (type.fullName === '.popclaw.profile.Profile' && tag === 8)) throw new Error('RESERVED_OCCURRENCE');
      const f = type.fieldsById[tag];
      if (!f) throw new Error('UNSUPPORTED_FIELD');
      if (!f.repeated && !f.map && seen.has(tag)) throw new Error('DUPLICATE_FIELD');
      seen.add(tag);
      if (f.partOf) {
        if (oneofs.has(f.partOf.name)) throw new Error('MULTIPLE_ONEOF');
        oneofs.add(f.partOf.name);
        if (type.fullName === '.popclaw.event.EventEnvelope' && f.partOf.name === 'body') body = tag;
      }
      const expected = f.resolvedType instanceof protobuf.Type || ['string','bytes'].includes(f.type) || f.map ? 2 :
        f.resolvedType instanceof protobuf.Enum || varints.has(f.type) ? 0 :
        ['fixed64','sfixed64','double'].includes(f.type) ? 1 : 5;
      if (wire !== expected) throw new Error('WIRE_TYPE');
      if (wire === 0) {
        const n = vint();
        if (['uint32','sint32'].includes(f.type) && n > 0xffffffffn) throw new Error('WIRE_RANGE');
        if ((f.type === 'int32' || f.resolvedType instanceof protobuf.Enum) &&
            n > 0xffffffffn && n < 0xffffffff80000000n) throw new Error('WIRE_RANGE');
        continue;
      }
      const length = wire === 2 ? Number(vint()) : wire === 1 ? 8 : 4;
      if (!Number.isSafeInteger(length) || length > bytes.length - pos) throw new Error('WIRE_TRUNCATED');
      const value = bytes.subarray(pos,pos+length); pos += length;
      if (f.map) {
        const entry = new protobuf.Type('MapEntry');
        entry.add(new protobuf.Field('key',1,(f as unknown as protobuf.MapField).keyType));
        entry.add(new protobuf.Field('value',2,f.type));
        scan(value,entry,depth+1);
      } else {
        if (f.type === 'string') utf8.decode(value);
        if (f.resolvedType instanceof protobuf.Type) scan(value,f.resolvedType,depth+1);
      }
    }
  }
  scan(raw,schema.lookupType('popclaw.event.EventEnvelope'),0);
  if (!body) throw new Error('MISSING_BODY');
  return body;
}

/** Public structural/privacy eligibility, not cryptographic or business admission.
 * Tags 20/21 (FollowDeclared/FollowRevoked) are absent from the public set: a
 * relation original is owed to its two participants' personal streams and is
 * never a public fact, whether `order` is absent, present or present-but-empty
 * (RELATIONS.md section 8). The body type alone decides, so the follow privacy
 * fields are no longer consulted here — they cannot readmit what the tag has
 * already excluded. This remains a public-eligibility test only: relation
 * originals still pass `checkEnvelopeWire`, keep their canonical bytes, CID and
 * author signature, and are still admitted through a House's ordinary verified
 * write entrance and delivered personally. */
export function checkPublicEnvelopeStructure(raw: Uint8Array): number {
  const tag = checkEnvelopeWire(raw);
  // Reflection preserves exact enum integers after bounded raw range checks.
  const env = schema.lookupType('popclaw.event.EventEnvelope').decode(raw) as unknown as {
    target?: {scope?: number; targetIds?: string[]; filterCriteria?: string};
    houseEvent?: {kind: string; publicScopes?: string[]};
  };
  if (![11,12,13,14,15,16,18,25,27,28,33,34].includes(tag)) throw new Error('NOT_PUBLIC');
  if (env.target) {
    if (![0,2].includes(env.target.scope ?? 0) || env.target.filterCriteria) throw new Error('NOT_PUBLIC');
    if ((env.target.scope ?? 0) === 0 && (env.target.targetIds?.length ?? 0)>0) throw new Error('INVALID_TARGET');
    if (env.target.scope === 2 && !(env.target.targetIds?.length)) throw new Error('INVALID_TARGET');
  }
  const typedEnv = env as typeof env & {
    inviteRequest?: {verificationMode?: number};
    questDispatch?: {verifyInvite?: {verificationMode?: number}};
    questResult?: {verificationProgress?: number};
  };
  if (typedEnv.inviteRequest && ![0,1].includes(typedEnv.inviteRequest.verificationMode ?? 0)) throw new Error('INVALID_ENUM');
  if (typedEnv.questDispatch?.verifyInvite && ![0,1].includes(typedEnv.questDispatch.verifyInvite.verificationMode ?? 0)) throw new Error('INVALID_ENUM');
  if (typedEnv.questResult && ![0,1,2,3].includes(typedEnv.questResult.verificationProgress ?? 0)) throw new Error('INVALID_ENUM');
  if (env.houseEvent) {
    const {kind, publicScopes = []} = env.houseEvent;
    if (kind.length > 128 || !/^[a-z0-9-]+\.[a-z0-9_]+$/.test(kind)) throw new Error('INVALID_KIND');
    if (publicScopes.length > 32 || new Set(publicScopes).size !== publicScopes.length ||
        publicScopes.some(s => !/^[A-Za-z0-9_-]{4,64}$/.test(s))) throw new Error('INVALID_SCOPES');
  }
  return tag;
}
