---
name: address-pr-feedback
description: Address the feedback on the current branch's PR (red checks, a failed Sonar quality gate, unresolved review threads, new comments), fix it on that branch and answer every thread. Use when a PR's CI goes red, a review or comment lands on it, or you are woken up on a PR.
---

Work on the PR of the current branch, in the current worktree. Commit on this branch only: no new branch, no new worktree, no force-push. The forge and its commands are in `docs/agents/forge.md`; the work lifecycle roles (**start**, **hand off for review**) are in `docs/agents/issue-tracker.md`. The GitHub commands for each step are in [references/github.md](references/github.md); on another forge, use its equivalent.

## 1. Find the PR and its issue

Find the open PR whose head is the current branch. With none, there is no feedback to address: say so and stop.

The PR's **issue** is the one whose identifier the branch name carries (`hlb-166`, `luis/hlb-166-afk-mode`), else the issue of the PR body's first closing line (`Closes HLB-166`). When the PR delivers a Spec, its issue is the Spec. Move the issue to **start**. Leave every other issue the PR closes in the state it has: a Ticket that is integrated or done stays so, and nothing here reopens it.

## 2. Collect the feedback

Wait until no check on the PR's head commit is pending, so the set of red checks is complete. Then collect every **item**:

- each failed or cancelled check, with its failing logs (the logs command in `docs/agents/forge.md`). A Sonar check is red when its quality gate failed: read the failed conditions and the new issues from its check-run summary or its PR comment;
- each unresolved review thread whose last comment is not yours. A thread you answered last waits on the reviewer, so it is not an item;
- each PR comment and review body written by someone else after the last push: the creation time of the earliest check suite on the head commit, which the forge creates when the commit is pushed. With no check suite on it, use the head commit's date. A commit's own date is when it was made, not pushed, so it never stands in when a check suite exists.

The step is done when every item has its full text, its author and, for a thread, its file and line. With no item, move the issue to **hand off for review** and stop.

## 3. Decide each item

Give every item one **verdict**:

- **fix**: the feedback is right and clear. Change the code.
- **decline**: the feedback asks for something out of scope or already handled. Change nothing, and give the reason.
- **ask**: the feedback is ambiguous, so two readings lead to different changes. Change nothing for it, and ask the question that settles it.
- **argue**: you disagree after reading the code it points at. Change nothing for it, and give the counter-argument with its evidence.

A red check always gets **fix**: it turns green only through a fix in the code under test, as in `engineering:verify` step 3, never by skipping, muting or loosening the check.

## 4. Fix, verify and push

Fix every **fix** item on the current branch. Commit with the convention in `docs/agents/forge.md`, and cite the PR's issue in each commit (a `Refs: HLB-166` footer), so the history ties back to the Spec. Note the SHA that fixes each item.

Call the Skill tool with `engineering:verify`, and update the PR body's `Verification` block when it has one. Push the branch. Leave the PR's draft state as it is.

## 5. Wait for the CI verdict

Wait for the CI verdict on the pushed SHA, `green` or `red`:

1. Note the pushed SHA and the time of the push. Wait until a workflow run on that SHA was created after that time, then wait for its checks with the checks command in `docs/agents/forge.md`. Run it in the background when it can outlast the shell timeout. Once every check has finished, look again a minute later and wait again if new checks showed up. No run on the SHA a minute after the push means no workflow matched the change.
2. It is `green` when every check on the SHA has passed, or was skipped by its own workflow condition. Pending, failed and cancelled checks are not green.
3. When a check goes red, rerun its failed jobs once and wait again, so a flaky check doesn't block. A check with no workflow run, such as Sonar's, has nothing to rerun: its red is final. Red again is `red`: fix it as a new **fix** item, back through step 4. When the same failure comes back after a fix, stop under `know-when-to-stop` and report the `BLOCKED/TRIED/NEED` block with the failing check and its logs, leaving the issue in **start**.

## 6. Answer every item

Reply in the thread of each review-thread item, in the Project's language:

- **fix**: the SHA that fixes it, and one line on what changed;
- **decline**: the reason;
- **ask**: the question;
- **argue**: the counter-argument and its evidence.

Leave every thread unresolved: the reviewer decides when the conversation ends. Answer the PR comments and review bodies the same way, in one PR comment that quotes each one. The step is done when every item from step 2 has its answer.

## 7. Hand off

Move the PR's issue to **hand off for review**. Never close it: the PR's merge is the approval.
