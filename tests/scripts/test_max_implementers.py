#!/usr/bin/env python3
import os
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "plugins", "engineering", "skills", "implement-spec", "scripts", "max-implementers.sh")


class MaxImplementersTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.checkout = self.tmp.name
        subprocess.run(["git", "init", "--quiet", self.checkout], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def environment(self, content):
        os.makedirs(os.path.join(self.checkout, "docs", "agents"), exist_ok=True)
        with open(os.path.join(self.checkout, "docs", "agents", "environment.md"), "w") as f:
            f.write(content)

    def run_script(self, cwd=None):
        return subprocess.run(["bash", SCRIPT], cwd=cwd or self.checkout, capture_output=True, text=True, check=False)

    def test_prints_the_limit_from_the_concurrency_section(self):
        self.environment("# Environment\n\n## Setup\n\n- `make deps`\n\n## Concurrency\n\n- Max implementers: 2\n")

        out = self.run_script()

        self.assertEqual((out.returncode, out.stdout), (0, "2\n"), out.stderr)

    def test_prints_nothing_without_the_line(self):
        self.environment("# Environment\n\n## Setup\n\n- Max implementers: 4\n")

        out = self.run_script()

        self.assertEqual((out.returncode, out.stdout), (0, ""), out.stderr)

    def test_prints_nothing_without_an_environment_file(self):
        out = self.run_script()

        self.assertEqual((out.returncode, out.stdout), (0, ""), out.stderr)

    def test_rejects_a_limit_that_is_not_a_positive_integer(self):
        for value in ("0", "three", ""):
            with self.subTest(value=value):
                self.environment(f"## Concurrency\n\n- Max implementers: {value}\n")

                out = self.run_script()

                self.assertNotEqual(out.returncode, 0)
                self.assertEqual(out.stdout, "")
                self.assertIn("positive integer", out.stderr)


if __name__ == "__main__":
    unittest.main()
