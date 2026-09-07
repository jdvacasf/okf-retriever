import unittest
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.exceptions import ErrorCode, ToolInputError
from okf_context.tools import create_okf_tools

class SimpleOKFAgent:
    """Minimal deterministic agent used to approve the tool contract."""

    def __init__(self, retriever):
        tools = create_okf_tools(retriever)
        self.search_context = tools["search_okf_context"]
        self.search_sections = tools["search_okf_sections"]
        self.browse = tools["browse_okf"]
        self.inspect_concept = tools["inspect_okf_concept"]
        self.read_section = tools["read_okf_section"]
        self.traverse_graph = tools["traverse_okf_graph"]
        self.get_context = tools["get_okf_context"]

    def run(self, query: str):
        return self.get_context(query=query, max_tokens=4000)


class SimpleAgentToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path("/home/dvf/ia/uxxi-academy")
        config = OKFContextConfig(root)
        retriever = OKFRetriever(OKFContextIndex.build(config), config)
        cls.quality_report = retriever.index.quality_report
        cls.agent = SimpleOKFAgent(retriever)

    def test_agent_retrieves_bounded_provenance_preserving_context(self):
        result = self.agent.run("context engineering")

        self.assertTrue(result.sections)
        self.assertLessEqual(result.estimated_tokens, 4000)
        self.assertTrue(all(section.path for section in result.sections))
        self.assertTrue(all(section.concept_id for section in result.sections))
        self.assertIsNotNone(self.quality_report)
        self.assertGreater(self.quality_report.documents_indexed, 0)
        print("\n[agent] query: context engineering")
        print(f"[agent] estimated_tokens: {result.estimated_tokens}")
        for section in result.sections:
            print(f"[agent] {section.concept_id} | {section.path} | {section.heading_path}")
            print(f"        {section.content[:1600].replace(chr(10), ' ')}")

    def test_agent_tools_are_invocable(self):
        context_results = self.agent.search_context(query="alucinaciones")
        section_results = self.agent.search_sections(query="ejecución incremental")
        browse_result = self.agent.browse(path="IA-academy/curso-ingenieria-del-prompt")
        self.assertTrue(context_results)
        self.assertTrue(section_results)
        self.assertIn("concepts", browse_result)
        concept_id = "IA-academy/curso-ingenieria-del-prompt/05-trabajo-con-contexto-y-conocimiento/05-context-engineering"
        self.assertEqual(self.agent.inspect_concept(concept_id=concept_id).concept_id, concept_id)
        section_id = f"{concept_id}#context-engineering"
        self.assertTrue(self.agent.read_section(section_id=section_id).content)
        graph_result = self.agent.traverse_graph(concept_id=concept_id)
        final_context = self.agent.get_context(query="context engineering", max_tokens=400)
        self.assertIsInstance(graph_result, list)
        self.assertTrue(final_context.sections)
        print("\n[tools] search_okf_context:", [(item.concept_id, item.score) for item in context_results[:3]])
        print("[tools] search_okf_sections:", [(item.section_id, item.score) for item in section_results[:3]])
        print("[tools] browse_okf concepts:", len(browse_result["concepts"]))
        print("[tools] traverse_okf_graph:", graph_result[:3])

    def test_agent_preserves_stable_invalid_query_error(self):
        with self.assertRaises(ToolInputError) as error:
            self.agent.run("!!!")
        self.assertEqual(error.exception.code, ErrorCode.TOOL_INPUT)


if __name__ == "__main__":
    unittest.main()
