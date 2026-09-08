import unittest

from okf_context import ContextPackage, ContextSection, ErrorCode, OKFReasoningError
from okf_context.reasoning import MultiDocumentAnswerer


EVIDENCE = [
    ContextSection("b#two", "b", "b.md", ["Two"], "Second.", 1.0, "unknown", None),
    ContextSection("a#one", "a", "a.md", ["One"], "First.", 1.0, "unknown", None),
]


class FixedRetriever:
    def get_context(self, query, max_tokens=None, max_sections=8):
        return ContextPackage(query, EVIDENCE, 2, False)


class FixedProvider:
    def __init__(self, candidate):
        self.candidate = candidate

    def answer(self, request):
        return self.candidate


def valid_candidate():
    return {
        "answer": "Supported.",
        "synthesis": "Evidence supports the answer.",
        "citations": [
            {"path": "b.md", "section_id": "b#two"},
            {"path": "a.md", "section_id": "a#one"},
        ],
        "insufficient": False,
        "conflicts": [],
    }


class AnswerValidationTests(unittest.TestCase):
    def assert_invalid(self, candidate):
        with self.assertRaises(OKFReasoningError) as raised:
            MultiDocumentAnswerer(FixedRetriever(), FixedProvider(candidate)).answer("question")
        self.assertEqual(raised.exception.code, ErrorCode.INVALID_PROVIDER_OUTPUT)

    def test_requires_exact_top_level_fields_and_types(self):
        missing = valid_candidate()
        missing.pop("synthesis")
        unknown = valid_candidate()
        unknown["extra"] = "no"
        wrong_types = [
            {**valid_candidate(), "answer": 1},
            {**valid_candidate(), "citations": {}},
            {**valid_candidate(), "insufficient": 1},
            {**valid_candidate(), "conflicts": {}},
        ]
        for candidate in [missing, unknown, *wrong_types]:
            with self.subTest(candidate=candidate):
                self.assert_invalid(candidate)

    def test_enforces_answer_invariants(self):
        self.assert_invalid({**valid_candidate(), "answer": "", "citations": []})
        self.assert_invalid({**valid_candidate(), "insufficient": True})

    def test_normalizes_citations_and_conflicts_deterministically(self):
        candidate = valid_candidate()
        candidate["conflicts"] = [
            {
                "summary": "Z conflict",
                "citations": [
                    {"path": "b.md", "section_id": "b#two"},
                    {"path": "a.md", "section_id": "a#one"},
                ],
            },
            {
                "summary": "A conflict",
                "citations": [
                    {"path": "a.md", "section_id": "a#one"},
                    {"path": "b.md", "section_id": "b#two"},
                ],
            },
        ]
        answer = MultiDocumentAnswerer(FixedRetriever(), FixedProvider(candidate)).answer("question")
        self.assertEqual([item.path for item in answer.citations], ["a.md", "b.md"])
        self.assertEqual([item.summary for item in answer.conflicts], ["A conflict", "Z conflict"])
        self.assertTrue(all(list(conflict.citations) == sorted(conflict.citations, key=lambda item: (item.path, item.section_id)) for conflict in answer.conflicts))


if __name__ == "__main__":
    unittest.main()
