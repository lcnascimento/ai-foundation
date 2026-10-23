---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
license: MIT
metadata:
  upstream: mattpocock/skills
  path: skills/engineering/implement/SKILL.md
  sha: 49dd158d1076134a641b33efb035946536778336
  status: derived
---

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask. Then:

- move the ticket to the **start** status of the work lifecycle in `docs/agents/issue-tracker.md`;
- work in a worktree of its own, outside the user's checkout, with the branch and the worktree directory both named after the ticket identifier in lowercase (`abc-12`): `git worktree add .claude/worktrees/abc-12 -b abc-12 <default branch>`. Run every command of this work from that worktree.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "engineering:verify" to verify the work, then with "engineering:code-review" to review it. If you open a PR, put the `Verification` block in its body.

Commit your work to the current branch (the ticket's branch, when there is a ticket).

If you open a PR, open it ready for review, never as a draft, so its CI runs even when the workflows skip draft PRs. Push and wait for its checks with the checks command in `docs/agents/forge.md` (`gh pr checks --watch` on GitHub). The work is done only when CI is **green**: every check reported on the pushed head commit has passed or was skipped by its own workflow condition, none pending, failed or cancelled. When a check goes red, read the failing run with the logs command in `docs/agents/forge.md`, fix the cause in the code under test, push and wait again; when the same failure comes back after a fix, stop under `know-when-to-stop`.

When the work is done, move the ticket to the **hand off for review** status, and put a closing line for it in the PR body, as the work lifecycle's **approval** says. Close the ticket yourself only when the user approves the work in the session.
