#!/usr/bin/env bash
set -euo pipefail

environment=$(git rev-parse --show-toplevel)/docs/agents/environment.md
[[ -f $environment ]] || exit 0
limit=$(awk '
	/^## / { in_section = ($0 == "## Concurrency") }
	in_section && /^- Max implementers:/ { sub(/^- Max implementers:[ \t]*/, ""); print; found = 1; exit }
	END { exit !found }
' "$environment") || exit 0
[[ $limit =~ ^[1-9][0-9]*$ ]] ||
	{ echo "max-implementers: '- Max implementers:' in $environment must be a positive integer, got '$limit'" >&2; exit 1; }
echo "$limit"
