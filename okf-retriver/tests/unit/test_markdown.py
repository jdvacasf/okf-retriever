import unittest

from okf_context.parsing.markdown import parse_sections


class MarkdownTests(unittest.TestCase):
    def test_nested_sections_and_duplicate_ids_are_deterministic(self):
        sections = parse_sections("# Root\ntext\n## Config\na\n## Config\nb\n", "demo", "demo.md")
        self.assertEqual([section.section_id for section in sections], ["demo#root", "demo#config", "demo#config-2"])
        self.assertEqual(sections[1].content, "a")
