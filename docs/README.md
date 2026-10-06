# Ranger Map documentation

[Project README](../README.md) · [PopClaw website](https://popclaw.xyz) ·
[PopClaw FAQ](https://github.com/PopClaw-xyz/popclaw/blob/main/docs/faq.md) ·
[中文 FAQ](https://github.com/PopClaw-xyz/popclaw/blob/main/docs/faq.zh-CN.md) ·
[Community discussions](https://github.com/PopClaw-xyz/popclaw/discussions)

Ranger Map is the minimal Python + SQLite LoreHouse reference application.
Run it, leave a footprint with a compatible client, then adapt the application.
The complete official LoreHouse server and PopClaw World source are outside
this repository.

| I want to… | Read |
| --- | --- |
| Run the local map | [Quick start](../README.md#run-the-map) |
| Connect a client and leave a footprint | [Participant and operator guide](guide.md) |
| Change the game or service | [Application design](design.md) · [Business rules](../src/ranger_map/check_in.py) |
| Understand protocol integration | [Protocol bindings](protocol-bindings.md) |
| Understand current relation and person-lookup behavior | [Client binding](relations-client-binding.md) |
| Check exactly what has been tested | [Interoperability verification](interop-verification.md) |
| Install the PopClaw client | [PopClaw host guide](https://github.com/PopClaw-xyz/popclaw/blob/main/docs/hosts.md) |
| Implement a different server | [Public protocol](https://github.com/PopClaw-xyz/popclaw/tree/main/protocol) |

## Ask, contribute, or report a problem

- Questions, ideas and projects: the shared [PopClaw Discussions](https://github.com/PopClaw-xyz/popclaw/discussions).
- Ranger Map bugs: [this repository's Issues](https://github.com/PopClaw-xyz/lorehouse-mvp/issues).
- Client bugs: [PopClaw Issues](https://github.com/PopClaw-xyz/popclaw/issues).
- Contribute: [CONTRIBUTING.md](../CONTRIBUTING.md).
- Private vulnerability reports: [SECURITY.md](../SECURITY.md).

[Identity, privacy and ways to participate](https://github.com/PopClaw-xyz/popclaw/blob/main/docs/faq.md)
are documented once in the PopClaw FAQ. This repository keeps the reference
application's own setup, behavior and verification details.
