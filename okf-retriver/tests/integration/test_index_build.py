import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex


FIXTURE = Path(__file__).parents[1] / "fixtures" / "okf"


class IndexBuildTests(unittest.TestCase):
    def test_builds_rebuildable_index(self):
        config = OKFContextConfig(FIXTURE)
        first = OKFContextIndex.build(config)
        second = OKFContextIndex.build(config)
        self.assertTrue(first.ready)
        self.assertEqual(sorted(first.concepts), sorted(second.concepts))
        self.assertEqual(sorted(first.sections), sorted(second.sections))
        self.assertIn("infrastructure/redis", first.outgoing["services/auth"])
        self.assertIn("services/auth", first.incoming["infrastructure/redis"])
        self.assertEqual(first.build_stats["documents"], len(first.concepts))
        self.assertEqual(first.build_stats["sections"], len(first.sections))
        self.assertIn("duration_seconds", first.build_stats)

    def test_unknown_metadata_and_diagnostics_are_safe(self):
        index = OKFContextIndex.build(OKFContextConfig(FIXTURE))
        self.assertIn("broken", index.concepts)
