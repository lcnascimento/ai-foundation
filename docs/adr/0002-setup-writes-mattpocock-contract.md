# Project setup writes the mattpocock-skills contract

`setup-ai-foundation` writes the same Project setup contract as mattpocock's `setup-matt-pocock-skills`: the `docs/agents/*.md` files and the `## Agent skills` block in `CLAUDE.md`/`AGENTS.md`. On top of that, it adds what this Marketplace needs (Linear, Notion, a pluggable forge). Defining our own contract was rejected. Every mattpocock skill that reads setup (`to-spec`, `to-tickets`, `implement`, `wayfinder`, `code-review`, `triage`, …) would have to be edited, turning dozens of Community skills into derived Custom skills, and each upstream update would become a manual merge instead of a sha bump.

## Considered Options

Vendored Community skills (`wayfinder`, `code-review`, `to-tickets`, `triage`) tell the user to run `/setup-matt-pocock-skills` when the contract is missing. To route that pointer to `setup-ai-foundation`:

- **A line in the `## Agent skills` block** saying setup replaces it: rejected. The pointer fires when the contract is missing, which usually means setup never ran, so the block isn't there either.
- **A line in the hook-injected Principles index** (ADR-0004): rejected. It costs context in every session and relies on the model connecting the two names, the same weakness ADR-0008 rejected.
- **Deriving every skill that carries the pointer**: rejected. It's the per-update merge cost this decision exists to avoid.

## Consequences

- The `setup-matt-pocock-skills` skill itself is not vendored; `setup-ai-foundation` replaces it. `foundation` ships a Custom skill named `setup-matt-pocock-skills` (`disable-model-invocation: true`) that only redirects the user to `/setup-ai-foundation`. Community skills that point to it stay correct without derivation, even in a Project that was never set up, because `foundation` is installed at user scope (ADR-0007).
- When the Upstream changes the contract (e.g. the `CONTEXT.md` → `GLOSSARY.md` rename), `setup-ai-foundation` must follow it in the same update that bumps the vendored skills.
