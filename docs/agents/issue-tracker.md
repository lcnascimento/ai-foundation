# Issue tracker: Linear

Issues and specs for this repo live in Linear, team **AI Foundation** (key `AI`), default project **Development**. Use the Linear MCP tools (`mcp__plugin_linear_linear__*`) for all operations; never the GitHub issue tracker.

## Conventions

- **Create an issue**: `save_issue` with `team: "AI Foundation"`, `project: "Development"`, `title`, `description` (Markdown, literal newlines).
- **Read an issue**: `get_issue` with the identifier (e.g. `AI-12`), plus `list_comments` for the thread.
- **List issues**: `list_issues` with `team`, `label`, `state`, `parentId`, `assignee` filters as needed.
- **Comment**: `save_comment` on the issue.
- **Labels**: `save_issue` with `addLabels` / `removeLabels`. If a label doesn't exist yet, create it first with `save_issue_label` (team-scoped).
- **Close**: `save_issue` with `state: "Done"` (or `"Canceled"` for won't-do), after commenting the reason.

Refer to issues by title in prose; the identifier (`AI-12`) and URL ride inside the link.

## When a skill says "publish to the issue tracker"

Create a Linear issue in team AI Foundation, project Development.

## When a skill says "fetch the relevant ticket"

`get_issue` + `list_comments` on the identifier.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **sub-issues** as tickets.

- **Map**: one issue labelled `wayfinder:map`, holding the Destination / Notes / Decisions-so-far / Not-yet-specified / Out-of-scope body.
- **Child ticket**: a Linear sub-issue of the map (`save_issue` with `parentId: <map identifier>`). Labels: `wayfinder:<type>` (`research` / `prototype` / `grilling` / `task`). Create missing `wayfinder:*` labels with `save_issue_label` on first use.
- **Blocking**: Linear's native **blocks / blocked by** relations, which are visible in the UI. Add an edge with `save_issue` on the child: `blockedBy: [<blocker identifier>]`. A ticket is unblocked when every blocker is in a completed or canceled state.
- **Frontier query**: `list_issues` with `parentId: <map>` and open states. Drop any with an assignee, or with an open blocker (check via `get_issue` relations). First in map order (creation order) wins.
- **Claim**: `save_issue` with `assignee: "me"`, the session's first write.
- **Resolve**: `save_comment` with the answer, then `save_issue` with `state: "Done"`, then append a context pointer (gist + link) to the map's Decisions-so-far (`save_issue` with a `patch` append on the map).
