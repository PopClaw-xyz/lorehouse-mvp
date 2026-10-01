//! Reads fixtures/test-vectors.json and re-verifies Rust algorithms.
//!
//! `cid_matches_all_vectors` only hashes the recorded bytes, so for any vector
//! this crate's own generator produced it is a tautology: it cannot tell that
//! `canonicalize_envelope` handles a newly added field correctly, only that
//! sha256 is sha256. `canonical_roundtrip_all_vectors` closes that — it decodes
//! each vector and RE-CANONICALIZES it, so a Rust canonicalizer that dropped a
//! present-but-empty sub-message, or re-ordered a field, goes red here instead
//! of being caught only by the Python and TypeScript suites.

use std::path::PathBuf;

use ed25519_dalek::{Signature, SigningKey, Verifier, VerifyingKey};
use popclaw_algorithms::{canonicalize_envelope, cid_from_canonical, sigil};
use popclaw_contracts::event::EventEnvelope;
use prost::Message;
use serde_json::Value;

fn fixtures_path() -> PathBuf {
    let mut p = std::env::var("CARGO_MANIFEST_DIR")
        .map(PathBuf::from)
        .expect("CARGO_MANIFEST_DIR");
    p.push("../../fixtures/test-vectors.json");
    p.canonicalize().expect("fixtures path exists")
}

fn load() -> Value {
    let text = std::fs::read_to_string(fixtures_path()).expect("read fixtures");
    serde_json::from_str(&text).expect("parse fixtures")
}

#[test]
fn cid_matches_all_vectors() {
    let v = load();
    for entry in v["canonical_serialization"].as_array().unwrap() {
        let canonical_hex = entry["canonical_bytes_hex"].as_str().unwrap();
        let expected_cid = entry["cid"].as_str().unwrap();
        let canonical = hex::decode(canonical_hex).unwrap();
        let actual = cid_from_canonical(&canonical);
        assert_eq!(
            actual,
            expected_cid,
            "cid mismatch for vector `{}`",
            entry["name"].as_str().unwrap_or("?")
        );
    }
}

#[test]
fn sigil_matches_all_vectors() {
    let v = load();
    for entry in v["sigil"].as_array().unwrap() {
        let popclaw_id = entry["popclaw_id"].as_str().unwrap();
        let length = entry["length"].as_u64().unwrap() as usize;
        let expected = entry["expected"].as_str().unwrap();
        let actual = sigil(popclaw_id, length);
        assert_eq!(
            actual, expected,
            "sigil mismatch for popclaw_id={popclaw_id} length={length}"
        );
    }
}

#[test]
fn signature_roundtrips_are_valid() {
    let v = load();
    for entry in v["signature_roundtrip"].as_array().unwrap() {
        let sk_hex = entry["master_private_key_hex"].as_str().unwrap();
        let pk_hex = entry["master_public_key_hex"].as_str().unwrap();
        let canonical_hex = entry["canonical_bytes_hex"].as_str().unwrap();
        let sig_hex = entry["signature_hex"].as_str().unwrap();

        let seed: [u8; 32] = hex::decode(sk_hex).unwrap().try_into().unwrap();
        let sk = SigningKey::from_bytes(&seed);
        let pk = sk.verifying_key();
        assert_eq!(hex::encode(pk.as_bytes()), pk_hex, "pubkey derivation");

        let canonical = hex::decode(canonical_hex).unwrap();
        let sig_bytes: [u8; 64] = hex::decode(sig_hex).unwrap().try_into().unwrap();
        let sig = Signature::from_bytes(&sig_bytes);

        let vk = VerifyingKey::from_bytes(pk.as_bytes()).unwrap();
        vk.verify(&canonical, &sig).expect("signature verifies");
    }
}

