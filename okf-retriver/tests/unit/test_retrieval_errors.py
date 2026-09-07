import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.exceptions import ErrorCode, OKFError, OKFInvalidQuery, OKFSectionNotFound


class RetrievalErrorTests(unittest.TestCase):
    def test_unavailable_index_has_stable_error(self):
        with self.assertRaises(OKFError) as raised:
            from okf_context.retrieval.search import RetrievalService
            RetrievalService(OKFContextIndex(), OKFContextConfig("."))
        self.assertEqual(raised.exception.code, ErrorCode.INDEX_NOT_READY)

    def setUp(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        self.retriever = OKFRetriever(OKFContextIndex.build(config), config)

    def test_stable_errors(self):
        with self.assertRaises(OKFInvalidQuery):
            self.retriever.search_context(query="!!!")
        with self.assertRaises(OKFSectionNotFound):
            self.retriever.read_section("services/auth#missing")
        with self.assertRaises(OKFError) as error:
            self.retriever.search_context(query="auth", limit=99)
        self.assertEqual(error.exception.code, ErrorCode.INVALID_LIMIT)
