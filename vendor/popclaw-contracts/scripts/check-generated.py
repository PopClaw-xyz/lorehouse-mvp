#!/usr/bin/env python3
"""Check regenerated outputs against a pre-run byte snapshot; works without Git."""
import hashlib
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent.parent

def snapshot():
    paths=list((ROOT/'packages/contracts/ts/contracts/src/generated').glob('*'))
    paths+=list((ROOT/'packages/contracts/crates/rust/src/generated').glob('*'))
    paths += [ROOT/'packages/contracts/proto/descriptor.pb',
              ROOT/'packages/contracts/fixtures/test-vectors.json',
              ROOT/'packages/contracts/fixtures/public-baseline.json']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}

before=snapshot()
subprocess.run(['bash','scripts/gen-proto.sh'],cwd=ROOT,check=True)
subprocess.run(['cargo','run','--locked','-p','popclaw-algorithms','--bin','gen-fixtures'],cwd=ROOT,check=True)
python=ROOT/'.venv/bin/python'
subprocess.run([str(python) if python.exists() else sys.executable,'scripts/gen-baseline-fixtures.py'],cwd=ROOT,check=True)
after=snapshot()
changed=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
if changed:
    print('Generated drift:\n'+'\n'.join(changed),file=sys.stderr)
    sys.exit(1)
print(f'No generated drift in {len(after)} outputs')
