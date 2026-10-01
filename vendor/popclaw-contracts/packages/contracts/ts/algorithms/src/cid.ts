import { sha256 } from '@noble/hashes/sha256';

/** CID — lowercase hex of SHA-256(canonical_bytes). 64 chars. */
export function cidFromCanonical(canonical: Uint8Array): string {
  const digest = sha256(canonical);
  let s = '';
  for (const b of digest) s += b.toString(16).padStart(2, '0');
  return s;
}
