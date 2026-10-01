// Copy the exact generated codec inputs into the compiled package distribution.
import fs from 'node:fs';
import path from 'node:path';
const source=path.resolve('src/generated');
const target=path.resolve('dist/generated');
fs.rmSync(target,{recursive:true,force:true});
fs.cpSync(source,target,{recursive:true});
