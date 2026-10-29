# Model / System Card - Grounded Copilot

## Overview
- **What it is:** a retrieval-augmented copilot with inline citations, an abstention guardrail, and a
  faithfulness check, built from scratch. No third-party dependency.
- **Base model:** pluggable. Offline, a composer that answers from the retrieved passages is used for
  tests and CI; in production, Anthropic's Claude via the Messages API.
- **Version and date:** 0.1.0, 2026.

## Intended use
- **Primary use case:** answering questions grounded in a document corpus, with citations and an
  honest abstention when the corpus cannot answer.
- **Primary users:** teams building document assistants that must not fabricate answers.

## Out-of-scope / prohibited use
- Not a general question-answering system; it answers only from its corpus.
- The TF-IDF retriever matches words, not meaning, so paraphrased questions may abstain.

## Performance
- Abstention accuracy 1.000, mean faithfulness 1.000, citation coverage 1.000 on the benchmark.
- Full method and tables: [`EVALUATION_REPORT.md`](EVALUATION_REPORT.md).

## Limitations and failure modes
- Word-overlap faithfulness catches blatant hallucination but is not an entailment model.
- Retrieval can miss a relevant passage phrased differently, causing a false abstention.

## Ethical considerations
- The copilot abstains rather than guessing, which reduces confident misinformation. In production
  the question and retrieved passages are sent to a third-party model; the credentials are read from
  the environment and never logged.
