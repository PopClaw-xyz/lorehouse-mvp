//! Predecode structural checks. These never replace signatures, identity,
//! body-specific authorization or transactional publication checks.
use popclaw_contracts::event::{event_envelope::Body, EventEnvelope};
use prost::Message;
use prost_types::{
    field_descriptor_proto::{Label, Type},
    DescriptorProto, FileDescriptorSet,
};
use std::{
    collections::{BTreeMap, BTreeSet},
    sync::OnceLock,
};

pub const ENVELOPE_BASELINE: &str = "public-envelope-02";
fn schema() -> &'static BTreeMap<String, DescriptorProto> {
    static SCHEMA: OnceLock<BTreeMap<String, DescriptorProto>> = OnceLock::new();
    SCHEMA.get_or_init(|| {
        fn add(
            out: &mut BTreeMap<String, DescriptorProto>,
            prefix: &str,
            types: Vec<DescriptorProto>,
        ) {
            for t in types {
                let name = format!("{}.{}", prefix, t.name());
                add(out, &name, t.nested_type.clone());
                out.insert(name, t);
            }
        }
        let set =
            FileDescriptorSet::decode(include_bytes!("../../../proto/descriptor.pb").as_slice())
                .expect("generated descriptor");
        let mut out = BTreeMap::new();
        for f in set.file {
            add(&mut out, &format!(".{}", f.package()), f.message_type);
        }
        out
    })
}
fn varint(bytes: &[u8], pos: &mut usize) -> Result<u64, &'static str> {
    let mut n = 0u64;
    for i in 0..10 {
        let b = *bytes.get(*pos).ok_or("WIRE_VARINT")?;
        *pos += 1;
        if i == 9 && b > 1 {
            return Err("WIRE_VARINT");
        }
        n |= u64::from(b & 127) << (7 * i);
        if b & 128 == 0 {
            return Ok(n);
        }
    }
    Err("WIRE_VARINT")
}
fn scan(
    bytes: &[u8],
    name: &str,
    depth: usize,
    budget: &mut usize,
    body: &mut u32,
) -> Result<(), &'static str> {
    if depth > 32 {
        return Err("WIRE_DEPTH");
    }
    let ty = schema().get(name).ok_or("UNSUPPORTED_TYPE")?;
    let mut pos = 0;
    let mut seen = BTreeSet::new();
    let mut oneofs = BTreeSet::new();
    while pos < bytes.len() {
        *budget = budget.checked_sub(1).ok_or("WIRE_LIMIT")?;
        let key = varint(bytes, &mut pos)?;
        let tag64 = key >> 3;
        if tag64 == 0 || tag64 > 536870911 {
            return Err("WIRE_TAG");
        }
        let tag = tag64 as i32;
        let wire = (key & 7) as u8;
        if (name == ".popclaw.event.EventEnvelope" && tag == 29)
            || (name == ".popclaw.profile.Profile" && tag == 8)
        {
            return Err("RESERVED_OCCURRENCE");
        }
        let f = ty
            .field
            .iter()
            .find(|f| f.number() == tag)
            .ok_or("UNSUPPORTED_FIELD")?;
        if f.label() != Label::Repeated && !seen.insert(tag) {
            return Err("DUPLICATE_FIELD");
        }
        if let Some(index) = f.oneof_index {
            if !oneofs.insert(index) {
                return Err("MULTIPLE_ONEOF");
            }
            if name == ".popclaw.event.EventEnvelope" {
                *body = tag as u32;
            }
        }
        let expected = match f.r#type() {
            Type::String | Type::Bytes | Type::Message => 2,
            Type::Fixed64 | Type::Sfixed64 | Type::Double => 1,
            Type::Fixed32 | Type::Sfixed32 | Type::Float => 5,
            _ => 0,
        };
        if wire != expected {
            return Err("WIRE_TYPE");
        }
        if wire == 0 {
            let n = varint(bytes, &mut pos)?;
            if matches!(f.r#type(), Type::Uint32 | Type::Sint32) && n > u32::MAX as u64 {
                return Err("WIRE_RANGE");
            }
            if matches!(f.r#type(), Type::Int32 | Type::Enum)
                && n > u32::MAX as u64
                && n < 0xffffffff80000000
            {
                return Err("WIRE_RANGE");
            }
            continue;
        }
        let len = if wire == 2 {
            varint(bytes, &mut pos)?
        } else if wire == 1 {
            8
        } else {
            4
        };
        if len > (bytes.len() - pos) as u64 {
            return Err("WIRE_TRUNCATED");
        }
        let value = &bytes[pos..pos + len as usize];
        pos += len as usize;
        if f.r#type() == Type::String {
            std::str::from_utf8(value).map_err(|_| "WIRE_UTF8")?;
        }
        if f.r#type() == Type::Message {
            scan(value, f.type_name(), depth + 1, budget, body)?;
        }
    }
    Ok(())
}
/// `L_ENVELOPE_MAX_BYTES` (LIMITS.md): the largest raw EventEnvelope a conforming reader must accept.
pub const L_ENVELOPE_MAX_BYTES: usize = 1_572_864;
/// Returns the supported body tag. Does not establish public membership.
pub fn check_envelope_wire(raw: &[u8]) -> Result<u32, &'static str> {
    if raw.len() > L_ENVELOPE_MAX_BYTES {
        return Err("WIRE_LIMIT");
    }
    let mut body = 0;
    scan(
        raw,
        ".popclaw.event.EventEnvelope",
        0,
        &mut 65536,
        &mut body,
    )?;
    if body == 0 {
        return Err("MISSING_BODY");
    }
    Ok(body)
}
/// Structural/privacy eligibility only; not cryptographic or business admission.
///
/// Tags 20/21 (FollowDeclared/FollowRevoked) are absent from the public set: a
/// relation original is owed to its two participants' personal streams and is
/// never a public fact, whether `order` is absent, present or present-but-empty
/// (RELATIONS.md section 8). The body type alone decides, so the follow privacy
/// fields are no longer consulted here — they cannot readmit what the tag has
/// already excluded. This remains a public-eligibility test only: relation
/// originals still pass `check_envelope_wire`, keep their canonical bytes, CID
/// and author signature, and are still admitted through a House's ordinary
/// verified write entrance and delivered personally.
pub fn check_public_envelope_structure(raw: &[u8]) -> Result<u32, &'static str> {
    let tag = check_envelope_wire(raw)?;
    if ![11, 12, 13, 14, 15, 16, 18, 25, 27, 28, 33, 34].contains(&tag) {
        return Err("NOT_PUBLIC");
    }
    let env = EventEnvelope::decode(raw).map_err(|_| "WIRE_DECODE")?;
    if let Some(t) = &env.target {
        if ![0, 2].contains(&t.scope) || !t.filter_criteria.is_empty() {
            return Err("NOT_PUBLIC");
        }
        if (t.scope == 0 && !t.target_ids.is_empty()) || (t.scope == 2 && t.target_ids.is_empty()) {
            return Err("INVALID_TARGET");
        }
    }
    match &env.body {
        Some(Body::InviteRequest(request)) if ![0, 1].contains(&request.verification_mode) => {
            return Err("INVALID_ENUM");
        }
        Some(Body::QuestDispatch(dispatch)) => {
            if let Some(popclaw_contracts::quest::quest_dispatch::Quest::VerifyInvite(payload)) = &dispatch.quest {
                if ![0, 1].contains(&payload.verification_mode) {
                    return Err("INVALID_ENUM");
                }
            }
        }
        Some(Body::QuestResult(result)) if ![0, 1, 2, 3].contains(&result.verification_progress) => {
            return Err("INVALID_ENUM");
        }
        _ => (),
    }
    match &env.body {
        Some(Body::HouseEvent(h)) => {
            let parts: Vec<_> = h.kind.split('.').collect();
            if h.kind.len() > 128
                || parts.len() != 2
                || parts.iter().any(|s| s.is_empty())
                || !parts[0]
                    .bytes()
                    .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-')
                || !parts[1]
                    .bytes()
                    .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'_')
            {
                return Err("INVALID_KIND");
            }
            let unique: BTreeSet<_> = h.public_scopes.iter().collect();
            if h.public_scopes.len() > 32
                || unique.len() != h.public_scopes.len()
                || h.public_scopes.iter().any(|s| {
                    s.len() < 4
                        || s.len() > 64
                        || !s
                            .bytes()
                            .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
                })
            {
                return Err("INVALID_SCOPES");
            }
        }
        _ => (),
    }
    Ok(tag)
}
