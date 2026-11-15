#!/usr/bin/env python3
import os
import subprocess
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "plugins", "engineering", "scripts", "worktree-lock.sh")


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class WorktreeLockTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = os.path.realpath(self.tmp.name)
        self.checkout = os.path.join(base, "app")
        self.worktree = os.path.join(base, "abc-1")
        git(base, "init", "--quiet", "--initial-branch", "main", self.checkout)
        git(self.checkout, "-c", "user.email=t@example.com", "-c", "user.name=T", "commit", "--quiet", "--allow-empty", "-m", "init")
        git(self.checkout, "worktree", "add", "--quiet", "-b", "abc-1", self.worktree)
        self.lock = os.path.join(git(self.worktree, "rev-parse", "--absolute-git-dir"), "agent.lock")
        self.live = subprocess.Popen(["sleep", "60"])

    def tearDown(self):
        self.live.kill()
        self.live.wait()
        self.tmp.cleanup()

    def start_script(self, *args, pid, session):
        env = {**os.environ, "CLAUDE_PID": str(pid), "CLAUDE_CODE_SESSION_ID": session}
        return subprocess.Popen(["bash", SCRIPT, *args], cwd=self.worktree, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def run_script(self, *args, pid, session):
        proc = self.start_script(*args, pid=pid, session=session)
        stdout, stderr = proc.communicate(timeout=10)
        return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)

    def owner(self):
        with open(self.lock) as f:
            return dict(line.split("=", 1) for line in f.read().splitlines())

    def dead_pid(self):
        proc = subprocess.Popen(["true"])
        proc.wait()
        return proc.pid

    def test_acquire_on_a_free_worktree_records_the_session(self):
        out = self.run_script("acquire", pid=self.live.pid, session="s-1")

        self.assertEqual(out.returncode, 0, out.stderr)
        owner = self.owner()
        self.assertEqual((owner["pid"], owner["session"]), (str(self.live.pid), "s-1"))
        self.assertRegex(owner["started_at"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_the_same_session_or_pid_acquires_again_and_keeps_the_lock(self):
        self.run_script("acquire", pid=self.live.pid, session="s-1")
        first = self.owner()

        same_session = self.run_script("acquire", pid=os.getpid(), session="s-1")
        subagent = self.run_script("acquire", pid=self.live.pid, session="s-sub")

        self.assertEqual(same_session.returncode, 0, same_session.stderr)
        self.assertEqual(subagent.returncode, 0, subagent.stderr)
        self.assertEqual(self.owner(), first)

    def test_a_lock_whose_pid_died_is_taken_over_and_logged(self):
        dead = self.dead_pid()
        self.run_script("acquire", pid=dead, session="s-old")

        out = self.run_script("acquire", pid=self.live.pid, session="s-new")

        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn(f"took over the lock held by pid {dead}, session s-old", out.stderr)
        self.assertEqual(self.owner()["session"], "s-new")

    def test_another_live_session_exits_3_naming_the_owner(self):
        self.run_script("acquire", pid=self.live.pid, session="s-1")
        first = self.owner()

        out = self.run_script("acquire", pid=os.getpid(), session="s-2")

        self.assertEqual(out.returncode, 3, out.stderr)
        self.assertIn(f"held by pid {self.live.pid}, session s-1, since {first['started_at']}", out.stderr)
        self.assertEqual(self.owner(), first)

    def test_acquire_with_wait_gets_the_lock_once_the_owner_releases_it(self):
        self.run_script("acquire", pid=self.live.pid, session="s-1")
        waiter = self.start_script("acquire", "--wait", "2", pid=os.getpid(), session="s-2")

        time.sleep(0.5)
        self.run_script("release", pid=self.live.pid, session="s-1")
        _, stderr = waiter.communicate(timeout=10)

        self.assertEqual(waiter.returncode, 0, stderr)
        self.assertEqual(self.owner()["session"], "s-2")

    def test_acquire_with_wait_exits_3_when_the_owner_keeps_the_lock(self):
        self.run_script("acquire", pid=self.live.pid, session="s-1")

        out = self.run_script("acquire", "--wait", "1", pid=os.getpid(), session="s-2")

        self.assertEqual(out.returncode, 3, out.stderr)
        self.assertEqual(self.owner()["session"], "s-1")

    def test_release_frees_only_a_lock_of_this_session(self):
        self.run_script("acquire", pid=self.live.pid, session="s-1")

        other = self.run_script("release", pid=os.getpid(), session="s-2")
        held_after_other = os.path.exists(self.lock)
        own = self.run_script("release", pid=self.live.pid, session="s-1")
        again = self.run_script("release", pid=self.live.pid, session="s-1")

        self.assertEqual([other.returncode, own.returncode, again.returncode], [0, 0, 0])
        self.assertTrue(held_after_other)
        self.assertFalse(os.path.exists(self.lock))


if __name__ == "__main__":
    unittest.main()
