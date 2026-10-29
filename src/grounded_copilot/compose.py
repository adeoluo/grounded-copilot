"""The offline answer composer used by the fake provider.

Given a prompt that embeds numbered context passages and a question, this picks the
passage most relevant to the question (by token overlap), extracts the sentence
within it that best matches, and returns that sentence followed by the passage's
citation marker. Because the answer is a sentence lifted from a cited passage, it
is faithful to the source by construction, which is what makes the offline
faithfulness measurement meaningful.
"""

from __future__ import annotations

import re

from grounded_copilot.retrieval import tokenize

_CONTEXT_LINE = re.compile(r"^\[(\d+)\]\s*(.*)$")


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _overlap(a: set[str], b: set[str]) -> int:
    return len(a & b)


def compose_from_prompt(prompt: str) -> str:
    """Compose a cited answer from the numbered context embedded in ``prompt``."""

    question = ""
    passages: list[tuple[int, str]] = []
    for line in prompt.splitlines():
        match = _CONTEXT_LINE.match(line.strip())
        if match:
            passages.append((int(match.group(1)), match.group(2)))
        elif line.startswith("QUESTION:"):
            question = line[len("QUESTION:") :].replace("<<END>>", "").strip()

    if not passages or not question:
        return ""

    q_tokens = set(tokenize(question))
    best_citation = 0
    best_sentence = ""
    best_score = -1
    for citation, text in passages:
        for sentence in _split_sentences(text):
            score = _overlap(q_tokens, set(tokenize(sentence)))
            if score > best_score:
                best_score = score
                best_sentence = sentence
                best_citation = citation
    if best_score <= 0:
        return ""
    return f"{best_sentence} [{best_citation}]"
