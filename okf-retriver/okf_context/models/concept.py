from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class OKFConcept:
    concept_id: str
    path: str
    title: str | None = None
    description: str | None = None
    type: str | None = None
    tags: list[str] = field(default_factory=list)
    status: str | None = None
    stale_after: date | None = None
    verified: bool | None = None
    generated: bool | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    section_ids: list[str] = field(default_factory=list)
    outgoing_links: list[str] = field(default_factory=list)
    incoming_links: list[str] = field(default_factory=list)
    estimated_tokens: int = 0
