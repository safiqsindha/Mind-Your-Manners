"""Tests for run_validation_gate()'s per-task reporting.

The gate previously returned only an aggregate n_passed. That is not enough
to act on: three roster models each scoring 3/5 is consistent both with
"these models have similar overall skill" and with "every model fails the
same two tasks", and those imply very different things about the roster,
the task sample, and the grader. It also placed every model's scratch
output at the same path, so each gate run destroyed the previous model's
artifacts.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from harness.providers.base import ModelConfig
from harness.study2.agent_loop import Trajectory, TrajectoryStep
from harness.study2.grader import GradeResult
from harness.study2.runner import run_validation_gate

MODEL = ModelConfig(
    key="test-model",
    provider="mock",
    model_id="test/model",
    display_name="Test Model",
    temperature=0.0,
    max_tokens=1024,
)


class _FakeTask:
    def __init__(self, task_id: str, instruction_type: str = "Cell-Level Manipulation"):
        self.task_id = task_id
        self.instruction_type = instruction_type
        self.instruction = "do the thing"
        self.answer_position = "A1"
        self.input_spreadsheet_paths = [Path("in.xlsx")]
        self.answer_spreadsheet_paths = [Path("ans.xlsx")]


def _trajectory(task_id: str, *, hit_limit: bool, stderr: str = "") -> Trajectory:
    traj = Trajectory(task_id=task_id, tone_level="none", trial=0)
    traj.steps.append(TrajectoryStep(0, "resp", "code", "out", stderr, is_final=True))
    traj.hit_turn_limit = hit_limit
    return traj


def _grade(task_id: str, passed: bool) -> GradeResult:
    return GradeResult(
        task_id=task_id,
        passed=passed,
        n_test_cases=3,
        n_test_cases_passed=3 if passed else 1,
        soft_restriction=1.0 if passed else 0.33,
        per_test_case_messages=[],
    )


@pytest.fixture
def gate(tmp_path):
    """Runs the gate over two tasks -- one passing, one failing -- with the
    model call and grader stubbed out, so only the reporting is exercised."""
    tasks = [_FakeTask("task_pass"), _FakeTask("task_fail", "Chart Generation")]
    trajectories = {
        "task_pass": _trajectory("task_pass", hit_limit=False),
        "task_fail": _trajectory("task_fail", hit_limit=True, stderr="boom: it broke"),
    }

    def fake_run(tracker, model, task_id, *a, **kw):
        return trajectories[task_id]

    def fake_grade(grader, task, traj, workdir):
        return _grade(task.task_id, task.task_id == "task_pass")

    with patch("harness.study2.runner.run_react_multi_round", side_effect=fake_run), \
         patch("harness.study2.runner._grade_trajectory", side_effect=fake_grade):
        # check_no_op=False: these assertions are about per-task reporting,
        # and the no-op floor has its own tests below.
        return run_validation_gate(MODEL, tasks, grader=None, out_dir=tmp_path, check_no_op=False)


def test_gate_reports_which_tasks_passed_not_just_how_many(gate):
    assert gate["n_passed"] == 1
    by_id = {t["task_id"]: t for t in gate["per_task"]}
    assert by_id["task_pass"]["passed"] is True
    assert by_id["task_fail"]["passed"] is False


def test_per_task_carries_the_signals_needed_to_explain_a_failure(gate):
    fail = next(t for t in gate["per_task"] if t["task_id"] == "task_fail")
    assert fail["hit_turn_limit"] is True
    assert fail["instruction_type"] == "Chart Generation"
    assert fail["n_test_cases_passed"] == 1
    assert fail["n_test_cases"] == 3
    # The stderr the model actually saw has to survive into the record.
    assert "boom: it broke" in fail["turn_diagnostics"][0]["stderr"]


def test_aggregate_fields_still_present_and_consistent(gate):
    assert gate["n_tasks"] == 2
    assert gate["observed_accuracy"] == 0.5
    assert gate["n_passed"] == sum(t["passed"] for t in gate["per_task"])


def test_scratch_dirs_are_namespaced_by_model(tmp_path):
    """Two models running the gate must not overwrite each other's output."""
    seen: list[Path] = []
    tasks = [_FakeTask("shared_task")]

    def capture_workdir(tracker, model, task_id, instruction, input_path, workdir, **kw):
        seen.append(Path(workdir))
        return _trajectory(task_id, hit_limit=False)

    with patch("harness.study2.runner.run_react_multi_round", side_effect=capture_workdir), \
         patch("harness.study2.runner._grade_trajectory", side_effect=lambda *a: _grade("shared_task", True)):
        run_validation_gate(MODEL, tasks, grader=None, out_dir=tmp_path, check_no_op=False)
        other = ModelConfig(
            key="other-model", provider="mock", model_id="other/model",
            display_name="Other", temperature=0.0, max_tokens=1024,
        )
        run_validation_gate(other, tasks, grader=None, out_dir=tmp_path, check_no_op=False)

    assert len(seen) == 2
    assert seen[0] != seen[1], "both models wrote to the same scratch dir"
    assert MODEL.key in seen[0].parts
    assert "other-model" in seen[1].parts


