#!/usr/bin/env python3
"""Git guardrail: a PreToolUse hook (matcher `Bash`) that always denies the
actions only the human may take (ADR-0009).

Reads the tool call JSON on stdin. When any part of the command is forbidden,
prints a Claude Code permission decision (`deny`) naming the blocked command and
the `know-when-to-stop` Principle. Otherwise prints nothing and exits 0, leaving
the normal permission flow untouched.

Denied: force-push in any form, push to the default branch (resolved from
`origin/HEAD`, including implicit pushes), `gh pr merge`, `glab mr merge`,
`--no-verify`, `reset --hard`, `clean -f`, `worktree remove --force`,
`checkout .`, `restore .`, `stash drop`, `stash clear`, and `branch -D` unless
every branch named is proven merged (see `merge_proven`). Commands nested in
`eval`, `xargs` and shell `-c` scripts (`bash -c`, `bash -lc`, ...) are checked
too.

`engineering:clean-worktrees` imports this file for `merge_proven`,
`branch_remote` and `forge_prs`.
"""

import json
import os
import re
import shlex
import subprocess
import sys

SEPARATORS = {"(", ")"}
PREFIXES = {"sudo", "command", "env", "time", "nohup", "exec", "builtin"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
WHOLE_TREE = {".", "./", ":/", ":/."}

# git global options that take a separate value.
GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}
# `git push` long options that take a separate value (`--opt value`; `--opt=value` is one word).
PUSH_LONG_WITH_VALUE = {"--push-option", "--repo", "--receive-pack", "--exec"}
# `git push` short options that take a value: the rest of the cluster, else the next word.
PUSH_SHORT_WITH_VALUE = set("o")
# Shell short options that take a separate value (`bash -o pipefail -c ...`).
SHELL_SHORT_WITH_VALUE = set("oO")
# xargs options that take a separate value.
XARGS_WITH_VALUE = {
    "-I", "-L", "-n", "-P", "-s", "-d", "-E", "-a", "-R", "-S",
    "--arg-file", "--delimiter", "--max-lines", "--max-args", "--max-procs", "--max-chars",
    "--process-slot-var",
}
# `git commit` short options that consume the rest of their cluster or the next word.
COMMIT_SHORT_WITH_VALUE = set("mFCctS")
# `git branch` options that take a separate value.
BRANCH_WITH_VALUE = {"-u", "--set-upstream-to", "--contains", "--no-contains", "--merged", "--no-merged", "--points-at", "--sort", "--format"}

UNPROVEN_DELETE = (
    "`branch -D` deletes a branch whose merge can't be proven: its tip is neither in "
    "`<remote>/<default>` nor the head of a merged PR/MR"
)
STOP = (
    "Only the human may do this, in interactive and AFK sessions alike. "
    "Do not retry or work around it: follow the `know-when-to-stop` Principle "
    "(load it with `foundation:principles know-when-to-stop`) and raise a "
    "BLOCKED / TRIED / NEED block."
)
HAND_OFF = (
    "Do not retry or work around it. Under the `know-when-to-stop` Principle, hand "
    "the user the cleanup command ready to run (`{segment}`) and go on with the rest "
    "of the work."
)


def run(cmd, cwd):
    """stdout of `cmd`, or None when it fails, is missing or takes over 5 s."""
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def git(cwd, *args):
    return run(["git", "-C", cwd, *args], cwd)


def strip_heads(ref):
    for prefix in ("refs/heads/", "heads/"):
        if ref.startswith(prefix):
            return ref[len(prefix):]
    return ref


def default_branches(cwd, remote):
    """Default branch of `remote` from `<remote>/HEAD`, falling back to origin's.

    Without either, assume `main` and `master` so the guardrail errs on denying.
    """
    for name in dict.fromkeys([remote, "origin"]):
        ref = git(cwd, "symbolic-ref", "--quiet", "--short", f"refs/remotes/{name}/HEAD")
        if ref and "/" in ref:
            return {ref.split("/", 1)[1]}
    return {"main", "master"}


def branch_remote(cwd, branch):
    remote = git(cwd, "config", f"branch.{branch}.remote")
    return remote if remote and remote != "." else "origin"


def forge_repo(cwd, remote):
    """(kind, host, path) of `remote` when it is on GitHub or GitLab, else None."""
    url = git(cwd, "config", "--get", f"remote.{remote}.url") or ""
    m = re.match(r"^(?:[a-z+]+://)?(?:[^@/]+@)?([^/:]+)(?::\d+)?[:/](.+?)(?:\.git)?/?$", url)
    if not m:
        return None
    host, path = m.groups()
    for kind in ("github", "gitlab"):
        if kind in host:
            return kind, host, path
    return None


