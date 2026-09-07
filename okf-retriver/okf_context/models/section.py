from dataclasses import dataclass


@dataclass
class OKFSection:
    section_id: str
    concept_id: str
    path: str
    heading: str
    heading_path: list[str]
    level: int
    content: str
    start_line: int
    end_line: int
    estimated_tokens: int
