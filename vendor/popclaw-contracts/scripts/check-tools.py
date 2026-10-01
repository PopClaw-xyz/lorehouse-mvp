#!/usr/bin/env python3
"""Fail generation on an unexpected compiler instead of silently changing outputs."""
import json
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parent.parent
x=json.loads((r/'TOOLCHAIN.json').read_text())
actual=subprocess.check_output(['protoc','--version'],text=True).strip()
if actual!='libprotoc '+x['generation']['protoc']:
    raise SystemExit(f'Expected protoc {x["generation"]["protoc"]}; found {actual}')
for package, expected in [('protobufjs-cli',x['generation']['protobufjs_cli']),('protobufjs',x['generation']['protobufjs'])]:
    script=f'console.log(require("{package}/package.json").version)'
    cwd=r if package=='protobufjs-cli' else r/'packages/contracts/ts/contracts'
    actual=subprocess.check_output(['node','-e',script],cwd=cwd,text=True).strip()
    if actual!=expected:raise SystemExit(f'Expected {package} {expected}; found {actual}')
print('Pinned code generation tools verified')
