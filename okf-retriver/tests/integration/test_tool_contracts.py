import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.tools import create_okf_tools


class ToolContractTests(unittest.TestCase):
    def test_seven_tools_are_created(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        tools = create_okf_tools(OKFRetriever(OKFContextIndex.build(config), config))
        self.assertEqual([tool.__name__ for tool in tools], ["search_okf_context", "search_okf_sections", "browse_okf", "inspect_okf_concept", "read_okf_section", "traverse_okf_graph", "get_okf_context"])

    def test_all_tools_are_invocable(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        retriever = OKFRetriever(OKFContextIndex.build(config), config)
        tools = create_okf_tools(retriever)
        self.assertTrue(tools[0](query="authentication"))
        self.assertTrue(tools[1](query="authentication"))
        self.assertIn("concepts", tools[2]())
        self.assertEqual(tools[3](concept_id="services/auth").concept_id, "services/auth")
        self.assertTrue(tools[4](section_id="services/auth#deployment").content)
        self.assertIsInstance(tools[5](concept_id="services/auth"), list)
        self.assertTrue(tools[6](query="authentication").sections)
