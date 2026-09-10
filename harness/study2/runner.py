"""Study 2 orchestration: validation gate, then pilot -> core -> frontier
stages, each under its own budget cap (harness/config.py), each applying the
five tone wrappers to the task instruction only -- spreadsheet contents,
tool definitions, and system prompt stay identical across conditions (task
spec requirement).

Grading design (verified against a real SpreadsheetBench clone -- see
grader.py and dataset.py module docstrings): each task ships 3 test cases,
each a differently-shaped variant of the same instruction. SpreadsheetBench
grades *generalization* -- one agent-produced solution is checked against
all 3. So the agent only ever sees test case 1's input; once it produces
code that writes a solution (`Trajectory.final_code`), that same code is
mechanically re-executed (no further model calls, no extra spend) against
test cases 2 and 3's inputs, and all 3 outputs are graded together via
`SpreadsheetBenchGrader.evaluate_task()`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import openpyxl

from ..providers.base import ModelConfig
from ..spend_tracker import SpendTracker, append_spend_log
from ..tone_wrappers import TONE_ORDER, TONE_WRAPPERS
from .agent_loop import Trajectory, run_react_multi_round, run_single_round
from .dataset import SpreadsheetTask
from .failure_taxonomy import classify_failure
from .grader import GradeResult, SpreadsheetBenchGrader
from .sandbox import execute_python_on_workbook
from .verification_scoring import score_trajectory


def _generalize_to_other_test_cases(traj: Trajectory, task: SpreadsheetTask, workdir: Path) -> list[Optional[Path]]:
    """Re-runs traj.final_code (produced against test case 1) against test
    cases 2..N's inputs, without any further model calls. Returns one output
    path per test case, in order, with test case 1's own output first."""
    outputs: list[Optional[Path]] = [traj.final_output_path]
    if traj.final_code is None:
        return outputs + [None] * (len(task.input_spreadsheet_paths) - 1)

    for idx, input_path in enumerate(task.input_spreadsheet_paths[1:], start=2):
        exec_result = execute_python_on_workbook(traj.final_code, input_path, workdir / f"generalize_case{idx}")
        outputs.append(exec_result.output_workbook_path)
    return outputs


def _grade_trajectory(grader: SpreadsheetBenchGrader, task: SpreadsheetTask, traj: Trajectory, workdir: Path) -> GradeResult:
    n_cases = len(task.answer_spreadsheet_paths)
    if traj.refused or traj.final_output_path is None:
        return GradeResult(task.task_id, False, n_cases, 0, 0.0, ["no output produced"] * n_cases, error="no output produced")

    output_paths = _generalize_to_other_test_cases(traj, task, workdir)
    return grader.evaluate_task(
        task.task_id, task.instruction_type, task.answer_position,
        output_paths, task.answer_spreadsheet_paths,
    )


def run_validation_gate(
    model: ModelConfig,
    tasks: list[SpreadsheetTask],
    grader: SpreadsheetBenchGrader,
    out_dir: Path,
    expected_accuracy: Optional[float] = None,
    tolerance: float = 0.08,
    max_turns: int = 6,
) -> dict:
    """Run the unmodified benchmark instruction (no tone wrapper) through
    the multi-round agent and grade with the authors' own evaluator, before
    any wrapper-condition spend happens (task spec: "Reproduce the published
    baseline accuracy for at least one model on the unmodified benchmark
    before running any tone conditions")."""
    tracker = SpendTracker(out_dir / "raw" / "study2_validation_gate.jsonl", phase="validation_gate", cap_usd=10.0)
    n_passed = 0
    for task in tasks:
        workdir = out_dir / "scratch" / "validation_gate" / task.task_id
        input_path = task.input_spreadsheet_paths[0]
        traj = run_react_multi_round(
            tracker, model, task.task_id, task.instruction, input_path, workdir,
            tone_level="none", trial=0, max_turns=max_turns,
        )
        grade = _grade_trajectory(grader, task, traj, workdir)
        n_passed += int(grade.passed)
    tracker.close()

    observed = n_passed / len(tasks) if tasks else float("nan")
    return {
        "model_key": model.key,
        "n_tasks": len(tasks),
        "n_passed": n_passed,
        "observed_accuracy": observed,
        "expected_accuracy": expected_accuracy,
        "tolerance": tolerance,
        "passed": expected_accuracy is not None and abs(observed - expected_accuracy) <= tolerance,
        "spend_usd": tracker.total_usd,
    }


