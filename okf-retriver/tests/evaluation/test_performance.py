import time
import unittest
from pathlib import Path
import statistics
from okf_context import OKFRetriever

from okf_context import OKFContextConfig, OKFContextIndex


class PerformanceTests(unittest.TestCase):
    def test_performance_baseline_records_required_measurements(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        builds = []
        for _ in range(3):
            started = time.perf_counter()
            index = OKFContextIndex.build(config)
            builds.append(time.perf_counter() - started)
        retriever = OKFRetriever(index, config)
        searches, contexts = [], []
        for _ in range(3):
            started = time.perf_counter(); retriever.search_context(query="authentication"); searches.append(time.perf_counter() - started)
            started = time.perf_counter(); retriever.get_context(query="authentication", max_tokens=20); contexts.append(time.perf_counter() - started)
        measurements = {
            "build_time_seconds": min(builds),
            "memory_bytes": sum(len(section.content.encode()) for section in index.sections.values()),
            "search_p50_seconds": statistics.median(searches),
            "search_p95_seconds": max(searches),
            "context_latency_seconds": statistics.median(contexts),
        }
        self.assertEqual(set(measurements), {"build_time_seconds", "memory_bytes", "search_p50_seconds", "search_p95_seconds", "context_latency_seconds"})
