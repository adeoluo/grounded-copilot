"""Tests for the HTTP service routing and the CLI."""

from __future__ import annotations

from grounded_copilot.cli import main
from grounded_copilot.service import CopilotService, handle

_SERVICE = CopilotService.with_provider()


def test_health_and_ready() -> None:
    status, payload = handle("GET", "/health", {}, _SERVICE)
    assert status == 200 and payload["provider"] == "FakeProvider"
    assert payload["passages"] > 0
    status, payload = handle("GET", "/ready", {}, _SERVICE)
    assert status == 200 and payload["status"] == "ready"


def test_ask_answerable() -> None:
    status, payload = handle("POST", "/ask", {"question": "What is the deepest ocean?"}, _SERVICE)
    assert status == 200
    assert payload["abstained"] is False
    assert payload["citations"]
    assert payload["faithfulness"] == 1.0


def test_ask_abstains() -> None:
    status, payload = handle(
        "POST", "/ask", {"question": "What is the chemical symbol for gold?"}, _SERVICE
    )
    assert status == 200
    assert payload["abstained"] is True
    assert payload["citations"] == []


def test_ask_validation() -> None:
    status, _ = handle("POST", "/ask", {"question": ""}, _SERVICE)
    assert status == 400
    status, _ = handle("POST", "/ask", {"question": 5}, _SERVICE)
    assert status == 400


def test_evaluate_route() -> None:
    status, payload = handle("GET", "/evaluate", {}, _SERVICE)
    assert status == 200
    assert payload["abstention_accuracy"] == 1.0
    assert payload["mean_faithfulness"] == 1.0


def test_unknown_route_and_metrics() -> None:
    status, _ = handle("GET", "/nope", {}, _SERVICE)
    assert status == 404
    handle("POST", "/ask", {"question": "What is the largest planet?"}, _SERVICE)
    assert "service_requests_total" in _SERVICE.metrics.render_prometheus()


def test_cli_commands(capsys) -> None:  # type: ignore[no-untyped-def]
    main(["evaluate"])
    main(["ask", "Why is Mars called the red planet?"])
    main(["ask", "What is the capital of France?"])
    out = capsys.readouterr().out
    assert "abstention accuracy" in out
    assert "answer:" in out
    assert "abstained" in out
