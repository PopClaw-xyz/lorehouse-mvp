import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { canonicalizeEnvelope } from '../src/canonical.js';
import { popclaw } from '@popclaw/contracts';

const FIXTURES_PATH = resolve(__dirname, '../../../fixtures/test-vectors.json');

type Vector = {
  name: string;
  canonical_bytes_hex: string;
  cid: string;
};

function toHex(bytes: Uint8Array): string {
  let s = '';
  for (const b of bytes) s += b.toString(16).padStart(2, '0');
  return s;
}

function envelopeByName(name: string): Record<string, unknown> {
  // These envelopes mirror the hardcoded inputs in
  // packages/contracts/crates/algorithms/src/bin/gen_fixtures.rs.
  // Any change there MUST be reflected here (and vice versa).
  //
  // NOTE: protobufjs encode() reads camelCase field names directly
  // (eventId, popclawId, originalUrl) — NOT snake_case.
  // ---- Scope B payload-variant vectors. Common outer fields: ----
  // actor.popclaw_id = 32×'1', target = {scope: BROADCAST (=0, default)},
  // lorehouse = 'twitter' (kept non-empty to distinguish Scope B envelopes),
  // timestamp = 1713657600. Only payload differs.
  const scopeBOuter = {
    actor: { popclawId: '11111111111111111111111111111111' },
    target: {}, // Present-but-empty Recipient; prost emits tag+len=0.
    lorehouse: 'twitter',
    timestamp: 1_713_657_600,
  };
  // Relation vectors are scoped to one house: `lorehouse` carries the base58
  // house key, the same value that appears inside RelationOrder.house_key.
  // Deliberately DIFFERENT from the followee id used in these vectors: when
  // house_key and followee are the same string, an implementation that fills
  // one with the other produces identical bytes and the vector is blind to it.
  const HOUSE_KEY = '9xQeWy8P3vNhKd2RmTzA6BcFgJ4LnSuVoXpYrEt5Hw1Z';
  const relationOuter = { ...scopeBOuter, lorehouse: HOUSE_KEY };
  // Raw 32 bytes 0..31 — used wherever the spec says
  // applicant_popclaw_id = base64(bytes 0..31).
  const applicantPkBytes = new Uint8Array(32);
  for (let i = 0; i < 32; i++) applicantPkBytes[i] = i;
  // Base64 decode of ZVbD0J7/SXeOzFaVq5pC2wlXtFYQm1xn7Jt3NnJ7s6c= — the
  // QuestResult evidence_hash in the spec.
  const evidenceHash = new Uint8Array([
    0x65, 0x56, 0xc3, 0xd0, 0x9e, 0xff, 0x49, 0x77, 0x8e, 0xcc, 0x56, 0x95, 0xab, 0x9a, 0x42,
    0xdb, 0x09, 0x57, 0xb4, 0x56, 0x10, 0x9b, 0x5c, 0x67, 0xec, 0x9b, 0x77, 0x36, 0x72, 0x7b,
    0xb3, 0xa7,
  ]);
  const TASK_ID_1 = '00000000-0000-0000-0000-000000000001';
  const TASK_ID_2 = '00000000-0000-0000-0000-000000000002';
  const EXPIRES_AT = 1_713_744_000;

  if (name === 'invite_request_payload_minimal') {
    return {
      ...scopeBOuter,
      inviteRequest: {
        platform: 'twitter',
        handle: 'testuser',
        nickname: 'Test User',
      },
    };
  }
  if (name === 'quest_dispatch_verify_invite_minimal') {
    return {
      ...scopeBOuter,
      questDispatch: {
        taskId: TASK_ID_1,
        kind: 1, // QUEST_KIND_VERIFY_INVITE
        expiresAt: EXPIRES_AT,
        verifyInvite: {
          platform: 'twitter',
          handle: 'testuser',
          applicantPopclawId: applicantPkBytes,
          expectedSigil: '837a8c',
        },
      },
    };
  }
  if (name === 'quest_dispatch_scrape_content_minimal') {
    return {
      ...scopeBOuter,
      questDispatch: {
        taskId: TASK_ID_2,
        kind: 2, // QUEST_KIND_SCRAPE_CONTENT
        expiresAt: EXPIRES_AT,
        scrapeContent: {
          platform: 'twitter',
          handle: 'testuser',
          // sinceTimestamp omitted — proto3 default (0) must not be emitted.
          maxItems: 20,
        },
      },
    };
  }
  if (name === 'quest_result_approve_minimal') {
    return {
      ...scopeBOuter,
      questResult: {
        taskId: TASK_ID_1,
        outcome: 1, // QUEST_OUTCOME_APPROVE
        evidenceHash,
      },
    };
  }
  if (name === 'invite_verified_milestone_minimal') {
    return {
      ...scopeBOuter,
      inviteVerified: {
        taskId: TASK_ID_1,
        applicantPopclawId: applicantPkBytes,
        platform: 'twitter',
        handle: 'testuser',
        approveCount: 2,
        rejectCount: 1,
      },
    };
  }

  // ---- payload-variant vectors. ----
  const WATCH_ID_1 = '00000000-0000-0000-0000-000000000001';

  if (name === 'ranger_registration_minimal') {
    return {
      ...scopeBOuter,
      rangerRegistration: {
        capabilities: ['x'],
        availabilityScore: 100,
      },
    };
  }
  if (name === 'watch_dispatch_minimal') {
    return {
      ...scopeBOuter,
      watchDispatch: {
        watchId: WATCH_ID_1,
        targetPopclawId: '11111111111111111111111111111111',
        platform: 'x',
        handle: 'blackfeather',
      },
    };
  }
  if (name === 'watch_heartbeat_minimal') {
    return {
      ...scopeBOuter,
      watchHeartbeat: {
        watchId: WATCH_ID_1,
        activeSince: 1_777_000_000,
        recentHits: 3,
      },
    };
  }
  if (name === 'watch_cancel_minimal') {
    return {
      ...scopeBOuter,
      watchCancel: {
        watchId: WATCH_ID_1,
        reason: 'reassigned',
      },
    };
  }
  // ---- popclaw-native Post protocol layer vectors. ----
  if (name === 'post_root_minimal') {
    // Mirror of gen_fixtures.rs Vector 13.
    return {
      actor: {
        popclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
        nickname: 'BlackFeather',
      },
      // lorehouse omitted — proto3 default "" elides (task 4.5b)
      timestamp: 1_713_657_600,
      // prevEventId omitted — proto3 default "" must NOT emit on wire.
      post: {
        blocks: [
          // blockType=TEXT (=0) MUST be omitted to mirror prost default-
          // elision (same pattern as MediaAttachment).
          { content: 'hi' },
        ],
      },
    };
  }
  if (name === 'post_reply_minimal') {
    // Mirror of gen_fixtures.rs Vector 14.
    return {
      actor: {
        popclawId: '6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM',
        nickname: 'Scout',
      },
      // lorehouse omitted — proto3 default "" elides (task 4.5b)
      timestamp: 1_713_657_700,
      prevEventId: vectors.canonical_serialization.find(
        (v) => v.name === 'post_root_minimal'
      )!.cid,
      post: {
        blocks: [{ content: 'ack' }],
      },
    };
  }
  if (name === 'profile_minimal') {
    // Mirror of gen_fixtures.rs profile_minimal.
    return {
      ...scopeBOuter,
      profile: {
        nickname: 'BlackFeather',
        oneLineIntro: '杭州，AI agent 研究者，爱龙虾',
        tasteTags: ['ai-agents', 'lobster-cuisine'],
        rolePersona: 'seeker',
        locationHint: 'Hangzhou',
        // avatarUri omitted — proto3 default "" must not be emitted.
        declaredAt: 1_747_526_400,
      },
    };
  }
  if (name === 'invite_request_with_landing_url') {
    // Mirror of gen_fixtures.rs invite_request_with_landing_url.
    return {
      ...scopeBOuter,
      inviteRequest: {
        platform: 'twitter',
        handle: 'testuser',
        nickname: 'Test User',
        landingUrl:
          'https://popclaw.me/invite/11111111111111111111111111111111?sigil=837a8c&nick=Test%20User',
      },
    };
  }
  if (name === 'post_quote_minimal') {
    // Mirror of gen_fixtures.rs Vector 15.
    const postRootCid = vectors.canonical_serialization.find(
      (v) => v.name === 'post_root_minimal'
    )!.cid;
    return {
      actor: {
        popclawId: '6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM',
        nickname: 'Scout',
      },
      // lorehouse omitted — proto3 default "" elides (task 4.5b)
      timestamp: 1_713_657_800,
      prevEventId: postRootCid,
      post: {
        blocks: [
          // blockType=TEXT (=0) MUST be omitted — proto3 default elision (Invariant #1).
          { content: '城东更便宜' },
          // blockType=LINK_CARD (=5) MUST be emitted — non-zero value.
          { blockType: 5, content: `https://popclaw.me/post/${postRootCid}` },
        ],
      },
    };
  }
  if (name === 'reply_minimal') {
    // Mirror of gen_fixtures.rs reply_minimal.
    return {
      actor: {
        popclawId: '6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM',
        nickname: 'Scout',
      },
      // lorehouse omitted — proto3 default "" elides (task 4.5b)
      timestamp: 1_713_657_900,
      reply: {
        fromPopclawId: '6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM',
        // authorPopclawId omitted — proto3 default "" must NOT emit.
        inReplyTo: { platform: 'x', platformPostId: '1234567890' },
        body: '好帖',
        ts: 1_713_657_900,
      },
    };
  }
  // ---- DM-encryption parity triple (additive fields 6/7) ----
  // The three shapes that decide whether adding `bytes ciphertext`/`nonce` to
  // DirectMessage can break signatures: ABSENT / PRESENT / PRESENT-BUT-EMPTY.
  // Outer envelope is identical across all three, so the only byte delta is
  // fields 6 and 7. Mirrors gen_fixtures.rs.
  const dmOuter = {
    actor: {
      popclawId: '6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM',
      nickname: 'Scout',
    },
    // lorehouse omitted — proto3 default "" elides (task 4.5b)
    timestamp: 1_713_658_000,
  };
  const dmInner = {
    fromPopclawId: '6EowM7D4wqWmMdMLmhmpoFZ1SeJrPdGK7VNLk2fKswvM',
    toPopclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
    // inReplyToPost omitted — unset message field must NOT emit a tag.
    body: '回头细聊',
    ts: 1_713_658_000,
  };
  if (name === 'direct_message_minimal') {
    // Case 1/3: ciphertext + nonce ABSENT — the pre-encryption DM shape.
    // Its bytes must be exactly what they were before fields 6/7 existed.
    return { ...dmOuter, directMessage: { ...dmInner } };
  }
  if (name === 'direct_message_encrypted') {
    // Case 2/3: ciphertext + nonce PRESENT. `body` is the non-empty base64-ish
    // placeholder (old lore-houses reject an empty body), NOT the message.
    // Ciphertext carries 0x00 and 0xff so any UTF-8 mangling of opaque bytes
    // by pbjs surfaces as a hex mismatch instead of passing silently.
    return {
      ...dmOuter,
      directMessage: {
        ...dmInner,
        body: '[encrypted]',
        ciphertext: new Uint8Array([
          0x00, 0xff, 0x10, 0x9b, 0x5c, 0x67, 0xec, 0x9b, 0x77, 0x36, 0x72, 0x7b, 0xb3, 0xa7,
          0x00, 0xff,
        ]),
        nonce: new Uint8Array(Array.from({ length: 24 }, (_, i) => i)),
      },
    };
  }
  if (name === 'direct_message_empty_ciphertext') {
    // Case 3/3: PRESENT-BUT-EMPTY. Deliberately passes explicit zero-length
    // Uint8Arrays rather than omitting the keys — this is the exact shape that
    // has historically broken CID parity. pbjs MUST elide them just as prost
    // does, so these bytes must equal direct_message_minimal's byte for byte.
    return {
      ...dmOuter,
      directMessage: {
        ...dmInner,
        ciphertext: new Uint8Array(0),
        nonce: new Uint8Array(0),
      },
    };
  }
  if (name === 'actor_device_id_empty') {
    // Mirror of gen_fixtures.rs actor_device_id_empty.
    // ActorInfo.device_id is `optional bytes` — proto3 EXPLICIT presence, so an
    // explicitly-empty value MUST be emitted (tag 0x22 + len 0), not elided.
    // This is the opposite of the implicit-presence DM ciphertext case: a
    // canonicalizer that drops every zero-length Uint8Array breaks parity here.
    return {
      ...dmOuter,
      actor: { ...dmOuter.actor, deviceId: new Uint8Array(0) },
      directMessage: { ...dmInner },
    };
  }
  if (name === 'follow_declared_minimal') {
    // Mirror of gen_fixtures.rs follow_declared_minimal.
    return {
      ...scopeBOuter,
      followDeclared: {
        followeePopclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
        // followType PUBLIC (=0) omitted — enum default must elide.
        tasteSubscribed: true, // non-default bool MUST emit
        // tasteSubscriptionVisibility SV_PUBLIC (=0) omitted — must elide.
      },
    };
  }
  if (name === 'follow_revoked_minimal') {
    // Mirror of gen_fixtures.rs follow_revoked_minimal.
    return {
      ...scopeBOuter,
      followRevoked: {
        followeePopclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
      },
    };
  }
  if (name === 'namecard_popclaw_minimal') {
    // Mirror of gen_fixtures.rs namecard_popclaw_minimal (S1 signProfile shape).
    return {
      actor: {
        popclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
        nickname: 'BlackFeather',
      },
      // lorehouse omitted — proto3 default "" elides (task 4.5b)
      timestamp: 1_747_526_400,
      profile: {
        nickname: 'BlackFeather',
        // oneLineIntro/tasteTags/rolePersona/locationHint/avatarUri omitted —
        // proto3 defaults must NOT emit (Invariant #1).
        declaredAt: 1_747_526_400,
      },
    };
  }
  if (name === 'post_with_origin') {
    // Mirror of gen_fixtures.rs post_with_origin — Post with Origin set.
    // Exercises Post.origin field 3 and all 5 Origin sub-fields.
    // reply_to_id="" elides (proto3 default).
    return {
      actor: {
        popclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
        nickname: 'BlackFeather',
      },
      // lorehouse omitted — proto3 default "" elides (task 4.5b)
      timestamp: 1_750_100_000,
      post: {
        blocks: [{ content: '今天的晚霞很美' }],
        origin: {
          platform: 'x',
          postId: '1800000000000000001',
          url: 'https://x.com/blackfeather_pc/status/1800000000000000001',
          createdAt: 1_750_099_800,
          // replyToId: '' — proto3 default, must NOT be emitted.
        },
      },
    };
  }

  if (name === 'invite_verified_with_account_id') {
    // Mirror of gen_fixtures.rs invite_verified_with_account_id — InviteVerified
    // with account_id set (field 8). reject_count=0 elides.
    return {
      ...scopeBOuter,
      inviteVerified: {
        taskId: TASK_ID_1,
        applicantPopclawId: applicantPkBytes,
        platform: 'x',
        handle: 'blackfeather_pc',
        approveCount: 3,
        // rejectCount: 0 — proto3 default, must NOT be emitted.
        followerCount: 12_400,
        accountId: '1234567890',
      },
    };
  }

  // ---- Federation-spec Layer 2 extension vectors (2026-07-26) ----
  // Mirrors of gen_fixtures.rs. The opaque body/params bytes must survive pbjs
  // encoding untouched, and every proto3 default MUST be omitted (not written
  // as 0 / '' / new Uint8Array(0)) or the bytes — and hence the CID — diverge
  // from prost's.
  if (name === 'house_event_minimal') {
    return {
      ...scopeBOuter,
      houseEvent: {
        kind: 'world.postcard',
        schemaVersion: 1,
        body: new Uint8Array([0x7b, 0x22, 0x74, 0x6f, 0x22, 0x3a, 0x00, 0xff, 0x7d]),
      },
    };
  }
  if (name === 'house_event_default_boundaries') {
    return {
      ...scopeBOuter,
      houseEvent: {
        kind: 'world.encounter',
        // schemaVersion: 0 and body: empty — proto3 defaults, MUST NOT be emitted.
      },
    };
  }
  if (name === 'intent_minimal') {
    return {
      ...scopeBOuter,
      intent: {
        lorehouse: 'world',
        intentKind: 'world.pack_and_travel',
        params: new TextEncoder().encode('{"destination":"kyoto"}'),
      },
    };
  }
  if (name === 'intent_default_boundaries') {
    return {
      ...scopeBOuter,
      intent: {
        // lorehouse: '' and params: empty — proto3 defaults, MUST NOT be emitted.
        intentKind: 'world.look_around',
      },
    };
  }

  if (name === 'follow_declared_ordered') {
    // Mirror of gen_fixtures.rs follow_declared_ordered.
    return {
      ...relationOuter,
      followDeclared: {
        followeePopclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
        tasteSubscribed: true,
        order: {
          seq: 7, // non-default uint64 MUST emit
          houseKey: HOUSE_KEY,
          // resolves [] omitted — an empty repeated field must elide.
        },
      },
    };
  }
  if (name === 'follow_declared_order_present_but_empty') {
    // Mirror of gen_fixtures.rs follow_declared_order_present_but_empty.
    // Every field inside `order` is default, but the sub-message itself still
    // emits (tag + len 0): proto3 message fields have EXPLICIT presence. This
    // is what lets presence be the activation marker for ordered mode — if
    // either language dropped an all-default sub-message, ordered and legacy
    // events would become indistinguishable on the wire.
    return {
      ...relationOuter,
      followDeclared: {
        followeePopclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
        tasteSubscribed: true,
        order: {},
      },
    };
  }
  if (name === 'follow_declared_seq_beyond_double') {
    // Mirror of gen_fixtures.rs follow_declared_seq_beyond_double. 2^53+1 is
    // the first uint64 a JS Number cannot hold, so this vector only matches if
    // the TS path carries the counter losslessly rather than rounding it.
    return {
      ...relationOuter,
      followDeclared: {
        followeePopclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
        order: {
          // NOT a BigInt literal: protobufjs does not accept one for a uint64
          // and silently encodes 0 — which is not even a rounding error, it is
          // the value the domain treats as "never set". A decimal string is
          // carried losslessly.
          seq: '9007199254740993',
          houseKey: HOUSE_KEY,
        },
      },
    };
  }
  if (name === 'follow_revoked_ordered_recovery') {
    // Mirror of gen_fixtures.rs follow_revoked_ordered_recovery — a fork
    // recovery statement, so `resolves` is non-empty and emits in order.
    return {
      ...relationOuter,
      followRevoked: {
        followeePopclawId: '7LhZ8x6c8Kmw5P9Wtnm4T6E7YcbTpZ7N7tfZcqLRv5cM',
        order: {
          seq: 9,
          houseKey: HOUSE_KEY,
          resolves: ['a'.repeat(64), 'b'.repeat(64)],
        },
      },
    };
  }

  throw new Error(`unknown vector name: ${name}`);
}

