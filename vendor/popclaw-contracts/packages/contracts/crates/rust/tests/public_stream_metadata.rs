use popclaw_contracts::world::{PublicStreamBoundary, PublicStreamCheckpoint, PublicStreamGap};
use prost::Message;
fn hex(value: impl Message) -> String {
    value
        .encode_to_vec()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}
fn boundary() -> PublicStreamBoundary {
    PublicStreamBoundary {
        log_incarnation: "log1".into(),
        scopes: vec!["scopeA".into()],
        high_water_seq: 9007199254740993,
        full_public: true,
    }
}
#[test]
fn public_stream_boundary_matches_typescript() {
    assert_eq!(
        hex(boundary()),
        "0a046c6f6731120673636f7065411881808080808080102001"
    );
}
#[test]
fn optional_unsigned_presence_and_max_match_typescript() {
    let mut checkpoint = PublicStreamCheckpoint {
        phase: "replay".into(),
        scopes: vec![],
        public_through_seq: None,
    };
    assert_eq!(hex(checkpoint.clone()), "0a067265706c6179");
    checkpoint.public_through_seq = Some(0);
    assert_eq!(hex(checkpoint.clone()), "0a067265706c61791800");
    let encoded = checkpoint.encode_to_vec();
    assert_eq!(
        PublicStreamCheckpoint::decode(encoded.as_slice())
            .unwrap()
            .public_through_seq,
        Some(0)
    );
    checkpoint.phase = "live".into();
    checkpoint.public_through_seq = Some(u64::MAX);
    assert_eq!(hex(checkpoint), "0a046c69766518ffffffffffffffffff01");
}
#[test]
fn gap_matches_typescript() {
    assert_eq!(hex(PublicStreamGap {reason:"history_pruned".into(), lane:"scope".into(), scope_id:"scopeA".into(), boundary:Some(boundary())}), "0a0e686973746f72795f7072756e6564120573636f70651a0673636f70654122190a046c6f6731120673636f7065411881808080808080102001");
}
