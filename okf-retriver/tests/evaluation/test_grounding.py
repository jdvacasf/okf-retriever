import unittest
from pathlib import Path

import yaml

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.reasoning import MultiDocumentAnswerer


class LabeledProvider:
    def __init__(self, case):
        self.case = case
        self.request = None

    def answer(self, request):
        self.request = request
        by_id = {item.section_id: item for item in request.evidence}
        citations = [
            {"path": by_id[section_id].path, "section_id": section_id}
            for section_id in self.case["required_section_ids"]
        ]
        conflicts = []
        if self.case["expected_outcome"] == "conflict":
            conflicts = [{"summary": "The labeled sources conflict.", "citations": citations}]
        return {
            "answer": "Labeled supported answer.",
            "synthesis": "Required evidence was cited.",
            "citations": citations,
            "insufficient": False,
            "conflicts": conflicts,
        }


class GroundingEvaluationTests(unittest.TestCase):
    def test_labeled_grounding_insufficiency_and_conflict_rates(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf-reasoning"
        config = OKFContextConfig(root)
        retriever = OKFRetriever(OKFContextIndex.build(config), config)
        cases = yaml.safe_load(Path(__file__).with_name("reasoning_dataset.yml").read_text())

        supported_results = []
        insufficient_results = []
        conflict_results = []
        for case in cases:
            self.assertIn(case["expected_outcome"], {"supported", "insufficient", "conflict"})
            provider = LabeledProvider(case)
            answer = MultiDocumentAnswerer(retriever, provider).answer(case["query"])
            cited = {item.section_id for item in answer.citations}
            required = set(case["required_section_ids"])
            if case["expected_outcome"] == "supported":
                supported_results.append(required <= cited and len(cited) >= case["minimum_citations"])
            elif case["expected_outcome"] == "insufficient":
                insufficient_results.append(answer.insufficient and not answer.answer)
            else:
                conflict_results.append(bool(answer.conflicts) and required <= cited)

        self.assertGreaterEqual(sum(supported_results) / len(supported_results), 0.9)
        self.assertTrue(all(insufficient_results))
        self.assertTrue(all(conflict_results))


if __name__ == "__main__":
    unittest.main()
