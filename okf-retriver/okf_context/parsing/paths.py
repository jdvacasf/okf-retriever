from pathlib import Path

from okf_context.exceptions import OKFPathNotFound, OKFSandboxViolation


def safe_resolve_path(graph_root: Path, relative_path: str, *, must_exist: bool = True) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise OKFSandboxViolation("absolute paths are not allowed")
    root = graph_root.expanduser().resolve()
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise OKFSandboxViolation("path escapes graph_root")
    if must_exist and not resolved.exists():
        raise OKFPathNotFound(str(relative_path))
    return resolved
