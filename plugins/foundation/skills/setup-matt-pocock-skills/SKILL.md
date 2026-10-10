---
name: setup-matt-pocock-skills
description: Redirects to /setup-ai-foundation, which writes the same Project setup contract in this Marketplace.
disable-model-invocation: true
---

# Setup Matt Pocock's Skills

In Projects that use the ai-foundation Marketplace, `setup-ai-foundation` writes the Project setup contract that mattpocock's skills read (the `## Agent skills` block and `docs/agents/*.md`), plus the Linear, docs backend and plugin configuration this Marketplace needs (ADR-0002).

Tell the user, in one short message, to run `/setup-ai-foundation` (or `/foundation:setup-ai-foundation`) instead. Run nothing else: setup is user-invoked only.
