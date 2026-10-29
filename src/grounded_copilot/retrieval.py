"""A from-scratch TF-IDF retriever over a corpus of text chunks.

Each chunk is tokenized, term frequencies are weighted by inverse document
frequency, and queries are scored by cosine similarity against the chunk vectors.
This is enough to rank passages by relevance to a question and, crucially, to
produce a top score the copilot can threshold on to decide whether to answer or
abstain. There is no numerical library; vectors are sparse dictionaries.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

_TOKEN = re.compile(r"[a-z0-9]+")

_STOPWORDS = frozenset(
    "the a an of to in on for with at by from as is are was were be been being this that it its "
    "and or but not what which who whom how when where why does do did has have had can could "
    "would should will may might must about into than then".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase and split ``text`` into content tokens, dropping common stop words."""

    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOPWORDS]


@dataclass
class TfidfRetriever:
    """Ranks corpus chunks against a query by TF-IDF cosine similarity."""

    chunks: list[str]
    _idf: dict[str, float] = field(default_factory=dict)
    _vectors: list[dict[str, float]] = field(default_factory=list)
    _norms: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        document_frequency: dict[str, int] = {}
        tokenized = [tokenize(chunk) for chunk in self.chunks]
        for tokens in tokenized:
            for term in set(tokens):
                document_frequency[term] = document_frequency.get(term, 0) + 1
        n = len(self.chunks)
        self._idf = {
            term: math.log((1 + n) / (1 + df)) + 1.0 for term, df in document_frequency.items()
        }
        for tokens in tokenized:
            vector = self._vectorize(tokens)
            self._vectors.append(vector)
            self._norms.append(math.sqrt(sum(w * w for w in vector.values())))

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        counts: dict[str, int] = {}
        for term in tokens:
            counts[term] = counts.get(term, 0) + 1
        total = len(tokens) or 1
        return {
            term: (count / total) * self._idf.get(term, 0.0)
            for term, count in counts.items()
            if self._idf.get(term, 0.0) > 0.0
        }

    def search(self, query: str, k: int = 3) -> list[tuple[int, float]]:
        """Return the top ``k`` ``(chunk_id, cosine_similarity)`` pairs for ``query``."""

        q_vector = self._vectorize(tokenize(query))
        q_norm = math.sqrt(sum(w * w for w in q_vector.values()))
        if q_norm == 0.0:
            return []
        scored: list[tuple[int, float]] = []
        for index, vector in enumerate(self._vectors):
            norm = self._norms[index]
            if norm == 0.0:
                continue
            dot = sum(weight * vector.get(term, 0.0) for term, weight in q_vector.items())
            scored.append((index, dot / (q_norm * norm)))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]
