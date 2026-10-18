---
name: implement-spec
description: "Implement the result of /to-spec and /to-tickets in code."
disable-model-invocation: true
license: MIT
metadata:
  upstream: mattpocock/skills
  path: skills/engineering/implement-spec/SKILL.md
  sha: 49dd158d1076134a641b33efb035946536778336
  status: derived
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

The issue tracker should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

The goal is the entire spec implemented on a single **integration branch**, with every ticket resolved the way the issue tracker closes work.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

## Steps

1. Read the spec and tickets to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create the integration branch. If the issue tracker closes work through PRs, or the user asks for one, open a draft PR after the first merge in step 5 (a branch with no commits ahead of main can't open one), marked as closing the spec and tickets.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - calls the Skill tool with `tdd` to build the ticket;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

7. Once all tickets are complete, call the Skill tool with `engineering:verify` and then with `engineering:code-review` on the integration branch. Fix all issues raised by the verification and the code review in a single **implementer subagent**. If a draft PR exists, put the `Verification` block in its body.

8. If a draft PR exists, push the integration branch and drive the PR's CI to **green**: every check reported on the pushed head commit has passed. Pending, failed or cancelled checks are not green, and neither is "no checks reported" while the Project has CI config (the run has not started yet: wait and look again).
   - Wait for the checks with the checks command in `docs/agents/forge.md` (`gh pr checks --watch` on GitHub), confirming they belong to the head commit you pushed. Run it in the background when it can outlast the shell timeout.
   - When a check goes red, read the failing run with the logs command in `docs/agents/forge.md` (`gh run view --log-failed` on GitHub), fix the cause in a single **implementer subagent**, push, and wait again. A check turns green only through a fix in the code under test, as in `engineering:verify` step 3.
   - When the workflows skip draft PRs, mark the PR ready to start them, and move it back to draft (`gh pr ready --undo`) if a check goes red.
   - When the same failure comes back after a fix, stop under `know-when-to-stop`: leave the PR in draft and report the `BLOCKED` block with the failing check and its logs.

9. If a draft PR exists, mark it ready for review once its CI is green. Otherwise, resolve each ticket the way the issue tracker closes work, and report the integration branch. The work is done only when the PR's CI is green.

10. Clean up all **implementer subagent** worktrees.
