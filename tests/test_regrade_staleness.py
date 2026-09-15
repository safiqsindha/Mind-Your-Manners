"""A regrade older than the instrument that produced it must not be compared.

While the formula-recalculation fix was rolling out arm by arm, a freshly
regraded control compared against stale treatment arms produced a clean
final-match "effect" of -0.36 at p < 0.0001 -- in three arms at once, which is
the only reason it was caught. Cross-instrument comparison has to fail loudly.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

import pytest

SUMMARY = pathlib.Path(__file__).resolve().parents[1] / "results" / "analysis" / "regrade_summary.py"


def _load_module(tmp_analysis, tmp_instrument):
    spec = importlib.util.spec_from_file_location("regrade_summary", SUMMARY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["regrade_summary"] = mod
    spec.loader.exec_module(mod)
    mod.ANALYSIS = tmp_analysis
    mod.INSTRUMENT = tmp_instrument
    return mod


@pytest.fixture
def staged(tmp_path):
    analysis = tmp_path / "analysis"
    analysis.mkdir()
    instrument = tmp_path / "progress.py"
    instrument.write_text("# instrument")
    return analysis, instrument


def _write_arm(analysis, stem, mtime):
    path = analysis / f"study2_core_{stem}_progress.json"
    path.write_text(json.dumps([{"task_id": "1", "final_match": 1.0}]))
    os.utime(path, (mtime, mtime))
    return path


def test_arm_older_than_instrument_is_refused(staged):
    analysis, instrument = staged
    mod = _load_module(analysis, instrument)
    instrument_mtime = instrument.stat().st_mtime
    _write_arm(analysis, "stale-arm", instrument_mtime - 3600)

    with pytest.raises(SystemExit) as exc:
        mod.load("stale-arm")
    assert "STALE" in str(exc.value)


def test_arm_newer_than_instrument_loads(staged):
    analysis, instrument = staged
    mod = _load_module(analysis, instrument)
    instrument_mtime = instrument.stat().st_mtime
    _write_arm(analysis, "fresh-arm", instrument_mtime + 3600)

    assert mod.load("fresh-arm") == [{"task_id": "1", "final_match": 1.0}]


def test_missing_arm_is_none_not_an_error(staged):
    analysis, instrument = staged
    mod = _load_module(analysis, instrument)
    assert mod.load("never-regraded") is None
