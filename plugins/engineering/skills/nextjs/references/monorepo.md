# Monorepo

pnpm workspaces (`apps/*`, `packages/*`, `tooling/*`) with Turborepo. The root `Makefile` is the entry point for quality gates (`make lint`, `make format`, `make test`, `make typecheck`, `make build`); CI and git hooks call `make`, so run it the same way.

## Internal packages are just-in-time

Internal packages ship TypeScript source, not builds:

- `package.json` `exports` maps each subpath straight to source: `"./workspace": { "types": "./src/workspace.ts", "default": "./src/workspace.ts" }`. Every exported path must point at a file that exists.
- There is no `build` script in an internal package.
- Every internal package an app imports is listed in that app's `transpilePackages` in `next.config.ts`.
- Packages are `@<scope>/<name>`, `private`, version `0.0.0`, `"type": "module"`, and extend the shared configs in `tooling/` (`@<scope>/typescript-config`, `@<scope>/eslint-config`).

## Adding a package

Create one when code is needed by more than one app, or has no knowledge of the app (design system, API client, i18n catalogue, shared types, formatters). Wire it in one change: `package.json` with `exports`, `tsconfig.json` extending `library.json`, `eslint.config.js` extending the right preset, a `vitest.config.ts` if it has tests, the app's `dependencies` (`"workspace:*"`) and `transpilePackages`.

## Boundaries

- Dependencies point one way: apps → packages. `api` and `utils` may depend on `types`; `ui` depends on no internal package.
- Import packages through their subpath exports (`@<scope>/api/workspace`) or their barrel; never reach into another package's `src/`.
- Inside an app, import app code through the `@/*` alias.
- Declare every dependency a package imports in that package's own `package.json`. Hoisting (`shamefully-hoist`) makes an undeclared import resolve locally and break elsewhere.
- In the monorepo, `next` and its bundled docs resolve under the app (`apps/<app>/node_modules/next`), not the root.
