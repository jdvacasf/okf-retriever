from okf_context.indexing.lexical import normalize


FIELD_WEIGHTS = {"title": 4.0, "description": 3.0, "tags": 3.0, "heading": 2.0, "body": 1.0}


def score_fields(query: str, fields: dict[str, str]) -> tuple[float, list[str], dict[str, float]]:
    terms = set(normalize(query))
    matched: set[str] = set()
    breakdown: dict[str, float] = {}
    for name, text in fields.items():
        hits = terms.intersection(normalize(text))
        if hits:
            value = FIELD_WEIGHTS.get(name, 1.0) * len(hits)
            breakdown[name] = value
            matched.update(hits)
    return sum(breakdown.values()), sorted(matched), breakdown
