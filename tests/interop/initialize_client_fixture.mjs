/** Use the fixed client's existing fresh-root fixture initialization. */
import { pathToFileURL } from 'node:url';
const [client, root] = process.argv.slice(2);
const { initializeTestRoot } = await import(pathToFileURL(`${client}/apps/popclaw-plugin/tests/helpers/initialize-test-root.ts`).href);
initializeTestRoot(root);
