import unittest

from okf_context.models import CorpusQualityReport, RetrievalDiagnostic


class HardeningModelTests(unittest.TestCase):
    def test_quality_report_is_serializable_and_sorted(self):
        report = CorpusQualityReport(1, 0, 2, 1, 0, 1, {"BROKEN_LINK": 1}, {"BROKEN_LINK": ["b.md", "a.md"]}, 0.1)
        self.assertEqual(report.to_dict()["diagnostic_paths"], {"BROKEN_LINK": ["a.md", "b.md"]})

    def test_diagnostic_can_be_recoverable(self):
        self.assertTrue(RetrievalDiagnostic("MALFORMED_FRONTMATTER", "x", recoverable=True).recoverable)

    def test_diagnostic_paths_are_unique_and_sorted(self):
        report = CorpusQualityReport(0, 0, 0, 0, 0, 0, {"BROKEN_LINK": 2}, {"BROKEN_LINK": ["b.md", "a.md", "a.md"]}, 0.1)
        self.assertEqual(report.to_dict()["diagnostic_paths"], {"BROKEN_LINK": ["a.md", "b.md"]})
