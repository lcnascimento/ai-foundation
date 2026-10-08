# ai-foundation

Personal AI development infrastructure for [Claude Code](https://claude.com/claude-code), packaged as a
[plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces). Skills, rules,
MCP servers and agents, organized as domain-specific plugins you install into any project.

## Install

```
/plugin marketplace add lcnascimento/ai-foundation
```

`foundation` installs automatically (base plugin, holds shared skills and every other plugin's
dependency). Enable the domains a given project actually needs:

```
/plugin enable backend
/plugin enable frontend
```

## Plugins

| Plugin | Purpose |
| --- | --- |
| `foundation` | Base skills and philosophy rules. Always enabled. |
| `backend` | Backend development skills, rules and MCPs. |
| `frontend` | Frontend development skills, rules and MCPs. |
| `design` | Product/UI design skills, rules and MCPs. |
| `infrastructure` | Infrastructure, deployment and DevOps skills, rules and MCPs. |
| `documentation` | Documentation authoring skills, rules and MCPs. |
| `product` | Product management skills, rules and MCPs. |
| `project-management` | Project/task management skills, rules and MCPs. |
| `marketing` | Marketing skills, rules and MCPs. |

## Structure

Each plugin is self-contained under `plugins/<name>/`:

```
plugins/<name>/
  .claude-plugin/plugin.json   # manifest, declares dependencies on foundation
  skills/                      # SKILL.md-based skills
  rules/                       # philosophy/guideline docs, loaded via a SessionStart hook
  hooks/                       # hooks.json, loads rules/*.md into context on session start
  agents/                      # custom subagents
  commands/                    # legacy slash commands
  .mcp.json                    # MCP servers this plugin needs
```

`foundation`'s skills are the source of truth for `.agents/skills`, which is symlinked from
`.claude/skills` for local development inside this repo itself.

## License

MIT — see [LICENSE](./LICENSE).
