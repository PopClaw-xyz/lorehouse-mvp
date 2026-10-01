/**
 * Crockford base32 — human-safe short-fingerprint alphabet.
 * Excludes `i`, `l`, `o`, `u` to avoid visual confusion; display is always
 * lowercase. Mirrors the Rust implementation in popclaw-algorithms::crockford.
 */
const ALPHABET = '0123456789abcdefghjkmnpqrstvwxyz';
const ALPHABET_SET = new Set(ALPHABET);

/**
 * Encodes `bytes` as lowercase Crockford base32: MSB-first 5-bit groups,
 * final partial group zero-padded on the right (not left).
 */
export function crockford32Lower(bytes: Uint8Array): string {
  let out = '';
  let buffer = 0;
  let bitCount = 0;

  for (const byte of bytes) {
    buffer = (buffer << 8) | byte;
    bitCount += 8;
    while (bitCount >= 5) {
      bitCount -= 5;
      const idx = (buffer >> bitCount) & 0x1f;
      out += ALPHABET[idx];
    }
    // Drop already-emitted high bits so `buffer` never accumulates past the
    // handful of unconsumed low bits carried into the next byte.
    buffer &= (1 << bitCount) - 1;
  }
  if (bitCount > 0) {
    const idx = (buffer << (5 - bitCount)) & 0x1f;
    out += ALPHABET[idx];
  }
  return out;
}

/**
 * Normalizes untrusted sigil/prefix input for resolution: trims, lowercases,
 * folds the visually-confusable `o`/`i`/`l` onto their Crockford neighbors,
 * then rejects anything left outside the alphabet (including `u`).
 *
 * Does NOT enforce the 6-12 char length window — that's a caller concern
 * (resolve endpoints validate length against the request semantics).
 */
export function normalizeSigilInput(s: string): string | null {
  let out = '';
  for (const ch of s.trim().toLowerCase()) {
    const folded = ch === 'o' ? '0' : ch === 'i' ? '1' : ch === 'l' ? '1' : ch;
    if (!ALPHABET_SET.has(folded)) return null;
    out += folded;
  }
  return out;
}
