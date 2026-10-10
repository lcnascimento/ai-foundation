#!/usr/bin/env bash
# Smoke install: add this Marketplace to a throwaway CLAUDE_CONFIG_DIR, install
# every plugin and fail unless each plugin and all of its dependencies end up
# installed and enabled. Catches broken sources and unresolved dependencies,
# which `claude plugin validate` does not report. Also fails unless every skill
# directory and every hook event of each plugin loads.
#
# Usage: scripts/smoke-install.sh [marketplace-dir]   (default: repo root)
set -euo pipefail

repo="$(cd "${1:-$(dirname "$0")/..}" && pwd)"
marketplace="$(jq -r '.name' "$repo/.claude-plugin/marketplace.json")"
# HTTPS, not owner/repo shorthand: CI runners have no SSH key for github.com.
official_source="https://github.com/anthropics/claude-plugins-official.git"

export CLAUDE_CONFIG_DIR="$(mktemp -d)"
trap 'rm -rf "$CLAUDE_CONFIG_DIR"' EXIT
echo "Isolated CLAUDE_CONFIG_DIR: $CLAUDE_CONFIG_DIR"
# Run outside any Project so its .claude/settings.json can't enable plugins.
cd "$CLAUDE_CONFIG_DIR"

# Cross-marketplace dependencies resolve only from marketplaces already added.
claude plugin marketplace add "$official_source"
claude plugin marketplace add "$repo"

plugins=($(jq -r '.plugins[].name' "$repo/.claude-plugin/marketplace.json"))
for plugin in "${plugins[@]}"; do
  echo "== install $plugin@$marketplace =="
  claude plugin install "$plugin@$marketplace"
  # Domain plugins ship defaultEnabled: false; a Project enables them.
  if [[ "$(jq -r '.defaultEnabled' "$repo/plugins/$plugin/.claude-plugin/plugin.json")" == "false" ]]; then
    claude plugin enable "$plugin@$marketplace"
  fi
done

installed="$(claude plugin list --json)"
echo "$installed" | jq .

fail=0
expect_enabled() {
  local id="$1"
  if echo "$installed" | jq -e --arg id "$id" \
    'any(.[]; .id == $id and .enabled == true and ((.errors // []) | length == 0))' >/dev/null; then
    echo "ok: $id installed and enabled"
  else
    echo "FAIL: $id is not installed, not enabled, or has load errors" >&2
    fail=1
  fi
}

for plugin in "${plugins[@]}"; do
  expect_enabled "$plugin@$marketplace"
  manifest="$repo/plugins/$plugin/.claude-plugin/plugin.json"
  for dep in $(jq -r --arg m "$marketplace" \
    '(.dependencies // [])[] | if type == "string" then . else .name + "@" + (.marketplace // $m) end
     | if test("@") then . else . + "@" + $m end' "$manifest"); do
    expect_enabled "$dep"
  done
done

for plugin in "${plugins[@]}"; do
  details="$(claude plugin details "$plugin@$marketplace")"

  # Every skill directory under plugins/<p>/skills/ must load as a skill.
  skills_line="$(echo "$details" | grep -E '^ *Skills \(' || true)"
  loaded=" $(echo "$skills_line" | sed -E 's/^ *Skills \([0-9]+\) *//; s/,/ /g') "
  for skill_md in "$repo"/plugins/"$plugin"/skills/*/SKILL.md; do
    skill="$(basename "$(dirname "$skill_md")")"
    if [[ "$loaded" == *" $skill "* ]]; then
      echo "ok: $plugin@$marketplace exposes skill $skill"
    else
      echo "FAIL: $plugin@$marketplace does not expose skill $skill" >&2
      echo "$details" >&2
      fail=1
    fi
  done

  # Every hook event a plugin declares in hooks/hooks.json must load with it.
  hooks_json="$repo/plugins/$plugin/hooks/hooks.json"
  [[ -f "$hooks_json" ]] || continue
  hooks_line="$(echo "$details" | grep -E '^ *Hooks \(' || true)"
  for event in $(jq -r '.hooks | keys[]' "$hooks_json"); do
    if echo "$hooks_line" | grep -qw "$event"; then
      echo "ok: $plugin@$marketplace registers a $event hook"
    else
      echo "FAIL: $plugin@$marketplace does not register its $event hook" >&2
      echo "$details" >&2
      fail=1
    fi
  done
done

exit "$fail"
