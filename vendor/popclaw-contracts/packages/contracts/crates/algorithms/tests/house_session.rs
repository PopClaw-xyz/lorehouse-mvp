//! house_session contract tests consuming fixtures/test-vectors.json. Request and ACK
//! vectors verify canonical bytes, domain-prefixed signing inputs, CIDs, signature
//! verification and deterministic re-signing against the same vectors used by
//! TypeScript. Sequence fixtures validate the structure of required state transitions
//! and races, including legal operation/outcome combinations; they do not execute a
//! server state machine.

use std::path::PathBuf;

use ed25519_dalek::{Signature, SigningKey, Verifier};
use prost::Message;
use serde_json::Value;

use popclaw_algorithms::cid_from_canonical;
use popclaw_algorithms::house_session::{
    ack_signing_input, canonical_ack_bytes, canonical_request_bytes, request_signing_input,
    ACK_DOMAIN, REQUEST_DOMAIN,
};
use popclaw_contracts::housesession::{AckCore, Operation, RequestCore};

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

fn house_session_group() -> Value {
    let v = load();
    v["house_session"].clone()
}

fn operation_from_name(name: &str) -> i32 {
    (match name {
        "ENTER" => Operation::Enter,
        "RENEW" => Operation::Renew,
        "LEAVE" => Operation::Leave,
        "STATUS" => Operation::Status,
        _ => panic!("unknown operation name in fixture: {name}"),
    }) as i32
}

/// Reconstruct RequestCore from language-neutral fixture JSON. Map snake_case wire
/// names explicitly so field-name mismatches fail tests.
fn request_core_from_fixture(entry: &Value) -> RequestCore {
    let c = &entry["core"];
    RequestCore {
        operation: operation_from_name(c["operation"].as_str().unwrap()) as i32,
        popclaw_id: c["popclaw_id"].as_str().unwrap().into(),
        installation_id: c["installation_id"].as_str().unwrap().into(),
        op_seq: c["op_seq"].as_u64().unwrap(),
        request_id: c["request_id"].as_str().unwrap().into(),
        house_origin: c["house_origin"].as_str().unwrap().into(),
        issued_at: c["issued_at"].as_u64().unwrap(),
        expires_at: c["expires_at"].as_u64().unwrap(),
        nonce: c["nonce"].as_str().unwrap().into(),
        expected_house_revision: c["expected_house_revision"].as_u64().unwrap_or(0),
        target_session_id: c
            .get("target_session_id")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .into(),
        action_id: c
            .get("action_id")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .into(),
        action_expires_at: c["action_expires_at"].as_u64().unwrap_or(0),
    }
}

fn ack_core_from_fixture(entry: &Value) -> AckCore {
    let c = &entry["core"];
    let status = c.get("status").filter(|s| !s.is_null()).map(|s| {
        popclaw_contracts::housesession::SessionInfo {
            session_id: s["session_id"].as_str().unwrap().into(),
            house_revision: s["house_revision"].as_u64().unwrap(),
            lease_expires_at: s["lease_expires_at"].as_u64().unwrap(),
            installation_id: s["installation_id"].as_str().unwrap().into(),
            entered_op_seq: s["entered_op_seq"].as_u64().unwrap(),
        }
    });
    AckCore {
        house_origin: c["house_origin"].as_str().unwrap().into(),
        popclaw_id: c["popclaw_id"].as_str().unwrap().into(),
        installation_id: c["installation_id"].as_str().unwrap().into(),
        request_id: c["request_id"].as_str().unwrap().into(),
        op_seq: c["op_seq"].as_u64().unwrap(),
        operation: operation_from_name(c["operation"].as_str().unwrap()),
        outcome: outcome_from_name(c["outcome"].as_str().unwrap()),
        error_code: c
            .get("error_code")
            .and_then(|v| v.as_str())
            .map(error_code_from_name)
            .unwrap_or(0),
        house_revision: c["house_revision"].as_u64().unwrap(),
        session_id: c
            .get("session_id")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .into(),
        session_active: c["session_active"].as_bool().unwrap_or(false),
        lease_expires_at: c["lease_expires_at"].as_u64().unwrap_or(0),
        server_committed_at: c["server_committed_at"].as_u64().unwrap_or(0),
        status,
        detail: c
            .get("detail")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .into(),
        inbox_read_token: c
            .get("inbox_read_token")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .into(),
    }
}

