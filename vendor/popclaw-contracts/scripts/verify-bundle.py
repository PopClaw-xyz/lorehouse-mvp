#!/usr/bin/env python3
"""Check the exact source set; --expected adds the caller's trusted digest pin."""
import argparse
import hashlib
import json
import re
from pathlib import PurePosixPath
from bundle_files import ROOT,paths,digest
p=argparse.ArgumentParser();p.add_argument('--expected');args=p.parse_args()
m=json.loads((ROOT/'CONTRACT-MANIFEST.json').read_text())
rows=m['files'];names=[r['path'] for r in rows]
if names!=sorted(set(names)):raise SystemExit('Unsorted/duplicate manifest path')
for r in rows:
    name=PurePosixPath(r['path'])
    if name.is_absolute() or '..' in name.parts or '\\' in r['path'] or str(name)!=r['path']:
        raise SystemExit('Unsafe manifest path')
    if not re.fullmatch('[0-9a-f]{64}',r['sha256']):raise SystemExit('Invalid file digest')
actual=digest(rows)
if m['bundle_sha256']!=actual:raise SystemExit('Manifest digest mismatch')
if args.expected and args.expected!=actual:raise SystemExit('Trusted digest mismatch')
if paths()!=names:raise SystemExit('Source membership mismatch')
for r in rows:
    if hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()!=r['sha256']:
        raise SystemExit('Changed file: '+r['path'])
print(f'Verified {len(rows)} source files; bundle {actual}'+(' (trusted pin matched)' if args.expected else ' (integrity only; no external trust pin supplied)'))
