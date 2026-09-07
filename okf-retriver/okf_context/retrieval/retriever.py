from okf_context.retrieval.context_builder import build_context
from okf_context.retrieval.search import RetrievalService
from okf_context.retrieval.traversal import traverse


class OKFRetriever:
    def __init__(self, index, config):
        self.index, self.config = index, config
        self.service = RetrievalService(index, config)

    def search_context(self, **kwargs):
        return self.service.search_context(**kwargs)

    def search_sections(self, **kwargs):
        return self.service.search_sections(**kwargs)

    def browse(self, **kwargs):
        return self.service.browse(**kwargs)

    def inspect_concept(self, concept_id):
        return self.service.inspect(concept_id)


    def read_section(self, section_id):
        return self.service.read_section(section_id)

    def traverse_graph(self, **kwargs):
        return traverse(self.index, **kwargs)

    def get_context(self, query, max_tokens=None, max_sections=8):
        return build_context(self.service, query, max_tokens or self.config.default_context_tokens, max_sections)
