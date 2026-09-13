"""Per-turn progress regrading.

The range parser here shipped with a bug that returned None for every
unprefixed range, which reads as "unmeasurable" rather than as a defect --
the failure mode that produces a confident analysis of nothing. These pin
the shapes that actually occur in SpreadsheetBench's answer_position field.
"""
import pytest

from harness.study2.progress import (
    TrajectoryProgress,
    TurnProgress,
    changed,
    match_fraction,
    parse_answer_position,
)


@pytest.mark.parametrize("text,expected", [
    # The bug: without a sheet prefix the unquoted alternative greedily ate
    # part of the range, parsing "P2:P7" as sheet "P2:" plus cell "P7".
    ("P2:P7", (None, "P2", "P7")),
    ("H3:H5", (None, "H3", "H5")),
    ("A1", (None, "A1", "A1")),
    ("AA10:AB20", (None, "AA10", "AB20")),
    ("'Vendor'!A1:D101", ("Vendor", "A1", "D101")),
    ("Sheet1!H3:H5", ("Sheet1", "H3", "H5")),
    ("Sheet 2!A1:B2", ("Sheet 2", "A1", "B2")),
    ("'My Sheet'!C3", ("My Sheet", "C3", "C3")),
])
def test_answer_position_forms(text, expected):
    assert parse_answer_position(text) == expected


def test_unparseable_answer_position_raises():
    """Silently returning None would make every affected task look
    unmeasurable instead of surfacing the problem."""
    for bad in ("", "not a range", "1A:2B"):
        with pytest.raises(ValueError):
            parse_answer_position(bad)


def test_match_fraction_is_type_tolerant():
    """An agent writing 3 where the answer holds 3.0 has not made a mistake,
    and blank vs empty string is not a difference worth counting."""
    assert match_fraction({"A1": 3, "A2": None}, {"A1": 3.0, "A2": ""}) == 1.0
    assert match_fraction({"A1": " x "}, {"A1": "x"}) == 1.0
    assert match_fraction({"A1": 1, "A2": 2}, {"A1": 1, "A2": 99}) == 0.5


def test_unreadable_output_is_none_not_zero():
    """A crashed turn is an absence of a measurement, not zero progress.
    Averaging it in as 0.0 would make arms with more crashes look like arms
    that regressed."""
    assert match_fraction(None, {"A1": 1}) is None
    assert changed(None, {"A1": 1}) is None
    assert changed({"A1": 1}, None) is None


def test_changed_detects_a_no_op_turn():
    assert changed({"A1": 1, "A2": 2}, {"A1": 1, "A2": 2}) is False
    assert changed({"A1": 1}, {"A1": 2}) is True
    # A cell appearing or vanishing counts as a change.
    assert changed({"A1": 1}, {"A1": 1, "A2": 3}) is True


def _traj(matches):
    turns = []
    prev = None
    for i, m in enumerate(matches):
        turns.append(TurnProgress(i, m is not None, m is not None, m,
                                  None if prev is None or m is None else (m != prev)))
        if m is not None:
            prev = m
    return TrajectoryProgress("t", 0, "arm", 1, turns)


def test_noop_turns_counted_only_when_measured():
    """Turns with no measurement must not be counted as no-ops -- that would
    inflate the very statistic the thrashing claim rests on."""
    t = _traj([0.5, 0.5, 0.5])
    assert t.n_noop_turns == 2
    assert _traj([0.5, None, None]).n_noop_turns == 0


def test_improved_at_end_flags_a_trajectory_that_quit_on_an_upswing():
    """This is the premature-stop test: a trajectory still climbing when it
    stopped left progress on the table."""
    assert _traj([0.2, 0.5, 0.9]).improved_at_end is True
    assert _traj([0.9, 0.9]).improved_at_end is False
    assert _traj([0.9, 0.2]).improved_at_end is False
    assert _traj([0.5]).improved_at_end is None


def test_best_and_final_ignore_unmeasured_tail():
    """Trajectories routinely end on a FINAL: line that produces no workbook.
    Reading the final match off that would report every one as unmeasurable."""
    t = _traj([0.4, 0.8, None])
    assert t.final_match == 0.8
    assert t.best_match == 0.8
    assert _traj([0.9, 0.3, None]).final_match == 0.3
    assert _traj([0.9, 0.3, None]).best_match == 0.9
