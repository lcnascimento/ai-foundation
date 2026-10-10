---
name: verify
description: Verify your own code change in layers (static checks, tests, runtime when observable behavior changed) and report a Verification block. Use before declaring work done or opening a PR, or when asked to verify a change.
---

# Verify

Check your own change before you call it done, and prove each claim with a command you ran. This is the procedure behind `prove-it-works`; load it with `foundation:principles prove-it-works` if it is not already in context. CI stays the deterministic gate: `verify` catches what would break CI before a PR opens, and what CI cannot see, which is the change running.

## 1. Read the Project files

Read both files if they exist. Both are optional, and a section missing from either falls back to the default below. Their format is in [references/project-files.md](references/project-files.md); read it when you write or fix one of them.

- `docs/agents/verify.md`: the command for each layer, deliberate exclusions, and what counts as passing.
- `docs/agents/environment.md`: how to start and stop dependencies, variables and `.env`, the health check, and where logs, metrics, traces and remote signals live.

Done when you know the command for each layer (or that it is missing) and whether the Project has an environment to start.

## 2. Run the layers

Run each layer in order. A layer with no command is **skipped**, with the reason; a skip is never a failure.

1. **Static**: format, then lint. Commit the changes the formatter applies.
2. **Tests**: start the environment first when `environment.md` exists, and wait for its health check.
3. **Runtime**: only when the change alters observable behavior (an endpoint, a worker, a CLI, the UI). Use `verify.md`'s runtime command if it has one; otherwise start the environment and exercise the changed behavior directly (call the endpoint, run the worker, drive the page), then read the real output and the local logs, metrics or traces `environment.md` points to. Skip it, with the reason, when no observable behavior changed.

Stop the environment you started once the layers are done.

### Default without `verify.md`

Run only the root `Makefile`, from the repo root:

| Layer | Command |
| --- | --- |
| Static | `make format` (commit what it changes), then `make lint` |
| Tests | `make test` (start the environment first when `environment.md` exists) |
| Runtime | none by default; follow step 2.3 with `environment.md` |

A target the root `Makefile` does not define is a skipped layer (`make -n <target>` fails with `No rule to make target`). Whether a target delegates to inner Makefiles is the Project's business. Without a root `Makefile`, every Makefile layer is skipped. Whenever the default runs, suggest `/setup-ai-foundation` to the user in your reply, which writes `verify.md` and `environment.md`; never run it yourself.

## 3. Fix and rerun

On a failure, fix the cause and rerun from the failing layer, then rerun the earlier layers if the fix touched what they cover. A check turns green only through a fix in the code under test: every check that ran stays in the run, with its assertions and its scope intact.

When the same failure happens a second time, stop under `know-when-to-stop`: load it with `foundation:principles know-when-to-stop` and follow it.

Done when every layer has passed or is skipped with a reason, or you have stopped under `know-when-to-stop`.

## 4. Report the Verification block

Write one row per layer you ran or skipped, with the exact command and its result: `passed`, `failed: <what failed>`, or `skipped: <reason>`. Split a layer into several rows when it ran several commands.

```markdown
## Verification

| Layer | Command | Result |
| --- | --- | --- |
| Static | `make format` | passed (committed formatting of 2 files) |
| Static | `make lint` | passed |
| Tests | `make test` | passed |
| Runtime | `curl -s localhost:8080/v1/orders/42` | passed: returns the new `status` field |
```

When `implement` or `implement-spec` called this skill, the block goes in the PR body. Otherwise it goes in your reply.
