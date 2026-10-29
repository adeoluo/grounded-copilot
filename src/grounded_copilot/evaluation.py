"""Evaluation: abstention accuracy, faithfulness, and citation coverage."""

from __future__ import annotations

from dataclasses import dataclass

from grounded_copilot.copilot import Copilot
from grounded_copilot.data import QuestionCase, question_cases


@dataclass(frozen=True)
class CopilotReport:
    """Measured quality of the copilot on the labeled benchmark."""

    abstention_accuracy: float
    answered_correctly: int
    abstained_correctly: int
    total: int
    mean_faithfulness: float
    citation_coverage: float

    def format(self) -> str:
        return (
            f"abstention accuracy={self.abstention_accuracy:.3f} "
            f"({self.answered_correctly + self.abstained_correctly}/{self.total}); "
            f"mean faithfulness={self.mean_faithfulness:.3f}; "
            f"citation coverage={self.citation_coverage:.3f}"
        )


def evaluate(
    copilot: Copilot | None = None, cases: list[QuestionCase] | None = None
) -> CopilotReport:
    """Score abstention, faithfulness, and citation coverage on the benchmark.

    Abstention is correct when the copilot answers an answerable question and
    abstains on an out-of-scope one. Faithfulness and citation coverage are measured
    over the questions it chooses to answer.
    """

    copilot = copilot or Copilot()
    cases = cases or question_cases()
    answered_correctly = 0
    abstained_correctly = 0
    faithfulness_scores: list[float] = []
    answered_with_citation = 0
    answered_total = 0
    for case in cases:
        answer = copilot.answer(case.question)
        if case.answerable and not answer.abstained:
            answered_correctly += 1
        if not case.answerable and answer.abstained:
            abstained_correctly += 1
        if not answer.abstained:
            answered_total += 1
            faithfulness_scores.append(answer.faithfulness.score)
            if answer.citations:
                answered_with_citation += 1
    mean_faithfulness = (
        sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0.0
    )
    citation_coverage = answered_with_citation / answered_total if answered_total else 0.0
    return CopilotReport(
        abstention_accuracy=(answered_correctly + abstained_correctly) / len(cases),
        answered_correctly=answered_correctly,
        abstained_correctly=abstained_correctly,
        total=len(cases),
        mean_faithfulness=mean_faithfulness,
        citation_coverage=citation_coverage,
    )
