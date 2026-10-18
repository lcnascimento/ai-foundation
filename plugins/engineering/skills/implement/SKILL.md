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

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "engineering:verify" to verify the work, then with "engineering:code-review" to review it. If you open a PR, put the `Verification` block in its body.

Commit your work to the current branch.

If you open a PR, push and wait for its checks with the checks command in `docs/agents/forge.md` (`gh pr checks --watch` on GitHub). The work is done only when CI is **green**: every check reported on the pushed head commit has passed or was skipped by its own workflow condition, none pending, failed or cancelled. When a check goes red, read the failing run with the logs command in `docs/agents/forge.md`, fix the cause in the code under test, push and wait again; when the same failure comes back after a fix, stop under `know-when-to-stop`.
