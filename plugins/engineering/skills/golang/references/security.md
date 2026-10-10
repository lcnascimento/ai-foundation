# Security

## Trust boundaries

Untrusted data enters at transport (requests, consumed messages) and at bridges (responses from systems we don't own). Validate there: request DTOs carry `validate:` tags and are validated before `ToDomain()`; a value used as a database, collection, file or key name (a tenant slug, say) is validated with its `Validate()` before use. Code behind the boundary trusts it.

Before reporting a vulnerability, trace the value back to where it enters and check for validation upstream; report what is reachable.

## Injection

- Queries are parameterized (driver placeholders, BSON filter documents built from typed values), never built by string concatenation.
- `exec.Command(name, args...)` with separate arguments, never `sh -c` with interpolated input.
- File access scoped to an allowed root with `os.Root` (Go 1.24+); `filepath.Clean` + `strings.HasPrefix` alone is not a path check.
- HTML goes through `html/template`.

## Secrets and crypto

- Secrets come from the environment (`env.Get`) with no real default; they never appear in code, logs, error attributes or test fixtures.
- Tokens and IDs that must be unguessable use `crypto/rand`, never `math/rand`.
- Compare secrets with `crypto/subtle.ConstantTimeCompare`.
- Passwords: Argon2id or bcrypt. Encryption: AES-GCM or `x/crypto` primitives. Check every crypto error and fail closed.

## Errors to clients

Clients see the Kind-derived status, the Code and safe reasons only (`errors.SafeReasons`). Driver messages, stack traces and internal attributes stay in logs.

## HTTP servers and clients

- Servers set `ReadHeaderTimeout`, `ReadTimeout`, `WriteTimeout` and `IdleTimeout`; a zero timeout is unbounded.
- Outbound requests carry a context with a deadline (`http.NewRequestWithContext`).
- Never trust client-supplied identity headers (`X-Forwarded-For`, `X-User-ID`) without the gateway guaranteeing them.

## Tooling

Run `govulncheck ./...` (or the Makefile target) when dependencies change. `gosec` findings are fixed, or suppressed with a `//nolint:gosec // <reason>` that explains why the input is safe.
