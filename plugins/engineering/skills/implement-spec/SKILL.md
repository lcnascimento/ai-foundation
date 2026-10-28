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

Every branch and worktree directory is named after its issue identifier in lowercase (`abc-12`): the integration branch after the spec, each implementer's branch after its ticket. Worktrees live in `<checkout>/.claude/worktrees/`, where `<checkout>` is the absolute path of the user's checkout. Create and remove them with the **worktree script**, `bash "${CLAUDE_SKILL_DIR}/../../scripts/worktree.sh"`: `add <id>` creates the branch and its worktree, copies the ignored files listed in `.worktreeinclude` from the checkout, runs the **Setup** commands of `docs/agents/environment.md` and prints the worktree's path last; `remove <id>` refuses uncommitted changes or a branch not merged into the current HEAD, and otherwise removes the worktree and the branch. Issues move through the **work lifecycle** in `docs/agents/issue-tracker.md` (**start**, **hand off for review**, **close**).

**Implementer subagents** should be run in the background where possible for maximum concurrency.

## Steps

1. Call the Skill tool with `engineering:clean-worktrees`, so merged work from earlier specs leaves no worktree behind. Create a **notes directory** outside the repo, accessible by all future subagents. Read the spec from the issue tracker once, with its comments, and save it there as `spec.md`; from then on, read the spec from that file, never from the tracker. If you edit the spec in the tracker, rewrite `spec.md` at once. Read the tickets to understand the task graph. Move the spec to **start**.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Pass it the path to `spec.md`. Ensure the exploration subagent can save files - it should save its markdown notes in the notes directory. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create the integration branch in its own worktree (**worktree script** `add <spec id>`, which fetches `origin` and starts at its default branch), and never switch the user's checkout to it: the user keeps working there. Run every git command on the integration branch from that worktree (merges, pushes, `git branch -d`, so it sees each merged branch as merged in step 5), and pass its path to every **merger subagent**. Open a draft PR after the first merge in step 5 (a branch with no commits ahead of main can't open one), with a closing line for the spec and for every ticket, as the work lifecycle's **approval** says. The PR stays in draft until step 8, once every ticket is complete and step 7's fixes are merged, where its CI runs as the **CI gate**. Never mark it ready earlier, not even to get checks on a merge.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Create both yourself, starting at the integration branch tip: **worktree script** `add <ticket id> --base <integration branch> --reset` (`--reset` also moves the branch of a previous attempt back to the tip, in its existing worktree, and refuses one with uncommitted changes). Move the ticket to **start**, then launch the subagent without `isolation`, passing it the path to `spec.md`, its ticket ID, its worktree path and the integration branch name. Each implementer subagent:
   - runs every command from its worktree, and changes nothing outside it;
   - reads its own ticket from the issue tracker and the spec from `spec.md`, never from the tracker;
   - calls the Skill tool with `tdd` to build the ticket;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**, working in the integration worktree, which runs the **merge gate** on the merge and reports its verdict without fixing anything. Merge one branch at a time, and start the next merge only on `green`. On `green`, move the ticket to **hand off for review**. Handle `red` as the **merge gate** says. A red the tickets expect does not block the next merge: the batches of a wide refactor that `to-tickets` sequenced to turn green only at their integrate ticket. Once the **merger subagent** has merged a branch, whatever the verdict, remove its worktree and branch with **worktree script** `remove <ticket id>`, run from the integration worktree.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

7. Once all tickets are complete, call the Skill tool with `engineering:verify` and then with `engineering:code-review` on the integration branch. Fix all issues raised by the verification and the code review in a single **implementer subagent**. Put the `Verification` block in the PR body.

8. Mark the PR ready for review (`gh pr ready` on GitHub), so its CI runs even when the workflows skip draft PRs, then run the **CI gate** on the integration branch, handling `red` as it says. This is the spec's one remote CI run, plus one per fix.

9. Once the PR's CI is green, move the spec to **hand off for review**. The work is done only when the PR's CI is green. The PR's merge closes the spec and its tickets; when the user approves the work in the session instead, close the spec and every ticket yourself.

10. Call the Skill tool with `engineering:clean-worktrees` to clean up the **implementer subagent** worktrees and branches still left. The branches of abandoned tickets, or of **implementer subagents** that failed before a merge, have no proven merge, so it keeps them: list them for the user with the commands that remove them. The integration worktree stays until the PR merges; in your final message, tell the user that `/engineering:clean-worktrees` then removes it and its branch.

## Merge gate

The **merge gate** checks one merge locally, without waiting for the forge, `green` or `red`:

1. From the integration worktree, run each command of the local gate in `docs/agents/forge.md`, in order. With no local gate listed there, a clean merge is `green`, and the **CI gate** in step 8 is the merge's first check.
2. The gate is `green` when every command exits 0. When one fails, run it once more, so a flaky test doesn't block. Failing again is `red`, reported with the command and its output.
3. On `green`, push the integration branch, and don't wait for its CI.

On `red`, fix the cause in a new **implementer subagent**, whose work goes back through a **merger subagent** and the **merge gate** like any ticket. When the same failure comes back after a fix, stop under `know-when-to-stop` and report the `BLOCKED` block with the failing command and its output.

## CI gate

The **CI gate** waits for the PR's CI verdict on the integration branch's head commit, `green` or `red`:

1. Push the integration branch and note the pushed SHA, and the time of the push or of `gh pr ready`, whichever came last.
2. Wait until the PR's head commit is that SHA and a workflow run on it was created after that time (`gh run list --commit <sha> --json createdAt` on GitHub), so the checks of an earlier draft run aren't read as the verdict. Then wait for its checks with the checks command in `docs/agents/forge.md` (`gh pr checks --watch` on GitHub). Run it in the background when it can outlast the shell timeout. Workflows register at different times, so once every check has finished, look again a minute later and wait again if new checks showed up. No workflow run created on the SHA after that time, a minute later, means no workflow matched the change, and the gate is `green`, but only on a ready PR: on a draft, it means nothing ran.
3. The gate is `green` when every check on the SHA has passed, or was skipped by its own workflow condition. Pending, failed or cancelled checks are not green, nor is a check skipped because the PR is a draft.
4. When a check goes red, rerun the failed jobs of each failed run once (`gh run rerun <run-id> --failed` on GitHub) and wait again, so a flaky check doesn't block. Red again is `red`, reported with the failing check and its logs, read with the logs command in `docs/agents/forge.md` (`gh run view --log-failed` on GitHub).

On `red`, fix the cause in a new **implementer subagent**, whose work goes back through a **merger subagent**, the **merge gate** and the **CI gate**. The PR stays ready meanwhile, so each push starts its CI. A check turns green only through a fix in the code under test, as in `engineering:verify` step 3. When the same failure comes back after a fix, stop under `know-when-to-stop`: move the PR back to draft (`gh pr ready --undo` on GitHub) and report the `BLOCKED` block with the failing check and its logs.