fn outcome_from_name(name: &str) -> i32 {
    use popclaw_contracts::housesession::Outcome;
    (match name {
        "ENTERED" => Outcome::Entered,
        "ALREADY_ENTERED" => Outcome::AlreadyEntered,
        "RENEWED" => Outcome::Renewed,
        "CLOSED" => Outcome::Closed,
        "ALREADY_CLOSED" => Outcome::AlreadyClosed,
        "SUPERSEDED" => Outcome::Superseded,
        "REJECTED" => Outcome::Rejected,
        "REPORTED" => Outcome::Reported,
        _ => panic!("unknown outcome name in fixture: {name}"),
    }) as i32
}

fn error_code_from_name(name: &str) -> i32 {
    use popclaw_contracts::housesession::ErrorCode;
    (match name {
        "INVALID_HOUSE" => ErrorCode::InvalidHouse,
        "HOUSE_LIFECYCLE_UNSUPPORTED" => ErrorCode::HouseLifecycleUnsupported,
        "HOUSE_DISABLED" => ErrorCode::HouseDisabled,
        "EXECUTOR_BUSY" => ErrorCode::ExecutorBusy,
        "STALE_OPERATION" => ErrorCode::StaleOperation,
        "SESSION_FENCED" => ErrorCode::SessionFenced,
        "LEASE_EXPIRED" => ErrorCode::LeaseExpired,
        "AUTH_INVALID" => ErrorCode::AuthInvalid,
        "AUDIENCE_MISMATCH" => ErrorCode::AudienceMismatch,
        "IDEMPOTENCY_CONFLICT" => ErrorCode::IdempotencyConflict,
        "PERSISTENCE_FAILED" => ErrorCode::PersistenceFailed,
        "ACTION_RESULT_UNKNOWN" => ErrorCode::ActionResultUnknown,
        _ => panic!("unknown error code name in fixture: {name}"),
    }) as i32
}

#[test]
fn domain_separators_are_fixed_length_and_distinct() {
    assert_eq!(REQUEST_DOMAIN, b"POPCLAW_HOUSE_SESSION_REQUEST_V1");
    assert_eq!(ACK_DOMAIN, b"POPCLAW_HOUSE_SESSION_ACK_V1");
    assert_ne!(REQUEST_DOMAIN, ACK_DOMAIN);
    assert!(!REQUEST_DOMAIN.is_empty() && !ACK_DOMAIN.is_empty());
}

