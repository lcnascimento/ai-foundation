# Concurrency

## Ownership

Every goroutine has an owner, a way to be told to stop (`ctx.Done()` or a closed channel) and someone who waits for it. Before writing `go`, name all three; if one is missing, keep the work synchronous.

- Every `select` in a long-running loop includes `case <-ctx.Done():`.
- Only the sender closes a channel. Declare direction (`chan<-`, `<-chan`) in signatures.
- Channels are unbuffered unless a measured need says otherwise.
- Bound fan-out with `errgroup.SetLimit(n)`, never one goroutine per item of unbounded input.
- Call `wg.Add` before `go`, or use `wg.Go(func(){...})` (Go 1.25+).

## Fatal errors in runners

A consumer or worker runs its loops under `errgroup.WithContext`. When a loop dies with a fatal error, the runner calls the `shutdown` hook injected with `WithShutdown`, which the bundle wires to `fx.Shutdowner`:

```go
fx.Provide(func(svc transport.WarehouseService, s fx.Shutdowner) *warehouse.Consumer {
    return warehouse.New(svc, warehouse.WithShutdown(func() { _ = s.Shutdown(fx.ExitCode(1)) }))
})
```

That stops the whole app gracefully (telemetry flushed, producers closed). `os.Exit` from a goroutine skips all of it.

## Context lifetime

- `context.WithoutCancel(ctx)` detaches work that must outlive its caller: a consumer started from `OnStart`, a cache refill the caller may abandon, test cleanup in `t.Cleanup`.
- Deadlines on outbound calls use `context.WithTimeout` with a named `const timeout`.
- `context.Background()` appears only in `main`, bootstrap and tests (`t.Context()` in tests).

## Shared state

| Need | Use |
| --- | --- |
| Collapse concurrent identical misses | `singleflight.Group` (plus `sync.RWMutex` around the cached value) |
| Counters, flags | typed atomics (`atomic.Int64`, `atomic.Bool`) |
| Struct fields read and written concurrently | `sync.Mutex`/`RWMutex`; never hold it across I/O |
| Lazy one-time init | `sync.OnceValue`/`OnceValues` |

A map read and written from more than one goroutine without a lock crashes the process, not just the request.

## Retries

Retries use exponential backoff with a cap and a total budget, waiting with `time.NewTimer` + `select` on `ctx.Done()` (not `time.Sleep`, not `time.After` in a loop). Keep the backoff values in package `var`s so tests can shrink them via `export_test.go`.

Optimistic concurrency uses a `version` field and a bounded retry loop; when retries run out, return a sentinel marked `Retryable()`.

## Tests

Run `go test -race` on anything that spawns goroutines. Use `go.uber.org/goleak` in packages that own long-lived goroutines.
