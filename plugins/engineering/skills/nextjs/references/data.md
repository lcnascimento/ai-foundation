# Data

This skill has no rules for Next caching (`"use cache"`, `revalidate`, Cache Components), client-side query caching or forms; read the bundled Next docs and the Project's code when a task needs them.

## Reads

- Server components read data by calling functions in an `actions/` file marked `"use server"`. Those functions call the `api` package and return parsed domain types.
- Client components get data as props or from a context provider fed by the server shell (see [server-client](server-client.md)). There is no client-side fetching library (no SWR, no `useEffect` + `fetch`).
- The `api` package returns a discriminated result (`{ kind: "ok"; data } | { kind: "error"; error }`, see [typescript](typescript.md) rule 1). The caller narrows on `kind`; on error a server component throws `new Error(message, { cause })` for `error.tsx`.
- Validate cookie- or URL-supplied IDs against the data you fetched before passing them down (an unknown workspace ID falls back to the first one the user has).

## Mutations and context switches

- A mutation is a `"use server"` function called from a client component inside `startTransition`, followed by `router.refresh()` so the server tree re-reads.
- Switching UI context (workspace, brand, locale) is a cookie write, not a server round-trip: the client writes the cookie through the writer in `shared/cookies/`, then calls `router.refresh()` inside `startTransition`. The server shell re-reads the cookie. A `TransitionProvider` exposes `isPending`, and the shell shows its skeleton while it is true.
- Cookie names and max-ages are constants exported from `shared/cookies/`, shared by the writer and the server reader.
- Every `"use server"` function is a public endpoint. Parse its arguments as `unknown` at the top and check authentication and authorization inside the function itself; a layout or page check doesn't protect it.

## Waterfalls

- Independent awaits run together: `const [a, b] = await Promise.all([getA(), getB()])`.
- Start a promise early and await it in the branch that needs it; an early return doesn't wait on data it never uses.
- Sibling server components that each fetch run in parallel only if no parent awaits first. Move each fetch into the component that renders it instead of awaiting everything in the page.
- Wrap a call that several components make in one request in `React.cache()`. Give it primitive arguments: it compares with `Object.is`, so an inline object argument never hits.
- Work the response doesn't depend on (audit logs, analytics) runs in `after()` from `next/server`.
