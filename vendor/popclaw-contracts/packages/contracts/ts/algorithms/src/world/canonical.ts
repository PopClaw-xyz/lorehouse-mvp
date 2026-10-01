import { cidFromCanonical } from '../cid.js';
import { popclaw } from '@popclaw/contracts';
import descriptor from '@popclaw/contracts/descriptor';
import protobuf from 'protobufjs';
import { validateWorldInput } from './json.js';

export interface Codec<T> {
  encode(message: T): { finish(): Uint8Array };
  decode(bytes: Uint8Array): T;
  getTypeUrl?(prefix?: string): string;
}

const schema = protobuf.Root.fromJSON(descriptor as protobuf.INamespace).resolveAll();
// The canonical descriptor distinguishes explicit presence from implicit
// defaults. Nested messages and repeated elements retain their positions.
function normalize(value: unknown, type?: protobuf.Type): unknown {
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (typeof value === 'number' && !Number.isSafeInteger(value)) throw new Error('UNSAFE_INTEGER');
  if (Array.isArray(value)) return value.map(item => normalize(item, type));
  if (typeof value !== 'object' || value === null) return value;
  if ('low' in value && 'high' in value && 'unsigned' in value && 'toNumber' in value) return value;
  const result: Record<string, unknown> = {};
  for (const [key, child] of Object.entries(value)) {
    if (child === undefined || child === null) continue;
    const field = type?.fields[key];
    // protobufjs models proto3 optional scalars as synthetic oneof members.
    if (!field?.partOf) {
      if (child === '' || child === false || child === 0) continue;
      if ((child instanceof Uint8Array || Array.isArray(child)) && child.length === 0) continue;
      if (typeof child === 'object' && 'low' in child && 'high' in child && child.low === 0 && child.high === 0) continue;
    }
    result[key] = normalize(child, field?.resolvedType instanceof protobuf.Type ? field.resolvedType : undefined);
  }
  return result;
}

/** Canonical proto3 core bytes. Accept generated types, never lossy JSON numbers. */
export function canonicalWorld<T>(codec: Codec<T>, core: T): Uint8Array {
  // Generated codecs may come from a consumer's canonical package while the
  // SDK bundles its own identical copy. Object identity is not a type identity.
  const name = codec.getTypeUrl?.().match(/\/popclaw\.world\.([A-Za-z][A-Za-z0-9_]*)$/)?.[1];
  if (!name) throw new Error('CANONICAL_WORLD_TYPE_REQUIRED');
  validateWorldInput(name, core);
  return codec.encode(normalize(core, schema.lookupType(`popclaw.world.${name}`)) as T).finish();
}

export interface WorkerSigner {
  readonly publicKey: Uint8Array;
  sign(bytes: Uint8Array): Promise<Uint8Array>;
}

export interface BuiltWorkerResult {
  readonly coreBytes: Uint8Array;
  readonly signedResultBytes: Uint8Array;
}

export function signingInput(domain: string, bytes: Uint8Array): Uint8Array {
  const prefix = new TextEncoder().encode(domain);
  const result = new Uint8Array(prefix.length + bytes.length);
  result.set(prefix);
  result.set(bytes, prefix.length);
  return result;
}

/** Build once after business commit; persist these bytes before any delivery. */
export async function signWorkerResult(signer: WorkerSigner, result: popclaw.world.IWorkerResult): Promise<Uint8Array> {
  return (await buildWorkerResult(signer, result)).signedResultBytes;
}

export async function buildWorkerResult(signer: WorkerSigner, result: popclaw.world.IWorkerResult): Promise<BuiltWorkerResult> {
  if (result.status !== 'succeeded' && result.status !== 'rejected') throw new Error('RESULT_NOT_TERMINAL');
  if ((result.resultBody?.length ?? 0) > 32768) throw new Error('RESULT_BODY_TOO_LARGE');
  if (cidFromCanonical(result.resultBody ?? new Uint8Array()) !== result.resultDigest) throw new Error('RESULT_DIGEST_MISMATCH');
  const core = canonicalWorld(popclaw.world.WorkerResult, result);
  const signature = await signer.sign(signingInput('POPCLAW_WORLD_WORKER_RESULT_V1', core));
  if (signature.length !== 64 || signer.publicKey.length !== 32) throw new Error('SIGNER_INVALID');
  return { coreBytes: new Uint8Array(core), signedResultBytes: popclaw.world.SignedWorkerResult.encode({ result: popclaw.world.WorkerResult.decode(core), signature }).finish() };
}
