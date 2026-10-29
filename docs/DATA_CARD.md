# Data Card - Grounded Copilot

## Source
- **Authored in-repository.** The corpus passages and the question benchmark are written for this
  project. There is no external dataset, download, or network access.

## Composition
- Seven factual passages across a few topics (the Solar System, oceans, photosynthesis, water), each
  with a source name used for citations.
- A benchmark of ten questions, seven answerable from the corpus and three out of scope.

## Labels and supervision
- The labels are the answerable flag per question, used to score abstention accuracy. There is no
  training.

## Provenance and licensing
- Authored for this repository under the MIT license. The facts are common-knowledge statements.

## Filtering and contamination
- Not applicable: the corpus and benchmark are fixed and used only for evaluation.

## Known limitations
- The corpus is small and clean by design so the benchmark is a clear, deterministic guard; it does
  not represent a large, noisy document set.
