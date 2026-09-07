import re

from okf_context.models import OKFSection

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def parse_sections(text: str, concept_id: str, path: str) -> list[OKFSection]:
    lines = text.splitlines()
    headings = [(i, len(match.group(1)), match.group(2)) for i, line in enumerate(lines) if (match := HEADING.match(line))]
    sections: list[OKFSection] = []
    used: dict[str, int] = {}
    for position, (start, level, heading) in enumerate(headings):
        end = len(lines)
        for next_start, next_level, _ in headings[position + 1:]:
            if next_level <= level:
                end = next_start
                break
        ancestors = [item[2] for item in headings[: position + 1] if item[1] < level]
        ancestors.append(heading)
        slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-") or "section"
        used[slug] = used.get(slug, 0) + 1
        suffix = f"-{used[slug]}" if used[slug] > 1 else ""
        content = "\n".join(lines[start + 1:end]).strip()
        sections.append(OKFSection(f"{concept_id}#{slug}{suffix}", concept_id, path, heading, ancestors, level, content, start + 1, end, estimate_tokens(content)))
    return sections


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split())) if text.strip() else 0
