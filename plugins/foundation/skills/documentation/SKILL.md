---
name: documentation
description: "Write this Project's documents into its docs backend (repo or Notion): ADRs, tutorials, how-tos, reference and explanations. Use when a decision needs recording, when domain-modeling hands off an ADR or explanation, when an issue carries a `document:<type>` label, or when the user asks to document part of this Project."
license: MIT
metadata:
  status: derived
  upstreams:
    - repo: nWave-ai/nWave
      sha: da401a8384dc867314ba2f4a5fd802fafa593e4f
      path: nWave/skills/nw-divio-framework/SKILL.md
      license: MIT
    - repo: mattpocock/skills
      sha: 49dd158d1076134a641b33efb035946536778336
      path: skills/engineering/domain-modeling/ADR-FORMAT.md
      license: MIT
    - repo: backnotprop/pstack
      sha: 3a604672c46cd8187d2b19980eae0a34f9f91138
      path: skills/technical-writing/SKILL.md
      license: MIT
    - repo: backnotprop/pstack
      sha: 3a604672c46cd8187d2b19980eae0a34f9f91138
      path: skills/unslop/SKILL.md
      license: MIT
    - repo: humanlayer/skills
      sha: 653b6411c1f70c275a18e37673b042ff99f67ceb
      path: plugins/show-me/skills/show-me/SKILL.md
      license: MIT
---

# Documentation

Classify, structure and write one Project document, then store it where the Project's docs backend says (ADR-0005, ADR-0012). A document has exactly one **Document type**, named identically in its `document:<type>` issue label, its repo directory and its Notion page:

| Type | Reader's job | Structure |
| - | - | - |
| `adr` | Know that a decision was made, and why | [adr.md](references/adr.md) |
| `tutorial` | Learn by doing, end to end, safely | [tutorial.md](references/tutorial.md) |
| `how-to` | Get one task done now | [how-to.md](references/how-to.md) |
| `reference` | Look up one fact | [reference.md](references/reference.md) |
| `explanation` | Understand the why | [explanation.md](references/explanation.md) |

Two kinds of document never go through this skill, whatever the backend: `GLOSSARY.md` stays at the repo root (owned by `domain-modeling`), and specs live in the issue tracker (`to-spec`).

## Process

### 1. Read the Project setup

- **Docs backend**: the heading of `docs/agents/domain.md`, `# Domain Docs (<backend>, <layout>)`. `<backend>` is `repo` or `notion`; `<layout>` is `single-context` or `multi-context`.
- **Project language**: the `## Language` section of `CLAUDE.md` or `AGENTS.md`. Write the whole document in it, title and Notion page name included. Code, identifiers, paths and commands stay as they are in the code.

When `domain.md` is missing, use the repo backend with `single-context`, and tell the user once that `/setup-ai-foundation` records the backend. Suggest it; never run it. When the Project language is missing, write in the language the user writes to you.

Done when you can state the backend, the layout and the Project language, and where each came from.

### 2. Classify

The type is given when the user names it, an issue carries `document:<type>`, or `domain-modeling` hands off an `adr` or an `explanation`. Otherwise classify with [classify.md](references/classify.md).

Done when the document has one type and one job-to-be-done sentence. A request that carries two jobs becomes two documents, each with its own type, linked to each other.

### 3. Gather the facts

Read the code, ADRs, issues and conversation the document describes. Every name, command, path, flag and number in the document comes from the source, at the commit the document lands on. A tutorial's or how-to's commands get run once, when the environment allows, and their real output goes in.

Done when every claim in the outline points at the source it came from.

### 4. Write

Follow the type's reference for structure, [style.md](references/style.md) for every sentence, and [diagrams.md](references/diagrams.md) when a picture says it faster than prose.

Done when the draft has every section its type requires, passes the style.md checklist, and fits that type's job and no other.

### 5. Store

Store the document in the backend from step 1, as its section below describes.

Done when the document exists in the backend and you have its path or URL.

### 6. Report

Reply with the path or URL. When an issue labelled `document:<type>` asked for the document, the resolution comment on that issue links it.

## Repo backend

- One directory per type, singular, created on demand: `docs/adr/`, `docs/tutorial/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/`.
- File name: a kebab-case slug of the title, in English even when the Project language isn't, so paths stay stable. ADRs add their number, `NNNN-<slug>.md` (see [adr.md](references/adr.md)).
- `multi-context` layout: a decision or doc that belongs to one context goes under `src/<context>/docs/<type>/`; system-wide ones go under the root `docs/<type>/`.
- Before creating a file, list the type's directory. An existing document on the same topic gets edited, not duplicated.
- Link other documents with relative paths.

## Notion backend

`docs/agents/domain.md` holds a `## Docs backend: notion` section, written by `/setup-ai-foundation`, naming the workspace, the Project's Notion MCP server and the domain page, and mapping each enabled Document type to its page, database and data source:

```markdown
## Docs backend: notion

- **Workspace**: <workspace name>
- **MCP server**: `<server>` (tools `mcp__<server>__*`, OAuth sign-in per Project)
- **Domain page**: <domain page title> (`<page ID>`)

| Document type | Page | Database ID | Data source |
| - | - | - | - |
| `adr` | ADRs | `<database ID>` | `collection://<data source ID>` |
| `tutorial` | Tutoriais | `<database ID>` | `collection://<data source ID>` |
```

- Talk to Notion only through the `MCP server` line's server (tools `mcp__<server>__*`). Use no other Notion connection: it may point at another Project's workspace.
- Read: `notion-fetch` a database or document by ID; `notion-query-data-sources` on the type's data source to list documents.
- Write: `notion-create-pages` with the type's data source as parent, Markdown content; `notion-update-page` to edit.
- Each document is one page inside its type's database. Read the database's schema first and fill its title property and any property it requires.
- ADRs: the database's Unique ID property numbers them (`ADR-1`, `ADR-2`, …). Leave it to Notion and cite ADRs by that ID.
- Before creating a page, search the type's database for the same topic. An existing page gets edited, not duplicated.
- A type with no row in `domain.md`, or whose IDs read `pending`, has no place in this backend: stop and suggest re-running `/setup-ai-foundation` with that type enabled.
- Mermaid goes in a `mermaid` code block, which Notion renders.
- When the Notion MCP server is unavailable (no OAuth yet, a cloud session), stop and say so. Never fall back to writing the document in the repo.

## Document types from Domain plugins

The five types above are `foundation`'s. A Domain plugin adds a type (for example `jtbd`) under the same contract, without editing this skill:

1. **Name**: one lowercase kebab-case value, used unchanged as the `document:<type>` label, the `docs/<type>/` directory and the Notion database's type key in `domain.md`.
2. **Skill**: the Domain plugin ships its own skill that writes the type. It follows this skill's steps 1, 3, 5 and 6 (setup, facts, backend storage, report), and loads [style.md](references/style.md) and [diagrams.md](references/diagrams.md) from here. Its description names the type and when to write it.
3. **Setup**: the Domain plugin declares the type to Project setup, which then creates the `document:<type>` label, the Notion database and its row in `domain.md`.

When classification lands on a type this skill doesn't own, hand the document to the skill that owns it.
