import unittest

from okf_context import ContextPackage, ContextSection, OKFReasoningError
from okf_context.reasoning import MultiDocumentAnswerer


class SensitiveRetriever:
    def get_context(self, query, max_tokens=None, max_sections=8):
        section = ContextSection("secret#one", "secret", "secret.md", ["Secret"], "sensitive evidence", 1.0, "unknown", None)
        return ContextPackage(query, [section], 2, False)


class FailingProvider:
    def answer(self, request):
        raise RuntimeError("sensitive provider payload")


class AnswerObservabilityTests(unittest.TestCase):
    def test_failure_log_contains_only_safe_outcome_and_elapsed_time(self):
        with self.assertLogs("okf_context", level="INFO") as logs:
            with self.assertRaises(OKFReasoningError):
                MultiDocumentAnswerer(SensitiveRetriever(), FailingProvider()).answer("sensitive question")
        output = " ".join(logs.output)
        self.assertIn("provider_failure", output)
        self.assertIn("elapsed_seconds=", output)
        for secret in ("sensitive question", "sensitive evidence", "sensitive provider payload"):
            self.assertNotIn(secret, output)


if __name__ == "__main__":
    unittest.main()
