---
name: golang
description: House Go conventions (layers, test levels, go-kit errors, uber/fx, OTel, testify + mockgen). Use when writing, reviewing, testing or debugging Go code.
license: MIT
metadata:
  status: derived
  upstreams:
    - repo: samber/cc-skills-golang
      sha: 8e899e20ff0cd4dc524af3993e4c62d8ee8c5717
      path: skills
      license: MIT
---

# Go

House conventions for a Go service built on `github.com/lcnascimento/go-kit`, uber/fx, golangci-lint v2, OpenTelemetry, testify and mockgen. Where generic Go advice disagrees with this skill, this skill wins. Lint and format rules live in the repo's `.golangci.yml`/`.golangci.yaml`: read it, and run the linter instead of guessing.

## Where code goes

Every change starts here: pick the layer, then the test level comes with it. Dependencies point inward (`transport` → `application` → `domain`; `application` → `repository`/`bridge` through interfaces).

| Layer | Path | Holds | Test level |
| --- | --- | --- | --- |
| `transport` | `internal/transport/...` | HTTP handlers, consumers, workers: parse, call the application, write the response | `unit` |
| `application` | `internal/application/<resource>` | Use cases: orchestrate domain, repositories and bridges; telemetry hooks | `unit` |
| `domain` | `pkg/domain` (shared), `internal/idomain` (private) | Entities, value objects, sentinels, pure logic | `unit` |
| `repository` | `internal/repository/<resource>` | State the service owns (its databases, caches) | `component` |
| `bridge` | `internal/bridge/<system>` | Systems the service does not own: another service's API, a SaaS, a queue or workflow used as output | `component` |

`cmd/<kind>/<name>/main.go` is a one-liner calling a constructor in `bundle/`, which wires everything with fx. `cmd` and `bundle` are tested only with `fx.ValidateApp`.

- **`unit`**: runs under `go test -short`; every collaborator is a mockgen mock.
- **`component`**: named `TestComponent<Unit>_<Scenario>`, runs against the real thing (database, emulator, sandbox), and calls `t.Skip` when `testing.Short()`.

Every layer has tests. Repository and bridge translate driver or client errors into domain sentinels; nothing above them sees a driver error type.

## Norms for any `.go` file

- Errors come from `go-kit/errors`: wrap with `ErrOperation.WithCause(err)`, never `fmt.Errorf` or `%w`.
- Interfaces live with the consumer in one `contracts.go` per consuming layer; constructors take interfaces and return concrete pointers.
- Logging, tracing and metrics live only in the package's `telemetry.go`, behind `on<Event>` hooks.
- `ctx context.Context` is the first parameter of anything that does I/O.
- Comments are optional, exported identifiers included. Write one only when the *why* is not in the code.
- Internals that callers must not touch go under an `internal/` package; an importable internal will be imported.
- Two hand-edited lists of the same items are a bug: derive one from the other, or add a test or `go generate` step that fails when they drift.
- A change that takes a file from under 1k lines to over 1k lines needs a strong reason; split it instead.

## References

Read the reference before working in its area.

- [architecture](references/architecture.md): layer responsibilities, repository vs bridge, dependency direction, decorators.
- [layout](references/layout.md): workspace, modules, package file set, versioned directories.
- [errors](references/errors.md): sentinels, `WithCause`, Kind/Code/Retryable, boundary translation, panics.
- [di](references/di.md): `contracts.go`, fx modules, `fx.Annotate`/`fx.As`, lifecycle, functional options.
- [concurrency](references/concurrency.md): goroutine ownership, errgroup + `fx.Shutdowner`, `WithoutCancel`, backoff, singleflight.
- [observability](references/observability.md): `telemetry.go`, `on<Event>` hooks, baggage, metrics, severity logging.
- [testing](references/testing.md): unit vs component, suites, mockgen, fixtures, naming, `errors.ErrMock`.
- [style](references/style.md): naming, type switches, `Parse*`/`Must*`, config via `env.Get`, imports.
- [safety](references/safety.md): nil, typed-nil interfaces, slice aliasing, numeric conversion, `defer` in loops.
- [security](references/security.md): trust boundaries, injection, crypto, secrets, error exposure.
- [performance](references/performance.md): measure first, benchmarks, allocation, HTTP transport, GC limits.
- [troubleshooting](references/troubleshooting.md): reproduce with a test, race detector, pprof, goroutine dumps.