# --- No-op floor ----------------------------------------------------------
# Some SpreadsheetBench tasks grade a range that already holds the expected
# values in the input, so handing the workbook back untouched scores a full
# pass. 4 of the first 40 sample tasks (10%) are free this way, and 2 of the
# gate's default 5 are -- making a raw accuracy number uninterpretable.

def _gate_with_free_tasks(tmp_path, free_ids: set[str]):
    tasks = [_FakeTask("free_a"), _FakeTask("real_b"), _FakeTask("free_c")]

    def fake_run(tracker, model, task_id, *a, **kw):
        return _trajectory(task_id, hit_limit=False)

    # The model passes free_a (which anyone passes) and real_b (a real solve),
    # and fails free_c -- i.e. it does worse than nothing on one free task.
    passing = {"free_a", "real_b"}

    with patch("harness.study2.runner.run_react_multi_round", side_effect=fake_run), \
         patch("harness.study2.runner._grade_trajectory",
               side_effect=lambda g, task, tr, wd: _grade(task.task_id, task.task_id in passing)), \
         patch("harness.study2.runner.no_op_passes",
               side_effect=lambda g, task, wd: task.task_id in free_ids):
        return run_validation_gate(MODEL, tasks, grader=None, out_dir=tmp_path)


def test_gate_reports_the_no_op_floor_beside_the_score(tmp_path):
    r = _gate_with_free_tasks(tmp_path, {"free_a", "free_c"})
    assert r["n_passed"] == 2
    assert r["no_op_n_passed"] == 2, "two tasks pass by doing nothing"
    assert r["no_op_accuracy"] == 2 / 3


def test_gate_counts_only_real_solves_as_beating_the_floor(tmp_path):
    r = _gate_with_free_tasks(tmp_path, {"free_a", "free_c"})
    # free_a passed but was free; real_b passed and was not.
    assert r["n_passed_beating_no_op"] == 1
    assert r["n_discriminating_tasks"] == 1
    by_id = {t["task_id"]: t for t in r["per_task"]}
    assert by_id["free_a"]["beat_no_op"] is False
    assert by_id["real_b"]["beat_no_op"] is True


def test_free_task_ids_are_named_so_the_sample_can_be_fixed(tmp_path):
    r = _gate_with_free_tasks(tmp_path, {"free_a", "free_c"})
    assert sorted(r["free_task_ids"]) == ["free_a", "free_c"]


def test_no_free_tasks_leaves_the_floor_at_zero(tmp_path):
    r = _gate_with_free_tasks(tmp_path, set())
    assert r["no_op_n_passed"] == 0
    assert r["n_discriminating_tasks"] == 3
    assert r["n_passed_beating_no_op"] == r["n_passed"]


def test_no_op_check_can_be_disabled(tmp_path):
    """Grading a no-op copy costs real grader work (LibreOffice recalc) and
    no model spend; it must still be possible to skip."""
    tasks = [_FakeTask("t1")]
    with patch("harness.study2.runner.run_react_multi_round",
               side_effect=lambda *a, **kw: _trajectory("t1", hit_limit=False)), \
         patch("harness.study2.runner._grade_trajectory", side_effect=lambda *a: _grade("t1", True)), \
         patch("harness.study2.runner.no_op_passes", side_effect=AssertionError("should not be called")):
        r = run_validation_gate(MODEL, tasks, grader=None, out_dir=tmp_path, check_no_op=False)
    assert "no_op_accuracy" not in r
    assert r["per_task"][0]["no_op_passes"] is None
