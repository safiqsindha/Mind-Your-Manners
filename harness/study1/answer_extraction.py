"""Extract a single multiple-choice letter answer from a model's raw text.

Three possible outcomes, all distinct (per task spec: "Log any refusals
separately as their own outcome; do not score them as wrong answers"):
  * a letter is extracted -> scored correct/incorrect against the key
  * the response is a refusal (provider-flagged, or refusal-shaped text)
    -> outcome="refused", excluded from the accuracy denominator
  * no letter could be extracted and it isn't a refusal -> outcome="unparseable",
    also excluded from the accuracy denominator but logged and reported
    separately so it doesn't get silently absorbed into "wrong"
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

_REFUSAL_PATTERNS = [
    r"\bI (?:can't|cannot|won't|will not) (?:help|assist|continue|answer)\b",
    r"\bI'm not (?:going to|able to) (?:continue|help|assist)\b",
    r"\bnot going to continue\b",
    r"\bI'd rather not\b",
]
_REFUSAL_RE = re.compile("|".join(_REFUSAL_PATTERNS), re.IGNORECASE)

# Matches "(C)", "C)", "C.", "C:", "answer is C", "**C**", or a bare trailing letter.
_LETTER_PATTERNS = [
    re.compile(r"answer\s*(?:is|:)?\s*\(?([A-J])\)?", re.IGNORECASE),
    re.compile(r"^\**\(?([A-J])\)?\**[.:)]?\s*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\(([A-J])\)"),
]


@dataclass(frozen=True)
class ExtractionResult:
    outcome: str  # "answered" | "refused" | "unparseable"
    letter: Optional[str]
    is_correct: Optional[bool]


def extract_answer(response_text: str, correct_letter: str, provider_flagged_refusal: bool) -> ExtractionResult:
    if provider_flagged_refusal or (response_text and _REFUSAL_RE.search(response_text)):
        return ExtractionResult(outcome="refused", letter=None, is_correct=None)

    text = (response_text or "").strip()
    if not text:
        return ExtractionResult(outcome="unparseable", letter=None, is_correct=None)

    for pattern in _LETTER_PATTERNS:
        m = pattern.search(text)
        if m:
            letter = m.group(1).upper()
            return ExtractionResult(
                outcome="answered",
                letter=letter,
                is_correct=(letter == correct_letter.upper()),
            )

    return ExtractionResult(outcome="unparseable", letter=None, is_correct=None)
