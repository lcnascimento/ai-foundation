# TypeScript

Sixteen rules for every `.ts`/`.tsx` file, rewritten from `backnotprop/pstack` `typescript-best-practices`. They apply the `type-system-discipline` and `boundary-discipline` Principles; load them with `engineering:principles <name>` when you design a type or a boundary.

The shared tsconfig preset is `strict` with `noUncheckedIndexedAccess`, so index access yields `T | undefined`: handle it with `?.` and `??`, or with a non-empty type (rule 4), never `!`.

## Modeling

**1. Discriminated unions.** Model variants with a literal discriminant so contradictory states can't exist. No bag of optional fields. Pick one discriminant name per codebase (`kind`) and keep it.

```ts
// A result envelope is a union, not { data?: T; error?: string }
type Result<T> = { kind: "ok"; data: T } | { kind: "error"; error: string };
```

**2. Branded types.** Brand primitives that can be mixed up (IDs from different entities): `type WorkspaceId = string & { readonly __brand: "WorkspaceId" }`. Mint the brand once, in the parser at the boundary; downstream code trusts it.

**3. Constructive modeling.** Shape the type so the illegal value can't be built: `[T, ...T[]]` for non-empty, `[T, T][]` for pairs, `{ start; durationMs }` instead of `{ start; end }` with a comment.

**4. Simplest total type.** Keep `T[]` while every operation on it is total. Strengthen to `NonEmpty<T>` only where the loose type forces `!`, a cast or a "should never happen" throw; returning `T | undefined` is the other honest signature.

**5. `unknown` over `any`.** External data is `unknown` until parsed: API payloads, `JSON.parse`, cookies, `searchParams`, `localStorage`, `postMessage`, env vars.

## Parsing and narrowing

**6. Boundary validation.** Parse where data crosses in, into a named domain type, and trust the type inside. In this stack the boundaries are Next request APIs (`cookies()`, `headers()`, `params`, `searchParams`), `"use server"` arguments (callable by anyone), API responses and browser storage. Never re-validate deep in a call chain.

**7. Schemas before guards.** At a boundary, use the Project's schema library (Zod) and infer the type from it (`z.infer`). Use `safeParse` when failure is an expected branch. Zod stays at boundaries; inside, types are plain TypeScript. Add no new schema dependency for one guard.

**8. No `as` casts.** Cast only what the compiler has already verified. To remove one, find why inference fails: add a discriminant, narrow a wide source type, parse an untyped boundary, or use `satisfies`/a brand. `useLocale() as Locale` is the typical offender: parse with the guard instead.

**9. Narrowing hierarchy.** Discriminant `switch`/`if` > `in` > `typeof`/`instanceof` > user-defined guard > `as` after validation.

**10. Type guards verify the claim.** A guard that checks less than its `x is T` promises is worse than `as`. Name guards `isX`/`hasX`.

**11. Exhaustiveness.** Every `switch` over a union ends in a `never` default, so a new variant fails to compile instead of falling into a default arm:

```ts
default: {
  const _exhaustive: never = role;
  return _exhaustive; // void _exhaustive; in a statement switch
}
```

**12. `satisfies` over `as`.** `const config = { … } satisfies Config` checks the value and keeps its literal types.

## Signatures

**13. Derived types.** Reach for `Pick`, `Omit`, `Parameters`, `ReturnType`, `Awaited`, `typeof` and `z.infer` before declaring a new interface. One entity has one declaration, in the `types` package or the package that owns it; import it instead of redeclaring it. Domain enumerations are literal unions derived from an `as const` tuple, so a `Record<Union, …>` stays total:

```ts
export const locales = ["pt-BR", "en"] as const;
export type Locale = (typeof locales)[number];
```

**14. Object arguments.** Functions with more than one argument of similar type take one object, so call sites name every value. Skip it on hot paths (per-frame render, parsers).

## Behaviour

**15. Real tests.** Run the real thing and mock only what can't run locally (see [testing](testing.md)). Assert behaviour with literal expected values; delete `expect(true)` placeholders and tests that read back what they just assigned.

**16. Structured telemetry.** Shipped code reports through the Project's logger or error tracker with structured context (an id to debug from). No `console.log`/`console.error` in shipped code, error boundaries included.
