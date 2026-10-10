# Components

Three kinds, three places:

| Kind | Place | Knows about |
| --- | --- | --- |
| Design-system component (shadcn) | `packages/ui/src/components/` | Nothing app-specific |
| Business primitive (`PageHeader`, `EmptyState`, `MetricCard`) | `packages/ui/src/primitives/` | Domain shapes, but no i18n and no data fetching |
| App composite (`NavGroup`, `WorkspaceSwitcher`) | `apps/<app>/shared/components/` or a route's `_components/` | The app: i18n, providers, routes |

Before writing an app composite, check `ui` for a primitive that already does it (a switcher, an empty state) and use or extend it.

## `ui` components

- Add shadcn components with the shadcn CLI run inside `packages/ui`, so `components.json` (style, base color, icon library, aliases) applies. Match the generation already in the package (e.g. `forwardRef` + `displayName` vs function components with `data-slot`); don't mix two in one package.
- Variants use `cva`; class merging uses `cn()` from `ui`'s `lib/utils`; polymorphism uses Radix `Slot` with `asChild`.
- Props are `interface XProps extends React.ComponentProps<"button">, VariantProps<typeof xVariants>`. Export the component, its variants and its props type by name from the file and from the `ui` barrel.
- Every component and primitive ships a Storybook story (see [testing](testing.md)).

## Business primitives

- Every user-facing string arrives as a prop (`label`, `emptyMessage`); primitives never call next-intl. The app passes translated strings.
- Status colours come from tokens (see [styling](styling.md)), not raw palette classes.

## App composites

- Icons come from the library in `ui`'s `components.json` (`iconLibrary`), and a component-typed prop renders them: `icon?: LucideIcon` rendered as `<Icon />`.
- Heavy client-only widgets (charts, editors) load with `next/dynamic` so they stay out of the initial bundle.
- Large icon or component libraries imported through their root barrel go in `experimental.optimizePackageImports` in `next.config.ts`; keep the barrel import in code. Internal package barrels are fine as they are.

## JSX

- Conditional rendering uses a ternary (`count > 0 ? <Badge … /> : null`) whenever the condition can be `0`, `NaN` or `""`, which `&&` would render.
- An expensive subtree that toggles visibility often (tabs, dropdown panels) is wrapped in `<Activity mode={open ? "visible" : "hidden"}>` to keep its state instead of unmounting.
- Static JSX that doesn't depend on props is hoisted to a module constant.
