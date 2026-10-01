import { sha256 } from '@noble/hashes/sha256';
import { crockford32Lower } from './crockford.js';

/**
 * Display length of a derived sigil. Single source of truth — no literal
 * `6`/`8` sigil lengths at call sites.
 */
export const SIGIL_LEN = 8;

/**
 * Sigil — first `len` Crockford base32 chars of SHA-256(popclaw_id as UTF-8),
 * encoded over the FULL 32-byte digest.
 * Matches the Rust implementation in popclaw-algorithms::sigil.
 */
export function sigil(popclawId: string, len: number = SIGIL_LEN): string {
  const bytes = new TextEncoder().encode(popclawId);
  const digest = sha256(bytes);
  const full = crockford32Lower(digest);
  return full.slice(0, len);
}
