import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex


class RecoveryRateTests(unittest.TestCase):
    def test_fixture_recovery_rate_is_at_least_95_percent(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf-hardening"
        index = OKFContextIndex.build(OKFContextConfig(root))
        recoverable = {"malformed.md", "missing-delimiter.md", "unknown.md", "valid.md"}
        indexed = {concept.path for concept in index.concepts.values()}
        self.assertGreaterEqual(len(recoverable & indexed) / len(recoverable), 0.95)
