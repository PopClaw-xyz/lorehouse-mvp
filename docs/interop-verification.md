# External client interoperability verification record

Date: 2026-09-10. Public-safe record; no internal paths, credentials or
fixture material are included. Full evidence lives in the G0 delivery
record cited below.

## Tested pair

| Role | Identity |
| --- | --- |
| Client (G0 public-envelope-01.3 TS candidate) | `11fbca5861542280c86078a8a93753a641866701` |
| Reference server (this repository) | `f17c8940f66636f901f0f475fec6acdcf1a03d2c` |
| Contract source both consume | commit `654a63a3f995d3f1b390541fb1de5233680dc7cd`, version `0.1.0-public-envelope-01.3`, bundle SHA-256 `3bc796e3aa4b69d0f957b2c3e71698f73c874527738f0a4c170f27b4d8e0d170` |
| G0 evidence commit (delivery + signed runtime reports) | `e75380b6daf07d416485a2a753d5660e7f661ef2` |

The reference server SHA above is the commit the interop trace actually
ran against. The subsequent code change through
`d69f783239b5055630542f2e667abc44935a9970` addresses cutover quiescence and
was separately reviewed with targeted tests. Documentation and private
source-distribution changes followed; the original trace is not claimed
to have run at this repository's current HEAD.

## What passed

Two real runtime phases against a loopback reference instance — an
ordinary process restart (SIGINT, same origin, preserved house key, server
incarnation and public log) between them; not a restore or cutover test:

- Two fixture identities performed real login, authenticated
  capability/guide preparation, and two `rangermap.check_in` submissions
  with verified signed receipts; business reads returned one latest row
  and two immutable footprints.
- Exact-request replay returned byte-identical receipts before leave,
  after acknowledged leave, and after the server restart.
- Public full lane and scope lane received both published facts; the
  **public receiver** resumed from its persisted public cursor (after
  stopping before the second fact and private message) and a fresh empty
  journal replayed both facts with no private content.
- Ordinary encrypted DMs were produced, relayed, decrypted and settled
  durably with exactly one business effect per CID, including **full wire
  replay of old messages through durable inbox dedup**; a third DM arrived
  after the restart. Non-recipient inbox-token rejection passed. A
  separate actual-HTTP **Last-Event-ID suffix** check verified that server
  capability; the client does **not** persist an inbox cursor.
- Independent read-only verification of the archived bytes — all PASS:
  both request CIDs with inner and outer signatures; both receipt
  signatures with all request/House/context bindings, the exact
  inner-envelope digest domain, and distinct wrapper bytes; both public
  `rangermap.checked_in` fact CIDs/signatures with fact bodies exactly
  equal to the signed `result_body`; and identical receipt hashes in both
  runtime reports (before and after restart).
- Manifest/proof/guide provenance: the manifest/proof/guide view retained
  by the earlier capture is byte-identical to the successful run's
  capability revision; its pin signature, declared result authority,
  guide hash, intent schema row and log incarnation were independently
  verified. The provenance is explicitly recorded and does not claim
  recovery from the deleted successful client root.

## Scope and non-claims

- **Ordinary two-phase interop: PASSED.** Deployment, hosted availability
  and behaviour on other platforms/hosts are **not** inferred from this
  record.
- The restart exercised is an ordinary process restart; log cutover,
  restore and quiesce behaviour is covered by this repository's own
  targeted regressions, not by this trace.
- DM admission policy: this reference server applies its explicit PRIVATE
  recipient-target requirement (an envelope target containing the
  recipient) to **all DM submissions it receives** — the tested client's
  new DM authoring now complies. It is not claimed as a public-wire
  mandate over DM envelopes generally: historical no-target envelopes
  remain byte-unchanged and are still accepted by the ordinary recipient
  verifier; reposting such an old envelope to this server remains
  unsupported.
