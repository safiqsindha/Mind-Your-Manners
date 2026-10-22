"""Progress and turn counts must be measured on the same trajectories.

The per-turn regrade covers every scheduled trajectory and has no firing flag;
the primary turn-count outcome excludes trajectories on which the interjection
never fired and, in the register run, injection position 0. Dividing a progress
effect from the first population by a turn effect from the second produced the
paper's "40-65% of each turn effect is repeated work" -- which is 56-93% once
both sides use the same trajectories. `load_aligned` joins each regrade row back
to its run record and applies the primary filters; these tests pin that the
aligned population IS the primary one, and that the unaligned one is not.
"""

from __future__ import annotations

import importlib.util
import pathlib
import statistics
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "results" / "analysis"))

import accuracy_null_mde as A  # noqa: E402
from _inputs import materialise  # noqa: E402


def _summary(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["regrade_summary.py", *argv])
    spec = importlib.util.spec_from_file_location(
        "regrade_summary_under_test", ROOT / "results" / "analysis" / "regrade_summary.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _mean_turns(rows):
    return statistics.fmean(
        statistics.fmean(v) for v in _by_task(rows, "n_acting").values())


def _by_task(rows, field):
    out = {}
    for r in rows:
        out.setdefault(r["task_id"], []).append(float(r[field]))
    return out


@pytest.fixture(scope="module", autouse=True)
def _inputs():
    materialise()


def test_aligned_turn_effect_is_the_primary_outcome(monkeypatch):
    """Demand vs control in the probe run is +1.168 turns, from accuracy_null_mde."""
    R = _summary(monkeypatch)
    probe = A.load(A.ARCHIVE / "core_gpt-luna_probe_records.json")
    primary = {arm: A.per_task(probe, arm=arm, field="n_turns")
               for arm in ("P0_control", "P1_demand_only")}
    shared = sorted(set(primary["P0_control"]) & set(primary["P1_demand_only"]))
    want = statistics.fmean(primary["P1_demand_only"][t] - primary["P0_control"][t] for t in shared)

    treat = R.load_aligned("gpt-luna-probe-P1_demand_only")
    ctrl = R.load_aligned("gpt-luna-probe-P0_control")
    t, c = R.per_task(treat, lambda r: r["n_acting"]), R.per_task(ctrl, lambda r: r["n_acting"])
    got = statistics.fmean(t[k] - c[k] for k in sorted(set(t) & set(c)))
    assert got == pytest.approx(want, abs=1e-9)
    assert want == pytest.approx(1.168, abs=1e-3)


def test_unaligned_population_is_larger_and_differs(monkeypatch):
    """The old population kept trajectories that never received the message."""
    aligned = _summary(monkeypatch).load_aligned("gpt-luna-probe-P0_control")
    every = _summary(monkeypatch, "--all-rows").load_aligned("gpt-luna-probe-P0_control")
    assert len(every) == 400 and len(aligned) == 300
    assert _mean_turns(every) != pytest.approx(_mean_turns(aligned), abs=1e-3)


def test_register_run_drops_injection_position_zero(monkeypatch):
    R = _summary(monkeypatch)
    rows = R.load_aligned("gpt-luna-cross7-L3_polite")
    assert {r["interjection_turn"] for r in rows} == {1, 2}


def test_redundant_share_reproduces_the_demand_effect(monkeypatch):
    """Demand in the probe run: +0.92 redundant steps of +1.17 turns, about 78%."""
    import numpy as np
    R = _summary(monkeypatch)
    sh = R.share_of_turn_effect(
        R.load_aligned("gpt-luna-probe-P1_demand_only"),
        R.load_aligned("gpt-luna-probe-P0_control"), np.random.default_rng(1))
    assert sh["turns"] == pytest.approx(1.168, abs=1e-3)
    assert sh["share"] == pytest.approx(0.78, abs=0.01)
    assert sh["clear"] is True
