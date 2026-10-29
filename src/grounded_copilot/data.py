"""A small knowledge base of passages and a labeled question benchmark.

The corpus is a set of self-contained factual passages, each with a source name.
The benchmark pairs questions with whether they are answerable from the corpus, so
the copilot can be scored on answering grounded questions and abstaining on
out-of-scope ones. Everything is fixed and offline.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Passage:
    """A corpus passage with a citable source name."""

    source: str
    text: str


def knowledge_base() -> list[Passage]:
    """Return the corpus passages."""

    return [
        Passage(
            "solar-system.md",
            "Mercury is the smallest planet in the Solar System and the closest to the Sun. "
            "It has no moons and almost no atmosphere.",
        ),
        Passage(
            "solar-system.md",
            "Jupiter is the largest planet in the Solar System. It is a gas giant with a mass "
            "more than two and a half times that of all the other planets combined.",
        ),
        Passage(
            "solar-system.md",
            "Mars is known as the red planet because iron oxide on its surface gives it a "
            "reddish appearance. It has two small moons, Phobos and Deimos.",
        ),
        Passage(
            "oceans.md",
            "The Pacific Ocean is the largest and deepest of the world's oceans. Its deepest "
            "point, the Challenger Deep, lies in the Mariana Trench.",
        ),
        Passage(
            "oceans.md",
            "The Atlantic Ocean is the second largest ocean and separates the Americas from "
            "Europe and Africa.",
        ),
        Passage(
            "photosynthesis.md",
            "Photosynthesis is the process by which green plants use sunlight to turn carbon "
            "dioxide and water into glucose and oxygen. It takes place in the chloroplasts.",
        ),
        Passage(
            "water.md",
            "Water boils at one hundred degrees Celsius at sea-level atmospheric pressure. The "
            "boiling point decreases at higher altitude as pressure drops.",
        ),
    ]


@dataclass(frozen=True)
class QuestionCase:
    """A question and whether the corpus can answer it."""

    question: str
    answerable: bool


def question_cases() -> list[QuestionCase]:
    """Return the labeled question benchmark."""

    return [
        QuestionCase("What is the largest planet in the Solar System?", True),
        QuestionCase("Why is Mars called the red planet?", True),
        QuestionCase("Which is the smallest planet?", True),
        QuestionCase("What is the deepest ocean?", True),
        QuestionCase("What does photosynthesis produce?", True),
        QuestionCase("At what temperature does water boil at sea level?", True),
        QuestionCase("How many moons does Mars have?", True),
        QuestionCase("Who was the first person to climb Mount Everest?", False),
        QuestionCase("What is the capital of Australia?", False),
        QuestionCase("How does a transformer neural network work?", False),
    ]
