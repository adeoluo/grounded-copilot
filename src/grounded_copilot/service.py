"""A dependency-free HTTP service exposing the grounded copilot.

The service answers questions from the built-in corpus, abstaining when retrieval
is weak, and reports its benchmark scores. By default it uses the offline composer,
so it runs with no credentials; a real provider can be injected in production. The
routing logic is a pure function tested without a socket.

Endpoints
---------
``GET  /health``   liveness, the active provider, and the corpus size.
``GET  /ready``    readiness.
``GET  /metrics``  per-route request, error, and latency metrics (Prometheus text).
``POST /ask``      body ``{"question": str}``; a grounded answer with citations or an abstention.
``GET  /evaluate`` abstention accuracy, faithfulness, and citation coverage on the benchmark.
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from grounded_copilot.copilot import Copilot
from grounded_copilot.evaluation import evaluate
from grounded_copilot.observability import ServiceMetrics
from grounded_copilot.provider import FakeProvider, Provider

JsonObject = dict[str, Any]
_MAX_QUESTION = 2000


@dataclass(frozen=True)
class CopilotService:
    """Holds a copilot and answers question and evaluation requests."""

    copilot: Copilot
    provider_name: str
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)

    @classmethod
    def with_provider(cls, provider: Provider | None = None) -> CopilotService:
        provider = provider or FakeProvider()
        return cls(copilot=Copilot(provider=provider), provider_name=type(provider).__name__)

    def ask(self, question: str) -> JsonObject:
        answer = self.copilot.answer(question)
        return {
            "text": answer.text,
            "abstained": answer.abstained,
            "citations": answer.citations,
            "sources": answer.sources,
            "retrieval_score": answer.retrieval_score,
            "faithfulness": round(answer.faithfulness.score, 6),
        }

    def evaluate(self) -> JsonObject:
        report = evaluate(self.copilot)
        return {
            "abstention_accuracy": round(report.abstention_accuracy, 6),
            "mean_faithfulness": round(report.mean_faithfulness, 6),
            "citation_coverage": round(report.citation_coverage, 6),
            "total": report.total,
        }


def _route(
    method: str, path: str, body: Mapping[str, Any], service: CopilotService
) -> tuple[int, JsonObject]:
    if method == "GET" and path == "/health":
        return 200, {
            "status": "ok",
            "provider": service.provider_name,
            "passages": len(service.copilot.passages),
        }
    if method == "GET" and path == "/evaluate":
        return 200, service.evaluate()
    if method == "POST" and path == "/ask":
        question = body.get("question")
        if not isinstance(question, str) or not question or len(question) > _MAX_QUESTION:
            return 400, {
                "error": (
                    f"'question' must be a non-empty string of at most {_MAX_QUESTION} characters"
                )
            }
        return 200, service.ask(question)
    return 404, {"error": f"no route for {method} {path}"}


def handle(
    method: str, path: str, body: Mapping[str, Any], service: CopilotService
) -> tuple[int, JsonObject]:
    """Route a request, recording per-route metrics, and return status and payload."""

    if method == "GET" and path == "/ready":
        return 200, {"status": "ready"}
    start = time.perf_counter()
    status, payload = _route(method, path, body, service)
    service.metrics.observe(
        f"{method} {path}", (time.perf_counter() - start) * 1000.0, error=status >= 400
    )
    return status, payload


class _Handler(BaseHTTPRequestHandler):  # pragma: no cover - exercised over sockets
    service: CopilotService

    def _respond(self, status: int, payload: JsonObject) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path == "/metrics":
            body = self.service.metrics.render_prometheus().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        status, payload = handle("GET", self.path, {}, self.service)
        self._respond(status, payload)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._respond(400, {"error": "request body is not valid JSON"})
            return
        status, payload = handle("POST", self.path, body, self.service)
        self._respond(status, payload)

    def log_message(self, *_: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:  # pragma: no cover
    """Start the HTTP service (blocking)."""

    handler = type("_BoundHandler", (_Handler,), {"service": CopilotService.with_provider()})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"grounded-copilot service listening on http://{host}:{port}")
    server.serve_forever()
