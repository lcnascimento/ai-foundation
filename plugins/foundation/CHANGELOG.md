# Changelog

All notable changes to the `foundation` plugin. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versioning rules of
[ADR-0006](../../docs/adr/0006-projects-track-main-without-pins.md): major renames or removes a skill or
Principle, or changes the Project setup contract; minor adds a skill, Principle or hook, or changes behavior
(including Community skill updates); patch fixes without behavior change.

A major entry always carries a **Migration** section with the steps to take in each Project (usually:
re-run `/setup-ai-foundation`).

## [0.2.0] - 2026-10-10

First usable release of the v1 spec (AI-36).

### Added

- Principles: the `principles` skill holds the full text of six universal Principles in `references/`
  (`exhaust-the-design-space`, `experience-first`, `guard-the-context-window`, `never-block-on-the-human`,
  `explain-the-number` derived without `benchmark-checklist`, and the Custom `know-when-to-stop`), loaded
  with `foundation:principles <name>` (ADR-0004, ADR-0009).
- Principles index hook on `SessionStart` and `SubagentStart`: one line per Principle plus the instruction
  to load it before applying and to cite every Principle that changed a decision.
- Git guardrail `PreToolUse` hook (matcher `Bash`): always denies force-push in any form, push to the
  default branch, `gh pr merge`, `glab mr merge`, `--no-verify`, `reset --hard`, `clean -f`, `branch -D`,
  `checkout .`, `restore .`, `stash drop` and `stash clear`, and points to `know-when-to-stop` (ADR-0009).
- `setup-ai-foundation` (manual, idempotent, diff per file; ADR-0007): writes the `## Agent skills` and
  `## Language` blocks, `docs/agents/issue-tracker.md`, `triage-labels.md`, `domain.md` and, with
  `engineering` enabled, `forge.md`, `environment.md` and `verify.md`; writes `.claude/settings.json`
  (`extraKnownMarketplaces` with `autoUpdate`, `enabledPlugins`), `.mcp.json` (Linear via
  `Bearer ${LINEAR_API_KEY}`, hosted Notion via OAuth) and `.envrc`; provisions the Linear labels and the
  Notion page tree; ends with a checklist of what it can't create.
- `setup-matt-pocock-skills`: manual alias that redirects to `/setup-ai-foundation` (ADR-0002).
- `documentation` (Custom, ADR-0012): classifies and writes a Project document (`adr`, `tutorial`,
  `how-to`, `reference`, `explanation`) into the Project's docs backend (repo or Notion).
- Community skills vendored with provenance (ADR-0001): `grilling`, `research`, `wayfinder`,
  `prototype`, `handoff`, `retro` (mattpocock), `show-me` (humanlayer), `bro`, `unslop`,
  `technical-writing` (pstack).
- `domain-modeling`, derived from mattpocock: offers an ADR or an explanation and hands the writing to
  `foundation:documentation`; uses `GLOSSARY.md`.
- Dependencies on the official `linear` and `notion` plugins.

### Removed

- The `rules/` directory and the `load-rules.sh` `SessionStart` hook that dumped `rules/*.md` into
  context. The Principles index is the only Rule (ADR-0004).
