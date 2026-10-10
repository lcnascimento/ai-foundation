# Section: issue-tracker

Points the Project at its own Linear workspace through a per-Project MCP server authenticated by a per-Project key, and writes the tracker and triage files the Community skills read (ADR-0002, ADR-0003, ADR-0007, ADR-0012).

## Runs when

Always. Linear is the only tracker.

## Detect

- `.mcp.json`: the server whose `url` is on `mcp.linear.app`. Its key is `{{server}}`; with none, `{{server}}` is `linear`.
- `docs/agents/issue-tracker.md`: its `team **<name>** (key \`<KEY>\`)` line is the previous team answer.
- `.envrc` and `.gitignore`: whether they exist and whether `.env` is already ignored (`git check-ignore -q .env`).

## Ask

The Linear team that receives this Project's issues, as name and key. Recommend the previous answer, else `Engineering`/`ENG` when `engineering` is enabled; otherwise ask for the team of the Project's domain.

## Render

**`.mcp.json`**, merged JSON. Fragment:

```json
{
  "mcpServers": {
    "{{server}}": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp",
      "headers": { "Authorization": "Bearer ${LINEAR_API_KEY}" }
    }
  }
}
```

It shares the official `linear` plugin's endpoint, so it replaces that plugin's server in this Project, and the tools become `mcp__{{server}}__*`. `${LINEAR_API_KEY}` stays literal in the file; Claude Code expands it from the environment.

**`.envrc`**, ensured line:

```
dotenv_if_exists .env
```

**`.gitignore`**, ensured line, only when `git check-ignore -q .env` fails:

```
.env
```

**`docs/agents/issue-tracker.md`**, owned Markdown, with `{{server}}`, `{{team_name}}` and `{{team_key}}` filled:

```markdown
# Issue tracker: Linear

Issues and specs for this Project live in Linear, team **{{team_name}}** (key `{{team_key}}`), in this Project's own Linear workspace. Use the `{{server}}` MCP server's tools (`mcp__{{server}}__*`) for all operations; never the forge's issue tracker. The server authenticates with `LINEAR_API_KEY` from this Project's `.env`, so it reaches only this Project's workspace.

## Conventions

- **Create an issue**: `save_issue` with `team: "{{team_name}}"`, `title`, `description` (Markdown, literal newlines). Set `project` only when the work belongs to a Linear project (a finite deliverable); there is no catch-all project.
- **Read an issue**: `get_issue` with the identifier (e.g. `{{team_key}}-12`), plus `list_comments` for the thread.
- **List issues**: `list_issues` with `team`, `label`, `state`, `parentId`, `assignee` filters as needed.
- **Comment**: `save_comment` on the issue.
- **Labels**: `save_issue` with `addLabels` / `removeLabels`. Labels live at workspace level, lowercase. Grouped labels are named without a prefix: `type` (`bug`, `feature`, `improvement`, `chore`), `triage` (see `docs/agents/triage-labels.md`), `document` (one per Document type: `adr`, `tutorial`, `how-to`, `reference`, `explanation`). An issue that delivers a document carries `document:<type>` instead of a `type` label. If a label doesn't exist yet, create it at workspace level with `save_issue_label`.
- **Close**: `save_issue` with `state: "Done"` (or `"Canceled"` for won't-do), after commenting the reason.

Refer to issues by title in prose; the identifier (`{{team_key}}-12`) and URL ride inside the link.

## When a skill says "publish to the issue tracker"

Create a Linear issue in team {{team_name}}.

## When a skill says "fetch the relevant ticket"

`get_issue` + `list_comments` on the identifier.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **sub-issues** as tickets.

- **Map**: one issue labelled `wayfinder:map`, holding the Destination / Notes / Decisions-so-far / Not-yet-specified / Out-of-scope body.
- **Child ticket**: a Linear sub-issue of the map (`save_issue` with `parentId: <map identifier>`). Labels: `wayfinder:<type>` (`research` / `prototype` / `grilling` / `task`), flat and prefixed. Create missing `wayfinder:*` labels at workspace level with `save_issue_label` on first use.
- **Document ticket**: a child labelled `document:<type>` delivers that document. Resolve it by writing the document with `foundation:documentation` into the docs backend (`docs/agents/domain.md`), and link the document from the resolution comment.
- **Blocking**: Linear's native **blocks / blocked by** relations, which are visible in the UI. Add an edge with `save_issue` on the child: `blockedBy: [<blocker identifier>]`. A ticket is unblocked when every blocker is in a completed or canceled state.
- **Frontier query**: `list_issues` with `parentId: <map>` and open states. Drop any with an assignee, or with an open blocker (check via `get_issue` relations). First in map order (creation order) wins.
- **Claim**: `save_issue` with `assignee: "me"`, the session's first write.
- **Resolve**: `save_comment` with the answer, then `save_issue` with `state: "Done"`, then append a context pointer (gist + link) to the map's Decisions-so-far (`save_issue` with a `patch` append on the map).
```

**`docs/agents/triage-labels.md`**, owned Markdown, no placeholders:

```markdown
# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this Project's issue tracker: the children of the single-select `triage` label group in Linear.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

The two category roles map to children of the single-select `type` label group:

| Category in mattpocock/skills | Label in our tracker |
| ----------------------------- | -------------------- |
| `bug`                         | `bug`                |
| `enhancement`                 | `feature`            |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from these tables.
```

## Agent skills entries

```markdown
### Issue tracker

Linear, team {{team_name}} (`{{team_key}}`), through the `{{server}}` MCP server. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles under the `triage` label group, names unchanged. See `docs/agents/triage-labels.md`.
```

## Checklist

- A Linear workspace for this Project, with the team {{team_name}} (`{{team_key}}`).
- The team's workflow: Backlog → Todo → In Progress → In Review → Done, plus Canceled and Duplicate.
- A Linear personal API key created in that workspace, stored as `LINEAR_API_KEY=<key>` in this Project's `.env` (never committed).
- For cloud sessions: `LINEAR_API_KEY` set on this Project's cloud environment.
