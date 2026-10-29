# ADR-0003: Measure faithfulness per sentence

- **Status:** Accepted
- **Date:** 2026-01-01

## Context
Citations alone do not guarantee that an answer's claims are actually supported by the cited
passages. A model can cite a passage and still assert something it does not say. The copilot needs a
measurable signal of grounding.

## Decision
Compute faithfulness at the sentence level: for each sentence in the answer, check whether its
content words sufficiently overlap one of the passages the answer cites. The faithfulness score is
the fraction of supported sentences, and an answer with no citations scores zero.

## Consequences
- Grounding becomes a number the pipeline reports and tests assert on, not an assumption.
- The check catches blatant hallucination: a test drives a provider that asserts an unsupported claim
  and the score drops below one half.
- Content-word overlap is a proxy for entailment; it is simple and dependency-free but would miss a
  paraphrase that is faithful in meaning yet shares few words, which the documentation notes.
