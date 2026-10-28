#!/usr/bin/env python3
import os
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "plugins", "engineering", "scripts", "worktree.sh")


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class WorktreeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = base = os.path.realpath(self.tmp.name)
        self.origin = os.path.join(base, "origin.git")
        self.checkout = os.path.join(base, "app")
        git(base, "init", "--quiet", "--bare", "--initial-branch", "main", self.origin)
        git(base, "init", "--quiet", "--initial-branch", "main", self.checkout)
        for args in (
            ["config", "user.email", "test@example.com"],
            ["config", "user.name", "Test"],
            ["remote", "add", "origin", self.origin],
            ["commit", "--quiet", "--allow-empty", "-m", "init"],
            ["push", "--quiet", "-u", "origin", "main"],
            ["remote", "set-head", "origin", "main"],
        ):
            git(self.checkout, *args)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args, cwd=None):
        return subprocess.run(
            ["bash", SCRIPT, *args], cwd=cwd or self.checkout, capture_output=True, text=True, check=False
        )

    def path(self, name):
        return os.path.join(self.checkout, ".claude", "worktrees", name)

    def commit_files(self, files):
        for rel, content in files.items():
            self.write(self.checkout, rel, content)
        git(self.checkout, "add", *files)
        git(self.checkout, "commit", "--quiet", "-m", "add " + ", ".join(files))

    def write(self, base, rel, content):
        os.makedirs(os.path.dirname(os.path.join(base, rel)), exist_ok=True)
        with open(os.path.join(base, rel), "w") as f:
            f.write(content)

    def read(self, base, rel):
        with open(os.path.join(base, rel)) as f:
            return f.read()

    def branches(self):
        return git(self.checkout, "branch", "--format=%(refname:short)").split()

    def push_upstream_commit(self, message):
        other = os.path.join(self.base, "other")
        git(self.base, "clone", "--quiet", self.origin, other)
        git(other, "-c", "user.email=o@example.com", "-c", "user.name=O", "commit", "--quiet", "--allow-empty", "-m", message)
        git(other, "push", "--quiet", "origin", "main")
        return git(other, "rev-parse", "HEAD")

    def test_add_starts_from_the_freshly_fetched_default_branch(self):
        upstream = self.push_upstream_commit("upstream work")

        out = self.run_script("add", "abc-1")

        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip().splitlines()[-1], self.path("abc-1"))
        self.assertEqual(git(self.path("abc-1"), "rev-parse", "HEAD"), upstream)
        self.assertEqual(git(self.path("abc-1"), "branch", "--show-current"), "abc-1")

    def test_add_in_a_project_without_include_or_setup_is_a_plain_worktree_add(self):
        self.commit_files({".gitignore": ".env\n", "docs/agents/environment.md": "# Environment\n\n## Start\n\n- `touch started`\n"})
        self.write(self.checkout, ".env", "SECRET=main\n")

        out = self.run_script("add", "abc-15", "--base", "main")

        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(git(self.path("abc-15"), "status", "--porcelain", "--ignored"), "")

    def test_add_from_a_local_base_needs_no_network(self):
        git(self.checkout, "branch", "integ")
        git(self.checkout, "commit", "--quiet", "--allow-empty", "-m", "on main only")
        git(self.checkout, "remote", "set-url", "origin", "/nonexistent")

        out = self.run_script("add", "abc-2", "--base", "integ")

        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(git(self.path("abc-2"), "rev-parse", "HEAD"), git(self.checkout, "rev-parse", "integ"))

    def test_add_copies_the_listed_ignored_files_and_a_rerun_never_overwrites_them(self):
        self.commit_files({".gitignore": ".env\nnode_modules/\n", ".worktreeinclude": ".env\nsvc/*/.env\n"})
        self.write(self.checkout, ".env", "SECRET=main\n")
        self.write(self.checkout, "svc/a/.env", "A=main\n")
        self.write(self.checkout, "node_modules/x/index.js", "x\n")
        wt = self.path("abc-4")

        first = self.run_script("add", "abc-4", "--base", "main")
        self.write(wt, ".env", "SECRET=edited\n")
        self.write(self.checkout, "svc/b/.env", "B=main\n")
        second = self.run_script("add", "abc-4", "--base", "main")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(self.read(wt, ".env"), "SECRET=edited\n")
        self.assertEqual(self.read(wt, "svc/a/.env"), "A=main\n")
        self.assertEqual(self.read(wt, "svc/b/.env"), "B=main\n")
        self.assertFalse(os.path.exists(os.path.join(wt, "node_modules")))

    def test_add_runs_the_setup_section_commands_in_order_inside_the_worktree(self):
        self.commit_files({
            ".gitignore": "setup.out\n",
            "docs/agents/environment.md": (
                "# Environment\n\n## Setup\n\n- `echo one > setup.out`\n- `pwd >> setup.out` (from the worktree)\n\n"
                "## Start\n\n- `echo start > start.out`\n"
            ),
        })

        out = self.run_script("add", "abc-5", "--base", "main")

        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(self.read(self.path("abc-5"), "setup.out"), f"one\n{self.path('abc-5')}\n")
        self.assertFalse(os.path.exists(os.path.join(self.path("abc-5"), "start.out")))

    def test_a_setup_command_reading_stdin_does_not_swallow_the_next_ones(self):
        self.commit_files({
            ".gitignore": "setup.out\n",
            "docs/agents/environment.md": "# Environment\n\n## Setup\n\n- `cat > /dev/null`\n- `echo two > setup.out`\n",
        })

        out = self.run_script("add", "abc-7", "--base", "main")

        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(self.read(self.path("abc-7"), "setup.out"), "two\n")

    def test_add_fails_when_a_setup_command_fails(self):
        self.commit_files({"docs/agents/environment.md": "# Environment\n\n## Setup\n\n- `exit 3`\n"})

        out = self.run_script("add", "abc-6", "--base", "main")

        self.assertNotEqual(out.returncode, 0)
        self.assertIn("exit 3", out.stderr)

    def test_add_refuses_an_existing_branch_unless_reset(self):
        git(self.checkout, "branch", "abc-8")
        git(self.checkout, "commit", "--quiet", "--allow-empty", "-m", "newer main")
        main = git(self.checkout, "rev-parse", "main")

        refused = self.run_script("add", "abc-8", "--base", "main")
        reset = self.run_script("add", "abc-8", "--base", "main", "--reset")

        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("branch 'abc-8' already exists; pass --reset", refused.stderr)
        self.assertEqual(reset.returncode, 0, reset.stderr)
        self.assertEqual(git(self.path("abc-8"), "rev-parse", "HEAD"), main)

    def test_reset_on_an_existing_worktree_moves_its_branch_back_to_the_base(self):
        self.run_script("add", "abc-9", "--base", "main")
        git(self.path("abc-9"), "commit", "--quiet", "--allow-empty", "-m", "previous attempt")

        out = self.run_script("add", "abc-9", "--base", "main", "--reset")

        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(git(self.path("abc-9"), "rev-parse", "HEAD"), git(self.checkout, "rev-parse", "main"))

    def test_reset_refuses_an_existing_worktree_with_uncommitted_changes(self):
        self.run_script("add", "abc-10", "--base", "main")
        git(self.path("abc-10"), "commit", "--quiet", "--allow-empty", "-m", "previous attempt")
        attempt = git(self.path("abc-10"), "rev-parse", "HEAD")
        self.write(self.path("abc-10"), "wip.txt", "wip\n")

        out = self.run_script("add", "abc-10", "--base", "main", "--reset")

        self.assertNotEqual(out.returncode, 0)
        self.assertIn("uncommitted changes", out.stderr)
        self.assertEqual(git(self.path("abc-10"), "rev-parse", "HEAD"), attempt)

    def test_add_refuses_a_name_that_is_not_a_plain_branch_name(self):
        out = self.run_script("add", "../escape", "--base", "main")

        self.assertNotEqual(out.returncode, 0)
        self.assertIn("got '../escape'", out.stderr)

    def test_remove_from_the_integration_worktree_deletes_a_ticket_merged_into_it(self):
        integ = self.path("spec-1")
        self.run_script("add", "spec-1", "--base", "main")
        self.run_script("add", "abc-11", "--base", "spec-1")
        git(self.path("abc-11"), "commit", "--quiet", "--allow-empty", "-m", "ticket work")
        git(integ, "merge", "--quiet", "--no-ff", "-m", "Merge abc-11", "abc-11")

        first = self.run_script("remove", "abc-11", cwd=integ)
        again = self.run_script("remove", "abc-11", cwd=integ)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertFalse(os.path.exists(self.path("abc-11")))
        self.assertNotIn("abc-11", self.branches())

    def test_remove_refuses_unmerged_commits_and_keeps_both(self):
        self.run_script("add", "abc-12", "--base", "main")
        git(self.path("abc-12"), "commit", "--quiet", "--allow-empty", "-m", "unmerged work")

        out = self.run_script("remove", "abc-12")

        self.assertNotEqual(out.returncode, 0)
        self.assertIn("unmerged commits", out.stderr)
        self.assertTrue(os.path.isdir(self.path("abc-12")))
        self.assertIn("abc-12", self.branches())

    def test_remove_refuses_uncommitted_changes_and_keeps_both(self):
        self.run_script("add", "abc-13", "--base", "main")
        self.write(self.path("abc-13"), "wip.txt", "wip\n")

        out = self.run_script("remove", "abc-13")

        self.assertNotEqual(out.returncode, 0)
        self.assertIn("uncommitted changes", out.stderr)
        self.assertTrue(os.path.isdir(self.path("abc-13")))
        self.assertIn("abc-13", self.branches())

    def test_remove_ignores_ignored_files_left_by_setup(self):
        self.commit_files({".gitignore": ".env\nnode_modules/\n", ".worktreeinclude": ".env\n"})
        self.write(self.checkout, ".env", "SECRET=main\n")
        self.run_script("add", "abc-14", "--base", "main")
        self.write(self.path("abc-14"), "node_modules/x/index.js", "x\n")

        out = self.run_script("remove", "abc-14")

        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertFalse(os.path.exists(self.path("abc-14")))
        self.assertNotIn("abc-14", self.branches())

    def test_add_without_a_base_fails_when_the_fetch_fails(self):
        git(self.checkout, "remote", "set-url", "origin", "/nonexistent")

        out = self.run_script("add", "abc-3")

        self.assertNotEqual(out.returncode, 0)
        self.assertIn("pass --base", out.stderr)
        self.assertFalse(os.path.exists(self.path("abc-3")))


if __name__ == "__main__":
    unittest.main()
