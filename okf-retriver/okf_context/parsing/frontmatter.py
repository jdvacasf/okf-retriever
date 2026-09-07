from datetime import date
from typing import Any

import yaml

from okf_context.exceptions import ErrorCode, OKFError


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    if not text.startswith("---\n"):
        return {}, text, []
    end = text.find("\n---", 4)
    if end < 0:
        raise OKFError("frontmatter closing marker is missing", ErrorCode.MALFORMED_FRONTMATTER)
    raw = text[4:end]
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise OKFError(str(exc), ErrorCode.MALFORMED_FRONTMATTER) from exc
    if not isinstance(data, dict):
        raise OKFError("frontmatter must be a mapping", ErrorCode.MALFORMED_FRONTMATTER)
    return data, text[end + 4:].lstrip("\n"), []


def freshness(stale_after: date | str | None) -> str:
    if stale_after is None:
        return "unknown"
    if isinstance(stale_after, str):
        stale_after = date.fromisoformat(stale_after)
    return "stale" if date.today() > stale_after else "current"
