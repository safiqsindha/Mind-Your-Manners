"""The two `n_turns` in the artefacts are different quantities, and must stay so.

The run records write `n_turns = behavior.n_code_turns` (turns that emitted
code); the per-turn regrade writes `n_turns = len(traj.steps)` (every model
call, including the closing FINAL: message or refusal, which carries no code).
They share a field name and differ on 751 of the micro-experiment's 800
trajectories.

That collision has already produced one real bug: `turn_count_family.py`
computed the primary outcome's micro-experiment row from the regrade file and
reported +1.02 turns where the run records give +1.32. It was caught in review,
not by the suite.

These tests pin the reconciliation so that (a) the identity is checked against
committed data rather than asserted in prose, and (b) if either definition is
ever changed to match the other, something fails loudly.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "results" / "analysis" / "turn_definitions.py"


@pytest.fixture(scope="module")
def td():
    spec = importlib.util.spec_from_file_location("turn_definitions", MODULE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["turn_definitions"] = mod
    spec.loader.exec_module(mod)
    mod.materialise()
    return mod


@pytest.mark.parametrize("arm", ["neutral", "threatening"])
def test_records_n_turns_is_acting_turns(td, arm):
    """The records' count is recoverable from the regrade's own diagnostics."""
    s = td.reconcile(arm)
    assert s["records_is_acting_turns"] == s["n"], (
        f"{arm}: records n_turns matches the count of code-emitting turns on only "
        f"{s['records_is_acting_turns']}/{s['n']} trajectories -- one of the two "
        "definitions has changed"
    )


@pytest.mark.parametrize("arm", ["neutral", "threatening"])
def test_gap_is_exactly_the_non_acting_turns(td, arm):
    """regrade - records == turns that emitted no code, on every trajectory."""
    s = td.reconcile(arm)
    assert s["identity_holds"] == s["n"], (
        f"{arm}: the identity holds on only {s['identity_holds']}/{s['n']}. If this "
        "fails the two counts are no longer explained by non-acting turns, and the "
        "difference IS a defect rather than a definition"
    )


@pytest.mark.parametrize("arm", ["neutral", "threatening"])
def test_they_differ_at_all(td, arm):
    """Guards the guard: if they ever agree everywhere, these tests prove nothing."""
    s = td.reconcile(arm)
    assert s["differ"] > 0, (
        f"{arm}: the two counts now agree everywhere, so the identity above is "
        "vacuous -- check whether a definition changed before deleting these tests"
    )


@pytest.mark.parametrize("arm", ["neutral", "threatening"])
def test_agreement_means_the_ceiling_was_hit(td, arm):
    """A trajectory cut off at the ceiling never emits its closing turn."""
    s = td.reconcile(arm)
    assert s["agree"] == s["agree_and_hit_ceiling"], (
        f"{arm}: {s['agree'] - s['agree_and_hit_ceiling']} trajectories have equal "
        "counts without hitting the turn ceiling, which the explanation in "
        "results/analysis/turn_definitions.py does not cover"
    )


def test_paper_reports_acting_turns(td):
    """The primary outcome is the smaller of the two, and the paper says which.

    Matched by content rather than by filename: the manuscript has been
    renumbered more than once, and a test that pins a file path fails on a
    rename rather than on the thing it is checking.
    """
    for arm in ("neutral", "threatening"):
        s = td.reconcile(arm)
        assert s["mean_acting"] < s["mean_calls"]
    prose = "\n".join(p.read_text() for p in sorted((ROOT / "paper").glob("*.md")))
    assert "acting turns" in prose, (
        "the paper no longer states which of the two quantities it reports; "
        "turn count is the primary outcome and the two differ by ~31%"
    )
