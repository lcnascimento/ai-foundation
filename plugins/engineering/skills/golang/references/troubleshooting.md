# Troubleshooting

Go-specific tools for a bug you are chasing. The loop itself (reproduce, one hypothesis at a time, root cause before fix) belongs to the debugging skill; this file says which Go tool answers which symptom.

## Symptom → first tool

| Symptom | First move |
| --- | --- |
| Doesn't compile | `go build ./... && go vet ./...`; read the first error only, fix, rebuild |
| Wrong result | A failing `unit` test at the layer where the value first goes wrong |
| Panic | Read the trace top-down to the first frame in our code; `GOTRACEBACK=all` for all goroutines |
| Flaky test | `go test -race -count=20 -run '^TestX$' ./pkg/...` |
| Hang | Goroutine dump: `curl localhost:6060/debug/pprof/goroutine?debug=2` or `SIGQUIT`; look for goroutines stuck on the same channel or lock |
| Slow request | The trace in the OTel backend first: which span holds the time? |
| High CPU | `go tool pprof http://host/debug/pprof/profile?seconds=30`, then `top` and `list <func>` |
| Memory growth | Two heap profiles minutes apart, `pprof -diff_base`; check goroutine count for leaks |
| Works locally, fails in CI | Compare Go version, env vars, `-short`, and whether component dependencies are up |

## Where to look in this stack

- **Error trees**: `errors.Reasons(err)` lists every cause; `errors.Kind(err)` explains the status code. A 500 with a known cause usually means an error built without go-kit somewhere in the chain.
- **Logs**: `onError` logs once per failed application call with the trace ID; follow the trace, not log lines.
- **fx startup failures**: the error names the missing type; usually a constructor's interface isn't bound with `fx.As` in the bundle. `fx.ValidateApp` reproduces it in a test.
- **Mocks out of date**: "missing call" or "unexpected call" after a contract change; run `make mocks`.
- **Component test hangs**: dependencies not running, or retry/backoff tunables not shrunk for tests.

## Debugger

Use Delve (`dlv test ./pkg/... -- -test.run '^TestX$'`) when stepping is faster than more logging; `go build -gcflags=-m` to see escape decisions when chasing allocations.
