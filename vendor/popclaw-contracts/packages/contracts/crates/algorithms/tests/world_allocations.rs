use popclaw_algorithms::canonicalize_envelope;
use popclaw_contracts::{
    event::{event_envelope, EventEnvelope, HouseEvent, IntentPayload, WorldStreamFrame},
    world::IntentContext,
};
use prost::Message;

fn intent(context: Option<IntentContext>, kind: &str) -> EventEnvelope {
    EventEnvelope {
        body: Some(event_envelope::Body::Intent(IntentPayload {
            intent_kind: kind.into(),
            context,
            ..Default::default()
        })),
        ..Default::default()
    }
}

#[test]
fn intent_context_matches_typescript_exact_bytes() {
    assert_eq!(
        hex::encode(canonicalize_envelope(&intent(None, "example.act"))),
        "9a020d120b6578616d706c652e616374"
    );
    let context = IntentContext {
        house_origin: "https://a.invalid".into(),
        session_id: "s".into(),
        valid_until: 99,
        ..Default::default()
    };
    assert_eq!(
        hex::encode(canonicalize_envelope(&intent(Some(context), "example.act"))),
        "9a0227120b6578616d706c652e61637422180a1168747470733a2f2f612e696e76616c69642201734063"
    );
    assert_eq!(
        hex::encode(canonicalize_envelope(&intent(
            Some(IntentContext::default()),
            ""
        ))),
        "9a02022200"
    );
    let large = IntentContext {
        valid_until: 9_007_199_254_740_993,
        ..Default::default()
    };
    assert_eq!(
        hex::encode(canonicalize_envelope(&intent(Some(large), ""))),
        "9a020b2209408180808080808010"
    );
}

#[test]
fn public_scopes_are_signed_but_relay_scopes_are_not() {
    let mut event = EventEnvelope {
        body: Some(event_envelope::Body::HouseEvent(HouseEvent {
            kind: "example.notice".into(),
            ..Default::default()
        })),
        ..Default::default()
    };
    let old = canonicalize_envelope(&event);
    if let Some(event_envelope::Body::HouseEvent(ref mut payload)) = event.body {
        payload.public_scopes = vec!["scope-a".into()];
    }
    let scoped = canonicalize_envelope(&event);
    assert_ne!(old, scoped);
    let frame = WorldStreamFrame {
        envelope: scoped.clone(),
        scopes: vec!["relay-only".into()],
        ..Default::default()
    };
    let decoded = WorldStreamFrame::decode(frame.encode_to_vec().as_slice()).unwrap();
    assert_eq!(decoded.envelope, scoped);
    assert_eq!(decoded.scopes, vec!["relay-only"]);
}
