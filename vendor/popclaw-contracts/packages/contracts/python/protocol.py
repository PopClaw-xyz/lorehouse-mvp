"""Fixed-descriptor consumption helpers, not a server or complete client SDK."""
from pathlib import Path
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

PROTO_ROOT = Path(__file__).resolve().parent.parent / 'proto'
_pool = descriptor_pool.DescriptorPool()
_set = descriptor_pb2.FileDescriptorSet.FromString((PROTO_ROOT / 'descriptor.pb').read_bytes())
_pending = list(_set.file)
while _pending:
    remaining = []
    for file in _pending:
        try:
            _pool.Add(file)
        except TypeError:
            remaining.append(file)
    if len(remaining) == len(_pending):
        raise ValueError('Incomplete descriptor import closure')
    _pending = remaining


def message_type(name):
    """Resolve only the pinned protocol's fully qualified message name."""
    return message_factory.GetMessageClass(_pool.FindMessageTypeByName(name))


def canonical_envelope(message):
    """Return signed core bytes; never use this to repair an unsupported wire input."""
    copy = message_type('popclaw.event.EventEnvelope')()
    copy.CopyFrom(message)
    copy.ClearField('event_id')
    copy.ClearField('signature')
    return _ordered_message(copy.SerializeToString(deterministic=True), copy.DESCRIPTOR)


def signing_input(domain, canonical):
    return domain.encode('utf-8') + canonical


def _varint(value):
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return bytes(out)


def _ordered_message(raw, descriptor):
    """Keep protobuf scalar/presence encoding, reorder string maps by UTF-8.

    Python deterministic serialization orders prefix keys differently from Rust.
    Walk only locally serialized known messages; this is not an ingress validator.
    """
    pos = 0
    chunks = []

    def read_varint():
        nonlocal pos
        value, shift = 0, 0
        while True:
            byte = raw[pos]
            pos += 1
            value |= (byte & 127) << shift
            if not byte & 128:
                return value
            shift += 7

    while pos < len(raw):
        start = pos
        key = read_varint()
        tag, wire = key >> 3, key & 7
        field = descriptor.fields_by_number.get(tag)
        order = None
        if wire == 0:
            read_varint()
        elif wire in (1, 5):
            pos += 8 if wire == 1 else 4
        elif wire == 2:
            size = read_varint()
            value = raw[pos:pos+size]
            pos += size
            if descriptor.GetOptions().map_entry and not value:
                continue  # prost omits empty string map keys/values, retaining the entry
            if field is not None and field.message_type is not None:
                ty = field.message_type
                value = _ordered_message(value, ty)
                if ty.GetOptions().map_entry:
                    entry = message_factory.GetMessageClass(ty).FromString(value)
                    if not isinstance(entry.key, str):
                        raise ValueError('Canonical map requires string keys')
                    order = entry.key.encode('utf-8')
                chunks.append((tag, order, _varint(key)+_varint(len(value))+value))
                continue
        else:
            raise ValueError('Unsupported canonical wire type')
        chunks.append((tag, order, raw[start:pos]))
    # Stable sorting preserves order of repeated non-map values.
    chunks.sort(key=lambda item: (item[0], item[1] if item[1] is not None else b''))
    return b''.join(item[2] for item in chunks)
