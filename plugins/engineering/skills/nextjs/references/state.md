# State

The URL and cookies are the source of truth for which workspace, brand and locale are active; client state never holds them on its own. This skill has no rules for a global client store: reach for one only when the spec asks for it.

## Context providers

Cross-cutting client state is a React Context in `providers/`, one file per concern, always in this shape:

```tsx
"use client";

const BrandContext = createContext<BrandContextValue | null>(null);

export function BrandProvider({ brands, activeBrandId, children }: BrandProviderProps) {
  const activeBrand = useMemo(
    () => brands.find((b) => b.id === activeBrandId) ?? null,
    [brands, activeBrandId],
  );
  const setActiveBrand = useCallback((id: BrandId) => { /* cookie + refresh, see data.md */ }, []);
  const value = useMemo(() => ({ brands, activeBrand, setActiveBrand }), [brands, activeBrand, setActiveBrand]);
  return <BrandContext value={value}>{children}</BrandContext>;
}

export function useBrand(): BrandContextValue {
  const ctx = useContext(BrandContext);
  if (ctx === null) throw new Error("useBrand must be used within BrandProvider");
  return ctx;
}
```

- The provider takes IDs and lists as props from the server shell and derives the active entity with `useMemo`.
- The context `value` is memoized; a fresh object literal re-renders every consumer on each render.
- Consumers call the throwing hook, never `useContext`/`use` on the bare context.
- Each provider is exported from the `providers/` barrel and mounted once, in the layout or shell that owns its data.

## Local state and effects

- Derive values during render. State that mirrors props, or an effect that sets state when a prop changes, is a bug: compute it, or reset with a `key`.
- Interaction logic runs in the event handler, not in an effect that watches a flag the handler set.
- Use the functional updater (`setItems((prev) => …)`) when the next state depends on the previous one; the callback then needs no state dependency.
- Expensive initial state uses the lazy initializer: `useState(() => build())`.
- Pending UI comes from `useTransition`'s `isPending`, not a hand-rolled `isLoading` state.
- A value read only inside a callback, or changing every frame (pointer position, timers), goes in a `useRef`, not state.
- `useEffectEvent` results never go in an effect's dependency array.

## Memoization

- `useMemo`/`useCallback` where identity matters (a context value, a dependency of another hook, a prop of a memoized child) or the work is expensive. A simple expression with a primitive result is computed inline.
- Never define a component inside another component; it remounts on every render.
- A non-primitive default prop (`items = []`) is hoisted to a module constant so it keeps its identity.
