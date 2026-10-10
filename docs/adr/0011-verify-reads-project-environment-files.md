# Agent verification reads the Project's environment from docs/agents, not from native run skills

`engineering` ships a Custom skill, `verify`, that checks the agent's own work in layers before it declares the work done: static checks (format, lint), tests, and runtime. Runtime runs only when the change alters observable behavior (an endpoint, a worker, the UI). CI stays the deterministic gate (ADR-0009). `verify` catches what would break CI before a PR opens, and what CI can't see, which is the change running. It is the procedure behind the `prove-it-works` Principle. The skill triggers on its description ("before declaring done"), and `implement`/`implement-spec` cite `engineering:verify` before `engineering:code-review`, which adds one line to their existing derivation (ADR-0008). Claude Code also ships a native `verify` skill, so every reference uses the qualified name `engineering:verify`, as ADR-0008 does for `code-review`.

It reads two optional Project files, following the `docs/agents/*.md` pattern (ADR-0007):

- `docs/agents/environment.md`: how to start and stop dependencies, variables and `.env`, the health check, where local logs, metrics and traces live, and an optional field for remote signals (Sentry, LGTM). Troubleshooting skills such as `diagnosing-bugs` use it too.
- `docs/agents/verify.md`: the commands for each layer, deliberate exclusions, and what counts as passing.

Without `verify.md`, the default runs only the root `Makefile`: `make format` (the changes it applies are committed), then `make lint`, then `make test`. Whether those targets delegate to inner Makefiles is up to the Project. A missing target is reported as a skipped layer, not a failure. If `environment.md` exists, the environment is started before `make test`.

Project setup's `engineering` section writes both files, prefilled from what it detects (`Makefile`, `docker-compose*.yml`, the CI workflow), and lists `environment.md` in the `## Agent skills` block so that Community skills find it without being derived. Without setup, `verify` falls back to the default and suggests `/setup-ai-foundation`.

The output is a `Verification` block listing each layer, its command, and its result (passed, failed, or skipped with the reason). It goes in the PR body when `implement*` calls the skill, and in the reply otherwise. On failure the agent fixes the problem and reruns. If the same failure happens twice, it stops under `know-when-to-stop`, and it never deletes or skips a check to turn it green.

## Considered Options

- **Adopt the native `run-<unit>` convention** (`.claude/skills/run-<unit>/SKILL.md`, written by `/run-skill-generator` and read by the native `/run`): rejected in favor of a plain file next to `forge.md`. That keeps the environment in the same place and shape as the rest of the Project setup contract, where setup writes it.
- **Mirror CI as the default** (read the CI workflow through `forge.md`): rejected in favor of the root `Makefile`, which follows the convention already used in the user's Projects.
- **Run every directory's Makefile touched by the diff**: rejected. Only the root `Makefile` is part of our structure.
- **Fold the fault-injecting independent Verifier into `verify`**: rejected. `verify` is the agent's own check in the session. The independent Verifier remains an open item among the known v1 gaps.

## Consequences

- Projects that only use `/run` get no environment from `verify`, and the two can drift if both exist.
- Homelab signals (Sentry, LGTM) reach `verify` only through the optional field in `environment.md`. Real integration remains open.
- `implement` and `implement-spec` carry one more line in their derivation.
- The native `verify` skill competes with `engineering:verify` for routing on its description. The first version of this ADR said no native `verify` existed. `implement*` and the docs already used the qualified name, so only the ADR changed.
