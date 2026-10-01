//! PopClaw cross-language algorithms — canonical / cid / sigil.
//!
//! Contract: every function here MUST produce byte-identical output to its TS
//! twin in `@popclaw/algorithms` for every input in
//! `packages/contracts/fixtures/test-vectors.json`.

pub mod canonical;
pub mod cid;
pub mod crockford;
pub mod house_session;
pub mod sigil;

pub use canonical::canonicalize_envelope;
pub use cid::cid_from_canonical;
pub use crockford::{crockford32_lower, normalize_sigil_input};
pub use house_session::{
    ack_signing_input, canonical_ack_bytes, canonical_request_bytes, request_signing_input,
    ACK_DOMAIN, REQUEST_DOMAIN,
};
pub use sigil::{sigil, SIGIL_LEN};

pub mod public_baseline;
