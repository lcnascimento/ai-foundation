#!/usr/bin/env bash
set -euo pipefail

fail() {
	echo "worktree: $*" >&2
	exit 1
}

root=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")

default_base() {
	git -C "$root" fetch --quiet origin || fail "git fetch origin failed; pass --base <ref> to work offline"
	git -C "$root" symbolic-ref --quiet --short refs/remotes/origin/HEAD ||
		fail "origin/HEAD is not set (run git remote set-head origin --auto) or pass --base <ref>"
}

worktree_dir() {
	[[ $1 =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] && git check-ref-format --branch "$1" >/dev/null 2>&1 ||
		fail "name must be a branch name made of letters, digits, '.', '_' and '-' (e.g. abc-12), got '$1'"
	echo "$root/.claude/worktrees/$1"
}

branch_exists() {
	git -C "$root" show-ref --verify --quiet "refs/heads/$1"
}

registered() {
	git -C "$root" worktree list --porcelain | grep -qxF "worktree $1"
}

copy_included() {
	local dir=$1 file
	[[ -f $dir/.worktreeinclude ]] || return 0
	while IFS= read -r file; do
		[[ -e $dir/$file ]] && continue
		echo "==> Copying $file"
		mkdir -p "$(dirname "$dir/$file")"
		cp -p "$root/$file" "$dir/$file"
	done < <(git -C "$root" ls-files --others --ignored --exclude-from="$dir/.worktreeinclude")
}

setup_commands() {
	local environment=$1/docs/agents/environment.md
	[[ -f $environment ]] || return 0
	awk '/^## / { in_setup = ($0 == "## Setup") } in_setup && /^- `/ { split($0, parts, "`"); print parts[2] }' "$environment"
}

run_setup() {
	local dir=$1 command
	while IFS= read -r command; do
		echo "==> $command"
		(cd "$dir" && bash -c "$command" </dev/null) || fail "setup command failed: $command"
	done < <(setup_commands "$dir")
}

usage() {
	fail "usage: worktree.sh add <name> [--base <ref>] [--reset] | remove <name>"
}

add() {
	local name=${1:-} base="" reset="" dir
	[[ $# -gt 0 ]] && shift
	while [[ $# -gt 0 ]]; do
		case $1 in
		--base) [[ $# -ge 2 ]] || usage; base=$2; shift 2 ;;
		--reset) reset=1; shift ;;
		*) usage ;;
		esac
	done
	dir=$(worktree_dir "$name")
	[[ -n $base ]] || base=$(default_base)
	if registered "$dir"; then
		echo "==> Reusing $dir"
		if [[ -n $reset ]]; then
			[[ -z $(git -C "$dir" status --porcelain) ]] ||
				fail "$dir has uncommitted changes; commit or discard them before --reset"
			git -C "$dir" switch --quiet -C "$name" "$base"
		fi
	elif [[ -n $reset ]]; then
		git -C "$root" worktree add --quiet -B "$name" "$dir" "$base"
	else
		branch_exists "$name" && fail "branch '$name' already exists; pass --reset to recreate it from $base"
		git -C "$root" worktree add --quiet -b "$name" "$dir" "$base"
	fi
	copy_included "$dir"
	run_setup "$dir"
	echo "$dir"
}

remove() {
	[[ $# -eq 1 ]] || usage
	local name=$1 dir merged_into
	dir=$(worktree_dir "$name")

	if branch_exists "$name"; then
		merged_into=$(git rev-parse --verify --quiet "$name@{upstream}" || git rev-parse HEAD)
		git merge-base --is-ancestor "$name" "$merged_into" ||
			fail "branch '$name' has unmerged commits; only the user may delete it"
	fi

	if registered "$dir"; then
		git -C "$root" worktree remove "$dir" ||
			fail "$dir has uncommitted changes or untracked files; commit them or ask the user"
	else
		echo "==> No worktree at $dir"
	fi

	if branch_exists "$name"; then
		git branch --quiet -d "$name"
	else
		echo "==> No branch $name"
	fi
}

command=${1:-}
[[ $# -gt 0 ]] && shift
case $command in
add) add "$@" ;;
remove) remove "$@" ;;
*) usage ;;
esac
