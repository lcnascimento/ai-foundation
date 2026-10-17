# ai-foundation

## Language

- **Project language: Portuguese (pt-BR).** Talk to the user, and write documentation (`README.md`, `GLOSSARY.md` definitions, ADRs and other documents, Notion pages), issue tracker content and PR bodies, in Portuguese (pt-BR).
- **Code artifacts are English**: code, identifiers, comments, commit messages, branch names, PR titles, skills, `CLAUDE.md`/`AGENTS.md` and `docs/agents/*`. `GLOSSARY.md` terms stay identical to the code identifiers.

## Agent skills

### Issue tracker

Linear, team AI Foundation (`AI`), through the `linear` MCP server. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles under the `triage` label group, names unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

single-context, docs backend repo (`docs/<type>/`). See `docs/agents/domain.md`.

### Forge

GitHub at `github.com` through the `gh` CLI, repository `lcnascimento/ai-foundation`. See `docs/agents/forge.md`.
