#!/usr/bin/env python3
"""Remove the worktrees under `<checkout>/.claude/worktrees/` whose work is merged.

Fetches `origin` with `--prune`, then for each worktree there prints one line:

- `skip <path> (<branch>): <why>`: uncommitted changes or untracked files (ignored
  files don't count), or an open PR/MR;
- `removed <path> (<branch>)`: the branch passes the foundation git guardrail's
  merge proof, so `git worktree remove <path>` (never `--force`) and
  `git branch -D <branch>` ran;
- `keep <path> (<branch>): <why>`: anything else.

The merge proof is the guardrail's own `merge_proven`, imported from the
`foundation` plugin, so the script and the guardrail never disagree. The user's
checkout is never pulled or checked out.

Usage: clean-worktrees.py [checkout]   (default: the current directory)
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REMOTE = "origin"


def guardrail_path():
    """git-guardrail.py of the sibling `foundation` plugin in this repo, else the installed one."""
    here = Path(__file__).resolve()
    sibling = here.parents[4] / "foundation" / "hooks" / "git-guardrail.py"
    if sibling.is_file():
        return sibling
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    try:
        installed = json.loads((config / "plugins" / "installed_plugins.json").read_text())["plugins"]
    except (OSError, ValueError, KeyError):
        installed = {}
    for key, installs in installed.items():
        if key.startswith("foundation@"):
            for install in installs:
                path = Path(install.get("installPath", "")) / "hooks" / "git-guardrail.py"
                if path.is_file():
                    return path
    return None


def load_guardrail():
    path = guardrail_path()
    if not path:
        sys.exit("clean-worktrees: the foundation plugin's git-guardrail.py was not found")
    spec = importlib.util.spec_from_file_location("git_guardrail", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def worktrees(checkout):
    """(path, branch or None, prunable) of every worktree, the main one first."""
    out, entry = [], {}
    for line in git(checkout, "worktree", "list", "--porcelain").stdout.splitlines() + [""]:
        key, _, value = line.partition(" ")
        if key == "worktree":
            entry = {"path": Path(value), "branch": None, "prunable": False}
        elif key == "branch":
            entry["branch"] = value.removeprefix("refs/heads/")
        elif key == "prunable":
            entry["prunable"] = True
        elif not line and entry:
            out.append(entry)
            entry = {}
    return out


def unproven_reason(guardrail, checkout, branch):
    remote = guardrail.branch_remote(str(checkout), branch)
    pushed = git(checkout, "merge-base", "--is-ancestor", branch, f"refs/remotes/{remote}/{branch}").returncode == 0
    merged = guardrail.forge_prs(str(checkout), remote, branch, "merged")
    parts = [] if pushed else [f"commits not on {remote}"]
    parts.append("forge unknown or unreachable" if merged is None else "no merged PR")
    return "merge not proven: " + ", ".join(parts)


def clean(guardrail, checkout, worktree):
    path, branch = worktree["path"], worktree["branch"]
    rel = os.path.relpath(path, checkout)
    if worktree["prunable"] or not path.is_dir():
        return f"keep {rel} ({branch}): directory missing, `git worktree prune` drops it"
    if not branch:
        return f"keep {rel}: detached HEAD"
    if Path.cwd().resolve().is_relative_to(path.resolve()):
        return f"keep {rel} ({branch}): the current directory is inside it"
    status = git(path, "status", "--porcelain")
    if status.returncode != 0 or status.stdout.strip():
        return f"skip {rel} ({branch}): uncommitted changes or untracked files"
    remote = guardrail.branch_remote(str(checkout), branch)
    open_prs = guardrail.forge_prs(str(checkout), remote, branch, "open")
    if open_prs:
        return f"skip {rel} ({branch}): PR #{open_prs[0]['number']} is open"
    if not guardrail.merge_proven(str(checkout), branch):
        return f"keep {rel} ({branch}): {unproven_reason(guardrail, checkout, branch)}"
    for args in (["worktree", "remove", str(path)], ["branch", "-D", branch]):
        done = git(checkout, *args)
        if done.returncode != 0:
            return f"keep {rel} ({branch}): `git {' '.join(args)}` failed: {done.stderr.strip()}"
    return f"removed {rel} ({branch})"


def main():
    start = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
    guardrail = load_guardrail()
    all_worktrees = worktrees(start)
    if not all_worktrees:
        sys.exit(f"clean-worktrees: {start} is not in a git repository")
    checkout = all_worktrees[0]["path"]
    fetch = git(checkout, "fetch", "--prune", "--quiet", REMOTE)
    if fetch.returncode != 0:
        print(f"warning: `git fetch --prune {REMOTE}` failed, proving against stale refs: {fetch.stderr.strip()}")
    root = checkout / ".claude" / "worktrees"
    for worktree in all_worktrees[1:]:
        if worktree["path"].parent == root:
            print(clean(guardrail, checkout, worktree))
    return 0


if __name__ == "__main__":
    sys.exit(main())
