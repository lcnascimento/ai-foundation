# Routing

App Router only; there is no `pages/` directory. For special-file APIs (`params` shape, `generateMetadata`, `not-found`, `proxy.ts`), read the bundled Next docs of the installed version.

## Layout of `app/`

- One route group per shell: `(auth)` for unauthenticated pages, `(dashboard)` for the app. Each group owns its `layout.tsx`, `loading.tsx` and `error.tsx`; the root has `global-error.tsx`.
- URL sections are plain nested folders (`brand/audience/contacts`). A route group exists only when it changes the shell.
- Route-private components go in the group's `_components/` with a barrel. A component a second group needs moves to `shared/components/`.
- Default exports only where Next requires them (`page`, `layout`, `loading`, `error`); everything else is a named export.
- Keep the route list in one registry that the sidebar, breadcrumbs and links read from; never hard-code the same paths in two places.

## Loading and streaming

- The group layout wraps its async server shell in `<Suspense fallback={<ShellSkeleton />}>`, and the skeleton mirrors the shell's layout.
- Await data in the component that needs it, behind its own `<Suspense>`, so the surrounding layout paints first. A page that awaits data only one section uses blocks the whole page.
- A page with nothing to stream needs no `loading.tsx` of its own; the group's covers it.

## Errors

- A server component that cannot render throws `new Error(message, { cause })`; the nearest `error.tsx` catches it. Data failures are not rendered as inline text from the shell.
- `error.tsx` and `global-error.tsx` are client components that report the error through the Project's error tracker in `useEffect` (never `console.error`), show `error.digest` so the user can quote it, and offer `reset`. Their strings are translated like any other UI (see [i18n](i18n.md)); `global-error.tsx` renders outside the providers, so it loads its messages itself.

## Metadata and assets

- Static `metadata` lives in the root layout; a page adds its own `metadata`/`generateMetadata` when it has a distinct title.
- Fonts come from `next/font`, exposed as a CSS variable (`--font-sans`) that the Tailwind theme reads.
- Analytics and error-tracking scripts load after hydration (`next/script` with `strategy="afterInteractive"` or `lazyOnload`, or the library's deferred component), never in the critical bundle.
