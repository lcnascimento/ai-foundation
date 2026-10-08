#!/usr/bin/env bash
set -euo pipefail

rules_dir="${CLAUDE_PLUGIN_ROOT}/rules"

[ -d "$rules_dir" ] || exit 0

shopt -s nullglob
files=("$rules_dir"/*.md)
[ "${#files[@]}" -eq 0 ] && exit 0

for f in "${files[@]}"; do
  cat "$f"
  echo
done
