"""Two arms must never share an execution directory.

The defect: the micro-experiment's neutral and threatening runs both used
tone L4_neutral over the same 50 tasks and the same 8 trials, so all 800
trajectories mapped onto 400 scratch directories and every graded pass/fail
in that pair of runs was suspect.

The fix put `tag` (which folds in --run-label) into the workdir path. But the
existing tests only assert that `_run_tag()` returns distinct STRINGS -- they
never call `run_condition_batch` and inspect the `workdir` it actually uses.
A refactor that dropped `tag` from the path would keep `_run_tag` intact and
pass every one of those tests while silently recreating the collision.

This pins it where the bug happened: the real path handed to the agent loop.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

from harness.config import ModelConfig
from harness.study2 import runner


def _model(key: str) -> ModelConfig:
    return ModelConfig(
        key=key, provider="mock", model_id=f"x/{key}",
        display_name=key, temperature=0.0, max_tokens=512,
    )


class _Task:
    def __init__(self, tid: str) -> None:
        self.task_id = tid
        self.instruction = "do the thing"
        self.instruction_type = "cell-level"
        self.answer_position = "A1"
        self.input_spreadsheet_paths = [Path("in.xlsx")]
        self.answer_spreadsheet_paths = [Path("ans.xlsx")]


def _workdirs_for(tmp_path: Path, run_label: str | None) -> list[Path]:
    """Run one arm and capture every workdir the agent loop was handed."""
    from harness.study2.agent_loop import Trajectory
    from harness.study2.grader import GradeResult

    seen: list[Path] = []

    def fake_run(tracker, model, task_id, instruction, input_path, workdir,
                 *, tone_level, trial, **kw):
        seen.append(Path(workdir))
        return Trajectory(task_id=task_id, tone_level=tone_level, trial=trial)

    def fake_grade(grader, task, traj, workdir):
        return GradeResult(task.task_id, False, 3, 0, 0.0, [])

    with patch("harness.study2.runner.run_react_multi_round", side_effect=fake_run), \
         patch("harness.study2.runner._grade_trajectory", side_effect=fake_grade), \
         patch("harness.study2.runner.no_op_passes", return_value=False):
        runner.run_condition_batch(
            [_model("m")], [_Task("t0")],
            grader=None, out_dir=tmp_path, phase="probe",
            budget_cap_usd=1e6, n_trials=1, tone_seed=0,
            run_label=run_label,
        )
    return seen


def test_two_labelled_arms_never_share_a_scratch_directory(tmp_path):
    """The exact collision that corrupted 800 grades."""
    a = _workdirs_for(tmp_path, run_label="neutral")
    b = _workdirs_for(tmp_path, run_label="threatening")

    assert a and b, "no workdirs captured -- the harness did not run"
    overlap = set(a) & set(b)
    assert not overlap, (
        "two arms shared execution directories: "
        f"{sorted(str(p) for p in overlap)[:3]}. The run label must appear in "
        "the scratch path, or one arm's output overwrites the other's."
    )


def test_the_run_label_is_what_separates_them(tmp_path):
    """Guard against a refactor that separates arms by something incidental."""
    a = _workdirs_for(tmp_path, run_label="neutral")
    b = _workdirs_for(tmp_path, run_label="threatening")
    assert any("neutral" in str(p) for p in a), (
        f"run_label absent from the scratch path: {a[0]}"
    )
    assert any("threatening" in str(p) for p in b), (
        f"run_label absent from the scratch path: {b[0]}"
    )


def test_one_arm_is_internally_unique(tmp_path):
    """Within an arm, each (task, trial, turn) still gets its own directory."""
    dirs = _workdirs_for(tmp_path, run_label="solo")
    assert len(dirs) == len(set(dirs)), "an arm reused a scratch directory internally"
