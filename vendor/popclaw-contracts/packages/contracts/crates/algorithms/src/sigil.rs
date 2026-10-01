use sha2::{Digest, Sha256};

use crate::crockford::crockford32_lower;

/// Display length of a derived sigil. Single source of truth — no literal
/// `6`/`8` sigil lengths at call sites.
pub const SIGIL_LEN: usize = 8;

/// Sigil — first `len` Crockford base32 chars of SHA-256(popclaw_id utf-8),
/// encoded over the FULL 32-byte digest.
pub fn sigil(popclaw_id: &str, len: usize) -> String {
    let digest = Sha256::digest(popclaw_id.as_bytes());
    let full = crockford32_lower(&digest);
    full.chars().take(len).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sigil_matches_hand_computed_value() {
        // SHA-256("BlackFeather") crockford32-lower, first 8 chars.
        // Oracle: python crockford32 over the full digest (see task report).
        let s = sigil("BlackFeather", SIGIL_LEN);
        assert_eq!(s, "gdx8rgtp");
    }

    #[test]
    fn sigil_len_defaults_to_eight() {
        assert_eq!(SIGIL_LEN, 8);
    }

    #[test]
    fn sigil_length_varies() {
        let full = sigil("BlackFeather", 16);
        assert_eq!(full.len(), 16);
        assert!(full.starts_with("gdx8rgtp"));
    }

    #[test]
    fn sigil_prefix_stability_across_lengths() {
        let six = sigil("BlackFeather", 6);
        let eight = sigil("BlackFeather", SIGIL_LEN);
        let twelve = sigil("BlackFeather", 12);
        assert!(twelve.starts_with(&eight));
        assert!(eight.starts_with(&six));
    }

    #[test]
    fn sigil_different_inputs_differ() {
        assert_ne!(sigil("A", 6), sigil("B", 6));
    }
}
