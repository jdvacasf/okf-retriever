import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from .search import ContextSection


@dataclass(frozen=True)
class AnswerRequest:
    question: str
    evidence: tuple[ContextSection, ...]
    instructions: str

    def __post_init__(self) -> None:
        if not isinstance(self.question, str) or not re.search(r"[\wÀ-ÿ]", self.question):
            raise ValueError("question has no searchable tokens")
        if type(self.evidence) is not tuple or not all(isinstance(item, ContextSection) for item in self.evidence):
            raise ValueError("evidence must be a tuple of ContextSection")
        if not self.evidence:
            raise ValueError("evidence must not be empty")
        section_ids = [section.section_id for section in self.evidence]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("evidence section IDs must be unique")
        if not isinstance(self.instructions, str) or not self.instructions.strip():
            raise ValueError("instructions must not be empty")


@dataclass(frozen=True)
class Citation:
    path: str
    section_id: str

    def __post_init__(self) -> None:
        if type(self.path) is not str or not self.path or PurePosixPath(self.path).is_absolute():
            raise ValueError("citation path must be relative")
        if type(self.section_id) is not str or not self.section_id:
            raise ValueError("citation section_id must not be empty")

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "section_id": self.section_id}


@dataclass(frozen=True)
class EvidenceConflict:
    summary: str
    citations: tuple[Citation, ...]

    def __post_init__(self) -> None:
        if type(self.summary) is not str or not self.summary.strip():
            raise ValueError("conflict summary must not be empty")
        if type(self.citations) is not tuple or not all(isinstance(item, Citation) for item in self.citations):
            raise ValueError("conflict citations must be a tuple of Citation")
        section_ids = [citation.section_id for citation in self.citations]
        if len(section_ids) < 2 or len(section_ids) != len(set(section_ids)):
            raise ValueError("conflict requires at least two unique citations")

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "citations": [citation.to_dict() for citation in self.citations],
        }


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    synthesis: str
    citations: tuple[Citation, ...]
    insufficient: bool
    conflicts: tuple[EvidenceConflict, ...]

    def __post_init__(self) -> None:
        if type(self.answer) is not str or type(self.synthesis) is not str:
            raise ValueError("answer and synthesis must be strings")
        if not isinstance(self.insufficient, bool):
            raise ValueError("insufficient must be a boolean")
        if type(self.citations) is not tuple or not all(isinstance(item, Citation) for item in self.citations):
            raise ValueError("citations must be a tuple of Citation")
        if type(self.conflicts) is not tuple or not all(isinstance(item, EvidenceConflict) for item in self.conflicts):
            raise ValueError("conflicts must be a tuple of EvidenceConflict")
        citation_ids = [citation.section_id for citation in self.citations]
        if len(citation_ids) != len(set(citation_ids)):
            raise ValueError("citation section IDs must be unique")
        if self.insufficient and self.answer:
            raise ValueError("insufficient answers must not contain an answer")
        if not self.insufficient and (not self.answer.strip() or not self.citations):
            raise ValueError("supported answers require answer text and citations")

    def to_dict(self) -> dict[str, object]:
        return {
            "answer": self.answer,
            "synthesis": self.synthesis,
            "citations": [citation.to_dict() for citation in self.citations],
            "insufficient": self.insufficient,
            "conflicts": [conflict.to_dict() for conflict in self.conflicts],
        }
