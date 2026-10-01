//! Crockford base32 — human-safe short-fingerprint alphabet.
//! Excludes `i`, `l`, `o`, `u` to avoid visual confusion; display is always
//! lowercase. See docs/adr/0015-short-fingerprint-sigil-crockford-b32.md.

const ALPHABET: &[u8; 32] = b"0123456789abcdefghjkmnpqrstvwxyz";

/// Encodes `bytes` as lowercase Crockford base32: MSB-first 5-bit groups,
/// final partial group zero-padded on the right (not left).
pub fn crockford32_lower(bytes: &[u8]) -> String {
    let mut out = String::with_capacity((bytes.len() * 8).div_ceil(5));
    let mut buffer: u32 = 0;
    let mut bit_count: u32 = 0;

    for &byte in bytes {
        buffer = (buffer << 8) | byte as u32;
        bit_count += 8;
        while bit_count >= 5 {
            bit_count -= 5;
            let idx = ((buffer >> bit_count) & 0x1f) as usize;
            out.push(ALPHABET[idx] as char);
        }
        // Drop already-emitted high bits so `buffer` never accumulates past
        // the handful of unconsumed low bits carried into the next byte.
        buffer &= (1 << bit_count) - 1;
    }
    if bit_count > 0 {
        let idx = ((buffer << (5 - bit_count)) & 0x1f) as usize;
        out.push(ALPHABET[idx] as char);
    }
    out
}

/// Normalizes untrusted sigil/prefix input for resolution: trims, lowercases,
/// folds the visually-confusable `o`/`i`/`l` onto their Crockford neighbors,
/// then rejects anything left outside the alphabet (including `u`).
///
/// Does NOT enforce the 6–12 char length window — that's a caller concern
/// (resolve endpoints validate length against the request semantics).
pub fn normalize_sigil_input(s: &str) -> Option<String> {
    let mut out = String::with_capacity(s.len());
    for ch in s.trim().chars() {
        let folded = match ch.to_ascii_lowercase() {
            'o' => '0',
            'i' => '1',
            'l' => '1',
            c => c,
        };
        if !ALPHABET.contains(&(folded as u8)) {
            return None;
        }
        out.push(folded);
    }
    Some(out)
}

#[cfg(test)]
mod tests {
    use sha2::{Digest, Sha256};

    use super::*;

    #[test]
    fn encodes_full_sha256_digest_of_blackfeather() {
        // Known-answer oracle: python crockford32 over sha256("BlackFeather")
        // (see task report for the derivation).
        let digest = Sha256::digest(b"BlackFeather");
        assert_eq!(
            crockford32_lower(&digest),
            "gdx8rgtpj9xsrkm2rmeh48pycejzzwhdnj0htzrmgyzcpkgsjdd0"
        );
    }

    #[test]
    fn empty_input_encodes_to_empty_string() {
        assert_eq!(crockford32_lower(&[]), "");
    }

    #[test]
    fn single_byte_pads_final_partial_group_on_the_right() {
        // 0xff = 11111111 -> groups of 5 MSB-first: 11111 1110(0) -> "z" "w"
        // (11111 = 31 = 'z'; 11100 = 28 = 'w', zero-padded on the right)
        assert_eq!(crockford32_lower(&[0xff]), "zw");
    }

    #[test]
    fn normalize_trims_and_lowercases() {
        assert_eq!(
            normalize_sigil_input("  2FF697AB  ").as_deref(),
            Some("2ff697ab")
        );
    }

    #[test]
    fn normalize_folds_confusable_chars() {
        assert_eq!(normalize_sigil_input("O0Il").as_deref(), Some("0011"));
    }

    #[test]
    fn normalize_rejects_u_and_other_out_of_alphabet_chars() {
        assert_eq!(normalize_sigil_input("abcu1234"), None);
    }
}
