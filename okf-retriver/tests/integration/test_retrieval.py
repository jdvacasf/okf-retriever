import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        self.retriever = OKFRetriever(OKFContextIndex.build(config), config)

    def test_search_inspect_read_and_traverse(self):
        self.assertTrue(self.retriever.search_context(query="autenticación"))
        self.assertEqual(self.retriever.inspect_concept("services/auth").title, "Authentication Service")
        self.assertEqual(self.retriever.read_section("services/auth#deployment").heading, "Deployment")
        self.assertEqual(self.retriever.traverse_graph(concept_id="services/auth", direction="outgoing")[0].concept_id, "infrastructure/redis")
