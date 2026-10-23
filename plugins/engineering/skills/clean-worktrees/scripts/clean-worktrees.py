#!/usr/bin/env python3

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

GUARDRAIL = Path("hooks") / "git-guardrail.py"
PLUGINS_DIR = Path(__file__).resolve().parents[4]


def sibling_guardrail():
    path = PLUGINS_DIR / "foundation" / GUARDRAIL
    return path if path.is_file() else None


def installed_guardrail():
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    try:
        installed = json.loads((config / "plugins" / "installed_plugins.json").read_text())["plugins"]
    except (OSError, ValueError, KeyError):
        installed = {}
    for key, installs in installed.items():
        if key.startswith("foundation@"):
            for install in installs:
                path = Path(install.get("installPath", "")) / GUARDRAIL
                if path.is_file():
                    return path
    return None


def load_guardrail():
    path = sibling_guardrail() or installed_guardrail()
    if not path:
        sys.exit("clean-worktrees: the foundation plugin's git-guardrail.py was not found")
    spec = importlib.util.spec_from_file_location("git_guardrail", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def worktrees(checkout):
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
    removal = git(checkout, "worktree", "remove", str(path))
    if removal.returncode != 0:
        return f"keep {rel} ({branch}): `git worktree remove` failed: {removal.stderr.strip()}"
    deletion = git(checkout, "branch", "-D", branch)
    if deletion.returncode != 0:
        return f"removed {rel}, kept branch {branch}: `git branch -D` failed: {deletion.stderr.strip()}"
    return f"removed {rel} ({branch})"


def main():
    start = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
    guardrail = load_guardrail()
    all_worktrees = worktrees(start)
    if not all_worktrees:
        sys.exit(f"clean-worktrees: {start} is not in a git repository")
    checkout = all_worktrees[0]["path"]
    root = (checkout / ".claude" / "worktrees").resolve()
    mine = [w for w in all_worktrees[1:] if w["path"].resolve().parent == root]
    remotes = {"origin"} | {guardrail.branch_remote(str(checkout), w["branch"]) for w in mine if w["branch"]}
    for remote in sorted(remotes):
        fetch = git(checkout, "fetch", "--prune", "--quiet", remote)
        if fetch.returncode != 0:
            print(f"warning: `git fetch --prune {remote}` failed, proving against stale refs: {fetch.stderr.strip()}")
    for worktree in mine:
        print(clean(guardrail, checkout, worktree))
    return 0


if __name__ == "__main__":
    sys.exit(main())
