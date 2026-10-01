//! Federation spec (2026-07-26) — Layer 2 extension slots, Rust side.
//!
//! The cross-language claim being pinned: the exact canonical bytes that
//! `canonical-parity.test.ts` reproduces with pbjs are the bytes prost decodes
//! back into the same kind / schema_version / opaque body. Both ends read the
//! same `fixtures/test-vectors.json` hex, so a divergence on either encoder
//! fails on one side or the other.

use std::path::PathBuf;

use popclaw_algorithms::cid_from_canonical;
use popclaw_contracts::event::{event_envelope, EventEnvelope};
use prost::Message as _;
use serde_json::Value;

fn vector(name: &str) -> (Vec<u8>, String) {
    let mut p = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR"));
    p.push("../../fixtures/test-vectors.json");
    let text = std::fs::read_to_string(p).expect("read fixtures");
    let v: Value = serde_json::from_str(&text).expect("parse fixtures");
    let entry = v["canonical_serialization"]
        .as_array()
        .unwrap()
        .iter()
        .find(|e| e["name"] == name)
        .unwrap_or_else(|| panic!("vector `{name}` missing from fixtures"))
        .clone();
    (
        hex::decode(entry["canonical_bytes_hex"].as_str().unwrap()).unwrap(),
        entry["cid"].as_str().unwrap().to_string(),
    )
}

fn body_of(name: &str) -> event_envelope::Body {
    let (bytes, cid) = vector(name);
    // The fixture CID must be the hash of the fixture bytes — otherwise the
    // vector itself is stale and the parity claim is vacuous.
    assert_eq!(cid_from_canonical(&bytes), cid, "stale fixture for {name}");
    EventEnvelope::decode(bytes.as_slice())
        .unwrap_or_else(|e| panic!("prost decode failed for {name}: {e}"))
        .body
        .unwrap_or_else(|| panic!("{name} decoded with no body"))
}

#[test]
fn house_event_minimal_decodes_with_opaque_body_intact() {
    let event_envelope::Body::HouseEvent(he) = body_of("house_event_minimal") else {
        panic!("expected HouseEvent body");
    };
    assert_eq!(he.kind, "world.postcard");
    assert_eq!(he.schema_version, 1);
    assert_eq!(
        he.body,
        vec![0x7b, 0x22, 0x74, 0x6f, 0x22, 0x3a, 0x00, 0xff, 0x7d]
    );
}

#[test]
fn house_event_default_boundaries_decode_as_defaults() {
    let event_envelope::Body::HouseEvent(he) = body_of("house_event_default_boundaries") else {
        panic!("expected HouseEvent body");
    };
    assert_eq!(he.kind, "world.encounter");
    assert_eq!(he.schema_version, 0);
    assert!(he.body.is_empty());
}

#[test]
fn intent_minimal_decodes_with_opaque_params_intact() {
    let event_envelope::Body::Intent(intent) = body_of("intent_minimal") else {
        panic!("expected Intent body");
    };
    assert_eq!(intent.lorehouse, "world");
    assert_eq!(intent.intent_kind, "world.pack_and_travel");
    assert_eq!(intent.params, br#"{"destination":"kyoto"}"#.to_vec());
}

#[test]
fn intent_default_boundaries_decode_as_defaults() {
    let event_envelope::Body::Intent(intent) = body_of("intent_default_boundaries") else {
        panic!("expected Intent body");
    };
    assert!(intent.lorehouse.is_empty());
    assert_eq!(intent.intent_kind, "world.look_around");
    assert!(intent.params.is_empty());
}

#[test]
fn reencoding_a_decoded_house_event_is_byte_identical() {
    // Opacity in the strict sense: prost must not normalise, reorder or
    // re-frame anything inside `body`. Decode → encode is a fixed point, so a
    // relaying lore-house can forward the bytes without invalidating the CID.
    for name in [
        "house_event_minimal",
        "house_event_default_boundaries",
        "intent_minimal",
        "intent_default_boundaries",
    ] {
        let (bytes, _) = vector(name);
        let reencoded = EventEnvelope::decode(bytes.as_slice())
            .unwrap()
            .encode_to_vec();
        assert_eq!(reencoded, bytes, "re-encode drifted for {name}");
    }
}
