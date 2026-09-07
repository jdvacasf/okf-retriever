from pathlib import Path

from okf_context.config import OKFContextConfig
from okf_context.exceptions import ErrorCode, OKFError, OKFInvalidQuery
from okf_context.indexing.index import OKFContextIndex
from okf_context.models import SearchResult
from okf_context.parsing.frontmatter import freshness
from .ranking import score_fields


class RetrievalService:
    def __init__(self, index: OKFContextIndex, config: OKFContextConfig):
        if not index.ready:
            raise OKFError("index is not ready", ErrorCode.INDEX_NOT_READY)
        self.index, self.config = index, config

    def _validate_query(self, query: str) -> None:
        if not query or not query.strip() or not __import__("re").search(r"[\wÀ-ÿ]", query):
            raise OKFInvalidQuery("query has no searchable tokens")

    def _validate_lexical_indexes(self) -> None:
        if (self.index.concept_lexical is None or self.index.section_lexical is None
                or not self.index.concept_lexical.is_consistent(set(self.index.concepts))
                or not self.index.section_lexical.is_consistent(set(self.index.sections))):
            raise OKFError("lexical index is not ready", ErrorCode.LEXICAL_INDEX_NOT_READY)

    def search_context(self, query: str, *, types=None, tags=None, status=None, path_prefix=None, limit=None) -> list[SearchResult]:
        self._validate_query(query)
        limit = self._limit(limit)
        self._validate_lexical_indexes()
        candidates = self.index.concept_lexical.search(query, len(self.index.concepts))
        results = []
        for concept_id, _, _ in candidates:
            concept = self.index.concepts[concept_id]
            if types and concept.type not in types or tags and not set(tags).intersection(concept.tags) or status and concept.status not in status or path_prefix and not concept.path.startswith(path_prefix):
                continue
            sections = [self.index.sections[item] for item in concept.section_ids]
            body = "\n".join(section.content for section in sections)
            score, matched, breakdown = score_fields(query, {"title": concept.title or "", "description": concept.description or "", "tags": " ".join(concept.tags), "body": body})
            if concept.status == "current":
                breakdown["metadata"] = 0.1
                score += 0.1
            if score:
                results.append(SearchResult(concept.concept_id, concept.path, score, title=concept.title, matched_terms=matched, snippet=body[:self.config.snippet_chars], freshness=freshness(concept.stale_after), verified=concept.verified, status=concept.status, score_breakdown=breakdown))
        return sorted(results, key=lambda item: (-item.score, item.concept_id))[:limit]

    def search_sections(self, query: str, *, path_prefix=None, concept_ids=None, limit=None) -> list[SearchResult]:
        self._validate_query(query)
        limit = self._limit(limit)
        self._validate_lexical_indexes()
        candidates = self.index.section_lexical.search(query, len(self.index.sections))
        results = []
        for section_id, _, _ in candidates:
            section = self.index.sections[section_id]
            concept = self.index.concepts[section.concept_id]
            if path_prefix and not section.path.startswith(path_prefix) or concept_ids and section.concept_id not in concept_ids:
                continue
            score, matched, breakdown = score_fields(query, {"title": concept.title or "", "heading": " ".join(section.heading_path), "tags": " ".join(concept.tags), "body": section.content})
            if score:
                results.append(SearchResult(concept.concept_id, section.path, score, section.section_id, concept.title, section.heading, matched, section.content[:self.config.snippet_chars], freshness(concept.stale_after), concept.verified, concept.status, breakdown))
        return sorted(results, key=lambda item: (-item.score, item.section_id or ""))[:limit]

    def browse(self, path: str = "", depth: int = 1) -> dict:
        prefix = path.rstrip("/")
        concepts = [concept for concept in self.index.concepts.values() if concept.path.startswith(prefix)]
        directories = sorted({str(Path(concept.path).parent) for concept in concepts if str(Path(concept.path).parent) != "."})
        return {"path": path, "concepts": [{"concept_id": c.concept_id, "title": c.title, "type": c.type} for c in concepts], "directories": directories, "depth": depth}

    def inspect(self, concept_id: str):
        return self.index.get_concept(concept_id)

    def read_section(self, section_id: str):
        return self.index.get_section(section_id)

    def _limit(self, limit: int | None) -> int:
        value = self.config.default_search_limit if limit is None else limit
        if value < 1 or value > self.config.max_search_limit:
            raise OKFError("invalid limit", ErrorCode.INVALID_LIMIT)
        return value
