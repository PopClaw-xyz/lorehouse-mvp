//! Canonical encoding and signing inputs for house_session control. Request and
//! acknowledgement cores use proto3 binary encoding without maps or proto3 optional
//! fields. prost default elision matches the protobufjs omitted-key convention; the
//! shared house_session golden vectors verify identical bytes. Signing input is the
//! fixed ASCII domain prefix followed by canonical core bytes. Request and ACK domains
//! are distinct and isolate session control from event signatures.

use prost::Message;

use popclaw_contracts::housesession::{AckCore, RequestCore};

/// ASCII request-signature domain separator, without a newline.
pub const REQUEST_DOMAIN: &[u8] = b"POPCLAW_HOUSE_SESSION_REQUEST_V1";
/// Server acknowledgement signature domain separator.
pub const ACK_DOMAIN: &[u8] = b"POPCLAW_HOUSE_SESSION_ACK_V1";

/// Canonical proto3 bytes of the request core.
pub fn canonical_request_bytes(core: &RequestCore) -> Vec<u8> {
    core.encode_to_vec()
}

/// Canonical proto3 bytes of the acknowledgement core.
pub fn canonical_ack_bytes(core: &AckCore) -> Vec<u8> {
    core.encode_to_vec()
}

/// Request signing input: REQUEST_DOMAIN followed by canonical core bytes.
pub fn request_signing_input(core: &RequestCore) -> Vec<u8> {
    let mut out = Vec::with_capacity(REQUEST_DOMAIN.len() + core.encoded_len());
    out.extend_from_slice(REQUEST_DOMAIN);
    out.extend_from_slice(&canonical_request_bytes(core));
    out
}

/// Acknowledgement signing input: ACK_DOMAIN followed by canonical core bytes.
pub fn ack_signing_input(core: &AckCore) -> Vec<u8> {
    let mut out = Vec::with_capacity(ACK_DOMAIN.len() + core.encoded_len());
    out.extend_from_slice(ACK_DOMAIN);
    out.extend_from_slice(&canonical_ack_bytes(core));
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    fn enter_core() -> RequestCore {
        RequestCore {
            operation: popclaw_contracts::housesession::Operation::Enter as i32,
            popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
            installation_id: "11111111-2222-4333-8444-555555555555".into(),
            op_seq: 10,
            request_id: "aaaaaaaa-0000-4000-8000-000000000001".into(),
            house_origin: "https://demo.lorehouse.com".into(),
            issued_at: 1_757_200_000,
            expires_at: 1_757_200_060,
            nonce: "n-0001".into(),
            expected_house_revision: 0,
            target_session_id: String::new(),
            action_id: String::new(),
            action_expires_at: 0,
        }
    }

    #[test]
    fn signing_input_is_domain_prefix_plus_canonical() {
        let core = enter_core();
        let input = request_signing_input(&core);
        assert!(input.starts_with(REQUEST_DOMAIN));
        assert_eq!(
            &input[REQUEST_DOMAIN.len()..],
            &canonical_request_bytes(&core)[..]
        );
    }

    #[test]
    fn canonical_bytes_elide_defaults() {
        // Empty target_session_id and zero expected_house_revision must emit no bytes.
        // For this fixture, fields 10 and 11 are the final populated fields, so the
        // default-elided encoding must be a strict prefix of the encoding with both
        // values set.
        let base = enter_core();
        let defaulted = canonical_request_bytes(&base);
        let mut set = base.clone();
        set.expected_house_revision = 3;
        set.target_session_id = "sess-1".into();
        let with_values = canonical_request_bytes(&set);
        assert!(
            with_values.starts_with(&defaulted),
            "default-valued trailing fields MUST elide entirely"
        );
        assert!(with_values.len() > defaulted.len());
    }

    #[test]
    fn ack_domain_differs_from_request_domain() {
        assert_ne!(REQUEST_DOMAIN, ACK_DOMAIN);
    }
}
