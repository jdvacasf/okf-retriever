from okf_context.exceptions import ErrorCode, OKFError
from okf_context.models import ContextPackage, ContextSection, SearchResult
from okf_context.parsing.frontmatter import freshness
from .traversal import traverse


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split())) if text.strip() else 0


def build_context(service, query: str, max_tokens: int = 4000, max_sections: int = 8) -> ContextPackage:
    if max_tokens < 1 or max_tokens > service.config.max_context_tokens:
        raise OKFError("invalid token budget", ErrorCode.INVALID_TOKEN_BUDGET)
    if max_sections < 1:
        raise OKFError("invalid section limit", ErrorCode.INVALID_LIMIT)
    candidates = service.search_sections(query, limit=service.config.max_search_limit)
    known_sections = {candidate.section_id for candidate in candidates}
    for candidate in list(candidates[:3]):
        for node in traverse(service.index, candidate.concept_id, depth=1, limit=service.config.max_graph_results):
            concept = service.index.concepts.get(node.concept_id)
            if not concept:
                continue
            for section_id in concept.section_ids:
                if section_id not in known_sections:
                    section = service.index.sections[section_id]
                    candidates.append(SearchResult(concept.concept_id, concept.path, candidate.score * 0.1, section_id, concept.title, section.heading, [], section.content[:service.config.snippet_chars], freshness(concept.stale_after), concept.verified, concept.status))
                    known_sections.add(section_id)
    selected: list[ContextSection] = []
    seen_content: set[str] = set()
    used = 0
    for candidate in candidates:
        section = service.read_section(candidate.section_id)
        if section.content in seen_content:
            continue
        cost = estimate_tokens(section.content)
        if used + cost > max_tokens:
            continue
        selected.append(ContextSection(section.section_id, section.concept_id, section.path, section.heading_path, section.content, candidate.score, candidate.freshness, candidate.verified))
        seen_content.add(section.content)
        used += cost
        if len(selected) >= max_sections:
            break
    return ContextPackage(query, selected, used, len(selected) < len(candidates))
