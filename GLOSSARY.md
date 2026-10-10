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
Guidance a plugin injects into every session's context through a hook, always on. Per-Project guidance written into a Project's `CLAUDE.md` by Project setup is not a Rule.
_Avoid_: guideline, policy

**Principle**:
A named development philosophy (e.g. "subtract before you add") the user wants agents to follow.
_Avoid_: rule (a Principle reaches every session only as one line of the Principles index, which is a Rule; its text loads on demand)

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
_Avoid_: Linear project

**Linear project**:
A finite deliverable inside a Project's issue tracker, possibly spanning several domains.

**Project setup**:
The per-Project configuration (issue tracker, forge, docs backend, Project language) that skills read instead of hard-coding tools.

**Forge**:
The platform hosting a Project's git repository and its code workflow: pull/merge requests, review, CI and releases (GitHub, GitLab). Distinct from the issue tracker.

**Docs backend**:
Where a Project's documents live: the repo (default) or Notion.

**Document type**:
The kind of a Project document (`adr`, `tutorial`, `how-to`, `reference`, `explanation`; Domain plugins may add more), named identically in its issue label, its repo directory and its Notion page.
_Avoid_: quadrant, doc category

**Project language**:
The human language agents use to talk to the user and to write a Project's documentation; code artifacts are always English.
_Avoid_: locale
