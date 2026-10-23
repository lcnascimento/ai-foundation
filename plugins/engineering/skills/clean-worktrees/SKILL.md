---
name: clean-worktrees
description: Remove the worktrees in `.claude/worktrees/` whose branch is merged, with their branches. Use before creating a worktree for new work, after a PR merges, or when asked to clean up worktrees or branches.
---

Run the script from the user's checkout or any of its worktrees:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/clean-worktrees.py"
```

It fetches `origin` with `--prune` and prints one line per worktree in `<checkout>/.claude/worktrees/`:

- `removed`: the branch passed the git guardrail's merge proof (its tip is in `<remote>/<default>`, or is the head of a merged PR/MR), so its worktree and branch are gone.
- `skip`: uncommitted changes, untracked files or an open PR/MR. The worktree holds live work.
- `keep`: anything else, with the reason (no merged PR, commits not on the remote, detached HEAD).

Report the lines to the user as the script printed them. Done when every worktree is accounted for. Leave `skip` and `keep` worktrees in place: a `keep` whose merge the user confirms, they remove themselves.
