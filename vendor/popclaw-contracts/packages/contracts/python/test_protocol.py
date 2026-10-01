import hashlib
import json
from pathlib import Path
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from protocol import message_type, canonical_envelope
from public_baseline import check_envelope_wire, check_public_envelope_structure

FIXTURES = Path(__file__).resolve().parent.parent / 'fixtures'
NEW = json.loads((FIXTURES / 'public-baseline.json').read_text())
OLD = json.loads((FIXTURES / 'test-vectors.json').read_text())


class ProtocolParity(unittest.TestCase):
    def test_prefix_map_and_defaults(self):
        env = message_type('popclaw.event.EventEnvelope')()
        block = env.post.blocks.add()
        block.block_type = 0
        block.content = ''
        self.assertEqual(canonical_envelope(env).hex(), 'da01020a00')
        block.metadata.update({'': '', 'a': '1', 'aa': '2'})
        self.assertEqual(canonical_envelope(env).hex(),
                         'da01150a131a001a060a01611201311a070a026161120132')

    def test_wire_matrix(self):
        for row in NEW['wire']:
            for check, key in [(check_envelope_wire,'structural'), (check_public_envelope_structure,'public')]:
                with self.subTest(name=row['name'],check=key):
                    raw = bytes.fromhex(row['wire_hex'])
                    if row[key]:
                        check(raw)
                    else:
                        with self.assertRaises(ValueError):
                            check(raw)

    def test_signed_envelope_and_wrapper(self):
        for row in NEW['signed']:
            with self.subTest(name=row['name']):
                raw = bytes.fromhex(row['wire_hex'])
                check_envelope_wire(raw)
                env = message_type('popclaw.event.EventEnvelope').FromString(raw)
                canonical = canonical_envelope(env)
                self.assertEqual(canonical.hex(),row['canonical_hex'])
                self.assertEqual(hashlib.sha256(canonical).hexdigest(),row['cid'])
                key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(row['public_key_hex']))
                key.verify(env.signature, canonical)
                tampered = canonical[:-1] + bytes([canonical[-1]^1])
                with self.assertRaises(InvalidSignature):
                    key.verify(env.signature,tampered)
                wrapper = message_type('popclaw.identity.SignedPayload').FromString(bytes.fromhex(row['signed_payload_hex']))
                self.assertEqual(wrapper.payload,raw)
                self.assertEqual(wrapper.signer_pubkey.hex(),row['public_key_hex'])
                key.verify(wrapper.signature,wrapper.payload)

    def test_retained_29_codec_vectors(self):
        for row in OLD['canonical_serialization']:
            with self.subTest(name=row['name']):
                raw = bytes.fromhex(row['canonical_bytes_hex'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['cid'])
                if row['name'] == 'verified_platform_with_account_id':
                    msg = message_type('popclaw.event.VerifiedPlatform').FromString(raw)
                    encoded = msg.SerializeToString(deterministic=True)
                else:
                    check_envelope_wire(raw)
                    encoded = canonical_envelope(message_type('popclaw.event.EventEnvelope').FromString(raw))
                self.assertEqual(encoded,raw)

    def test_session_request_ack_bytes_and_signatures(self):
        session = OLD['house_session']
        for group in ['requests','acks']:
            for row in session[group]:
                with self.subTest(group=group,name=row['name']):
                    raw=bytes.fromhex(row['canonical_bytes_hex'])
                    ty='RequestCore' if group=='requests' else 'AckCore'
                    obj=message_type('popclaw.housesession.'+ty).FromString(raw)
                    self.assertEqual(obj.SerializeToString(deterministic=True),raw)
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),row['cid'])
                    key=Ed25519PublicKey.from_public_bytes(bytes.fromhex(row['signer_pubkey_hex']))
                    signed=bytes.fromhex(row['signing_input_hex'])
                    domain=b'POPCLAW_HOUSE_SESSION_REQUEST_V1' if group=='requests' else b'POPCLAW_HOUSE_SESSION_ACK_V1'
                    self.assertEqual(signed,domain+raw)
                    key.verify(bytes.fromhex(row['signature_hex']),signed)

    def test_retained_world_signing_rules(self):
        golden=json.loads((FIXTURES/'retained-signing-golden.json').read_text())
        for row in golden['vectors']:
            with self.subTest(type=row['type']):
                raw=bytes.fromhex(row['signed_core_bytes_hex'])
                msg=message_type('popclaw.world.'+row['type']).FromString(raw)
                self.assertEqual(msg.SerializeToString(deterministic=True),raw)
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
                key=Ed25519PublicKey.from_public_bytes(bytes.fromhex(row['signer_public_key_hex']))
                sig=bytes.fromhex(row['signature_hex'])
                key.verify(sig,row['domain'].encode()+raw)
                with self.assertRaises(InvalidSignature):
                    key.verify(sig,(row['domain']+'X').encode()+raw)

    def test_reserved_crypto_valid_and_stripping_is_not_repair(self):
        row=NEW['signed_reserved']
        key=Ed25519PublicKey.from_public_bytes(bytes.fromhex(row['public_key_hex']))
        sig=bytes.fromhex(row['signature_hex'])
        core=bytes.fromhex(row['canonical_hex']);raw=bytes.fromhex(row['wire_hex'])
        key.verify(sig,core)
        with self.assertRaisesRegex(ValueError,'RESERVED_OCCURRENCE'):
            check_envelope_wire(raw)
        decoded=message_type('popclaw.event.EventEnvelope').FromString(raw)
        # Python preserves unknown fields; explicit discard here demonstrates the
        # lossy-decoder hazard. The production guard runs BEFORE any such decode.
        decoded.DiscardUnknownFields()
        stripped=canonical_envelope(decoded)
        self.assertNotEqual(hashlib.sha256(stripped).hexdigest(),row['cid'])
        with self.assertRaises(InvalidSignature): key.verify(sig,stripped)

if __name__ == '__main__':
    unittest.main(verbosity=2)
