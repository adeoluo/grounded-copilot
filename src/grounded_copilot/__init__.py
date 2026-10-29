"""Grounded Copilot - retrieval-augmented answers with citations and faithfulness."""

from __future__ import annotations

from grounded_copilot.copilot import Answer, Copilot, build_prompt
from grounded_copilot.data import Passage, QuestionCase, knowledge_base, question_cases
from grounded_copilot.evaluation import CopilotReport, evaluate
from grounded_copilot.faithfulness import FaithfulnessReport, extract_citations, faithfulness
from grounded_copilot.provider import AnthropicProvider, FakeProvider, Provider
from grounded_copilot.retrieval import TfidfRetriever, tokenize

__version__ = "0.1.0"

__all__ = [
    "Answer",
    "AnthropicProvider",
    "Copilot",
    "CopilotReport",
    "FaithfulnessReport",
    "FakeProvider",
    "Passage",
    "Provider",
    "QuestionCase",
    "TfidfRetriever",
    "__version__",
    "build_prompt",
    "evaluate",
    "extract_citations",
    "faithfulness",
    "knowledge_base",
    "question_cases",
    "tokenize",
]
