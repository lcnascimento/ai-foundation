# Project files read by `verify`

The format of `docs/agents/verify.md` and `docs/agents/environment.md`. Project setup (`/setup-ai-foundation`) writes both, prefilled from the `Makefile`, `docker-compose*.yml` and the CI workflow; users edit them by hand. Every section is optional: a missing section means the default for that part.

## `docs/agents/verify.md`

One section per layer, each with the commands to run from the repo root, in order. A layer with no section falls back to the default (`make format` + `make lint`, `make test`, no runtime command); a layer whose section says `none` is skipped with the reason given.

```markdown
# Verify

## Static

- `make format` (commit what it changes)
- `make lint`

## Tests

- `make test`

## Runtime

- `make run-api`, then `curl -s localhost:8080/healthz`

Run when the change touches an endpoint or a worker.

## Exclusions

- `make test-e2e`: needs staging credentials; CI runs it.

## Passing

- Every command exits 0.
- `make lint` reports no new warnings in changed files.
```

- **Static / Tests / Runtime**: the commands for each layer. Runtime may add when it applies.
- **Exclusions**: checks the agent deliberately leaves out of the run, each with the reason. `verify` reports them as skipped with that reason.
- **Passing**: what counts as passing beyond exit code 0, when the Project needs more.

## `docs/agents/environment.md`

How to bring up what the tests and the running change need, and where to look when they misbehave. Troubleshooting skills such as `diagnosing-bugs` read it too.

```markdown
# Environment

## Start

- `docker compose up -d postgres redis`

## Stop

- `docker compose down`

## Variables

- Copy `.env.example` to `.env`; `direnv` loads it.
- `DATABASE_URL` points at the compose Postgres.

## Health check

- `curl -sf localhost:8080/healthz` returns 200.

## Local signals

- Logs: `docker compose logs -f api`
- Metrics: http://localhost:9090
- Traces: http://localhost:16686

## Remote signals

- Sentry project `orders-api`; LGTM dashboard `Orders`.
```

- **Start / Stop**: commands to start and stop dependencies. `verify` starts them before the tests and stops them at the end.
- **Variables**: how variables and `.env` are set up. Name the variables; never write their secret values.
- **Health check**: the command that shows the environment is ready.
- **Local signals**: where local logs, metrics and traces live.
- **Remote signals**: optional; external tools (Sentry, LGTM) the agent may consult.
