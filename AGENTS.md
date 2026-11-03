# AGENTS.md

Working notes for coding agents and contributors in **Grounded Copilot**. The [README](README.md)
explains what the project does and why; this file explains how to change it safely.

## Project

A retrieval-augmented copilot that answers only from its sources, with inline citations, an abstention guardrail when retrieval is weak, and a faithfulness check that verifies every claim traces back to a cited passage.

## Layout

- `benchmarks/`: benchmark scripts and recorded results
- `docker-compose.yml`: local container setup
- `docs/`: documentation, architecture diagram source and render, design records
- `src/`: library and service source
- `tests/`: test suite

Key modules:

- `src/grounded_copilot/__init__.py`: Grounded Copilot - retrieval-augmented answers with citations and faithfulness.
- `src/grounded_copilot/cli.py`: Command line interface for the grounded copilot.
- `src/grounded_copilot/compose.py`: The offline answer composer used by the fake provider.
- `src/grounded_copilot/copilot.py`: The copilot pipeline: retrieve, abstain or answer, cite, and check faithfulness.
- `src/grounded_copilot/data.py`: A small knowledge base of passages and a labeled question benchmark.
- `src/grounded_copilot/evaluation.py`: Evaluation: abstention accuracy, faithfulness, and citation coverage.
- `src/grounded_copilot/faithfulness.py`: Faithfulness checking: does every answer sentence trace to a cited source? An answer is faithful when each of its claims is supported by a passage it cites.
- `src/grounded_copilot/observability.py`: In-process request metrics for the HTTP service (Prometheus text exposition).
- `src/grounded_copilot/provider.py`: The language-model provider interface, a deterministic fake, and a real client.
- `src/grounded_copilot/retrieval.py`: A from-scratch TF-IDF retriever over a corpus of text chunks.
- `src/grounded_copilot/service.py`: A standard-library HTTP service exposing the grounded copilot.

## Commands

| Command | Purpose |
|---|---|
| `make help` | Show this help |
| `make setup` | Install dependencies and pre-commit hooks |
| `make format` | Format automatically |
| `make lint` | Lint (no fixes) |
| `make type` | Type-check |
| `make test` | Run tests |
| `make coverage` | Tests with coverage gate |
| `make evaluation` | Reproduce the results table |
| `make run` | Run the HTTP service |
| `make diagram` | Render architecture diagram to SVG |
| `make docker-build` | Build the image |
| `make docker-up` | Run via docker compose |
| `make clean` | Remove caches and artifacts |
| `make all` | Full local gate (mirror of continuous integration) |
| `make changelog` | Regenerate CHANGELOG.md from Conventional Commits (git-cliff) |
| `make cut-release` | Cut a release locally: version bump, changelog, tag, GitHub release (RELEASE_VERSION=vX.Y.Z optional) |

Run the full local gate (`make all`) before committing; CI runs the same checks.

## Conventions

- Commits follow Conventional Commits (`feat:`, `fix:`, `perf:`, `refactor:`, `docs:`, `test:`, `ci:`, `chore:`).
  The changelog and the next version number are derived from them.
- Every number quoted in the README is produced by a command in this repository. When behavior
  changes, rerun that command and update the number in the same commit.
- When a component is added, removed or renamed, update `docs/architecture/architecture.mmd`
  and re-render `architecture.svg` so the diagram matches the code.
- README sections keep their fixed order. Prose avoids em and en dashes and promotional wording.
- Tests accompany behavior changes; a bug fix comes with a test that fails without it.
- Releases are cut with `make cut-release`.

## Python notes

- Python is managed with `uv`; run commands through `uv run` so the locked environment is used.
- Lint and format with `ruff`; type-check with `mypy`; tests use `pytest`.
- Public functions carry type hints and a docstring that states the contract, not the steps.
