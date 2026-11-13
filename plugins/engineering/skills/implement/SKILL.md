---
name: implement
description: "Implement a Spec or issue in code. Use when asked to implement a Spec or issue, or when one is delegated to you in an AFK session."
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
- call the Skill tool with `engineering:clean-worktrees`, so merged work from earlier tickets leaves no worktree behind;
- work in a worktree of its own (in AFK mode, the current one: see **Branch** below), outside the user's checkout, with the branch and the worktree directory both named after the ticket identifier in lowercase (`abc-12`): `bash "${CLAUDE_SKILL_DIR}/../../scripts/worktree.sh" add abc-12`, which starts it at `origin`'s default branch, sets it up as `docs/agents/environment.md` says, and prints its path last. Run every command of this work from that worktree.

Call the Skill tool with "tdd" where possible, at pre-agreed seams (in AFK mode, see **Seams** below).

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "engineering:verify" to verify the work, then with "engineering:code-review" to review it (in AFK mode, see **Review point** below). If you open a PR, put the `Verification` block in its body.

Commit your work to the current branch (the ticket's branch, when there is a ticket).

If the branch already has an open PR (`gh pr view` on GitHub), push to it instead of opening another. If you open a PR, open it ready for review, never as a draft, so its CI runs even when the workflows skip draft PRs. Push and wait for its checks with the checks command in `docs/agents/forge.md` (`gh pr checks --watch` on GitHub). The work is done only when CI is **green**: every check reported on the pushed head commit has passed or was skipped by its own workflow condition, none pending, failed or cancelled. When a check goes red, read the failing run with the logs command in `docs/agents/forge.md`, fix the cause in the code under test, push and wait again; when the same failure comes back after a fix, stop under `know-when-to-stop`.

When the work is done, move the ticket to the **hand off for review** status, and put a closing line for it in the PR body, as the work lifecycle's **approval** says. Close the ticket yourself only when the user approves the work in the session. In your final message, tell the user that once the PR merges, `/engineering:clean-worktrees` removes the ticket's worktree and branch.

## AFK mode

AFK mode is on when `AI_FOUNDATION_AFK` is `1` (`printenv AI_FOUNDATION_AFK`); the foundation plugin then injects an `# AFK mode` rule into the session. Decide it from the flag alone, never from whether the checkout is a linked worktree. With the flag off, skip this section. With it on, these rules replace the matching steps above:

- **Branch**: the current worktree and branch are the work branch, as the delegating agent opened them. Run every command from the current worktree, create no worktree or branch of your own for it, and never rename the current branch.
- **Seams**: the seams the Spec or the Ticket names count as confirmed with the user, so `tdd`'s confirmation is already met. Before the first test at a seam neither names, post it, with what it catches and what it misses, as an Assumption comment on the Ticket, and then treat it as confirmed.
- **Review point**: pass `engineering:code-review` the merge-base of the current branch with `origin`'s default branch as its fixed point (`git merge-base HEAD origin/<default branch>`, after `git fetch origin`).
- **Retro**: as the last step, after the Delivery comment and the move to **hand off for review**, or after the BLOCKED/TRIED/NEED comment when the session stops, call the Skill tool with `foundation:retro`, passing the ticket and its PR. A failure of the retro changes nothing in the delivery.
