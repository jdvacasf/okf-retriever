import logging
import time
from pathlib import Path

from okf_context.config import OKFContextConfig
from okf_context.indexing.graph import add_relationships
from okf_context.indexing.index import OKFContextIndex
from okf_context.models import OKFConcept, RetrievalDiagnostic
from okf_context.parsing.frontmatter import freshness, parse_frontmatter
from okf_context.parsing.links import extract_links
from okf_context.parsing.markdown import estimate_tokens, parse_sections
from okf_context.parsing.paths import safe_resolve_path

logger = logging.getLogger(__name__)


def build_index(config: OKFContextConfig) -> OKFContextIndex:
    started = time.perf_counter()
    root = config.graph_root.expanduser().resolve()
    index = OKFContextIndex()
    if not root.is_dir():
        index.diagnostics.append(RetrievalDiagnostic("PATH_NOT_FOUND", str(root), str(root)))
        index.build_stats = {"documents": 0, "sections": 0, "edges": 0, "diagnostics": 1, "duration_seconds": time.perf_counter() - started, "progress_documents": 0}
        return index
    files = sorted(root.rglob("*.md"))
    for position, file_path in enumerate(files, 1):
        relative = file_path.relative_to(root).as_posix()
        concept_id = relative[:-3]
        try:
            safe_resolve_path(root, relative)
            raw = file_path.read_text(encoding="utf-8")
            metadata, body, _ = parse_frontmatter(raw)
        except Exception as exc:
            index.diagnostics.append(RetrievalDiagnostic("MALFORMED_DOCUMENT", str(exc), relative))
            continue
        sections = parse_sections(body, concept_id, relative)
        title = metadata.get("title") or (sections[0].heading if sections else Path(relative).stem)
        stale_after = metadata.get("stale_after")
        try:
            stale_value = stale_after if hasattr(stale_after, "year") else stale_after
            freshness(stale_value)
        except (TypeError, ValueError):
            stale_value = None
            index.diagnostics.append(RetrievalDiagnostic("INVALID_FRESHNESS", "invalid stale_after", relative))
        concept = OKFConcept(
            concept_id=concept_id,
            path=relative,
            title=str(title) if title is not None else None,
            description=metadata.get("description"),
            type=metadata.get("type"),
            tags=[str(tag) for tag in metadata.get("tags", [])] if isinstance(metadata.get("tags", []), list) else [],
            status=metadata.get("status"), stale_after=stale_value,
            verified=metadata.get("verified"), generated=metadata.get("generated"),
            metadata=dict(metadata), section_ids=[section.section_id for section in sections],
            outgoing_links=extract_links(body, relative), estimated_tokens=estimate_tokens(body),
        )
        index.concepts[concept_id] = concept
        for section in sections:
            index.sections[section.section_id] = section
        _add_metadata_indexes(index, concept)
        logger.info("index progress: %d/%d documents", position, len(files))
    for concept in index.concepts.values():
        missing = [link for link in concept.outgoing_links if link not in index.concepts]
        index.diagnostics.extend(RetrievalDiagnostic("BROKEN_LINK", link, concept.path) for link in missing)
        concept.outgoing_links = [link for link in concept.outgoing_links if link in index.concepts]
        add_relationships(index, concept)
    for target, sources in index.incoming.items():
        if target in index.concepts:
            index.concepts[target].incoming_links = sorted(sources)
    index.ready = True
    index.build_stats = {
        "documents": len(index.concepts),
        "sections": len(index.sections),
        "edges": sum(map(len, index.outgoing.values())),
        "diagnostics": len(index.diagnostics),
        "duration_seconds": time.perf_counter() - started,
        "progress_documents": len(files),
    }
    logger.info("index built: documents=%d sections=%d edges=%d", len(index.concepts), len(index.sections), sum(map(len, index.outgoing.values())))
    return index


def _add_metadata_indexes(index, concept: OKFConcept) -> None:
    if concept.type:
        index.by_type.setdefault(concept.type, set()).add(concept.concept_id)
    if concept.status:
        index.by_status.setdefault(concept.status, set()).add(concept.concept_id)
    for tag in concept.tags:
        index.by_tag.setdefault(tag, set()).add(concept.concept_id)
