# Testing

## Levels

| Level | Layers | How it runs | Collaborators |
| --- | --- | --- | --- |
| `unit` | domain, application, transport | `go test -short` | mockgen mocks only |
| `component` | repository, bridge | `go test -run Component` | the real thing: database, emulator, sandbox |
| bootstrap | `cmd`, `bundle` | with the unit tests | `fx.ValidateApp` on each bundle constructor |

Component tests are named `TestComponent<Unit>_<Scenario>` and start with:

```go
if testing.Short() {
    t.Skip("component test")
}
```

Each component test isolates its data (a random tenant or database name such as `test_schemas_<uuid>`) and removes it in `t.Cleanup` with `context.WithoutCancel(t.Context())`. Use the Makefile targets (`make test`, `make test.unit`, `make test.component`) when they exist.

## Shape

- External test packages (`package schemas_test`). An internal test package needs `//nolint:testpackage // <reason>`; expose test hooks through `export_test.go` instead when possible.
- Assertions use testify `require` (`s.Require()` in suites). Assert errors with `ErrorIs` on both the operation error and its cause.
- Use a `testify/suite` when tests share setup (mocks, the unit under test); `SetupTest` builds a fresh `gomock.Controller` and the unit. Run the suite with `t.Parallel()`.
- Table-driven tests only for many inputs through one path (parsers, codecs, mappers). Behaviour with different setup gets separate test methods.
- Names: `Test<Unit>_<Scenario>` describing behaviour (`TestGet_WrapsRepositoryErrors`); suite methods the same without the `Test<Unit>` prefix.
- Fake errors are `errors.ErrMock` from go-kit, not `errors.New("some error")`.
- Use `t.Context()`, `t.Helper()` in helpers, `t.Cleanup` for teardown.

## Mocks

Mocks come from mockgen (`go.uber.org/mock`), generated from `contracts.go` into the sibling `internal/mocks/mocks.go`. Regenerate with `make mocks` after changing a contract; never edit `mocks.go`. Set `EXPECT()` only for the calls the scenario is about, with `gomock.Any()` for arguments the test doesn't care about, so tests fail on behaviour changes, not refactors.

## Fixtures

Randomized builders in the public `pkg/fixture` (`fixture.RandomEventSchema()`) produce valid entities; the test overrides only the fields under test. Add a builder there instead of hand-building entities in test files.

## HTTP handlers

Test handlers through the real router (`mux.Router` or whatever the transport uses) with `httptest`, asserting status and body with `JSONEq`.

## Every layer

Every new package ships with tests at its layer's level. A deliberate exclusion (a flaky emulator, say) is written in the Makefile and CI with the reason, not silently skipped.
