import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.exceptions import ErrorCode, ToolInputError
from okf_context.tools import create_okf_tools


class ToolValidationTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).parents[1] / "fixtures" / "okf"
        config = OKFContextConfig(root)
        self.tools = create_okf_tools(OKFRetriever(OKFContextIndex.build(config), config))

    def test_unknown_argument_is_rejected(self):
        with self.assertRaises(ToolInputError) as error:
            self.tools["browse_okf"](unexpected=True)
        self.assertEqual(error.exception.code, ErrorCode.TOOL_INPUT)

    def test_schema_is_explicit(self):
        schema = self.tools["search_okf_context"].schema()
        self.assertIn("query", {parameter["name"] for parameter in schema["parameters"]})

    def test_unsearchable_query_is_rejected_at_tool_boundary(self):
        with self.assertRaises(ToolInputError):
            self.tools["search_okf_context"](query="!!!")

    def test_configured_upper_bound_is_rejected_at_tool_boundary(self):
        with self.assertRaises(ToolInputError):
            self.tools["search_okf_context"](query="auth", limit=99)
