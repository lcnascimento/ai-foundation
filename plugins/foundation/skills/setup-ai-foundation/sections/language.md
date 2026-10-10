# Section: language

Records the Project language in the always-loaded instructions file, so subagents and skills that never open `docs/agents/` follow it (ADR-0005, ADR-0007).

## Runs when

Always.

## Detect

- The `## Language` section of the instructions file: its `**Project language: <language>.**` line is the previous answer.

## Ask

The Project language. Recommend the previous answer, else the language the user is writing in.

## Render

The `## Language` managed section of the instructions file, with `{{language}}` filled:

```markdown
## Language

- **Project language: {{language}}.** Talk to the user, and write documentation (`README.md`, `GLOSSARY.md` definitions, ADRs and other documents, Notion pages), issue tracker content and PR bodies, in {{language}}.
- **Code artifacts are English**: code, identifiers, comments, commit messages, branch names, PR titles, skills, `CLAUDE.md`/`AGENTS.md` and `docs/agents/*`. `GLOSSARY.md` terms stay identical to the code identifiers.
```

## Agent skills entries

None.

## Checklist

None.
