# Section: environment

Writes `docs/agents/environment.md`, which `engineering:verify` and troubleshooting skills read to start the Project's dependencies and find its logs, metrics and traces (ADR-0011). Its format is owned by `engineering:verify`'s `references/project-files.md` (`plugins/engineering/skills/verify/references/project-files.md` in the Marketplace). Render that format exactly; don't add sections.

## Runs when

`engineering` is enabled. Without it, ask nothing and render nothing here.

## Detect

- `docs/agents/environment.md`: when it exists, its whole content is the previous answer, hand edits included.
- `Makefile` targets (`grep -E '^[A-Za-z0-9_.-]+:' Makefile`, skipping `.PHONY` and pattern rules): environment targets named `up`, `down`, `start`, `stop`, `env-up`, `env-down`, `deps`, `deps-up`, `deps-down`, `compose-up`, `compose-down`, `health`, `healthcheck`, `logs`.
- Compose files at the root, in this order: `compose.yaml`, `compose.yml`, `docker-compose.yaml`, `docker-compose.yml`, then any other `docker-compose*.yml`/`docker-compose*.yaml` alphabetically. Read each file's services in file order, with their `image`, published `ports` and whether they declare a `healthcheck`. Use `-f <file>` in commands only for a file other than the first default one found.
- `.env.example` (or `.env.sample`): its variable names, in file order. Never read `.env`.
- The CI config (`.github/workflows/*.yml`, `.gitlab-ci.yml`): `services:` it starts and environment variable names it sets for tests.

## Ask

When `docs/agents/environment.md` exists, recommend it unchanged and show only what detection found that it lacks (a new compose service, a new Makefile target), each as an optional addition. Otherwise recommend the proposal below, section by section, and ask for **Remote signals** (recommend none).

Proposal, each section omitted when it has nothing to say:

- **Start**: the `make` start target (`up`, `start`, `env-up`, `deps-up`, `deps`, `compose-up`, first found) if any, else `docker compose [-f <file>] up -d --wait` per compose file. Then one line `Services: \`<service>\`, ...` listing the compose services in file order. With neither a target nor compose but CI `services:`, one line per CI service saying the tests expect it (e.g. `Postgres 16 on localhost:5432, as in CI`), for the user to confirm.
- **Stop**: the matching `make` stop target, else `docker compose [-f <file>] down` per compose file.
- **Variables**: `Copy \`.env.example\` to \`.env\`; \`direnv\` loads it.` when the example file exists, then one line per variable name (`` `NAME` ``), never a value.
- **Health check**: the `make` `health`/`healthcheck` target if any; else, when every compose service declares a `healthcheck`, `` `docker compose [-f <file>] ps` shows every service healthy (Start waits for it with `--wait`). ``; else ask.
- **Local signals**: `Logs: \`docker compose [-f <file>] logs -f <service>\`` for the services, or `make logs` when that target exists. For a service whose image is Prometheus, Grafana, Jaeger, Tempo, Loki or an OpenTelemetry collector, a `Metrics:`/`Dashboards:`/`Traces:` line with `http://localhost:<published port>`.
- **Remote signals**: only what the user names.

## Render

**`docs/agents/environment.md`**, owned Markdown: the approved content in the format of `project-files.md`, `# Environment` first, then the sections in its order (Start, Stop, Variables, Health check, Local signals, Remote signals), one blank line between blocks, list items as `- `, a trailing newline. When the previous file is accepted unchanged, render it byte for byte. When every section is empty, render no file and leave out the entry below.

## Agent skills entries

```markdown
### Environment

How to start the Project's dependencies and where its logs, metrics and traces live. See `docs/agents/environment.md`.
```

## Checklist

- Docker running, when **Start** uses `docker compose` (verify with `docker compose version`).
