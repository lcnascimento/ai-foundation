# Dependency injection

## Interfaces at the consumer

Each consuming layer has one `contracts.go` (`internal/application/contracts.go`, `internal/transport/contracts.go`, ...) that declares only the methods that layer calls. The same interface may be redeclared in several layers; that is intended, since each layer depends only on what it uses.

```go
type SchemasRepository interface {
    Get(ctx context.Context, tenant orgdomain.BrandSlug, id domain.SchemaID) (*domain.Schema, error)
    Create(ctx context.Context, tenant orgdomain.BrandSlug, schema *domain.Schema) error
}
```

- Always name interface parameters (`ctx`, `tenant`, `id`); never blank them.
- An external SDK client is wrapped as an embedding interface for mocking (`type TemporalClient interface { client.Client }`) or narrowed to the methods used (`type MongoClient interface { Ping(...) error }`).
- mockgen generates `internal/mocks/mocks.go` from every `contracts.go` (`make mocks`). Regenerate after changing a contract.

Constructors take interfaces and return concrete pointers: `func New(repo application.SchemasRepository, opts ...Option) *Application`.

## Wiring with fx

Each component is an `fx.Module` in `bundle/` that provides the concrete type and binds it to each consumer interface:

```go
func SchemasRepository() fx.Option {
    return fx.Module(
        "Schemas Repository",
        fx.Provide(schemas.New),
        fx.Provide(fx.Annotate(schemas.New, fx.As(new(application.SchemasRepository)))),
    )
}
```

- Start and stop go through `fx.Lifecycle` hooks (`fx.Hook{OnStart: server.Start, OnStop: server.Shutdown}`), never goroutines started from a constructor.
- Resources with a `Close` register it as an `OnStop` hook in the same module that provides them.
- A runner that must stop the app on a fatal error receives `fx.Shutdowner` and calls `Shutdown(fx.ExitCode(1))`; see [concurrency](concurrency.md).
- Each binary's bundle constructor has an `fx.ValidateApp` test; that is the only test `cmd`/`bundle` get.

## Functional options

Optional configuration is `type Option func(*T)` plus `With…` functions in `options.go`, and constructors take `opts ...Option`. Create `options.go` only when there is at least one `With…`; an empty `Option` type is dead code.
