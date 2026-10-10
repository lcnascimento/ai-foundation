# Testing

The level for each place is in `SKILL.md`. This file holds how to write and place each level.

## All levels

- Name tests by behaviour (`"editor can create and edit but not delete"`) and assert literal expected values (`"R$ 1.234,56"`), not values recomputed by the code under test.
- Colocate tests with the code: `names.ts` → `names.test.ts`, `workspace-switcher.tsx` → `workspace-switcher.test.tsx`. No `__tests__/` folders.
- Every package or app with tests has a `test` script and a `vitest.config.ts`, and is listed in the root Vitest workspace; a test file nobody runs doesn't exist.

## `unit`

- Vitest with `environment: "node"`. Pure functions only: formatters, ability factories, parsers and guards, the data shaping you pulled out of a server component or a `"use server"` function.
- Table-driven with `it.each` when cases differ only in data.

## `component`

- In the app: Vitest + Testing Library with `environment: "jsdom"` (declare `jsdom` in that package). Render the client component inside the providers it needs, query by role and accessible name, and drive it with `@testing-library/user-event`.
- Mock only the edge you can't run: `next/navigation` (`useRouter().refresh`) and `"use server"` imports. Don't mock providers; render the real one with test props.
- In `ui`: every component and primitive has a CSF3 story next to it (`button.stories.tsx`): `const meta = { component, tags: ["autodocs"], argTypes } satisfies Meta<typeof X>`, one named export per meaningful state. Interactions are `play` functions. Stories run as tests through the Storybook Vitest addon, with the a11y addon on.

## `e2e`

- Playwright against a production build (`next build && next start`) and the real backend, in CI. Only the critical flows the spec lists; everything reachable at a lower level is tested there.
- Select by role and accessible name, as a user would. Each test creates the data it needs and leaves the environment usable for the next.
