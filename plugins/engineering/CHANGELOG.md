# Changelog

All notable changes to the `engineering` plugin. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versioning rules of
[ADR-0006](../../docs/adr/0006-projects-track-main-without-pins.md): major renames or removes a skill or
Principle, or changes the Project setup contract; minor adds a skill, Principle or hook, or changes behavior
(including Community skill updates); patch fixes without behavior change.

A major entry always carries a **Migration** section with the steps to take in each Project (usually:
re-run `/setup-ai-foundation`).

## [0.2.0] - 2026-10-10

First usable release of the v1 spec (AI-36).

### Added

- Principles: the `principles` skill holds the full text of 19 engineering Principles in `references/`
  (11 engineering + 8 adaptable, Community and unchanged), loaded with `engineering:principles <name>`,
  and a Principles index hook on `SessionStart` and `SubagentStart` (ADR-0004).
- `verify` (Custom, ADR-0011): layered self-check (static, tests, runtime) before declaring work done,
  driven by the Project's `verify.md` and `environment.md`, with a `make format` / `make lint` /
  `make test` default; reports a `Verification` block.
- `golang` and `nextjs` (Custom, rewritten from several Upstreams, ADR-0010): stack skills that decide where
  code goes and at which level to test it.
- `how`, `why`, `teach`, derived from pstack, using the native subagent `model` field.
- `to-spec`, derived from mattpocock: records the agreed interfaces and seams in the spec, consulting
  `codebase-design` and running design-it-twice when an interface is open.
- `implement`, `implement-spec`, derived from mattpocock: cite `engineering:verify` and then
  `engineering:code-review` by qualified name, never the native `/code-review` (ADR-0008).
- `improve-codebase-architecture`, derived from mattpocock: hands ADRs to `foundation:documentation`.
- Community skills vendored with provenance (ADR-0001): `to-tickets`, `triage`, `tdd`, `code-review`,
  `codebase-design`, `diagnosing-bugs`, `resolving-merge-conflicts`, `pr`.
- Dependencies on `foundation` and the official `context7` plugin.
