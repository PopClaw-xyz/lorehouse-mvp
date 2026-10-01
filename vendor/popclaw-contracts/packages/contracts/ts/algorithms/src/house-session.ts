import { popclaw } from '@popclaw/contracts';

/**
 * Canonical encoding and signing inputs for house_session control. Request and ACK cores
 * use proto3 binary encoding and contain neither maps nor proto3 optional fields.
 * protobufjs can emit explicit default keys that prost omits; canonicalRequestCore and
 * canonicalAckCore remove those keys before encoding. The shared house_session golden
 * vectors verify cross-language byte equality.
 */

/**
 * ASCII domain separator for request signatures.
 */
export const REQUEST_DOMAIN = 'POPCLAW_HOUSE_SESSION_REQUEST_V1';
/**
 * Domain separator for server acknowledgement signatures.
 */
export const ACK_DOMAIN = 'POPCLAW_HOUSE_SESSION_ACK_V1';

type Core = Record<string, unknown>;

interface Codec {
  encode(message: unknown): { finish(): Uint8Array };
}

function requestCodec(): Codec {
  const ns = (popclaw as unknown as { housesession: { RequestCore: Codec } }).housesession;
  return ns.RequestCore;
}

function ackCodec(): Codec {
  const ns = (popclaw as unknown as { housesession: { AckCore: Codec } }).housesession;
  return ns.AckCore;
}

function isPlainObject(v: unknown): v is Core {
  return typeof v === 'object' && v !== null && !Array.isArray(v) && !(v instanceof Uint8Array);
}

/**
 * Detect protobufjs Long values produced by decoding 64-bit fields or constructed by
 * callers. Check low/high/unsigned and the toNumber method without converting to Number:
 * values above 2^53 would lose precision.
 */
function isLongLike(v: unknown): v is { low: number; high: number; unsigned: boolean } {
  if (!isPlainObject(v)) return false;
  const candidate = v as Record<string, unknown>;
  return (
    typeof candidate.low === 'number' &&
    typeof candidate.high === 'number' &&
    typeof candidate.unsigned === 'boolean' &&
    typeof candidate.toNumber === 'function'
  );
}

/**
 * Remove implicit-default keys (0, empty string/bytes, false, Long(0), null and undefined)
 * to match prost encoding. Preserve nonzero Long values unchanged: the encoder uses
 * low/high without a Number round-trip. Callers must supply Long values, including through
 * fromObject, for integers above 2^53; precision already lost in a JS number cannot be
 * recovered here. Preserve nested-message presence, including empty messages encoded as
 * tag plus zero length, while recursively removing their scalar defaults. Empty repeated
 * arrays emit no bytes and are also removed.
 */
export function stripDefaultKeys(core: Core): Core {
  const out: Core = {};
  for (const key of Object.keys(core)) {
    const value = core[key];
    if (value === null || value === undefined) continue;
    if (typeof value === 'number' && value === 0) continue;
    if (typeof value === 'string' && value === '') continue;
    if (typeof value === 'boolean' && value === false) continue;
    if (value instanceof Uint8Array && value.length === 0) continue;
    if (Array.isArray(value) && value.length === 0) continue;
    if (isLongLike(value)) {
      if (value.low === 0 && value.high === 0) continue; // Long(0) elides like prost
      out[key] = value; // non-zero Long: keep as-is, no number round-trip
      continue;
    }
    if (isPlainObject(value)) {
      out[key] = stripDefaultKeys(value);
      continue;
    }
    out[key] = value;
  }
  return out;
}

/**
 * Canonical proto3 bytes of the request core.
 */
export function canonicalRequestCore(core: Core): Uint8Array {
  return requestCodec().encode(stripDefaultKeys(core)).finish();
}

/**
 * Canonical proto3 bytes of the acknowledgement core.
 */
export function canonicalAckCore(core: Core): Uint8Array {
  return ackCodec().encode(stripDefaultKeys(core)).finish();
}

function domainPrefixed(domain: string, canonical: Uint8Array): Uint8Array {
  const domainBytes = new TextEncoder().encode(domain);
  const out = new Uint8Array(domainBytes.length + canonical.length);
  out.set(domainBytes, 0);
  out.set(canonical, domainBytes.length);
  return out;
}

/**
 * Request signing input: REQUEST_DOMAIN followed by canonical core bytes.
 */
export function requestSigningInput(core: Core): Uint8Array {
  return domainPrefixed(REQUEST_DOMAIN, canonicalRequestCore(core));
}

/**
 * Acknowledgement signing input: ACK_DOMAIN followed by canonical core bytes.
 */
export function ackSigningInput(core: Core): Uint8Array {
  return domainPrefixed(ACK_DOMAIN, canonicalAckCore(core));
}
