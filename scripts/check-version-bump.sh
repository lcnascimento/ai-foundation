#!/usr/bin/env bash
# Version bump check (ADR-0006): fail when a change touches plugins/<p>/**
# without raising that plugin's `version` in plugins/<p>/.claude-plugin/plugin.json.
# Each plugin is checked on its own; files outside plugins/ never need a bump.
#
# Changed files come from the merge base of <base> and <head>, so commits that
# landed on <base> after the branch point don't count. The version is compared
# against <base> itself, so a bump must still be ahead of what <base> ships.
# A plugin that doesn't exist on <base> is new and passes; a deleted one passes.
#
# Usage: scripts/check-version-bump.sh <base-ref> [head-ref]   (head default: HEAD)
set -euo pipefail

base="${1:?usage: $0 <base-ref> [head-ref]}"
head="${2:-HEAD}"

# Prints the plugin.json version at <ref>, or nothing when the file is absent.
version_at() {
  { git show "$2:plugins/$1/.claude-plugin/plugin.json" 2>/dev/null || true; } | jq -r '.version // empty'
}

# True when semver $1 is strictly greater than $2 (X.Y.Z only).
semver_gt() {
  local IFS=.
  local -a a=($1) b=($2)
  for i in 0 1 2; do
    ((10#${a[i]} > 10#${b[i]})) && return 0
    ((10#${a[i]} < 10#${b[i]})) && return 1
  done
  return 1
}

merge_base="$(git merge-base "$base" "$head")"
plugins=($(git diff --name-only "$merge_base" "$head" -- plugins/ | cut -d/ -f2 | sort -u))

if ((${#plugins[@]} == 0)); then
  echo "No plugin changed; no version bump required."
  exit 0
fi

semver='^[0-9]+\.[0-9]+\.[0-9]+$'
failed=0
for plugin in "${plugins[@]}"; do
  new="$(version_at "$plugin" "$head")"
  old="$(version_at "$plugin" "$base")"
  if [[ -z "$new" ]] && ! git cat-file -e "$head:plugins/$plugin" 2>/dev/null; then
    echo "ok   $plugin: removed"
  elif [[ ! "$new" =~ $semver ]]; then
    echo "FAIL $plugin: version '$new' in plugins/$plugin/.claude-plugin/plugin.json is not X.Y.Z"
    failed=1
  elif [[ -z "$old" ]]; then
    echo "ok   $plugin: new plugin at $new"
  elif [[ ! "$old" =~ $semver ]] || semver_gt "$new" "$old"; then
    echo "ok   $plugin: $old -> $new"
  else
    echo "FAIL $plugin: files changed but version is $new (base has $old); bump plugins/$plugin/.claude-plugin/plugin.json"
    failed=1
  fi
done

exit "$failed"
