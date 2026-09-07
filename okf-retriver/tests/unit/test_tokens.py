import unittest
from okf_context.retrieval.context_builder import estimate_tokens


class TokenTests(unittest.TestCase):
    def test_estimate_is_positive_for_content(self):
        self.assertEqual(estimate_tokens("one two three"), 3)
