# Lint, format and typecheck

The rules live in the repo's configs. Read them there; this file holds only how to work with them.

- ESLint 9 flat config, layered in the `eslint-config` tooling package: `base` (typescript-eslint type-checked rules, import order) → `react` (React, hooks, jsx-a11y) → `next` (`@next/next`). Each package's `eslint.config.js` extends the most specific preset that matches its code: a package with `.tsx` components extends `react`, the app extends `next`.
- Prettier formats; ESLint doesn't. Run `make format` before `make lint`, and let both rewrite the file instead of fixing order and spacing by hand.
- tsconfig: packages extend `library.json`, apps extend `nextjs.json`, both from the `typescript-config` tooling package. Don't repeat options the preset sets.
- A lint or type error is fixed at its cause. `eslint-disable`, `@ts-ignore`, `@ts-expect-error` and `any` are not ways to make a check pass; when a rule is wrong for the whole repo, change the preset in its own commit and say why.
- Import order and type-only imports are enforced by the config (`import-x/order`, `consistent-type-imports`); write imports however and let `--fix` sort them.
