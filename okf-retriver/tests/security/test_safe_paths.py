import tempfile
import unittest
from pathlib import Path

from okf_context.exceptions import OKFSandboxViolation
from okf_context.parsing.paths import safe_resolve_path


class SafePathTests(unittest.TestCase):
    def test_rejects_absolute_and_traversal(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            (root_path / "ok.md").write_text("ok")
            for value in ("/etc/passwd", "../secret", "foo/../../secret"):
                with self.assertRaises(OKFSandboxViolation):
                    safe_resolve_path(root_path, value)

    def test_accepts_file_inside_root(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "ok.md"
            path.write_text("ok")
            self.assertEqual(safe_resolve_path(Path(root), "ok.md"), path.resolve())
