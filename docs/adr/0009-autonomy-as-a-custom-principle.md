# Agent autonomy ships as a Custom Principle, and merging stays human

Agents in v1 work "solo" by default in every session: they decide, proceed, and state each assumption in one line, as the Community Principle `never-block-on-the-human` already asks. Its counterpart is a new Custom Principle in `foundation`, `know-when-to-stop`, delivered through the Principles index (ADR-0004) like any other. It names the only three reasons to interrupt the human: an irreversible or outward-facing action (force-push, push or merge to the default branch, release or deploy, deleting data, messaging third parties, publishing), a dead end after exhausting every source (repeating the same failure twice counts as one), and an ambiguity about outcome or product direction that no reading or prototype can settle. When it stops, the agent raises everything at once in a `BLOCKED` / `TRIED` / `NEED` block, posted as a comment on the tracker ticket when no human is in the session. It must not invent values or turn a failing check green by deleting it, and it never asks what it can look up.

The AFK boundary for engineering is "PR In Review". Pushing the agent's own branch, opening a draft PR, marking it ready, and commenting on or moving Linear issues are all autonomous. Merging is always the human's.

Because only the index line is always in context, the Principle's `description` lists the three stops compactly, and `references/know-when-to-stop.md` holds the detail. The text is our own. The stop format credits `not-your-babysitter` (tech-leads-club, CC-BY-4.0) as inspiration, without copying from it.

## Considered Options

- **A Rule in `foundation`'s hook**: rejected. Autonomy is a development philosophy with a clear trigger, which is what the index is for, and the Principle reaches subagents through `SubagentStart` anyway.
- **Derive `never-block-on-the-human` and add the stops to its boundaries**: rejected. The two Principles fire on different triggers ("tempted to ask" vs "about to act irreversibly, or stuck"), and one trigger per index line recalled better in the ADR-0004 eval.
- **Vendor `poteto-mode` or `not-your-babysitter` as a mode**: rejected, like every mode in the v1 catalog. So were their autonomy levels (`paired` / `solo` / `heads-down`) and session overrides: the human changes posture in plain language, and native permission modes cover the harness side.
- **Allow merge on green CI**: rejected. Green is not the same as reviewed, and the human's merge is the one gate before work becomes shared.

## Consequences

- `foundation`'s `principles` skill now holds Community references, a derived one (`explain-the-number`), and a Custom one.
- v1 ships no custom subagents. `implement*` uses `general-purpose`, and the index brings autonomy to subagents.
- Where AFK sessions run (local worktrees, cloud sessions, Coder) is infrastructure, outside this spec.
- `foundation` also ships a Custom `PreToolUse` hook (matcher `Bash`) that hard-enforces the irreversible stops. It always denies, in interactive and AFK sessions alike, and points the agent to `know-when-to-stop`. It blocks force-pushes in any form, pushes to the default branch (resolved from `origin/HEAD`), PR/MR merges (`gh pr merge`, `glab mr merge`), `--no-verify`, and local destructive commands (`reset --hard`, `clean -f`, `branch -D`, `checkout .`/`restore .`, `stash drop`/`clear`). Commits on the default branch and pushes of the agent's own branch stay allowed. The Community `git-guardrails-claude-code` is not vendored, because it blocks every push. Forge branch protection remains the real guard for shared state and is a recommended item on the Project setup checklist.
- Plugins ship no lint/format hooks, and Project setup installs no pre-commit. CI is the deterministic gate.
