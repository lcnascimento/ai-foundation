# Layout

## Modules

A backend is a Go workspace (`go.work`) with one module per service. A service's public `pkg/` (domain, events, client models, fixtures) is its own module, so other services import it without pulling the service; `replace` directives wire local paths.

## Service tree

```
<service>/
  cmd/<kind>/<name>/main.go     # one line: bundle.Run(bundle.New<Name>())
  bundle/                       # fx modules: infrastructure, repositories, services, runners
  internal/
    transport/                  # api/<surface>/internal/{routes,handlers/<resource>/v1}, consumer/, worker/
    application/<resource>/
    idomain/
    repository/<resource>/
    bridge/<system>/
  pkg/{domain,event,client,fixture}
```

## Package file set

Every application, repository, bridge and transport package uses the same file names, so an agent finds things without searching:

| File | Holds |
| --- | --- |
| `application.go` / `repository.go` / `bridge.go` / `server.go` / `consumer.go` | The type, `New`, methods |
| `errors.go` | The package's sentinels, one `var (...)` block |
| `telemetry.go` | `pkg` name, logger, tracer, meter, metrics, `on<Event>` hooks |
| `options.go` | `type Option func(*T)` and its `With…` functions; only when at least one `With…` exists |
| `contracts.go` | Interfaces this layer consumes (one per consuming layer, see [di](di.md)) |
| `internal/mocks/mocks.go` | mockgen output from the sibling `contracts.go` |

## Versioned directories

Anything with an external contract is versioned by directory: handlers (`handlers/<resource>/v1`), events (`pkg/event/<stream>/v1`), workflows (`workflow/v1`). A breaking change adds `v2` beside `v1`.

## Package names

Package names describe the resource they serve (`schemas`, `profiles`, `dedup`); a plural resource name is fine. `util`, `common` and `helpers` say nothing about content: name the abstraction instead.
