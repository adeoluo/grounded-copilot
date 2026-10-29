# ADR-0002: Abstain when retrieval is weak

- **Status:** Accepted
- **Date:** 2026-01-01

## Context
A retrieval-augmented copilot should not answer a question its corpus cannot support. Without a
guard, the model is prompted with whatever passages retrieval returns, even irrelevant ones, and may
produce a confident but ungrounded answer.

## Decision
Gate answering on the retrieval score. After ranking passages by TF-IDF cosine similarity, if the
top score is below a threshold the copilot abstains with an explicit message rather than calling the
model. Stop-word filtering keeps the score driven by content words, so unrelated questions score near
zero and are abstained.

## Consequences
- Out-of-scope questions are declined rather than answered incorrectly, which the benchmark measures
  as abstention accuracy.
- The threshold is a tunable operating point; too high abstains on answerable questions, too low
  answers out-of-scope ones. The default separates the benchmark cleanly.
- Abstention depends on retrieval quality; a better retriever would reduce false abstentions on
  paraphrased questions.
