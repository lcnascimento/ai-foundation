---
name: retro
description: "Conduct a retrospective on a coding session. Use when the user asks for a retro, or as the last step of an AFK session when `implement`, `implement-spec` or `address-pr-feedback` call it."
license: MIT
metadata:
  upstream: mattpocock/skills
  path: skills/engineering/retro/SKILL.md
  sha: 49dd158d1076134a641b33efb035946536778336
  status: derived
---

The user, or in AFK mode the skill that called you, has asked for a **retrospective**. You are suggesting improvements to the coding agent's **environment** to improve future runs.

## Steps

1. Call the Skill tool with `foundation:writing-for-agents` for the writing style guide.

2. Read the primary sources for the session the user specifies. This may mean searching through session logs on this machine. If the user doesn't specify a session, default to the current one.

3. Look for candidates for improvement in these categories.

- **Navigation**: how easy was it for the agent to find the right files? Are there hidden dependencies between files? Would a **navigation pointer** make it easier? _Use when_ the session took a long time to find a piece of information.
- **Automated checks**: are there automated checks that could catch errors the agent made? Linting, typing, tests, filesystem linters? Read the repo's own check command first (its `package.json`/build-tool `lint`/`check` scripts, its CI workflow), so a check that already exists but sits unwired or silently broken is the finding, not a reinvention. A repo with no **guardrail** (no pre-commit hook and no CI job running its lint/typecheck/test command) is itself a finding: an un-linted repo is a standing missed opportunity, not a neutral default. _Use when_ the agent made a mistake an automated check could have caught, or the repo has no guardrail at all.
- **Coding standards**: should the **reviewer agent** be given a new rule to enforce? Should an existing rule be removed or clarified? Classify the violation first: a **mechanical** one (a fixed syntactic pattern, a banned API, an import shape, a file-location rule) gets a deterministic check, full stop: a custom rule in the repo's own linter, a new pre-commit hook, or a new CI job, whichever the repo's language and existing guardrail make cheapest. Default to building the check over writing the rule. Reserve `CODING_STANDARDS.md` for genuine **judgement calls** (cross-file consistency, "matches the surrounding style," anything no guardrail could ever substitute for). _Use when_ the reviewer agent failed to catch a mistake.
- **Global AGENTS.md**: are there any steering instructions that should be moved to coding standards (or automated checks) instead? _Use when_ the AGENTS.md file is particularly large - in the repo OR the user's global scope.
- **Tool economy**: did the agent make expensive tool calls that could be streamlined? Is there any custom tooling (CLI's, MCP's) that is particularly token-inefficient? _Use when_ the agent made an expensive tool call.
- **No-ops**: look for instructions in steering files that don't modify the agent's behavior. _Use when_ the steering files are large and unwieldy.
- **Information access**: look for opportunities to increase the agent's access to information. Teeing dev server logs, readonly access to third-party services. _Use when_ a crucial piece of information was not available to the agent.

4. Present these candidates to the user, in order of severity. In AFK mode, file them instead, as **AFK mode** below says.

## AFK mode

AFK mode is on when `AI_FOUNDATION_AFK` is `1` (`printenv AI_FOUNDATION_AFK`). With the flag off, skip this section. With it on, the skill that called you passed the **origin issue** (the Spec or issue the session worked on) and its PR, if any. Step 4 becomes:

1. Keep at most 2 candidates, the most severe, and only from Automated checks, Navigation and Information access. With none left, stop: no issue, no comment.
2. For each candidate, search the issue tracker for an open issue that asks for the same change (`list_issues` with a `query` on its key terms). When one exists, comment the new evidence on it instead of creating an issue.
3. Otherwise, publish it to the issue tracker (`docs/agents/issue-tracker.md`):
   - status `Backlog`;
   - labels `improvement`, the `needs-triage` role of `docs/agents/triage-labels.md`, `retro`, and the `target` label naming the repo the change lands in: `ai-foundation` for a skill, hook or script of the ai-foundation plugins, else the Project's own repo. Create a missing label as `docs/agents/issue-tracker.md` says;
   - a `related` relation to the origin issue;
   - a description in the Project's language with the problem observed, the evidence (origin issue, PR, and the excerpt of the session that went wrong), the category and the proposed change.
4. Post one Retro comment on the origin issue, listing each issue created or commented on.

A failure here never changes the delivery: on any error, stop the retro and leave the origin issue, its status and the PR as they are.

## Reference

### Implementation vs Review

Remember that all work goes through two stages: implementation and review. The implementation agent has the most **context pressure**. They are responsible for exploration, writing code, and debugging failures.

The review agent has the least context pressure - it receives a diff, so no exploration needed. It often does not need to write code or debug.

This means that the review agent should be responsible for imposing coding standards, not the implementation agent.

### Files

You have access to several files in the repo:

- `CLAUDE.md`/`AGENTS.md`: these files are pushed to the context window of any agent working in this repo. They should be used incredibly sparingly, usually only for **navigation pointers** to other files.
- `CODING_STANDARDS.md`: this file is read during review, not implementation. Add **navigation pointers** to docs folders if the standards file gets more than 1,000 lines long.
- Docs: use docs as references files, pointed to by other files. Look for existing docs before writing new ones.
- Skills: use skills for docs (since their description goes into the agent's context window), or for user-invoked commands. Follow the advice in the `foundation:writing-for-agents` skill.
