from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OKFContextConfig:
    graph_root: Path
    default_search_limit: int = 8
    max_search_limit: int = 20
    default_context_tokens: int = 4000
    max_context_tokens: int = 8000
    max_graph_depth: int = 2
    max_graph_results: int = 30
    snippet_chars: int = 250
    include_drafts: bool = True
    include_deprecated: bool = True

    def __post_init__(self) -> None:
        if self.default_search_limit < 1 or self.default_search_limit > self.max_search_limit:
            raise ValueError("default_search_limit must be within configured limits")
        if self.max_context_tokens < 1 or self.default_context_tokens > self.max_context_tokens:
            raise ValueError("context token limits are invalid")
        if self.max_graph_depth < 0 or self.max_graph_results < 1:
            raise ValueError("graph limits are invalid")
