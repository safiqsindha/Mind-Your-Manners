"""Tests for three design-level holes found in a pre-core-run review.

Unlike most of this suite these are not about crashes. Each one could have
produced a plausible-looking NUMBER that was wrong, which is worse: a crash
announces itself, a confound does not.
"""
from __future__ import annotations

import collections
from pathlib import Path
from unittest.mock import patch

import openpyxl
import pytest

from harness.providers.base import ModelConfig
from harness.study2.runner import _run_tag
from harness.study2.sandbox import execute_python_on_workbook

LIST_SIBLINGS = """
import os
d = os.path.dirname(WORKBOOK_PATH)
print("SIBLINGS:", sorted(os.listdir(d)))
"""


def _model(key: str) -> ModelConfig:
    return ModelConfig(
        key=key, provider="mock", model_id=f"x/{key}",
        display_name=key, temperature=0.0, max_tokens=512,
    )


# --- 1. Answer-key isolation ----------------------------------------------
# SpreadsheetBench stores ground truth beside the input:
# spreadsheet/59196/1_59196_input.xlsx next to 1_59196_answer.xlsx. With
# WORKBOOK_PATH pointing into the dataset, one os.listdir reached the answer,
# and the sandbox does not restrict filesystem access.

def _dataset_dir(tmp_path: Path) -> Path:
    """A directory shaped like SpreadsheetBench's: input beside answer."""
    d = tmp_path / "spreadsheet" / "59196"
    d.mkdir(parents=True)
    for name, value in (("1_59196_input.xlsx", 1), ("1_59196_answer.xlsx", 999)):
        wb = openpyxl.Workbook()
        wb.active["A1"] = value
        wb.save(d / name)
    return d


def test_model_code_cannot_see_the_answer_file(tmp_path: Path):
    """The whole point: a model listing its workbook's directory must not
    find the ground truth there."""
    data = _dataset_dir(tmp_path)

    result = execute_python_on_workbook(
        LIST_SIBLINGS, data / "1_59196_input.xlsx", tmp_path / "work"
    )

    assert result.returncode == 0, result.stderr
    assert "_answer" not in result.stdout, (
        f"answer key reachable from the sandbox: {result.stdout}"
    )


def test_the_workbook_the_model_reads_is_a_copy_not_the_dataset_file(tmp_path: Path):
    data = _dataset_dir(tmp_path)
    workdir = tmp_path / "work"

    execute_python_on_workbook(
        "print('PATH:', WORKBOOK_PATH)", data / "1_59196_input.xlsx", workdir
    )

    copied = workdir / "1_59196_input.xlsx"
    assert copied.exists(), "input should be copied into the workdir"
    assert copied.parent == workdir


def test_the_copy_has_the_same_contents_as_the_original(tmp_path: Path):
    """Isolation must not change what the model is working on."""
    data = _dataset_dir(tmp_path)
    src = data / "1_59196_input.xlsx"

    result = execute_python_on_workbook(
        "import openpyxl\nprint('VAL:', openpyxl.load_workbook(WORKBOOK_PATH).active['A1'].value)",
        src, tmp_path / "work",
    )

    assert "VAL: 1" in result.stdout, result.stdout
    assert (tmp_path / "work" / src.name).read_bytes() == src.read_bytes()


def test_the_original_dataset_file_is_not_modified(tmp_path: Path):
    """Model code writing to WORKBOOK_PATH must hit the copy, never the
    benchmark's own input file."""
    data = _dataset_dir(tmp_path)
    src = data / "1_59196_input.xlsx"
    before = src.read_bytes()

    execute_python_on_workbook(
        "import openpyxl\nwb = openpyxl.load_workbook(WORKBOOK_PATH)\n"
        "wb.active['A1'] = 'CLOBBERED'\nwb.save(WORKBOOK_PATH)",
        src, tmp_path / "work",
    )

    assert src.read_bytes() == before, "model code modified the dataset input"


def test_the_extension_is_preserved_so_xlsm_handling_still_works(tmp_path: Path):
    """Real model code branches on WORKBOOK_PATH.lower().endswith('.xlsm')."""
    src = tmp_path / "book.xlsm"
    wb = openpyxl.Workbook()
    wb.active["A1"] = 1
    wb.save(src)

    result = execute_python_on_workbook(
        "print('EXT_OK:', WORKBOOK_PATH.lower().endswith('.xlsm'))", src, tmp_path / "work"
    )

    assert "EXT_OK: True" in result.stdout, result.stdout


# --- 2. Tone order randomisation ------------------------------------------
# A fixed L1..L7 sequence confounds tone with position-in-burst. Retry backoff
# accumulates across consecutive calls, so the last tone would systematically
# meet worse provider conditions than the first.

