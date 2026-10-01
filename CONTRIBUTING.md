# Contributing

Ranger Map is a Python + SQLite reference application for PopClaw. Small fixes, clearer examples, and documentation improvements are welcome.

## Bugs, ideas, and questions

Use this repository's Issues for the map, application behavior, or reference server. Include your commit or release version, Python version, operating system, and the smallest reproduction. Use synthetic data and remove credentials and personal data from logs. For a suspected vulnerability, follow [SECURITY.md](SECURITY.md).

Client and installation issues belong in [PopClaw](https://github.com/PopClaw-xyz/popclaw/issues). If you are unsure, report the problem here; maintainers can help route it.

## Changes and pull requests

Start with the [README](README.md) and [application guide](docs/guide.md). Keep changes focused, match the surrounding style, and explain how you verified the result. Follow the repository's documented test commands, add a regression test for a behavior fix where practical, and state any checks you did not run.

Before changing protocol behavior, read the [protocol bindings](docs/protocol-bindings.md) and [interop verification record](docs/interop-verification.md). Discuss changes to the consumed protocol or compatibility rules before implementation. The authoritative protocol lives in [PopClaw's packages/contracts](https://github.com/PopClaw-xyz/popclaw/tree/main/packages/contracts); the bindings document records the version consumed here. Do not hand-edit generated protocol files or infer compatibility with other clients from an application-only test.

When reporting interoperability results, identify both client and server versions and the scenarios actually tested.

## Contact

Use Issues for non-sensitive project questions. For private matters, use the private maintainer contact channel supplied when you received repository access. Never post access tokens or signing keys in an issue or pull request.

By contributing you agree that your contributions are licensed under Apache-2.0. See [LICENSE](LICENSE).
