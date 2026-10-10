import assert from 'node:assert/strict';
import fs from 'node:fs';
import Ajv2020 from 'ajv/dist/2020.js';
const base = 'packages/contracts/protocol/';
const read = p => JSON.parse(fs.readFileSync(base+p,'utf8'));
const profile=read('retained/schema-profile.schema.json');
const ajv=new Ajv2020({strict:false,allErrors:true});
ajv.addMetaSchema(profile);
const board=read('public-envelope-02/board.schema.json');
const validate=ajv.compile(board);
const examples=read('public-envelope-02/examples.json');
assert(validate(examples.public_only),JSON.stringify(validate.errors));
const absent=structuredClone(examples.public_only);delete absent.public_stream.envelope_baseline;
assert.equal(validate(absent),false,'new receiver rejects missing baseline');
const different=structuredClone(examples.public_only);different.public_stream.envelope_baseline='unsupported';
assert.equal(validate(different),false,'new receiver rejects other baseline');
const old=structuredClone(board);delete old.$defs.public_stream.properties.envelope_baseline;
old.$defs.public_stream.required=old.$defs.public_stream.required.filter(k=>k!=='envelope_baseline');
assert.equal(ajv.compile(old)(examples.public_only),false,'strict old receiver rejects added field');
assert(ajv.compile(old)(absent),'original block shape remains representable');
// Block failures are isolated by a two-stage consumer, not by ignoring failures
// of the full schema. This illustrates the exact independent block schemas.
const block=name=>ajv.compile({$defs:board.$defs,$ref:'#/$defs/'+name});
assert(block('actions')(examples.manual_action.actions));
assert.equal(block('public_stream')(absent.public_stream),false);
assert(block('actions')(examples.manual_action.actions),'unrelated valid action block remains independently valid');
let count=0;
for(const path of ['public-envelope-02/board.schema.json','public-envelope-02/action-kind.schema.json',
 'public-envelope-02/interpreted-event-kind.schema.json','retained/participation.schema.json','retained/private-message.schema.json']) {
  const schema=read(path);
  assert(ajv.validateSchema(schema),`${path}: ${JSON.stringify(ajv.errors)}`);
  ajv.compile(schema);count++;
}
// Verify self-contained local $ref closure. $schema is an annotation identifier,
// never a request to fetch a remote schema.
function refs(value,root){
 if(Array.isArray(value)){for(const v of value) refs(v,root);return;}
 if(!value||typeof value!=='object')return;
 if(typeof value.$ref==='string'){assert(value.$ref.startsWith('#/'));let target=root;
  for(const k of value.$ref.slice(2).split('/'))target=target[k.replaceAll('~1','/').replaceAll('~0','~')];
  assert(target!==undefined,`missing ${value.$ref}`);
 }
 for(const child of Object.values(value))refs(child,root);
}
for(const path of ['public-envelope-02/board.schema.json','public-envelope-02/action-kind.schema.json',
 'public-envelope-02/interpreted-event-kind.schema.json','retained/participation.schema.json',
 'retained/private-message.schema.json','retained/schema-profile.schema.json']){const x=read(path);refs(x,x);}
console.log(`Schema/negotiation tests passed; ${count} payload schemas compiled and 6 local reference closures checked`);
