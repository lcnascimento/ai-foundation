# Section: verify

Writes `docs/agents/verify.md`, the commands `engineering:verify` runs for each layer (ADR-0011). Its format is owned by `engineering:verify`'s `references/project-files.md` (`plugins/engineering/skills/verify/references/project-files.md` in the Marketplace). Render that format exactly; don't add sections.

## Runs when

`engineering` is enabled. Without it, ask nothing and render nothing here.

## Detect

- `docs/agents/verify.md`: when it exists, its whole content is the previous answer, hand edits included.
- Root `Makefile` targets (`grep -E '^[A-Za-z0-9_.-]+:' Makefile`, skipping `.PHONY` and pattern rules), in file order:
  - static: `format`, `fmt`, `lint`, `vet`, `typecheck`, `check`;
  - tests: `test`, and every `test-*`/`test_*` target;
  - runtime: `run`, `run-*`, `dev`, `serve`, `start`.
- The CI config (`.github/workflows/*.yml` `steps[].run`, `.gitlab-ci.yml` `script`): each command in job and step order, and whether it needs a secret (`secrets.`, a protected variable), a deploy or publish target, or a remote environment.
- The **Health check** of the `environment` section's answer.

## Ask

When `docs/agents/verify.md` exists, recommend it unchanged and show only what detection found that it lacks (a new Makefile target, a new CI step), each as an optional addition. Otherwise recommend the proposal below, section by section.

Proposal, each section omitted when it has nothing to say:

- **Static**: `make <format target> (commit what it changes)` first when a format target exists, then `make <target>` for the other static targets in file order. Without static targets, the CI commands that format, lint, vet or typecheck, in CI order.
- **Tests**: `make test` when it exists, else `make <target>` for each `test-*` target. Without test targets, the CI commands that run tests and need no secret, in CI order. Ask about every other `test-*` target: in Tests, or in Exclusions with a reason.
- **Runtime**: `make <runtime target>`, then the environment's health check, when both exist; the user confirms it, and adds when it applies.
- **Exclusions**: each CI command that needs a secret, deploys, publishes or targets a remote environment, as `` `<command>`: CI only, <reason>. ``; plus the `test-*` targets the user excluded, with their reasons.
- **Passing**: only what the user adds beyond exit code 0.

## Render

**`docs/agents/verify.md`**, owned Markdown: the approved content in the format of `project-files.md`, `# Verify` first, then the sections in its order (Static, Tests, Runtime, Exclusions, Passing), one blank line between blocks, list items as `- ` with commands in backticks, a trailing newline. When the previous file is accepted unchanged, render it byte for byte. When every section is empty, render no file; `engineering:verify` then uses its default.

## Agent skills entries

None. `engineering:verify` reads the file directly.

## Checklist

None.
