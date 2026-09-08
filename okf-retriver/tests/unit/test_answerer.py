import unittest

from okf_context import ContextPackage, ContextSection
from okf_context.reasoning import MultiDocumentAnswerer


def section(section_id: str, path: str, content: str) -> ContextSection:
    return ContextSection(section_id, path[:-3], path, ["Heading"], content, 1.0, "unknown", None)


class RecordingRetriever:
    def __init__(self) -> None:
        self.calls = []

    def get_context(self, query, max_tokens=None, max_sections=8):
        self.calls.append((query, max_tokens, max_sections))
        sections = [section("a#one", "a.md", "First fact."), section("b#two", "b.md", "Second fact.")]
        return ContextPackage(query, sections, 4, False)


class RecordingProvider:
    def __init__(self) -> None:
        self.requests = []

    def answer(self, request):
        self.requests.append(request)
        return {
            "answer": "Combined answer.",
            "synthesis": "Both facts support it.",
            "citations": [{"path": "a.md", "section_id": "a#one"}],
            "insufficient": False,
            "conflicts": [],
        }


class AnswererTests(unittest.TestCase):
    def test_builds_immutable_request_and_calls_provider_once(self):
        retriever = RecordingRetriever()
        provider = RecordingProvider()
        result = MultiDocumentAnswerer(retriever, provider).answer("Combine facts", max_tokens=50, max_sections=2)

        self.assertEqual(result.answer, "Combined answer.")
        self.assertEqual(retriever.calls, [("Combine facts", 50, 2)])
        self.assertEqual(len(provider.requests), 1)
        request = provider.requests[0]
        self.assertIsInstance(request.evidence, tuple)
        self.assertIn("untrusted", request.instructions.lower())
        self.assertNotIn("First fact.", request.instructions)


if __name__ == "__main__":
    unittest.main()
