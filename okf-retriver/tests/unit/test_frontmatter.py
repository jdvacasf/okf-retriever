import unittest
from datetime import date

from okf_context.parsing.frontmatter import parse_frontmatter


class FrontmatterTests(unittest.TestCase):
    def test_parses_and_preserves_unknown_metadata(self):
        data, body, _ = parse_frontmatter("---\ntitle: Demo\ncustom: value\n---\n# Body\n")
        self.assertEqual(data["custom"], "value")
        self.assertEqual(body, "# Body\n")

    def test_missing_frontmatter_is_valid(self):
        self.assertEqual(parse_frontmatter("# Body")[0], {})
