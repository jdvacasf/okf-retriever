import unittest
from pathlib import Path

from okf_context.exceptions import OKFError
from okf_context.parsing.frontmatter import parse_frontmatter


ROOT = Path(__file__).parents[1] / "fixtures" / "okf-hardening"


class FrontmatterHardeningTests(unittest.TestCase):
    def test_malformed_yaml_keeps_body_and_diagnostic(self):
        data, body, diagnostics = parse_frontmatter((ROOT / "malformed.md").read_text())
        self.assertEqual(data, {})
        self.assertIn("# Recovered", body)
        self.assertEqual(diagnostics[0].kind, "MALFORMED_FRONTMATTER")
        self.assertTrue(diagnostics[0].recoverable)

    def test_missing_delimiter_recovers_from_first_heading(self):
        _, body, diagnostics = parse_frontmatter((ROOT / "missing-delimiter.md").read_text())
        self.assertTrue(body.startswith("# Recovered heading"))
        self.assertEqual(diagnostics[0].kind, "MISSING_FRONTMATTER_DELIMITER")

    def test_missing_delimiter_without_boundary_is_rejected(self):
        with self.assertRaises(OKFError):
            parse_frontmatter((ROOT / "no-boundary.md").read_text())
