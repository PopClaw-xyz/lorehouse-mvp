#!/usr/bin/env python3
"""Deterministic, reviewed postprocessing of pbjs output; never hand-edit output."""
from pathlib import Path
p = Path('packages/contracts/ts/contracts/src/generated/index.js')
s = p.read_text().replace('import * as $protobuf from "protobufjs/minimal";',
                         'import $protobuf from "protobufjs/minimal.js";')
s = s.replace('import $protobuf from "protobufjs/minimal";',
              'import $protobuf from "protobufjs/minimal.js";')
needle = 'Object.keys(message.metadata)'
assert s.count(needle) >= 1, 'expected metadata map encoder'
s = s.replace(needle, needle + '.sort($compareUtf8)')
map_encoder = 'writer.uint32(/* id 3, wireType 2 =*/26).fork().uint32(/* id 1, wireType 2 =*/10).string(keys[i]).uint32(/* id 2, wireType 2 =*/18).string(message.metadata[keys[i]]).ldelim();'
assert s.count(map_encoder) == 1, 'expected one string map encoder'
s = s.replace(map_encoder, """{
                            writer.uint32(26).fork();
                            if (keys[i] !== '') writer.uint32(10).string(keys[i]);
                            if (message.metadata[keys[i]] !== '') writer.uint32(18).string(message.metadata[keys[i]]);
                            writer.ldelim();
                        }""")
s += '''
// Deterministic UTF-8 map order, matching the Rust BTreeMap canonical encoder.
// Sorting the key array also handles integer-like keys that object insertion
// order cannot sort lexically. This is generation-time postprocessing.
function $compareUtf8(a, b) {
    const encoder = new TextEncoder();
    const left = encoder.encode(a), right = encoder.encode(b);
    for (let i = 0; i < Math.min(left.length, right.length); i++) {
        if (left[i] !== right[i]) return left[i] - right[i];
    }
    return left.length - right.length;
}
'''
p.write_text(s)