/**
 * Encode a named vector's canonical bytes for parity comparison.
 * Most vectors encode as EventEnvelope; the standalone VerifiedPlatform
 * sub-message (verified_platform_with_account_id) encodes via its own codec.
 */
function bytesForVector(name: string): Uint8Array {
  if (name === 'verified_platform_with_account_id') {
    // Mirror of gen_fixtures.rs standalone VerifiedPlatform encode.
    // VerifiedPlatform only appears as a projected sub-message (WorldFeedItem),
    // not as an EventEnvelope body — so we encode it directly here.
    const ns = popclaw as unknown as {
      event: {
        VerifiedPlatform: { encode(m: unknown): { finish(): Uint8Array } };
      };
    };
    return ns.event.VerifiedPlatform.encode({
      platform: 'x',
      handle: 'blackfeather_pc',
      profileUrl: 'https://x.com/blackfeather_pc',
      followerCount: 12_400,
      accountId: '1234567890',
    }).finish();
  }
  return canonicalizeEnvelope(envelopeByName(name));
}

const vectors: { canonical_serialization: Vector[] } = JSON.parse(
  readFileSync(FIXTURES_PATH, 'utf-8')
);

describe('canonical parity with Rust', () => {
  for (const v of vectors.canonical_serialization) {
    it(`canonical bytes match for ${v.name}`, () => {
      const out = bytesForVector(v.name);
      expect(toHex(out)).toBe(v.canonical_bytes_hex);
    });
  }
});

