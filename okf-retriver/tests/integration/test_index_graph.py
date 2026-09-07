import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex


class IndexGraphTests(unittest.TestCase):
    def test_index_document_and_backlinks(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        index = OKFContextIndex.build(OKFContextConfig(root))
        self.assertIn("index", index.concepts)
        self.assertIn("runbooks/deploy-auth", index.incoming["services/auth"])
