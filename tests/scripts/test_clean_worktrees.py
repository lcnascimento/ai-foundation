#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "plugins", "engineering", "skills", "clean-worktrees", "scripts", "clean-worktrees.py")
GUARDRAIL = os.path.join(ROOT, "plugins", "foundation", "hooks", "git-guardrail.py")
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

    def install(self, script_dir, guardrails):
        script = os.path.join(self.tmp.name, script_dir, "skills", "clean-worktrees", "scripts", "clean-worktrees.py")
        os.makedirs(os.path.dirname(script))
        shutil.copy(SCRIPT, script)
        for guardrail_dir, source in guardrails.items():
            hooks = os.path.join(self.tmp.name, guardrail_dir, "hooks")
            os.makedirs(hooks)
            shutil.copy(source, os.path.join(hooks, "git-guardrail.py"))
        return script

    def merged_worktree(self, branch):
        path = self.worktree(branch)
        git(path, "push", "--quiet", "origin", branch)
        git(self.checkout, "merge", "--quiet", "--ff-only", branch)
        git(self.checkout, "push", "--quiet", "origin", "main")
        return path

    def run_script(self, script):
        return subprocess.run(
            [sys.executable, script], cwd=self.checkout, env=self.env, capture_output=True, text=True, check=False
        )

    def clean(self, script=SCRIPT):
        out = self.run_script(script)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def rewind_local_main(self, commit):
        git(self.checkout, "reset", "--quiet", "--keep", commit)

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
        self.rewind_local_main("HEAD~1")

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
        self.rewind_local_main(head)

        self.clean()

        self.assertEqual(git(self.checkout, "rev-parse", "HEAD"), head)
        self.assertEqual(git(self.checkout, "branch", "--show-current"), "main")

    def test_finds_the_guardrail_in_the_marketplace_layout(self):
        script = self.install(
            os.path.join("marketplace", "plugins", "engineering"),
            {os.path.join("marketplace", "plugins", "foundation"): GUARDRAIL},
        )
        path = self.merged_worktree("abc-7")

        output = self.clean(script)

        self.assertFalse(os.path.exists(path))
        self.assertIn("removed .claude/worktrees/abc-7 (abc-7)", output)

    def test_loads_the_highest_foundation_version_in_the_cache_layout(self):
        stale = os.path.join(self.tmp.name, "stale-guardrail.py")
        with open(stale, "w") as f:
            f.write('raise SystemExit("loaded foundation 0.9.0")\n')
        foundation = os.path.join("cache", "acme", "foundation")
        script = self.install(
            os.path.join("cache", "acme", "engineering", "0.13.0"),
            {
                os.path.join(foundation, "0.9.0"): stale,
                os.path.join(foundation, "0.10.0"): GUARDRAIL,
                os.path.join(foundation, "latest"): stale,
            },
        )
        path = self.merged_worktree("abc-8")

        output = self.clean(script)

        self.assertFalse(os.path.exists(path))
        self.assertIn("removed .claude/worktrees/abc-8 (abc-8)", output)

    def test_reports_a_missing_guardrail(self):
        script = self.install(os.path.join("cache", "acme", "engineering", "0.13.0"), {})

        out = self.run_script(script)

        self.assertEqual(out.returncode, 1)
        self.assertEqual(out.stderr.strip(), "clean-worktrees: the foundation plugin's git-guardrail.py was not found")


if __name__ == "__main__":
    unittest.main(verbosity=2)
