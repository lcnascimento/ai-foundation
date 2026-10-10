#!/usr/bin/env bash
# Principles index (ADR-0004): on SessionStart and SubagentStart, inject one line
# per Principle of this plugin (name + `description` from its reference
# frontmatter) plus the instruction to load and cite it.
#
# Plugin-agnostic: every plugin that owns Principles ships an identical copy at
# hooks/principles-index.sh (tests/principles-index.test.sh enforces it) and
# keeps the full texts in skills/principles/references/<name>.md, each with a
# one-line `description:` in its frontmatter.
#
# Contract: reads the hook event JSON on stdin; writes
# {"hookSpecificOutput":{"hookEventName":<event>,"additionalContext":<index>}}.
# Pure bash + awk: hooks run on user machines where jq may be missing.
set -euo pipefail

root="${CLAUDE_PLUGIN_ROOT:?CLAUDE_PLUGIN_ROOT is not set}"
refs="$root/skills/principles/references"
[ -d "$refs" ] || exit 0

event="$(cat | tr -d '\n' | sed -n 's/.*"hook_event_name"[[:space:]]*:[[:space:]]*"\([A-Za-z]*\)".*/\1/p')"
event="${event:-SessionStart}"

# First "name" in plugin.json is the plugin's own (author.name comes later).
plugin="$(sed -n 's/^[[:space:]]*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$root/.claude-plugin/plugin.json" | head -n 1)"

shopt -s nullglob
files=("$refs"/*.md)
[ "${#files[@]}" -eq 0 ] && exit 0
first="$(basename "${files[0]}" .md)"

index="$(
  echo "# Principles ($plugin)"
  echo
  echo "Development Principles to apply while working; each line says when one applies. Before applying a Principle, load its full text with the Skill tool: \`$plugin:principles <name>\` (e.g. \`$plugin:principles $first\`). Never apply one from its index line alone. In your final reply, cite each Principle that changed a decision and the specific choice it changed."
  echo
  for f in "${files[@]}"; do
    desc="$(awk '
      NR == 1 && $0 != "---" { exit }
      NR > 1 && $0 == "---" { exit }
      /^description:/ {
        sub(/^description:[[:space:]]*/, "")
        if ($0 ~ /^".*"$/) { $0 = substr($0, 2, length($0) - 2); gsub(/\\"/, "\"") }
        else if ($0 ~ /^'\''.*'\''$/) { $0 = substr($0, 2, length($0) - 2); gsub(/'\'''\''/, "'\''") }
        print; exit
      }' "$f")"
    echo "- **$(basename "$f" .md)**: $desc"
  done
)"

json_escape() {
  awk 'BEGIN { ORS = "" }
    {
      gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); gsub(/\t/, "\\t"); gsub(/\r/, "")
      if (NR > 1) print "\\n"
      print
    }'
}

printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}\n' \
  "$event" "$(printf '%s' "$index" | json_escape)"
