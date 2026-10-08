# Project setup writes the mattpocock-skills contract

`setup-ai-foundation` writes the same Project setup contract as mattpocock's `setup-matt-pocock-skills`: the `docs/agents/*.md` files and the `## Agent skills` block in `CLAUDE.md`/`AGENTS.md`. On top of that, it adds what this Marketplace needs (Linear, Notion, a pluggable forge). Defining our own contract was rejected. Every mattpocock skill that reads setup (`to-spec`, `to-tickets`, `implement`, `wayfinder`, `code-review`, `triage`, …) would have to be edited, turning dozens of Community skills into derived Custom skills, and each upstream update would become a manual merge instead of a sha bump.

## Consequences

- The `setup-matt-pocock-skills` skill itself is not vendored; `setup-ai-foundation` replaces it.
- When the Upstream changes the contract (e.g. the `CONTEXT.md` → `GLOSSARY.md` rename), `setup-ai-foundation` must follow it in the same update that bumps the vendored skills.
