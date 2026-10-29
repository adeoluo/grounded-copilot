# Threat Model - Grounded Copilot

## Assets
- The HTTP service's availability and the integrity of its answers, and any credentials used by a
  production provider.

## Trust boundaries
- The user's question is untrusted. The retriever and corpus are in-process and trusted. In
  production the question and retrieved passages are sent to a third-party model over HTTPS.

## Entry points and mitigations

### `POST /ask`
- **Malformed JSON** is rejected with 400 before routing.
- **Validation:** the question must be a non-empty string within a size bound.
- **Grounding:** the copilot answers only from retrieved passages, abstains when retrieval is weak,
  and the faithfulness check flags answers not supported by their citations.

### `GET` routes
- `/health`, `/ready`, `/evaluate`, and `/metrics` take no user input and return fixed-shape
  payloads. `/metrics` exposes only aggregate counters.

## Provider and credentials
- The offline composer needs no secrets. The Anthropic provider reads its key from the environment,
  never from the request, and never logs it. CI uses only the offline composer.

## Data handling
- The corpus is the only knowledge source; the copilot does not use outside knowledge, and it abstains
  rather than guessing, which limits fabricated answers.

## Supply chain
- Zero third-party runtime dependencies; the production provider uses the standard-library HTTP
  client. Development tooling is pinned via `uv.lock`. CodeQL and dependency scanning run in CI.

## Residual risk
- A retrieval miss can cause a false abstention, and word-overlap faithfulness can be fooled by a
  faithful paraphrase; a deployment would add an embedding retriever and an entailment check.
