"""Real installed MCP wire, fresh temporary House and identity, loopback only.

No builds, installation or owner data. A synthetic peer's Profile is fixture
setup through signed ingress; follow/unfollow and the DM preview use native
tools. The preview is never sent or treated as approval-chain acceptance.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'src')]

import uvicorn
from ranger_map import wire
from ranger_map.app import create_app
from ranger_map.house import load_or_setup
from ranger_map.keys import load_or_create_identity
from ranger_map.store import Store
from ranger_map.streams import StreamHub
from tests.interop.profile_http_loop import Mcp, require
from tests.interop.wire_helpers import Actor, make_profile, wrap_signed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--bundle-sha256', required=True)
    parser.add_argument('--node', required=True)
    parser.add_argument('--expected-reference-sha', required=True)
    parser.add_argument('--development-dirty', action='store_true')
    args = parser.parse_args()
    reference = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'], text=True).strip()
    require(reference == args.expected_reference_sha, 'reference HEAD differs')
    dirty = bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'],text=True).strip())
    require(not dirty or args.development_dirty, 'reference tree is not fixed')
    digest = hashlib.sha256(args.bundle.read_bytes()).hexdigest()
    require(digest == args.bundle_sha256, 'installed bundle differs')
    report = {'reference_sha':reference,'development_dirty':dirty,'bundle_sha256':digest,'commands':{}}
    with tempfile.TemporaryDirectory(prefix='reference-relations-mcp-') as t:
        temp=Path(t)
        sock=socket.socket(); sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
        require(port not in (8113,19863), 'reserved integration port')
        origin=f'http://127.0.0.1:{port}'
        store=Store.open(temp/'house'); identity=load_or_create_identity(temp/'house')
        state=load_or_setup(store,identity,origin)
        server=uvicorn.Server(uvicorn.Config(create_app(store,identity=identity,house_state=state,hub=StreamHub(store)),
                                           log_level='error',lifespan='off'))
        thread=threading.Thread(target=lambda:server.run(sockets=[sock]),daemon=True); thread.start()
        process=None
        log=open(temp/'stderr','w+')
        try:
            deadline=time.monotonic()+10
            while not server.started and time.monotonic()<deadline: time.sleep(.05)
            require(server.started, 'temporary house failed to start')
            peer=Actor('Synthetic Peer')
            raw=make_profile(peer,'SyntheticPeer')
            with urllib.request.urlopen(urllib.request.Request(origin+'/v1/push',data=wrap_signed(raw,peer)),timeout=5) as r:
                require(r.status==200, 'fixture Profile admission')
            data=temp/'client'; (data/'config/cadence').mkdir(parents=True); (temp/'home').mkdir()
            (data/'config/plugin.json').write_text(json.dumps({'lore_houses':[origin]}))
            (data/'config/cadence/cadence.json').write_text(json.dumps({'schemaVersion':1,'delivery':{'primaryLanguage':'en'}}))
            attempts=temp/'non-loopback'
            guard=temp/'guard.mjs'
            guard.write_text("""import net from 'node:net';import dns from 'node:dns';import {appendFileSync} from 'node:fs';
const loop=new Set(['127.0.0.1','localhost','::1']);const deny=h=>{appendFileSync(ATTEMPTS,h+'\\n');throw Error('non-loopback refused');};
const c=net.Socket.prototype.connect;net.Socket.prototype.connect=function(...args){let a=Array.isArray(args[0])?args[0][0]:args[0];if((typeof a==='string'&&a.startsWith('/'))||typeof a?.path==='string')return c.apply(this,args);const h=typeof a==='object'?(a.host??'localhost'):(typeof args[1]==='string'?args[1]:'localhost');if(!loop.has(h))return deny(h);return c.apply(this,args);};
const l=dns.lookup;dns.lookup=function(h,...a){if(!loop.has(h))return deny('dns:'+h);return l.call(this,h,...a);};
""".replace('ATTEMPTS',json.dumps(str(attempts))))
            process=subprocess.Popen([args.node,'--import',str(guard),str(args.bundle)],cwd=args.bundle.parent,
                                     stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log,text=True,
                                     env={'PATH':os.environ.get('PATH',''),'HOME':str(temp/'home'),'TMPDIR':str(temp),
                                          'LANG':'en_US.UTF-8','POPCLAW_LANG':'en','POPCLAW_DATA_ROOT':str(data),
                                          'POPCLAW_CANVAS_BASE_URL':origin,'POPCLAW_WEB_BASE_URL':origin})
            m=Mcp(process)
            m.request('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'reference-relations-loop','version':'1'}})
            process.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');process.stdin.flush()
            m.call('popclaw_check_status')
            report['commands']['login']=m.call('popclaw_house_login',{'host':origin})
            report['commands']['set_name']=m.call('popclaw_set_name',{'nickname':'SyntheticSender'})
            report['commands']['follow']=m.call('popclaw_follow',{'name':peer.popclaw_id})
            edge=store.query_one('SELECT * FROM relation_edges WHERE followee=?',(peer.popclaw_id,))
            require(edge is not None and edge['state']=='active' and edge['applied_seq']==1,'native follow did not apply: '+str(report['commands']['follow']))
            report['commands']['unfollow']=m.call('popclaw_unfollow',{'name':peer.popclaw_id})
            edge=store.query_one('SELECT * FROM relation_edges WHERE followee=?',(peer.popclaw_id,))
            require(edge['state']=='revoked' and edge['applied_seq']==2,'native unfollow did not apply')
            report['commands']['draft']=m.call('popclaw_draft_message',{'recipient':peer.popclaw_id,'body':'Synthetic interoperability preview; never send.'})
            preview=json.dumps(report['commands']['draft'])
            require('SyntheticPeer' in preview and "Can't reach" not in preview,'native person resolution failed')
            require(store.query_one('SELECT COUNT(*) n FROM accepted_envelopes WHERE body_tag=26')['n']==0,'preview unexpectedly sent')
            report['relation_originals']=[]
            for row in store.query_all('SELECT r.*,a.envelope_bytes FROM relation_originals r JOIN accepted_envelopes a USING(event_id) ORDER BY r.seq'):
                e=wire.EventEnvelope.FromString(row['envelope_bytes'])
                b=e.follow_declared if row['action']=='active' else e.follow_revoked
                valid=wire.verify_ed25519(wire.key_bytes_from_popclaw_id(row['follower']),bytes(e.signature),wire.canonical_envelope(e))
                require(valid and wire.envelope_cid(row['envelope_bytes'])==row['event_id'],'native original lost signature/CID')
                report['relation_originals'].append({'event_id':row['event_id'],'seq':str(b.order.seq),'house_key':b.order.house_key,
                                                     'lorehouse':e.lorehouse,'signature_and_cid_valid':valid,'status':row['event_status']})
            require(not attempts.exists(),'non-loopback attempt')
            report['personal_delivery_rows']=store.query_one('SELECT COUNT(*) n FROM personal_log')['n']
            report['relation_public_rows']=store.query_one('SELECT COUNT(*) n FROM public_log WHERE kind IN (\'follow_declared\',\'follow_revoked\')')['n']
            require(report['personal_delivery_rows']==4 and report['relation_public_rows']==0,'private delivery obligation mismatch')
            report['dm_sent']=False
            print(json.dumps(report,indent=2))
        except BaseException:
            log.flush();log.seek(0);print(log.read()[-3000:],file=sys.stderr)
            raise
        finally:
            if process:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: process.kill();process.wait(timeout=5)
            server.should_exit=True;thread.join(timeout=5);store.close();log.close()


if __name__=='__main__':
    main()
