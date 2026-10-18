# Comments follow a closed exception list, through a Custom Principle and a `code-review` gate

The implementer writes useless comments often. Commit [`636aa58`](https://github.com/lcnascimento/boilerplate/commit/636aa58e9c93f8675ce20784b61ee84db489001c) in `boilerplate` deleted dozens of them: narration of what the code does, change history, doc comments that repeat the name, and usage manuals and architecture tours in Makefiles, Tiltfiles, compose files and CI workflows. The only rule we had was one line in `golang` ("write one only when the *why* is not in the code"), and that open criterion is exactly what the model uses to convince itself its comment explains a why. On top of that, Claude Code's system prompt tells the agent to match the comment density of the surrounding code.

We adopt the stance of `comment-sicko` (the `no-comments` skill, backnotprop/pstack): every comment is deleted unless it matches a closed exception list, and a doubtful one goes too. The rule ships through two paths:

- **`earn-every-comment`**, a Custom Principle in `engineering`, delivered through the index (ADR-0004). It applies when a comment is written, in any file, and reaches `implement*` subagents through `SubagentStart`. The exceptions are a license header; behavior forced by an external dependency we cannot reshape; a doc comment that defines a public API contract, consumed outside the repository or published module; an issue or RFC link; and a lint suppression whose rule is faulty, pedantic or style-only. A surprise in our own code becomes a reshape of the code, and a constraint becomes a test, type or lint. When neither fits the task's scope, it goes to the PR body or a ticket, never into a comment. The rule covers what the agent writes and the existing comments on lines the diff touches.
- **Fowler's Comments smell** in `code-review`'s baseline, judged against the Principle. It is the one hard violation of the baseline, while the other smells stay heuristics. "The repo overrides" still holds.

## Considered Options

- **Keep the open why criterion**: rejected, because it produces the comments we are deleting.
- **The closed list plus an exception for constraints of our own design**: rejected. It would save comments like `# 9330 clears every port…`, but it reopens the door the list closes. A surprise in our own code should become a reshape.
- **Shorten a comment instead of deleting it**: rejected. A comment outside the list goes whole.
- **The Principle alone**: rejected. An index line competes with the model's habit and with the system prompt's density instruction, and `encode-lessons-in-structure` asks that a recurring correction become a gate.
- **Vendor `no-comments`**: rejected. It depends on `poteto-mode`, `/architect` and a persona, and would add a subagent to every `implement`. `code-review` already runs at the end of `implement`.
- **An extra step in `implement`**: rejected. The review already covers it without another pass.

## Consequences

- `engineering` now has 20 Principles. Its index uses 5184 of its 7000 characters. ADR-0004 is updated with the new count.
- `code-review` moves from Community to derived, so each mattpocock update is a manual merge of the Comments smell.
- `golang` points to the Principle instead of restating a rule. `nextjs` had no comment rule and is covered by the index.
- The Principle's text is original. `comment-sicko` is credited as inspiration, as ADR-0009 did with `not-your-babysitter`.
