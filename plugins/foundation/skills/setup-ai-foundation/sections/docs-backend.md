# Section: docs-backend

Records where the Project's documents live and how skills read the domain docs (ADR-0005, ADR-0012). `GLOSSARY.md` always stays in the repo and specs always live in the issue tracker, whatever the backend.

## Runs when

Always.

## Detect

- `docs/agents/domain.md`: its `# Domain Docs (<backend>, <layout>)` heading is the previous answer.
- `GLOSSARY.md`, `GLOSSARY-MAP.md`, `docs/adr/`, `src/*/docs/adr/`.
- Monorepo signals: `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, `go.work`, or a populated `packages/*` with its own `src/`.

## Ask

1. The docs backend. Offer only `repo` (recommended).
2. The layout, only when a monorepo signal or `GLOSSARY-MAP.md` exists: `single-context` or `multi-context`. Otherwise write `single-context` without asking.

## Render

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

## Agent skills entries

```markdown
### Domain docs

{{layout}}, docs backend repo (`docs/<type>/`). See `docs/agents/domain.md`.
```

## Checklist

None.
