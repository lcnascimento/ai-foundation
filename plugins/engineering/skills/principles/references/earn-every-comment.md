---
name: earn-every-comment
description: "Apply before writing a comment, doc comment or lint suppression in any file (code, config, CI, build), or when a diff touches one. Delete by default; keep only the closed exception list; reshape the code or encode the constraint instead of explaining it."
---

# Earn Every Comment

A comment is guilty until it matches the exception list below. The code, its names, its types and its tests carry the meaning; a comment carries only what they cannot. When you are not sure an exception applies, the comment goes.

**Why:** A comment is a second copy of the meaning that no compiler or test keeps true, so it drifts. Most comments an agent writes restate the code, narrate the change for the reviewer, or apologise for a shape the code should not have. Each one costs every future reader, and a file full of them teaches the next agent to write more.

**The exception list.** Only these survive:

1. A legal or license header.
2. Non-obvious behavior forced by an external dependency, platform, vendor or protocol we cannot reshape, in one sentence that names it ("goose v3 silently skips an applied version with no file").
3. A doc comment that defines a public API contract. Public means consumed outside this repository or published module: a library, an SDK, an OpenAPI spec. An exported identifier in an internal or service package is not public.
4. A link to an issue or RFC that explains a constraint the code cannot express.
5. A lint suppression whose rule is faulty, pedantic or style-only, or a formatter directive (`// prettier-ignore`).

A surviving comment states the reason in its shortest true form. A comment outside the list is deleted, never shortened into a smaller one.

**Instead of a comment:**

- **Narration** of what the code does, a doc comment that repeats the name, a section banner: delete it. If the code needs it to be understood, rename, extract or retype until it does not.
- **Change history** ("added X to fix Y", "now uses Z"): put it in the commit message or the PR body.
- **A surprise in our own code** (a workaround, an ordering trick, a magic value): reshape the code so the behavior is obvious, with a named constant, an extracted function, a type, or a redesign. When the reshape is outside the task's scope, delete the comment and list the symbol as open work in the PR body or a tracker ticket.
- **A constraint** (`IMPORTANT`, `do not remove`, `keep in sync with`): encode it as a test, type, runtime check or lint rule (see encode-lessons-in-structure). When no cheap encoding exists, delete the comment and list the constraint as open work.
- **A lint suppression on a rule that guards correctness or safety** (`eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `//nolint`): remove it and fix the code the rule flagged.
- **A usage manual or architecture tour** in a Makefile, Tiltfile, compose file or CI workflow: delete it. If humans need it, write it as a document with `foundation:documentation`.
- **Commented-out code**: delete it. Git keeps it.

**Scope.** Apply the list to every comment you write and to every existing comment on a line your diff touches. Sweep whole files only in a change dedicated to that. The comment density of the surrounding code is no license: match its naming and idiom, and hold its comments to this list.

**The test:** For each comment in the diff, name the exception it matches. A comment with no number from the list is deleted.

Inspired by `comment-sicko` from `no-comments` (backnotprop/pstack, MIT); this text is original.
