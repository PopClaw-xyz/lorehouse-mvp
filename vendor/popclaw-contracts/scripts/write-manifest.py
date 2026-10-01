#!/usr/bin/env python3
"""Freeze the reviewed source file set. This does not publish or install anything."""
import json
from bundle_files import ROOT,entries,digest
rows=entries()
manifest={'protocol_version':'0.1.0-public-envelope-01.6','envelope_baseline':'public-envelope-01',
          'digest_algorithm':'sha256(sorted(file_sha256 + "  " + relative_path + "\\n"))',
          'bundle_sha256':digest(rows),'files':rows}
(ROOT/'CONTRACT-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Frozen {len(rows)} files: {manifest["bundle_sha256"]}')