#[test]
fn request_vectors_canonical_bytes_and_signatures_hold() {
    let group = house_session_group();
    let entries = group["requests"].as_array().expect("requests array");
    assert!(
        !entries.is_empty(),
        "house_session.requests must not be empty"
    );

    for entry in entries {
        let name = entry["name"].as_str().unwrap();
        let core = request_core_from_fixture(entry);
        let canonical = canonical_request_bytes(&core);
        assert_eq!(
            hex::encode(&canonical),
            entry["canonical_bytes_hex"].as_str().unwrap(),
            "canonical bytes mismatch for request vector `{name}`"
        );

        let signing_input = request_signing_input(&core);
        assert_eq!(
            hex::encode(&signing_input),
            entry["signing_input_hex"].as_str().unwrap(),
            "signing input mismatch for request vector `{name}`"
        );
        assert!(
            signing_input.starts_with(REQUEST_DOMAIN),
            "signing input must start with the request domain separator (`{name}`)"
        );
        assert_eq!(
            signing_input.len(),
            REQUEST_DOMAIN.len() + canonical.len(),
            "signing input = domain || canonical bytes (`{name}`)"
        );

        assert_eq!(
            cid_from_canonical(&canonical),
            entry["cid"].as_str().unwrap(),
            "cid mismatch for request vector `{name}`"
        );

        let seed: [u8; 32] = hex::decode(entry["signer_seed_hex"].as_str().unwrap())
            .unwrap()
            .try_into()
            .unwrap();
        let sk = SigningKey::from_bytes(&seed);
        assert_eq!(
            hex::encode(sk.verifying_key().as_bytes()),
            entry["signer_pubkey_hex"].as_str().unwrap(),
            "pubkey derivation for `{name}`"
        );

        // Identity binding: except for explicit negative vectors, core.popclaw_id must
        // be the base58 encoding of the signer public key, as required by /v1/house-
        // session.
        let signer_b58 = bs58::encode(sk.verifying_key().as_bytes()).into_string();
        let expect_match = entry
            .get("expect_signer_match")
            .and_then(|v| v.as_bool())
            .unwrap_or(true);
        if expect_match {
            assert_eq!(
                core.popclaw_id, signer_b58,
                "positive vector `{name}` must bind actor to the signer key"
            );
        } else {
            assert_ne!(
                core.popclaw_id, signer_b58,
                "negative vector `{name}` must actually mismatch (else it pins nothing)"
            );
            assert_eq!(name, "signer_mismatch_rejected");
        }

        let sig_bytes: [u8; 64] = hex::decode(entry["signature_hex"].as_str().unwrap())
            .unwrap()
            .try_into()
            .unwrap();
        let sig = Signature::from_bytes(&sig_bytes);
        sk.verifying_key()
            .verify(&signing_input, &sig)
            .unwrap_or_else(|e| panic!("signature does not verify for `{name}`: {e}"));

        // Deterministic re-sign must be byte-identical (pins the signing input,
        // not just the key).
        use ed25519_dalek::Signer;
        assert_eq!(
            hex::encode(sk.sign(&signing_input).to_bytes()),
            entry["signature_hex"].as_str().unwrap(),
            "re-sign mismatch for `{name}`"
        );
    }
}

#[test]
fn request_vectors_round_trip_through_decode() {
    let group = house_session_group();
    let entries = group["requests"].as_array().unwrap();
    for entry in entries {
        let name = entry["name"].as_str().unwrap();
        let canonical = hex::decode(entry["canonical_bytes_hex"].as_str().unwrap()).unwrap();
        let decoded = RequestCore::decode(canonical.as_slice())
            .unwrap_or_else(|e| panic!("decode failed for `{name}`: {e}"));
        assert_eq!(
            hex::encode(canonical_request_bytes(&decoded)),
            entry["canonical_bytes_hex"].as_str().unwrap(),
            "decode→encode not stable for `{name}`"
        );
    }
}

#[test]
fn ack_vectors_canonical_bytes_and_signatures_hold() {
    let group = house_session_group();
    let entries = group["acks"].as_array().expect("acks array");
    assert!(!entries.is_empty(), "house_session.acks must not be empty");

    for entry in entries {
        let name = entry["name"].as_str().unwrap();
        let core = ack_core_from_fixture(entry);
        let canonical = canonical_ack_bytes(&core);
        assert_eq!(
            hex::encode(&canonical),
            entry["canonical_bytes_hex"].as_str().unwrap(),
            "canonical bytes mismatch for ack vector `{name}`"
        );

        let signing_input = ack_signing_input(&core);
        assert_eq!(
            hex::encode(&signing_input),
            entry["signing_input_hex"].as_str().unwrap(),
            "signing input mismatch for ack vector `{name}`"
        );
        assert!(signing_input.starts_with(ACK_DOMAIN));

        assert_eq!(
            cid_from_canonical(&canonical),
            entry["cid"].as_str().unwrap(),
            "cid mismatch for ack vector `{name}`"
        );

        let seed: [u8; 32] = hex::decode(entry["signer_seed_hex"].as_str().unwrap())
            .unwrap()
            .try_into()
            .unwrap();
        let sk = SigningKey::from_bytes(&seed);
        let sig_bytes: [u8; 64] = hex::decode(entry["signature_hex"].as_str().unwrap())
            .unwrap()
            .try_into()
            .unwrap();
        use ed25519_dalek::Signer;
        sk.verifying_key()
            .verify(&signing_input, &Signature::from_bytes(&sig_bytes))
            .unwrap_or_else(|e| panic!("ack signature does not verify for `{name}`: {e}"));
        assert_eq!(
            hex::encode(sk.sign(&signing_input).to_bytes()),
            entry["signature_hex"].as_str().unwrap(),
            "ack re-sign mismatch for `{name}`"
        );
    }
}

