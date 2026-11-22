"""Regression checks for the validator used to gate Pages deployment."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts/host/check-docs.py"


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "docs").mkdir()
        (self.root / "site").mkdir()
        (self.root / "README.md").write_text("# Readme\n")
        (self.root / "AGENTS.md").write_text("# Rules\n")
        (self.root / "docs/index.md").write_text("# Home\n")
        (self.root / "zensical.toml").write_text(
            '[project]\nsite_url = "https://example.github.io/lab/"\n'
            'docs_dir = "docs"\nsite_dir = "site"\nnav = ["index.md"]\n'
        )
        self.page = self.root / "site/index.html"
        self.page.write_text('<h1 id="home">Home</h1><a href="/lab/#home">Home</a>')

    def run_check(self):
        return subprocess.run(
            [sys.executable, str(CHECK)],
            cwd=self.root, capture_output=True, text=True, timeout=5
        )

    def test_valid_subpath_and_anchor(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_root_absolute_link_cannot_escape_repository_subpath(self):
        self.page.write_text('<a href="/index.html">Wrong root</a>')
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("escapes site subpath", result.stderr)

    def test_broken_page_and_anchor_are_rejected(self):
        self.page.write_text(
            '<a href="missing/">Missing page</a><a href="#missing">Missing anchor</a>'
        )
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken built link", result.stderr)
        self.assertIn("missing anchor", result.stderr)

    def test_unlisted_page_and_broken_snippet_are_rejected(self):
        (self.root / "docs/extra.md").write_text('# Extra\n--8<-- "missing.c"\n')
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Page missing from navigation", result.stderr)
        self.assertIn("missing snippet", result.stderr)
