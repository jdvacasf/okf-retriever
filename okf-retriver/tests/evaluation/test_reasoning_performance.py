import time
import unittest

from okf_context import ContextPackage, ContextSection
from okf_context.reasoning import MultiDocumentAnswerer


class BoundedRetriever:
    def __init__(self):
        self.calls = []

    def get_context(self, query, max_tokens=None, max_sections=8):
        self.calls.append((max_tokens, max_sections))
        sections = [
            ContextSection(f"doc-{index}#fact", f"doc-{index}", f"doc-{index}.md", ["Fact"], f"fact-{index}", 1.0, "unknown", None)
            for index in range(max_sections)
        ]
        return ContextPackage(query, sections, len(sections), False)


class RecordingProvider:
    def __init__(self):
        self.last_request = None

    def answer(self, request):
        self.last_request = request
        first = request.evidence[0]
        return {
            "answer": "Fast answer.",
            "synthesis": "One cited fact.",
            "citations": [{"path": first.path, "section_id": first.section_id}],
            "insufficient": False,
            "conflicts": [],
        }


class ReasoningPerformanceTests(unittest.TestCase):
    def test_orchestration_overhead_and_evidence_budget(self):
        retriever = BoundedRetriever()
        provider = RecordingProvider()
        answerer = MultiDocumentAnswerer(retriever, provider)
        started = time.perf_counter()
        for _ in range(100):
            answerer.answer("bounded question", max_tokens=20, max_sections=20)
        average_seconds = (time.perf_counter() - started) / 100

        self.assertLess(average_seconds, 0.05)
        self.assertEqual(retriever.calls[-1], (20, 20))
        self.assertEqual(len(provider.last_request.evidence), 20)
        self.assertLessEqual(sum(len(item.content.split()) for item in provider.last_request.evidence), 20)


if __name__ == "__main__":
    unittest.main()
