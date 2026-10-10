#!/usr/bin/env python3
"""Table-driven test of the foundation git guardrail's stdin -> stdout contract.

Runs the hook as Claude Code would, against a throwaway clone whose `origin/HEAD`
points at `main`, from the default branch and from a feature branch.

Usage: python3 tests/hooks/test_git_guardrail.py
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOOK = os.path.join(ROOT, "plugins", "foundation", "hooks", "git-guardrail.py")

DEFAULT, FEATURE = "main", "feature"

# (command, branch checked out, expect denied)
CASES = [
    # Force-push in any form.
    ("git push --force origin feature", FEATURE, True),
    ("git push -f", FEATURE, True),
    ("git push -uf origin feature", FEATURE, True),
    ("git push --force-with-lease", FEATURE, True),
    ("git push --force-with-lease=feature:abc123 origin feature", FEATURE, True),
    ("git push origin +feature", FEATURE, True),
    ("git push origin +HEAD:feature", FEATURE, True),
    # Push to the default branch, explicit and implicit.
    ("git push origin main", FEATURE, True),
    ("git push origin HEAD:main", FEATURE, True),
    ("git push origin feature:refs/heads/main", FEATURE, True),
    ("git push", DEFAULT, True),
    ("git push origin", DEFAULT, True),
    ("git push -u origin HEAD", DEFAULT, True),
    ("git push --all", FEATURE, True),
    ("git -C . push origin main", FEATURE, True),
    # PR/MR merges.
    ("gh pr merge 12 --squash", FEATURE, True),
    ("gh pr merge --auto", FEATURE, True),
    ("glab mr merge 7", FEATURE, True),
    # Skipping hooks.
    ("git commit --no-verify -m wip", FEATURE, True),
    ("git commit -nm wip", FEATURE, True),
    ("git push --no-verify", FEATURE, True),
    # Local destructive commands.
    ("git reset --hard", FEATURE, True),
    ("git reset --hard HEAD~1", FEATURE, True),
    ("git clean -f", FEATURE, True),
    ("git clean -fdx", FEATURE, True),
    ("git clean --force -d", FEATURE, True),
    ("git branch -D old", FEATURE, True),
    ("git branch --delete --force old", FEATURE, True),
    ("git checkout .", FEATURE, True),
    ("git checkout -- .", FEATURE, True),
    ("git restore .", FEATURE, True),
    ("git restore --worktree --staged .", FEATURE, True),
    ("git stash drop", FEATURE, True),
    ("git stash drop stash@{0}", FEATURE, True),
    ("git stash clear", FEATURE, True),
    # Compound commands with one forbidden part.
    ("git add . && git commit -m wip && git push --force", FEATURE, True),
    ("make test; git reset --hard", FEATURE, True),
    ("git log --oneline | head -1 && gh pr merge 3", FEATURE, True),
    ("git status || git clean -f", FEATURE, True),
    ("(cd . && git stash clear)", FEATURE, True),
    ("echo ok\ngit push origin main", FEATURE, True),
    ("bash -c 'git push -f'", FEATURE, True),
    ("GIT_TRACE=1 git push origin main", FEATURE, True),
    # Allowed.
    ("git commit -m 'work on main'", DEFAULT, False),
    ("git add -A && git commit -m wip", DEFAULT, False),
    ("git push", FEATURE, False),
    ("git push -u origin feature", FEATURE, False),
    ("git push -u origin HEAD", FEATURE, False),
    ("git push origin feature:feature", FEATURE, False),
    ("gh pr create --draft --fill", FEATURE, False),
    ("gh pr ready 12", FEATURE, False),
    ("glab mr create --draft", FEATURE, False),
    ("git push --dry-run origin feature", FEATURE, False),
    ("git commit -m 'never use --force here'", FEATURE, False),
    ("git branch -d merged", FEATURE, False),
    ("git checkout -b topic", FEATURE, False),
    ("git checkout src/app.go", FEATURE, False),
    ("git restore --staged .", FEATURE, False),
    ("git reset --soft HEAD~1", FEATURE, False),
    ("git clean -n", FEATURE, False),
    ("git stash && git stash pop", FEATURE, False),
    ("git log -n 3 --oneline", FEATURE, False),
    ("echo 'git push -f' > notes.txt", FEATURE, False),
]


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


def make_repo(base):
    origin = os.path.join(base, "origin.git")
    work = os.path.join(base, "work")
    run(["git", "init", "--quiet", "--bare", "--initial-branch", DEFAULT, origin], base)
    run(["git", "clone", "--quiet", origin, work], base)
    for args in (
        ["config", "user.email", "test@example.com"],
        ["config", "user.name", "Test"],
        ["commit", "--quiet", "--allow-empty", "-m", "init"],
        ["push", "--quiet", "origin", DEFAULT],
        ["remote", "set-head", "origin", DEFAULT],
        ["branch", FEATURE],
    ):
        run(["git", *args], work)
    return work


def invoke(command, cwd):
    event = {
        "session_id": "test",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": cwd,
    }
    out = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )
    return out


class GitGuardrailTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = make_repo(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_origin_head_is_configured(self):
        ref = subprocess.run(
            ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            cwd=self.repo, capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertEqual(ref, f"origin/{DEFAULT}")

    def test_table(self):
        for command, branch, denied in CASES:
            with self.subTest(command=command, branch=branch):
                run(["git", "checkout", "--quiet", branch], self.repo)
                out = invoke(command, self.repo)
                self.assertEqual(out.returncode, 0, out.stderr)
                if not denied:
                    self.assertEqual(out.stdout.strip(), "", "expected the command to be allowed")
                    continue
                self.assertTrue(out.stdout.strip(), "expected the command to be denied")
                decision = json.loads(out.stdout)["hookSpecificOutput"]
                self.assertEqual(decision["hookEventName"], "PreToolUse")
                self.assertEqual(decision["permissionDecision"], "deny")
                reason = decision["permissionDecisionReason"]
                self.assertIn("know-when-to-stop", reason)
                named = re.search(r"`((?:git|gh|glab) [^`]+)`", reason)
                self.assertIsNotNone(named, "deny reason must name the blocked command")
                self.assertLessEqual(set(named.group(1).split()), set(re.sub(r"[()']", " ", command).split()))

    def test_ignores_other_tools(self):
        event = {"tool_name": "Write", "tool_input": {"command": "git push -f"}, "cwd": self.repo}
        out = subprocess.run(
            [sys.executable, HOOK], input=json.dumps(event), capture_output=True, text=True, check=False
        )
        self.assertEqual((out.returncode, out.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
