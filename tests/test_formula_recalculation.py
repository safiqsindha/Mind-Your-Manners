"""A formula-writing turn must not read as unmeasurable.

THE DEFECT THIS GUARDS. `progress.py` graded each turn's output with
openpyxl's `data_only=True` and never recalculated it, while `grader.py` had
always passed output workbooks through LibreOffice first. openpyxl writes a
formula with no cached value, so a turn answering `=SUM(A1:A3)` read back as
None, scored 0.0, and was indistinguishable from a turn that wrote nothing.
56-62% of one model's final gradable turns write formulas, and the effect was
large enough to invert a published conclusion: the continue-signal arm read as
a null on progress when it in fact gains +0.028 of the graded range.

The check that would have caught it -- benchmark-passed trajectories should
score a final match of 1.0 -- was described in the paper and never run. These
tests run the equivalent of it on a fixture, so the failure mode cannot come
back silently.
"""

from __future__ import annotations

import openpyxl
import pytest

from harness.study2 import progress


def _book(tmp_path, name, values):
    """A workbook whose B column holds `values` (literals or formula strings)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    for i, v in enumerate(values, start=1):
        ws[f"A{i}"] = i
        ws[f"B{i}"] = v
    path = tmp_path / name
    wb.save(path)
    wb.close()
    return path


def test_uncached_formula_in_range_is_detected(tmp_path):
    book = _book(tmp_path, "formula.xlsx", ["=A1*2", "=A2*2", "=A3*2"])
    assert progress._has_uncached_formula(book, "B1:B3") is True


def test_literal_values_do_not_trigger_recalculation(tmp_path):
    book = _book(tmp_path, "literal.xlsx", [2, 4, 6])
    assert progress._has_uncached_formula(book, "B1:B3") is False


def test_formula_outside_the_graded_range_does_not_trigger(tmp_path):
    """Recalculation is expensive; only the graded range should pay for it."""
    book = _book(tmp_path, "elsewhere.xlsx", [2, 4, "=A3*2"])
    assert progress._has_uncached_formula(book, "B1:B2") is False
    assert progress._has_uncached_formula(book, "B1:B3") is True


def test_unparseable_range_is_reported_as_no_formula(tmp_path):
    """Documented blind spot: an unparseable range skips recalculation rather
    than raising. Asserted so the behaviour is deliberate, not accidental."""
    book = _book(tmp_path, "bad.xlsx", ["=A1*2"])
    assert progress._has_uncached_formula(book, "not a range!!") is False


def test_formula_turn_reads_as_unmeasurable_without_recalculation(tmp_path):
    """The defect itself, pinned: this is what the regrade used to do."""
    book = _book(tmp_path, "defect.xlsx", ["=A1*2", "=A2*2", "=A3*2"])
    values = progress.range_values(book, "B1:B3", recalculate=False)
    assert values is not None
    assert all(v is None for v in values.values()), (
        "openpyxl should report uncached formulas as None -- if this ever "
        "changes, the recalculation path's rationale changes with it"
    )


@pytest.mark.skipif(
    not progress.__dict__.get("openpyxl"), reason="openpyxl unavailable"
)
def test_recalculation_makes_a_formula_turn_gradable(tmp_path):
    """End to end: with recalculate=True the same workbook grades correctly.

    Skipped where LibreOffice is absent, because the point of the test is the
    real conversion path rather than a mock of it.
    """
    import shutil

    if not (shutil.which("soffice") or shutil.which("libreoffice")):
        pytest.skip("LibreOffice not on PATH")

    book = _book(tmp_path, "recalc.xlsx", ["=A1*2", "=A2*2", "=A3*2"])
    values = progress.range_values(book, "B1:B3", recalculate=True)

    assert values is not None
    assert [values[f"B{i}"] for i in (1, 2, 3)] == [2, 4, 6]

    answer = {f"B{i}": v for i, v in zip((1, 2, 3), (2, 4, 6))}
    assert progress.match_fraction(values, answer) == 1.0


def test_match_fraction_is_zero_without_recalculation(tmp_path):
    """The scoring consequence: a correct formula answer scored 0.0.

    This is the single assertion that, had it existed, would have caught the
    defect before it reached the paper.
    """
    book = _book(tmp_path, "scored.xlsx", ["=A1*2", "=A2*2", "=A3*2"])
    answer = {"B1": 2, "B2": 4, "B3": 6}

    unrecalculated = progress.range_values(book, "B1:B3", recalculate=False)
    assert progress.match_fraction(unrecalculated, answer) == 0.0
