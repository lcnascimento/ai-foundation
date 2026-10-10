---
name: nextjs
description: House conventions for React and Next.js App Router code - where a file goes, server vs client components, data reads and mutations, state, styling, i18n, TypeScript rules and test levels. Use when writing, reviewing or testing React, Next.js or TypeScript (.ts/.tsx) code.
license: MIT
metadata:
  status: derived
  upstreams:
    - repo: vercel-labs/agent-skills
      sha: 063bee94c3f4df8453406c830b0a7df0f2860278
      path: skills/react-best-practices
      license: MIT
    - repo: backnotprop/pstack
      sha: 3a604672c46cd8187d2b19980eae0a34f9f91138
      path: skills/typescript-best-practices
      license: MIT
---

# Next.js

House conventions for the stack: Next.js App Router, React 19, a pnpm + Turborepo monorepo, shadcn, Tailwind v4, next-intl, Storybook, ESLint 9 and Vitest. Where the Project's code or `CODING_STANDARDS.md` says otherwise, the Project wins.

This skill holds what the code and the framework docs don't tell you. For Next.js and React APIs (special files, `params`, caching, `proxy.ts`, config options), read the docs bundled with the installed version at `node_modules/next/dist/docs/` (in the monorepo, under the app, e.g. `apps/web/node_modules/next/dist/docs/`), and fall back to Context7 when they are absent. Lint and format rules live in the repo's ESLint and Prettier configs; read them there.

## Where code goes

Decide this first for every change. Walk the list top to bottom and stop at the first match:

| Place | What goes there |
| --- | --- |
| `app/` | Routes only: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, inside route groups such as `(auth)` and `(dashboard)`. Server components. |
| `app/<group>/_components/` | Components used by one route group, with a barrel `index.ts`. The server shell that fetches the group's data lives here. |
| `providers/` | Client context providers, one per concern, with a barrel. Pattern in [state](references/state.md). |
| `shared/` | App-wide pieces used by more than one route group: `shared/components/`, `shared/cookies/` (cookie names, writers, readers), `shared/_messages/` (app i18n namespaces). |
| `actions/` | `"use server"` functions: the reads server components call and the mutations client code calls. |
| `packages/<name>` | Code more than one app needs or that has no app knowledge: `ui` (design system), `api` (backend client), `i18n`, `types`, `utils`. See [monorepo](references/monorepo.md). |

Components are **server by default**. Put `"use client"` on the leaf that needs state, effects, event handlers or browser APIs, and keep layouts, pages and shells on the server. When a server tree needs one interactive piece, extract that piece into its own client file instead of marking the parent. Details in [server-client](references/server-client.md).

## Test levels

| Level | Runner | What it covers |
| --- | --- | --- |
| `unit` | Vitest, `environment: "node"` | Pure TypeScript: `packages/*` logic (`utils`, `auth` abilities, `i18n` config), cookie parsing, data shaping pulled out of server components and actions. |
| `component` | Vitest + Testing Library in the app; Storybook stories run as tests in `ui` | Client components, hooks and providers in the app; every `ui` component and primitive through its story. |
| `e2e` | Playwright against the real stack (production build + backend), in CI | The critical flows the spec lists: pages, server components and actions end to end. |

Async server components and `"use server"` functions have no `component` level: move their logic into plain functions tested at `unit`, and cover the wiring with `e2e`. Conventions in [testing](references/testing.md).

## References

Read the reference before writing code in its area.

| Reference | Read when |
| --- | --- |
| [typescript](references/typescript.md) | Writing any `.ts`/`.tsx`: the 16 type rules. |
| [routing](references/routing.md) | Adding or changing a route, layout, loading/error state or metadata. |
| [server-client](references/server-client.md) | Choosing a component's side, passing props across the boundary, hydration. |
| [data](references/data.md) | Reading data, mutating, switching context (workspace, locale), awaiting in parallel. |
| [state](references/state.md) | Adding client state or a context provider; effects and memoization. |
| [components](references/components.md) | Writing a `ui` component, a business primitive or an app composite. |
| [styling](references/styling.md) | Writing classes, tokens, dark mode or Tailwind config. |
| [i18n](references/i18n.md) | Any user-facing string, message namespace or locale handling. |
| [monorepo](references/monorepo.md) | Adding a package, an export, a dependency or an import across packages. |
| [testing](references/testing.md) | Writing or placing a test or a story. |
| [lint](references/lint.md) | A lint or format failure, or editing the ESLint/Prettier/tsconfig presets. |
