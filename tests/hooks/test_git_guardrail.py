#!/usr/bin/env python3
"""Table-driven test of the foundation git guardrail's stdin -> stdout contract.

Runs the hook as Claude Code would, against a throwaway clone whose `origin/HEAD`
points at `main`, from the default branch and from a feature branch.

Usage: python3 tests/hooks/test_git_guardrail.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOOK = os.path.join(ROOT, "plugins", "foundation", "hooks", "git-guardrail.py")
FAKES = os.path.join(ROOT, "tests", "fakes")

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
    ("git worktree remove --force ../wt", FEATURE, True),
    ("git worktree remove -f ../wt", FEATURE, True),
    # Compound commands with one forbidden part.
    ("git add . && git commit -m wip && git push --force", FEATURE, True),
    ("make test; git reset --hard", FEATURE, True),
    ("git log --oneline | head -1 && gh pr merge 3", FEATURE, True),
    ("git status || git clean -f", FEATURE, True),
    ("(cd . && git stash clear)", FEATURE, True),
    ("echo ok\ngit push origin main", FEATURE, True),
    ("bash -c 'git push -f'", FEATURE, True),
    ("GIT_TRACE=1 git push origin main", FEATURE, True),
    # Shells with combined short flags, and xargs.
    ("bash -lc 'git push -f'", FEATURE, True),
    ("sh -ec 'git reset --hard'", FEATURE, True),
    ("bash -o pipefail -c 'git push origin main'", FEATURE, True),
    ("zsh --login -xc 'git stash clear'", FEATURE, True),
    ("echo feature | xargs git push -f", FEATURE, True),
    ("ls | xargs -n 1 git branch -D", FEATURE, True),
    ("printf 'a' | xargs -I {} git clean -fd {}", FEATURE, True),
    # Push options that take a value.
    ("git push -o ci.skip -f origin feature", FEATURE, True),
    ("git push --push-option ci.skip origin main", FEATURE, True),
    ("git push --exec /usr/bin/git-receive-pack origin main", FEATURE, True),
    # Force-deleting a branch whose merge can't be proven.
    ("git branch -D unmerged", FEATURE, True),
    ("git branch -D merged unmerged", FEATURE, True),
    ("git branch -d -f unmerged", FEATURE, True),
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
    # Force-deleting branches whose tips are in origin/main.
    ("git branch -D merged", FEATURE, False),
    ("git branch -D merged feature", FEATURE, False),
    ("git branch --delete --force merged", FEATURE, False),
    ("git checkout -b topic", FEATURE, False),
    ("git worktree remove ../wt", FEATURE, False),
    ("git checkout src/app.go", FEATURE, False),
    ("git restore --staged .", FEATURE, False),
    ("git reset --soft HEAD~1", FEATURE, False),
    ("git clean -n", FEATURE, False),
    ("git stash && git stash pop", FEATURE, False),
    ("git log -n 3 --oneline", FEATURE, False),
    ("echo 'git push -f' > notes.txt", FEATURE, False),
    ("bash -lc 'git status'", FEATURE, False),
    ("bash script.sh -c 'git push -f'", FEATURE, False),
    ("ls | xargs git add", FEATURE, False),
    ("git push -ofix=1 origin feature", FEATURE, False),
    ("git push -uo main origin feature", FEATURE, False),
    ("git push --push-option main origin feature", FEATURE, False),
    ("git push --receive-pack git-receive-pack origin feature", FEATURE, False),
    ("git push --repo origin feature", FEATURE, False),
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
        ["checkout", "--quiet", "-b", "merged"],
        ["commit", "--quiet", "--allow-empty", "-m", "merged work"],
        ["checkout", "--quiet", DEFAULT],
        ["merge", "--quiet", "--no-ff", "-m", "merge", "merged"],
        ["push", "--quiet", "origin", DEFAULT],
        ["checkout", "--quiet", "-b", "unmerged"],
        ["commit", "--quiet", "--allow-empty", "-m", "unmerged work"],
        ["checkout", "--quiet", DEFAULT],
    ):
        run(["git", *args], work)
    return work


def invoke(command, cwd, env=None):
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
        env=env,
        check=False,
    )
    return out


def git_out(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


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


class ForgeProofTest(unittest.TestCase):
    """`branch -D` of a squash- or rebase-merged branch, proven by the forge's merged PR."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = make_repo(self.tmp.name)
        run(["git", "remote", "set-url", "origin", "https://github.com/acme/app.git"], self.repo)
        run(["git", "checkout", "--quiet", "-b", "squashed"], self.repo)
        run(["git", "commit", "--quiet", "--allow-empty", "-m", "squashed work"], self.repo)
        run(["git", "checkout", "--quiet", DEFAULT], self.repo)
        self.tip = git_out(self.repo, "rev-parse", "squashed")
        self.prs = os.path.join(self.tmp.name, "prs")
        os.makedirs(os.path.join(self.prs, "merged"))
        git_dir = os.path.dirname(shutil.which("git"))
        self.env = {**os.environ, "PATH": f"{FAKES}{os.pathsep}{git_dir}", "FAKE_GH_DIR": self.prs}

    def tearDown(self):
        self.tmp.cleanup()

    def merged_pr(self, head):
        with open(os.path.join(self.prs, "merged", "squashed.json"), "w") as f:
            json.dump([{"headRefOid": head}], f)

    def decision(self, env):
        out = invoke("git branch -D squashed", self.repo, env)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)["hookSpecificOutput"] if out.stdout.strip() else None

    def test_allows_a_branch_whose_tip_is_a_merged_pr_head(self):
        self.merged_pr(self.tip)
        self.assertIsNone(self.decision(self.env))

    def test_denies_when_the_merged_pr_head_differs_from_the_tip(self):
        self.merged_pr("0" * 40)
        reason = self.decision(self.env)["permissionDecisionReason"]
        self.assertIn("merge can't be proven", reason)
        self.assertIn("hand the user the cleanup command ready to run (`git branch -D squashed`)", reason)
        self.assertIn("know-when-to-stop", reason)

    def test_denies_without_a_merged_pr(self):
        self.assertEqual(self.decision(self.env)["permissionDecision"], "deny")

    def test_denies_when_gh_is_missing(self):
        self.merged_pr(self.tip)
        env = {**self.env, "PATH": os.path.dirname(shutil.which("git"))}
        self.assertEqual(self.decision(env)["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main(verbosity=2)
