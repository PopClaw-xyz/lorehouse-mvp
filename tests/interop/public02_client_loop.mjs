/** Fixed native public receiver against a fresh Python reference; loopback only. */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const input = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const load = relative => import(pathToFileURL(`${input.clientRoot}/apps/popclaw-plugin/${relative}`).href);
const { LocalHostDb } = await load('src/host/local-host-db.ts');
const { makeWorldManifestPreparer, readHouseCapabilityView } = await load('src/world/world-capabilities.ts');
const { preparePublicStreamJournal, EMPTY_PUBLIC_CONSUMER_MAPPING_DIGEST } = await load('src/world/scoped-stream-journal.ts');
const { PublicV1Receiver } = await load('src/ingress/public-world-stream-client.ts');
const db = new LocalHostDb(input.database);
const controller = new AbortController();
const gate = { origin: input.origin, signal: controller.signal, isActive: () => !controller.signal.aborted };
const errors = [], requests = [];
const localFetch = async (url, options) => {
  assert.equal(new URL(url instanceof Request ? url.url : url).origin, input.origin, 'non-fixture fetch');
  requests.push(String(url)); return fetch(url, options);
};
const until = async (check) => {
  const end = Date.now() + 15000;
  while (!check()) {
    if (errors.length) throw new Error(JSON.stringify(errors));
    assert.ok(Date.now() < end, 'client receiver timeout');
    await new Promise(resolve => setTimeout(resolve, 25));
  }
};
let receiver;
try {
  const response = await localFetch(input.origin + '/v1/manifest');
  const rawBytes = new Uint8Array(await response.arrayBuffer());
  const prepared = await makeWorldManifestPreparer({ fetch: localFetch })({ origin: input.origin, rawBytes,
    proofHeader: response.headers.get('x-popclaw-manifest-proof'), ackKeyHex: input.ackKeyHex,
    provenance: 'loopback_fixture', signal: controller.signal });
  db.transaction(prepared.commit);
  const view = readHouseCapabilityView(db, input.origin);
  assert.equal(view.publicStream.validation, 'valid');
  assert.ok(view.publicStreamCapability);
  assert.equal(view.publicStreamCapability.publicStream.envelope_baseline, 'public-envelope-02');
  assert.equal(view.publicStreamCapability.publicStream.log_incarnation, input.log);
  assert.ok(view.verified.guideBytes?.length, 'verified guide bytes absent');
  const options = { capability: view.publicStreamCapability, gate, executionDb: db,
    selection: { fullPublic: true, scopes: [] },
    producerPolicy: { house: view.verified.house, capabilityRevision: view.verified.capabilityRevision,
      officialActorIds: JSON.parse(Buffer.from(rawBytes).toString()).official_ids },
    approvedConsumerMappingDigest: EMPTY_PUBLIC_CONSUMER_MAPPING_DIGEST,
    consumerContracts: [], consumers: [], fetch: localFetch,
    onError: error => errors.push(String(error)) };
  const preparation = preparePublicStreamJournal(options);
  assert.equal(preparation.imported, 0); assert.equal(preparation.restricted, 0);
  receiver = new PublicV1Receiver(options);
  await receiver.start();
  await until(() => receiver.receiveStatus().caughtUp && receiver.receiveStatus().publicAfter === '1');
  const replay = receiver.receiveStatus();
  let rows = db.queryAll('SELECT * FROM world_public_events_v1');
  assert.equal(rows.length, 1);
  assert.equal(Buffer.from(rows[0].envelope).toString('hex'), input.replayHex);
  for (let repeat = 0; repeat < 2; repeat++) {
    const pushed = await localFetch(input.origin + '/v1/push', { method: 'POST', body: Buffer.from(input.liveWrapperHex, 'hex') });
    assert.equal(pushed.status, 200);
    const receipt = await pushed.json();
    assert.equal(receipt.event_id, input.liveCid);
    assert.equal(receipt.public, true);
    if (repeat) assert.equal(receipt.duplicate, true);
  }
  await until(() => receiver.receiveStatus().caughtUp && receiver.receiveStatus().publicAfter === '2'
    && receiver.receiveStatus().checkpointHighWater === '2');
  const live = receiver.receiveStatus();
  rows = db.queryAll('SELECT * FROM world_public_events_v1');
  assert.equal(rows.length, 2);
  assert.equal(Buffer.from(rows.find(row => row.event_id === input.liveCid).envelope).toString('hex'), input.liveHex);
  await receiver.stop();
  receiver = new PublicV1Receiver(options);
  await receiver.start();
  await until(() => receiver.receiveStatus().caughtUp && receiver.receiveStatus().publicAfter === '2');
  assert.equal(db.queryAll('SELECT * FROM world_public_events_v1').length, 2);
  assert.ok(requests.some(url => url.includes('public_after=1') || url.includes('public_after=2')));
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ manifestProofAndGuideVerified: true, baseline: 'public-envelope-02',
    freshJournal: preparation, replay, live, resumed: receiver.receiveStatus(),
    exactOriginalBytesAndCid: true, durableEvents: rows.length, errors, requests }, null, 2));
} finally {
  if (receiver) await receiver.stop();
  controller.abort(); db.close();
}
