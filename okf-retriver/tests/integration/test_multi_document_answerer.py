import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.reasoning import MultiDocumentAnswerer


class EvidenceProvider:
    def __init__(self) -> None:
        self.requests = []

    def answer(self, request):
        self.requests.append(request)
        citations = [
            {"path": item.path, "section_id": item.section_id}
            for item in request.evidence
        ]
        return {
            "answer": "Answer from retrieved evidence.",
            "synthesis": "The cited sections were combined.",
            "citations": citations,
            "insufficient": False,
            "conflicts": [],
        }


class MultiDocumentAnswererIntegrationTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf-reasoning"
        config = OKFContextConfig(root)
        self.provider = EvidenceProvider()
        self.answerer = MultiDocumentAnswerer(
            OKFRetriever(OKFContextIndex.build(config), config),
            self.provider,
        )

    def test_combines_multiple_documents(self):
        result = self.answerer.answer("memory context", max_sections=6)
        paths = {citation.path for citation in result.citations}
        self.assertIn("memory.md", paths)
        self.assertTrue({"context.md", "context-copy.md"}.intersection(paths))

    def test_single_document_uses_same_contract(self):
        result = self.answerer.answer("checkpoints")
        self.assertFalse(result.insufficient)
        self.assertEqual({citation.path for citation in result.citations}, {"memory.md"})

    def test_evidence_is_deduplicated_and_bounded(self):
        self.answerer.answer("context", max_tokens=40, max_sections=2)
        request = self.provider.requests[-1]
        contents = [item.content for item in request.evidence]
        self.assertEqual(len(contents), len(set(contents)))
        self.assertLessEqual(len(contents), 2)
        self.assertLessEqual(sum(len(item.content.split()) for item in request.evidence), 40)


if __name__ == "__main__":
    unittest.main()
