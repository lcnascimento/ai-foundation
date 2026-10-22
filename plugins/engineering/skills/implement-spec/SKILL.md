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

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers. Report progress on the spec as comments, and touch the spec issue itself only to change its state.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

## Steps

1. Create a **notes directory** outside the repo, accessible by all future subagents. Read the spec from the issue tracker once, with its comments, and save it there as `spec.md`; from then on, read the spec from that file, never from the tracker. If you edit the spec in the tracker, rewrite `spec.md` at once. Read the tickets to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Pass it the path to `spec.md`. Ensure the exploration subagent can save files - it should save its markdown notes in the notes directory. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create the integration branch in its own worktree, outside the user's checkout (`git worktree add <path> -b <integration branch> <default branch>`), and never switch the user's checkout to it: the user keeps working there. Run every git command on the integration branch from that worktree (merges, pushes, `git branch -d`, so it sees each merged branch as merged in step 5), and pass its path to every **merger subagent**. Open a draft PR after the first merge in step 5 (a branch with no commits ahead of main can't open one), marked as closing the spec and tickets when the issue tracker closes work through PRs. The PR is what starts the CI behind the **CI gate**.

4. Use **implementer subagents** to implement each ticket, each in its own worktree (`isolation: "worktree"`) on its own branch. Pass each one the path to `spec.md`, its ticket ID, the integration branch name and the name of its own branch. Before retrying a ticket, remove the worktree of the previous attempt. Each implementer subagent:
   - reads its own ticket from the issue tracker and the spec from `spec.md`, never from the tracker;
   - starts with `git switch -C <its branch> <integration branch>`, since the worktree starts from the default branch;
   - calls the Skill tool with `tdd` to build the ticket;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**, working in the integration worktree, which runs the **CI gate** on the merge and reports its verdict without fixing anything. Merge one branch at a time, and start the next merge only on `green`. Handle `red` as the **CI gate** says. A red the tickets expect does not block the next merge: the batches of a wide refactor that `to-tickets` sequenced to turn green only at their integrate ticket. Once the **merger subagent** has merged a branch, whatever the verdict, remove its worktree and branch (`git worktree remove <path>`, `git branch -d <branch>`).

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

7. Once all tickets are complete, call the Skill tool with `engineering:verify` and then with `engineering:code-review` on the integration branch. Fix all issues raised by the verification and the code review in a single **implementer subagent**. Put the `Verification` block in the PR body.

8. Run the **CI gate** on the integration branch, handling `red` as it says. When the workflows skip draft PRs, mark the PR ready to start them, and move it back to draft (`gh pr ready --undo`) if a check goes red.

9. Mark the PR ready for review once its CI is green. If the issue tracker doesn't close work through PRs, resolve each ticket the way it closes work. The work is done only when the PR's CI is green.

10. Clean up the **implementer subagent** worktrees and branches still left: tickets abandoned, or **implementer subagents** that failed before a merge. The integration worktree stays until the PR merges; then remove it and its branch.

## CI gate

The **CI gate** pushes the integration branch and waits for the PR's verdict on that one commit, `green` or `red`:

1. Push the integration branch and note the pushed SHA.
2. Wait until the PR's head commit is that SHA, then wait for its checks with the checks command in `docs/agents/forge.md` (`gh pr checks --watch` on GitHub). Run it in the background when it can outlast the shell timeout. Workflows register at different times, so once every check has finished, look again a minute later and wait again if new checks showed up. No workflow run on the SHA a minute after the push (`gh run list --commit <sha>` on GitHub) means no workflow matched the change, and the gate is `green`.
3. The gate is `green` when every check on the SHA has passed, or was skipped by its own workflow condition. Pending, failed or cancelled checks are not green.
4. When a check goes red, rerun the failed jobs of each failed run once (`gh run rerun <run-id> --failed` on GitHub) and wait again, so a flaky check doesn't block. Red again is `red`, reported with the failing check and its logs, read with the logs command in `docs/agents/forge.md` (`gh run view --log-failed` on GitHub).

On `red`, fix the cause in a new **implementer subagent**, whose work goes back through a **merger subagent** and the **CI gate** like any ticket. A check turns green only through a fix in the code under test, as in `engineering:verify` step 3. When the same failure comes back after a fix, stop under `know-when-to-stop`: leave the PR in draft and report the `BLOCKED` block with the failing check and its logs.
