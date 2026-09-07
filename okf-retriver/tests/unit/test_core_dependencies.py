import unittest


class CoreDependencyTests(unittest.TestCase):
    def test_core_import_does_not_require_langchain(self):
        import okf_context
        self.assertTrue(hasattr(okf_context, "OKFRetriever"))
