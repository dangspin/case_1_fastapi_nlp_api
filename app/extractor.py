"""Transparent regular-expression entity extraction rules."""

from __future__ import annotations

import re
from typing import TypedDict


class ExtractedEntities(TypedDict):
    order_id: str | None
    email: str | None
    phone: str | None
    amount: str | None
    date: str | None


ORDER_ID_PATTERN = re.compile(r"\bORD[-\s]?\d{4,}\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)[\s.-]?|\d{2,4}[\s.-])\d{3,4}[\s.-]\d{3,4}(?!\w)"
)
AMOUNT_PATTERN = re.compile(
    r"(?<!\w)(?:[$€£]\s?\d[\d,]*(?:\.\d{2})?|\d[\d,]*(?:\.\d{2})?\s?(?:USD|EUR|GBP))(?!\w)",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(
    r"(?:\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b|"
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)\s+\d{1,2}(?:,\s*|\s+)\d{4}\b)",
    re.IGNORECASE,
)


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(0) if match else None


def extract_entities(text: str) -> ExtractedEntities:
    """Extract the first match for each supported entity type."""

    return {
        "order_id": _first_match(ORDER_ID_PATTERN, text),
        "email": _first_match(EMAIL_PATTERN, text),
        "phone": _first_match(PHONE_PATTERN, text),
        "amount": _first_match(AMOUNT_PATTERN, text),
        "date": _first_match(DATE_PATTERN, text),
    }