def _has_formula(path: Optional[Path]) -> bool:
    if path is None or not Path(path).exists():
        return False
    try:
        wb = openpyxl.load_workbook(path, data_only=False)
        for row in wb.active.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    return True
    except Exception:
        return False
    return False


def run_condition_batch(
    models: list[ModelConfig],
    tasks: list[SpreadsheetTask],
    grader: SpreadsheetBenchGrader,
    out_dir: Path,
    phase: str,
    budget_cap_usd: float,
    n_trials: int = 3,
    multi_round: bool = True,
    max_turns: int = 6,
) -> list[dict]:
    """Runs every (model, task, tone, trial) combination, grades each, and
    returns one flat record per trajectory ready for study2/analysis.py.
    Only the instruction is wrapped -- task.instruction is passed through
    the tone wrapper, everything else about the task is untouched."""
    tracker = SpendTracker(out_dir / "raw" / f"study2_{phase}.jsonl", phase=phase, cap_usd=budget_cap_usd)
    records: list[dict] = []
    try:
        for model in models:
            for task in tasks:
                for tone_key in TONE_ORDER:
                    wrapper = TONE_WRAPPERS[tone_key]
                    wrapped_instruction = wrapper.apply(task.instruction)
                    for trial in range(n_trials):
                        workdir = out_dir / "scratch" / phase / model.key / tone_key / f"{task.task_id}_t{trial}"
                        input_path = task.input_spreadsheet_paths[0]
                        run_fn = run_react_multi_round if multi_round else run_single_round
                        kwargs = dict(max_turns=max_turns) if multi_round else {}
                        traj = run_fn(
                            tracker, model, task.task_id, wrapped_instruction, input_path, workdir,
                            tone_level=tone_key, trial=trial, **kwargs,
                        )
                        grade = _grade_trajectory(grader, task, traj, workdir)
                        expected_uses_formula = _has_formula(task.answer_spreadsheet_paths[0]) if task.answer_spreadsheet_paths else False
                        behavior = score_trajectory(traj.code_snippets_in_order)
                        severity = classify_failure(
                            passed=grade.passed,
                            output_loaded_ok=traj.final_output_path is not None,
                            hit_turn_limit=traj.hit_turn_limit,
                            inspected_before_acting=behavior.inspected_before_acting,
                            expected_uses_formula=expected_uses_formula,
                            output_has_formula=_has_formula(traj.final_output_path),
                            grader_stdout="; ".join(grade.per_test_case_messages),
                        )
                        total_tokens = sum(r.prompt_tokens + r.completion_tokens + r.reasoning_tokens for r in traj.result_rows)
                        total_cost = sum(r.cost_usd for r in traj.result_rows)
                        records.append(
                            {
                                "model_key": model.key,
                                "task_id": task.task_id,
                                "instruction_type": task.instruction_type,
                                "tone_level": tone_key,
                                "trial": trial,
                                "passed": grade.passed,
                                "soft_restriction": grade.soft_restriction,
                                "refused": traj.refused,
                                "severity": severity.category,
                                "severity_detail": severity.detail,
                                "inspected_before_acting": behavior.inspected_before_acting,
                                "self_checked_output": behavior.self_checked_output,
                                "took_destructive_action": behavior.took_destructive_action,
                                "destructive_action_had_backup": behavior.destructive_action_had_backup,
                                "n_turns": behavior.n_code_turns,
                                "cost_usd": total_cost,
                                "total_tokens": total_tokens,
                            }
                        )
                        append_spend_log(
                            out_dir / "spend_log.jsonl",
                            {"phase": phase, "cumulative_usd": tracker.total_usd, "n_calls": tracker.n_calls},
                        )
    finally:
        tracker.close()
    (out_dir / "analysis" / f"study2_{phase}_records.json").parent.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "analysis" / f"study2_{phase}_records.json", "w") as fh:
        json.dump(records, fh, indent=2, default=str)
    return records
