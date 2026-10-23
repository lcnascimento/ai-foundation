#!/usr/bin/env bash
# Project language reminder: on UserPromptSubmit, read the `**Project language: X.**`
# line that setup-ai-foundation writes into CLAUDE.md (else AGENTS.md) and remind
# the agent to talk to the user in X. A prompt that is only a slash command or a
# ticket ID leaves an all-English context, which otherwise pulls replies to English.
#
# Contract: reads the hook event JSON on stdin; writes
# {"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":<reminder>}},
# or nothing when no Project language is set or it is English.
# Pure bash + sed/awk: hooks run on user machines where jq may be missing.
set -euo pipefail

input="$(cat | tr -d '\n')"
dir="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$dir" ]; then
  dir="$(printf '%s' "$input" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
fi
[ -n "$dir" ] || exit 0

for f in "$dir/CLAUDE.md" "$dir/AGENTS.md"; do
  [ -f "$f" ] || continue
  language="$(sed -n 's/.*\*\*Project language: \([^*]*\)\.\*\*.*/\1/p' "$f" | head -n 1)"
  [ -n "$language" ] && break
done
[ -n "${language:-}" ] || exit 0
case "$(printf '%s' "$language" | tr '[:upper:]' '[:lower:]')" in english*) exit 0 ;; esac

json_escape() {
  awk 'BEGIN { ORS = "" } { gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); gsub(/\t/, "\\t"); gsub(/\r/, ""); print }'
}

reminder="Reply to the user in $language, the Project language: every message, including progress updates and summaries of subagent reports."
printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' \
  "$(printf '%s' "$reminder" | json_escape)"
