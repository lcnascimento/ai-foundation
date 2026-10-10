# Section: forge

Records the Project's forge, its CLI and host, and the commit, PR and CI conventions, so skills read them from a file instead of inferring them from `git remote` at runtime (ADR-0007).

## Runs when

`engineering` is enabled. Without it, ask nothing and render nothing here.

## Detect

- `docs/agents/forge.md`: its `# Forge: <forge> (<host>)` heading, its `Repository` line, its `Default branch` line and its `## Commits` paragraph are the previous answers.
- `git remote get-url origin` (else the first remote): its host and `<owner>/<repo>` path. Host `github.com` proposes GitHub; host `gitlab.com` or any host containing `gitlab` proposes GitLab with that host. Any other host proposes nothing: ask.
- `git symbolic-ref --short refs/remotes/origin/HEAD` (strip `origin/`): the default branch; else `main`.
- `git log --oneline -20`: whether history exists and whether most subjects already follow Conventional Commits (`type(scope): ...`).
- `.github/workflows/*.yml` and `.gitlab-ci.yml`: whether CI exists.

## Ask

1. The forge and host: GitHub or GitLab, recommending the previous answer, else the one proposed from the remote. The CLI follows the forge.
2. The repository (`<owner>/<repo>`) and the default branch, recommending the previous answers, else the detected ones.
3. The commit convention: `git-log` (recommended) or `conventional`. Recommend the previous answer, else `git-log`; mention `conventional` when the history already follows it.

## Render

Placeholders that follow the forge:

| Placeholder | GitHub | GitLab |
| - | - | - |
| `{{forge}}` | `GitHub` | `GitLab` |
| `{{cli}}` | `gh` | `glab` |
| `{{host_env}}` | `GH_HOST` | `GITLAB_HOST` |
| `{{change}}` | `pull request` | `merge request` |
| `{{create}}` | `gh pr create --base {{default_branch}}` | `glab mr create --target-branch {{default_branch}}` |
| `{{view}}` | `gh pr view` | `glab mr view` |
| `{{checks}}` | `gh pr checks --watch` | `glab ci status --live` |
| `{{ci_logs}}` | `gh run view --log-failed` | `glab ci trace` |
| `{{ci_config}}` | `.github/workflows/` | `.gitlab-ci.yml` |

`{{commit_convention}}` is one of these paragraphs, verbatim:

- `git-log`: `Follow the style of \`git log\` (subject length, tense, prefixes, body). With no history, write an imperative sentence without a prefix, e.g. "Add order export endpoint".`
- `conventional`: `Use Conventional Commits: \`<type>(<optional scope>): <imperative summary>\`, with \`feat\`, \`fix\`, \`docs\`, \`refactor\`, \`test\`, \`chore\`, \`ci\` or \`build\` as the type, and \`!\` or a \`BREAKING CHANGE:\` footer for breaking changes.`

`{{ci}}` is, verbatim, `CI is defined in \`{{ci_config}}\` and is the deterministic gate: a {{change}} merges only when it passes. Read a failing run with \`{{ci_logs}}\`.` when CI exists, else `No CI is configured yet.`

**`docs/agents/forge.md`**, owned Markdown, every placeholder filled (fill the ones nested in `{{create}}` and `{{ci}}` too):

```markdown
# Forge: {{forge}} ({{host}})

This Project's code lives on {{forge}} at `{{host}}`. Use the `{{cli}}` CLI for every forge operation ({{change}}s, review, CI). Read the forge from this file; never infer it from `git remote`. Issues live in the issue tracker (`docs/agents/issue-tracker.md`), never in the forge.

- Repository: `{{repo}}`
- Default branch: `{{default_branch}}`
- When a `{{cli}}` command runs outside this repo, set `{{host_env}}={{host}}`.

## Commits

{{commit_convention}}

## {{forge}} {{change}}s

- Work on a branch, never on `{{default_branch}}`.
- Open: `{{create}}`, with the title following the commit convention and the body following the Project language.
- Inspect: `{{view}}`; wait for checks with `{{checks}}`.
- Merge only after review and green checks.

## CI

{{ci}}
```

## Agent skills entries

```markdown
### Forge

{{forge}} at `{{host}}` through the `{{cli}}` CLI, repository `{{repo}}`. See `docs/agents/forge.md`.
```

## Checklist

- The `{{cli}}` CLI installed and authenticated for `{{host}}` (verify with `{{cli}} auth status --hostname {{host}}`).
- Branch protection for `{{default_branch}}` configured on {{forge}}, so merges go through a reviewed {{change}}.
