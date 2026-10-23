#!/usr/bin/env python3
"""Scenario test of the `engineering:clean-worktrees` script.

Each test builds a checkout whose `origin` is a GitHub URL rewritten to a local
bare repo, with one worktree under `.claude/worktrees/`, and a fake `gh` on the
PATH serving the PRs in `$FAKE_GH_DIR/<state>/<branch>.json`.

Usage: python3 tests/scripts/test_clean_worktrees.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "plugins", "engineering", "skills", "clean-worktrees", "scripts", "clean-worktrees.py")
FAKES = os.path.join(ROOT, "tests", "fakes")
URL = "https://github.com/acme/app.git"


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class CleanWorktreesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = self.tmp.name
        origin = os.path.join(base, "origin.git")
        self.checkout = os.path.join(base, "app")
        git(base, "init", "--quiet", "--bare", "--initial-branch", "main", origin)
        git(base, "init", "--quiet", "--initial-branch", "main", self.checkout)
        for args in (
            ["config", "user.email", "test@example.com"],
            ["config", "user.name", "Test"],
            ["config", f"url.{origin}.insteadOf", URL],
            ["remote", "add", "origin", URL],
            ["commit", "--quiet", "--allow-empty", "-m", "init"],
            ["push", "--quiet", "-u", "origin", "main"],
            ["remote", "set-head", "origin", "main"],
        ):
            git(self.checkout, *args)
        self.prs = os.path.join(base, "prs")
        for state in ("merged", "open"):
            os.makedirs(os.path.join(self.prs, state))
        path = os.pathsep.join(dict.fromkeys([FAKES, os.path.dirname(shutil.which("git")), os.path.dirname(sys.executable)]))
        self.env = {**os.environ, "PATH": path, "FAKE_GH_DIR": self.prs}

    def tearDown(self):
        self.tmp.cleanup()

    def worktree(self, branch):
        path = os.path.join(self.checkout, ".claude", "worktrees", branch)
        git(self.checkout, "worktree", "add", "--quiet", "-b", branch, path, "main")
        git(path, "commit", "--quiet", "--allow-empty", "-m", f"work on {branch}")
        return path

    def pr(self, state, branch, head):
        with open(os.path.join(self.prs, state, f"{branch}.json"), "w") as f:
            json.dump([{"headRefOid": head, "number": 7}], f)

    def clean(self):
        out = subprocess.run(
            [sys.executable, SCRIPT], cwd=self.checkout, env=self.env, capture_output=True, text=True, check=False
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def branches(self):
        return git(self.checkout, "branch", "--format=%(refname:short)").split()

    def assert_left(self, verb, path, branch, output, why):
        self.assertTrue(os.path.isdir(path))
        self.assertIn(branch, self.branches())
        self.assertIn(f"{verb} {os.path.relpath(path, self.checkout)} ({branch}): {why}", output)

    def test_removes_a_clean_worktree_merged_with_a_merge_commit(self):
        path = self.worktree("abc-1")
        git(path, "push", "--quiet", "origin", "abc-1")
        git(self.checkout, "merge", "--quiet", "--no-ff", "-m", "Merge abc-1", "abc-1")
        git(self.checkout, "push", "--quiet", "origin", "main")
        git(self.checkout, "push", "--quiet", "origin", "--delete", "abc-1")
        git(self.checkout, "reset", "--quiet", "--keep", "HEAD~1")  # local main stays behind

        output = self.clean()

        self.assertFalse(os.path.exists(path))
        self.assertEqual(self.branches(), ["main"])
        self.assertIn("removed .claude/worktrees/abc-1 (abc-1)", output)

    def test_removes_a_squash_merged_worktree_proven_by_its_merged_pr(self):
        path = self.worktree("abc-2")
        self.pr("merged", "abc-2", git(path, "rev-parse", "HEAD"))
        git(self.checkout, "commit", "--quiet", "--allow-empty", "-m", "abc-2 squashed (#7)")
        git(self.checkout, "push", "--quiet", "origin", "main")

        output = self.clean()

        self.assertFalse(os.path.exists(path))
        self.assertEqual(self.branches(), ["main"])
        self.assertIn("removed .claude/worktrees/abc-2 (abc-2)", output)

    def test_keeps_a_worktree_with_uncommitted_changes(self):
        path = self.worktree("abc-3")
        self.pr("merged", "abc-3", git(path, "rev-parse", "HEAD"))
        with open(os.path.join(path, "notes.txt"), "w") as f:
            f.write("draft\n")

        self.assert_left("skip", path, "abc-3", self.clean(), "uncommitted changes or untracked files")

    def test_keeps_a_worktree_whose_pr_is_open(self):
        path = self.worktree("abc-4")
        git(path, "push", "--quiet", "origin", "abc-4")
        self.pr("open", "abc-4", git(path, "rev-parse", "HEAD"))

        self.assert_left("skip", path, "abc-4", self.clean(), "PR #7 is open")

    def test_keeps_a_branch_with_no_pr_and_unpushed_commits(self):
        path = self.worktree("abc-5")

        self.assert_left("keep", path, "abc-5", self.clean(), "merge not proven: commits not on origin, no merged PR")

    def test_never_touches_the_users_checkout(self):
        self.worktree("abc-6")
        head = git(self.checkout, "rev-parse", "HEAD")
        git(self.checkout, "commit", "--quiet", "--allow-empty", "-m", "remote only")
        git(self.checkout, "push", "--quiet", "origin", "main")
        git(self.checkout, "reset", "--quiet", "--keep", head)

        self.clean()

        self.assertEqual(git(self.checkout, "rev-parse", "HEAD"), head)
        self.assertEqual(git(self.checkout, "branch", "--show-current"), "main")


if __name__ == "__main__":
    unittest.main(verbosity=2)
