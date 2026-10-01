use sha2::{Digest, Sha256};

/// Computes the PopClaw CID over already-canonicalized bytes.
pub fn cid_from_canonical(canonical: &[u8]) -> String {
    let digest = Sha256::digest(canonical);
    hex::encode(digest)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_input_has_known_sha256() {
        // SHA-256("") = e3b0c442...
        let cid = cid_from_canonical(&[]);
        assert_eq!(
            cid,
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
        assert_eq!(cid.len(), 64);
    }

    #[test]
    fn cid_is_lowercase_hex() {
        let cid = cid_from_canonical(b"hello");
        assert!(cid
            .chars()
            .all(|c| c.is_ascii_hexdigit() && !c.is_ascii_uppercase()));
    }
}
