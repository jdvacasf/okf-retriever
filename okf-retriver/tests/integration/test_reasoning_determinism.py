import unittest

from okf_context import ContextPackage, ContextSection
from okf_context.reasoning import MultiDocumentAnswerer


class FixedRetriever:
    def get_context(self, query, max_tokens=None, max_sections=8):
        sections = [
            ContextSection("b#two", "b", "b.md", ["B"], "B.", 1.0, "unknown", None),
            ContextSection("a#one", "a", "a.md", ["A"], "A.", 1.0, "unknown", None),
        ]
        return ContextPackage(query, sections, 2, False)


class ReverseProvider:
    def answer(self, request):
        citations = [{"path": item.path, "section_id": item.section_id} for item in request.evidence]
        return {
            "answer": "Stable.",
            "synthesis": "Stable synthesis.",
            "citations": citations,
            "insufficient": False,
            "conflicts": [{"summary": "Stable conflict.", "citations": citations}],
        }


class ReasoningDeterminismTests(unittest.TestCase):
    def test_repeated_runs_have_identical_fields_and_ordering(self):
        answerer = MultiDocumentAnswerer(FixedRetriever(), ReverseProvider())
        results = [answerer.answer("same question").to_dict() for _ in range(5)]
        self.assertTrue(all(result == results[0] for result in results[1:]))
        self.assertEqual([item["path"] for item in results[0]["citations"]], ["a.md", "b.md"])


if __name__ == "__main__":
    unittest.main()
