import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.reasoning import MultiDocumentAnswerer


class ConflictProvider:
    def answer(self, request):
        citations = [
            {"path": item.path, "section_id": item.section_id}
            for item in request.evidence
            if item.path.startswith("retention-")
        ]
        return {
            "answer": "The sources disagree about retention.",
            "synthesis": "One policy says 30 days and another says 90 days.",
            "citations": citations,
            "insufficient": False,
            "conflicts": [{"summary": "Retention is 30 or 90 days.", "citations": citations}],
        }


class MultiDocumentFailureIntegrationTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf-reasoning"
        config = OKFContextConfig(root)
        self.retriever = OKFRetriever(OKFContextIndex.build(config), config)

    def test_absent_evidence_is_insufficient(self):
        answer = MultiDocumentAnswerer(self.retriever, ConflictProvider()).answer("absent quantum policy")
        self.assertTrue(answer.insufficient)
        self.assertFalse(answer.citations)

    def test_conflicting_sources_cite_both_sides(self):
        answer = MultiDocumentAnswerer(self.retriever, ConflictProvider()).answer("session retention")
        self.assertFalse(answer.insufficient)
        self.assertEqual(len(answer.conflicts), 1)
        self.assertEqual(
            {item.path for item in answer.conflicts[0].citations},
            {"retention-current.md", "retention-legacy.md"},
        )


if __name__ == "__main__":
    unittest.main()
