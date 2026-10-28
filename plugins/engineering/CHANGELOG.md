# Changelog

All notable changes to the `engineering` plugin. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versioning rules of
[ADR-0006](../../docs/adr/0006-projects-track-main-without-pins.md): major renames or removes a skill or
Principle, or changes the Project setup contract; minor adds a skill, Principle or hook, or changes behavior
(including Community skill updates); patch fixes without behavior change.

A major entry always carries a **Migration** section with the steps to take in each Project (usually:
re-run `/setup-ai-foundation`).

## [0.11.0] - 2026-10-27

### Added

- `scripts/worktree.sh`: `add <id> [--base <ref>] [--reset]` creates `<checkout>/.claude/worktrees/<id>` on
  branch `<id>` (from `origin`'s default branch, freshly fetched, when `--base` is left out), copies the ignored
  files listed in `.worktreeinclude` from the checkout without overwriting any, and runs the **Setup** commands
  of `docs/agents/environment.md`, so a new worktree is ready for the tests. A rerun completes an existing
  worktree; `--reset` recreates the branch from the base and refuses a worktree with uncommitted changes.
  `remove <id>` refuses uncommitted changes or a branch not merged into the current HEAD (or its upstream),
  leaving both in place, and is idempotent. It has no force mode: forced removal stays the user's, as the git
  guardrail requires.
- `project-files.md`: an optional **Setup** section in `docs/agents/environment.md`, with the commands that
  prepare a fresh checkout.

### Changed

- `implement` and `implement-spec` create their worktrees with `worktree.sh add`, retry a ticket with
  `add --reset`, and `implement-spec` removes merged ticket worktrees with `worktree.sh remove`.
  `clean-worktrees` is unchanged: its guardrail merge proof also covers squash merges, which `remove`'s
  `git branch -d` rule does not.

## [0.10.1] - 2026-10-23

### Fixed

- `implement-spec`: the PR leaves draft only in step 8, once every ticket is complete and the verify and
  code-review fixes are merged, never earlier to get checks on a merge. A check skipped because the PR is a
  draft, or no workflow run on a draft, is no longer read as a green **CI gate**.

## [0.10.0] - 2026-10-23

### Added

- `clean-worktrees`: a script that fetches `origin --prune` and removes each worktree in `.claude/worktrees/`
  whose branch passes the git guardrail's merge proof, with its branch, and reports the ones it skips (live
  work, open PR) or keeps (merge not proven). Needs `foundation` 0.7.0, whose guardrail it imports.

### Changed

- `implement` and `implement-spec` call `clean-worktrees` before creating their worktrees and point to it in
  their final message; `implement-spec` step 10 cleans up with it.

## [0.9.0] - 2026-10-23

### Changed

- `implement-spec`: each merge to the integration branch passes a local **merge gate** (the local gate commands
  of `docs/agents/forge.md`, needs `foundation` 0.6.0 to declare them) instead of waiting for the remote CI,
  so merges no longer queue behind a CI run each. The PR stays in draft until all tickets are merged, then is
  marked ready and its CI runs once as the **CI gate**. The CI gate waits for a workflow run created after the
  push or the `gh pr ready`, so a draft run's skipped checks are never read as green. On a red check the PR
  stays ready while the fix goes through, and moves back to draft only on a `BLOCKED` stop.
- `implement`: opens its PR ready for review, never as a draft, so its CI runs when the workflows skip drafts.

## [0.8.0] - 2026-10-22

### Changed

- `implement` and `implement-spec` name every branch and worktree directory after its issue identifier in
  lowercase (`abc-12`), with worktrees in `.claude/worktrees/` of the user's checkout. `implement` with a
  ticket now works in a worktree of its own instead of the current branch.
- `implement-spec` creates each implementer's worktree itself, at the integration branch tip, instead of
  using `isolation: "worktree"`; the implementer no longer runs `git switch -C`.
