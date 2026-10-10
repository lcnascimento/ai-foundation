# ai-foundation

Personal AI development infrastructure for [Claude Code](https://claude.com/claude-code), packaged as a
[plugin marketplace](https://code.claude.com/docs/en/plugins/host-marketplace). Every Project gets the same
skills, Principles and guardrails, locally and in cloud sessions. Each change reaches Projects through a
reviewed version bump.

Vocabulary (Foundation, Domain plugin, Principle, Community skill, Project setup, Forge, Docs backend…) is
defined in [GLOSSARY.md](./GLOSSARY.md); decisions live in [docs/adr/](./docs/adr/).

## Plugins

| Plugin | Scope | What it brings |
| --- | --- | --- |
| [`foundation`](./plugins/foundation) | user, always enabled | Skills for any domain, the 6 universal Principles, the git guardrail and `/setup-ai-foundation`. Depends on the official `linear` and `notion` plugins. |
| [`engineering`](./plugins/engineering) | Project | The engineering SDLC, 19 engineering Principles, the `golang` and `nextjs` stack skills. Depends on `foundation` and the official `context7` plugin. |

### `foundation`

- **Thinking and planning:** `grilling`, `domain-modeling`, `wayfinder`, `research`, `prototype`, `handoff`, `retro`.
- **Writing:** `documentation` writes a Project document (`adr`, `tutorial`, `how-to`, `reference`,
  `explanation`) into the Project's docs backend (repo or Notion); `technical-writing`, `unslop`, `bro` and
  `show-me` are manual.
- **Project setup:** `/setup-ai-foundation` (manual); `/setup-matt-pocock-skills` only redirects to it.
- **Principles:** `exhaust-the-design-space`, `experience-first`, `guard-the-context-window`,
  `never-block-on-the-human`, `explain-the-number`, `know-when-to-stop`.
- **Hooks:** the Principles index (`SessionStart`, `SubagentStart`) and the git guardrail (`PreToolUse` on
  `Bash`), which always denies force-push, push to the default branch, PR/MR merge, `--no-verify` and
  destructive local commands. Merging stays with the user.

### `engineering`

| Phase | Skills |
| --- | --- |
| Investigation | `how`, `why`, `teach` |
| Spec and tickets | `to-spec`, `to-tickets`, `triage` |
| Design | `codebase-design`, `improve-codebase-architecture` |
| Build | `tdd`, `implement`, `implement-spec` (manual) |
| Verify and review | `verify`, `code-review` (the native `/code-review`, `/security-review` and `/simplify` complement it) |
| Debug | `diagnosing-bugs`, `resolving-merge-conflicts` |
| PR | `pr` |
| Stack | `golang`, `nextjs` |

Its 19 Principles reach every session through the same index hook. Load any Principle's full text with
`<plugin>:principles <name>`.

## Bootstrap (once per machine)

Add the Marketplace and install `foundation` at user scope, so every Project on this machine has the
general skills and the setup:

```
claude plugin marketplace add lcnascimento/ai-foundation
claude plugin install foundation@ai-foundation --scope user
```

Also install [direnv](https://direnv.net/): Project setup gives each Project its own tokens through `.envrc`.

## Set up a Project (once per Project)

In the Project, run:

```
/setup-ai-foundation
```

It asks which plugins the Project uses, plus the Project language, the Linear workspace, the docs backend
and (with `engineering`) the forge. Then it shows a diff per file and writes only what you approve:

- the `## Agent skills` and `## Language` blocks in `CLAUDE.md`/`AGENTS.md`, plus `docs/agents/*.md`;
- `.claude/settings.json` with the Marketplace (`autoUpdate: true`, no `ref`) and `enabledPlugins`, so
  other machines and cloud sessions get the same plugins with no manual steps;
- `.mcp.json` (Linear via `Bearer ${LINEAR_API_KEY}`, hosted Notion via OAuth) and an `.envrc` that reads a
  git-ignored `.env`. Setup never writes a secret.

It also creates the Linear labels and the Notion tree through MCP, then gives you a checklist of what it
can't create (workspace, team, In Review status, tokens, OAuth, branch protection). Re-running is safe: a
second run with the same answers produces no diff.

### Uninstall the Upstream plugins

The Marketplace vendors the skills it uses from mattpocock, pstack and others. If those Upstream plugins
stay installed too, two copies of each skill compete for routing. In each Project, remove them:

```
claude plugin uninstall mattpocock-skills@claude-plugins-official --scope project
```

Run that command for each plugin the Marketplace replaces (`mattpocock-skills`, pstack, `superpowers`…).
Use `--scope user` for plugins installed at user scope. Also delete their keys from `enabledPlugins` in the
Project's `.claude/settings.json`.

## Updates

Projects follow `main` with `autoUpdate` ([ADR-0006](./docs/adr/0006-projects-track-main-without-pins.md)):

- **When updates arrive:** a plugin updates only when its `version` in `plugin.json` goes up. A merged
  change without a bump ships nothing, so CI blocks it. Auto-update runs after the first message of an
  interactive session. Run `/reload-plugins` or restart to apply it.
- **What changed:** each plugin has a `CHANGELOG.md` ([foundation](./plugins/foundation/CHANGELOG.md),
  [engineering](./plugins/engineering/CHANGELOG.md)). A major lists its migration steps, usually "re-run
  `/setup-ai-foundation`".
- **Rollback:** revert the change on `main` and bump the patch version. There are no pins or channels.
- **Emergency pin:** every release is tagged `<plugin>--vX.Y.Z` (for example, `foundation--v0.2.0`). To
  hold a Project on a tag, set `"ref": "<tag>"` on the `ai-foundation` source in
  `extraKnownMarketplaces`. The Marketplace checkout is shared per user, so this pins every Project on that
  machine. Remove the pin once the fix ships.

## Developing the Marketplace

Try a development version in any Project without publishing it:

```
claude --plugin-dir ~/path/to/ai-foundation/plugins/foundation \
       --plugin-dir ~/path/to/ai-foundation/plugins/engineering
```

After each edit, run `/reload-plugins`. No version bump is needed to test locally.

Layout of each plugin:

```
plugins/<name>/
  .claude-plugin/plugin.json   # manifest: version, dependencies
  CHANGELOG.md                 # Keep a Changelog, one entry per release
  skills/<skill>/SKILL.md      # skills; principles/references/ holds the Principle texts
  hooks/hooks.json             # Principles index, git guardrail (foundation)
```

Community and derived skills carry `license` and `metadata.*` provenance in their frontmatter and ship the
Upstream `LICENSE` next to them ([ADR-0001](./docs/adr/0001-vendor-community-skills.md),
[ADR-0010](./docs/adr/0010-stack-skills-rewrite-community-content.md)).

`writing-for-agents` (from `mattpocock-skills`) and `skill-creator` are tools for authoring this repo and
are not part of any plugin. `skill-creator` is enabled only here, at project scope, in
[.claude/settings.json](./.claude/settings.json). `mattpocock-skills` is not enabled here, since its other
skills would compete with the vendored copies for routing; load `writing-for-agents` from a separate install
when needed.

### Releasing

1. In the PR, bump `version` in `plugins/<p>/.claude-plugin/plugin.json` for every plugin you changed.
   Follow semver as ADR-0006 defines it: major renames or removes a skill or Principle, or changes the setup
   contract; minor adds a skill, Principle or hook, or changes behavior; patch is for fixes. Plugins stay
   at `0.x` until v1 ships.
2. Add the matching `CHANGELOG.md` entry, with a **Migration** section for majors.
3. Before a minor or major bump, run the behavioral evals below.
4. CI runs on every PR: `claude plugin validate --strict` on the Marketplace and on each plugin, a smoke
   install in an isolated `CLAUDE_CONFIG_DIR`, the hook tests, the provenance check and the version-bump
   check (`scripts/check-version-bump.sh <base>`). After the merge to `main`, CI tags each new version as
   `<plugin>--vX.Y.Z`.

### Behavioral evals (manual)

CI can't check whether agents actually use the plugins: that takes real model calls (tokens and an API
secret). Run these evals by hand **before every minor or major bump**. Use the approach of the
`prototype/principles-delivery` branch (`build.sh` / `run.sh` / `analyze.py`):

1. Copy a small fixture Project (a Go module with a few packages, plus a `package.json` app for `nextjs`)
   into a fresh temp directory for each run.
2. Run each scenario headlessly with the working tree's plugins:

   ```
   claude -p "<scenario prompt>" \
     --plugin-dir "$REPO/plugins/foundation" --plugin-dir "$REPO/plugins/engineering" \
     --output-format stream-json --verbose --max-turns 25 > run.jsonl
   ```

3. Grade each transcript (`run.jsonl`) against the scenario's expectation:

| Scenario | Passes when |
| --- | --- |
| Principle recall | On a task that one Principle governs, the agent loads `<plugin>:principles <name>` before its first edit and cites it in the final answer; a control task loads none. |
| Stack routing | A Go change loads `engineering:golang`; a Next.js change loads `engineering:nextjs`. Both come from the description alone. |
| Verify routing | Before declaring a change done, the agent loads `engineering:verify` and reports a `Verification` block. |
| Documentation routing | "Record this decision" loads `foundation:documentation` and writes `docs/adr/…` in the repo backend. |
| Review in `implement*` | `/implement` calls `engineering:code-review`, never the native `/code-review`. |
| Idempotent setup | Running `/setup-ai-foundation` twice with the same answers produces no diff on the second run. This covers the file-writing part only; MCP provisioning is out of scope. |

Record the results (pass/fail per scenario) in the release PR body. A regression blocks the bump.

## License

MIT, see [LICENSE](./LICENSE). Vendored skills keep their Upstream licenses next to them.
