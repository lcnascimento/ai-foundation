# Docs live in the repo by default, in Notion opt-in, written in the Project language

Each Project picks a docs backend in Project setup, recorded in `docs/agents/domain.md`, and that one switch covers both ADRs and Divio docs. By default it is the repo: `docs/adr/` (mattpocock's layout, unchanged) plus `docs/{tutorials,how-to,reference,explanation}/`, created lazily, with no domain level. With Notion on, each Project gets its own Notion workspace (mirroring ADR-0003) holding one page per domain (only Engineering for now). Each domain page holds five pages (tutorials, how-tos, reference, explanations, ADRs), each with a database for its child pages. ADRs are numbered by a Unique ID property prefixed `ADR-`, and `domain.md` stores the workspace and database IDs. `GLOSSARY.md` always stays in the repo, specs always live in the issue tracker (`to-spec` as is), and this repo itself runs with the repo backend.

Separately, Project setup records a **Project language**. Agents use it to talk to the user and to write all documentation: `README.md`, `GLOSSARY.md` definitions (terms stay identical to the code identifiers), ADRs, Divio docs, Notion page names included, issue tracker content and PR bodies. Code artifacts are always English: code, identifiers, comments, commit messages, branch names, PR titles, skills, `CLAUDE.md`/`AGENTS.md` and `docs/agents/*`. This repo's Project language is English.

## Considered Options

- **ADRs always in the repo, Notion only for Divio**: rejected. The user wants all long-form documentation, ADRs included, in one browsable place when Notion is on.
- **Repo as source plus a Notion mirror**: rejected because sync is build cost and a drift risk for no reader gain.
- **One shared Notion workspace with a root page per Project**: rejected in favor of a workspace per Project, consistent with Linear.
- **Fixed language split (docs in Portuguese, repo in English)**: rejected because the language is a per-user setting, not a per-location rule.

## Consequences

- `domain-modeling` (`ADR-FORMAT.md` plus its file-structure section) and `improve-codebase-architecture` (one line) become derived Custom skills that read and write ADRs wherever `domain.md` says, defaulting to `docs/adr/`. Each Upstream update to them is a manual merge.
- With Notion on, agents read ADRs and docs through the Notion MCP, which has a context cost and, on the free plan, a 3 req/s limit. Whether it works headless or in cloud sessions with a workspace per Project is still open.
- `setup-ai-foundation` asks for the docs backend and the Project language and writes both into the contract files.
