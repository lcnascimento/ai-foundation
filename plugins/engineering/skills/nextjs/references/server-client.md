# Server and client components

## Choosing the side

- Server by default. A file gets `"use client"` only when it uses state, effects, event handlers, context or a browser API.
- Push the directive to the leaf: extract the interactive part (a toggle, a switcher, a menu) into its own client file and render it from the server parent. Layouts, pages, shells and headers stay server components.
- A client component can still render server output it receives as `children` or props; use that to keep a provider client-side while its subtree stays on the server.
- Server components that use no async API call `useTranslations` directly; async ones use `getTranslations` (see [i18n](i18n.md)).

## Crossing the boundary

Every prop a server component passes to a client component is serialized into the HTML and every RSC payload.

- Pass only the fields the client uses: `<Profile name={user.name} />`, not the whole `user`.
- Serialization dedupes by reference, not value. Don't send both `items` and `items.filter(…)` or `items.toSorted()`: send `items` once and derive in the client.
- Props must be serializable: plain data, Dates, Promises, server actions. Functions other than server actions cannot cross.
- Data loaded on the server reaches client components through a context provider rendered by the server shell: `<WorkspaceProvider workspaces={…} activeWorkspaceId={…}>`. Client components read it with the provider's hook. They don't fetch it again.

## Request state on the server

- Module scope on the server is shared by concurrent requests. Request data (user, session, cookies) lives in arguments and props, never in module-level variables.
- Module scope is right for immutable, request-independent work: a font file, a static config, a regex. Load it once at module level instead of per request.

## Hydration

- A value that differs between server and client (theme, locale from the browser, time) is the usual mismatch.
- Theme is handled by `next-themes`, with `suppressHydrationWarning` on `<html>` only. Don't spread `suppressHydrationWarning` to fix other mismatches.
- A widget whose output depends on client-only state renders `null` until mounted (`const [mounted, setMounted] = useState(false)` + `useEffect(() => setMounted(true), [])`) and reserves its space so the layout doesn't shift.
- Prefer moving the value to a cookie the server can read; then no guard is needed.
