# Errors

All errors come from `github.com/lcnascimento/go-kit/errors`. It re-exports `Is` and `As`, so the standard `errors` package is unnecessary. A `CustomError` carries a message, a `Kind`, a `Code`, attributes, a `Retryable` flag and a list of causes (`Unwrap() []error`).

## Two tiers of sentinel

Declare every sentinel in the package's `errors.go`:

```go
var (
    // Boundary errors: callers branch on them; set Kind and Code.
    ErrSchemaNotFound = errors.New("schema not found").
        WithKind(errors.KindNotFound).
        WithCode("SCHEMA_NOT_FOUND")

    // Operation errors: name the failed step; no Kind or Code.
    ErrGetSchema = errors.New("failed to get schema")
)
```

- **Boundary errors** live in `pkg/domain` (or the package callers branch on). Set `WithCode` with a stable SCREAMING_SNAKE code, no `ERR_` prefix. `Kind` is optional; an error whose tree has no Kind is treated as internal.
- **Operation errors** live in the application package, one per method: `failed to <verb> <noun>`.

## Wrapping

Wrap with the operation error as the head and the cause as a child:

```go
if err := a.schemas.Create(ctx, tenant, schema); err != nil {
    return a.onError(ctx, ErrCreateSchema.WithCause(err))
}
```

`errors.Is` then matches both `ErrCreateSchema` and whatever the cause is, and tests assert both. `fmt.Errorf` and `%w` are never used: they build a plain error that cannot carry a Kind, Code, attributes or `Retryable`, and that bakes the cause into its message, so logs stop grouping by message.

Add context with `WithAttribute("reason", "empty request")`, not by formatting values into the message. Messages stay constant so logs group by message.

## Kind, Code, Retryable

- **Kind** decides the transport status: `httpserver/util.WriteError` takes the first non-unknown Kind in the tree and maps it to an HTTP status. It also decides log severity (`errors.Severity`). Pick from the `errors.Kind*` constants.
- **Code** is the stable identifier a client may branch on.
- **`Retryable()`** marks transient conditions (an exhausted optimistic-concurrency retry, a timeout from a dependency). Callers check `errors.IsRetryable(err)`.

## Translation at the boundary

Repositories and bridges translate driver or client errors into domain sentinels at the call site (`mongo.ErrNoDocuments` → `ErrSchemaNotFound`; `errors.As(err, &apiErr)` on the client's error type). Every `Parse*` function returns a typed sentinel (`ErrInvalidSchemaID.WithCause(err)`), never the raw parser error.

## Handling once

An application method logs and returns in one step through `a.onError(ctx, err)` (see [observability](observability.md)). Nothing else logs an error: transport writes it, and lower layers only return it.

Every returned error is checked. A discarded error is written `_ = f()` with a reason on the line when the reason is not obvious.

## Panics

`panic` only in `Must*` constructors and at fx provider/bootstrap time, where failing fast is the point. Everything else returns an error.
