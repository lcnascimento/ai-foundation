# Section: docs-backend

Records where the Project's documents live and how skills read the domain docs (ADR-0005, ADR-0012). `GLOSSARY.md` always stays in the repo and specs always live in the issue tracker, whatever the backend.

## Runs when

Always.

## Detect

- `docs/agents/domain.md`: its `# Domain Docs (<backend>, <layout>)` heading is the previous answer. With `notion`, its `Workspace`, `MCP server` and `Domain page` lines and its Document type table are the previous Notion answers and IDs.
- `.mcp.json`: the server whose `url` is on `mcp.notion.com`. Its key is the previous `{{server}}`, and its presence alone means a previous run chose `notion`.
- `GLOSSARY.md`, `GLOSSARY-MAP.md`, `docs/adr/`, `src/*/docs/adr/`.
- Monorepo signals: `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, `go.work`, or a populated `packages/*` with its own `src/`.

## Ask

1. The docs backend: `repo` or `notion`. Recommend the previous answer, else `repo`.
2. The layout, only when a monorepo signal or `GLOSSARY-MAP.md` exists: `single-context` or `multi-context`. Otherwise write `single-context` without asking.
3. With `notion` only:
   - The Notion workspace that holds this Project's documents, by name (`{{workspace}}`). It must be a workspace of its own, never another Project's.
   - The domain page title (`{{domain_page}}`). Recommend the previous one, else `Engineering` written in the Project language (`Engenharia` in pt-BR).

`{{server}}` is never asked: it is the previous key, else `notion-<project>`, where `<project>` is the repo root's directory name lowercased with every run of other characters than `a-z0-9` turned into `-`.

## Render

With `repo`, render nothing Notion: no `.mcp.json` fragment and no provisioning. When `.mcp.json` holds a Notion server from a previous run, remove it with `del(.mcpServers["<key>"])` in the merge filter. The Notion pages are left as they are.

**`.mcp.json`**, merged JSON, with `notion` only. Fragment:

```json
{
  "mcpServers": {
    "{{server}}": {
      "type": "http",
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

Hosted Notion MCP authenticates by OAuth only, so the file holds no token and no header. Claude Code stores one sign-in per server definition (name included), so the per-Project name gives each Project its own grant, and one grant reaches one workspace. It shares the official `notion` plugin's endpoint, so it replaces that plugin's server in this Project, and the tools become `mcp__{{server}}__*`.

**`docs/agents/domain.md`**, owned Markdown. For the `repo` backend, `{{layout}}` filled:

~~~markdown
# Domain Docs (repo, {{layout}})

How skills consume and write this Project's domain documentation.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root, or
- **`GLOSSARY-MAP.md`** at the repo root if it exists: it points at one `GLOSSARY.md` per context. Read each one relevant to the topic.
- **`docs/adr/`**: read ADRs that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill creates them lazily when terms or decisions actually get resolved.

## Docs backend: repo

Documents live in the repo, one directory per Document type, singular and created on demand: `docs/adr/`, `docs/tutorial/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/`. Write any of them with `foundation:documentation`. `GLOSSARY.md` stays at the root and specs live in the issue tracker.

## File structure

Single-context repo (most repos):

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

Multi-context repo (presence of `GLOSSARY-MAP.md` at the root):

```
/
├── GLOSSARY-MAP.md
├── docs/adr/                          ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── GLOSSARY.md
    │   └── docs/adr/                  ← context-specific decisions
    └── billing/
        ├── GLOSSARY.md
        └── docs/adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
~~~

For the `notion` backend, `{{layout}}`, `{{workspace}}`, `{{server}}`, `{{domain_page}}`, `{{domain_page_id}}` and `{{type_rows}}` filled. `{{type_rows}}` is one line per enabled Document type, in the order `adr`, `tutorial`, `how-to`, `reference`, `explanation`, then any type a Domain plugin declares, each as ``| `<type>` | <page name> | `<database ID>` | `collection://<data source ID>` |``:

~~~markdown
# Domain Docs (notion, {{layout}})

How skills consume and write this Project's domain documentation.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root, or
- **`GLOSSARY-MAP.md`** at the repo root if it exists: it points at one `GLOSSARY.md` per context. Read each one relevant to the topic.
- **ADRs** in the Notion `adr` database below: query it for ADRs that touch the area you're about to work in.

If any of these don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill creates them lazily when terms or decisions actually get resolved.

## Docs backend: notion

Documents live in Notion, in this Project's own workspace. `GLOSSARY.md` stays in the repo and specs live in the issue tracker. Write any document with `foundation:documentation`.

- **Workspace**: {{workspace}}
- **MCP server**: `{{server}}` (tools `mcp__{{server}}__*`, OAuth sign-in per Project)
- **Domain page**: {{domain_page}} (`{{domain_page_id}}`)

Each Document type has one page under the domain page, holding one database whose rows are the documents. Page names follow the Project language.

| Document type | Page | Database ID | Data source |
| - | - | - | - |
{{type_rows}}

- **Read**: `notion-fetch` a database or a document by ID; `notion-query-data-sources` on the data source to list documents (view mode is unmetered on every plan).
- **Write**: `notion-create-pages` with the type's data source as parent, Markdown content; `notion-update-page` to edit.
- **ADR numbers**: the `adr` database's `ID` property is a Unique ID prefixed `ADR-`. Notion assigns it on creation; read it back with `notion-fetch` and cite ADRs as `ADR-<n>`. Never set it.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-7 (event-sourced orders), but worth reopening because…_
~~~

## Provision

With `notion` only. Provisions, through the `{{server}}` tools, the Notion tree of ADR-0005 and ADR-0012: the domain page, then per enabled Document type one page holding one database. It is a plan shown in step 3 next to the file diffs and applied in step 4 only after approval. It never deletes, renames or moves anything in Notion.

**When the tools are missing.** If `mcp__{{server}}__notion-fetch` isn't in this session (the server was just added to `.mcp.json`, isn't loaded, or isn't signed in), skip the plan. Render `domain.md` only when the previous one already holds every ID; otherwise leave it as it is, so skills keep the previous backend until the tree exists. Keep the provisioning checklist item open.

**Confirm the workspace.** Before planning, ask: "Provision the Notion tree in the workspace **{{workspace}}**?" On no, skip the plan as above.

**Desired tree.** Names in the Project language; these are the English and pt-BR names:

| Node | English | pt-BR |
| - | - | - |
| domain page (workspace level) | `{{domain_page}}`, default Engineering | `{{domain_page}}`, default Engenharia |
| `adr` page and database | ADRs | ADRs |
| `tutorial` page and database | Tutorials | Tutoriais |
| `how-to` page and database | How-tos | How-tos |
| `reference` page and database | Reference | Referência |
| `explanation` page and database | Explanations | Explicações |

Each database is inline in its type's page, titled like the page, with the title property `Name`. The `adr` database also has `ID`, a Unique ID property with prefix `ADR-`.

**Match.** For each node, in tree order:

- With an ID from the previous `domain.md`, `notion-fetch` it. Found and not in trash: **ok**. Not found: match it by name as below and note the stale ID.
- Without an ID, match by exact name: the domain page with `notion-search` for `{{domain_page}}`, keeping only workspace-level pages; a type page among the children `notion-fetch` shows for the domain page; a database among the children of its type page.
- One match: **ok**, record its ID. None: **create**. Several: **conflict**, never chosen; the user resolves it in Notion and re-runs.
- For the `adr` database, **ok** also requires `ID` to be a Unique ID with prefix `ADR-`; otherwise plan **add ID** on it.

A run where every node is **ok** prints "notion: no changes" and makes no write.

**Render** the plan:

```
notion tree (<workspace>)
  ok        Engenharia
  create    Engenharia / Tutoriais (page)
  create    Engenharia / Tutoriais / Tutoriais (database)
  add ID    Engenharia / ADRs / ADRs (Unique ID ADR-)
  conflict  Engenharia / Referência: 2 pages with this name
```

While the plan holds a **create**, step 3 shows `domain.md` with `pending` in place of each missing ID.

**Apply** in step 4, before writing any file, in plan order:

- Domain page: `notion-create-pages` with no parent (a private workspace-level page) and the title only.
- Type page: `notion-create-pages` with the domain page as parent and the title only.
- Database: `notion-create-database` with the type page as parent, the title and the properties above.
- **add ID**: `notion-update-data-source` adding the `ID` Unique ID property with prefix `ADR-`. If the tool rejects it, keep the checklist item for adding it by hand.

Then `notion-fetch` each database to read its database ID and its data source ID (`collection://…`), re-render `domain.md` with every ID, show its diff, and match again: the plan must hold only **ok** and **conflict** lines. A second run finds every ID and creates nothing.

## Agent skills entries

With `repo`:

```markdown
### Domain docs

{{layout}}, docs backend repo (`docs/<type>/`). See `docs/agents/domain.md`.
```

With `notion`:

```markdown
### Domain docs

{{layout}}, docs backend Notion (workspace {{workspace}}, through the `{{server}}` MCP server). See `docs/agents/domain.md`.
```

## Checklist

With `repo`: none. With `notion`:

- A Notion workspace for this Project, {{workspace}}, where you can create pages.
- Notion signed in for this Project: after `/reload-plugins` or a restart, run `/mcp`, pick `{{server}}` and authenticate (or `claude mcp login {{server}}`), choosing {{workspace}} on the consent screen. Once per Project per machine; nothing goes in `.env`. Cloud sessions can't complete this sign-in, so they don't read Notion docs.
- Notion tree provisioned: run `/setup-ai-foundation` again after signing in when the `{{server}}` tools weren't loaded during this run. Mark it done only when the last plan of this run held no **create** or **add ID** line.
- Each **conflict** from the plan resolved in Notion, and the `ID` Unique ID property (prefix `ADR-`) added by hand to the `adr` database when the tool rejected it.
