"""Tests for retrieval, faithfulness, the copilot, and evaluation."""

from __future__ import annotations

from grounded_copilot.copilot import Copilot
from grounded_copilot.data import knowledge_base, question_cases
from grounded_copilot.evaluation import evaluate
from grounded_copilot.faithfulness import extract_citations, faithfulness
from grounded_copilot.retrieval import TfidfRetriever, tokenize


def test_tokenize_drops_stopwords() -> None:
    tokens = tokenize("What is the largest planet?")
    assert "largest" in tokens and "planet" in tokens
    assert "the" not in tokens and "what" not in tokens


def test_retriever_ranks_relevant_chunk_first() -> None:
    chunks = [p.text for p in knowledge_base()]
    retriever = TfidfRetriever(chunks)
    hits = retriever.search("largest planet", 3)
    assert hits
    assert "largest planet" in chunks[hits[0][0]].lower()


def test_retriever_scores_zero_for_unrelated_query() -> None:
    retriever = TfidfRetriever([p.text for p in knowledge_base()])
    hits = retriever.search("quantum entanglement cryptography blockchain", 3)
    assert not hits or hits[0][1] == 0.0


def test_extract_citations() -> None:
    assert extract_citations("Jupiter is largest [2]. It is a gas giant [2].") == [2, 2]
    assert extract_citations("no citation here") == []


def test_faithfulness_rewards_supported_and_penalizes_hallucination() -> None:
    passage = ["Jupiter is the largest planet in the Solar System."]
    supported = faithfulness("Jupiter is the largest planet [1].", passage)
    assert supported.score == 1.0
    hallucinated = faithfulness("Saturn has the most moons of any planet [1].", passage)
    assert hallucinated.score < 1.0


def test_faithfulness_zero_without_citation() -> None:
    assert faithfulness("Jupiter is the largest planet.", []).score == 0.0


def test_copilot_answers_with_citation() -> None:
    answer = Copilot().answer("What is the largest planet in the Solar System?")
    assert not answer.abstained
    assert answer.citations
    assert answer.faithfulness.score == 1.0
    assert answer.sources


def test_copilot_abstains_on_out_of_scope() -> None:
    answer = Copilot().answer("What is the capital of Australia?")
    assert answer.abstained
    assert answer.citations == []
    assert "enough information" in answer.text


def test_copilot_catches_hallucinating_provider() -> None:
    class Hallucinator:
        def complete(self, system: str, prompt: str) -> str:
            return "The Moon is made of cheese and orbits Mars twice a day [1]."

    answer = Copilot(provider=Hallucinator()).answer("What is the largest planet?")
    assert not answer.abstained
    assert answer.faithfulness.score < 0.5  # the claim is not supported by the cited passage


def test_evaluation_strong_on_benchmark() -> None:
    report = evaluate()
    assert report.abstention_accuracy == 1.0
    assert report.mean_faithfulness == 1.0
    assert report.citation_coverage == 1.0


def test_benchmark_has_answerable_and_unanswerable() -> None:
    cases = question_cases()
    assert any(c.answerable for c in cases)
    assert any(not c.answerable for c in cases)
