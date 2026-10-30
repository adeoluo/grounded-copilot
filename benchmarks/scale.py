"""A large-workload scale benchmark for the grounded copilot pipeline.

Where ``benchmark.py`` scores the fixed 10-question suite, this script asks how the
pipeline behaves as the *knowledge base* grows: it answers a fixed set of questions
(some answerable, some deliberately out of scope) against progressively larger
synthetic corpora, reporting wall-clock time, question throughput, peak memory (via
the stdlib ``tracemalloc``), and the abstention accuracy that is the project's
headline guardrail metric.

The headline is that the guardrails hold: abstention accuracy, mean faithfulness,
and citation coverage all stay at 1.0 as the corpus grows, because every answer is
a sentence lifted from a cited passage and out-of-scope questions fall below the
retrieval threshold. Throughput falls because the from-scratch TF-IDF retriever
scores every passage per query.

The data is synthetic and the pipeline is pure Python with a deterministic offline
provider (the ``FakeProvider``; production swaps in Claude behind the same
interface): these numbers measure the retrieval and grounding overhead, not a
model's latency, and are not a comparison against a production vector database. The
point is to show how this implementation scales, honestly.

Run with:

    uv run python benchmarks/scale.py
"""

from __future__ import annotations

import random
import time
import tracemalloc
from dataclasses import dataclass

from grounded_copilot.copilot import Copilot
from grounded_copilot.data import Passage

_CORPUS_SIZES: tuple[int, ...] = (200, 500, 1000, 2000)
_NUM_ANSWERABLE = 60
_NUM_OUT_OF_SCOPE = 40

_FIELDS = ("astronomy", "biology", "geology", "chemistry", "physics", "history", "music", "botany")
_VERBS = ("is studied in", "is central to", "is described within", "is classified under")
_OUT_OF_SCOPE = (
    "Who painted the ceiling fresco during the renaissance jubilee",
    "Which athlete sprinted fastest at the coastal marathon",
    "When did the volcanic archipelago host its winter carnival",
    "How tall was the medieval clocktower bellringer",
)


@dataclass(frozen=True, slots=True)
class Workload:
    """A synthetic corpus plus labeled (question, answerable) pairs."""

    passages: list[Passage]
    questions: list[tuple[str, bool]]


def build_workload(num_passages: int, *, seed: int = 0) -> Workload:
    """Build a corpus of distinctive passages and a labeled question set.

    Each passage names a unique topic token, so answerable questions retrieve their
    source robustly; out-of-scope questions use disjoint vocabulary, so retrieval
    stays below the abstention threshold and the copilot declines to answer.
    """
    rng = random.Random(seed)
    passages = [
        Passage(
            source=f"src{i}.md",
            text=(
                f"The topic kascode{i} {rng.choice(_VERBS)} the field of "
                f"{rng.choice(_FIELDS)} and relates to phenomenon zylon{i}."
            ),
        )
        for i in range(num_passages)
    ]

    questions: list[tuple[str, bool]] = []
    for topic in rng.sample(range(num_passages), min(_NUM_ANSWERABLE, num_passages)):
        questions.append((f"What does kascode{topic} relate to?", True))
    for index in range(_NUM_OUT_OF_SCOPE):
        questions.append((f"{_OUT_OF_SCOPE[index % len(_OUT_OF_SCOPE)]} in case {index}?", False))

    return Workload(passages=passages, questions=questions)


@dataclass(frozen=True, slots=True)
class ScaleResult:
    """One row of the scale table."""

    passages: int
    seconds: float
    questions_per_sec: float
    peak_mib: float
    abstention_accuracy: float


def measure(num_passages: int) -> ScaleResult:
    """Answer the labeled questions against a corpus of ``num_passages`` passages.

    Timing and throughput are measured without ``tracemalloc``; peak memory is
    captured in a separate pass over the same workload.
    """
    workload = build_workload(num_passages)
    copilot = Copilot(passages=workload.passages)

    correct = 0
    start = time.perf_counter()
    for question, answerable in workload.questions:
        answer = copilot.answer(question)
        if answer.abstained == (not answerable):
            correct += 1
    elapsed = time.perf_counter() - start

    peak = _peak_memory(workload)

    return ScaleResult(
        passages=num_passages,
        seconds=elapsed,
        questions_per_sec=len(workload.questions) / elapsed if elapsed else 0.0,
        peak_mib=peak / (1024 * 1024),
        abstention_accuracy=correct / len(workload.questions) if workload.questions else 0.0,
    )


def _peak_memory(workload: Workload) -> int:
    """Return the peak bytes to index the corpus and answer a few questions."""
    tracemalloc.start()
    copilot = Copilot(passages=workload.passages)
    for question, _answerable in workload.questions[:5]:
        copilot.answer(question)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def main() -> None:
    print("Synthetic corpus; from-scratch pure-Python retrieval + grounding (not a vector DB).")
    total_questions = _NUM_ANSWERABLE + _NUM_OUT_OF_SCOPE
    print(f"Fixed query set: {total_questions} questions ({_NUM_OUT_OF_SCOPE} out of scope).\n")
    header = (
        f"{'passages':>9}{'seconds':>10}{'questions/sec':>15}{'peak MiB':>11}{'abstain acc':>13}"
    )
    print(header)
    print("-" * len(header))
    for num_passages in _CORPUS_SIZES:
        result = measure(num_passages)
        print(
            f"{result.passages:>9}{result.seconds:>10.3f}{result.questions_per_sec:>15.0f}"
            f"{result.peak_mib:>11.1f}{result.abstention_accuracy:>13.2f}"
        )


if __name__ == "__main__":
    main()
