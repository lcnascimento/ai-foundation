---
name: setup-ai-foundation
description: "Configure this Project for the ai-foundation plugins: Project language, Linear issue tracker and labels, docs backend, per-Project MCP and tokens, and project-scoped plugins. Idempotent; re-run it to migrate after a major."
disable-model-invocation: true
---

# Setup ai-foundation

Write the Project setup contract that the Marketplace's skills read: the `## Agent skills` block and the `## Language` section in `CLAUDE.md`/`AGENTS.md`, the `docs/agents/*.md` files, `.claude/settings.json`, `.mcp.json`, `.envrc` and the `.env` line in `.gitignore`. The contract mirrors mattpocock's `setup-matt-pocock-skills`, so vendored Community skills work unedited.

Every run is a convergence: render every file from the answers, diff it against the Project, write only what the user approves. A run whose answers match what the files already say produces no diff. Re-running is the migration path after a major.

## Sections

Each section is a file in `sections/` holding its questions, the files it renders, its `## Agent skills` entries and its checklist items. Run the sections in this order, skipping any whose **Runs when** is false:

| Section | Runs when |
| - | - |
| [plugins](sections/plugins.md) | always; its answer decides the enabled plugins every later **Runs when** reads |
| [language](sections/language.md) | always |
| [issue-tracker](sections/issue-tracker.md) | always |
| [linear-labels](sections/linear-labels.md) | always; provisions Linear labels through MCP instead of writing files |
| [docs-backend](sections/docs-backend.md) | always |
| [forge](sections/forge.md) | `engineering` is enabled |
| [environment](sections/environment.md) | `engineering` is enabled |
| [verify](sections/verify.md) | `engineering` is enabled |

A new section is a new file with the same headings (**Runs when**, **Detect**, **Ask**, **Render**, **Agent skills entries**, **Checklist**) plus one row here.

## Process

### 1. Explore

Read the Project's current state; read files, never assume:

- `git remote -v`, and whether `CLAUDE.md` and/or `AGENTS.md` exist at the root.
- Every file a section renders, plus each section's **Detect** list.
- The previous answers, recovered from the files a past run wrote (each section's **Detect** says where). They become the recommended answers.

Done when you can state, per section, its recommended answer and where it came from (previous run, Project signal, or default).

### 2. Ask

Take the sections in order: one section, its questions, its answers, then the next. Lead every question with the recommended answer so the user can accept it in a word. When a previous answer exists, recommend it unchanged.

Ask for names of secrets, never their values. If the user pastes a token, leave it out of every file and tell them it belongs in `.env`.

Done when every running section has an answer for each of its questions.

### 3. Render and diff

Pick the instructions file: `CLAUDE.md` if it exists, else `AGENTS.md`; if neither exists, ask which to create (recommend `CLAUDE.md`). Never create the second one.

Render every file into a staging tree that mirrors the Project paths:

```bash
stage="$(mktemp -d)"
```

Apply the [write rules](#write-rules) per file, then show one diff per file:

```bash
git diff --no-index -- "<path or /dev/null when absent>" "$stage/<path>"
```

Exit 0 means the file is unchanged: list it as unchanged and leave it out of the write. Then run the secret check; it must print nothing:

```bash
grep -rnE 'lin_api_|ntn_|secret_|gh[pousr]_|glpat-|Bearer [^$]' "$stage"
```

A section that provisions through MCP (linear-labels) shows its plan here instead of a file diff.

Done when every rendered file is either listed as unchanged or has its diff shown, every provisioning plan is shown, and the secret check printed nothing.

### 4. Write

Ask once to write the changed files, letting the user drop any of them. Copy each approved file from `$stage` over the Project path, then `rm -rf "$stage"`. Never write `.env`. Apply the approved provisioning plan lines as their section says.

### 5. Checklist

Print the checklist: every section's **Checklist** items, then the [core items](#core-checklist), as `- [ ]` lines. Mark an item `- [x]` only when you verified it without reading a secret (for example `command -v direnv`, or `grep -q '^LINEAR_API_KEY=' .env` with the output discarded). End with the files written, the files unchanged, and `/reload-plugins` or a restart so the new settings and MCP servers load.

## Write rules

A section's template is the body of its fenced block, without the fence lines. Each rendered file belongs to one shape. A file several sections render (`.mcp.json`, the instructions file) is rendered once with every section's contribution.

- **Owned Markdown** (`docs/agents/*.md`): the whole file is the section's template with its placeholders filled. Fill placeholders exactly and keep the template's text, spacing and trailing newline, so equal answers render equal bytes.
- **Managed sections** (`## Agent skills` and `## Language` in the instructions file): replace from the heading through the line before the next `## ` heading (or end of file) with the rendered section; append it at the end, after one blank line, when missing. Every other byte stays as it was.
- **Merged JSON** (`.claude/settings.json`, `.mcp.json`): deep-merge the section fragments onto the existing file (`{}` when absent), keeping every key setup doesn't manage:

  ```bash
  fragment='<merged fragments>'   # single quotes keep ${LINEAR_API_KEY} literal
  { cat "<path>" 2>/dev/null || echo '{}'; } \
    | jq --indent 2 --argjson frag "$fragment" '. * $frag' > "$stage/<path>"
  ```

  A key a previous run managed and the current answers drop (a plugin no longer enabled) is removed with `del(...)` in the same filter.
- **Ensured lines** (`.envrc`, `.gitignore`): copy the existing file and append each required line that's missing, preserving a trailing newline. Never remove lines.

## Agent skills block

The `## Agent skills` block holds the sections' **Agent skills entries** in section order:

```markdown
## Agent skills

### <entry title>

<one-line summary>. See `docs/agents/<file>.md`.
```

## Core checklist

Items no section owns:

- direnv installed and hooked into the shell (`direnv allow` run once in this Project after `.envrc` changes).
