# Section: plugins

Registers the Marketplace in the Project and enables its plugins at project scope, so other machines and contributors who trust the folder receive the same harness (ADR-0006, ADR-0007).

## Runs when

Always.

## Detect

- `.claude/settings.json`: the `ai-foundation` entry under `extraKnownMarketplaces` and the `*@ai-foundation` keys under `enabledPlugins` set to `true` are the previous answer.
- Code signals for the engineering recommendation: `go.mod`, `package.json`, `Makefile`, `src/`, a CI directory (`.github/workflows/`, `.gitlab-ci.yml`).

## Ask

Which Domain plugins to enable. `foundation` is always enabled and isn't asked.

| Plugin | Recommend when |
| - | - |
| `engineering` | a code signal exists, or a previous run enabled it |

## Render

`.claude/settings.json`, merged JSON. Fragment, with one `enabledPlugins` key per enabled plugin (`foundation` always):

```json
{
  "extraKnownMarketplaces": {
    "ai-foundation": {
      "source": { "source": "github", "repo": "lcnascimento/ai-foundation" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "foundation@ai-foundation": true,
    "engineering@ai-foundation": true
  }
}
```

The source carries no `ref`: Projects follow `main`. Remove `<plugin>@ai-foundation` from `enabledPlugins` when a previous run enabled it and the user declined it now.

## Agent skills entries

None.

## Checklist

- Accept the workspace trust dialog for this folder in Claude Code, so the project `extraKnownMarketplaces` applies.
