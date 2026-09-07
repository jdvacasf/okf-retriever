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