/// Enter default-elision boundary: expected_house_revision=0 and target_session_id=""
/// emit no bytes, matching prost. Clients supplying explicit defaults must obtain
/// identical canonical bytes; TypeScript tests cover that side using the same vector.
#[test]
fn request_defaults_elide_from_canonical_bytes() {
    let group = house_session_group();
    let entries = group["requests"].as_array().unwrap();
    let minimal = entries
        .iter()
        .find(|e| e["name"] == "enter_minimal")
        .expect("enter_minimal vector present");
    let boundaries = entries
        .iter()
        .find(|e| e["name"] == "default_boundaries")
        .expect("default_boundaries vector present");

    assert_eq!(
        minimal["canonical_bytes_hex"].as_str().unwrap(),
        boundaries["canonical_bytes_hex"].as_str().unwrap(),
        "explicit proto3 defaults MUST elide — enter_minimal and default_boundaries must share bytes"
    );

    // And the boundary vector explicitly declares it set them.
    let core = &boundaries["core"];
    assert_eq!(core["expected_house_revision"].as_u64(), Some(0));
    assert_eq!(core["target_session_id"].as_str(), Some(""));
}

// Sequence fixtures for protocol race examples.

fn legal_outcomes_for(op: &str) -> &'static [&'static str] {
    match op {
        "ENTER" => &["ENTERED", "ALREADY_ENTERED", "REJECTED"],
        "RENEW" => &["RENEWED", "REJECTED"],
        "LEAVE" => &["CLOSED", "ALREADY_CLOSED", "SUPERSEDED", "REJECTED"],
        "STATUS" => &["REPORTED", "REJECTED"],
        _ => panic!("unknown op {op}"),
    }
}

#[test]
fn sequences_are_structurally_valid() {
    let group = house_session_group();
    let sequences = group["sequences"].as_array().expect("sequences array");
    assert!(!sequences.is_empty());

    for seq in sequences {
        let name = seq["name"].as_str().unwrap();
        let steps = seq["steps"]
            .as_array()
            .unwrap_or_else(|| panic!("{name}: steps"));
        assert!(!steps.is_empty(), "{name}: no steps");

        for (i, step) in steps.iter().enumerate() {
            let op = step["op"]
                .as_str()
                .unwrap_or_else(|| panic!("{name} step {i}: op"));
            let outcome = step["expected_outcome"]
                .as_str()
                .unwrap_or_else(|| panic!("{name} step {i}: expected_outcome"));
            assert!(
                legal_outcomes_for(op).contains(&outcome),
                "{name} step {i}: outcome {outcome} not legal for op {op}"
            );
            assert!(
                step["op_seq"].as_u64().is_some(),
                "{name} step {i}: op_seq required"
            );
            assert!(
                step["request_id"].as_str().is_some(),
                "{name} step {i}: request_id required"
            );
            assert!(
                step["installation_id"].as_str().is_some(),
                "{name} step {i}: installation_id required"
            );
            // Rejections require an error code; other outcomes must omit it.
            let err = step.get("expected_error_code").and_then(|v| v.as_str());
            if outcome == "REJECTED" {
                assert!(
                    err.is_some(),
                    "{name} step {i}: REJECTED must carry error_code"
                );
            } else {
                assert!(
                    err.is_none(),
                    "{name} step {i}: non-REJECTED must not carry error_code"
                );
            }
        }
    }
}

