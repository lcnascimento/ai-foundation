# Changelog

All notable changes to the `engineering` plugin. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versioning rules of
[ADR-0006](../../docs/adr/0006-projects-track-main-without-pins.md): major renames or removes a skill or
Principle, or changes the Project setup contract; minor adds a skill, Principle or hook, or changes behavior
(including Community skill updates); patch fixes without behavior change.

A major entry always carries a **Migration** section with the steps to take in each Project (usually:
re-run `/setup-ai-foundation`).

## [0.5.0] - 2026-10-21

### Changed

- `implement-spec`: the leader reads the spec from the issue tracker once, saves it with its comments as
  `spec.md` in a notes directory outside the repo, and passes that path to every subagent, which reads its
  own ticket from the tracker and the spec only from the file. Progress on the spec goes in comments; the
  spec issue itself is touched only to change its state.

## [0.4.0] - 2026-10-18

### Changed

- `implement-spec` and `implement`: when they open a PR, they wait for its CI and fix failing checks until
  every check on the pushed head commit is green; `implement-spec` marks the PR ready only then, and stops
  under `know-when-to-stop` with the PR in draft when the same failure returns.

## [0.3.0] - 2026-10-16

### Added

- Principles: `earn-every-comment` (Custom, ADR-0013), the 20th engineering Principle. A comment, doc
  comment or lint suppression survives only on a closed exception list; everything else is deleted,
  reshaped into code, or encoded as a test, type or lint.

### Changed

- `code-review` is now derived from mattpocock: its smell baseline adds Fowler's **Comments**, the one
  hard violation of the baseline, judged against `earn-every-comment`.
- `golang`: the comment norm points to `earn-every-comment` instead of restating a looser rule.

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
