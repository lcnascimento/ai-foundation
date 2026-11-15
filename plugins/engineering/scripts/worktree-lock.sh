#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

fail() {
	echo "worktree-lock: $*" >&2
	exit 1
}

pid=${CLAUDE_PID:-}
session=${CLAUDE_CODE_SESSION_ID:-}
[[ $pid =~ ^[0-9]+$ ]] || fail "CLAUDE_PID is not set; run this from a Claude Code session"

lock=$(git rev-parse --absolute-git-dir)/agent.lock
stale=$lock.stale.$$

field() {
	sed -n "s/^$1=//p" <<<"$2"
}

mine() {
	[[ $(field pid "$1") == "$pid" ]] || [[ -n $session && $(field session "$1") == "$session" ]]
}

describe() {
	echo "held by pid $(field pid "$1"), session $(field session "$1"), since $(field started_at "$1")"
}

alive() {
	local err
	err=$(kill -0 "$1" 2>&1) || [[ $err == *"not permitted"* ]]
}

usage() {
	fail "usage: worktree-lock.sh acquire [--wait <seconds>] | release"
}

acquire() {
	local owner wait=0 deadline
	case $# in
	0) ;;
	2) [[ $1 == --wait && $2 =~ ^[0-9]+$ ]] || usage; wait=$2 ;;
	*) usage ;;
	esac
	deadline=$((SECONDS + wait))
	tmp=$(mktemp "$lock.XXXXXX")
	trap 'rm -f "$tmp" "$stale"' EXIT
	printf 'pid=%s\nsession=%s\nstarted_at=%s\n' "$pid" "$session" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >"$tmp"
	until ln "$tmp" "$lock" 2>/dev/null; do
		owner=$(cat "$lock" 2>/dev/null) || continue
		mine "$owner" && return 0
		if alive "$(field pid "$owner")"; then
			if ((SECONDS < deadline)); then
				sleep $((deadline - SECONDS < 30 ? deadline - SECONDS : 30))
				continue
			fi
			echo "worktree-lock: $(git rev-parse --show-toplevel) is $(describe "$owner")" >&2
			exit 3
		fi
		mv "$lock" "$stale" 2>/dev/null || continue
		if [[ $(cat "$stale") == "$owner" ]]; then
			echo "worktree-lock: took over the lock $(describe "$owner"): that pid is gone" >&2
		else
			ln "$stale" "$lock" 2>/dev/null || true
		fi
		rm -f "$stale"
	done
}

release() {
	local owner
	owner=$(cat "$lock" 2>/dev/null) || return 0
	if mine "$owner"; then
		rm -f "$lock"
	else
		echo "worktree-lock: left the lock alone, it is $(describe "$owner")" >&2
	fi
}

command=${1:-}
[[ $# -gt 0 ]] && shift
case $command in
acquire) acquire "$@" ;;
release) [[ $# -eq 0 ]] || usage; release ;;
*) usage ;;
esac
