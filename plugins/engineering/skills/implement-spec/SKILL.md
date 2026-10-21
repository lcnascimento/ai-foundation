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

3. Create the integration branch. Open a draft PR after the first merge in step 5 (a branch with no commits ahead of main can't open one), marked as closing the spec and tickets when the issue tracker closes work through PRs. The PR is what starts the CI behind the **CI gate**.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Pass each one the path to `spec.md` and its ticket ID. Each implementer subagent:
   - reads its own ticket from the issue tracker and the spec from `spec.md`, never from the tracker;
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - calls the Skill tool with `tdd` to build the ticket;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**, which runs the **CI gate** on the merge and reports `green`, or `red` with the failing check and its logs. Merge one branch at a time, and start the next merge only on `green`.
   - On `red`, the merger stops without fixing. Hand the failure to a new **implementer subagent** as a fix, which merges back through a merger and the CI gate like any ticket.
   - When the same failure comes back after a fix, stop under `know-when-to-stop` and report the `BLOCKED` block with the failing check and its logs.
   - A red the tickets expect, such as the batches of a wide refactor that promise green only at their integrate ticket, does not block the next merge.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

7. Once all tickets are complete, call the Skill tool with `engineering:verify` and then with `engineering:code-review` on the integration branch. Fix all issues raised by the verification and the code review in a single **implementer subagent**. Put the `Verification` block in the PR body.

8. Run the **CI gate** on the integration branch. On `red`, fix the cause in a single **implementer subagent** and run the gate again. A check turns green only through a fix in the code under test, as in `engineering:verify` step 3. When the same failure comes back after a fix, stop under `know-when-to-stop`: leave the PR in draft and report the `BLOCKED` block with the failing check and its logs.

9. Mark the PR ready for review once its CI is green. If the issue tracker doesn't close work through PRs, resolve each ticket the way it closes work. The work is done only when the PR's CI is green.

10. Clean up all **implementer subagent** worktrees.

## CI gate

The **CI gate** pushes the integration branch and waits for the PR's verdict on that one commit:

1. Push the integration branch and note the pushed SHA.
2. Wait until the PR's head commit is that SHA and checks are reported on it, then wait for them with the checks command in `docs/agents/forge.md` (`gh pr checks --watch` on GitHub). Run it in the background when it can outlast the shell timeout. When no check shows up, look for workflow runs on the SHA (`gh run list --commit <sha>` on GitHub): a run means CI hasn't reported yet, so wait and look again; no run means no workflow matched the change, and the gate is `green`.
3. When the workflows skip draft PRs, mark the PR ready to start them, and move it back to draft (`gh pr ready --undo`) once the verdict is in.
4. The gate is `green` when every check on the SHA has passed, or was skipped by its own workflow condition. Pending, failed or cancelled checks are not green.
5. When a check goes red, rerun the failed jobs once (`gh run rerun --failed` on GitHub) and wait again, so a flaky check doesn't block. Red again is `red`: read the failing run with the logs command in `docs/agents/forge.md` (`gh run view --log-failed` on GitHub).
