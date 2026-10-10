"""Re-runnable real MCP / reference-house loop, using only temporary identities.

Run with the reference server's Python environment. The client checkout is
read-only; installed client dependencies must already exist. No package build,
installation, daemon or production data is involved. See protocol-bindings.md.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]

import uvicorn
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from ranger_map import wire
from ranger_map.app import create_app
from ranger_map.house import load_or_setup
from ranger_map.keys import load_or_create_identity
from ranger_map.store import Store
from ranger_map.streams import StreamHub
from tests.interop.wire_helpers import Actor, build_envelope, signed_envelope_bytes, wrap_signed


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


class Recorder:
    def __init__(self, app):
        self.app, self.requests, self.posts = app, [], []

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        at = time.monotonic()
        method, path = scope['method'], scope['path']
        self.requests.append(dict(at=at, method=method, path=path))
        chunks, status = [], 0
        async def reading():
            event = await receive()
            if path == '/v1/push' and event['type'] == 'http.request':
                chunks.append(event.get('body', b''))
            return event
        async def sending(event):
            nonlocal status
            if event['type'] == 'http.response.start':
                status = event['status']
            await send(event)
        await self.app(scope, reading, sending)
        if path == '/v1/push' and chunks:
            envelope = wire.EventEnvelope.FromString(
                wire.SignedPayload.FromString(b''.join(chunks)).payload)
            if envelope.WhichOneof('body') == 'profile':
                self.posts.append(dict(at=at, status=status,
                                       nickname=envelope.profile.nickname,
                                       event_id=envelope.event_id))


class Mcp:
    def __init__(self, process):
        self.process, self.responses, self.next_id = process, queue.Queue(), 0
        def reading():
            for line in process.stdout:
                try:
                    self.responses.put(json.loads(line))
                except ValueError:
                    self.responses.put(dict(error='non-JSON MCP stdout'))
            self.responses.put(dict(error='MCP exited'))
        threading.Thread(target=reading, daemon=True).start()

    def request(self, method, params):
        self.next_id += 1
        self.process.stdin.write(json.dumps(dict(jsonrpc='2.0', id=self.next_id,
                                                method=method, params=params)) + '\n')
        self.process.stdin.flush()
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            response = self.responses.get(timeout=max(.01, deadline - time.monotonic()))
            if response.get('id') == self.next_id:
                require('error' not in response, f'MCP error: {response}')
                return response['result']
            require('error' not in response, str(response))
        raise TimeoutError(method)

    def call(self, name, arguments=None):
        return self.request('tools/call', dict(name=name, arguments=arguments or {}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-root', type=Path, required=True)
    parser.add_argument('--expected-client-sha', required=True)
    parser.add_argument('--node', default=shutil.which('node'))
    parser.add_argument('--allow-dirty', action='store_true',
                        help='Development probe only; never claim a fixed joint candidate')
    args = parser.parse_args()
    client = args.client_root.resolve()
    pkg = client / 'apps/popclaw-plugin'
    sha = git(client, 'rev-parse', 'HEAD')
    require(sha == args.expected_client_sha, 'client HEAD differs from the supplied full SHA')
    client_dirty, reference_dirty = git(client, 'status', '--porcelain'), git(ROOT, 'status', '--porcelain')
    require(args.allow_dirty or not (client_dirty or reference_dirty),
            'joint run requires clean fixed trees; use --allow-dirty only for development')
    require(args.node and (pkg / 'node_modules/tsx').exists(), 'existing Node/tsx dependencies required')
    report = dict(reference_sha=git(ROOT, 'rev-parse', 'HEAD'), client_sha=sha,
                  client_dirty=bool(client_dirty), reference_dirty=bool(reference_dirty),
                  fixed_joint_candidate=not (client_dirty or reference_dirty),
                  node=subprocess.check_output([args.node, '--version'], text=True).strip())
    process = None
    server = None
    store = None
    thread = None
    with tempfile.TemporaryDirectory(prefix='profile-http-loop-') as temporary:
        temp = Path(temporary)
        try:
            sock = socket.socket()
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
            require(port != 8113, 'reserved production port refused')
            origin = f'http://127.0.0.1:{port}'
            store = Store.open(temp / 'house')
            identity = load_or_create_identity(temp / 'house')
            state = load_or_setup(store, identity, origin)
            recorder = Recorder(create_app(store, identity=identity, house_state=state,
                                           hub=StreamHub(store)))
            server = uvicorn.Server(uvicorn.Config(recorder, log_level='error', lifespan='off'))
            thread = threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True)
            thread.start()
            deadline = time.monotonic() + 10
            while not server.started and time.monotonic() < deadline:
                time.sleep(.02)
            require(server.started, 'temporary loopback server failed to start')
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            actor = Actor()
            data = temp / 'client'
            (data / 'config/cadence').mkdir(parents=True)
            (data / 'vault/social/identity').mkdir(parents=True)
            (temp / 'home').mkdir()
            key_path = data / 'vault/social/identity/master.key'
            key_path.write_text(json.dumps(dict(version=1, type='master-raw-seed',
                created_at='2026-10-01T00:00:00Z', public_key=actor.popclaw_id,
                seed=actor.private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()).hex())))
            key_path.chmod(0o600)
            # Current first-release clients require a complete fresh storage
            # profile. This helper preserves the synthetic fixture identity;
            # it initializes only this new temporary root, never old data.
            subprocess.run([args.node, '--import', str(pkg / 'node_modules/tsx/dist/loader.mjs'),
                str(ROOT / 'tests/interop/initialize_client_fixture.mjs'), str(client), str(data)],
                cwd=pkg, check=True, capture_output=True, text=True,
                env=dict(PATH=os.environ.get('PATH', ''), HOME=str(temp / 'home'), TMPDIR=str(temp),
                         LANG='en_US.UTF-8', POPCLAW_DATA_ROOT=str(data)))
            (data / 'config/plugin.json').write_text(json.dumps(dict(lore_houses=[origin])))
            (data / 'config/cadence/cadence.json').write_text(json.dumps(
                dict(schemaVersion=1, delivery=dict(primaryLanguage='en'))))
            attempts = temp / 'non-loopback-attempts'
            guard = temp / 'loopback-only.mjs'
            guard.write_text("""import net from 'node:net'; import dns from 'node:dns';
