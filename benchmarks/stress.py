"""A production-style stress benchmark for the copilot service.

Drives the /ask handler under sustained, concurrent load over benchmark questions
and reports throughput with p50, p95, and p99 latency. Deterministic and offline;
run with:

    uv run python benchmarks/stress.py
"""

from __future__ import annotations

import random
import time
from concurrent.futures import ThreadPoolExecutor

from grounded_copilot.data import question_cases
from grounded_copilot.service import CopilotService, handle


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def main() -> None:
    service = CopilotService.with_provider()
    rng = random.Random(0)
    questions = [case.question for case in question_cases()]
    requests = [{"question": rng.choice(questions)} for _ in range(5000)]

    def one(body: dict[str, object]) -> float:
        start = time.perf_counter()
        handle("POST", "/ask", body, service)
        return (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        latencies = list(pool.map(one, requests))
    total_s = time.perf_counter() - start

    print(f"Requests: {len(requests)} | Workers: 8")
    print(f"Throughput: {len(requests) / total_s:.0f} req/sec")
    print(
        "Latency ms  "
        f"p50 {_percentile(latencies, 0.50):.3f}  "
        f"p95 {_percentile(latencies, 0.95):.3f}  "
        f"p99 {_percentile(latencies, 0.99):.3f}"
    )


if __name__ == "__main__":
    main()
