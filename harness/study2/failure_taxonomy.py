"""Failure severity categories for a failed SpreadsheetBench task.

Roadmap requirement: "Failure severity using SpreadsheetBench 2's
published taxonomy -- their claim, cited, not yours to invent." An
earlier version of this module checked only
`github.com/RUCKBReasoning/SpreadsheetBench-2`'s repo docs, found no
formal taxonomy there, and used four placeholder categories instead. That
was checking the wrong artifact: the paper itself, arXiv 2606.29955
("SpreadsheetBench 2: Evaluating Agents on End-to-End Business
Spreadsheet Workflows"), publishes two taxonomies, fetched and read
directly (not guessed) before rewriting this module:

  Table 6 -- ten error types specific to their Debugging task category
  (Double Counting, Embedded Hardcodes, Errors, Inconsistent Color,
  Incorrect Average, Cross-Sheet References, Incorrect Index-Match,
  Incorrect Sign, Relative vs. Absolute References, Unit Mismatch). Not
  used here: this describes errors *seeded into* a debugging task for the
  agent to find, and Study 2's substrate is the original SpreadsheetBench
  (v1, generation-style tasks), not SpreadsheetBench 2's debugging split.

  Table 7, the one actually used below -- six failure MODES reported
  across all their task types (their own trajectory analysis, not
  task-content-specific):

    Task Misunderstanding    -- "the agent misinterprets the user's
                                 instructions and pursues an entirely
                                 incorrect objective"
    Insufficient Inspection  -- "the agent fails to sufficiently explore
                                 the spreadsheet prior to making edits"
    Wrong Target Selection   -- "the agent correctly identifies the
                                 required action but applies it to the
                                 incorrect cells or worksheets"
    Turn Limit Exceeded      -- "the agent fails to complete the task
                                 before exceeding the maximum permitted
                                 number of dialogue turns"
    Format/Output Error      -- "the agent derives the correct values but
                                 applies an incorrect format"
    Other                    -- "there was some other problem that
                                 prevented the agent from resolving this
                                 issue"

  Their own reported finding: Insufficient Inspection and Wrong Target
  Selection were the dominant failure modes across the models they
  tested.

HONEST COVERAGE NOTE: this is a heuristic classifier over signals this
harness can actually observe (did the agent inspect the sheet, did it hit
the turn limit, did its output load, does it look like a right-value/
wrong-format case) -- it is not a semantic judge. `Task Misunderstanding`
and `Wrong Target Selection` in particular require understanding intent
and cell-level diffs this classifier doesn't attempt; failures that would
genuinely belong there mostly fall into `OTHER` below rather than being
force-fit into a category the available signals can't actually support.
That's a deliberate scope limit, not an oversight -- see `classify_failure`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

TASK_MISUNDERSTANDING = "task_misunderstanding"
INSUFFICIENT_INSPECTION = "insufficient_inspection"
WRONG_TARGET_SELECTION = "wrong_target_selection"
TURN_LIMIT_EXCEEDED = "turn_limit_exceeded"
FORMAT_OUTPUT_ERROR = "format_output_error"
OTHER = "other"
CORRECT = "correct"

CATEGORIES = [
    TASK_MISUNDERSTANDING,
    INSUFFICIENT_INSPECTION,
    WRONG_TARGET_SELECTION,
    TURN_LIMIT_EXCEEDED,
    FORMAT_OUTPUT_ERROR,
    OTHER,
]


@dataclass(frozen=True)
class SeverityLabel:
    category: str
    detail: str


def classify_failure(
    passed: bool,
    output_loaded_ok: bool,
    hit_turn_limit: bool,
    inspected_before_acting: bool,
    expected_uses_formula: bool,
    output_has_formula: bool,
    grader_stdout: str = "",
) -> SeverityLabel:
    """Best-effort heuristic classifier onto SpreadsheetBench 2's
    benchmark-wide six-category failure taxonomy (see module docstring).

    Args mirror observable signals already computed elsewhere in Study 2:
    `output_loaded_ok`/`expected_uses_formula`/`output_has_formula` from
    harness/study2/runner.py's own workbook inspection, `hit_turn_limit`
    from `Trajectory.hit_turn_limit` (agent_loop.py), and
    `inspected_before_acting` from
    verification_scoring.TrajectoryBehavior -- reused here rather than
    re-derived, since "did it look before it leaped" is the same question
    their Insufficient Inspection category asks.
    """
    if passed:
        return SeverityLabel(CORRECT, "passed grader")

    if hit_turn_limit:
        return SeverityLabel(TURN_LIMIT_EXCEEDED, "agent hit max_turns without a FINAL response")

    if not inspected_before_acting:
        return SeverityLabel(
            INSUFFICIENT_INSPECTION,
            "agent's first code turn did not inspect the sheet before acting",
        )

    if not output_loaded_ok:
        # Their taxonomy has no dedicated "output failed to load" bucket --
        # this is closest to a severe case of Other rather than a forced
        # fit into one of the five named categories.
        return SeverityLabel(OTHER, "output workbook failed to load/parse")

    if expected_uses_formula and not output_has_formula:
        return SeverityLabel(
            FORMAT_OUTPUT_ERROR,
            "answer key uses a formula; model output uses a literal value (right value, wrong representation)",
        )

    # Inspected the sheet, produced a loadable output, didn't hit the turn
    # limit, and still failed grading: plausibly Wrong Target Selection
    # (correct action, wrong cell/sheet) or Task Misunderstanding, but this
    # classifier has no per-cell diff or intent signal to distinguish
    # either from a plain wrong-value computation -- see module docstring.
    return SeverityLabel(OTHER, grader_stdout[:500])
