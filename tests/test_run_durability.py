"""Tests for not losing graded work, and not re-granting a spent budget.

Two failures on the paid path, both found by auditing for the bug classes
this project already hit once:

1. run_condition_batch() dumped its graded records AFTER the try/finally, so
   any exception escaping the loop skipped the write. The exception that ends
   a capped run is BudgetExceeded -- raised by SpendTracker.record() the
   moment the cap is reached, i.e. the EXPECTED termination of a core run. A
   $150 run ending exactly as designed wrote zero graded records.

2. SpendTracker opened its log in append mode but initialised total_usd to
   0.0, so restarting a run granted a fresh full cap. Combined with (1) --
   crash, lose the records, rerun -- the cap could be spent several times
   over.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness.spend_tracker import BudgetExceeded, ResultRow, SpendTracker, _prior_spend
from harness.study2.runner import _append_record, _write_records


def _row(cost: float) -> ResultRow:
    return ResultRow(
        row_id="r", study="study2", phase="core", item_id="t", tone_level="L4_neutral",
        trial=0, model_key="m", model_id="m", provider="p", temperature=0.0, seed=None,
        reasoning_effort=None, thinking_budget_tokens=None, prompt_tokens=1,
        completion_tokens=1, reasoning_tokens=0, cost_usd=cost, latency_s=0.0,
        refused=False, error=None, response_text="", extracted_answer=None,
        is_correct=None, timestamp=0.0,
    )


# --- Budget is not re-granted on restart ----------------------------------

def test_restarting_a_run_does_not_hand_out_a_fresh_budget(tmp_path: Path):
    log = tmp_path / "raw.jsonl"
    first = SpendTracker(log, phase="core", cap_usd=10.0)
    first.record(_row(6.0))
    first.close()

    second = SpendTracker(log, phase="core", cap_usd=10.0)
    assert second.total_usd == pytest.approx(6.0), "prior spend must carry over"
    assert second.n_calls == 1
    # Only $4 of the $10 cap is left, so $5 more must stop the run.
    with pytest.raises(BudgetExceeded):
        second.record(_row(5.0))
    second.close()


def test_a_fresh_log_starts_at_zero(tmp_path: Path):
    t = SpendTracker(tmp_path / "new.jsonl", phase="core", cap_usd=10.0)
    assert t.total_usd == 0.0 and t.n_calls == 0
    t.close()


def test_prior_spend_survives_a_truncated_final_line(tmp_path: Path):
    """A process killed mid-write leaves a partial line. That must not stop
    the next run from starting, and must not reset the budget to zero."""
    log = tmp_path / "raw.jsonl"
    log.write_text(
        json.dumps({"cost_usd": 1.5}) + "\n"
        + json.dumps({"cost_usd": 2.5}) + "\n"
        + '{"cost_usd": 9.9, "resp'  # killed mid-write
    )
    total, n = _prior_spend(log)
    assert total == pytest.approx(4.0)
    assert n == 2


def test_prior_spend_ignores_rows_with_no_cost(tmp_path: Path):
    log = tmp_path / "raw.jsonl"
    log.write_text(json.dumps({"cost_usd": None}) + "\n" + json.dumps({"cost_usd": 2.0}) + "\n")
    total, _ = _prior_spend(log)
    assert total == pytest.approx(2.0)


# --- Graded records survive the run ending --------------------------------

def test_records_are_written_even_when_the_run_raises(tmp_path: Path):
    """_write_records is called from a finally block; it must not itself
    raise, or a secondary failure would destroy the records while handling
    the primary one."""
    records = [{"task_id": "t1", "passed": True}]
    _write_records(tmp_path, "core", records, "gpt-luna")
    written = json.loads((tmp_path / "analysis" / "study2_core_gpt-luna_records.json").read_text())
    assert written == records


def test_write_records_survives_an_unwritable_destination(tmp_path: Path, capsys):
    bad = tmp_path / "file_not_a_dir"
    bad.write_text("x")  # analysis/ cannot be created underneath a file
    _write_records(bad, "core", [{"task_id": "t"}], "gpt-luna")  # must not raise
    assert "WARNING" in capsys.readouterr().out


def test_each_record_is_durable_before_the_run_ends(tmp_path: Path):
    """The end-of-run JSON only exists once the loop finishes. A SIGKILL or
    OOM runs no finally block, so records must also land as they are made."""
    for i in range(3):
        _append_record(tmp_path, "core", {"task_id": f"t{i}", "passed": i == 0}, "gpt-luna")

    lines = (tmp_path / "analysis" / "study2_core_gpt-luna_records.jsonl").read_text().strip().splitlines()
    assert len(lines) == 3
    assert [json.loads(x)["task_id"] for x in lines] == ["t0", "t1", "t2"]


def test_appending_records_never_raises_into_the_run(tmp_path: Path, capsys):
    bad = tmp_path / "file_not_a_dir"
    bad.write_text("x")
    _append_record(bad, "core", {"task_id": "t"}, "gpt-luna")  # must not raise
    assert "WARNING" in capsys.readouterr().out
