"""Fixed client public02 receiver, fresh reference/identity and random loopback port.

No host installation, old data, external House or CI. Client checkout is read-only.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
import uvicorn
from ranger_map import wire
from ranger_map.app import create_app
from ranger_map.house import load_or_setup
from ranger_map.keys import load_or_create_identity
from ranger_map.store import Store
from ranger_map.streams import StreamHub
from tests.interop.profile_http_loop import git, require
from tests.interop.wire_helpers import Actor, make_post, wrap_signed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-root', type=Path, required=True)
    parser.add_argument('--expected-client-sha', required=True)
    parser.add_argument('--expected-reference-sha', required=True)
    parser.add_argument('--node', required=True)
    parser.add_argument('--development-dirty', action='store_true')
    args = parser.parse_args()
    client = args.client_root.resolve()
    require(git(client, 'rev-parse', 'HEAD') == args.expected_client_sha, 'client HEAD mismatch')
    require(git(ROOT, 'rev-parse', 'HEAD') == args.expected_reference_sha, 'reference HEAD mismatch')
    require(not git(client, 'status', '--porcelain'), 'client must be clean')
    require(args.development_dirty or not git(ROOT, 'status', '--porcelain'), 'reference must be fixed')
    pkg = client / 'apps/popclaw-plugin'
    with tempfile.TemporaryDirectory(prefix='reference-public02-loop-') as temporary:
        temp = Path(temporary)
        sock = socket.socket(); sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        require(port not in (8113, 19863), 'reserved integration port')
        origin = f'http://127.0.0.1:{port}'
        store = Store.open(temp / 'house'); identity = load_or_create_identity(temp / 'house')
        state = load_or_setup(store, identity, origin)
        server = uvicorn.Server(uvicorn.Config(create_app(store, identity=identity, house_state=state, hub=StreamHub(store)),
            log_level='error', lifespan='off'))
        thread = threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True); thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started and time.monotonic() < deadline: time.sleep(.025)
            require(server.started, 'temporary House startup failed')
            actor = Actor('Synthetic public02 pairing')
            replay = make_post(actor, 'Synthetic replay evidence')
            from ranger_map.ingress import handle_push
            result = handle_push(store, identity, state, wrap_signed(replay, actor))
            require(result.public and result.http_status == 200, 'fixture replay admission')
            live = make_post(actor, 'Synthetic live evidence')
            payload = dict(clientRoot=str(client), origin=origin, ackKeyHex=identity.ack_pubkey_hex,
                log=state.log_incarnation, database=str(temp / 'execution.db'), replayHex=replay.hex(),
                liveHex=live.hex(), liveCid=wire.envelope_cid(live), liveWrapperHex=wrap_signed(live, actor).hex())
            config = temp / 'input.json'; config.write_text(json.dumps(payload))
            (temp / 'home').mkdir()
            output = subprocess.run([args.node, '--import', str(pkg / 'node_modules/tsx/dist/loader.mjs'),
                str(ROOT / 'tests/interop/public02_client_loop.mjs'), str(config)], cwd=pkg,
                env={'PATH': os.environ.get('PATH', ''), 'HOME': str(temp / 'home'), 'TMPDIR': str(temp),
                     'LANG': 'en_US.UTF-8', 'POPCLAW_DATA_ROOT': str(temp / 'client')},
                capture_output=True, text=True, timeout=60)
            require(output.returncode == 0, output.stderr + output.stdout)
            report = json.loads(output.stdout)
            require(store.public_log_high_water(state.log_incarnation) == 2, 'duplicate fabricated public sequence')
            report.update(referenceSha=args.expected_reference_sha, clientSha=args.expected_client_sha,
                fixedJointCandidate=not args.development_dirty, sourcePublicRows=2,
                temporaryIdentity=True, loopbackOnly=True)
            print(json.dumps(report, indent=2))
        finally:
            server.should_exit = True; thread.join(timeout=5); store.close(); sock.close()


if __name__ == '__main__': main()
