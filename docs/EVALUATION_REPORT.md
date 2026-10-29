# Evaluation Report - Grounded Copilot

> Reproduce with `python -m grounded_copilot evaluate` and `benchmarks/benchmark.py`. The corpus,
> retriever, and offline composer are deterministic.

## Setup

- **Corpus:** seven factual passages across a few topics, each with a source name.
- **Benchmark:** ten questions, each labeled answerable from the corpus or out of scope.
- **Provider:** the offline composer that answers strictly from the retrieved passages, so results
  are reproducible with no credentials.
- **Metrics:** abstention accuracy (answer the answerable, abstain on the out-of-scope), mean
  faithfulness over answered questions, and citation coverage.
- **Hardware / cost:** CPU only; the benchmark runs in a few milliseconds. No external services.

## Results

| Metric | Value |
|---|---:|
| abstention accuracy | 1.000 (10/10) |
| mean faithfulness | 1.000 |
| citation coverage | 1.000 |

The copilot answers all seven answerable questions and abstains on all three out-of-scope ones; every
answer is fully supported by its citations, and every answer carries a citation. Out-of-scope
questions retrieve with a top score of zero after stop-word filtering, which is why the abstention
gate separates them cleanly.

## The faithfulness check catches hallucination

Faithfulness is not always one by construction. A test drives a deliberately hallucinating provider
that cites a passage but asserts an unsupported claim; the faithfulness score for that answer falls
below one half. This is the signal that would flag a production model straying from its sources.

## Retrieval behavior

TF-IDF cosine similarity with stop-word filtering ranks the relevant passage first for answerable
questions (top scores from about 0.26 to 0.54 on the benchmark) and scores unrelated questions at
zero, which drives the abstention gate.

## Service performance

The `/ask` handler retrieves, composes, and checks faithfulness per request; with the offline
provider a concurrent stress benchmark sustains about 4,100 requests per second with p50 near
0.16 ms. In production the latency is dominated by the model call.

## Reproducibility

- Deterministic: the corpus, retriever, and offline composer produce identical results every run.
- No network access, no credentials, no external data in CI.
- Regenerate every number with the CLI and `benchmarks/benchmark.py`.
