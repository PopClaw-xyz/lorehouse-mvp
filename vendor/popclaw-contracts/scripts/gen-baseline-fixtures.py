#!/usr/bin/env python3
"""Generate numeric adversarial wire and public signing vectors from fixed inputs."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'packages/contracts/python'))
from protocol import message_type, canonical_envelope
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def vi(n):
    out = bytearray()
    while n > 127:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return bytes(out)


def field(n, v):
    return vi(n << 3 | 2) + vi(len(v)) + v


def scalar(n, v):
    return vi(n << 3) + vi(v)


def b58(b):
    abc = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(b, 'big')
    out = ''
    while n:
        n, rem = divmod(n, 58)
        out = abc[rem] + out
    return '1' * (len(b) - len(b.lstrip(b'\0'))) + out


rows = []

def case(name, raw, structural, public):
    rows.append(dict(name=name, wire_hex=raw.hex(), structural=structural, public=public))


he = field(34, field(1,b'unknown-house.some_verb') + field(3,b'\xea\x01\x00\xff\x00'))
profile = field(28, field(1,b'Ada'))
case('opaque_unknown_legal_business', he, True, True)
case('profile_supported', profile, True, True)
case('typed_post_empty_structure_only', field(27,b''), True, True)
case('dm_structural_but_private', field(26,b''), True, False)
for tag in [17,30,31,32,35]:
    case('nonpublic_body_'+str(tag),field(tag,b''),True,False)
for name, raw in [
    ('reserved_outer_empty',field(29,b'')),
    ('reserved_outer_zero',scalar(29,0)),
    ('reserved_outer_fixed64',vi(29<<3|1)+b'\0'*8),
    ('reserved_outer_fixed32',vi(29<<3|5)+b'\0'*4),
    ('reserved_outer_before_supported',field(29,b'')+he),
    ('reserved_outer_after_supported',he+field(29,b'')),
    ('reserved_outer_nonminimal_tag',b'\xea\x81\x00\x00'+he),
    ('reserved_profile_empty',field(28,field(8,b''))),
    ('reserved_profile_zero',field(28,scalar(8,0))),
    ('reserved_profile_reordered',field(28,field(8,b'')+field(1,b'Ada'))),
    ('reserved_profile_discarded_oneof',field(28,field(8,b''))+he),
    ('reserved_profile_merged_occurrence',field(28,field(8,b''))+profile),
    ('duplicate_body',he+he),
    ('multiple_body',profile+he),
    ('duplicate_privacy',field(3,scalar(1,0)+scalar(1,1))+he),
    ('unknown_privacy',field(3,scalar(4,0))+he),
    ('unknown_envelope',field(99,b'')+he),
    ('wrong_body_wire',scalar(34,0)),
    ('zero_tag',b'\0'+he),
    ('truncated_length',b'\x92\x02\x7f'),
    ('overflow_varint',b'\x28'+b'\xff'*10+he),
    ('invalid_utf8',field(28,field(1,b'\xff'))),
    ('missing_body',scalar(5,1)),
    ('privacy_integer_wrap',field(3,scalar(1,1<<32))+he),
]:
    case(name,raw,False,False)
case('explicit_default_privacy',field(3,scalar(1,0))+he,True,True)
case('nonminimal_default_privacy',field(3,b'\x08\x80\x00')+he,True,True)
case('unknown_recipient_enum',field(3,scalar(1,99))+he,True,False)
case('private_recipient',field(3,scalar(1,1))+he,True,False)
case('conditional_recipient',field(3,scalar(1,3))+he,True,False)
case('undefined_filter',field(3,field(3,b'x'))+he,True,False)
case('follow_private',field(20,scalar(2,1)),True,False)
case('follow_taste_private',field(20,scalar(4,1)),True,False)
# A relation original is never publicly eligible (RELATIONS.md section 8). The
# body type alone decides, so the whole declared/revoked x order
# absent/present/present-but-empty matrix is structurally well formed -- it
# survives the generic codec, keeps its canonical bytes, CID and signature and
# is still admissible through a House's ordinary verified write entrance -- and
# publicly ineligible all the same. FollowDeclared.order is field 5,
# FollowRevoked.order is field 3; RelationOrder.seq is field 1.
for body_tag, order_tag, who in [(20,5,'declared'),(21,3,'revoked')]:
    case('follow_'+who+'_order_absent',field(body_tag,field(1,b'followee')),True,False)
    case('follow_'+who+'_order_empty',
         field(body_tag,field(1,b'followee')+field(order_tag,b'')),True,False)
    case('follow_'+who+'_order_present',
         field(body_tag,field(1,b'followee')+field(order_tag,scalar(1,7))),True,False)
    # Default-field bodies are the exact shape a public lane would have carried.
    case('follow_'+who+'_default_fields',field(body_tag,b''),True,False)
    # Exclusion by body type must not mask a genuine wire fault: an unknown
    # Follow field still fails the structural check, not the public one.
    case('follow_'+who+'_unknown_field',field(body_tag,field(99,b'')),False,False)
case('duplicate_scope',field(34,field(1,b'house.verb')+field(4,b'abcd')*2),True,False)
case('invalid_kind',field(34,field(1,b'bad')),True,False)
case('uint64_max',scalar(5,(1<<64)-1)+he,True,True)
case('profile_declared_at_negative',field(28,scalar(7,(1<<64)-1)),True,True)
# New wait fields are supported structure. Invalid enum values remain structurally
# readable but are not public; duplicates are ambiguous and structurally invalid.
case('invite_wait_request_mode_field8',field(11,field(1,b'x')+field(2,b'tester')+scalar(5,1)+scalar(8,1)),True,True)
case('invite_wait_cancel_field9',field(11,field(1,b'x')+field(2,b'tester')+scalar(8,1)+field(9,b'task-1')),True,True)
case('invite_wait_duplicate_mode',field(11,scalar(8,1)+scalar(8,1)),False,False)
case('invite_wait_duplicate_cancel_task',field(11,field(9,b'task-1')+field(9,b'task-2')),False,False)
case('invite_wait_unknown_mode',field(11,scalar(8,99)),True,False)
case('invite_wait_dispatch_unknown_mode',field(12,field(10,scalar(6,99))),True,False)
case('invite_wait_progress_unknown_enum',field(13,scalar(10,99)),True,False)
case('invite_wait_duplicate_progress',field(13,scalar(10,1)+scalar(10,2)),False,False)
case('invite_wait_duplicate_dispatch_mode',field(12,field(10,scalar(6,1)+scalar(6,1))),False,False)
case('invite_wait_duplicate_progress_revision',field(13,scalar(11,1)+scalar(11,2)),False,False)

seed = bytes(range(32))
key = Ed25519PrivateKey.from_private_bytes(seed)
pub = key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
Env = message_type('popclaw.event.EventEnvelope')
signed = []
for name in ['unknown_business_signed','profile_signed','optional_presence_signed','wide_integer_signed','map_order_signed','dm_signed']:
    env = Env()
    env.actor.popclaw_id = b58(pub)
    env.actor.nickname = 'Fixture'
    env.timestamp = 1750000000
    if name == 'profile_signed':
        env.profile.nickname = 'Fixture'
        env.profile.declared_at = 1750000000
    elif name == 'dm_signed':
        env.direct_message.body = 'encrypted fixture placeholder'
        env.direct_message.ciphertext = b'\0\xff\1'
        env.direct_message.nonce = bytes(range(24))
    elif name == 'map_order_signed':
        block = env.post.blocks.add()
        block.content = 'Map order'
        block.metadata.update({'__proto__':'prototype-key','constructor':'constructor-key','toString':'method-key','b':'2','a':'1','aa':'prefix','aaa':'long-prefix','':'empty-key','empty-value':'','10':'ten','2':'two','\ue000':'bmp','\U00010000':'astral'})
    else:
        env.house_event.kind = 'unknown-house.some_verb'
        env.house_event.body = b'\xea\1\0\xff\0'
        env.house_event.public_scopes.extend(['scopeB','scopeA'])
        if name == 'optional_presence_signed':
            env.actor.supersedes = ''
            env.actor.device_id = b''
            env.actor.role = 0
        if name == 'wide_integer_signed':
            env.timestamp = (1<<64)-1
    canonical = canonical_envelope(env)
    env.event_id = hashlib.sha256(canonical).hexdigest()
    env.signature = key.sign(canonical)
    raw = env.SerializeToString(deterministic=True)
    wrapper = message_type('popclaw.identity.SignedPayload')()
    wrapper.payload = raw
    wrapper.signer_pubkey = pub
    wrapper.signature = key.sign(raw)
    signed.append(dict(name=name,canonical_hex=canonical.hex(),cid=env.event_id,
                       wire_hex=raw.hex(),signature_hex=env.signature.hex(),
                       public_key_hex=pub.hex(),signer_seed_hex=seed.hex(),
                       signed_payload_hex=wrapper.SerializeToString(deterministic=True).hex()))

# Deterministic signed vectors pin all five new fields. The first matches the
# House invite_wait_test::signed_push_body helper exactly: seed [91; 32], actor
# nickname Someone, timestamp 1713657600, and the original x/tester request.
def finish_signed(name, env, signer_seed):
    signer = Ed25519PrivateKey.from_private_bytes(signer_seed)
    signer_pub = signer.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    canonical = canonical_envelope(env)
    env.event_id = hashlib.sha256(canonical).hexdigest()
    env.signature = signer.sign(canonical)
    raw = env.SerializeToString(deterministic=True)
    wrapper = message_type('popclaw.identity.SignedPayload')()
    wrapper.payload = raw
    wrapper.signer_pubkey = signer_pub
    wrapper.signature = signer.sign(raw)
    return dict(name=name, canonical_hex=canonical.hex(), cid=env.event_id,
                wire_hex=raw.hex(), signature_hex=env.signature.hex(),
                public_key_hex=signer_pub.hex(), signer_seed_hex=signer_seed.hex(),
                signed_payload_hex=wrapper.SerializeToString(deterministic=True).hex())

wait_seed = bytes([91]) * 32
wait_env = Env()
wait_pub = Ed25519PrivateKey.from_private_bytes(wait_seed).public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
wait_env.actor.popclaw_id = b58(wait_pub)
wait_env.actor.nickname = 'Someone'
wait_env.timestamp = 1713657600
wait_env.invite_request.platform = 'x'
wait_env.invite_request.handle = 'tester'
wait_env.invite_request.replace = True
wait_env.invite_request.verification_mode = 1
signed.append(finish_signed('invite_wait_request_house_helper', wait_env, wait_seed))

cancel_env = Env()
cancel_env.actor.popclaw_id = b58(wait_pub)
cancel_env.actor.nickname = 'Someone'
cancel_env.timestamp = 1713657601
cancel_env.invite_request.platform = 'x'
cancel_env.invite_request.handle = 'tester'
cancel_env.invite_request.verification_mode = 1
cancel_env.invite_request.cancel_task_id = '00000000-0000-4000-8000-000000000001'
signed.append(finish_signed('invite_wait_cancel_signed', cancel_env, wait_seed))

dispatch_env = Env()
dispatch_env.actor.popclaw_id = b58(wait_pub)
dispatch_env.actor.nickname = 'House'
dispatch_env.timestamp = 1713657602
dispatch_env.quest_dispatch.task_id = '00000000-0000-4000-8000-000000000001'
dispatch_env.quest_dispatch.kind = 1
dispatch_env.quest_dispatch.verify_invite.platform = 'x'
dispatch_env.quest_dispatch.verify_invite.handle = 'tester'
dispatch_env.quest_dispatch.verify_invite.applicant_popclaw_id = wait_pub
dispatch_env.quest_dispatch.verify_invite.expected_sigil = '837a8c00'
dispatch_env.quest_dispatch.verify_invite.verification_mode = 1
signed.append(finish_signed('invite_wait_dispatch_signed', dispatch_env, wait_seed))

progress_env = Env()
progress_env.actor.popclaw_id = b58(wait_pub)
progress_env.actor.nickname = 'Ranger'
progress_env.timestamp = 1713657603
progress_env.quest_result.task_id = '00000000-0000-4000-8000-000000000001'
progress_env.quest_result.verification_progress = 2
progress_env.quest_result.progress_revision = 1
signed.append(finish_signed('invite_wait_ready_progress_signed', progress_env, wait_seed))

manifest={'world_interaction':{'version':1,'public_stream':{'endpoint':'/v1/world-stream',
          'mode':'public-v1','log_incarnation':'log-fixture-1','initial_public_scopes':[],
          'envelope_baseline':'public-envelope-02'}}}
manifest_bytes=json.dumps(manifest,separators=(',',':')).encode()
proof=message_type('popclaw.world.ManifestProof')()
proof.house.origin='https://house.example'
proof.house.house_key=b58(pub)
proof.house.incarnation='server-fixture-1'
proof.manifest_digest=hashlib.sha256(manifest_bytes).hexdigest()
proof.signed_at=1750000000
proof_core=proof.SerializeToString(deterministic=True)
proof.authority_signature=key.sign(b'POPCLAW_WORLD_MANIFEST_PROOF_V1'+proof_core)
manifest_vector={'manifest_utf8':manifest_bytes.decode(),'digest':proof.manifest_digest,
                 'proof_hex':proof.SerializeToString(deterministic=True).hex(),
                 'public_key_hex':pub.hex(),'core_hex':proof_core.hex()}

actor=message_type('popclaw.identity.ActorInfo')()
actor.popclaw_id=b58(pub)
actor.nickname='Fixture'
reserved_core=field(2,actor.SerializeToString(deterministic=True))+scalar(5,1750000000)+field(28,field(1,b'Fixture')+field(8,b''))
reserved_cid=hashlib.sha256(reserved_core).hexdigest()
reserved_signature=key.sign(reserved_core)
reserved_wire=field(1,reserved_cid.encode())+reserved_core+field(6,reserved_signature)
reserved_signed={'canonical_hex':reserved_core.hex(),'cid':reserved_cid,
                 'wire_hex':reserved_wire.hex(),'signature_hex':reserved_signature.hex(),
                 'public_key_hex':pub.hex()}

out = ROOT/'packages/contracts/fixtures/public-baseline.json'
out.write_text(json.dumps({'baseline':'public-envelope-02','wire':rows,'signed':signed,'manifest':manifest_vector,'signed_reserved':reserved_signed},indent=2)+'\n')
print(f'Generated {len(rows)} wire and {len(signed)} signing vectors')
