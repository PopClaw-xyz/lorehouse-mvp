"""Original-byte structural/privacy checks. No identity or signature admission."""
from google.protobuf.descriptor import FieldDescriptor as F
from protocol import message_type

ENVELOPE_BASELINE = 'public-envelope-02'
# L_ENVELOPE_MAX_BYTES (LIMITS.md): the largest raw EventEnvelope a conforming reader must accept.
L_ENVELOPE_MAX_BYTES = 1572864


def check_envelope_wire(raw):
    if len(raw) > L_ENVELOPE_MAX_BYTES:
        raise ValueError('WIRE_LIMIT')
    budget = [65536]
    body = [0]

    def scan(data, ty, depth):
        if depth > 32:
            raise ValueError('WIRE_DEPTH')
        pos = 0
        seen = set()
        oneofs = set()

        def varint():
            nonlocal pos
            n = 0
            for i in range(10):
                if pos == len(data):
                    raise ValueError('WIRE_VARINT')
                b = data[pos]
                pos += 1
                if i == 9 and b > 1:
                    raise ValueError('WIRE_VARINT')
                n |= (b & 127) << (7*i)
                if not b & 128:
                    return n
            raise ValueError('WIRE_VARINT')

        while pos < len(data):
            budget[0] -= 1
            if budget[0] < 0:
                raise ValueError('WIRE_LIMIT')
            key = varint()
            tag, wire = key >> 3, key & 7
            if not 1 <= tag <= 536870911:
                raise ValueError('WIRE_TAG')
            if (ty.full_name == 'popclaw.event.EventEnvelope' and tag == 29 or
                    ty.full_name == 'popclaw.profile.Profile' and tag == 8):
                raise ValueError('RESERVED_OCCURRENCE')
            f = ty.fields_by_number.get(tag)
            if f is None:
                raise ValueError('UNSUPPORTED_FIELD')
            if not f.is_repeated and tag in seen:
                raise ValueError('DUPLICATE_FIELD')
            seen.add(tag)
            if f.containing_oneof is not None:
                group = f.containing_oneof.name
                if group in oneofs:
                    raise ValueError('MULTIPLE_ONEOF')
                oneofs.add(group)
                if ty.full_name == 'popclaw.event.EventEnvelope':
                    body[0] = tag
            expected = (2 if f.type in [F.TYPE_STRING, F.TYPE_BYTES, F.TYPE_MESSAGE] else
                        1 if f.type in [F.TYPE_FIXED64, F.TYPE_SFIXED64, F.TYPE_DOUBLE] else
                        5 if f.type in [F.TYPE_FIXED32, F.TYPE_SFIXED32, F.TYPE_FLOAT] else 0)
            if wire != expected:
                raise ValueError('WIRE_TYPE')
            if wire == 0:
                n = varint()
                if f.type in [F.TYPE_UINT32, F.TYPE_SINT32] and n > 0xffffffff:
                    raise ValueError('WIRE_RANGE')
                if f.type in [F.TYPE_INT32, F.TYPE_ENUM] and 0xffffffff < n < 0xffffffff80000000:
                    raise ValueError('WIRE_RANGE')
                continue
            length = varint() if wire == 2 else 8 if wire == 1 else 4
            if length > len(data) - pos:
                raise ValueError('WIRE_TRUNCATED')
            value = data[pos:pos+length]
            pos += length
            if f.type == F.TYPE_STRING:
                value.decode('utf-8', errors='strict')
            if f.type == F.TYPE_MESSAGE:
                scan(value, f.message_type, depth+1)
    scan(raw, message_type('popclaw.event.EventEnvelope').DESCRIPTOR, 0)
    if not body[0]:
        raise ValueError('MISSING_BODY')
    return body[0]


def check_public_envelope_structure(raw):
    """Additional public privacy filter; callers still verify signatures/identity/body.

    Tags 20/21 (FollowDeclared/FollowRevoked) are absent from the public set: a
    relation original is owed to its two participants' personal streams and is
    never a public fact, whether `order` is absent, present or present-but-empty
    (RELATIONS.md section 8). The body type alone decides, so the follow privacy
    fields are no longer consulted here - they cannot readmit what the tag has
    already excluded. This remains a public-eligibility test only: relation
    originals still pass check_envelope_wire, keep their canonical bytes, CID and
    author signature, and are still admitted through a House's ordinary verified
    write entrance and delivered personally.
    """
    import re
    tag = check_envelope_wire(raw)
    if tag not in [11, 12, 13, 14, 15, 16, 18, 25, 27, 28, 33, 34]:
        raise ValueError('NOT_PUBLIC')
    env = message_type('popclaw.event.EventEnvelope').FromString(raw)
    if env.HasField('target'):
        t = env.target
        if t.scope not in [0, 2] or t.filter_criteria:
            raise ValueError('NOT_PUBLIC')
        if t.scope == 0 and t.target_ids or t.scope == 2 and not t.target_ids:
            raise ValueError('INVALID_TARGET')
    if env.HasField('invite_request') and env.invite_request.verification_mode not in (0, 1):
        raise ValueError('INVALID_ENUM')
    if env.HasField('quest_dispatch') and env.quest_dispatch.HasField('verify_invite') and env.quest_dispatch.verify_invite.verification_mode not in (0, 1):
        raise ValueError('INVALID_ENUM')
    if env.HasField('quest_result') and env.quest_result.verification_progress not in (0, 1, 2, 3):
        raise ValueError('INVALID_ENUM')
    if env.HasField('house_event'):
        h = env.house_event
        if len(h.kind) > 128 or re.fullmatch(r'[a-z0-9-]+\.[a-z0-9_]+', h.kind, flags=re.ASCII) is None:
            raise ValueError('INVALID_KIND')
        if (len(h.public_scopes) > 32 or len(set(h.public_scopes)) != len(h.public_scopes) or
                any(re.fullmatch(r'[A-Za-z0-9_-]{4,64}', s, flags=re.ASCII) is None for s in h.public_scopes)):
            raise ValueError('INVALID_SCOPES')
    return tag
