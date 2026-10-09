#!/usr/bin/env bash
# PROTOTYPE (AI-11): builds one throwaway plugin per Principle-delivery variant from pstack's principle skills.
# Usage: build.sh <pstack-checkout>
set -euo pipefail
src="$1/skills"
here="$(cd "$(dirname "$0")" && pwd)"
out="$here/variants"
rm -rf "$out"

body() { awk 'BEGIN{n=0} /^---$/{n++; next} n>=2' "$1"; }
desc() { sed -n 's/^description: *//p' "$1" | sed 's/^"//; s/"$//'; }
names() { for d in "$src"/principle-*; do basename "$d" | sed 's/^principle-//'; done; }

plugin() { # <dir> : manifest + SessionStart hook that cats rules/*.md
  mkdir -p "$1/.claude-plugin" "$1/hooks" "$1/rules"
  cat > "$1/.claude-plugin/plugin.json" <<JSON
{ "name": "principles-proto", "version": "0.0.0", "description": "PROTOTYPE AI-11" }
JSON
  cp "$here/../../plugins/foundation/hooks/hooks.json" "$1/hooks/"
  cp "$here/../../plugins/foundation/hooks/load-rules.sh" "$1/hooks/"
}

index() { # <how-to-load sentence>
  echo "# Principles"
  echo
  echo "Development principles to apply while working. Each line says when it applies. $1 Do not apply a principle from this one-liner alone."
  echo "In your final reply, name each principle that shaped a decision and the specific choice it changed."
  echo
  for n in $(names); do echo "- **$n**: $(desc "$src/principle-$n/SKILL.md")"; done
}

# A: always-on index Rule + one `principles` skill, full texts as references/ read on demand
a="$out/a-index-references"; plugin "$a"; mkdir -p "$a/skills/principles/references"
index 'To apply one, first invoke the `principles` skill with its name as argument (e.g. `principles prove-it-works`) and read the full text.' > "$a/rules/principles.md"
for n in $(names); do body "$src/principle-$n/SKILL.md" > "$a/skills/principles/references/$n.md"; done
cat > "$a/skills/principles/SKILL.md" <<'MD'
---
name: principles
description: Load the full text of a named development principle (see the Principles index) before applying it. Pass the principle name as argument, e.g. `prove-it-works`.
argument-hint: <principle-name>
---

Read `${CLAUDE_SKILL_DIR}/references/$ARGUMENTS.md` in full and apply it to the current work.
If the name doesn't match a file in `${CLAUDE_SKILL_DIR}/references/`, list that folder and pick the closest.
MD

# B: one model-invocable skill per principle, no index (routing by description only)
b="$out/b-skill-per-principle"; mkdir -p "$b/.claude-plugin"; cp "$a/.claude-plugin/plugin.json" "$b/.claude-plugin/"
for n in $(names); do
  mkdir -p "$b/skills/principle-$n"
  grep -v '^disable-model-invocation:' "$src/principle-$n/SKILL.md" > "$b/skills/principle-$n/SKILL.md"
done

# C: always-on index Rule + one model-invocable skill per principle (pstack's poteto-mode index, made always-on)
c="$out/c-index-skills"; plugin "$c"; cp -R "$b/skills" "$c/"
index 'To apply one, first invoke its skill (`principle-<name>`, e.g. `principle-prove-it-works`) and read the full text.' > "$c/rules/principles.md"

# D: everything as an always-on Rule (full texts through SessionStart)
d="$out/d-all-rules"; plugin "$d"
{ echo "# Principles"; echo; echo "In your final reply, name each principle that shaped a decision and the specific choice it changed."; echo
  for n in $(names); do body "$src/principle-$n/SKILL.md"; echo; done; } > "$d/rules/principles.md"

wc -c "$a/rules/principles.md" "$c/rules/principles.md" "$d/rules/principles.md"
