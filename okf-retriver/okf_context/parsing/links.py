import re
import posixpath
from pathlib import PurePosixPath

LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)\s]+)")


def extract_links(text: str, source_path: str) -> list[str]:
    result: list[str] = []
    source = PurePosixPath(source_path)
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:")) or target.startswith("#"):
            continue
        clean = target.split("#", 1)[0]
        if not clean:
            continue
        path = posixpath.normpath((source.parent / clean).as_posix())
        if path.endswith(".md"):
            path = path[:-3]
        result.append(path.lstrip("./"))
    return sorted(set(result))
