import descriptor from '@popclaw/contracts/descriptor';
import protobuf from 'protobufjs';

const root = protobuf.Root.fromJSON(descriptor as protobuf.INamespace).resolveAll();
export function validateEnvelopeShape(value: object): void {
  if (root.lookupType('popclaw.event.EventEnvelope').verify(value)) throw new Error('REQUEST_ENVELOPE_INVALID');
}

/** Validate integer ranges before pbjs can truncate/wrap a typed JS value. */
export function validateWorldInput(typeName: string, input: unknown): void {
  function visit(type: protobuf.Type, input: unknown): void {
    if (!input || typeof input !== 'object') throw new Error('PROTOBUF_MESSAGE_INVALID');
    for (const field of type.fieldsArray) {
      const raw = (input as Record<string, unknown>)[field.name];
      if (raw === undefined || raw === null) continue;
      const values = field.repeated ? raw : [raw];
      if (!Array.isArray(values)) throw new Error('PROTOBUF_REPEATED_INVALID');
      for (const value of values) {
        if (field.resolvedType instanceof protobuf.Type) { visit(field.resolvedType, value); continue; }
        if (['uint64', 'int64', 'uint32', 'int32', 'sint32', 'sint64', 'fixed32', 'fixed64', 'sfixed32', 'sfixed64'].includes(field.type) || field.resolvedType instanceof protobuf.Enum) {
          if (typeof value === 'number' && !Number.isSafeInteger(value)) throw new Error('UNSAFE_INTEGER');
          if (typeof value !== 'number' && !(value && typeof value === 'object' && 'low' in value && 'high' in value && 'toNumber' in value)) throw new Error('PROTOBUF_INTEGER_INVALID');
          const n = BigInt(String(value));
          const unsigned = field.type.startsWith('u') || field.type.startsWith('fixed');
          const bits = field.type.endsWith('64') ? 64n : 32n;
          const min = unsigned ? 0n : -(1n << (bits - 1n));
          const max = unsigned ? (1n << bits) - 1n : (1n << (bits - 1n)) - 1n;
          if (n < min || n > max) throw new Error('INTEGER_RANGE');
        }
      }
    }
  }
  visit(root.lookupType(`popclaw.world.${typeName}`), input);
}
export function uint64(value: string): string {
  if (typeof value !== 'string' || !/^(0|[1-9][0-9]{0,19})$/.test(value) || BigInt(value) > 18446744073709551615n) throw new Error('UINT64_INVALID');
  return value;
}

function time(value: unknown): string {
  const seconds = BigInt(String(value));
  if (seconds < -62167219200n || seconds > 253402300799n) throw new Error('TIME_INVALID');
  return new Date(Number(seconds) * 1000).toISOString().replace('.000Z', 'Z');
}

/** JSON rendering derives field kinds from the canonical generated descriptor.
 * Input uses generated camelCase properties; JSON uses the frozen snake_case
 * names, decimal uint64 counters, RFC3339 whole-second int64 times. */
export function worldToJson(typeName: string, value: object): Record<string, unknown> {
  const type = root.lookupType(`popclaw.world.${typeName}`);
  function convert(type: protobuf.Type, input: object): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    for (const key of Object.keys(input)) if (!Object.hasOwn(type.fields, key)) throw new Error('JSON_UNKNOWN_FIELD');
    for (const field of type.fieldsArray) {
      const key = field.name;
      const supplied = (input as Record<string, unknown>)[key];
      // Canonical wire bytes omit scalar zero values. Restore them from the
      // descriptor even when decoding supplied no own property, while absent
      // nested messages remain absent and cannot fabricate business facts.
      if ((supplied === undefined || supplied === null) && (field.partOf || (field.resolvedType instanceof protobuf.Type && !field.repeated))) continue;
      const raw = supplied ?? (field.repeated ? [] : field.type === 'bytes' ? new Uint8Array() : field.defaultValue);
      if ((key === 'channels' && Array.isArray(raw) && raw.length === 0) || ((key === 'dmResponseSlotKey' || key === 'sourceEventId') && raw === '')) continue;
      const scalar = (item: unknown): unknown => {
        if (field.resolvedType instanceof protobuf.Type) return convert(field.resolvedType, item as object);
        if (field.type === 'uint64') {
          if (typeof item === 'number' && !Number.isSafeInteger(item)) throw new Error('UNSAFE_INTEGER');
          return uint64(String(item));
        }
        if (field.type === 'int64') {
          if (typeof item === 'number' && !Number.isSafeInteger(item)) throw new Error('UNSAFE_INTEGER');
          return time(item);
        }
        if (field.type === 'bytes') {
          if (!(item instanceof Uint8Array)) throw new Error('BYTES_INVALID');
          return protobuf.util.base64.encode(item, 0, item.length);
        }
        return item;
      };
      result[key.replace(/[A-Z]/g, letter => '_' + letter.toLowerCase())] = field.repeated ? (raw as unknown[]).map(scalar) : scalar(raw);
    }
    // The frozen participation JSON schema groups the three proto window
    // fields under `window`. This is a rendering adapter, not another wire type.
    if (type.name === 'ParticipationDescriptor') {
      const fields = input as Record<string, unknown>;
      result.revision ??= '0';
      result.window = { id: fields.windowId ?? '', opens_at: time(fields.windowOpensAt ?? 0), closes_at: time(fields.windowClosesAt ?? 0) };
      delete result.window_id;
      delete result.window_opens_at;
      delete result.window_closes_at;
      result.action_groups ??= [];
      result.opportunities ??= [];
      result.budgets ??= [];
    }
    if (type.name === 'Budget') result.suggested_limit ??= 0;
    if (type.name === 'Opportunity') {
      const fields = input as Record<string, unknown>;
      result.not_before ??= time(fields.notBefore ?? 0);
      result.expires_at ??= time(fields.expiresAt ?? 0);
    }
    return result;
  }
  return convert(type, value);
}

/** Canonical JSON for already parsed, integer-only documents. No coercion. */
export function canonicalJson(value: unknown, maxDepth = 8): string {
  function render(value: unknown, depth: number): string {
    if (depth > maxDepth) throw new Error('JSON_DEPTH_LIMIT');
    if (value === null || typeof value === 'boolean' || typeof value === 'string') return JSON.stringify(value);
    if (typeof value === 'number') { if (!Number.isSafeInteger(value)) throw new Error('JSON_INTEGER_REQUIRED'); return JSON.stringify(value); }
    if (Array.isArray(value)) return '[' + value.map(item => render(item, depth + 1)).join(',') + ']';
    if (typeof value !== 'object' || Object.getPrototypeOf(value) !== Object.prototype) throw new Error('JSON_VALUE_INVALID');
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + render((value as Record<string, unknown>)[key], depth + 1)).join(',') + '}';
  }
  return render(value, 0);
}
