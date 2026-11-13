#!/usr/bin/env bash
# Contract test for the AFK mode hook, stdin -> stdout.
#
#   - foundation's hooks/hooks.json runs hooks/afk-mode.sh on SessionStart and
#     SubagentStart, and no other plugin ships or wires it;
#   - with AI_FOUNDATION_AFK=1, on both events, the output is hookSpecificOutput
#     JSON for the event received, with the AFK rule in additionalContext;
#   - without AI_FOUNDATION_AFK=1 (unset, empty or another value), the hook
#     exits 0 and prints nothing.
#
# Usage: tests/afk-mode.test.sh
# Needs: bash, jq.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
foundation="$repo/plugins/foundation"
hook="$foundation/hooks/afk-mode.sh"

fail=0
failed() { echo "FAIL: $*" >&2; fail=1; }

run_hook() {
  local event="$1"; shift
  printf '{"session_id":"t","hook_event_name":"%s","cwd":"/tmp"}' "$event" \
    | env -u AI_FOUNDATION_AFK "$@" CLAUDE_PLUGIN_ROOT="$foundation" "$hook"
}

[ -x "$hook" ] || { echo "FAIL: $hook missing or not executable" >&2; exit 1; }

for event in SessionStart SubagentStart; do
  jq -e --arg e "$event" \
    '(.hooks[$e] // []) | any(.[].hooks[]; .type == "command" and (.command | contains("${CLAUDE_PLUGIN_ROOT}/hooks/afk-mode.sh")))' \
    "$foundation/hooks/hooks.json" >/dev/null || failed "foundation: hooks.json does not run afk-mode.sh on $event"
done

for dir in "$repo"/plugins/*/; do
  dir="${dir%/}"
  [ "$dir" = "$foundation" ] && continue
  name="$(basename "$dir")"
  [ -e "$dir/hooks/afk-mode.sh" ] && failed "$name: ships its own hooks/afk-mode.sh"
  if [ -f "$dir/hooks/hooks.json" ] && grep -qF "afk-mode.sh" "$dir/hooks/hooks.json"; then
    failed "$name: hooks.json wires afk-mode.sh"
  fi
done

rule_fragments=(
  "AFK mode"
  "Never use AskUserQuestion"
  "record the assumption in a comment on the issue"
  "foundation:principles know-when-to-stop"
  "BLOCKED/TRIED/NEED"
  "all your questions, numbered, in a single comment"
  "end the session"
  "Never close a Spec"
  "Assumption, BLOCKED/TRIED/NEED, Questions and Delivery"
  "in the Project's language"
  "no signature"
)

for event in SessionStart SubagentStart; do
  out="$(run_hook "$event" AI_FOUNDATION_AFK=1)" || { failed "on/$event: hook exited non-zero"; continue; }
  got_event="$(jq -r .hookSpecificOutput.hookEventName <<<"$out")" || { failed "on/$event: output is not JSON"; continue; }
  [ "$got_event" = "$event" ] || failed "on/$event: hookEventName is '$got_event'"
  ctx="$(jq -r .hookSpecificOutput.additionalContext <<<"$out")"
  for frag in "${rule_fragments[@]}"; do
    grep -qF -- "$frag" <<<"$ctx" || failed "on/$event: rule misses '$frag'"
  done
done

for value in unset "" 0 true; do
  for event in SessionStart SubagentStart; do
    if [ "$value" = unset ]; then
      out="$(run_hook "$event")" || { failed "off($value)/$event: hook exited non-zero"; continue; }
    else
      out="$(run_hook "$event" AI_FOUNDATION_AFK="$value")" || { failed "off($value)/$event: hook exited non-zero"; continue; }
    fi
    [ -z "$out" ] || failed "off($value)/$event: hook printed '$out'"
  done
done

[ "$fail" -eq 0 ] && echo "ok: AFK mode hook contract holds"
exit "$fail"