describe('implicit defaults and explicit presence', () => {
  it('elides explicit ordinary defaults while retaining empty nested messages', () => {
    expect(toHex(canonicalizeEnvelope({post: {blocks: [{blockType: 0, content: ''}]}})))
      .toBe('da01020a00');
    expect(toHex(canonicalizeEnvelope({timestamp: {low: 0, high: 0, unsigned: true}, lorehouse: '', target: {scope: 0}, post: {blocks: [{blockType: 0, content: ''}]}})))
      .toBe(toHex(canonicalizeEnvelope({target: {}, post: {blocks: [{}]}})));
  });
  it('preserves optional defaults and map values including empty keys', () => {
    expect(toHex(canonicalizeEnvelope({actor: {supersedes: '', deviceId: new Uint8Array(), role: 0}, post: {}})))
      .not.toBe(toHex(canonicalizeEnvelope({actor: {}, post: {}})));
    expect(toHex(canonicalizeEnvelope({post: {blocks: [{metadata: {'': '', a: '1', aa: '2'}}]}})))
      .toBe('da01150a131a001a060a01611201311a070a026161120132');
  });
});


describe('literal map keys', () => {
  it('retains prototype-looking keys through object cloning and decoded ingress', () => {
    const expected = 'da011a0a181a0e0a095f5f70726f746f5f5f1201761a060a0161120131';
    const input = {post: {blocks: [{metadata: JSON.parse('{"__proto__":"v","a":"1"}')} ]}};
    expect(toHex(canonicalizeEnvelope(input))).toBe(expected);
    const decoded = popclaw.event.EventEnvelope.decode(Buffer.from(expected, 'hex'));
    expect(toHex(canonicalizeEnvelope(decoded))).toBe(expected);
  });
});
