# Styling

Tailwind CSS v4, CSS-first. Styling is utility classes only: no CSS modules, no CSS-in-JS, no inline `style` except for values computed at runtime.

## Where the config lives

- The theme lives in `ui`'s global stylesheet: `@import "tailwindcss"`, `@custom-variant dark (&:is(.dark *))`, `@theme inline` tokens and `@layer base`. Change tokens there.
- The app's `globals.css` imports `ui`'s stylesheet and adds `@source` for every package whose classes must be scanned. A new package with components needs a new `@source` line.
- `tailwind.config.ts` files are not loaded under v4. Don't add configuration to them.

## Tokens

- Colours are OKLCH CSS custom properties exposed as semantic tokens (`bg-background`, `text-primary`, `text-muted-foreground`, `chart-1`…). Use the semantic token; when no token fits (a success/danger trend colour), add one to the theme in both `:root` and `.dark` instead of writing `text-green-600`.
- Dark mode is the `.dark` class set by `next-themes`. Tokens already switch with it, so `dark:` variants are only for the rare case a token doesn't cover.
- Fonts and radii come from theme variables (`--font-sans`, `--radius-*`).

## Classes

- Merge conditional or overridable classes with `cn()`; accept a `className` prop on every component and merge it last.
- Reuse the data-attribute and group variants shadcn components expose (`data-[state=open]:…`, `group-data-[collapsible=icon]:…`) instead of mirroring their state in React.
- Class order is Prettier's (`prettier-plugin-tailwindcss`, which also sorts inside `cn` and `cva`); run the formatter instead of ordering by hand.
