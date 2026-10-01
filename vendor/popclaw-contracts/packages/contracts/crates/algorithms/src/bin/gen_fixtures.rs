//! Deterministically builds fixtures/test-vectors.json from hardcoded inputs.
//! Run with: `cargo run -p popclaw-algorithms --bin gen-fixtures`.

use std::{fs, path::PathBuf};

use ed25519_dalek::{Signer, SigningKey};
use popclaw_algorithms::{canonicalize_envelope, cid_from_canonical, sigil};
use popclaw_contracts::event::{
    content_block, event_envelope, recipient, ContentBlock, DirectMessage, EventEnvelope,
    FollowDeclared, FollowRevoked, HouseEvent, IntentPayload, Origin, Post, PostRef,
    RangerRegistration, Recipient, RelationOrder, Reply, VerifiedPlatform, WatchCancel,
    WatchDispatch, WatchHeartbeat,
};
use popclaw_contracts::identity::ActorInfo;
use popclaw_contracts::invite::{InviteRequest, InviteVerified};
use popclaw_contracts::profile::Profile;
use popclaw_contracts::quest::{
    quest_dispatch, QuestDispatch, QuestKind, QuestOutcome, QuestResult, ScrapeContentPayload,
    VerifyInvitePayload,
};
use serde_json::json;

