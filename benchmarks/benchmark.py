"""A deterministic micro-benchmark for the grounded copilot.

Reports abstention accuracy, mean faithfulness, and citation coverage on the
labeled question benchmark. Deterministic and offline; run with:

    uv run python benchmarks/benchmark.py
"""

from __future__ import annotations

import time

from grounded_copilot.evaluation import evaluate


def main() -> None:
    start = time.perf_counter()
    report = evaluate()
    elapsed = (time.perf_counter() - start) * 1000
    print(f"Grounded copilot benchmark ({report.total} questions, {elapsed:.0f} ms):")
    print(f"  {report.format()}")


if __name__ == "__main__":
    main()
