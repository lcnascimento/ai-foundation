# Style

`gofmt`, `gci` (import groups) and the enabled linters are in the repo's golangci config; read it rather than guessing, and run the linter before you finish. This file covers what the config does not say.

## Comments

No comment is required, exported identifiers included (`revive:exported` is off). Write one only when the code cannot say *why*: a non-obvious constraint, a workaround, a deliberate exception. Every `//nolint:<linter>` carries `// <reason>` after it.

## Types and values

- Domain IDs are typed (`type SchemaID struct{ util.CanonicalID }`) with a `Parse<Type>` that returns a typed sentinel and a `Must<Type>` that panics, for tests and constants only.
- Enums are `type Kind string` constants. Go doesn't check them for exhaustiveness, so every `switch` over an enum or type has a `default` that returns an error.
- Domain structs carry `json` tags and may be written straight to responses; storage uses separate models (see [architecture](architecture.md)). Tag names are snake_case.
- Constructors are `New` when the package has one primary type, `New<Type>` otherwise.

## Functions

- `ctx context.Context` first, then the tenant when there is one, then inputs.
- Early return on error, with a blank line before each `return` that follows other statements.
- Keep functions within the configured `funlen`; extract a helper named for what it does.

## Configuration

Configuration is environment variables read with `go-kit/env.Get(KEY, env.WithDefaultValue(<local default>))`, where the default points at the local docker-compose infrastructure. Read each key in one place (the bundle) and inject it; no `os.Getenv`, no config structs.

## Imports

Alias an import only on a name collision, and use the same alias for the same package everywhere (e.g. `orgdomain` for another service's `pkg/domain`). The `gci` section order in the golangci config decides grouping.

## Generic Go defaults that hold here

- Prefer the `slices` and `maps` packages over hand-written loops for search, sort, clone.
- Comma-ok type assertions (`v, ok := x.(T)`); for errors use `errors.As`.
- Unexport by default; exporting later is cheap, unexporting is a breaking change.
