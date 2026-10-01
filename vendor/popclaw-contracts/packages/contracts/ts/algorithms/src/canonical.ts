import { popclaw } from '@popclaw/contracts';
import descriptor from '@popclaw/contracts/descriptor';
import protobuf from 'protobufjs';
import { stripDefaultKeys } from './house-session.js';

/**
 * Reflection view of the schema, built once from the generated descriptor.
 *
 * The static-module codegen we encode with carries no field metadata, so it
 * cannot answer the one question canonicalization depends on: does this field
 * track explicit presence? Reflection can, so we ask the schema rather than
 * maintaining a list of field names by hand.
 */
let cachedRoot: protobuf.Root | undefined;
function schema(): protobuf.Root {
  if (!cachedRoot) {
    cachedRoot = protobuf.Root.fromJSON(descriptor as protobuf.INamespace);
    cachedRoot.resolveAll(); // populate field.resolvedType for nested walks
  }
  return cachedRoot;
}

/** Proto3 implicit defaults elide; oneof/optional, map and repeated values retain presence. */
function isImplicitDefault(field: protobuf.Field | undefined, value: unknown): boolean {
  if (!field || field.partOf || field.repeated || field.map || field.resolvedType instanceof protobuf.Type) return false;
  if (field.type === 'bytes') return value instanceof Uint8Array && value.length === 0;
  if (field.type === 'string') return value === '';
  if (field.type === 'bool') return value === false;
  if (value === 0 || value === '0' || value === 0n) return true;
  if (value && typeof value === 'object' && 'low' in value && 'high' in value) {
    const long = value as {low: number; high: number};
    return long.low === 0 && long.high === 0;
  }
  return false;
}

/**
 * Canonicalize an EventEnvelope to proto3 bytes, stripping event_id and signature.
 *
 * The wire format matches what Rust `popclaw-algorithms::canonicalize_envelope`
 * produces. Both rely on:
 *   1. proto3 default-value field omission
 *   2. `protobufjs` writer emits fields in tag order
 *   3. maps (none in EventEnvelope directly, but ContentBlock.metadata is a map)
 *      are encoded with keys sorted byte-wise ascending
 */
export function canonicalizeEnvelope(envelope: unknown): Uint8Array {
  // Deep-clone without going through JSON — Scope B payloads contain `bytes`
  // fields (applicant_popclaw_id, evidence_hash, …) represented as Uint8Array
  // on the JS side, and JSON.stringify would turn those into plain objects
  // with string keys, which protobufjs refuses to treat as bytes.
  // Descriptor context distinguishes implicit defaults from explicit presence.
  const copy = deepClone(
    envelope,
    schema().lookupType('popclaw.event.EventEnvelope')
  ) as Record<string, unknown>;
  // Strip event_id and signature so the encoded bytes are reproducible.
  // Use delete so protobufjs's hasOwnProperty guard doesn't emit the field
  // (setting to an empty value still writes the tag+length bytes, diverging
  // from Rust/prost which omits proto3 default-value fields entirely).
  delete copy.event_id;
  delete copy.eventId;
  delete copy.signature;

  // Recursively sort any map<string, string> fields. For the current schema,
  // only ContentBlock.metadata is a map. Walk generically to future-proof.
  sortMaps(copy);

  const ns = popclaw as unknown as {
    event: { EventEnvelope: { encode(m: unknown): { finish(): Uint8Array } } };
  };
  return ns.event.EventEnvelope.encode(copy).finish();
}

/** Clone with descriptor context, preserving explicit scalar/message presence. */
function deepClone(value: unknown, type?: protobuf.Type): unknown {
  if (value === null || typeof value !== 'object') return value;
  if (value instanceof Uint8Array) {
    const out = new Uint8Array(value.length);
    out.set(value);
    return out;
  }
  if (Array.isArray(value)) return value.map((item) => deepClone(item, type));
  // A1 is a new signed core with the same zero-default discipline as the
  // session core. Keep this scoped to IntentContext: legacy envelope rules
  // and explicit presence (including ActorInfo.device_id) stay unchanged.
  if (type?.fullName === '.popclaw.world.IntentContext') {
    return stripDefaultKeys(value as Record<string, unknown>);
  }
  const out: Record<string, unknown> = Object.create(null);
  for (const k of Object.keys(value as Record<string, unknown>)) {
    const v = (value as Record<string, unknown>)[k];
    const field = type?.fields?.[k];
    if (isImplicitDefault(field, v)) {
      continue; // implicit-presence proto3 default — must elide to match prost
    }
    const nested = field?.resolvedType;
    out[k] = deepClone(v, nested instanceof protobuf.Type ? nested : undefined);
  }
  return out;
}

/**
 * Walks the object tree; for every key named `metadata` that is a plain object,
 * replace it with an equivalent object whose own-keys are sorted ascending.
 * protobufjs encodes objects in own-key order, so this enforces canonical order.
 */
function sortMaps(root: unknown): void {
  if (root === null || typeof root !== 'object') return;
  if (root instanceof Uint8Array) return;
  const obj = root as Record<string, unknown>;
  for (const key of Object.keys(obj)) {
    const val = obj[key];
    if (
      key === 'metadata' &&
      val &&
      typeof val === 'object' &&
      !Array.isArray(val) &&
      !(val instanceof Uint8Array)
    ) {
      const sorted: Record<string, unknown> = Object.create(null);
      for (const k of Object.keys(val as Record<string, unknown>).sort()) {
        sorted[k] = (val as Record<string, unknown>)[k];
      }
      obj[key] = sorted;
    } else if (Array.isArray(val)) {
      for (const item of val) sortMaps(item);
    } else if (val && typeof val === 'object' && !(val instanceof Uint8Array)) {
      sortMaps(val);
    }
  }
}