import {appendFileSync} from 'node:fs';
const LOOP = new Set(['127.0.0.1', 'localhost', '::1']);
const deny = h => { appendFileSync(ATTEMPTS, h+'\\n'); throw Error('non-loopback refused: '+h); };
const connect = net.Socket.prototype.connect;
net.Socket.prototype.connect = function (...args) {
 const a = Array.isArray(args[0]) ? args[0][0] : args[0];
 if ((typeof a === 'string' && a.startsWith('/')) || typeof a?.path === 'string') return connect.apply(this,args);
 const h = typeof a === 'object' ? (a.host ?? 'localhost') : (typeof args[1] === 'string' ? args[1] : 'localhost');
 if (!LOOP.has(h)) return deny(h);
 return connect.apply(this,args);
};
const lookup = dns.lookup;
dns.lookup = function(h,...args) { if (!LOOP.has(h)) return deny('dns:'+h); return lookup.call(this,h,...args); };
""".replace('ATTEMPTS', json.dumps(str(attempts))))
            log = open(temp / 'mcp-stderr.log', 'w+')
            process = subprocess.Popen([args.node, '--import', str(guard), '--import', 'tsx',
                                        str(pkg / 'src/mcp.ts')], cwd=pkg, text=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log,
                env=dict(PATH=os.environ.get('PATH', ''), HOME=str(temp / 'home'), TMPDIR=str(temp),
                         LANG='en_US.UTF-8', POPCLAW_LANG='en', POPCLAW_DATA_ROOT=str(data),
                         POPCLAW_CANVAS_BASE_URL=origin, POPCLAW_WEB_BASE_URL=origin))
            mcp = Mcp(process)
            init = mcp.request('initialize', dict(protocolVersion='2025-06-18', capabilities={},
                              clientInfo=dict(name='reference-profile-loop', version='1')))
            require(init.get('serverInfo', {}).get('name') == 'popclaw', 'wrong MCP server')
            process.stdin.write(json.dumps(dict(jsonrpc='2.0', method='notifications/initialized')) + '\n')
            process.stdin.flush()
            mcp.call('popclaw_check_status')
            report['login'] = mcp.call('popclaw_house_login', dict(host=origin))
            # Quiet background boot/login work before each command attribution.
            def quiet():
                last = len(recorder.requests)
                for _ in range(20):
                    time.sleep(.5)
                    now = len(recorder.requests)
                    if now == last:
                        return
                    last = now
                raise AssertionError('temporary house never became quiet')
            def read():
                with opener.open(origin + '/v1/profile/' + actor.popclaw_id, timeout=5) as r:
                    return json.load(r)
            quiet()
            require('card' not in read(), 'no-card initial state expected')
            report['commands'] = []
            for name in ['Mira', 'Nova']:
                quiet()
                start = time.monotonic()
                result = mcp.call('popclaw_set_name', dict(nickname=name))
                end = time.monotonic()
                time.sleep(.5)
                posts = [p for p in recorder.posts if p['nickname'] == name and start <= p['at'] <= end]
                gets = [r for r in recorder.requests if r['method'] == 'GET'
                        and r['path'] == '/v1/profile/' + actor.popclaw_id and start <= r['at'] <= end]
                body = read()
                require(len(posts) == 1 and posts[0]['status'] == 200, f'{name}: expected one accepted command Profile, got {posts}; result={result}')
                require(gets and gets[0]['at'] <= posts[0]['at'], f'{name}: no pre-write GET')
                require(body['card']['nickname'] == name, f'{name}: projection did not update')
                row = store.query_one('SELECT declared_at FROM profiles WHERE ranger_id = ?', (actor.popclaw_id,))
                require(body['card']['declared_at_ms'] == row['declared_at'] * 1000, 'incorrect ms translation')
                report['commands'].append(dict(name=name, accepted_profiles=1,
                                              pre_write_get=True, response=result, projection=body))
            # Seed protected cards through real signed ingress, explicitly a
            # fixture setup rather than a client command acceptance claim.
            for field, value in [('one_line_intro', 'first card'), ('avatar_uri', 'https://example.invalid/avatar.png')]:
                old = read()['card']
                def setter(e):
                    e.profile.nickname = 'Protected'
                    e.profile.declared_at = old['declared_at_ms'] // 1000 + 10
                    setattr(e.profile, field, value)
                raw = signed_envelope_bytes(build_envelope(actor, setter), actor)
                with opener.open(urllib.request.Request(origin + '/v1/push', data=wrap_signed(raw, actor)), timeout=5) as r:
                    require(r.status == 200, 'protected fixture admission failed')
                quiet()
                before = read()
                profile_count = store.query_one('SELECT COUNT(*) AS c FROM accepted_envelopes WHERE body_tag = 28')['c']
                stored_before = dict(store.query_one(
                    'SELECT card_json, declared_at, event_id FROM profiles WHERE ranger_id = ?',
                    (actor.popclaw_id,)))
                start = time.monotonic()
                result = mcp.call('popclaw_set_name', dict(nickname='Blocked' + field))
                end = time.monotonic()
                time.sleep(1)
                after = read()
                gets = [r for r in recorder.requests if r['method'] == 'GET'
                        and r['path'] == '/v1/profile/' + actor.popclaw_id and start <= r['at'] <= end]
                require(gets, f'{field}: no command-time pre-write GET')
                require(before == after, f'{field}: protected card changed')
                stored_after = dict(store.query_one(
                    'SELECT card_json, declared_at, event_id FROM profiles WHERE ranger_id = ?',
                    (actor.popclaw_id,)))
                require(stored_before == stored_after, f'{field}: stored row changed')
                require(store.query_one('SELECT COUNT(*) AS c FROM accepted_envelopes WHERE body_tag = 28')['c'] == profile_count,
                        f'{field}: issued a new Profile')
                require(not [p for p in recorder.posts if p['at'] >= start], f'{field}: unexpected Profile POST')
                require(field in json.dumps(result), f'{field}: command did not report protection')
                report['commands'].append(dict(protected_field=field, accepted_profiles=0,
                                              profile_posts=0, pre_write_get=True,
                                              preserved=True, response=result,
                                              before=before, after=after,
                                              stored_before=stored_before, stored_after=stored_after))
            # Deliberately bypass the client guard to establish the old
            # whole-row loss mechanism through real HTTP ingress. This probe
            # is NOT a user-chain acceptance test and changes no ingress code.
            report['direct_ingress_probe'] = dict(bypasses_client_guard=True, cases=[])
            protected = read()
            seconds = protected['card']['declared_at_ms'] // 1000
            for label, declared in [('older_no_overwrite', seconds - 1),
                                    ('newer_whole_row_clear', seconds + 1)]:
                before = read()
                stored_before = dict(store.query_one(
                    'SELECT card_json, declared_at, event_id FROM profiles WHERE ranger_id = ?',
                    (actor.popclaw_id,)))
                def setter(e):
                    e.profile.nickname = 'DirectProbe'
                    e.profile.declared_at = declared
                raw = signed_envelope_bytes(build_envelope(actor, setter), actor)
                wrapped = wrap_signed(raw, actor)
                with opener.open(urllib.request.Request(origin + '/v1/push', data=wrapped), timeout=5) as r:
                    response = json.load(r)
                    require(r.status == 200, 'direct probe ingress rejected')
                after = read()
                if label == 'older_no_overwrite':
                    require(before == after, 'older declaration unexpectedly overwrote protected card')
                else:
                    require(after['card']['avatar_uri'] == '' and after['card']['nickname'] == 'DirectProbe',
                            'newer whole-row declaration did not demonstrate field loss')
                report['direct_ingress_probe']['cases'].append(dict(
                    label=label, declared_at=declared, before=before, after=after,
                    stored_before=stored_before, stored_after=dict(store.query_one(
                        'SELECT card_json, declared_at, event_id FROM profiles WHERE ranger_id = ?',
                        (actor.popclaw_id,))),
                    response=response, envelope_sha256=hashlib.sha256(raw).hexdigest(),
                    signed_payload_base64=base64.b64encode(wrapped).decode('ascii')))
            require(not attempts.exists(), 'client attempted non-loopback networking')
            report['non_loopback_attempts'] = []
            print(json.dumps(report, ensure_ascii=False, indent=2))
        except Exception:
            if process is not None:
                log.flush()
                log.seek(0)
                print(log.read()[-6000:], file=sys.stderr)
            raise
        finally:
            if process is not None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                log.close()
            if server is not None:
                server.should_exit = True
                if thread is not None:
                    thread.join(timeout=5)
            if store is not None:
                store.close()


if __name__ == '__main__':
    main()
