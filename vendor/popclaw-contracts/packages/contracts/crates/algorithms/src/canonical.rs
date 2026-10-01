use popclaw_contracts::event::EventEnvelope;
use prost::Message;

/// Serializes an EventEnvelope with `event_id` cleared and `signature` cleared
/// to its canonical proto3 byte form.
pub fn canonicalize_envelope(envelope: &EventEnvelope) -> Vec<u8> {
    let mut copy = envelope.clone();
    copy.event_id = String::new();
    copy.signature = Vec::new();
    copy.encode_to_vec()
}

#[cfg(test)]
mod tests {
    use super::*;
    use popclaw_contracts::event::{
        content_block, event_envelope, ContentBlock, EventEnvelope, Post,
    };
    use popclaw_contracts::identity::ActorInfo;

    fn sample_envelope() -> EventEnvelope {
        EventEnvelope {
            event_id: String::new(),
            actor: Some(ActorInfo {
                popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
                nickname: "BlackFeather".into(),
                supersedes: None,
                device_id: None,
                role: None,
            }),
            target: None,
            lorehouse: String::new(),
            timestamp: 1_713_657_600,
            signature: Vec::new(),
            prev_event_id: String::new(),
            body: Some(event_envelope::Body::Post(Post {
                blocks: vec![ContentBlock {
                    block_type: content_block::Type::Text as i32,
                    content: "canonical test".into(),
                    metadata: Default::default(),
                }],
                media: vec![],
                origin: None,
            })),
        }
    }

    #[test]
    fn canonicalize_is_deterministic() {
        let e = sample_envelope();
        let a = canonicalize_envelope(&e);
        let b = canonicalize_envelope(&e);
        assert_eq!(a, b, "canonical serialization must be deterministic");
        assert!(!a.is_empty(), "canonical bytes must not be empty");
    }

    #[test]
    fn canonicalize_strips_event_id_and_signature() {
        let mut e = sample_envelope();
        let base = canonicalize_envelope(&e);

        e.event_id = "deadbeef".into();
        e.signature = b"not-a-signature".to_vec();
        let after = canonicalize_envelope(&e);

        assert_eq!(base, after, "event_id and signature must be ignored");
    }
}
