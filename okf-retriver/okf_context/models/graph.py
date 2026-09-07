from dataclasses import dataclass


@dataclass
class GraphNode:
    concept_id: str
    direction: str
    distance: int


@dataclass
class RetrievalDiagnostic:
    kind: str
    message: str
    path: str | None = None
    recoverable: bool = False


@dataclass(frozen=True)
class CorpusQualityReport:
    documents_indexed: int
    documents_rejected: int
    sections_indexed: int
    links_total: int
    links_valid: int
    links_broken: int
    diagnostics_by_kind: dict[str, int]
    diagnostic_paths: dict[str, list[str]]
    duration_seconds: float

    def to_dict(self) -> dict[str, object]:
        return {
            "documents_indexed": self.documents_indexed,
            "documents_rejected": self.documents_rejected,
            "sections_indexed": self.sections_indexed,
            "links_total": self.links_total,
            "links_valid": self.links_valid,
            "links_broken": self.links_broken,
            "diagnostics_by_kind": dict(sorted(self.diagnostics_by_kind.items())),
            "diagnostic_paths": {key: sorted(set(paths)) for key, paths in sorted(self.diagnostic_paths.items())},
            "duration_seconds": self.duration_seconds,
        }
