#!/usr/bin/env bash
set -euo pipefail

key='- Max implementers:'
environment=$(git rev-parse --show-toplevel)/docs/agents/environment.md
[[ -f $environment ]] || exit 0
limit=$(awk -v key="$key" '
	/^## / { in_section = ($0 == "## Concurrency") }
	in_section && index($0, key) == 1 { value = substr($0, length(key) + 1); sub(/^[ \t]*/, "", value); print value; found = 1; exit }
	END { exit !found }
' "$environment") || exit 0
[[ $limit =~ ^[1-9][0-9]*$ ]] ||
	{ echo "max-implementers: '$key' in $environment must be a positive integer, got '$limit'" >&2; exit 1; }
echo "$limit"
