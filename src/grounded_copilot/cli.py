"""Command line interface for the grounded copilot."""

from __future__ import annotations

import argparse

from grounded_copilot.copilot import Copilot
from grounded_copilot.evaluation import evaluate


def _cmd_evaluate(_: argparse.Namespace) -> None:
    report = evaluate()
    print("Grounded copilot evaluation:")
    print(f"  {report.format()}")


def _cmd_ask(args: argparse.Namespace) -> None:
    answer = Copilot().answer(args.question)
    if answer.abstained:
        print(f"[abstained, retrieval score {answer.retrieval_score}]")
        print(f"  {answer.text}")
        return
    print(f"answer: {answer.text}")
    print(f"sources: {', '.join(answer.sources) or 'none'}")
    print(
        f"faithfulness: {answer.faithfulness.score:.3f}  retrieval score: {answer.retrieval_score}"
    )


def _cmd_serve(args: argparse.Namespace) -> None:
    from grounded_copilot.service import serve

    serve(host=args.host, port=args.port)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="grounded-copilot", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("evaluate", help="abstention accuracy, faithfulness, and citation coverage")

    ask = sub.add_parser("ask", help="answer a question from the corpus, or abstain")
    ask.add_argument("question")

    serve = sub.add_parser("serve", help="start the HTTP service")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    handlers = {"evaluate": _cmd_evaluate, "ask": _cmd_ask, "serve": _cmd_serve}
    args = parser.parse_args(argv)
    handlers[args.command](args)


if __name__ == "__main__":
    main()
