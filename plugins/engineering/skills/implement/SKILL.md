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
