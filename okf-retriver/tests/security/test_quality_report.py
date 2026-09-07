import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex


class QualityReportSecurityTests(unittest.TestCase):
    def test_report_has_no_body_or_absolute_root(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf-hardening"
        payload = OKFContextIndex.build(OKFContextConfig(root)).quality_report.to_dict()
        text = repr(payload)
        self.assertNotIn("# Recovered", text)
        self.assertNotIn(str(root.resolve()), text)
