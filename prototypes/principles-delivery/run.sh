#!/usr/bin/env bash
# PROTOTYPE (AI-11): runs every scenario against every variant headlessly, in a fresh copy of the fixture.
# Usage: run.sh <runs-dir> [rep]   (variant "0-none" = no plugin, the baseline)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
runs="$1"; rep="${2:-1}"
jobs=()
for v in 0-none $(ls "$here/variants"); do
  while IFS=$'\t' read -r id expected prompt; do
    jobs+=("$v|$id|$prompt")
  done < "$here/scenarios.tsv"
done
one() {
  IFS='|' read -r v id prompt <<<"$1"
  dir="$runs/$v/$id-r$rep"; rm -rf "$dir"; mkdir -p "$dir"; cp -R "$here/fixture/." "$dir/"
  plug=(); [ "$v" = 0-none ] || plug=(--plugin-dir "$here/variants/$v")
  (cd "$dir" && claude -p "$prompt" "${plug[@]}" --output-format stream-json --verbose \
     --dangerously-skip-permissions --max-turns 25 > "$runs/$v/$id-r$rep.jsonl" 2>"$runs/$v/$id-r$rep.err" || true)
  echo "done $v $id r$rep"
}
export -f one; export here runs rep
printf '%s\0' "${jobs[@]}" | xargs -0 -P 8 -I{} bash -c 'one "$@"' _ {}
