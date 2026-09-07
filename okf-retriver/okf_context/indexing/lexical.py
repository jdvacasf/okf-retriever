import math
import re
from collections import Counter

TOKEN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


def normalize(text: str) -> list[str]:
    return TOKEN.findall(text.casefold())


class LexicalIndex:
    def __init__(self) -> None:
        self.documents: dict[str, list[str]] = {}
        self.term_documents: dict[str, set[str]] = {}

    def add(self, key: str, text: str) -> None:
        tokens = normalize(text)
        self.documents[key] = tokens
        for token in set(tokens):
            self.term_documents.setdefault(token, set()).add(key)

    def search(self, query: str, limit: int) -> list[tuple[str, float, list[str]]]:
        query_tokens = normalize(query)
        if not query_tokens:
            return []
        total = max(1, len(self.documents))
        average = sum(map(len, self.documents.values())) / total
        results: list[tuple[str, float, list[str]]] = []
        for key, tokens in self.documents.items():
            counts = Counter(tokens)
            score = 0.0
            matched: list[str] = []
            for term in query_tokens:
                if term not in counts:
                    continue
                matched.append(term)
                doc_count = len(self.term_documents.get(term, ()))
                idf = math.log(1 + (total - doc_count + 0.5) / (doc_count + 0.5))
                tf = counts[term]
                length = len(tokens) or 1
                score += idf * (tf * 2.2) / (tf + 1.2 * (0.75 + 0.25 * length / max(1, average)))
            if score:
                results.append((key, score, sorted(set(matched))))
        return sorted(results, key=lambda item: (-item[1], item[0]))[:limit]
