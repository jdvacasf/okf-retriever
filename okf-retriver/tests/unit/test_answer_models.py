import unittest

from okf_context.models import (
    AnswerRequest,
    Citation,
    ContextSection,
    EvidenceConflict,
    GroundedAnswer,
)


def evidence(section_id: str = "memory#langgraph-memory") -> ContextSection:
    return ContextSection(
        section_id=section_id,
        concept_id="memory",
        path="memory.md",
        heading_path=["LangGraph Memory"],
        content="Memory preserves state.",
        relevance=1.0,
        freshness="unknown",
        verified=None,
    )


class AnswerModelTests(unittest.TestCase):
    def test_answer_request_is_immutable_and_rejects_invalid_evidence(self):
        request = AnswerRequest("What is memory?", (evidence(),), "Use evidence only.")
        self.assertEqual(request.evidence[0].path, "memory.md")
        with self.assertRaises(AttributeError):
            request.question = "changed"
        with self.assertRaises(AttributeError):
            request.evidence[0].path = "fabricated.md"
        with self.assertRaises(AttributeError):
            request.evidence[0].heading_path += ("Injected",)
        with self.assertRaises(ValueError):
            AnswerRequest("!!!", (evidence(),), "Use evidence only.")
        with self.assertRaises(ValueError):
            AnswerRequest("memory", (), "Use evidence only.")
        with self.assertRaises(ValueError):
            AnswerRequest("memory", (evidence(), evidence()), "Use evidence only.")

    def test_grounded_answer_invariants(self):
        citation = Citation("memory.md", "memory#langgraph-memory")
        with self.assertRaises(ValueError):
            GroundedAnswer("Supported", "Summary", (), False, ())
        with self.assertRaises(ValueError):
            GroundedAnswer("Unsupported", "Summary", (), True, ())
        with self.assertRaises(ValueError):
            GroundedAnswer("Supported", "Summary", (citation, citation), False, ())
        with self.assertRaises(ValueError):
            GroundedAnswer("Supported", "Summary", [citation], False, ())
        self.assertEqual(
            GroundedAnswer("Supported", "Summary", (citation,), False, ()).answer,
            "Supported",
        )

    def test_serialization_has_stable_plain_values(self):
        first = Citation("memory.md", "memory#langgraph-memory")
        second = Citation("context.md", "context#context-management")
        conflict = EvidenceConflict("Different guidance", (first, second))
        answer = GroundedAnswer("Use both.", "Combined evidence.", (first, second), False, (conflict,))
        self.assertEqual(
            answer.to_dict(),
            {
                "answer": "Use both.",
                "synthesis": "Combined evidence.",
                "citations": [
                    {"path": "memory.md", "section_id": "memory#langgraph-memory"},
                    {"path": "context.md", "section_id": "context#context-management"},
                ],
                "insufficient": False,
                "conflicts": [
                    {
                        "summary": "Different guidance",
                        "citations": [
                            {"path": "memory.md", "section_id": "memory#langgraph-memory"},
                            {"path": "context.md", "section_id": "context#context-management"},
                        ],
                    }
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
