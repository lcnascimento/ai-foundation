#!/usr/bin/env python3
"""Git guardrail: a PreToolUse hook (matcher `Bash`) that always denies the
actions only the human may take (ADR-0009).

Reads the tool call JSON on stdin. When any part of the command is forbidden,
prints a Claude Code permission decision (`deny`) naming the blocked command and
the `know-when-to-stop` Principle. Otherwise prints nothing and exits 0, leaving
the normal permission flow untouched.

Denied: force-push in any form, push to the default branch (resolved from
`origin/HEAD`, including implicit pushes), `gh pr merge`, `glab mr merge`,
`--no-verify`, `reset --hard`, `clean -f`, `branch -D`, `checkout .`,
`restore .`, `stash drop`, `stash clear`.
"""

import json
import os
import shlex
import subprocess
import sys

SEPARATORS = {"(", ")"}
PREFIXES = {"sudo", "command", "env", "time", "nohup", "exec", "builtin"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
WHOLE_TREE = {".", "./", ":/", ":/."}

# git global options that take a separate value.
GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}
# `git push` options that take a separate value.
PUSH_WITH_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
# `git commit` short options that consume the rest of their cluster or the next word.
COMMIT_SHORT_WITH_VALUE = set("mFCctS")


def git(cwd, *args):
    try:
        out = subprocess.run(
            ["git", "-C", cwd, *args],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


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


def check_push(args, cwd):
    if any(a in ("--force", "--force-with-lease") or a.startswith("--force-with-lease=") for a in args):
        return "force-push"
    if "--mirror" in args or "--all" in args or "--branches" in args:
        return "push of every branch, including the default branch"
    # Short clusters, skipping the values of -o.
    i, letters = 0, set()
    while i < len(args):
        a = args[i]
        if a == "--":
            break
        if a.startswith("-") and not a.startswith("--"):
            letters.update(a[1:])
            if a.endswith("o"):
                i += 1
        i += 1
    if "f" in letters:
        return "force-push"

    pos = positionals(args, PUSH_WITH_VALUE)
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
            return "`branch -D` deletes a branch with unmerged work"
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


def check(command, cwd, depth=0):
    """Return (segment, reason) for the first forbidden part of `command`, or None."""
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
        elif depth < 3 and (prog == "eval" or (prog in SHELLS and "-c" in words)):
            if prog == "eval":
                script = " ".join(words[1:])
            else:
                script = " ".join(words[words.index("-c") + 1:][:1])
            found = check(script, cwd, depth + 1)
            if found:
                return found
        if reason:
            return " ".join(words), reason
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
    segment, reason = found
    message = (
        f"Blocked by the foundation git guardrail: `{segment}` ({reason}). "
        "Only the human may do this, in interactive and AFK sessions alike. "
        "Do not retry or work around it: follow the `know-when-to-stop` Principle "
        "(load it with `foundation:principles know-when-to-stop`) and raise a "
        "BLOCKED / TRIED / NEED block."
    )
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
