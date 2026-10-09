# Projects track `main` with auto-update, without pins or channels

Projects register the Marketplace from public GitHub (`lcnascimento/ai-foundation`) with `autoUpdate: true` and no `ref`, so they always follow `main`. A release is a merged PR that bumps a plugin's `version`: each plugin carries its own semver in `plugin.json`, bumped only when that plugin changes, because the computed version is the only update signal Claude Code has. There is no stable/dev channel; the development version is used in a Project through `claude --plugin-dir` plus `/reload-plugins`, and a rollback is a revert plus a patch bump, not a pin.

## Considered Options

- **Pin each Project to a tag or a `stable` branch**: rejected. Relative-path plugins can only be pinned through the Marketplace ref, and `known_marketplaces.json` is per user and keyed by name, so every Project on a machine ends up on the same ref anyway.
- **Two marketplaces as channels** (`ai-foundation` and `ai-foundation-dev`): rejected as build and setup cost for a single developer whom `--plugin-dir` already serves.
- **Lockstep versioning** (all plugins and `marketplace.json` share one version): rejected; it reinstalls unchanged plugins on every release. `marketplace.json` carries no `version`.
- **Hosting on the homelab GitLab, or a private GitHub repo**: rejected because Anthropic cloud sessions can't reach the homelab, and a private repo needs credentials on every machine and session. The repo holds no secrets.

## Consequences

- A forgotten bump silently ships nothing, so CI fails any PR that changes `plugins/<p>/**` without bumping that plugin's `version`. CI also runs `claude plugin validate --strict`, a smoke install in an isolated `CLAUDE_CONFIG_DIR`, and a provenance check on vendored skills.
- Semver: major renames or removes a skill or Principle, or changes the Project setup contract in a way that requires re-running setup; minor adds a skill, Principle or hook, or changes behavior (including Community skill updates); patch fixes without behavior change. Plugins stay at `0.x` until the v1 spec is built.
- Each plugin keeps a `CHANGELOG.md` (Keep a Changelog) updated in the bump PR, with migration steps for majors. CI tags each release as `<plugin>--v<X.Y.Z>` on merge, which also allows an emergency pin.
- `setup-ai-foundation` writes `extraKnownMarketplaces` and `enabledPlugins` into the Project's `.claude/settings.json`.
