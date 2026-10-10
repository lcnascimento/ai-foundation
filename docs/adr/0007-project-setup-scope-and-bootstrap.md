# Project setup is one manual skill that writes files, provisions trackers, and never stores secrets

`setup-ai-foundation` is a single skill in `foundation`, invoked only by the user (`disable-model-invocation: true`), and it replaces both `setup-matt-pocock-skills` and `setup-pstack`. It runs idempotently and shows a diff per file. Its sections depend on which plugins are enabled; for example, the forge section appears only with `engineering`. It writes:

- `CLAUDE.md`/`AGENTS.md`: the `## Agent skills` block (mattpocock contract, ADR-0002, plus a `### Forge` entry pointing to `forge.md`) plus a `## Language` section holding the Project language, which is always in context, so subagents and skills that never open `docs/agents/` still follow it.
- `docs/agents/issue-tracker.md` (Linear), `triage-labels.md`, `domain.md` (docs backend, plus Notion IDs, ADR-0005), and `forge.md` (forge, CLI `gh`/`glab`, host, commit, PR and CI conventions; the forge default is proposed from `git remote` but stored, never inferred at runtime, and the commit default is "follow the style of `git log`; with no history, an imperative sentence without a prefix", with Conventional Commits offered as an option).
- `.claude/settings.json`: `extraKnownMarketplaces` with `autoUpdate`, and `enabledPlugins` (ADR-0006).
- `.mcp.json`: Linear with `Bearer ${LINEAR_API_KEY}`, and the hosted Notion MCP over OAuth when the Notion backend is on.
- `.envrc` reading a git-ignored `.env`, so each Project on a machine gets its own tokens through direnv. Setup never writes a secret.

Through the MCPs it also provisions what they can create, idempotently: the Linear labels (ADR-0003) and the Notion page/database tree (ADR-0005). It hands the user a checklist for the rest: the workspace, the team, the In Review status, tokens, and the OAuth grant.

Bootstrap: once per machine, the user adds the Marketplace and installs `foundation` at user scope, then runs `/setup-ai-foundation` in the Project, which pins everything else at project scope so other machines and cloud sessions receive it.

## Considered Options

- **Infer the forge from `git remote` in every skill**: rejected. A self-hosted GitLab host needs a heuristic in every skill, and an explicit file mirrors `issue-tracker.md`.
- **One setup fragment per Domain plugin** (`engineering:setup` orchestrated by `foundation`): deferred. With a single Domain plugin, the split is pure coordination cost; the first non-engineering plugin reopens it.
- **Per-Project variable names (`LINEAR_API_KEY_REMARKS`) or a Keychain `headersHelper`**: rejected in favor of direnv, which works the same in the terminal and maps directly to cloud-session environment variables.
- **Local `@notionhq/notion-mcp-server` with `NOTION_TOKEN`**: rejected because it is unmaintained, even though it is the only option that runs headless.
- **Recording the stack and per-Project Principle toggles**: rejected. The stack is already in the repo (`go.mod`, `package.json`), and the active Principles are those of the enabled plugins (ADR-0004).
- **A `curl | sh` bootstrap or a hand-written `settings.json`**: rejected because it adds an artifact to maintain, and `foundation` is always enabled anyway.

## Consequences

- Cloud sessions in Projects with the Notion backend can't read ADRs or docs, because the hosted Notion MCP needs interactive OAuth.
- Re-running setup is the migration path: a major that changes the contract tells users, in its `CHANGELOG.md`, to re-run it.
- Skills that find the contract missing suggest `/setup-ai-foundation` to the user; they never run it.
- Machines need direnv installed.
- Per-Project always-on guidance (language, where the contract files live, commit conventions) reaches the agent through the `CLAUDE.md` this setup writes, not through a plugin Rule (ADR-0004).
