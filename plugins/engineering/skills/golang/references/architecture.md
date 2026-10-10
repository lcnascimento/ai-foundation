# Architecture

## Flow

`cmd/<kind>/<name>/main.go` → `bundle/` (fx wiring) → `internal/{transport, application, idomain, repository, bridge}`, with the shared domain in the public `pkg/domain`.

Each binary is its own `fx.App`: an API server, a consumer and a worker are separate processes built from the same bundle pieces.

## Layers

- **transport** is thin: parse path and body, call one application method, write the response or the error (`httpserver/util.WriteResponse`, `WriteError`, `WriteID`). No business rules. Request DTOs carry `validate:` tags and convert to domain with `ToDomain()`; partial updates use `Apply(current)`.
- **application** holds the use case. Every method opens with its telemetry hook, calls domain, repositories and bridges through `contracts.go` interfaces, and returns errors through `a.onError(ctx, err)`.
- **domain** is pure: entities, value objects, sentinels, mutations (`type SchemaMutation func(current *Schema) (*Schema, error)`). No I/O, no telemetry. Shared types go in `pkg/domain`; logic private to the service goes in `internal/idomain`.
- **repository** persists the state this service owns. It translates driver errors into domain sentinels (`mongo.ErrNoDocuments` → `ErrXNotFound`, duplicate key → `ErrXAlreadyExists`) and returns other driver errors raw. It has no telemetry of its own; driver auto-instrumentation covers it.
- **bridge** talks to systems this service does not own: another service's API, a SaaS, a queue or workflow engine used as output. Same rules as a repository: translate the client's errors (`errors.As` against the client's error type, gRPC `status.Code`, HTTP status) into domain sentinels at the boundary.

Repository vs bridge: if the service would lose data when the system disappears, it is a repository; if it would lose a capability, it is a bridge.

## Dependency direction

Dependencies point inward. `domain` imports nothing from the service. `application` imports `domain` and its own `contracts.go`, never a concrete repository or bridge. Concrete types meet interfaces only in `bundle/`.

## Persistence models

Storage models and their mappers live in a nested `internal/` package under the repository (`internal/repository/<resource>/internal/{model.go,mapper.go}`), so nothing outside the repository can import them. The repository owns storage-managed fields (`version`, `created_at`, `updated_at`); the mapper leaves them zero.

## Decorators

Cross-cutting behaviour on a dependency (caching, retries) is a decorator that wraps the concrete type and is bound to its own interface (`CachedRepository` wraps `*Repository`, bound to `CachedSchemasRepository`). The consumer picks which one it depends on in its `contracts.go`.

## Idempotency

Operations that can be retried must tolerate "already done": deterministic IDs for workflows and jobs, "already exists"/"not found" treated as success where the end state matches, and checkpoints saved only after the effect is applied. Name the test after the property (`..._IsIdempotent`).
