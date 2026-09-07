import unittest

from okf_context.indexing.lexical import LexicalIndex


class LexicalIndexTests(unittest.TestCase):
    def test_search_uses_postings_candidates(self):
        index = LexicalIndex()
        index.add("a", "authentication service")
        index.add("b", "unrelated topic")
        self.assertEqual(index.search("authentication", 10)[0][0], "a")
        self.assertEqual(index.last_candidate_count, 1)
