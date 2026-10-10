# Safety

Bugs we cause ourselves: panics and silent corruption in ordinary code. For attackers, see [security](security.md); for concurrent access, [concurrency](concurrency.md).

## Nil

- A typed nil pointer stored in an interface is not `== nil`. A function returning an interface (including `error`) returns a literal `nil` on the nil path, never a nil `*T` variable.
- Writing to a nil map panics. Initialize maps in the constructor, or lazily in the method that writes.
- A nil channel blocks forever on send and receive.
- Design types whose zero value is either usable or obviously invalid; a constructor that must be called is `New`, and the zero value of an enum is its "unknown" member.

## Slices and maps

- `append` reuses the backing array when capacity allows, so two slices can silently share memory. When you append to a slice you don't own, force a copy: `append(s[:len(s):len(s)], x)` or `slices.Clone`.
- A method that returns an internal slice or map returns `slices.Clone`/`maps.Clone`, or callers mutate your state.
- A small subslice of a large array keeps the whole array alive; clone it when you keep it long-term.

## Numbers

- Integer conversions truncate silently (`int64` → `int32` wraps). Check bounds against `math.MaxInt32`/`math.MinInt32` before converting values that come from outside.
- Integer division by zero panics; guard the divisor.
- Compare floats with a tolerance, never `==`. Money is integer minor units or `math/big`, never `float64`.

## Resources

- `defer` runs at function exit, not per loop iteration. Inside a loop, move the body (open, `defer Close`, use) into its own function.
- Close what you open on every path; check the `Close` error when it can lose data (files written, transactions).

## Initialization

No `init()` with side effects and no ordering assumptions between files: wire everything through fx constructors. Package-level `var`s are for loggers, tracers, metrics, sentinels and test-shrinkable tunables only.
