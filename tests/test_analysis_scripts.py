"""Regression tests for results/analysis/ scripts.

These scripts compute numbers that appear in the paper, but they live outside
`harness/` and so were historically covered by neither CI's py_compile pass nor
pytest. Two real defects shipped in that blind spot:

  * a local Benjamini-Hochberg reimplementation that was not the step-up
    procedure -- it compared each p-value against its own critical value
    individually, so it could refuse rank 3 while accepting rank 4 at a larger
    p-value; and
  * a "the two comparisons that matter" summary whose numbers were hardcoded
    string literals rather than the values computed immediately above them.

Both are pinned here.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from harness.stats import benjamini_hochberg

ANALYSIS = pathlib.Path(__file__).resolve().parents[1] / "results" / "analysis"
SCRIPTS = sorted(ANALYSIS.glob("*.py"))


def test_analysis_scripts_exist():
    assert SCRIPTS, "expected at least one script in results/analysis/"


@pytest.mark.parametrize("path", SCRIPTS, ids=lambda p: p.name)
def test_analysis_script_parses(path: pathlib.Path):
    """CI's py_compile pass covers harness/ and tests/ only; cover these too."""
    ast.parse(path.read_text(), filename=str(path))


@pytest.mark.parametrize("path", SCRIPTS, ids=lambda p: p.name)
def test_no_local_benjamini_hochberg(path: pathlib.Path):
    """The shared, tested step-up implementation is the only one allowed."""
    tree = ast.parse(path.read_text(), filename=str(path))
    local = [n.name for n in ast.walk(tree)
             if isinstance(n, ast.FunctionDef) and "benjamini" in n.name.lower()]
    assert not local, (
        f"{path.name} defines its own {local}; import it from harness.stats "
        "instead -- a second implementation is how the non-step-up bug shipped"
    )


def test_bh_is_step_up_not_per_rank():
    """The exact case the old local implementation got wrong.

    Rank 3 (p=0.048) exceeds its own critical value 0.0375, but rank 4
    (p=0.049 <= 0.05) passes, so the step-up rule rescues every rank below it.
    A per-rank comparison returns the non-monotonic [T, T, F, T].
    """
    got = [r.significant for r in benjamini_hochberg([0.001, 0.003, 0.048, 0.049])]
    assert got == [True, True, True, True]

    per_rank = []
    pvals = [0.001, 0.003, 0.048, 0.049]
    order = sorted(range(4), key=lambda i: pvals[i])
    out = [None] * 4
    for rank, i in enumerate(order, start=1):
        out[i] = pvals[i] <= 0.05 * rank / 4
    per_rank = out
    assert per_rank == [True, True, False, True]
    assert per_rank != got, "test no longer distinguishes the two procedures"


def test_timing_summary_is_not_hardcoded():
    """The headline summary must be formatted from computed values."""
    src = (ANALYSIS / "timing_is_a_proxy.py").read_text()
    head = src.split("The two comparisons that matter")[1]
    for literal in ("+0.34", "+1.97", "+1.66"):
        assert literal not in head, (
            f"{literal!r} is hardcoded in the summary; format it from the "
            "computed contrasts so a regrade cannot leave it silently stale"
        )


@pytest.mark.parametrize("path", SCRIPTS, ids=lambda p: p.name)
def test_no_absolute_paths_outside_repo(path: pathlib.Path):
    """Scripts must be runnable from a fresh clone."""
    src = path.read_text()
    for bad in ("/home/user/Mind-Your-Manners", "/Users/", "C:\\\\"):
        assert bad not in src, f"{path.name} hardcodes {bad!r}; use a ROOT-relative path"


def test_permutation_p_values_are_never_exactly_zero():
    """Phipson & Smyth, on the PRIMARY tests -- not just one secondary one.

    `clustered_paired_comparison` and `clustered_trend_test` back the
    pre-registered trend test and the BH-corrected pairwise matrix for both
    studies. Both used a bare `np.mean(...)`, which returns exactly 0.0
    whenever the observed effect exceeds every permutation draw. The observed
    statistic is itself one draw from the null distribution, so an exact 0 is
    not a value a permutation test can report; the floor is 1/(draws+1).
    """
    from harness.study1.analysis import (
        N_PERMUTATIONS,
        clustered_paired_comparison,
    )

    rows = []
    for i in range(30):  # cleanly separated -- beats every sign-flip draw
        rows.append({"item_id": f"t{i}", "tone_level": "A",
                     "outcome": "answered", "is_correct": True})
        rows.append({"item_id": f"t{i}", "tone_level": "B",
                     "outcome": "answered", "is_correct": False})

    result = clustered_paired_comparison(rows, "A", "B")
    p = result.p_value if hasattr(result, "p_value") else result["p_value"]

    assert p > 0.0, "a permutation test cannot honestly report p = 0 exactly"
    assert p == pytest.approx(1.0 / (N_PERMUTATIONS + 1), rel=1e-6), (
        "maximal separation should land on the floor 1/(draws+1), not below it"
    )