- Both move issues through the work lifecycle of `docs/agents/issue-tracker.md` (needs `foundation` 0.4.0):
  start when work begins, hand off for review when a ticket's merge is green or the PR is ready, and close on
  the PR's merge, whose body now always closes the spec and every ticket, or when the user approves the work
  in the session.

## [0.7.0] - 2026-10-21

### Changed

- `implement-spec`: the leader passes each implementer the integration branch and its own branch name, and the
  implementer starts with `git switch -C <its branch> <integration branch>` instead of resetting onto the
  integration branch, which the git guardrail denies. The leader removes each worktree and branch once its
  merge is done, whatever the CI gate's verdict, and stays on the integration branch so `git branch -d` sees
  the merge; the final cleanup only sweeps what is left.

## [0.6.0] - 2026-10-21

### Changed

- `implement-spec`: the merger pushes the integration branch after each merge and waits for the PR's CI on
  the pushed commit; a red check blocks the next merge until a fix, merged through the same gate, turns it
  green. The draft PR now always opens after the first merge, since its CI is the gate. Merges and the final
  push share one CI gate routine, which reruns failed jobs once before calling a check red.

## [0.5.0] - 2026-10-21

### Changed

- `implement-spec`: the leader reads the spec from the issue tracker once, saves it with its comments as
  `spec.md` in a notes directory outside the repo, and passes that path to every subagent, which reads its
  own ticket from the tracker and the spec only from the file. Progress on the spec goes in comments; the
  spec issue itself is touched only to change its state.

## [0.4.0] - 2026-10-18

### Changed

- `implement-spec` and `implement`: when they open a PR, they wait for its CI and fix failing checks until
  every check on the pushed head commit is green; `implement-spec` marks the PR ready only then, and stops
  under `know-when-to-stop` with the PR in draft when the same failure returns.

## [0.3.0] - 2026-10-16

### Added

- Principles: `earn-every-comment` (Custom, ADR-0013), the 20th engineering Principle. A comment, doc
  comment or lint suppression survives only on a closed exception list; everything else is deleted,
  reshaped into code, or encoded as a test, type or lint.

### Changed

- `code-review` is now derived from mattpocock: its smell baseline adds Fowler's **Comments**, the one
  hard violation of the baseline, judged against `earn-every-comment`.
- `golang`: the comment norm points to `earn-every-comment` instead of restating a looser rule.

## [0.2.0] - 2026-10-10

First usable release of the v1 spec (AI-36).

### Added

- Principles: the `principles` skill holds the full text of 19 engineering Principles in `references/`
  (11 engineering + 8 adaptable, Community and unchanged), loaded with `engineering:principles <name>`,
  and a Principles index hook on `SessionStart` and `SubagentStart` (ADR-0004).
- `verify` (Custom, ADR-0011): layered self-check (static, tests, runtime) before declaring work done,
  driven by the Project's `verify.md` and `environment.md`, with a `make format` / `make lint` /
  `make test` default; reports a `Verification` block.
- `golang` and `nextjs` (Custom, rewritten from several Upstreams, ADR-0010): stack skills that decide where
  code goes and at which level to test it.
- `how`, `why`, `teach`, derived from pstack, using the native subagent `model` field.
- `to-spec`, derived from mattpocock: records the agreed interfaces and seams in the spec, consulting
  `codebase-design` and running design-it-twice when an interface is open.
- `implement`, `implement-spec`, derived from mattpocock: cite `engineering:verify` and then
  `engineering:code-review` by qualified name, never the native `/code-review` (ADR-0008).
- `improve-codebase-architecture`, derived from mattpocock: hands ADRs to `foundation:documentation`.
- Community skills vendored with provenance (ADR-0001): `to-tickets`, `triage`, `tdd`, `code-review`,
  `codebase-design`, `diagnosing-bugs`, `resolving-merge-conflicts`, `pr`.
- Dependencies on `foundation` and the official `context7` plugin.
