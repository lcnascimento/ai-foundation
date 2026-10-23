# Section: linear-statuses

Provisions the workflow statuses that the work lifecycle in `docs/agents/issue-tracker.md` moves issues through. It writes no file: its output is a status plan, shown like a diff and applied only after approval. Statuses are never renamed, moved or deleted.

## Runs when

Always, after linear-labels, whose workspace confirmation it reuses.

## Detect

- The tool `mcp__{{server}}__list_issue_statuses` in this session, and `LINEAR_API_KEY` in the environment or in `.env` (`grep -q '^LINEAR_API_KEY=' .env`, output discarded). When either is missing, skip the rest of this section and keep its checklist item open.
- Every status of team {{team_name}}: `list_issue_statuses` with `team: "{{team_name}}"`, noting each one's `name` and `type`.

## Ask

Nothing: the workspace was confirmed in linear-labels. When that confirmation was declined, skip the section.

## Desired statuses

| Status | Type |
| - | - |
| `In Progress` | `started` |
| `In Review` | `started` |
| `Done` | `completed` |

## Plan

Match each desired status against the team's statuses by name, case-insensitively. Classify it as:

- **ok**: a match of the right type, whatever its letter case. No call.
- **create**: `In Review` with no match. Create it with the **Missing status** command of `docs/agents/issue-tracker.md` (the rendered file, so `{{team_key}}` is filled).
- **conflict**: a match of the wrong type, a name several statuses share, or a missing `In Progress` or `Done`. Never changed; reported for the user to resolve in Linear, then re-run.

A run where every desired status is **ok** prints "statuses: no changes" and makes no call.

## Render

The plan, shown in step 3 next to the file diffs:

```
linear statuses (team {{team_name}})
  ok        In Progress (started)
  create    In Review (started, after the other started statuses)
  ok        Done (completed)
```

Step 4 applies the **create** line when the user approves it, then lists the statuses again and shows the plan once more: it must hold only **ok** and **conflict** lines.

## Agent skills entries

None. `docs/agents/issue-tracker.md` already describes the work lifecycle.

## Checklist

- Linear statuses provisioned for team {{team_name}}: run `/setup-ai-foundation` again after `/reload-plugins` when the `{{server}}` MCP server or `LINEAR_API_KEY` wasn't available during this run. Mark it done only when the last plan of this run held no **create** line.
- Each **conflict** status from the plan resolved in Linear.
