# Stack skills rewrite Community content into house norms

Each stack gets one derived Custom skill in `engineering`, written in house norms. We don't vendor Community skills for a stack. A stack skill's Upstreams are recorded as a list in `metadata.upstreams` (`repo`, `sha`, `path`, `license`), with `status: derived` and one `licenses/<owner>-<repo>` file per Upstream. When an Upstream ships no `LICENSE` file, its license file holds the standard text plus a note on where the license is declared.

The content we keep is rewritten into themed `references/`. Wherever it conflicts with the house norms extracted from remarks, the house norm wins in the text itself. A line survives the rewrite only if it changes the model's default behaviour or records a convention the code doesn't reveal. Personas, audit modes and sub-agent orchestration are dropped. Lint rules are read from the repo's config instead of restated.

- **`engineering:golang`**
  - Upstream: `samber/cc-skills-golang` (MIT).
  - References: architecture, layout, errors, DI, concurrency, observability, testing, style, safety, security, performance, troubleshooting.
  - Example house norm: go-kit errors with `WithCause`, never `%w`.
- **`engineering:nextjs`**
  - Upstreams: `vercel-labs/agent-skills` `react-best-practices`, and only the performance rules that change default behaviour; `backnotprop/pstack` `typescript-best-practices`, whose 16 rules become `references/typescript.md`.
  - References: typescript, routing, server-client, data, state, components, styling, i18n, monorepo, testing, lint.
  - Generic Next.js API knowledge is left to the docs bundled with the installed version (`node_modules/next/dist/docs/`, Context7 as fallback). The skill's job is house conventions, which no Upstream carries: reads through `"use server"` functions, cookie + `router.refresh()`, the throwing-hook Context pattern, JIT internal packages.

## Considered Options

- **Vendor the Community skills as-is** (ADR-0001's default): rejected.
  - For Go, 46 samber entries crowd the skill listing budget and compete for routing, and their defaults (`%w`, `samber/oops`, `samber/do`) contradict the house stack.
  - For Next.js, the candidates contradict the house too: SWR for client reads, a nullable context read through `use()`, the official `shadcn` skill's fixed `--no-monorepo`.
- **Copy selected Upstream skills byte for byte under `references/`** and add an overrides section, as Principles do (ADR-0004): rejected. Each loaded reference would carry rules the agent must then unlearn, plus hundreds of cross-references to skills that aren't installed.
- **Base `engineering:nextjs` on `next-best-practices`** (19 App Router references): rejected. Its vendor retired it in 2026, reporting that version-bundled docs plus the `AGENTS.md` emitted by `next dev` beat skills in their evals (100% vs up to 79%).
- **A separate TypeScript skill**: rejected. TS only appears in the frontend of this stack, so a separate skill would compete with `engineering:nextjs` for routing.

## Consequences

- Upstream updates are manual: read the Upstream diff and decide what to rewrite. There is no copy-plus-sha-bump path. The CI provenance check accepts the `metadata.upstreams` list.
- A stack skill assumes its house stack and has no rules for what the reference Project declares but doesn't exercise.
  - `engineering:golang` assumes go-kit, uber/fx, golangci-lint v2, OTel, testify and mockgen. It has no rules for HTTP router, databases, queues, workflow engines or tenancy.
  - `engineering:nextjs` assumes Next.js App Router, React 19, a pnpm + Turborepo monorepo, shadcn, Tailwind v4, next-intl, Storybook, ESLint 9 and Vitest. It has no rules for global client state, client-side query caching, forms, authorization or Next caching. Zod appears only as boundary validation.
- `SKILL.md` carries where code goes and the test level for each place, because every task in the stack starts by deciding where the code goes.
  - **Go:** layers `transport`, `application`, `domain`, `repository`, `bridge`. Domain, application and transport are tested at `unit`; repository and bridge at `component`.
  - **Next.js:** `app/` → `_components/` → `providers/` → `shared/` → `actions/` and the internal packages, plus the server-by-default / `"use client"`-at-leaves rule.
  - **Next.js test levels:**
    - `unit`: Vitest in node.
    - `component`: Vitest + Testing Library in the app; Storybook stories run as tests in `ui`.
    - `e2e`: Playwright against the real stack (production build + backend) for the critical flows listed in the spec, run in CI.
- A stack skill reaches `implement*` and the Standards axis of `engineering:code-review` by its description. A Project that wants a guarantee lists the skill in its `CODING_STANDARDS.md`. No vendored skill is derived for this.
