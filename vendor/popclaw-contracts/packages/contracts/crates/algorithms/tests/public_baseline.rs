use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use popclaw_algorithms::{
    canonicalize_envelope, cid_from_canonical,
    public_baseline::{check_envelope_wire, check_public_envelope_structure},
};
use popclaw_contracts::{
    event::{EventEnvelope, VerifiedPlatform},
    identity::SignedPayload,
};
use prost::Message;
use serde_json::Value;
fn vectors() -> Value {
    serde_json::from_str(include_str!("../../../fixtures/public-baseline.json")).unwrap()
}
#[test]
fn original_wire_positive_and_adversarial_matrix() {
    for v in vectors()["wire"].as_array().unwrap() {
        let raw = hex::decode(v["wire_hex"].as_str().unwrap()).unwrap();
        assert_eq!(
            check_envelope_wire(&raw).is_ok(),
            v["structural"].as_bool().unwrap(),
            "structural {}",
            v["name"]
        );
        assert_eq!(
            check_public_envelope_structure(&raw).is_ok(),
            v["public"].as_bool().unwrap(),
            "public {}",
            v["name"]
        );
    }
}
#[test]
fn invite_wait_singular_fields_report_duplicate_field() {
    let all = vectors();
    for name in [
        "invite_wait_duplicate_mode",
        "invite_wait_duplicate_cancel_task",
        "invite_wait_duplicate_progress",
        "invite_wait_duplicate_dispatch_mode",
        "invite_wait_duplicate_progress_revision",
    ] {
        let v = all["wire"]
            .as_array().unwrap().iter()
            .find(|v| v["name"] == name).unwrap_or_else(|| panic!("missing vector {name}"));
        let raw = hex::decode(v["wire_hex"].as_str().unwrap()).unwrap();
        assert_eq!(check_envelope_wire(&raw), Err("DUPLICATE_FIELD"), "{name}");
    }
}
#[test]
fn shared_signed_bytes_cid_signature_and_outer_wrapper() {
    for v in vectors()["signed"].as_array().unwrap() {
        let raw = hex::decode(v["wire_hex"].as_str().unwrap()).unwrap();
        check_envelope_wire(&raw).unwrap();
        let env = EventEnvelope::decode(raw.as_slice()).unwrap();
        let canonical = canonicalize_envelope(&env);
        assert_eq!(
            hex::encode(&canonical),
            v["canonical_hex"].as_str().unwrap(),
            "{}",
            v["name"]
        );
        assert_eq!(cid_from_canonical(&canonical), v["cid"].as_str().unwrap());
        let pk: [u8; 32] = hex::decode(v["public_key_hex"].as_str().unwrap())
            .unwrap()
            .try_into()
            .unwrap();
        let key = VerifyingKey::from_bytes(&pk).unwrap();
        let sig = Signature::from_slice(&env.signature).unwrap();
        key.verify(&canonical, &sig).unwrap();
        let mut tampered = canonical.clone();
        let last = tampered.len() - 1;
        tampered[last] ^= 1;
        assert!(key.verify(&tampered, &sig).is_err());
        let wrapper = SignedPayload::decode(
            hex::decode(v["signed_payload_hex"].as_str().unwrap())
                .unwrap()
                .as_slice(),
        )
        .unwrap();
        assert_eq!(wrapper.payload, raw);
        assert_eq!(wrapper.signer_pubkey, pk);
        key.verify(&raw, &Signature::from_slice(&wrapper.signature).unwrap())
            .unwrap();
    }
}
#[test]
fn retained_codec_roundtrip_does_not_rewrite_bytes() {
    let old: Value =
        serde_json::from_str(include_str!("../../../fixtures/test-vectors.json")).unwrap();
    for v in old["canonical_serialization"].as_array().unwrap() {
        let raw = hex::decode(v["canonical_bytes_hex"].as_str().unwrap()).unwrap();
        if v["name"] == "verified_platform_with_account_id" {
            assert_eq!(
                VerifiedPlatform::decode(raw.as_slice())
                    .unwrap()
                    .encode_to_vec(),
                raw
            );
        } else {
            check_envelope_wire(&raw).unwrap();
            assert_eq!(
                canonicalize_envelope(&EventEnvelope::decode(raw.as_slice()).unwrap()),
                raw,
                "{}",
                v["name"]
            );
        }
    }
}
#[test]
fn retained_world_signing_rules() {
    use popclaw_contracts::world::*;
    let golden: Value = serde_json::from_str(include_str!(
        "../../../fixtures/retained-signing-golden.json"
    ))
    .unwrap();
    for v in golden["vectors"].as_array().unwrap() {
        let raw = hex::decode(v["signed_core_bytes_hex"].as_str().unwrap()).unwrap();
        macro_rules! round {
            ($ty:ty) => {
                <$ty>::decode(raw.as_slice()).unwrap().encode_to_vec()
            };
        }
        let encoded = match v["type"].as_str().unwrap() {
            "ManifestProof" => round!(ManifestProof),
            "ActionResult" => round!(ActionResult),
            "SubscriptionObservation" => round!(SubscriptionObservation),
            "ActionStatusRequest" => round!(ActionStatusRequest),
            "ExecutionPermit" => round!(ExecutionPermit),
            "WorkerResult" => round!(WorkerResult),
            "ClosureQueryRequest" => round!(ClosureQueryRequest),
            "ClosureObservation" => round!(ClosureObservation),
            _ => panic!("unreviewed golden type"),
        };
        assert_eq!(encoded, raw, "{}", v["type"]);
        assert_eq!(cid_from_canonical(&raw), v["sha256"].as_str().unwrap());
        let pk: [u8; 32] = hex::decode(v["signer_public_key_hex"].as_str().unwrap())
            .unwrap()
            .try_into()
            .unwrap();
        let key = VerifyingKey::from_bytes(&pk).unwrap();
        let sig =
            Signature::from_slice(&hex::decode(v["signature_hex"].as_str().unwrap()).unwrap())
                .unwrap();
        let mut msg = v["domain"].as_str().unwrap().as_bytes().to_vec();
        msg.extend(&raw);
        key.verify(&msg, &sig).unwrap();
        msg[0] ^= 1;
        assert!(key.verify(&msg, &sig).is_err());
    }
}
#[test]
fn valid_signature_does_not_make_reserved_structure_supported() {
    let all = vectors();
    let v = &all["signed_reserved"];
    let core = hex::decode(v["canonical_hex"].as_str().unwrap()).unwrap();
    let raw = hex::decode(v["wire_hex"].as_str().unwrap()).unwrap();
    let pk: [u8; 32] = hex::decode(v["public_key_hex"].as_str().unwrap())
        .unwrap()
        .try_into()
        .unwrap();
    let key = VerifyingKey::from_bytes(&pk).unwrap();
    let sig =
        Signature::from_slice(&hex::decode(v["signature_hex"].as_str().unwrap()).unwrap()).unwrap();
    key.verify(&core, &sig).unwrap();
    assert_eq!(check_envelope_wire(&raw), Err("RESERVED_OCCURRENCE"));
    let stripped = canonicalize_envelope(&EventEnvelope::decode(raw.as_slice()).unwrap());
    assert_ne!(cid_from_canonical(&stripped), v["cid"].as_str().unwrap());
    assert!(key.verify(&stripped, &sig).is_err());
}