def _tone_sequences(tone_seed: int, n_tasks: int = 8):
    """Run the batch loop with everything stubbed, capturing tone order."""
    from harness.study2 import runner

    seen: dict[str, list[str]] = collections.defaultdict(list)

    class _Task:
        def __init__(self, tid):
            self.task_id = tid
            self.instruction_type = "Cell-Level Manipulation"
            self.instruction = "do it"
            self.answer_position = "A1"
            self.input_spreadsheet_paths = [Path("in.xlsx")]
            self.answer_spreadsheet_paths = [Path("ans.xlsx")]

    from harness.study2.agent_loop import Trajectory

    def fake_run(tracker, model, task_id, instruction, input_path, workdir, *, tone_level, trial, **kw):
        seen[task_id].append(tone_level)
        return Trajectory(task_id=task_id, tone_level=tone_level, trial=trial)

    def fake_grade(grader, task, traj, workdir):
        from harness.study2.grader import GradeResult
        return GradeResult(task.task_id, False, 3, 0, 0.0, [])

    with patch("harness.study2.runner.run_react_multi_round", side_effect=fake_run), \
         patch("harness.study2.runner._grade_trajectory", side_effect=fake_grade), \
         patch("harness.study2.runner.no_op_passes", return_value=False):
        runner.run_condition_batch(
            [_model("m")], [_Task(f"t{i}") for i in range(n_tasks)],
            grader=None, out_dir=Path("/tmp/_tone_order_probe"), phase="probe",
            budget_cap_usd=1e6, n_trials=1, tone_seed=tone_seed,
        )
    return seen


def test_tone_order_is_not_the_same_every_task():
    """The bug: identical L1..L7 for every task and trial."""
    seen = _tone_sequences(tone_seed=0)
    orders = {tuple(v) for v in seen.values()}
    assert len(orders) > 1, f"tone order identical across all tasks: {orders}"


def test_every_tone_still_runs_exactly_once_per_task():
    """Shuffling must not drop or duplicate a condition."""
    from harness.tone_wrappers import TONE_ORDER

    for task_id, tones in _tone_sequences(tone_seed=0).items():
        assert sorted(tones) == sorted(TONE_ORDER), f"{task_id} got {tones}"


def test_tone_order_is_reproducible_for_a_seed():
    assert _tone_sequences(tone_seed=7) == _tone_sequences(tone_seed=7)


def test_a_different_seed_gives_a_different_arrangement():
    assert _tone_sequences(tone_seed=1) != _tone_sequences(tone_seed=2)


# --- 3. Per-run file namespacing ------------------------------------------
# Four models run as concurrent processes shared one raw log, one records
# file, and -- worst -- one SpendTracker resume source, so each model would
# count all four models' spend against its own cap.

def test_a_single_model_run_gets_its_own_tag():
    assert _run_tag([_model("gpt-luna")]) == "gpt-luna"


def test_two_single_model_runs_do_not_collide():
    """The parallel case: each process must write its own files."""
    tags = {_run_tag([_model(k)]) for k in ("gpt-luna", "glm-current", "deepseek-current", "qwen-current")}
    assert len(tags) == 4


def test_a_multi_model_run_in_one_process_shares_one_tag():
    """Correct: they are genuinely one run under one budget cap."""
    assert _run_tag([_model("a"), _model("b")]) == "multi"


# --- 4. The validation gate's spend log was still shared -------------------
# Fix 3 namespaced the core path's files but left the gate's SpendTracker log
# on one fixed name. The gate is the phase that runs four models AT ONCE by
# design, and SpendTracker resumes its running total from that file, so each
# model would count all four models' spend against its own $10 cap.

def _gate_tracker_path(model_key: str, out_dir: Path) -> Path:
    """Run the gate with zero tasks and report where SpendTracker was pointed."""
    from harness.study2 import runner

    seen: list[Path] = []

    class _FakeTracker:
        total_usd = 0.0

        def __init__(self, path, **kw):
            seen.append(Path(path))

        def close(self):
            pass

    with patch("harness.study2.runner.SpendTracker", _FakeTracker):
        runner.run_validation_gate(_model(model_key), [], grader=None, out_dir=out_dir)
    return seen[0]


def test_two_models_gating_do_not_share_a_spend_log(tmp_path: Path):
    a = _gate_tracker_path("gpt-luna", tmp_path)
    b = _gate_tracker_path("qwen-current", tmp_path)
    assert a != b, f"both models wrote spend to {a}"


def test_the_gate_spend_log_names_its_model(tmp_path: Path):
    path = _gate_tracker_path("deepseek-current", tmp_path)
    assert "deepseek-current" in path.name, path.name
