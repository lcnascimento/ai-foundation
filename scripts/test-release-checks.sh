#!/usr/bin/env bash
# Tests for check-version-bump.sh and tag-releases.sh against throwaway git
# repos: each case builds a base and a PR branch and asserts pass or fail.
#
# Usage: scripts/test-release-checks.sh
set -euo pipefail

scripts="$(cd "$(dirname "$0")" && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.com
export GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.com

failures=0

set_version() { # <plugin> <version>
  mkdir -p "plugins/$1/.claude-plugin"
  printf '{"name":"%s","version":"%s"}\n' "$1" "$2" >"plugins/$1/.claude-plugin/plugin.json"
}

touch_file() { # <path>
  mkdir -p "$(dirname "$1")"
  echo "$RANDOM" >>"$1"
}

commit() { git add -A && git commit --quiet -m "$1"; }

# Fresh repo with foundation and engineering at 0.1.0 on main, on branch pr.
new_repo() {
  local dir="$work/$1"
  git init --quiet -b main "$dir"
  cd "$dir"
  set_version foundation 0.1.0
  set_version engineering 0.1.0
  touch_file docs/readme.md
  commit base
  git checkout --quiet -b pr
}

expect() { # <pass|fail> <case name> [expected output substring]
  local want="$1" name="$2" needle="${3:-}" out status=0
  out="$("$scripts/check-version-bump.sh" main pr 2>&1)" || status=$?
  local got=pass; ((status == 0)) || got=fail
  if [[ "$got" != "$want" ]] || [[ -n "$needle" && "$out" != *"$needle"* ]]; then
    echo "not ok - $name (want $want${needle:+ with '$needle'}, got $got)"
    sed 's/^/    /' <<<"$out"
    failures=$((failures + 1))
  else
    echo "ok - $name"
  fi
}

new_repo docs-only
touch_file docs/adr/0099-x.md && touch_file .github/workflows/ci.yml && commit docs
expect pass "change outside plugins needs no bump"

new_repo no-bump
touch_file plugins/foundation/skills/a/SKILL.md && commit change
expect fail "plugin change without bump fails and names the plugin" "FAIL foundation"

new_repo bump
touch_file plugins/foundation/skills/a/SKILL.md && set_version foundation 0.2.0 && commit change
expect pass "plugin change with bump passes"

new_repo downgrade
touch_file plugins/foundation/skills/a/SKILL.md && set_version foundation 0.0.9 && commit change
expect fail "lower version fails" "FAIL foundation"

new_repo two-one-bumped
touch_file plugins/foundation/a.md && touch_file plugins/engineering/b.md
set_version foundation 0.1.1 && commit change
expect fail "two plugins changed, only one bumped, fails on the other" "FAIL engineering"

new_repo two-both-bumped
touch_file plugins/foundation/a.md && touch_file plugins/engineering/b.md
set_version foundation 0.1.1 && set_version engineering 1.0.0 && commit change
expect pass "two plugins changed, both bumped independently"

new_repo new-plugin
set_version design 0.1.0 && touch_file plugins/design/skills/x/SKILL.md && commit add
expect pass "new plugin needs no prior version"

new_repo removed-plugin
git rm --quiet -r plugins/engineering && commit remove
expect pass "removed plugin passes"

new_repo base-moved
touch_file plugins/foundation/a.md && set_version foundation 0.2.0 && commit change
git checkout --quiet main && touch_file plugins/foundation/c.md && set_version foundation 0.2.0 && commit other
git checkout --quiet pr
expect fail "bump already taken on base fails" "FAIL foundation"

new_repo base-moved-elsewhere
touch_file docs/x.md && commit docs
git checkout --quiet main && touch_file plugins/foundation/c.md && set_version foundation 0.2.0 && commit other
git checkout --quiet pr
expect pass "plugin changes only on base don't count against the PR"

# tag-releases.sh: tags each new version once, skips existing tags.
git init --quiet --bare "$work/remote.git"
new_repo tags
git checkout --quiet main
git remote add origin "$work/remote.git" && git push --quiet origin main
"$scripts/tag-releases.sh" >/dev/null
set_version engineering 0.2.0 && commit bump && git push --quiet origin main
out="$("$scripts/tag-releases.sh")"
tags="$(git ls-remote --tags --refs origin | awk '{print $2}' | sort | tr '\n' ' ')"
want="refs/tags/engineering--v0.1.0 refs/tags/engineering--v0.2.0 refs/tags/foundation--v0.1.0 "
if [[ "$tags" == "$want" && "$out" == *"skip foundation--v0.1.0"* && "$out" == *"tag  engineering--v0.2.0"* ]] &&
  [[ "$(git rev-parse 'engineering--v0.2.0^{commit}')" == "$(git rev-parse HEAD)" ]]; then
  echo "ok - tags new versions at HEAD and skips existing tags"
else
  echo "not ok - tag-releases (tags: $tags)"
  sed 's/^/    /' <<<"$out"
  failures=$((failures + 1))
fi

# A tag created locally whose push failed is pushed on the next run, not skipped.
set_version foundation 0.2.0 && commit bump-foundation && git push --quiet origin main
git tag -a foundation--v0.2.0 -m "foundation 0.2.0" # as if the earlier push had failed
out="$("$scripts/tag-releases.sh")"
if git ls-remote --tags --refs origin | grep -q 'refs/tags/foundation--v0.2.0$' &&
  [[ "$out" == *"push foundation--v0.2.0"* && "$out" == *"skip engineering--v0.2.0"* ]]; then
  echo "ok - pushes a local tag missing on the remote"
else
  echo "not ok - tag-releases retry"
  sed 's/^/    /' <<<"$out"
  failures=$((failures + 1))
fi

((failures == 0)) || { echo "$failures failing"; exit 1; }
echo "all passed"