fn main() -> anyhow::Result<()> {
    let repo_root = find_repo_root()?;
    let out = repo_root.join("packages/contracts/fixtures/test-vectors.json");
    fs::create_dir_all(out.parent().unwrap())?;

    // ---- canonical_serialization vectors ----
    // canon1 / canon2: originally FeedPayload envelopes (Task 4.5a retired
    // FeedPayload, field 10 now reserved). They are no longer emitted as
    // canonical_serialization entries — the vectors have been deleted. canon1 is
    // kept here only because the signature-roundtrip section still signs it to
    // pin the Ed25519 signing path with a known key+bytes+sig triple.
    let canon1: Vec<u8> = hex::decode(
        "123c0a2c374c685a38783663384b6d7735503957746e6d345436453759636254\
         705a374e3774665a63714c527635634d120c426c61636b466561746865722207\
         747769747465722880ae91b1065220121e68747470733a2f2f6578616d706c65\
         2e696e76616c69642f706f73742f31",
    )
    .expect("hardcoded hex");

    // ---- Scope B payload-variant vectors ----
    // All 5 share the same outer fields (common Scope B envelope shape);
    // only the oneof payload differs. See the `scope_b_envelope` helper.
    let applicant_pk_bytes: Vec<u8> = (0u8..32).collect();
    const SCOPE_B_TASK_ID_1: &str = "00000000-0000-0000-0000-000000000001";
    const SCOPE_B_TASK_ID_2: &str = "00000000-0000-0000-0000-000000000002";
    const SCOPE_B_EXPIRES_AT: u64 = 1_713_744_000;
    // Fixed-bytes SHA-256 hash used in QuestResult; matches the base64 string
    // `ZVbD0J7/SXeOzFaVq5pC2wlXtFYQm1xn7Jt3NnJ7s6c=` documented in the
    // test-vector spec (decoded to raw 32 bytes here for proto encoding).
    let evidence_hash: Vec<u8> = vec![
        0x65, 0x56, 0xc3, 0xd0, 0x9e, 0xff, 0x49, 0x77, 0x8e, 0xcc, 0x56, 0x95, 0xab, 0x9a, 0x42,
        0xdb, 0x09, 0x57, 0xb4, 0x56, 0x10, 0x9b, 0x5c, 0x67, 0xec, 0x9b, 0x77, 0x36, 0x72, 0x7b,
        0xb3, 0xa7,
    ];

    let scope_b_envelope = |body: event_envelope::Body| EventEnvelope {
        event_id: String::new(),
        actor: Some(ActorInfo {
            popclaw_id: "11111111111111111111111111111111".into(),
            nickname: String::new(),
            supersedes: None,
            device_id: None,
            role: None,
        }),
        target: Some(Recipient {
            scope: recipient::Scope::Broadcast as i32,
            target_ids: Vec::new(),
            filter_criteria: String::new(),
        }),
        lorehouse: "twitter".into(),
        timestamp: 1_713_657_600,
        signature: Vec::new(),
        prev_event_id: String::new(),
        body: Some(body),
    };

    // Vector 3: invite_request_payload_minimal
    // Relation vectors are scoped to one house: `lorehouse` carries the
    // base58 house key the ordering namespace belongs to, and the same value
    // appears inside RelationOrder.house_key. Everything else is Scope B.
    // Deliberately DIFFERENT from the followee id below. When house_key,
    // followee and lorehouse are all the same string, an implementation that
    // fills house_key with the followee (or vice versa) produces identical
    // bytes and the vector cannot see the mistake.
    const HOUSE_KEY: &str = "9xQeWy8P3vNhKd2RmTzA6BcFgJ4LnSuVoXpYrEt5Hw1Z";
    let relation_envelope = |body: event_envelope::Body| EventEnvelope {
        lorehouse: HOUSE_KEY.into(),
        ..scope_b_envelope(body)
    };

    let env_invite_request = scope_b_envelope(event_envelope::Body::InviteRequest(InviteRequest {
        platform: "twitter".into(),
        handle: "testuser".into(),
        nickname: "Test User".into(),
        landing_url: String::new(),
        replace: false,
        proof_url: String::new(),
        mirror_optin: false,
    }));
    let canon_invite_request = canonicalize_envelope(&env_invite_request);
    let cid_invite_request = cid_from_canonical(&canon_invite_request);

    // Vector: invite_request_with_landing_url — InviteRequestPayload with landing_url populated
    let env_invite_request_landing = scope_b_envelope(event_envelope::Body::InviteRequest(
        InviteRequest {
            platform: "twitter".into(),
            handle: "testuser".into(),
            nickname: "Test User".into(),
            landing_url:
                "https://popclaw.me/invite/11111111111111111111111111111111?sigil=837a8c&nick=Test%20User"
                    .into(),
            replace: false,
            proof_url: String::new(),
            mirror_optin: false,
        },
    ));
    let canon_invite_request_landing = canonicalize_envelope(&env_invite_request_landing);
    let cid_invite_request_landing = cid_from_canonical(&canon_invite_request_landing);

    // Vector 4: quest_dispatch_verify_invite_minimal
    let env_qd_verify = scope_b_envelope(event_envelope::Body::QuestDispatch(QuestDispatch {
        task_id: SCOPE_B_TASK_ID_1.into(),
        kind: QuestKind::VerifyInvite as i32,
        expires_at: SCOPE_B_EXPIRES_AT,
        quest: Some(quest_dispatch::Quest::VerifyInvite(VerifyInvitePayload {
            platform: "twitter".into(),
            handle: "testuser".into(),
            applicant_popclaw_id: applicant_pk_bytes.clone(),
            expected_sigil: "837a8c".into(),
            proof_url: String::new(),
        })),
    }));
    let canon_qd_verify = canonicalize_envelope(&env_qd_verify);
    let cid_qd_verify = cid_from_canonical(&canon_qd_verify);

    // Vector 5: quest_dispatch_scrape_content_minimal
    let env_qd_scrape = scope_b_envelope(event_envelope::Body::QuestDispatch(QuestDispatch {
        task_id: SCOPE_B_TASK_ID_2.into(),
        kind: QuestKind::ScrapeContent as i32,
        expires_at: SCOPE_B_EXPIRES_AT,
        quest: Some(quest_dispatch::Quest::ScrapeContent(ScrapeContentPayload {
            platform: "twitter".into(),
            handle: "testuser".into(),
            since_timestamp: 0,
            max_items: 20,
        })),
    }));
    let canon_qd_scrape = canonicalize_envelope(&env_qd_scrape);
    let cid_qd_scrape = cid_from_canonical(&canon_qd_scrape);

    // Vector 6: quest_result_approve_minimal
    let env_qr_approve = scope_b_envelope(event_envelope::Body::QuestResult(QuestResult {
        task_id: SCOPE_B_TASK_ID_1.into(),
        outcome: QuestOutcome::Approve as i32,
        evidence_hash: evidence_hash.clone(),
        evidence_sample: Vec::new(),
        reason: String::new(),
        // proto3 default "" elides — existing CID unchanged.
        account_id: String::new(),
        // proto3 defaults (0 / "" / "") elide — existing CID unchanged.
        follower_count: 0,
        avatar_url: String::new(),
        bio: String::new(),
    }));
    let canon_qr_approve = canonicalize_envelope(&env_qr_approve);
    let cid_qr_approve = cid_from_canonical(&canon_qr_approve);

    // Vector 7: invite_verified_milestone_minimal
    let env_iv_milestone = scope_b_envelope(event_envelope::Body::InviteVerified(InviteVerified {
        task_id: SCOPE_B_TASK_ID_1.into(),
        applicant_popclaw_id: applicant_pk_bytes.clone(),
        platform: "twitter".into(),
        handle: "testuser".into(),
        approve_count: 2,
        reject_count: 1,
        // additive: proto3 default 0 elides on the wire, so this
        // milestone fixture's canonical bytes + CID stay unchanged.
        follower_count: 0,
        // proto3 default "" elides — existing CID unchanged.
        account_id: String::new(),
    }));
    let canon_iv_milestone = canonicalize_envelope(&env_iv_milestone);
    let cid_iv_milestone = cid_from_canonical(&canon_iv_milestone);

    // ---- payload-variant vectors ----
    // Reuses the same `scope_b_envelope` helper so outer envelope fields are
    // identical; only the oneof payload differs.

    // Vector 8: ranger_registration_minimal
    let env_reg = scope_b_envelope(event_envelope::Body::RangerRegistration(
        RangerRegistration {
            capabilities: vec!["x".to_string()],
            availability_score: 100,
        },
    ));
    let canon_reg = canonicalize_envelope(&env_reg);
    let cid_reg = cid_from_canonical(&canon_reg);

    // Vector 9: watch_dispatch_minimal
    let env_wd = scope_b_envelope(event_envelope::Body::WatchDispatch(WatchDispatch {
        watch_id: "00000000-0000-0000-0000-000000000001".into(),
        target_popclaw_id: "11111111111111111111111111111111".into(),
        platform: "x".into(),
        handle: "blackfeather".into(),
        since: 0,
    }));
    let canon_wd = canonicalize_envelope(&env_wd);
    let cid_wd = cid_from_canonical(&canon_wd);

    // Vector 10: watch_heartbeat_minimal
    let env_hb = scope_b_envelope(event_envelope::Body::WatchHeartbeat(WatchHeartbeat {
        watch_id: "00000000-0000-0000-0000-000000000001".into(),
        active_since: 1_777_000_000,
        recent_hits: 3,
    }));
    let canon_hb = canonicalize_envelope(&env_hb);
    let cid_hb = cid_from_canonical(&canon_hb);

    // Vector 11: watch_cancel_minimal
    let env_wc = scope_b_envelope(event_envelope::Body::WatchCancel(WatchCancel {
        watch_id: "00000000-0000-0000-0000-000000000001".into(),
        reason: "reassigned".into(),
    }));
    let canon_wc = canonicalize_envelope(&env_wc);
    let cid_wc = cid_from_canonical(&canon_wc);

    // ---- popclaw-native Post protocol layer vectors ----
    // Vector: post_root_minimal — single TEXT block "hi", no prev.
    let env_post_root = EventEnvelope {
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
        prev_event_id: String::new(), // root post
        body: Some(event_envelope::Body::Post(Post {
            blocks: vec![ContentBlock {
                block_type: content_block::Type::Text as i32,
                content: "hi".into(),
                metadata: Default::default(),
            }],
            media: vec![],
            // origin absent (None) — proto3 message field elides; CID unchanged.
            origin: None,
        })),
    };
    let canon_post_root = canonicalize_envelope(&env_post_root);
    let cid_post_root = cid_from_canonical(&canon_post_root);

    // Vector 14: post_reply_minimal — replies to post_root_minimal.
    let env_post_reply = EventEnvelope {
        event_id: String::new(),
        actor: Some(ActorInfo {
            popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            nickname: "Scout".into(),
            supersedes: None,
            device_id: None,
            role: None,
        }),
        target: None,
        lorehouse: String::new(),
        timestamp: 1_713_657_700,
        signature: Vec::new(),
        prev_event_id: cid_post_root.clone(), // Continue the thread
        body: Some(event_envelope::Body::Post(Post {
            blocks: vec![ContentBlock {
                block_type: content_block::Type::Text as i32,
                content: "ack".into(),
                metadata: Default::default(),
            }],
            media: vec![],
            // origin absent (None) — proto3 message field elides; CID unchanged.
            origin: None,
        })),
    };
    let canon_post_reply = canonicalize_envelope(&env_post_reply);
    let cid_post_reply = cid_from_canonical(&canon_post_reply);

    // Vector 15: post_quote_minimal — quotes post_root_minimal via LINK_CARD.
    // Exercises:
    //   - LINK_CARD content serialization (the popclaw.me URI)
    //   - Multi-block ordering (TEXT before LINK_CARD — mirrors signPost() build convention)
    //   - ContentBlock.LINK_CARD enum value (=5, non-zero, MUST emit)
    //   - ContentBlock.TEXT enum value (=0, default, MUST elide)
    //   - ContentBlock.metadata={} elision on both blocks
    //   - prev_event_id + payload PostPayload coexisting in same envelope
    let post_quote_link = format!("https://popclaw.me/post/{cid_post_root}");
    let env_post_quote = EventEnvelope {
        event_id: String::new(),
        actor: Some(ActorInfo {
            popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            nickname: "Scout".into(),
            supersedes: None,
            device_id: None,
            role: None,
        }),
        target: None,
        lorehouse: String::new(),
        timestamp: 1_713_657_800,
        signature: Vec::new(),
        prev_event_id: cid_post_root.clone(), // quotes post_root_minimal
        body: Some(event_envelope::Body::Post(Post {
            blocks: vec![
                ContentBlock {
                    block_type: content_block::Type::Text as i32, // TEXT (proto3 default — MUST elide on canonical)
                    content: "城东更便宜".into(),
                    metadata: Default::default(), // empty map — MUST elide
                },
                ContentBlock {
                    block_type: content_block::Type::LinkCard as i32, // LINK_CARD (non-zero — MUST emit)
                    content: post_quote_link.clone(),
                    metadata: Default::default(), // empty map — MUST elide
                },
            ],
            media: vec![],
            // origin absent (None) — proto3 message field elides; CID unchanged.
            origin: None,
        })),
    };
    let canon_post_quote = canonicalize_envelope(&env_post_quote);
    let cid_post_quote = cid_from_canonical(&canon_post_quote);

    // Vector: profile_minimal — Profile
    let env_profile = scope_b_envelope(event_envelope::Body::Profile(Profile {
        nickname: "BlackFeather".into(),
        one_line_intro: "杭州，AI agent 研究者，爱龙虾".into(),
        taste_tags: vec!["ai-agents".into(), "lobster-cuisine".into()],
        role_persona: "seeker".into(),
        location_hint: "Hangzhou".into(),
        avatar_uri: String::new(),
        declared_at: 1_747_526_400,
    }));
    let canon_profile = canonicalize_envelope(&env_profile);
    let cid_profile = cid_from_canonical(&canon_profile);

    // ---- social payload vectors (Reply / DM / Follow*) ----
    // Close the parity blind spot: these payloads shipped in Plans 11.1/12 but
    // never had canonical vectors, so TS/Rust encoding drift was unguarded.

    // Vector: reply_minimal — Scout replies to an X post whose author has no
    // popclaw mapping yet (author_popclaw_id="" — proto3 default MUST elide).
    let env_reply = EventEnvelope {
        event_id: String::new(),
        actor: Some(ActorInfo {
            popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            nickname: "Scout".into(),
            supersedes: None,
            device_id: None,
            role: None,
        }),
        target: None,
        lorehouse: String::new(),
        timestamp: 1_713_657_900,
        signature: Vec::new(),
        prev_event_id: String::new(),
        body: Some(event_envelope::Body::Reply(Reply {
            from_popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            in_reply_to: Some(PostRef {
                platform: "x".into(),
                platform_post_id: "1234567890".into(),
                author_popclaw_id: String::new(),
            }),
            body: "好帖".into(),
            ts: 1_713_657_900,
        })),
    };
    let canon_reply = canonicalize_envelope(&env_reply);
    let cid_reply = cid_from_canonical(&canon_reply);

    // Vector: direct_message_minimal — Scout DMs BlackFeather; in_reply_to_post
    // absent (unset message field MUST NOT emit a tag).
    //
    // DM-ENCRYPTION PARITY TRIPLE (case 1 of 3: ciphertext/nonce ABSENT).
    // This is the pre-encryption DM shape. Its canonical bytes and CID MUST NOT
    // change now that DirectMessage has fields 6/7 — that is the
    // additive guarantee: every DM signed before encryption existed still
    // verifies. See the sibling vectors below for cases 2 and 3.
    let env_dm = EventEnvelope {
        event_id: String::new(),
        actor: Some(ActorInfo {
            popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            nickname: "Scout".into(),
            supersedes: None,
            device_id: None,
            role: None,
        }),
        target: None,
        lorehouse: String::new(),
        timestamp: 1_713_658_000,
        signature: Vec::new(),
        prev_event_id: String::new(),
        body: Some(event_envelope::Body::DirectMessage(DirectMessage {
            from_popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            to_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
            in_reply_to_post: None,
            body: "回头细聊".into(),
            ts: 1_713_658_000,
            // Case 1: ciphertext/nonce absent — proto3 `bytes` default elides.
            ciphertext: Vec::new(),
            nonce: Vec::new(),
            media_ciphertext: Vec::new(),
            media_nonce: Vec::new(),
        })),
    };
    let canon_dm = canonicalize_envelope(&env_dm);
    let cid_dm = cid_from_canonical(&canon_dm);

    // Vector: direct_message_encrypted (case 2 of 3: ciphertext/nonce PRESENT).
    // Same outer envelope as direct_message_minimal so the byte delta is exactly
    // fields 6 and 7. `body` carries the non-empty base64 placeholder described
    // in event.proto (old lore-houses reject an empty body) — it is NOT the
    // message. Ciphertext deliberately contains 0x00 and 0xff so any UTF-8-ish
    // mangling of opaque bytes across the pbjs↔prost boundary shows up as a
    // hex/CID mismatch rather than passing silently.
    let dm_ciphertext: Vec<u8> = vec![
        0x00, 0xff, 0x10, 0x9b, 0x5c, 0x67, 0xec, 0x9b, 0x77, 0x36, 0x72, 0x7b, 0xb3, 0xa7, 0x00,
        0xff,
    ];
    // 24-byte nacl.box nonce (fixed here for determinism; real ones are random).
    let dm_nonce: Vec<u8> = (0u8..24).collect();
    let env_dm_encrypted = EventEnvelope {
        body: Some(event_envelope::Body::DirectMessage(DirectMessage {
            from_popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            to_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
            in_reply_to_post: None,
            body: "[encrypted]".into(), // placeholder, not the message
            ts: 1_713_658_000,
            ciphertext: dm_ciphertext.clone(),
            nonce: dm_nonce.clone(),
            media_ciphertext: Vec::new(),
            media_nonce: Vec::new(),
        })),
        ..env_dm.clone()
    };
    let canon_dm_encrypted = canonicalize_envelope(&env_dm_encrypted);
    let cid_dm_encrypted = cid_from_canonical(&canon_dm_encrypted);

    // Vector: direct_message_empty_ciphertext (case 3 of 3: PRESENT-BUT-EMPTY).
    // The historically dangerous shape: a client that sets ciphertext/nonce to
    // zero-length instead of omitting them. proto3 `bytes` defaults MUST elide,
    // so these canonical bytes MUST come out byte-identical to
    // direct_message_minimal (asserted in fixture_parity.rs). The TS mirror in
    // canonical-parity.test.ts passes explicit `new Uint8Array(0)` values here —
    // if pbjs emitted a zero-length field where prost elides, this vector is the
    // one that catches it.
    let env_dm_empty_ct = EventEnvelope {
        body: Some(event_envelope::Body::DirectMessage(DirectMessage {
            from_popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            to_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
            in_reply_to_post: None,
            body: "回头细聊".into(),
            ts: 1_713_658_000,
            ciphertext: Vec::new(), // present-but-empty — MUST elide
            nonce: Vec::new(),      // present-but-empty — MUST elide
            media_ciphertext: Vec::new(),
            media_nonce: Vec::new(),
        })),
        ..env_dm.clone()
    };
    let canon_dm_empty_ct = canonicalize_envelope(&env_dm_empty_ct);
    let cid_dm_empty_ct = cid_from_canonical(&canon_dm_empty_ct);

    // Vector: actor_device_id_empty — EXPLICIT-PRESENCE boundary, the mirror
    // image of the DM ciphertext case above.
    //
    // ActorInfo.device_id is `optional bytes` (proto3 explicit presence), so
    // presence IS tracked: prost holds Option<Vec<u8>> and encodes whenever it
    // is Some(_), including Some(vec![]) → emits tag 0x22 + len 0. protobufjs
    // does the same for its synthetic-oneof proto3-optional field. So unlike an
    // implicit-presence `bytes`, an explicitly-empty device_id MUST be EMITTED
    // by both sides, NOT elided. Any canonicalizer that blanket-drops empty
    // byte arrays breaks parity here in the opposite direction.
    let env_device_id_empty = EventEnvelope {
        actor: Some(ActorInfo {
            popclaw_id: "6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM".into(),
            nickname: "Scout".into(),
            supersedes: None,
            device_id: Some(Vec::new()), // present-but-empty → MUST emit tag+len0
            role: None,
        }),
        ..env_dm.clone()
    };
    let canon_device_id_empty = canonicalize_envelope(&env_device_id_empty);
    let cid_device_id_empty = cid_from_canonical(&canon_device_id_empty);

    // Vector: follow_declared_minimal — exercises non-default bool emission
    // (taste_subscribed=true MUST emit) alongside two enum defaults
    // (follow_type=PUBLIC=0, taste_subscription_visibility=SV_PUBLIC=0 — both
    // MUST elide).
    let env_follow = scope_b_envelope(event_envelope::Body::FollowDeclared(FollowDeclared {
        followee_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
        follow_type: 0,
        taste_subscribed: true,
        taste_subscription_visibility: 0,
        // Absent: this vector predates ordered relations and its canonical
        // bytes must not move. A present `order` is what activates ordered
        // mode; None elides, so the CID stays byte-identical.
        order: None,
    }));
    let canon_follow = canonicalize_envelope(&env_follow);
    let cid_follow = cid_from_canonical(&canon_follow);

    // Vector: follow_revoked_minimal — single non-default field (followee id).
    let env_unfollow = scope_b_envelope(event_envelope::Body::FollowRevoked(FollowRevoked {
        followee_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
        follow_type: 0,
        order: None,
    }));
    let canon_unfollow = canonicalize_envelope(&env_unfollow);
    let cid_unfollow = cid_from_canonical(&canon_unfollow);

    // Ordered mode: the nested RelationOrder with seq and house_key both
    // non-default (MUST emit) and `resolves` empty (MUST elide, repeated).
    let env_follow_ordered =
        relation_envelope(event_envelope::Body::FollowDeclared(FollowDeclared {
            followee_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
            follow_type: 0,
            taste_subscribed: true,
            taste_subscription_visibility: 0,
            order: Some(RelationOrder {
                seq: 7,
                house_key: HOUSE_KEY.into(),
                resolves: vec![],
            }),
        }));
    let canon_follow_ordered = canonicalize_envelope(&env_follow_ordered);
    let cid_follow_ordered = cid_from_canonical(&canon_follow_ordered);

    // The vector that makes presence usable as the activation marker at all.
    // Every field inside RelationOrder is at its default, yet the message
    // itself MUST still emit (tag + length 0), because proto3 message fields
    // carry explicit presence. A canonicalizer that blanket-drops "empty"
    // sub-messages makes ordered mode indistinguishable from legacy, and the
    // whole scheme degrades silently.
    let env_follow_order_empty =
        relation_envelope(event_envelope::Body::FollowDeclared(FollowDeclared {
            followee_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
            follow_type: 0,
            taste_subscribed: true,
            taste_subscription_visibility: 0,
            order: Some(RelationOrder::default()),
        }));
    let canon_follow_order_empty = canonicalize_envelope(&env_follow_order_empty);
    let cid_follow_order_empty = cid_from_canonical(&canon_follow_order_empty);

    // 2^53 + 1, the first uint64 a JavaScript Number cannot represent. A
    // counter that silently rounds is worse than one that fails, so both
    // languages must carry this losslessly or the vectors disagree here and
    // nowhere else.
    let env_follow_big_seq =
        relation_envelope(event_envelope::Body::FollowDeclared(FollowDeclared {
            followee_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
            follow_type: 0,
            taste_subscribed: false,
            taste_subscription_visibility: 0,
            order: Some(RelationOrder {
                seq: 9_007_199_254_740_993,
                house_key: HOUSE_KEY.into(),
                resolves: vec![],
            }),
        }));
    let canon_follow_big_seq = canonicalize_envelope(&env_follow_big_seq);
    let cid_follow_big_seq = cid_from_canonical(&canon_follow_big_seq);

    // A fork recovery statement: `resolves` names every branch it settles, so
    // the repeated string field is non-empty and MUST emit, twice, in order.
    let env_unfollow_ordered =
        relation_envelope(event_envelope::Body::FollowRevoked(FollowRevoked {
            followee_popclaw_id: "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into(),
            follow_type: 0,
            order: Some(RelationOrder {
                seq: 9,
                house_key: HOUSE_KEY.into(),
                resolves: vec!["a".repeat(64), "b".repeat(64)],
            }),
        }));
    let canon_unfollow_ordered = canonicalize_envelope(&env_unfollow_ordered);
    let cid_unfollow_ordered = cid_from_canonical(&canon_unfollow_ordered);

    // Vector: namecard_popclaw_minimal — production namecard shape (S1
    // signProfile): plain envelope (no target), lorehouse empty (=local house), minimal
    // Profile (nickname + declared_at only; all optional strings and
    // taste_tags elide per Invariant #1).
    let env_namecard = EventEnvelope {
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
        timestamp: 1_747_526_400,
        signature: Vec::new(),
        prev_event_id: String::new(),
        body: Some(event_envelope::Body::Profile(Profile {
            nickname: "BlackFeather".into(),
            one_line_intro: String::new(),
            taste_tags: vec![],
            role_persona: String::new(),
            location_hint: String::new(),
            avatar_uri: String::new(),
            declared_at: 1_747_526_400,
        })),
    };
    let canon_namecard = canonicalize_envelope(&env_namecard);
    let cid_namecard = cid_from_canonical(&canon_namecard);

    // ---- mirror-provenance vectors ----

    // Vector: post_with_origin — Post carrying a fully-populated Origin.
    // Exercises: Origin message serialisation; Post.origin field 3; all 5 Origin
    // sub-fields non-default (MUST emit). Existing post_root_minimal / post_reply_minimal
    // / post_quote_minimal envelopes carry NO origin — their CIDs are UNCHANGED.
    let env_post_with_origin = EventEnvelope {
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
        timestamp: 1_750_100_000,
        signature: Vec::new(),
        prev_event_id: String::new(),
        body: Some(event_envelope::Body::Post(Post {
            blocks: vec![ContentBlock {
                block_type: content_block::Type::Text as i32,
                content: "今天的晚霞很美".into(),
                metadata: Default::default(),
            }],
            media: vec![],
            origin: Some(Origin {
                platform: "x".into(),
                post_id: "1800000000000000001".into(),
                url: "https://x.com/blackfeather_pc/status/1800000000000000001".into(),
                created_at: 1_750_099_800,
                reply_to_id: String::new(), // root post on X; elides per proto3 default
            }),
        })),
    };
    let canon_post_with_origin = canonicalize_envelope(&env_post_with_origin);
    let cid_post_with_origin = cid_from_canonical(&canon_post_with_origin);

    // Vector: invite_verified_with_account_id — InviteVerified carrying account_id
    // (field 8). Exercises the additive account_id field on InviteVerified.
    // The existing invite_verified_milestone_minimal (account_id="" → elides) is
    // UNCHANGED in bytes.
    let env_iv_with_account_id =
        scope_b_envelope(event_envelope::Body::InviteVerified(InviteVerified {
            task_id: SCOPE_B_TASK_ID_1.into(),
            applicant_popclaw_id: applicant_pk_bytes.clone(),
            platform: "x".into(),
            handle: "blackfeather_pc".into(),
            approve_count: 3,
            reject_count: 0,
            follower_count: 12_400,
            account_id: "1234567890".into(), // X rest_id
        }));
    let canon_iv_with_account_id = canonicalize_envelope(&env_iv_with_account_id);
    let cid_iv_with_account_id = cid_from_canonical(&canon_iv_with_account_id);

    // Vector: verified_platform_with_account_id — WorldFeedItem not exercised
    // directly here (it's a read-side projection), so we instead build a
    // FollowDeclared envelope that carries a VerifiedPlatform in the actor's
    // verified list via a FeedPayload. Actually: VerifiedPlatform only appears
    // inside WorldFeedItem (a projection message), not in any EventEnvelope body
    // directly. We therefore test it via a standalone canonical-bytes pin:
    // serialize a VerifiedPlatform with account_id set, capture hex + hash.
    use prost::Message as _;
    let vp_with_account_id = VerifiedPlatform {
        platform: "x".into(),
        handle: "blackfeather_pc".into(),
        profile_url: "https://x.com/blackfeather_pc".into(),
        follower_count: 12_400,
        account_id: "1234567890".into(),
    };
    let vp_bytes = vp_with_account_id.encode_to_vec();
    let vp_hex = hex::encode(&vp_bytes);
    let vp_cid = cid_from_canonical(&vp_bytes);

    // ---- Federation-spec Layer 2 extension vectors (2026-07-26) ----
    //
    // The point of these four: prove that an opaque `bytes` body survives the
    // pbjs↔prost boundary byte-for-byte, including the two boundaries that
    // historically broke CID parity — a proto3 default scalar (schema_version=0)
    // and an empty `bytes` (body=b""). Both MUST elide; the TS mirror in
    // canonical-parity.test.ts has to omit them to reproduce these hexes.

    // Vector: house_event_minimal — non-default everything, body carries a NUL
    // byte and a 0xff byte so any UTF-8-ish mangling of the opaque payload shows up.
    let house_event_body: Vec<u8> = vec![
        0x7b, 0x22, 0x74, 0x6f, 0x22, 0x3a, 0x00, 0xff, 0x7d, // {"to":\0\xff}
    ];
    let env_house_event = scope_b_envelope(event_envelope::Body::HouseEvent(HouseEvent {
        public_scopes: Vec::new(),
        kind: "world.postcard".into(),
        schema_version: 1,
        body: house_event_body.clone(),
    }));
    let canon_house_event = canonicalize_envelope(&env_house_event);
    let cid_house_event = cid_from_canonical(&canon_house_event);

    // Vector: house_event_default_boundaries — schema_version=0 and body=b""
    // both elide; only `kind` reaches the wire.
    let env_house_event_defaults = scope_b_envelope(event_envelope::Body::HouseEvent(HouseEvent {
        public_scopes: Vec::new(),
        kind: "world.encounter".into(),
        schema_version: 0,
        body: Vec::new(),
    }));
    let canon_house_event_defaults = canonicalize_envelope(&env_house_event_defaults);
    let cid_house_event_defaults = cid_from_canonical(&canon_house_event_defaults);

    // Vector: intent_minimal — all three fields non-default.
    let intent_params: Vec<u8> = br#"{"destination":"kyoto"}"#.to_vec();
    let env_intent = scope_b_envelope(event_envelope::Body::Intent(IntentPayload {
        context: None,
        lorehouse: "world".into(),
        intent_kind: "world.pack_and_travel".into(),
        params: intent_params.clone(),
    }));
    let canon_intent = canonicalize_envelope(&env_intent);
    let cid_intent = cid_from_canonical(&canon_intent);

    // Vector: intent_default_boundaries — lorehouse="" (talk to the house you're
    // already connected to, per EventEnvelope.lorehouse semantics) and params=b""
    // both elide.
    let env_intent_defaults = scope_b_envelope(event_envelope::Body::Intent(IntentPayload {
        context: None,
        lorehouse: String::new(),
        intent_kind: "world.look_around".into(),
        params: Vec::new(),
    }));
    let canon_intent_defaults = canonicalize_envelope(&env_intent_defaults);
    let cid_intent_defaults = cid_from_canonical(&canon_intent_defaults);

    // house_session control-plane vectors. Requests use the identity signing key with
    // the deterministic signature_roundtrip seed. ACKs use a fixed house-session key
    // seed. Rust and TypeScript consume identical canonical bytes, domain-prefixed
    // inputs, CIDs and signatures. Sequence fixtures fix the structure of required
    // server transitions and races without executing a server.
    use popclaw_algorithms::house_session::{
        ack_signing_input, canonical_ack_bytes, canonical_request_bytes, request_signing_input,
    };
    use popclaw_contracts::housesession::{AckCore, Operation, RequestCore, SessionInfo};

    const HOUSE_SESSION_ORIGIN: &str = "https://demo.loreshow.com";
    const HS_INSTALL_A: &str = "11111111-2222-4333-8444-555555555555";
    const HS_INSTALL_B: &str = "99999999-8888-4777-8666-555555555555";
    const HS_ISSUED_AT: u64 = 1_757_200_000;
    const HS_EXPIRES_AT: u64 = 1_757_200_060;
    const HS_HOUSE_SEED_HEX: &str =
        "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90";
    // Reuse the deterministic signature_roundtrip request-key seed, declared locally to
    // avoid depending on the later seed_hex/sk declaration.
    const HS_IDENTITY_SEED_HEX: &str =
        "0011223344556677889900aabbccddeeff00112233445566778899aabbccddee";

    let hs_house_seed: [u8; 32] = hex::decode(HS_HOUSE_SEED_HEX)?.try_into().unwrap();
    let hs_house_sk = SigningKey::from_bytes(&hs_house_seed);
    let hs_house_pk = hex::encode(hs_house_sk.verifying_key().as_bytes());
    let hs_identity_seed: [u8; 32] = hex::decode(HS_IDENTITY_SEED_HEX)?.try_into().unwrap();
    let hs_identity_sk = SigningKey::from_bytes(&hs_identity_seed);
    let hs_identity_pk = hex::encode(hs_identity_sk.verifying_key().as_bytes());

    // Identity binding: positive vectors derive popclaw_id from the signing seed public
    // key. /v1/house-session requires actor and signer to use the same key;
    // inconsistent vectors would all be AUTH_INVALID.
    fn hs_popclaw_id() -> String {
        let seed: [u8; 32] = hex::decode(HS_IDENTITY_SEED_HEX)
            .unwrap()
            .try_into()
            .unwrap();
        let sk = SigningKey::from_bytes(&seed);
        bs58::encode(sk.verifying_key().as_bytes()).into_string()
    }

    fn op_name(op: i32) -> &'static str {
        match op {
            x if x == Operation::Enter as i32 => "ENTER",
            x if x == Operation::Renew as i32 => "RENEW",
            x if x == Operation::Leave as i32 => "LEAVE",
            x if x == Operation::Status as i32 => "STATUS",
            _ => panic!("unknown operation"),
        }
    }

    fn request_core(
        operation: Operation,
        op_seq: u64,
        request_id: &str,
        installation_id: &str,
        expected_house_revision: u64,
        target_session_id: &str,
    ) -> RequestCore {
        RequestCore {
            operation: operation as i32,
            popclaw_id: hs_popclaw_id(),
            installation_id: installation_id.into(),
            op_seq,
            request_id: request_id.into(),
            house_origin: HOUSE_SESSION_ORIGIN.into(),
            issued_at: HS_ISSUED_AT,
            expires_at: HS_EXPIRES_AT,
            nonce: format!("nonce-{request_id}"),
            expected_house_revision,
            target_session_id: target_session_id.into(),
            action_id: String::new(),
            action_expires_at: 0,
        }
    }

    fn request_core_json(core: &RequestCore) -> serde_json::Value {
        json!({
            "operation": op_name(core.operation),
            "popclaw_id": core.popclaw_id,
            "installation_id": core.installation_id,
            "op_seq": core.op_seq,
            "request_id": core.request_id,
            "house_origin": core.house_origin,
            "issued_at": core.issued_at,
            "expires_at": core.expires_at,
            "nonce": core.nonce,
            "expected_house_revision": core.expected_house_revision,
            "target_session_id": core.target_session_id,
        })
    }

    fn signed_request_vector(
        name: &str,
        description: &str,
        core: RequestCore,
        explicit_defaults: bool,
        signer: &SigningKey,
        signer_seed_hex: &str,
        signer_pubkey_hex: &str,
    ) -> serde_json::Value {
        let canonical = canonical_request_bytes(&core);
        let signing_input = request_signing_input(&core);
        let signature = signer.sign(&signing_input);
        let mut v = json!({
            "name": name,
            "description": description,
            "core": request_core_json(&core),
            "canonical_bytes_hex": hex::encode(&canonical),
            "cid": cid_from_canonical(&canonical),
            "signer_seed_hex": signer_seed_hex,
            "signer_pubkey_hex": signer_pubkey_hex,
            "signing_input_hex": hex::encode(&signing_input),
            "signature_hex": hex::encode(signature.to_bytes()),
        });
        if explicit_defaults {
            v["explicit_defaults"] = json!(true);
        }
        v
    }

    fn ack_core_json(core: &AckCore) -> serde_json::Value {
        let mut c = json!({
            "house_origin": core.house_origin,
            "popclaw_id": core.popclaw_id,
            "installation_id": core.installation_id,
            "request_id": core.request_id,
            "op_seq": core.op_seq,
            "operation": op_name(core.operation),
            "outcome": match core.outcome {
                x if x == popclaw_contracts::housesession::Outcome::Entered as i32 => "ENTERED",
                x if x == popclaw_contracts::housesession::Outcome::AlreadyEntered as i32 => "ALREADY_ENTERED",
                x if x == popclaw_contracts::housesession::Outcome::Renewed as i32 => "RENEWED",
                x if x == popclaw_contracts::housesession::Outcome::Closed as i32 => "CLOSED",
                x if x == popclaw_contracts::housesession::Outcome::AlreadyClosed as i32 => "ALREADY_CLOSED",
                x if x == popclaw_contracts::housesession::Outcome::Superseded as i32 => "SUPERSEDED",
                x if x == popclaw_contracts::housesession::Outcome::Rejected as i32 => "REJECTED",
                x if x == popclaw_contracts::housesession::Outcome::Reported as i32 => "REPORTED",
                _ => panic!("unknown outcome"),
            },
            "house_revision": core.house_revision,
            "session_id": core.session_id,
            "session_active": core.session_active,
            "lease_expires_at": core.lease_expires_at,
            "server_committed_at": core.server_committed_at,
            "detail": core.detail,
        });
        if core.error_code != 0 {
            let name = match core.error_code {
                x if x == popclaw_contracts::housesession::ErrorCode::InvalidHouse as i32 => {
                    "INVALID_HOUSE"
                }
                x if x
                    == popclaw_contracts::housesession::ErrorCode::HouseLifecycleUnsupported
                        as i32 =>
                {
                    "HOUSE_LIFECYCLE_UNSUPPORTED"
                }
                x if x == popclaw_contracts::housesession::ErrorCode::HouseDisabled as i32 => {
                    "HOUSE_DISABLED"
                }
                x if x == popclaw_contracts::housesession::ErrorCode::ExecutorBusy as i32 => {
                    "EXECUTOR_BUSY"
                }
                x if x == popclaw_contracts::housesession::ErrorCode::StaleOperation as i32 => {
                    "STALE_OPERATION"
                }
                x if x == popclaw_contracts::housesession::ErrorCode::SessionFenced as i32 => {
                    "SESSION_FENCED"
                }
                x if x == popclaw_contracts::housesession::ErrorCode::LeaseExpired as i32 => {
                    "LEASE_EXPIRED"
                }
                x if x == popclaw_contracts::housesession::ErrorCode::AuthInvalid as i32 => {
                    "AUTH_INVALID"
                }
                x if x == popclaw_contracts::housesession::ErrorCode::AudienceMismatch as i32 => {
                    "AUDIENCE_MISMATCH"
                }
                x if x
                    == popclaw_contracts::housesession::ErrorCode::IdempotencyConflict as i32 =>
                {
                    "IDEMPOTENCY_CONFLICT"
                }
                x if x == popclaw_contracts::housesession::ErrorCode::PersistenceFailed as i32 => {
                    "PERSISTENCE_FAILED"
                }
                x if x
                    == popclaw_contracts::housesession::ErrorCode::ActionResultUnknown as i32 =>
                {
                    "ACTION_RESULT_UNKNOWN"
                }
                _ => panic!("unknown error code"),
            };
            c["error_code"] = json!(name);
        }
        if let Some(s) = &core.status {
            c["status"] = json!({
                "session_id": s.session_id,
                "house_revision": s.house_revision,
                "lease_expires_at": s.lease_expires_at,
                "installation_id": s.installation_id,
                "entered_op_seq": s.entered_op_seq,
            });
        }
        c
    }

    fn signed_ack_vector(
        name: &str,
        description: &str,
        core: AckCore,
        signer: &SigningKey,
        signer_seed_hex: &str,
        signer_pubkey_hex: &str,
    ) -> serde_json::Value {
        let canonical = canonical_ack_bytes(&core);
        let signing_input = ack_signing_input(&core);
        let signature = signer.sign(&signing_input);
        json!({
            "name": name,
            "description": description,
            "core": ack_core_json(&core),
            "canonical_bytes_hex": hex::encode(&canonical),
            "cid": cid_from_canonical(&canonical),
            "signer_seed_hex": signer_seed_hex,
            "signer_pubkey_hex": signer_pubkey_hex,
            "signing_input_hex": hex::encode(&signing_input),
            "signature_hex": hex::encode(signature.to_bytes()),
        })
    }

    fn ack_core(
        operation: Operation,
        request_id: &str,
        op_seq: u64,
        outcome: popclaw_contracts::housesession::Outcome,
        house_revision: u64,
        session_id: &str,
        session_active: bool,
        error_code: i32,
        detail: &str,
    ) -> AckCore {
        AckCore {
            house_origin: HOUSE_SESSION_ORIGIN.into(),
            popclaw_id: hs_popclaw_id(),
            installation_id: HS_INSTALL_A.into(),
            request_id: request_id.into(),
            op_seq,
            operation: operation as i32,
            outcome: outcome as i32,
            error_code,
            house_revision,
            session_id: session_id.into(),
            session_active,
            lease_expires_at: if session_active { HS_ISSUED_AT + 90 } else { 0 },
            server_committed_at: HS_ISSUED_AT + 1,
            status: None,
            detail: detail.into(),
            inbox_read_token: String::new(),
        }
    }

    let mut hs_requests = vec![
        signed_request_vector(
            "enter_minimal",
            "Initial enter: omit expected_house_revision=0 and empty target_session_id; fields 10/11 emit no bytes.",
            request_core(Operation::Enter, 10, "aaaaaaaa-0000-4000-8000-000000000001", HS_INSTALL_A, 0, ""),
            false,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        ),
        signed_request_vector(
            "enter_with_expected_revision",
            "Re-enter with expected compare-and-set house_revision=3.",
            request_core(Operation::Enter, 12, "aaaaaaaa-0000-4000-8000-000000000003", HS_INSTALL_A, 3, ""),
            false,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        ),
        signed_request_vector(
            "renew_minimal",
            "Renew with the current session.",
            request_core(Operation::Renew, 13, "aaaaaaaa-0000-4000-8000-000000000004", HS_INSTALL_A, 0, "sess-demo-0002"),
            false,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        ),
        signed_request_vector(
            "leave_minimal",
            "Leave without a session ID; late leave has the same shape because its operation watermark defines the scope.",
            request_core(Operation::Leave, 11, "aaaaaaaa-0000-4000-8000-000000000002", HS_INSTALL_A, 0, ""),
            false,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        ),
        signed_request_vector(
            "leave_with_session",
            "Leave with a known session ID.",
            request_core(Operation::Leave, 14, "aaaaaaaa-0000-4000-8000-000000000005", HS_INSTALL_A, 0, "sess-demo-0002"),
            false,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        ),
        signed_request_vector(
            "status_minimal",
            "Status query does not advance op_seq; includes the latest local sequence for reference.",
            request_core(Operation::Status, 13, "aaaaaaaa-0000-4000-8000-000000000006", HS_INSTALL_A, 0, ""),
            false,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        ),
        signed_request_vector(
            "default_boundaries",
            "Explicit-default boundary: expected_house_revision=0 and empty target_session_id are present in the input, but canonical bytes must match enter_minimal exactly through TypeScript default stripping and prost elision.",
            request_core(Operation::Enter, 10, "aaaaaaaa-0000-4000-8000-000000000001", HS_INSTALL_A, 0, ""),
            true,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        ),
        signed_request_vector(
            "enter_big_op_seq",
            "64-bit precision boundary: op_seq=2^60 exceeds 2^53. TypeScript must preserve Long values from decode/fromObject without a Number round-trip; both languages produce identical canonical bytes.",
            request_core(Operation::Enter, 1u64 << 60, "aaaaaaaa-0000-4000-8000-000000000007", HS_INSTALL_A, 0, ""),
            false,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        ),
    ];

    // Negative identity vector: its signature is cryptographically valid, but
    // core.popclaw_id is not the base58 encoding of the signer key. The server must
    // return AUTH_INVALID. Positive vectors use matching keys.
    {
        let mut core = request_core(
            Operation::Enter,
            10,
            "cccccccc-0000-4000-8000-000000000001",
            HS_INSTALL_A,
            0,
            "",
        );
        core.popclaw_id = "7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM".into();
        let mut v = signed_request_vector(
            "signer_mismatch_rejected",
            "Actor differs from signer: the signature verifies, but popclaw_id does not equal base58(signer_pubkey); identity binding must fail with AUTH_INVALID.",
            core,
            false,
            &hs_identity_sk,
            HS_IDENTITY_SEED_HEX,
            &hs_identity_pk,
        );
        v["expect_signer_match"] = json!(false);
        hs_requests.push(v);
    }

    use popclaw_contracts::housesession::Outcome;
    let hs_acks = vec![
        signed_ack_vector(
            "ack_entered",
            "Enter acknowledgement: a new session generation is created and its lease is active.",
            ack_core(Operation::Enter, "aaaaaaaa-0000-4000-8000-000000000001", 10, Outcome::Entered, 1, "sess-demo-0001", true, 0, ""),
            &hs_house_sk,
            HS_HOUSE_SEED_HEX,
            &hs_house_pk,
        ),
        signed_ack_vector(
            "ack_closed",
            "Leave acknowledgement: the session is closed and session_active=false.",
            ack_core(Operation::Leave, "aaaaaaaa-0000-4000-8000-000000000002", 11, Outcome::Closed, 2, "sess-demo-0001", false, 0, ""),
            &hs_house_sk,
            HS_HOUSE_SEED_HEX,
            &hs_house_pk,
        ),
        signed_ack_vector(
            "ack_superseded",
            "Late leave acknowledgement: SUPERSEDED; the newer sess-demo-0002 remains session_active=true and is not closed by the old logout.",
            ack_core(Operation::Leave, "aaaaaaaa-0000-4000-8000-000000000002", 11, Outcome::Superseded, 4, "sess-demo-0002", true, 0, "seq 11 predates the live enter at seq 12"),
            &hs_house_sk,
            HS_HOUSE_SEED_HEX,
            &hs_house_pk,
        ),
        signed_ack_vector(
            "ack_rejected_busy",
            "Cross-installation conflict: REJECTED with EXECUTOR_BUSY; do not expose or preempt the holder session.",
            ack_core(Operation::Enter, "bbbbbbbb-0000-4000-8000-000000000001", 1, Outcome::Rejected, 1, "", true, popclaw_contracts::housesession::ErrorCode::ExecutorBusy as i32, "held by another installation"),
            &hs_house_sk,
            HS_HOUSE_SEED_HEX,
            &hs_house_pk,
        ),
        signed_ack_vector(
            "ack_status_reported",
            "Status acknowledgement: REPORTED with a session snapshot.",
            AckCore {
                status: Some(SessionInfo {
                    session_id: "sess-demo-0002".into(),
                    house_revision: 4,
                    lease_expires_at: HS_ISSUED_AT + 90,
                    installation_id: HS_INSTALL_A.into(),
                    entered_op_seq: 12,
                }),
                ..ack_core(Operation::Status, "aaaaaaaa-0000-4000-8000-000000000006", 13, Outcome::Reported, 4, "sess-demo-0002", true, 0, "")
            },
            &hs_house_sk,
            HS_HOUSE_SEED_HEX,
            &hs_house_pk,
        ),
        signed_ack_vector(
            "ack_empty_status_presence",
            "Presence boundary: explicitly empty SessionInfo encodes as tag plus zero length (7200). TypeScript decode and canonicalization must retain empty-message presence even when every nested scalar is default.",
            AckCore {
                status: Some(SessionInfo::default()),
                ..ack_core(Operation::Status, "aaaaaaaa-0000-4000-8000-000000000006", 13, Outcome::Reported, 4, "", false, 0, "")
            },
            &hs_house_sk,
            HS_HOUSE_SEED_HEX,
            &hs_house_pk,
        ),
    ];

    // Sequence fixtures follow actual server processing order. Locally generated but
    // undelivered operations appear only in descriptions. Repeated request_id means
    // idempotent delivery=replay with an ALREADY_* outcome. Cross-language consistency
    // tests and server integration tests consume the same data.
    let hs_sequences = json!([
        {
            "name": "enter_rotated_enter_late_leave",
            "description": "Two logins around a delayed logout, in server delivery order. LEAVE(11) is generated locally but not delivered. ENTER(12) performs same-installation generation rotation: close the old session, increment the fence and create a new session. LEAVE(11) then arrives for the first time: entered_op_seq=12 exceeds 11, so it is SUPERSEDED and session_active=true throughout. Old logout never closes the newer generation.",
            "steps": [
                { "op": "ENTER", "op_seq": 10, "request_id": "r-e1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED" },
                { "op": "ENTER", "op_seq": 12, "request_id": "r-e2", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED", "note": "op_seq exceeds the old entered_op_seq=10: generation rotation returns ENTERED, not ALREADY_ENTERED reuse." },
                { "op": "LEAVE", "op_seq": 11, "request_id": "r-l1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "SUPERSEDED", "note": "Generated earlier but delivered to the server for the first time now; record the watermark without changing the newer generation." }
            ]
        },
        {
            "name": "enter_retry_same_seq_already_entered",
            "description": "Enter retry at the same op_seq: the same installation and generation return ALREADY_ENTERED, reuse the session and refresh the lease without rotation or a fence increase.",
            "steps": [
                { "op": "ENTER", "op_seq": 10, "request_id": "r-e1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED" },
                { "op": "ENTER", "op_seq": 10, "request_id": "r-e1", "installation_id": HS_INSTALL_A, "delivery": "replay", "expected_outcome": "ALREADY_ENTERED", "note": "Idempotent replay of the same request_id; refresh signing times and nonce without changing semantic contents." }
            ]
        },
        {
            "name": "enter_leave_enter_leave_retry",
            "description": "Re-enter after committed leave, followed by an old retry: LEAVE(11) commits CLOSED; ENTER(12) creates a new generation; replaying LEAVE(11) returns ALREADY_CLOSED, settles only its old outbox row and preserves the newer session.",
            "steps": [
                { "op": "ENTER", "op_seq": 10, "request_id": "r-e1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED" },
                { "op": "LEAVE", "op_seq": 11, "request_id": "r-l1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "CLOSED" },
                { "op": "ENTER", "op_seq": 12, "request_id": "r-e2", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED", "note": "New generation after a completed leave." },
                { "op": "LEAVE", "op_seq": 11, "request_id": "r-l1", "installation_id": HS_INSTALL_A, "delivery": "replay", "expected_outcome": "ALREADY_CLOSED", "note": "Retry of an already decided request: replay its stored outcome with no new side effects." }
            ]
        },
        {
            "name": "leave_before_enter_commit",
            "description": "Logout before unacknowledged enter: leave(11) arrives first, records a disabled-through=11 tombstone even without a session and returns session_active=false. A late enter(10) is rejected by the watermark, leaving no orphan session.",
            "steps": [
                { "op": "LEAVE", "op_seq": 11, "request_id": "r-l1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "CLOSED" },
                { "op": "ENTER", "op_seq": 10, "request_id": "r-e1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "REJECTED", "expected_error_code": "STALE_OPERATION" }
            ]
        },
        {
            "name": "leave_ack_lost_retry",
            "description": "Leave commits but its ACK is lost. Retrying the same request_id returns ALREADY_CLOSED with no second effect. After re-entry, an old ACK settles only its original outbox row and preserves new state.",
            "steps": [
                { "op": "LEAVE", "op_seq": 11, "request_id": "r-l1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "CLOSED", "note": "ACK lost in transit after server commit." },
                { "op": "LEAVE", "op_seq": 11, "request_id": "r-l1", "installation_id": HS_INSTALL_A, "delivery": "replay", "expected_outcome": "ALREADY_CLOSED", "note": "Refresh signing times and nonce while preserving semantic request_id." }
            ]
        },
        {
            "name": "cross_installation_busy",
            "description": "Concurrent login across installations: one executor per house and identity; the later requester receives REJECTED with EXECUTOR_BUSY, without preemption or background takeover polling. Generation rotation applies only within one installation.",
            "steps": [
                { "op": "ENTER", "op_seq": 10, "request_id": "r-eA1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED" },
                { "op": "ENTER", "op_seq": 1, "request_id": "r-eB1", "installation_id": HS_INSTALL_B, "delivery": "first", "expected_outcome": "REJECTED", "expected_error_code": "EXECUTOR_BUSY" }
            ]
        },
        {
            "name": "renew_after_fence_rejected",
            "description": "Renew of a fenced generation cannot substitute for enter: reject with SESSION_FENCED and never revive the old session.",
            "steps": [
                { "op": "ENTER", "op_seq": 10, "request_id": "r-e1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED" },
                { "op": "LEAVE", "op_seq": 11, "request_id": "r-l1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "CLOSED" },
                { "op": "ENTER", "op_seq": 12, "request_id": "r-e2", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED" },
                { "op": "RENEW", "op_seq": 13, "request_id": "r-n1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "REJECTED", "expected_error_code": "SESSION_FENCED", "note": "target_session_id=sess-demo-0001 identifies the fenced old generation." }
            ]
        },
        {
            "name": "status_authenticated_report",
            "description": "Status requires signature authentication before returning a REPORTED snapshot. Unsigned probes are rejected at HTTP level without a signed acknowledgement; they are outside these sequence steps and require an HTTP 401 integration check.",
            "steps": [
                { "op": "ENTER", "op_seq": 10, "request_id": "r-e1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "ENTERED" },
                { "op": "STATUS", "op_seq": 10, "request_id": "r-s1", "installation_id": HS_INSTALL_A, "delivery": "first", "expected_outcome": "REPORTED" }
            ]
        }
    ]);

    let house_session_group = json!({
        "requests": hs_requests,
        "acks": hs_acks,
        "sequences": hs_sequences,
    });

    // ---- sigil vectors ----
    let sigil_inputs = [("BlackFeather", 6), ("Scout", 6), ("BlackFeather", 12)];
    let sigil_vectors: Vec<_> = sigil_inputs
        .iter()
        .map(|(input, len)| {
            json!({
                "popclaw_id": input,
                "length": len,
                "expected": sigil(input, *len),
            })
        })
        .collect();

    // ---- signature_roundtrip vectors ----
    // A deterministic seed (32 bytes), known public key derivable.
    let seed_hex = "0011223344556677889900aabbccddeeff00112233445566778899aabbccddee";
    let seed_bytes: [u8; 32] = hex::decode(seed_hex)?.try_into().unwrap();
    let sk = SigningKey::from_bytes(&seed_bytes);
    let pk = sk.verifying_key();
    let sig = sk.sign(&canon1);

    let json_out = json!({
        "canonical_serialization": [
            {
                "name": "invite_request_payload_minimal",
                "input_envelope_description": "EventEnvelope (actor=31-one popclaw_id, target=BROADCAST, twitter, ts=1713657600) carrying InviteRequestPayload{platform=twitter, handle=testuser, nickname=Test User}",
                "canonical_bytes_hex": hex::encode(&canon_invite_request),
                "cid": cid_invite_request,
            },
            json!({
                "name": "invite_request_with_landing_url",
                "input_envelope_description":
                    "InviteRequestPayload twitter/testuser/Test User with landing_url populated",
                "canonical_bytes_hex": hex::encode(&canon_invite_request_landing),
                "cid": cid_invite_request_landing,
            }),
            {
                "name": "quest_dispatch_verify_invite_minimal",
                "input_envelope_description": "EventEnvelope carrying QuestDispatchPayload{kind=VERIFY_INVITE, task_id=...0001, expires_at=1713744000, verify_invite={twitter/testuser, applicant=bytes 0..31, sigil=837a8c}}",
                "canonical_bytes_hex": hex::encode(&canon_qd_verify),
                "cid": cid_qd_verify,
            },
            {
                "name": "quest_dispatch_scrape_content_minimal",
                "input_envelope_description": "EventEnvelope carrying QuestDispatchPayload{kind=SCRAPE_CONTENT, task_id=...0002, expires_at=1713744000, scrape_content={twitter/testuser, since=0, max_items=20}}",
                "canonical_bytes_hex": hex::encode(&canon_qd_scrape),
                "cid": cid_qd_scrape,
            },
            {
                "name": "quest_result_approve_minimal",
                "input_envelope_description": "EventEnvelope carrying QuestResultPayload{task_id=...0001, outcome=APPROVE, evidence_hash=fixed 32B, evidence_sample=empty, reason=empty}",
                "canonical_bytes_hex": hex::encode(&canon_qr_approve),
                "cid": cid_qr_approve,
            },
            {
                "name": "invite_verified_milestone_minimal",
                "input_envelope_description": "EventEnvelope carrying InviteVerifiedPayload{task_id=...0001, applicant=bytes 0..31, twitter/testuser, approve_count=2, reject_count=1}",
                "canonical_bytes_hex": hex::encode(&canon_iv_milestone),
                "cid": cid_iv_milestone,
            },
            {
                "name": "ranger_registration_minimal",
                "input_envelope_description": "EventEnvelope carrying RangerRegistration{capabilities=[\"x\"], availability_score=100}",
                "canonical_bytes_hex": hex::encode(&canon_reg),
                "cid": cid_reg,
            },
            {
                "name": "watch_dispatch_minimal",
                "input_envelope_description": "EventEnvelope carrying WatchDispatch{watch_id=...0001, target_popclaw_id=31-one, platform=x}",
                "canonical_bytes_hex": hex::encode(&canon_wd),
                "cid": cid_wd,
            },
            {
                "name": "watch_heartbeat_minimal",
                "input_envelope_description": "EventEnvelope carrying WatchHeartbeat{watch_id=...0001, active_since=1777000000, recent_hits=3}",
                "canonical_bytes_hex": hex::encode(&canon_hb),
                "cid": cid_hb,
            },
            {
                "name": "watch_cancel_minimal",
                "input_envelope_description": "EventEnvelope carrying WatchCancel{watch_id=...0001, reason=reassigned}",
                "canonical_bytes_hex": hex::encode(&canon_wc),
                "cid": cid_wc,
            },
            {
                "name": "post_root_minimal",
                "input_envelope_description": "EventEnvelope (actor BlackFeather, lorehouse=empty, ts=1713657600) carrying PostPayload{blocks=[TEXT 'hi'], media=[]}, prev_event_id empty (root)",
                "canonical_bytes_hex": hex::encode(&canon_post_root),
                "cid": cid_post_root,
            },
            {
                "name": "post_reply_minimal",
                "input_envelope_description": "EventEnvelope (actor Scout, lorehouse=empty, ts=1713657700) carrying PostPayload{blocks=[TEXT 'ack'], media=[]}, prev_event_id = CID of post_root_minimal",
                "canonical_bytes_hex": hex::encode(&canon_post_reply),
                "cid": cid_post_reply,
            },
            {
                "name": "post_quote_minimal",
                "input_envelope_description": format!(
                    "EventEnvelope (actor Scout, lorehouse=empty, ts=1713657800) carrying \
                     PostPayload{{blocks=[TEXT containing a fixed UTF-8 Chinese sample, LINK_CARD '{post_quote_link}'], \
                     media=[]}}, prev_event_id = CID of post_root_minimal"
                ),
                "canonical_bytes_hex": hex::encode(&canon_post_quote),
                "cid": cid_post_quote,
            },
            {
                "name": "profile_minimal",
                "input_envelope_description": "Profile with nickname BlackFeather, two taste_tags, seeker role, location_hint Hangzhou, declared_at 1747526400",
                "canonical_bytes_hex": hex::encode(&canon_profile),
                "cid": cid_profile,
            },
            {
                "name": "reply_minimal",
                "input_envelope_description": "EventEnvelope (actor Scout, lorehouse=empty, ts=1713657900) carrying Reply{from=Scout, in_reply_to=PostRef{x/1234567890, author empty}, body containing a fixed UTF-8 Chinese sample, ts=1713657900}",
                "canonical_bytes_hex": hex::encode(&canon_reply),
                "cid": cid_reply,
            },
            {
                "name": "direct_message_minimal",
                "input_envelope_description": "EventEnvelope (actor Scout, lorehouse=empty, ts=1713658000) carrying DirectMessage{from=Scout, to=BlackFeather, no in_reply_to_post, body containing a fixed UTF-8 Chinese sample, ts=1713658000, ciphertext/nonce ABSENT(elide)} — DM-encryption parity case 1/3; CID pinned pre-encryption and MUST NOT drift",
                "canonical_bytes_hex": hex::encode(&canon_dm),
                "cid": cid_dm,
            },
            {
                "name": "direct_message_encrypted",
                "input_envelope_description": "Same envelope as direct_message_minimal but DirectMessage{body='[encrypted]' placeholder, ciphertext=16 opaque bytes incl. 0x00/0xff (field 6), nonce=bytes 0..23 (field 7)} — DM-encryption parity case 2/3 (PRESENT)",
                "canonical_bytes_hex": hex::encode(&canon_dm_encrypted),
                "cid": cid_dm_encrypted,
            },
            {
                "name": "direct_message_empty_ciphertext",
                "input_envelope_description": "Same envelope as direct_message_minimal with ciphertext=b'' and nonce=b'' PRESENT-BUT-EMPTY — DM-encryption parity case 3/3; proto3 bytes defaults MUST elide, so bytes+CID are identical to direct_message_minimal",
                "canonical_bytes_hex": hex::encode(&canon_dm_empty_ct),
                "cid": cid_dm_empty_ct,
            },
            {
                "name": "actor_device_id_empty",
                "input_envelope_description": "Same envelope as direct_message_minimal but ActorInfo.device_id = Some(b'') — proto3 EXPLICIT-presence (`optional bytes`) boundary: presence is tracked, so both prost and pbjs MUST emit tag 0x22 + len 0 rather than eliding. Guards against a canonicalizer that blanket-drops empty byte arrays.",
                "canonical_bytes_hex": hex::encode(&canon_device_id_empty),
                "cid": cid_device_id_empty,
            },
            {
                "name": "follow_declared_minimal",
                "input_envelope_description": "EventEnvelope carrying FollowDeclared{followee=BlackFeather id, follow_type=PUBLIC(elide), taste_subscribed=true(emit), visibility=SV_PUBLIC(elide)}",
                "canonical_bytes_hex": hex::encode(&canon_follow),
                "cid": cid_follow,
            },
            {
                "name": "follow_revoked_minimal",
                "input_envelope_description": "EventEnvelope carrying FollowRevoked{followee=BlackFeather id, follow_type=PUBLIC(elide)}",
                "canonical_bytes_hex": hex::encode(&canon_unfollow),
                "cid": cid_unfollow,
            },
            {
                "name": "follow_declared_ordered",
                "input_envelope_description": "Scope B envelope carrying FollowDeclared with RelationOrder{seq=7(emit), house_key=BlackFeather id(emit), resolves=[](elide)} — ordered mode",
                "canonical_bytes_hex": hex::encode(&canon_follow_ordered),
                "cid": cid_follow_ordered,
            },
            {
                "name": "follow_declared_order_present_but_empty",
                "input_envelope_description": "Same as follow_declared_ordered but RelationOrder is entirely default. proto3 message fields have EXPLICIT presence, so the sub-message MUST still emit (tag + len 0) — 'present but empty' must stay distinguishable from 'absent', or ordered mode silently degrades to legacy",
                "canonical_bytes_hex": hex::encode(&canon_follow_order_empty),
                "cid": cid_follow_order_empty,
            },
            {
                "name": "follow_declared_seq_beyond_double",
                "input_envelope_description": "Ordered FollowDeclared with seq = 2^53+1, the first uint64 a JS Number cannot hold. Pins that both languages carry the counter losslessly — a counter that silently rounds is worse than one that fails",
                "canonical_bytes_hex": hex::encode(&canon_follow_big_seq),
                "cid": cid_follow_big_seq,
            },
            {
                "name": "follow_revoked_ordered_recovery",
                "input_envelope_description": "Scope B envelope carrying FollowRevoked with RelationOrder{seq=9, house_key, resolves=[64*'a', 64*'b']} — a fork recovery statement; the repeated string field emits both entries in order",
                "canonical_bytes_hex": hex::encode(&canon_unfollow_ordered),
                "cid": cid_unfollow_ordered,
            },
            {
                "name": "namecard_popclaw_minimal",
                "input_envelope_description": "Production namecard envelope (no target, lorehouse=empty, ts=1747526400) carrying Profile{nickname=BlackFeather, declared_at=1747526400, all else elided}",
                "canonical_bytes_hex": hex::encode(&canon_namecard),
                "cid": cid_namecard,
            },
            {
                "name": "post_with_origin",
                "input_envelope_description": "EventEnvelope (actor BlackFeather, lorehouse=empty, ts=1750100000) carrying Post{blocks=[TEXT containing a fixed UTF-8 Chinese sample], media=[], origin={platform=x, post_id=1800000000000000001, url=https://x.com/blackfeather_pc/status/1800000000000000001, created_at=1750099800, reply_to_id=''(elides)}} — Origin on Post",
                "canonical_bytes_hex": hex::encode(&canon_post_with_origin),
                "cid": cid_post_with_origin,
            },
            {
                "name": "invite_verified_with_account_id",
                "input_envelope_description": "EventEnvelope carrying InviteVerified{task_id=...0001, applicant=bytes 0..31, x/blackfeather_pc, approve_count=3, reject_count=0(elides), follower_count=12400, account_id=1234567890} — account_id on InviteVerified",
                "canonical_bytes_hex": hex::encode(&canon_iv_with_account_id),
                "cid": cid_iv_with_account_id,
            },
            {
                "name": "verified_platform_with_account_id",
                "input_envelope_description": "Standalone VerifiedPlatform{platform=x, handle=blackfeather_pc, profile_url=https://x.com/blackfeather_pc, follower_count=12400, account_id=1234567890} sub-message canonical bytes — account_id on VerifiedPlatform",
                "canonical_bytes_hex": vp_hex,
                "cid": vp_cid,
            },
            {
                "name": "house_event_minimal",
                "input_envelope_description": "EventEnvelope carrying HouseEvent{kind=world.postcard, schema_version=1, body=9 opaque bytes incl. 0x00 and 0xff} — federation spec Layer 2 extension slot (field 34)",
                "canonical_bytes_hex": hex::encode(&canon_house_event),
                "cid": cid_house_event,
            },
            {
                "name": "house_event_default_boundaries",
                "input_envelope_description": "EventEnvelope carrying HouseEvent{kind=world.encounter, schema_version=0(elides), body=empty(elides)} — proto3 default boundary; pbjs MUST omit both to match prost",
                "canonical_bytes_hex": hex::encode(&canon_house_event_defaults),
                "cid": cid_house_event_defaults,
            },
            {
                "name": "intent_minimal",
                "input_envelope_description": "EventEnvelope carrying IntentPayload{lorehouse=world, intent_kind=world.pack_and_travel, params={\"destination\":\"kyoto\"}} — federation spec upstream primitive (field 35)",
                "canonical_bytes_hex": hex::encode(&canon_intent),
                "cid": cid_intent,
            },
            {
                "name": "intent_default_boundaries",
                "input_envelope_description": "EventEnvelope carrying IntentPayload{lorehouse=''(elides), intent_kind=world.look_around, params=empty(elides)} — proto3 default boundary",
                "canonical_bytes_hex": hex::encode(&canon_intent_defaults),
                "cid": cid_intent_defaults,
            }
        ],
        "sigil": sigil_vectors,
        "house_session": house_session_group,
        "signature_roundtrip": [
            {
                "name": "master_key_signs_canon1",
                "master_private_key_hex": seed_hex,
                "master_public_key_hex": hex::encode(pk.as_bytes()),
                "canonical_bytes_hex": hex::encode(&canon1),
                "signature_hex": hex::encode(sig.to_bytes()),
            }
        ]
    });

    let pretty = serde_json::to_string_pretty(&json_out)?;
    fs::write(&out, pretty + "\n")?;
    println!("wrote {}", out.display());
    Ok(())
}

fn find_repo_root() -> anyhow::Result<PathBuf> {
    let mut p = std::env::current_dir()?;
    loop {
        if p.join("Cargo.toml").is_file() && p.join("pnpm-workspace.yaml").is_file() {
            return Ok(p);
        }
        p = p
            .parent()
            .ok_or_else(|| anyhow::anyhow!("repo root not found"))?
            .to_path_buf();
    }
}
