import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever


class ContextBuilderTests(unittest.TestCase):
    def test_context_has_provenance_and_budget(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root, default_context_tokens=20)
        package = OKFRetriever(OKFContextIndex.build(config), config).get_context("authentication", max_tokens=20)
        self.assertLessEqual(package.estimated_tokens, 20)
        self.assertTrue(all(section.path for section in package.sections))

    def test_graph_expansion_preserves_freshness(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        package = OKFRetriever(OKFContextIndex.build(config), config).get_context("redis", max_tokens=100)
        self.assertTrue(any(section.freshness != "unknown" for section in package.sections))
