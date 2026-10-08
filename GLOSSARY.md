# ai-foundation

Personal, domain-agnostic AI harness for Claude Code, distributed as a plugin marketplace that any personal project can install.

## Language

### Packaging

**Marketplace**:
This repository, as the single catalog of installable plugins.

**Plugin**:
A self-contained, installable bundle of skills, rules, hooks and MCP servers under `plugins/<name>/`.

**Foundation**:
The always-enabled plugin holding everything a plugin of *any* domain would use; the test is "would a marketing plugin use this?".
_Avoid_: core, base, shared

**Domain plugin**:
An opt-in plugin scoped to one area of work (engineering, marketing, business), depending on Foundation.

### Behavior

**Skill**:
A `SKILL.md` capability loaded on demand when its description matches the task or the user invokes it.

**Rule**:
Guidance injected into every session's context, always on.
_Avoid_: guideline, policy

**Principle**:
A named development philosophy (e.g. "subtract before you add") the user wants agents to follow.
_Avoid_: rule (a Principle may or may not be delivered as a Rule)

**Community skill**:
A skill vendored from an Upstream and kept identical to it at the pinned commit, except for provenance frontmatter.
_Avoid_: third-party skill, external skill

**Custom skill**:
A skill authored in this repo, or a Community skill edited beyond its provenance frontmatter (a derived skill).

**Upstream**:
The external repository and pinned commit a Community skill or derived Custom skill was copied from.

### Projects

**Project**:
A personal repository that installs the Marketplace's plugins; distinct from this repo.

**Project setup**:
The per-Project configuration (issue tracker, forge, docs location) that skills read instead of hard-coding tools.
