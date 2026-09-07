from dataclasses import dataclass, field

from okf_context.models import OKFConcept, OKFSection, RetrievalDiagnostic


@dataclass
class OKFContextIndex:
    concepts: dict[str, OKFConcept] = field(default_factory=dict)
    sections: dict[str, OKFSection] = field(default_factory=dict)
    by_type: dict[str, set[str]] = field(default_factory=dict)
    by_tag: dict[str, set[str]] = field(default_factory=dict)
    by_status: dict[str, set[str]] = field(default_factory=dict)
    outgoing: dict[str, set[str]] = field(default_factory=dict)
    incoming: dict[str, set[str]] = field(default_factory=dict)
    diagnostics: list[RetrievalDiagnostic] = field(default_factory=list)
    build_stats: dict[str, int | float] = field(default_factory=dict)
    ready: bool = False

    @classmethod
    def build(cls, config):
        from .builder import build_index
        return build_index(config)

    def get_concept(self, concept_id: str) -> OKFConcept:
        from okf_context.exceptions import OKFConceptNotFound
        try:
            return self.concepts[concept_id]
        except KeyError as exc:
            raise OKFConceptNotFound(concept_id) from exc

    def get_section(self, section_id: str) -> OKFSection:
        from okf_context.exceptions import OKFSectionNotFound
        try:
            return self.sections[section_id]
        except KeyError as exc:
            raise OKFSectionNotFound(section_id) from exc
