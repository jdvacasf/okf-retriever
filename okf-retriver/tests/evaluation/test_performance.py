import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever


class RetrievalPerformanceTests(unittest.TestCase):
    def test_candidate_count_is_bounded_by_index_size(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        index = OKFContextIndex.build(config)
        OKFRetriever(index, config).search_context(query="authentication")
        self.assertLessEqual(index.concept_lexical.last_candidate_count, len(index.concepts))
