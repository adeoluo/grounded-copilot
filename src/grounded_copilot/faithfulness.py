"""Faithfulness checking: does every answer sentence trace to a cited source?

An answer is faithful when each of its claims is supported by a passage it cites.
This computes support at the sentence level: a sentence is supported if its content
words sufficiently overlap one of the passages cited in the answer. The faithfulness
score is the fraction of answer sentences that are supported, and an answer with no
citations scores zero. This is the guard against a confident but ungrounded answer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from grounded_copilot.retrieval import tokenize

_CITATION = re.compile(r"\[(\d+)\]")
_STOP = frozenset(
    "the a an of to in on for with at by from as is are was were be this that it its and or".split()
)


def extract_citations(answer: str) -> list[int]:
    """Return the citation indices referenced in ``answer`` (one-based)."""

    return [int(match) for match in _CITATION.findall(answer)]


def _content_words(text: str) -> set[str]:
    return {t for t in tokenize(text) if t not in _STOP}


def _sentences(text: str) -> list[str]:
    stripped = _CITATION.sub("", text)
    parts = re.split(r"(?<=[.!?])\s+", stripped.strip())
    return [p.strip() for p in parts if p.strip()]


@dataclass(frozen=True)
class FaithfulnessReport:
    """The faithfulness score and the count of supported sentences."""

    score: float
    supported: int
    total: int


def faithfulness(
    answer: str, cited_passages: list[str], *, threshold: float = 0.5
) -> FaithfulnessReport:
    """Return the fraction of answer sentences supported by the cited passages.

    A sentence is supported when at least ``threshold`` of its content words appear
    in some cited passage. An answer with no sentences or no citations scores zero.
    """

    sentences = _sentences(answer)
    if not sentences or not cited_passages:
        return FaithfulnessReport(score=0.0, supported=0, total=len(sentences))
    passage_words = [_content_words(passage) for passage in cited_passages]
    supported = 0
    for sentence in sentences:
        words = _content_words(sentence)
        if not words:
            supported += 1
            continue
        best = max((len(words & pw) / len(words) for pw in passage_words), default=0.0)
        if best >= threshold:
            supported += 1
    return FaithfulnessReport(
        score=supported / len(sentences), supported=supported, total=len(sentences)
    )
