import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever


class RankingTests(unittest.TestCase):
    def test_title_and_tag_matches_rank(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        results = OKFRetriever(OKFContextIndex.build(OKFContextConfig(root)), OKFContextConfig(root)).search_context(query="authentication", limit=5)
        self.assertIn("services/auth", [result.concept_id for result in results])
        self.assertEqual(results, sorted(results, key=lambda item: (-item.score, item.concept_id)))
