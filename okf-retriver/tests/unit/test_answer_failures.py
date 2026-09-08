import unittest

from okf_context import ContextPackage, ContextSection, ErrorCode, OKFReasoningError
from okf_context.reasoning import MultiDocumentAnswerer


class FixedRetriever:
    def __init__(self, sections):
        self.sections = sections

    def get_context(self, query, max_tokens=None, max_sections=8):
        return ContextPackage(query, self.sections, len(self.sections), False)


class NeverProvider:
    def __init__(self):
        self.called = False

    def answer(self, request):
        self.called = True
        raise AssertionError("provider must not be called")


class RaisingProvider:
    def answer(self, request):
        raise RuntimeError("provider secret payload")


class InvalidProvider:
    def answer(self, request):
        return {"answer": "invalid"}


class AnswerFailureTests(unittest.TestCase):
    def setUp(self):
        self.evidence = [
            ContextSection("a#one", "a", "a.md", ["One"], "Fact.", 1.0, "unknown", None)
        ]

    def test_no_evidence_returns_insufficient_without_provider_call(self):
        provider = NeverProvider()
        answer = MultiDocumentAnswerer(FixedRetriever([]), provider).answer("missing fact")
        self.assertTrue(answer.insufficient)
        self.assertEqual(answer.answer, "")
        self.assertFalse(provider.called)

    def test_missing_provider_has_stable_error(self):
        with self.assertRaises(OKFReasoningError) as raised:
            MultiDocumentAnswerer(FixedRetriever(self.evidence)).answer("fact")
        self.assertEqual(raised.exception.code, ErrorCode.PROVIDER_NOT_CONFIGURED)

    def test_provider_exception_has_stable_error_without_leaking_detail(self):
        with self.assertRaises(OKFReasoningError) as raised:
            MultiDocumentAnswerer(FixedRetriever(self.evidence), RaisingProvider()).answer("fact")
        self.assertEqual(raised.exception.code, ErrorCode.PROVIDER_FAILURE)
        self.assertNotIn("secret", str(raised.exception))

    def test_malformed_output_has_stable_error(self):
        with self.assertRaises(OKFReasoningError) as raised:
            MultiDocumentAnswerer(FixedRetriever(self.evidence), InvalidProvider()).answer("fact")
        self.assertEqual(raised.exception.code, ErrorCode.INVALID_PROVIDER_OUTPUT)


if __name__ == "__main__":
    unittest.main()
