"""The copilot pipeline: retrieve, abstain or answer, cite, and check faithfulness."""

from __future__ import annotations

from dataclasses import dataclass, field

from grounded_copilot.data import Passage, knowledge_base
from grounded_copilot.faithfulness import FaithfulnessReport, extract_citations, faithfulness
from grounded_copilot.provider import FakeProvider, Provider
from grounded_copilot.retrieval import TfidfRetriever

_SYSTEM = (
    "You answer only from the numbered context passages. Cite each claim with its passage "
    "number in square brackets, like [1]. If the context does not contain the answer, say you "
    "do not have enough information. Never use outside knowledge."
)
_ABSTENTION = "I do not have enough information in the provided sources to answer that."


@dataclass(frozen=True)
class Answer:
    """A copilot answer with citations, abstention status, and faithfulness."""

    text: str
    abstained: bool
    citations: list[int]
    sources: list[str]
    retrieval_score: float
    faithfulness: FaithfulnessReport


def build_prompt(question: str, passages: list[tuple[int, Passage]]) -> str:
    """Return the prompt embedding the numbered context and the question."""

    lines = [f"[{number}] {passage.text}" for number, passage in passages]
    context = "\n".join(lines)
    return f"Context:\n{context}\n\nQUESTION:{question}<<END>>\nAnswer with citations."


@dataclass
class Copilot:
    """Answers questions grounded in a retrieved context, or abstains."""

    provider: Provider = field(default_factory=FakeProvider)
    passages: list[Passage] = field(default_factory=knowledge_base)
    top_k: int = 3
    abstain_threshold: float = 0.08
    _retriever: TfidfRetriever = field(init=False)

    def __post_init__(self) -> None:
        self._retriever = TfidfRetriever([p.text for p in self.passages])

    def answer(self, question: str) -> Answer:
        """Answer ``question`` from the corpus, or abstain when retrieval is weak."""

        hits = self._retriever.search(question, self.top_k)
        top_score = hits[0][1] if hits else 0.0
        if not hits or top_score < self.abstain_threshold:
            return Answer(
                text=_ABSTENTION,
                abstained=True,
                citations=[],
                sources=[],
                retrieval_score=round(top_score, 4),
                faithfulness=FaithfulnessReport(score=0.0, supported=0, total=0),
            )

        numbered = [(i + 1, self.passages[chunk_id]) for i, (chunk_id, _score) in enumerate(hits)]
        raw = self.provider.complete(_SYSTEM, build_prompt(question, numbered)).strip()
        if not raw:
            return Answer(
                text=_ABSTENTION,
                abstained=True,
                citations=[],
                sources=[],
                retrieval_score=round(top_score, 4),
                faithfulness=FaithfulnessReport(score=0.0, supported=0, total=0),
            )

        citations = extract_citations(raw)
        index_to_passage = dict(numbered)
        cited_passages = [index_to_passage[c].text for c in citations if c in index_to_passage]
        sources = [index_to_passage[c].source for c in citations if c in index_to_passage]
        report = faithfulness(raw, cited_passages)
        return Answer(
            text=raw,
            abstained=False,
            citations=citations,
            sources=sources,
            retrieval_score=round(top_score, 4),
            faithfulness=report,
        )
