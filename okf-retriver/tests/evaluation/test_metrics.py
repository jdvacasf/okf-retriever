import unittest
from pathlib import Path
import yaml

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever


class EvaluationTests(unittest.TestCase):
    def test_recall_baseline_metrics(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        retriever = OKFRetriever(OKFContextIndex.build(config), config)
        dataset = yaml.safe_load(Path(__file__).with_name("dataset.yml").read_text())
        recalls = {5: [], 10: []}
        reciprocal_ranks = []
        for case in dataset:
            results = [item.concept_id for item in retriever.search_context(query=case["query"], limit=10)]
            expected = set(case["expected_concepts"])
            for k in recalls:
                recalls[k].append(bool(expected.intersection(results[:k])))
            reciprocal_ranks.append(next((1 / (i + 1) for i, item in enumerate(results) if item in expected), 0))
        metrics = {f"recall_at_{k}": sum(values) / len(values) for k, values in recalls.items()}
        metrics["mrr"] = sum(reciprocal_ranks) / len(reciprocal_ranks)
        self.assertGreaterEqual(metrics["recall_at_5"], 0)
        self.assertGreaterEqual(metrics["recall_at_10"], metrics["recall_at_5"])
        self.assertGreaterEqual(metrics["mrr"], 0)
