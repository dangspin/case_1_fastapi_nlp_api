"""Deterministic priority and keyword rules for the ticket workflow."""

from __future__ import annotations

import re
from collections.abc import Mapping


CONFIDENCE_THRESHOLD = 0.70
MAX_KEYWORDS = 5

HIGH_PRIORITY_PHRASES = (
    "urgent",
    "immediately",
    "blocked",
    "failed",
    "cannot access",
    "payment declined",
    "order has not arrived",
    "not arrived",
)

MEDIUM_PRIORITY_PHRASES = (
    "issue",
    "problem",
    "error",
    "late",
    "missing",
    "refund",
    "charged twice",
    "broken",
)

STOPWORDS = {
    "a",
    "about",
    "after",
    "again",
    "an",
    "and",
    "are",
    "at",
    "be",
    "can",
    "could",
    "for",
    "from",
    "has",
    "have",
    "help",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "the",
    "this",
    "to",
    "was",
    "we",
    "with",
    "you",
    "your",
    "not",
    "contact",
}

TOKEN_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z'-]{2,}\b")


def _contains_phrase(text: str, phrase: str) -> bool:
    pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def detect_priority(text: str) -> str:
    """Apply high-over-medium-over-low priority rules."""

    if any(_contains_phrase(text, phrase) for phrase in HIGH_PRIORITY_PHRASES):
        return "high"
    if any(_contains_phrase(text, phrase) for phrase in MEDIUM_PRIORITY_PHRASES):
        return "medium"
    return "low"


def needs_review(confidence: float, threshold: float = CONFIDENCE_THRESHOLD) -> bool:
    """Return whether the classifier confidence is below the review threshold."""

    return float(confidence) < float(threshold)


def extract_keywords(
    text: str,
    entities: Mapping[str, str | None] | None = None,
    limit: int = MAX_KEYWORDS,
) -> list[str]:
    """Select up to five useful tokens in their original message order."""

    masked_text = text
    for value in (entities or {}).values():
        if value:
            masked_text = masked_text.replace(value, " ")

    selected: list[str] = []
    for token in TOKEN_PATTERN.findall(masked_text.lower()):
        normalized = token.strip("'-")
        if len(normalized) < 3 or normalized in STOPWORDS or normalized in selected:
            continue
        selected.append(normalized)
        if len(selected) >= limit:
            break
    return selected

