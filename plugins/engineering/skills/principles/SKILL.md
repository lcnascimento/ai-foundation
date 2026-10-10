---
name: principles
description: Load the full text of an engineering Principle named in the Principles index before applying it. Pass the Principle name as argument, e.g. `engineering:principles prove-it-works`.
argument-hint: <principle-name>
---

Read `${CLAUDE_SKILL_DIR}/references/$ARGUMENTS.md` in full and apply it to the current work.

If the name doesn't match a file in `${CLAUDE_SKILL_DIR}/references/`, list that folder and pick the closest match.

In your final reply, cite each Principle that changed a decision and the specific choice it changed.
