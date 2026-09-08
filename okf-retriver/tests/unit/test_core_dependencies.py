import unittest


class CoreDependencyTests(unittest.TestCase):
    def test_core_import_does_not_require_langchain(self):
        import okf_context
        from okf_context.reasoning import AnswerProvider, MultiDocumentAnswerer

        self.assertTrue(hasattr(okf_context, "OKFRetriever"))
        self.assertTrue(AnswerProvider)
        self.assertTrue(MultiDocumentAnswerer)
