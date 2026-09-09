"""Failure severity categories for a failed SpreadsheetBench task.

The task spec asks us to "Use SpreadsheetBench 2's published failure
taxonomy where it applies rather than inventing categories." A repo pass
over both github.com/RUCKBReasoning/SpreadsheetBench and
github.com/RUCKBReasoning/SpreadsheetBench-2 (see README.md "Dataset
availability") found task *categories* (Debugging / Financial_Model /
Template / Visualization) but no separate, published failure/error taxonomy
in either repo's documentation. The four categories below are therefore the
ones given directly in the task spec itself, not invented here -- if
SpreadsheetBench 2's paper turns out to publish a formal taxonomy, swap
these labels for theirs before a live run rather than keeping this
placeholder.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

WRONG_FORMULA = "wrong_formula"
HARDCODED_VALUE_WHERE_FORMULA_REQUIRED = "hardcoded_value_where_formula_required"
DROPPED_OR_TRUNCATED_ROWS = "dropped_or_truncated_rows"
STRUCTURALLY_BROKEN_OUTPUT = "structurally_broken_output"
CORRECT = "correct"
UNKNOWN_FAILURE = "unknown_failure"

CATEGORIES = [
    WRONG_FORMULA,
    HARDCODED_VALUE_WHERE_FORMULA_REQUIRED,
    DROPPED_OR_TRUNCATED_ROWS,
    STRUCTURALLY_BROKEN_OUTPUT,
]


@dataclass(frozen=True)
class SeverityLabel:
    category: str
    detail: str


def classify_failure(
    passed: bool,
    expected_uses_formula: bool,
    output_has_formula: bool,
    output_row_count: Optional[int],
    expected_row_count: Optional[int],
    output_loaded_ok: bool,
    grader_stdout: str = "",
) -> SeverityLabel:
    """Best-effort heuristic classifier. Requires the caller to have already
    inspected the produced workbook (openpyxl `data_only=False` load lets
    you check whether a cell holds a formula string vs. a literal, per
    `output_has_formula`).
    """
    if not output_loaded_ok:
        return SeverityLabel(STRUCTURALLY_BROKEN_OUTPUT, "output workbook failed to load/parse")

    if passed:
        return SeverityLabel(CORRECT, "passed grader")

    if expected_row_count is not None and output_row_count is not None and output_row_count < expected_row_count:
        return SeverityLabel(
            DROPPED_OR_TRUNCATED_ROWS,
            f"expected >= {expected_row_count} rows, got {output_row_count}",
        )

    if expected_uses_formula and not output_has_formula:
        return SeverityLabel(
            HARDCODED_VALUE_WHERE_FORMULA_REQUIRED,
            "answer key uses a formula; model output uses a literal value",
        )

    if expected_uses_formula and output_has_formula:
        return SeverityLabel(WRONG_FORMULA, "formula present but produces the wrong result")

    return SeverityLabel(UNKNOWN_FAILURE, grader_stdout[:500])
