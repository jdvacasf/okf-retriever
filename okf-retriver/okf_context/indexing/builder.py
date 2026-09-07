import logging
import time
from pathlib import Path

from okf_context.config import OKFContextConfig
from okf_context.indexing.graph import add_relationships
from okf_context.indexing.index import OKFContextIndex
from okf_context.models import CorpusQualityReport, OKFConcept, RetrievalDiagnostic
from okf_context.indexing.lexical import LexicalIndex
from okf_context.parsing.frontmatter import freshness, parse_frontmatter
from okf_context.parsing.links import extract_links
from okf_context.parsing.markdown import estimate_tokens, parse_sections
from okf_context.parsing.paths import safe_resolve_path

logger = logging.getLogger(__name__)


def build_index(config: OKFContextConfig) -> OKFContextIndex:
    started = time.perf_counter()
    root = config.graph_root.expanduser().resolve()
    index = OKFContextIndex()
    index.concept_lexical = LexicalIndex()
    index.section_lexical = LexicalIndex()
    rejected = 0
    if not root.is_dir():
        index.diagnostics.append(RetrievalDiagnostic("PATH_NOT_FOUND", "configured graph root does not exist"))
        index.quality_report = CorpusQualityReport(0, 0, 0, 0, 0, 0, {"PATH_NOT_FOUND": 1}, {"PATH_NOT_FOUND": []}, time.perf_counter() - started)
        index.build_stats = {"documents": 0, "sections": 0, "edges": 0, "diagnostics": 1, "duration_seconds": time.perf_counter() - started, "progress_documents": 0}
        return index
    files = sorted(root.rglob("*.md"))
    for position, file_path in enumerate(files, 1):
        relative = file_path.relative_to(root).as_posix()
        concept_id = relative[:-3]
        try:
            safe_resolve_path(root, relative)
            raw = file_path.read_text(encoding="utf-8")
            metadata, body, diagnostics = parse_frontmatter(raw)
        except Exception as exc:
            index.diagnostics.append(RetrievalDiagnostic("MALFORMED_DOCUMENT", str(exc), relative))
            rejected += 1
            continue
        index.diagnostics.extend(
            RetrievalDiagnostic(item.kind, item.message, relative, item.recoverable) for item in diagnostics
        )
        sections = parse_sections(body, concept_id, relative)
        title = metadata.get("title") or (sections[0].heading if sections else Path(relative).stem)
        metadata_diagnostics = []
        status = metadata.get("status")
        if status is not None and not isinstance(status, str):
            status = None
            metadata_diagnostics.append(RetrievalDiagnostic("INVALID_METADATA", "status must be a string", relative, True))
        tags_value = metadata.get("tags", [])
        if not isinstance(tags_value, list) or not all(isinstance(tag, (str, int, float)) for tag in tags_value):
            tags_value = []
            metadata_diagnostics.append(RetrievalDiagnostic("INVALID_METADATA", "tags must be a list of scalar values", relative, True))
        index.diagnostics.extend(metadata_diagnostics)
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
            tags=[str(tag) for tag in tags_value],
            status=status, stale_after=stale_value,
            verified=metadata.get("verified"), generated=metadata.get("generated"),
            metadata=dict(metadata), section_ids=[section.section_id for section in sections],
            outgoing_links=extract_links(body, relative), estimated_tokens=estimate_tokens(body),
        )
        index.concepts[concept_id] = concept
        index.concept_lexical.add(concept_id, " ".join([concept.title or "", concept.description or "", " ".join(concept.tags), body]))
        for section in sections:
            index.sections[section.section_id] = section
            index.section_lexical.add(section.section_id, " ".join([concept.title or "", " ".join(section.heading_path), " ".join(concept.tags), section.content]))
        _add_metadata_indexes(index, concept)
        logger.info("index progress: %d/%d documents", position, len(files))
    links_total = sum(len(concept.outgoing_links) for concept in index.concepts.values())
    broken_links = 0
    for concept in index.concepts.values():
        missing = [link for link in concept.outgoing_links if link not in index.concepts]
        broken_links += len(missing)
        index.diagnostics.extend(RetrievalDiagnostic("BROKEN_LINK", link, concept.path) for link in missing)
        concept.outgoing_links = [link for link in concept.outgoing_links if link in index.concepts]
        add_relationships(index, concept)
    for target, sources in index.incoming.items():
        if target in index.concepts:
            index.concepts[target].incoming_links = sorted(sources)
    index.ready = True
    by_kind: dict[str, int] = {}
    diagnostic_paths: dict[str, list[str]] = {}
    for diagnostic in index.diagnostics:
        by_kind[diagnostic.kind] = by_kind.get(diagnostic.kind, 0) + 1
        if diagnostic.path:
            diagnostic_paths.setdefault(diagnostic.kind, []).append(diagnostic.path)
    index.quality_report = CorpusQualityReport(
        len(index.concepts), rejected, len(index.sections), links_total,
        links_total - broken_links, broken_links, by_kind, diagnostic_paths,
        time.perf_counter() - started,
    )
    index.build_stats = {
        "documents": len(index.concepts),
        "sections": len(index.sections),
        "edges": sum(map(len, index.outgoing.values())),
        "diagnostics": len(index.diagnostics),
        "duration_seconds": time.perf_counter() - started,
        "progress_documents": len(files),
        **index.quality_report.to_dict(),
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
