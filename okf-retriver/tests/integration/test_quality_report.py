import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex


class QualityReportTests(unittest.TestCase):
    def test_report_counts_recovery_rejection_and_broken_links(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf-hardening"
        index = OKFContextIndex.build(OKFContextConfig(root))
        report = index.quality_report
        self.assertIsNotNone(report)
        self.assertEqual(report.documents_indexed, 5)
        self.assertEqual(report.documents_rejected, 1)
        self.assertEqual(report.links_broken, 1)
        self.assertEqual(report.diagnostics_by_kind["BROKEN_LINK"], 1)

    def test_missing_root_still_exposes_quality_report(self):
        root = Path(__file__).parents[1] / "fixtures" / "does-not-exist"
        index = OKFContextIndex.build(OKFContextConfig(root))
        self.assertIsNotNone(index.quality_report)
        self.assertEqual(index.quality_report.documents_indexed, 0)
