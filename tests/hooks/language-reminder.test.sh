#!/usr/bin/env bash
# Contract test for the Project language reminder hook, stdin -> stdout.
#
#   - hooks/hooks.json wires hooks/language-reminder.sh to UserPromptSubmit;
#   - a Project language in CLAUDE.md (else AGENTS.md) yields valid
#     hookSpecificOutput JSON naming that language;
#   - no instructions file, no language line or an English language yields no output.
#
# Usage: tests/hooks/language-reminder.test.sh
# Needs: bash, jq.
set -euo pipefail

repo="$(cd "$(dirname "$0")/../.." && pwd)"
plugin="$repo/plugins/foundation"
hook="$plugin/hooks/language-reminder.sh"

fail=0
failed() { echo "FAIL: $*" >&2; fail=1; }

[ -x "$hook" ] || { echo "FAIL: $hook missing or not executable" >&2; exit 1; }
jq -e '(.hooks.UserPromptSubmit // []) | any(.[].hooks[]; .type == "command" and (.command | contains("${CLAUDE_PLUGIN_ROOT}/hooks/language-reminder.sh")))' \
  "$plugin/hooks/hooks.json" >/dev/null || failed "hooks.json does not run language-reminder.sh on UserPromptSubmit"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

line() { printf -- '- **Project language: %s.** Talk to the user in %s.\n' "$1" "$1"; }

# run <dir> [via-cwd]: the project dir comes from CLAUDE_PROJECT_DIR, or from the event's cwd.
run() {
  local event="{\"hook_event_name\":\"UserPromptSubmit\",\"cwd\":\"$1\",\"prompt\":\"/engineering:implement AI-12\"}"
  if [ "${2:-}" = via-cwd ]; then
    printf '%s' "$event" | env -u CLAUDE_PROJECT_DIR "$hook"
  else
    printf '%s' "$event" | CLAUDE_PROJECT_DIR="$1" "$hook"
  fi
}

# expect <name> <dir> <language> [via-cwd]
expect() {
  local out
  out="$(run "$2" "${4:-}")" || { failed "$1: hook exited non-zero"; return; }
  jq -e --arg l "$3" '.hookSpecificOutput.hookEventName == "UserPromptSubmit"
    and (.hookSpecificOutput.additionalContext | contains("Reply to the user in " + $l + ","))' \
    <<<"$out" >/dev/null || failed "$1: unexpected output: $out"
}

# expect_none <name> <dir>
expect_none() {
  local out
  out="$(run "$2")" || { failed "$1: hook exited non-zero"; return; }
  [ -z "$out" ] || failed "$1: expected no output, got: $out"
}

mkdir -p "$tmp/claude" && { echo "# p"; echo; echo "## Language"; echo; line "Portuguese (pt-BR)"; } >"$tmp/claude/CLAUDE.md"
expect "CLAUDE.md" "$tmp/claude" "Portuguese (pt-BR)"
expect "cwd fallback" "$tmp/claude" "Portuguese (pt-BR)" via-cwd

mkdir -p "$tmp/agents" && line "Spanish" >"$tmp/agents/AGENTS.md"
expect "AGENTS.md fallback" "$tmp/agents" "Spanish"

mkdir -p "$tmp/both" && echo "# no language" >"$tmp/both/CLAUDE.md" && line "French" >"$tmp/both/AGENTS.md"
expect "CLAUDE.md without the line falls back to AGENTS.md" "$tmp/both" "French"

mkdir -p "$tmp/escape" && line 'Pig "Latin" \ dialect' >"$tmp/escape/CLAUDE.md"
expect "escaping" "$tmp/escape" 'Pig "Latin" \ dialect'

mkdir -p "$tmp/none"
expect_none "no instructions file" "$tmp/none"

mkdir -p "$tmp/noline" && echo "# nothing here" >"$tmp/noline/CLAUDE.md"
expect_none "no language line" "$tmp/noline"

mkdir -p "$tmp/english" && line "English" >"$tmp/english/CLAUDE.md"
expect_none "English" "$tmp/english"

if [ "$fail" -eq 0 ]; then echo "ok: language reminder hook"; fi
exit "$fail"
