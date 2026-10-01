#!/usr/bin/env python3
"""Verify the vendored PopClaw contract bundle against its trusted pin.

Controlled copy per protocol/public-envelope-01/CONSUMPTION.md: the bundle's
CONTRACT-MANIFEST.json lists every allowed file with its SHA-256; the bundle
digest is SHA-256 over the sorted concatenation of
``<file-sha256>  <relative-path>\\n`` entries (the manifest file itself is
excluded). The expected digest below was recorded from the independently
reviewed trusted distribution (receipt-verified by the release coordinator);
this script never re-pins itself to whatever happens to be on disk.

Usage: python tools/vendor_verify_contracts.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

VENDOR_ROOT = Path(__file__).resolve().parent.parent / "vendor" / "popclaw-contracts"

# Trusted pin: 0.1.0-public-envelope-01.6 (seal commit f42bf5db; taken
# from the public candidate head 3f985f47 of merge/candidate-0.1.0, whose
# protocol files are identical to the seal). The architect signed this
# object for the re-seal scope; a whole-package acceptance receipt is still
# pending. Previous pins: .01.5 bundle
# 7956e0d9aebd7f9031193047c30322c1e5fb22a8e3788a78f3d503ad67f03bef and
# .01.3 bundle
# 3bc796e3aa4b69d0f957b2c3e71698f73c874527738f0a4c170f27b4d8e0d170. Do not
# update to match a downloaded replacement; a new pin requires a new
# reviewed candidate.
EXPECTED_BUNDLE_SHA256 = "d01bd7a060cdaa2bb35937b67e5fb4dc64a350a646b30cf2fe5dd919701ea54b"
EXPECTED_PROTOCOL_VERSION = "0.1.0-public-envelope-01.6"
EXPECTED_BASELINE = "public-envelope-01"


def main() -> int:
    manifest_path = VENDOR_ROOT / "CONTRACT-MANIFEST.json"
    if not manifest_path.exists():
        print(f"FAIL: {manifest_path} is missing", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest["protocol_version"] != EXPECTED_PROTOCOL_VERSION:
        print(f"FAIL: protocol version {manifest['protocol_version']!r} != expected",
              file=sys.stderr)
        return 1
    if manifest["envelope_baseline"] != EXPECTED_BASELINE:
        print(f"FAIL: baseline {manifest['envelope_baseline']!r} != expected",
              file=sys.stderr)
        return 1

    entries = []
    problems: list[str] = []
    listed = set()
    names = [entry["path"] for entry in manifest["files"]]
    if names != sorted(set(names)):
        print("FAIL: manifest paths are unsorted or duplicated", file=sys.stderr)
        return 1
    for entry in manifest["files"]:
        rel = entry["path"]
        listed.add(rel)
        file_path = VENDOR_ROOT / rel
        if not file_path.is_file():
            problems.append(f"missing file: {rel}")
            continue
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            problems.append(f"hash mismatch: {rel}")
        entries.append(f"{entry['sha256']}  {rel}\n")

    # No unlisted strays inside the vendor tree (local build caches such as
    # __pycache__ are not part of the controlled copy and are ignored, per
    # the bundle's own membership rules).
    ignored_parts = {"__pycache__", ".git", "node_modules", "target", ".venv"}
    for path in sorted(VENDOR_ROOT.rglob("*")):
        if path.is_file():
            rel = path.relative_to(VENDOR_ROOT)
            if ignored_parts & set(rel.parts):
                continue
            rel = rel.as_posix()
            if rel != "CONTRACT-MANIFEST.json" and rel not in listed:
                problems.append(f"unlisted file: {rel}")

    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1

    # Digest over the manifest's (sorted) row order, matching the bundle's
    # own scripts/bundle_files.py digest().
    bundle_digest = hashlib.sha256("".join(entries).encode("utf-8")).hexdigest()
    if bundle_digest != EXPECTED_BUNDLE_SHA256:
        print(f"FAIL: bundle digest {bundle_digest} != trusted pin", file=sys.stderr)
        return 1

    print(f"OK: {len(listed)} files verified against the manifest; "
          f"bundle SHA-256 matches the trusted pin {EXPECTED_BUNDLE_SHA256[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
