# Performance

## Measure first

No optimization without a profile or benchmark showing the bottleneck. First rule out the outside: if traces show the time is in a database, a bridge call or a queue, fix that (query, index, batching, caching) instead of the Go code.

## Cycle

1. Name the metric (latency, throughput, allocations, memory) and the target.
2. Write a benchmark that isolates one function, using `b.Loop()` (Go 1.24+).
3. Baseline: `go test -bench=BenchmarkX -benchmem -count=6 ./pkg/... > before.txt`.
4. Change one thing.
5. Compare with `benchstat before.txt after.txt`; keep the change only if the difference is significant.
6. Put the `benchstat` output in the commit body, and a one-line comment at the optimized code saying why it is shaped that way, so nobody "simplifies" it back.

## What usually pays

- **Allocations**: preallocate slices and maps when the size is known (`make([]T, 0, n)`), use `strings.Builder`, avoid converting `[]byte` ↔ `string` in loops.
- **Batching**: one bulk write over N single writes; one query with `$in` over N lookups.
- **Work avoidance**: compile regexes and templates once at package level; `singleflight` for concurrent identical fetches.
- **HTTP clients**: a shared `http.Client` with a tuned `Transport` (`MaxIdleConnsPerHost` defaults to 2); always drain and close response bodies.
- **Containers**: set `GOMEMLIMIT` to 80-90% of the container memory limit.

## What usually doesn't

`unsafe`, manual inlining, struct field reordering and `sync.Pool` are justified only by a profile of a verified hot path. Avoid `reflect.DeepEqual` and `panic`/`recover` in production paths.
