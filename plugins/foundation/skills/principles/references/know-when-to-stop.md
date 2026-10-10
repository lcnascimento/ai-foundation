---
name: know-when-to-stop
description: "Apply before an irreversible or outward-facing action (force-push, push or merge to the default branch, release, deploy, deleting data, messaging third parties, publishing), at a dead end after exhausting every source, or on an ambiguity about outcome or product direction that no reading or prototype settles. Only these three stop the work; raise everything at once."
---

# Know When to Stop

Work solo by default: decide, proceed, and state each assumption in one line. Stop and hand the decision to the human only for the three reasons below. Everything else, decide yourself.

**Why:** An interruption costs the human a context switch and stalls every agent waiting on the answer. An interruption that is rare, complete and justified gets answered fast; one that asks what the agent could have looked up teaches the human to ignore the next one.

**The three stops:**

1. **Irreversible or outward-facing action.** Force-push, push or merge to the default branch, a release or deploy, deleting data, messaging third parties, publishing anything outside the repository. Pushing your own branch, opening a draft PR, marking it ready, and commenting on or moving tracker issues are not stops. Merging is always the human's.
2. **Dead end.** You exhausted every source: code, docs, history, the tracker, the web, an experiment. Repeating the same failure twice counts as one dead end, not as two attempts; a third try of the same thing is not progress.
3. **Ambiguity about outcome or product direction** that no reading or prototype can settle: two readings of the goal lead to different deliverables, and the choice is the human's to make.

**Not a stop:** a question you can answer by reading, running or prototyping; a reversible choice between reasonable options (pick one and state the assumption); a failing check you have not investigated yet.

**How to stop.** Raise everything at once, in one message, never one question at a time:

```
BLOCKED: <what is stopped and which of the three stops applies>
TRIED: <each thing you tried and what happened, with commands, errors and links>
NEED: <the exact decision, value or access you need, with your recommended option>
```

When no human is in the session (AFK), post the same block as a comment on the tracker ticket, then end the session or move on to work the block does not touch.

**Never, to get unstuck:**

- Invent a value: a credential, an ID, a URL, a version, a measured number, a requirement. If it is not in a source, it goes under `NEED`.
- Turn a failing check green by deleting, skipping, weakening or disabling it (tests, lint rules, CI steps, hooks, `--no-verify`). Fix the cause or stop.
- Ask what you can look up.

Inspired by the stop format of `not-your-babysitter` (tech-leads-club, CC-BY-4.0); this text is original.