def forge_prs(cwd, remote, branch, state):
    """[{"number", "head"}] of the PRs/MRs from `branch` in `state` (`merged` or `open`).

    None when the forge is unknown, or its CLI is missing, fails or takes over 5 s.
    """
    repo = forge_repo(cwd, remote)
    if not repo:
        return None
    kind, host, path = repo
    if kind == "github":
        cmd = ["gh", "pr", "list", "--repo", f"{host}/{path}", "--head", branch, "--state", state, "--json", "number,headRefOid"]
        number, head = "number", "headRefOid"
    else:
        cmd = ["glab", "mr", "list", "--repo", f"https://{host}/{path}", "--source-branch", branch, "--output", "json"]
        cmd += ["--merged"] if state == "merged" else []
        number, head = "iid", "sha"
    out = run(cmd, cwd)
    try:
        return [{"number": item[number], "head": item[head]} for item in json.loads(out)] if out is not None else None
    except (ValueError, TypeError, KeyError):
        return None


def merge_proven(cwd, branch):
    """Whether `branch` can go without losing work: its tip is in `<remote>/<default>`
    (local proof), or is the head of a merged PR/MR from it (forge proof, for squash
    and rebase merges)."""
    tip = git(cwd, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}^{{commit}}")
    if not tip:
        return False
    remote = branch_remote(cwd, branch)
    for default in default_branches(cwd, remote):
        if git(cwd, "merge-base", "--is-ancestor", tip, f"refs/remotes/{remote}/{default}") is not None:
            return True
    return any(pr["head"] == tip for pr in forge_prs(cwd, remote, branch, "merged") or [])


def tokenize(command):
    command = command.replace("\n", " ; ")
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = "#"
    try:
        return list(lexer)
    except ValueError:
        # Unbalanced quotes: fall back to a plain split so the check still runs.
        return command.replace(";", " ; ").replace("&&", " && ").replace("|", " | ").split()


def segments(tokens):
    current = []
    for tok in tokens:
        if tok in SEPARATORS or (tok and set(tok) <= set(";&|")):
            if current:
                yield current
            current = []
        else:
            current.append(tok)
    if current:
        yield current


def strip_prefixes(words):
    i = 0
    while i < len(words):
        w = words[i]
        if "=" in w and not w.startswith("-") and w.split("=", 1)[0].isidentifier():
            i += 1  # VAR=value
        elif w in PREFIXES:
            i += 1
            if w == "env":
                while i < len(words) and words[i].startswith("-"):
                    i += 1
        else:
            break
    return words[i:]


