from dataclasses import dataclass, field


@dataclass
class SearchResult:
    concept_id: str
    path: str
    score: float
    section_id: str | None = None
    title: str | None = None
    heading: str | None = None
    matched_terms: list[str] = field(default_factory=list)
    snippet: str | None = None
    freshness: str = "unknown"
    verified: bool | None = None
    status: str | None = None
    score_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass
class ContextSection:
    section_id: str
    concept_id: str
    path: str
    heading_path: list[str]
    content: str
    relevance: float
    freshness: str
    verified: bool | None


@dataclass
class ContextPackage:
    query: str
    sections: list[ContextSection]
    estimated_tokens: int
    truncated: bool
