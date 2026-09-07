import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.tools import create_okf_tools


class ToolSchemaTests(unittest.TestCase):
    def test_all_tools_are_named_and_schemaed(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        tools = create_okf_tools(OKFRetriever(OKFContextIndex.build(config), config))
        self.assertEqual(len(tools), 7)
        self.assertTrue(all(tool.schema()["parameters"] is not None for tool in tools.values()))
