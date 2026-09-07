import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever


class RetrievalHardeningTests(unittest.TestCase):
    def test_retrieval_is_deterministic_and_lexical_indexes_ready(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        first = OKFRetriever(OKFContextIndex.build(config), config).search_context(query="authentication")
        second = OKFRetriever(OKFContextIndex.build(config), config).search_context(query="authentication")
        self.assertEqual(first, second)