/// DM encryption (additive fields 6/7) must not move any existing CID.
///
/// Case 1 (ABSENT) vs case 3 (PRESENT-BUT-EMPTY): proto3 `bytes` defaults elide,
/// so both MUST canonicalize to identical bytes — which is also what makes every
/// DirectMessage signed before fields 6/7 existed still verify.
/// Case 2 (PRESENT) must differ, or the ciphertext isn't actually being carried.
#[test]
fn dm_ciphertext_is_additive_and_elides_when_empty() {
    let v = load();
    let arr = v["canonical_serialization"].as_array().unwrap();
    let get = |name: &str| {
        arr.iter()
            .find(|e| e["name"] == name)
            .unwrap_or_else(|| panic!("missing vector `{name}`"))
    };

    let absent = get("direct_message_minimal");
    let empty = get("direct_message_empty_ciphertext");
    let present = get("direct_message_encrypted");

    assert_eq!(
        absent["canonical_bytes_hex"].as_str().unwrap(),
        empty["canonical_bytes_hex"].as_str().unwrap(),
        "ADR-0003: empty ciphertext/nonce MUST elide — absent and present-but-empty \
         must produce byte-identical canonical bytes"
    );
    assert_eq!(
        absent["cid"].as_str().unwrap(),
        empty["cid"].as_str().unwrap(),
        "CID drift between absent and present-but-empty ciphertext"
    );

    // Regression pin: the pre-encryption DM CID, captured from main before
    // fields 6/7 were added to DirectMessage. If adding a field ever changes
    // this, every DM signature in the wild breaks.
    assert_eq!(
        absent["cid"].as_str().unwrap(),
        "044b3208159b7a326e0a125606997cd11f438456341e3f8e8513a67c4b76e9ef",
        "pre-encryption direct_message_minimal CID changed — ADR-0003 violation"
    );

    assert_ne!(
        absent["cid"].as_str().unwrap(),
        present["cid"].as_str().unwrap(),
        "populated ciphertext MUST change the CID (otherwise it isn't on the wire)"
    );

    // The opposite invariant. ActorInfo.device_id is `optional bytes` — proto3
    // EXPLICIT presence — so an explicitly-empty value MUST be emitted, not
    // elided. Same envelope as direct_message_minimal apart from device_id, so
    // if the two ever match it means someone taught the canonicalizer to drop
    // empty byte arrays unconditionally.
    let device_id_empty = get("actor_device_id_empty");
    assert_ne!(
        absent["cid"].as_str().unwrap(),
        device_id_empty["cid"].as_str().unwrap(),
        "proto3 `optional bytes` tracks presence: an explicitly-empty device_id \
         MUST still be emitted, so it cannot share a CID with the envelope that omits it"
    );
}

#[test]
fn invite_landing_url_changes_cid() {
    let v = load();
    let arr = v["canonical_serialization"].as_array().unwrap();
    let without = arr
        .iter()
        .find(|e| e["name"] == "invite_request_payload_minimal")
        .expect("missing invite_request_payload_minimal");
    let with_url = arr
        .iter()
        .find(|e| e["name"] == "invite_request_with_landing_url")
        .expect("missing invite_request_with_landing_url");
    assert_ne!(
        without["cid"].as_str().unwrap(),
        with_url["cid"].as_str().unwrap(),
        "ADR-0009: empty vs populated landing_url MUST yield different CIDs"
    );
}

/// Decode every recorded ENVELOPE vector and canonicalize it again. The bytes
/// must come back identical, and the CID with them.
///
/// This is the test that actually exercises the Rust canonicalizer against the
/// vector set. A field added to the proto but mishandled here — an elided
/// present-but-empty sub-message, a re-ordered tag — produces different bytes
/// on the way back out and fails, which hashing the recorded bytes never could.
///
/// One vector is deliberately NOT an envelope: `verified_platform_with_account_id`
/// records a standalone VerifiedPlatform message. It is named and counted here
/// rather than filtered loosely, so a second standalone vector — or a rename —
/// makes this test say so instead of silently skipping more.
#[test]
fn canonical_roundtrip_all_envelope_vectors() {
    let v = load();
    let mut checked = 0usize;
    let mut skipped: Vec<String> = Vec::new();
    for entry in v["canonical_serialization"].as_array().unwrap() {
        let name = entry["name"].as_str().unwrap_or("?").to_string();
        let description = entry["input_envelope_description"].as_str().unwrap_or("");
        if description.starts_with("Standalone ") {
            skipped.push(name);
            continue;
        }
        let canonical_hex = entry["canonical_bytes_hex"].as_str().unwrap();
        let recorded = hex::decode(canonical_hex).unwrap();
        let envelope = EventEnvelope::decode(recorded.as_slice())
            .unwrap_or_else(|e| panic!("vector `{name}` does not decode: {e}"));
        let reencoded = canonicalize_envelope(&envelope);
        assert_eq!(
            hex::encode(&reencoded),
            canonical_hex,
            "canonical bytes changed on re-encode for vector `{name}`"
        );
        assert_eq!(
            cid_from_canonical(&reencoded),
            entry["cid"].as_str().unwrap(),
            "cid changed on re-encode for vector `{name}`"
        );
        checked += 1;
    }
    assert_eq!(
        skipped,
        vec!["verified_platform_with_account_id".to_string()],
        "the set of non-envelope vectors changed; update this test on purpose"
    );
    assert!(
        checked >= 32,
        "expected the full envelope vector set, saw {checked}"
    );
}
