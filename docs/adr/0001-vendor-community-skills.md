# Vendor Community skills instead of depending on their upstream plugins

Community skills are copied into `plugins/<plugin>/skills/<name>/`, pinned to an Upstream commit recorded in the `SKILL.md` frontmatter (`license`, `metadata.upstream`, `metadata.path`, `metadata.sha`, `metadata.status`), with the Upstream `LICENSE` copied alongside, and updated by hand. Depending on the upstream plugin (e.g. `mattpocock-skills`) was rejected: a dependency pulls the whole plugin (dozens of skills, including in-progress ones) into the skill listing budget, lets upstream changes land unreviewed (e.g. the `CONTEXT.md` → `GLOSSARY.md` rename), and leaves two copies of the same skill competing for routing. Vendoring a skill also vendors the skills it invokes. Editing a vendored copy turns it into a derived Custom skill (`metadata.status: derived`).

## Consequences

- MCP servers are never plugin dependencies: Project setup writes them into the Project's `.mcp.json` (`linear`, and `notion` with that docs backend), named per Project so each one reaches only its own workspace. An MCP is configuration pointing at an endpoint, with nothing to curate. Depending on the official plugins (`linear@claude-plugins-official`, `notion@claude-plugins-official`) was dropped: the dependency re-enabled them at user scope on every plugin load, so a user who removed them got them back, and their single user-scope sign-in reached the same workspace from every Project, against ADR-0003.
- The Marketplace is the single source of skills in Projects: once a skill is vendored, its upstream plugin is uninstalled there. Plugins used only to build this repo stay in this repo's project scope.
- Updates reach Projects only with a plugin `version` bump.