def positionals(args, with_value=()):
    out, i = [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            out.extend(args[i + 1:])
            break
        if a.startswith("-") and a != "-":
            if a in with_value:
                i += 1
        else:
            out.append(a)
        i += 1
    return out


def short_flags(args):
    """Letters of every short-option cluster (`-xdf` -> x, d, f)."""
    letters = set()
    for a in args:
        if a == "--":
            break
        if a.startswith("-") and not a.startswith("--"):
            letters.update(a[1:])
    return letters


def parse_push(args):
    """Split `git push` args into (long options, short flag letters, positionals).

    Option values are skipped: `-o <v>`, `-o<v>`, `-uo <v>`, `--push-option <v>`,
    `--repo <v>`, `--receive-pack <v>`, `--exec <v>`; `--opt=<v>` is one word.
    """
    longs, letters, pos, i = [], set(), [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            pos.extend(args[i + 1:])
            break
        if a.startswith("--"):
            longs.append(a)
            if a in PUSH_LONG_WITH_VALUE:
                i += 1
        elif a.startswith("-") and a != "-":
            cluster = a[1:]
            for j, ch in enumerate(cluster):
                letters.add(ch)
                if ch in PUSH_SHORT_WITH_VALUE:
                    if j == len(cluster) - 1:
                        i += 1  # the value is the next word
                    break  # otherwise the rest of the cluster is the value
        else:
            pos.append(a)
        i += 1
    return longs, letters, pos


def check_push(args, cwd):
    longs, letters, pos = parse_push(args)
    if any(a in ("--force", "--force-with-lease") or a.startswith("--force-with-lease=") for a in longs):
        return "force-push"
    if any(a in ("--mirror", "--all", "--branches") for a in longs):
        return "push of every branch, including the default branch"
    if "f" in letters:
        return "force-push"
    remote = pos[0] if pos else "origin"
    refspecs = pos[1:]
    if any(r.startswith("+") for r in refspecs):
        return "force-push"

    defaults = default_branches(cwd, remote)
    current = git(cwd, "symbolic-ref", "--quiet", "--short", "HEAD")

    if not refspecs:
        # Implicit push: the current branch goes to its push destination.
        dest = git(cwd, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{push}")
        for branch in (current, dest.split("/", 1)[-1] if dest else None):
            if branch in defaults:
                return f"push to the default branch `{branch}`"
        return None

    for spec in refspecs:
        src, _, dst = spec.partition(":")
        target = dst if dst else src
        if target in ("HEAD", "@"):
            target = current or ""
        if strip_heads(target) in defaults:
            return f"push to the default branch `{strip_heads(target)}`"
    return None


def check_git(words, cwd):
    args = words[1:]
    i = 0
    while i < len(args) and args[i].startswith("-"):
        opt = args[i]
        if opt in GIT_GLOBAL_WITH_VALUE:
            if opt == "-C" and i + 1 < len(args):
                cwd = os.path.join(cwd, args[i + 1])
            i += 2
        else:
            i += 1
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]

    if "--no-verify" in rest:
        return "`--no-verify` skips the repository's hooks"
    if sub == "commit":
        for a in rest:
            if a == "--":
                break
            if a.startswith("-") and not a.startswith("--"):
                for ch in a[1:]:
                    if ch == "n":
                        return "`commit -n` skips the repository's hooks"
                    if ch in COMMIT_SHORT_WITH_VALUE:
                        break
    if sub == "push":
        return check_push(rest, cwd)
    if sub == "reset" and "--hard" in rest:
        return "`reset --hard` discards uncommitted work"
    if sub == "clean" and ("--force" in rest or "f" in short_flags(rest)):
        return "`clean -f` deletes untracked files"
    if sub == "branch":
        flags = short_flags(rest)
        deleting = "d" in flags or "--delete" in rest
        forcing = "f" in flags or "--force" in rest
        if "D" in flags or (deleting and forcing):
            names = positionals(rest, BRANCH_WITH_VALUE)
            if not names or not all(merge_proven(cwd, b) for b in names):
                return UNPROVEN_DELETE
    if sub == "worktree":
        pos = positionals(rest)
        if pos and pos[0] == "remove" and ("--force" in rest or "f" in short_flags(rest)):
            return "`worktree remove --force` deletes uncommitted changes and untracked files"
    if sub in ("checkout", "restore"):
        pos = positionals(rest, {"-s", "--source", "-b", "-B", "--orphan", "--conflict"})
        if any(p in WHOLE_TREE for p in pos):
            staged_only = sub == "restore" and ("--staged" in rest or "S" in short_flags(rest)) and not (
                "--worktree" in rest or "W" in short_flags(rest)
            )
            if not staged_only:
                return f"`{sub} .` discards uncommitted changes in the whole tree"
    if sub == "stash":
        pos = positionals(rest)
        if pos and pos[0] in ("drop", "clear"):
            return f"`stash {pos[0]}` deletes stashed work"
    return None


def check_forge(words, noun, verb):
    pos = positionals(words[1:], {"-R", "--repo"})
    if len(pos) >= 2 and pos[0] == noun and pos[1] == verb:
        return f"merging a {'PR' if noun == 'pr' else 'MR'} is always the human's call"
    return None


def shell_script(words):
    """The `-c` script of a shell call (`bash -c s`, `bash -lc s`, `sh -e -o pipefail -c s`), or None."""
    i = 1
    while i < len(words):
        a = words[i]
        if a.startswith("--") and a != "--":
            i += 1  # --login, --norc, ...
            continue
        if not a.startswith("-") or a in ("-", "--"):
            return None  # a script file or stdin: nothing inline to check
        cluster = a[1:]
        values = sum(1 for ch in cluster if ch in SHELL_SHORT_WITH_VALUE)
        if "c" in cluster:
            idx = i + 1 + values
            return words[idx] if idx < len(words) else None
        i += 1 + values
    return None


def xargs_command(words):
    """The words of the command xargs runs, without xargs's own options."""
    i = 1
    while i < len(words):
        a = words[i]
        if a == "--":
            i += 1
            break
        if not a.startswith("-") or a == "-":
            break
        i += 2 if a in XARGS_WITH_VALUE else 1
    return words[i:]


def check(command, cwd, depth=0):
    """Return (segment, reason, next step) for the first forbidden part of `command`, or None."""
    for words in segments(tokenize(command)):
        words = strip_prefixes(words)
        if not words:
            continue
        prog = os.path.basename(words[0])
        if prog == "cd" and len(words) > 1:
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        reason = None
        if prog == "git":
            reason = check_git(words, cwd)
        elif prog == "gh":
            reason = check_forge(words, "pr", "merge")
        elif prog == "glab":
            reason = check_forge(words, "mr", "merge")
        elif depth < 3 and (prog in ("eval", "xargs") or prog in SHELLS):
            if prog == "eval":
                script = " ".join(words[1:])
            elif prog == "xargs":
                script = shlex.join(xargs_command(words))
            else:
                script = shell_script(words)
            found = check(script, cwd, depth + 1) if script else None
            if found:
                return found
        if reason:
            segment = " ".join(words)
            next_step = HAND_OFF.format(segment=segment) if reason == UNPROVEN_DELETE else STOP
            return segment, reason, next_step
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command") or ""
    cwd = event.get("cwd") or os.getcwd()
    found = check(command, cwd)
    if not found:
        return 0
    segment, reason, next_step = found
    message = f"Blocked by the foundation git guardrail: `{segment}` ({reason}). {next_step}"
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
