# Section: linear-labels

Provisions, through the Project's Linear MCP server, the workspace label taxonomy that `triage`, `to-tickets` and `wayfinder` apply (ADR-0003, ADR-0012). It writes no file: its output is a label plan, shown like a diff and applied only after approval. Labels are never deleted, and never renamed or moved without the change appearing in the plan.

## Runs when

Always, after issue-tracker, whose `{{server}}` it uses.

## Detect

- The tools `mcp__{{server}}__list_issue_labels` and `mcp__{{server}}__save_issue_label` in this session. When they're missing (the server was just added to `.mcp.json` and isn't loaded yet), skip the rest of this section and keep its checklist item open.
- The workspace the server reaches (`mcp__{{server}}__get_workspace` when available, else the team list). It must be this Project's workspace, never another Project's.
- Every workspace label, groups included: `list_issue_labels` with `includeGroups: true`, no `team`, `limit: 250`, following `cursor` until the last page. Note each label's `id`, `name`, whether it `isGroup`, its parent group when the listing shows one, and `retiredAt`/`archivedAt`.

## Ask

Confirm the workspace by name before planning: "Provision labels in the Linear workspace **<name>**?" On no, skip the section.

## Desired labels

All lowercase, at workspace level (no `teamId`):

| Label | Kind | Children |
| - | - | - |
| `type` | group, `singleSelect` | `bug`, `feature`, `improvement`, `chore` |
| `triage` | group, `singleSelect` | `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix` |
| `document` | group, `singleSelect` | one per enabled Document type: `adr`, `tutorial`, `how-to`, `reference`, `explanation`, plus any type an enabled Domain plugin declares |
| `wayfinder:map`, `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, `wayfinder:task` | flat, no group | none |

The `triage` children are exactly the five rows of `docs/agents/triage-labels.md`, in the same spelling; change one only together with the other.

## Plan

Match each desired label against the existing ones by name, case-insensitively, preferring a label already in the right group. Classify it as:

- **ok**: same name byte for byte, same kind, under the right group (or ungrouped for `wayfinder:*`), not retired or archived. No call.
- **create**: no match. `save_issue_label` with `name`, plus `isGroup: true, groupType: "singleSelect"` for a group or `parent: "<group name>"` for a child. Create groups before their children.
- **adopt**: a match that differs. Reuse its `id` and list each change, old → new: rename to lowercase (`Bug` → `bug`), move into the group (`parent`), restore a retired label (`restore_issue_label`). One `save_issue_label` with `id` and only the changed fields.
- **conflict**: a match of the wrong kind (a plain label named `type`, a group named `bug`) or a name used by several labels. Never changed; reported for the user to resolve in Linear, then re-run.

When the listing doesn't show a label's parent, don't guess and don't re-save it: report it as **unverified** with a note to check its group in Linear.

Labels that aren't desired are left alone and not listed. A run where every desired label is **ok** prints "labels: no changes" and makes no call.

## Render

The plan, shown in step 3 next to the file diffs:

```
linear labels (<workspace name>)
  ok        triage/needs-triage
  create    group document (singleSelect)
  create    document/adr
  adopt     Bug → type/bug   (rename "Bug" → "bug", parent → type)
  conflict  type: existing plain label, expected a group
```

Step 4 applies the **create** and **adopt** lines the user approves, in plan order, then lists the labels again and shows the plan once more: it must hold only **ok**, **conflict** and **unverified** lines.

## Agent skills entries

None. `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md` already describe the taxonomy.

## Checklist

- Linear labels provisioned in this Project's workspace: run `/setup-ai-foundation` again after `/reload-plugins` when the `{{server}}` MCP server wasn't loaded during this run. Mark it done only when the last plan of this run held no **create** or **adopt** line.
- Each **conflict** or **unverified** label from the plan resolved in Linear.
