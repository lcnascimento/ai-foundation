# Observability

OpenTelemetry covers traces, metrics and logs. The logger is `go-kit/o11y/log` (slog-based); `o11y.MustStart` and `o11y.Shutdown` bracket the app in the bundle.

## `telemetry.go`

All logging, tracing and metrics of a package live in its `telemetry.go`. Business code calls only `on<Event>` hooks; no `logger.`, `tracer.Start` or `slog.` call appears anywhere else outside `bundle/`.

```go
var (
    pkg    = "cdp/application/schemas"   // "<service>/<layer>/<name>"
    logger = log.MustNewLogger(pkg)
    meter  = otel.Meter(pkg)
    tracer = otel.Tracer(pkg)

    schemasCreated = metric.MustIntCounter(meter, "cdp.schemas.created", "Number of schemas created")
)

func (a *Application) onCreateStart(ctx context.Context, tenant orgdomain.BrandSlug) (context.Context, trace.Span) {
    ctx, span := tracer.Start(ctx, "CreateSchema")
    ctx = baggage.ContextWithMembers(ctx, baggage.NewMember(orgdomain.ContextKeyBrandSlug, tenant.String()))
    logger.Debug(ctx, "creating schema")
    return ctx, span
}

func (a *Application) onCreated(ctx context.Context, tenant orgdomain.BrandSlug, schema *domain.Schema) {
    schemasCreated.Add(ctx, 1, tenantAttributes(tenant))
    logger.Info(ctx, "schema created")
}

func (a *Application) onError(ctx context.Context, err error) error {
    logger.ErrorBySeverity(ctx, err)
    return err
}
```

A method then reads as: `ctx, span := a.onCreateStart(...)`, `defer span.End()`, work, `a.onCreated(...)`, with every error returned through `a.onError`.

## Hooks

- One hook per event. A new method gets its own `on<Method>Start` and `on<Done>` hooks, even if an existing hook looks close enough; reuse makes spans and metrics lie.
- `onError` logs by severity (`ErrorBySeverity` derives the level from the error's Kind) and returns the same error, so logging and returning are one step.
- A hook that publishes a domain event handles a publish failure with `_ = a.onError(ctx, err)`; the business result stands.

## Context propagation

Correlation fields (tenant, entity IDs) travel as OTel baggage, keyed by exported `ContextKey*` constants in the domain package. Add them in the start hook so every log and span below carries them.

## Metrics

Metrics are package-level instruments created with `metric.MustIntCounter` (and siblings), named `<service>.<resource>.<event>` in past tense, with low-cardinality attributes (tenant yes, entity ID no).

## Below the application

Repositories and bridges add no telemetry of their own: driver auto-instrumentation (`otelmongo`, `redisotel`, `otelhttp`) covers them. Transport packages have a `telemetry.go` only for transport events (a consumer's message received, a subscriber died).
