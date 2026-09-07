from datetime import date
import re
from typing import Any

import yaml

from okf_context.exceptions import ErrorCode, OKFError
from okf_context.models import RetrievalDiagnostic


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[RetrievalDiagnostic]]:
    if not text.startswith("---\n"):
        return {}, text, []
    lines = text.splitlines(keepends=True)
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        heading = next((i for i, line in enumerate(lines[1:], 1) if re.match(r"^#{1,6}\s+", line)), None)
        if heading is None:
            raise OKFError("frontmatter closing marker is missing and no heading boundary exists", ErrorCode.MALFORMED_FRONTMATTER)
        return {}, "".join(lines[heading:]), [RetrievalDiagnostic("MISSING_FRONTMATTER_DELIMITER", "closing marker is missing; recovered from first heading", recoverable=True)]
    raw = "".join(lines[1:end])
    body = "".join(lines[end + 1:]).lstrip("\n")
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return {}, body, [RetrievalDiagnostic("MALFORMED_FRONTMATTER", str(exc), recoverable=True)]
    if not isinstance(data, dict):
        return {}, body, [RetrievalDiagnostic("MALFORMED_FRONTMATTER", "frontmatter must be a mapping", recoverable=True)]
    return data, body, []


def freshness(stale_after: date | str | None) -> str:
    if stale_after is None:
        return "unknown"
    if isinstance(stale_after, str):
        stale_after = date.fromisoformat(stale_after)
    return "stale" if date.today() > stale_after else "current"
