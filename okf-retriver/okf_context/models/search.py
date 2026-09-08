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


@dataclass(frozen=True)
class ContextSection:
    section_id: str
    concept_id: str
    path: str
    heading_path: tuple[str, ...]
    content: str
    relevance: float
    freshness: str
    verified: bool | None

    def __post_init__(self) -> None:
        if not isinstance(self.heading_path, (list, tuple)) or not all(isinstance(item, str) for item in self.heading_path):
            raise ValueError("heading_path must contain strings")
        object.__setattr__(self, "heading_path", tuple(self.heading_path))


@dataclass
class ContextPackage:
    query: str
    sections: list[ContextSection]
    estimated_tokens: int
    truncated: bool
