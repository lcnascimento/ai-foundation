#!/usr/bin/env bash
# Contract test for the Principles index hook (ADR-0004), stdin -> stdout.
#
# For every plugin that owns Principles (plugins/*/skills/principles/references),
# or the plugin dirs given as arguments, and for both SessionStart and
# SubagentStart:
#   - hooks/hooks.json wires hooks/principles-index.sh to both events;
#   - hooks/principles-index.sh is identical to foundation's copy;
#   - the output is hookSpecificOutput JSON for the event received;
#   - additionalContext has exactly one line per reference, with its name and
#     its frontmatter `description` (YAML-parsed), plus the load/cite instruction;
#   - each plugin stays within its budget and all indexes together stay under
#     SessionStart's 10,000-char cap.
#
# Usage: tests/principles-index.test.sh [plugin-dir...]
# Needs: bash, jq, python3 with PyYAML.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
canonical="$repo/plugins/foundation/hooks/principles-index.sh"
total_cap=10000
# Per-plugin budgets leave room for the other plugins in the shared cap.
budget() { case "$1" in foundation) echo 3000 ;; engineering) echo 7000 ;; *) echo "$total_cap" ;; esac; }

if [ "$#" -gt 0 ]; then
  plugins=("$@")
else
  plugins=()
  for d in "$repo"/plugins/*/; do
    [ -d "$d/skills/principles/references" ] && plugins+=("${d%/}")
  done
fi
[ "${#plugins[@]}" -gt 0 ] || { echo "FAIL: no plugin with Principles found" >&2; exit 1; }

fail=0
failed() { echo "FAIL: $*" >&2; fail=1; }
total=0

yaml_description() {
  python3 - "$1" <<'PY'
import sys, yaml
text = open(sys.argv[1], encoding="utf-8").read()
_, fm, _ = text.split("---\n", 2)
print(yaml.safe_load(fm)["description"])
PY
}

for dir in "${plugins[@]}"; do
  dir="$(cd "$dir" && pwd)"
  plugin="$(jq -r .name "$dir/.claude-plugin/plugin.json")"
  hook="$dir/hooks/principles-index.sh"
  echo "== $plugin =="

  [ -x "$hook" ] || { failed "$plugin: $hook missing or not executable"; continue; }
  cmp -s "$hook" "$canonical" || failed "$plugin: hooks/principles-index.sh differs from foundation's copy"

  for event in SessionStart SubagentStart; do
    jq -e --arg e "$event" \
      '(.hooks[$e] // []) | any(.[].hooks[]; .type == "command" and (.command | contains("${CLAUDE_PLUGIN_ROOT}/hooks/principles-index.sh")))' \
      "$dir/hooks/hooks.json" >/dev/null || failed "$plugin: hooks.json does not run principles-index.sh on $event"
  done

  names=()
  for f in "$dir"/skills/principles/references/*.md; do names+=("$(basename "$f" .md)"); done

  for event in SessionStart SubagentStart; do
    out="$(printf '{"session_id":"t","hook_event_name":"%s","cwd":"/tmp"}' "$event" \
      | CLAUDE_PLUGIN_ROOT="$dir" "$hook")" || { failed "$plugin/$event: hook exited non-zero"; continue; }
    got_event="$(jq -r .hookSpecificOutput.hookEventName <<<"$out")" || { failed "$plugin/$event: output is not JSON"; continue; }
    [ "$got_event" = "$event" ] || failed "$plugin/$event: hookEventName is '$got_event'"
    ctx="$(jq -r .hookSpecificOutput.additionalContext <<<"$out")"

    lines="$(grep -c '^- \*\*' <<<"$ctx" || true)"
    [ "$lines" -eq "${#names[@]}" ] || failed "$plugin/$event: $lines index lines for ${#names[@]} Principles"
    for n in "${names[@]}"; do
      want="- **$n**: $(yaml_description "$dir/skills/principles/references/$n.md")"
      [ "$(grep -cxF -- "$want" <<<"$ctx")" -eq 1 ] || failed "$plugin/$event: no exact index line for '$n'"
    done
    grep -qF "\`$plugin:principles <name>\`" <<<"$ctx" || failed "$plugin/$event: missing load instruction ($plugin:principles <name>)"
    grep -qF "In your final reply, cite each Principle that changed a decision" <<<"$ctx" || failed "$plugin/$event: missing citation instruction"
  done

  size="${#ctx}"
  max="$(budget "$plugin")"
  echo "$plugin index: ${#names[@]} Principles, $size chars (budget $max)"
  [ "$size" -lt "$max" ] || failed "$plugin: index is $size chars, budget $max"
  total=$((total + size))
done

echo "all indexes: $total chars (cap $total_cap)"
[ "$total" -lt "$total_cap" ] || failed "indexes add up to $total chars, cap $total_cap"

[ "$fail" -eq 0 ] && echo "ok: Principles index contract holds"
exit "$fail"
