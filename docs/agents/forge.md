# Forge: GitHub (github.com)

This Project's code lives on GitHub at `github.com`. Use the `gh` CLI for every forge operation (pull requests, review, CI). Read the forge from this file; never infer it from `git remote`. Issues live in the issue tracker (`docs/agents/issue-tracker.md`), never in the forge.

- Repository: `lcnascimento/ai-foundation`
- Default branch: `main`
- When a `gh` command runs outside this repo, set `GH_HOST=github.com`.

## Commits

Use Conventional Commits: `<type>(<optional scope>): <imperative summary>`, with `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci` or `build` as the type, and `!` or a `BREAKING CHANGE:` footer for breaking changes.

## GitHub pull requests

- Work on a branch, never on `main`.
- Open: `gh pr create --base main`, with the title following the commit convention and the body following the Project language.
- Inspect: `gh pr view`; wait for checks with `gh pr checks --watch`.
- Merge only after review and green checks.

## CI

CI is defined in `.github/workflows/` and is the deterministic gate: a pull request merges only when it passes. Read a failing run with `gh run view --log-failed`.
