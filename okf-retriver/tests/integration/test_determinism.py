import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever


class DeterminismTests(unittest.TestCase):
    def test_same_query_has_same_order(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        retriever = OKFRetriever(OKFContextIndex.build(config), config)
        first = [item.concept_id for item in retriever.search_context(query="authentication")]
        second = [item.concept_id for item in retriever.search_context(query="authentication")]
        self.assertEqual(first, second)
