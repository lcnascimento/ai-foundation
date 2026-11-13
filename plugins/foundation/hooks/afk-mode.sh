#!/usr/bin/env bash
# Pure bash + awk: hooks run on machines where jq may be missing.
set -euo pipefail

[ "${AI_FOUNDATION_AFK:-}" = "1" ] || exit 0

event="$(cat | tr -d '\n' | sed -n 's/.*"hook_event_name"[[:space:]]*:[[:space:]]*"\([A-Za-z]*\)".*/\1/p')"
event="${event:-SessionStart}"

read -r -d '' rule <<'EOF' || true
# AFK mode

No human is in this session (AI_FOUNDATION_AFK=1). Nobody will answer a question, so a question stalls the session for good.

- Never use AskUserQuestion, and never wait for a confirmation or an approval.
- Decide every reversible choice yourself, then record the assumption in a comment on the issue it concerns.
- Stop only for the stops of the know-when-to-stop Principle (load it with `foundation:principles know-when-to-stop`), and report each stop as a BLOCKED/TRIED/NEED block.
- When you must stop, put all your questions, numbered, in a single comment, then end the session.
- Never close a Spec: merging its PR is the approval.
- Post only four kinds of AFK comment: Assumption, BLOCKED/TRIED/NEED, Questions and Delivery. Write them in the Project's language, with no signature, on the Spec or the Ticket they concern.
EOF

json_escape() {
  awk 'BEGIN { ORS = "" }
    {
      gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); gsub(/\t/, "\\t"); gsub(/\r/, "")
      if (NR > 1) print "\\n"
      print
    }'
}

printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}\n' \
  "$event" "$(printf '%s' "$rule" | json_escape)"