/// Require the three race examples: two logins around a delayed logout in actual
/// delivery order, logout before an unacknowledged enter, and retry after a lost ACK.
#[test]
fn mandated_race_examples_are_pinned() {
    let group = house_session_group();
    let names: Vec<&str> = group["sequences"]
        .as_array()
        .unwrap()
        .iter()
        .map(|s| s["name"].as_str().unwrap())
        .collect();

    for required in [
        "enter_rotated_enter_late_leave",
        "leave_before_enter_commit",
        "leave_ack_lost_retry",
    ] {
        assert!(
            names.contains(&required),
            "mandated protocol example `{required}` missing from sequences (had: {names:?})"
        );
    }
}

/// Delivery semantics follow actual server processing order. A first delivery must use
/// an unseen request_id. A replay must reference an earlier first delivery and return
/// ALREADY_*. SUPERSEDED must be a first delivery: a committed request replays its
/// stored outcome instead of being reclassified.
#[test]
fn sequences_delivery_semantics_are_consistent() {
    let group = house_session_group();
    for seq in group["sequences"].as_array().unwrap() {
        let name = seq["name"].as_str().unwrap();
        let mut seen_first: Vec<&str> = Vec::new();
        for (i, step) in seq["steps"].as_array().unwrap().iter().enumerate() {
            let delivery = step["delivery"]
                .as_str()
                .unwrap_or_else(|| panic!("{name} step {i}: delivery field required"));
            let request_id = step["request_id"].as_str().unwrap();
            let outcome = step["expected_outcome"].as_str().unwrap();
            match delivery {
                "first" => {
                    assert!(
                        !seen_first.contains(&request_id),
                        "{name} step {i}: request {request_id} delivered first twice"
                    );
                    seen_first.push(request_id);
                }
                "replay" => {
                    assert!(
                        seen_first.contains(&request_id),
                        "{name} step {i}: replay of a request never delivered first"
                    );
                    assert!(
                        outcome.starts_with("ALREADY"),
                        "{name} step {i}: replay outcome must be ALREADY_*, got {outcome}"
                    );
                }
                other => panic!("{name} step {i}: unknown delivery {other:?}"),
            }
            if outcome == "SUPERSEDED" {
                assert_eq!(
                    delivery, "first",
                    "{name} step {i}: SUPERSEDED must be a first delivery, not a replay"
                );
            }
        }
    }
}

/// A late leave must not close a newer session. Its first delivery returns SUPERSEDED,
/// and the new generation remains session_active=true.
#[test]
fn late_leave_example_ends_with_new_session_alive() {
    let group = house_session_group();
    let seq = group["sequences"]
        .as_array()
        .unwrap()
        .iter()
        .find(|s| s["name"] == "enter_rotated_enter_late_leave")
        .unwrap();
    let steps = seq["steps"].as_array().unwrap();
    let last = steps.last().unwrap();
    assert_eq!(last["op"].as_str(), Some("LEAVE"));
    assert_eq!(last["delivery"].as_str(), Some("first"));
    assert_eq!(last["expected_outcome"].as_str(), Some("SUPERSEDED"));
    // The second enter must rotate the generation (ENTERED), rather than reuse it as
    // ALREADY_ENTERED.
    assert_eq!(steps[1]["expected_outcome"].as_str(), Some("ENTERED"));
    let note = seq["description"].as_str().unwrap_or("");
    assert!(
        note.contains("session_active") && note.contains("rotation"),
        "description must state the rotation rule and the session_active assertion"
    );
}
