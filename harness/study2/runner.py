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
import shutil
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


def no_op_passes(grader: SpreadsheetBenchGrader, task: SpreadsheetTask, workdir: Path) -> bool:
    """Does this task pass when the agent does NOTHING -- i.e. when each
    input workbook is handed back unmodified?

    Some SpreadsheetBench tasks grade a cell range that already holds the
    expected values in the input, so a copy scores a full pass. Measured
    over the first 40 tasks of the 200-task sample: 4 of them (10%) are
    free this way. That is survivable spread across a large run, but the
    gate takes the first 5 tasks in file order, and 2 of those 5 happen to
    be free -- so a model that does nothing scores 2/5, exactly what three
    of the four roster models scored.

    An accuracy number is uninterpretable without this comparison, so the
    gate reports it alongside every result rather than silently dropping
    the tasks: dropping them would quietly redefine which benchmark subset
    is being run, and the point here is to make the baseline legible, not
    to make the number look better.
    """
    outputs: list[Optional[Path]] = []
    for idx, src in enumerate(task.input_spreadsheet_paths, start=1):
        dst = workdir / f"no_op_case{idx}{src.suffix}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        outputs.append(dst)
    return grader.evaluate_task(
        task.task_id, task.instruction_type, task.answer_position,
        outputs, task.answer_spreadsheet_paths,
    ).passed


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
    max_turns: int = 10,
    check_no_op: bool = True,
) -> dict:
    """Run the unmodified benchmark instruction (no tone wrapper) through
    the multi-round agent and grade with the authors' own evaluator, before
    any wrapper-condition spend happens (task spec: "Reproduce the published
    baseline accuracy for at least one model on the unmodified benchmark
    before running any tone conditions")."""
    tracker = SpendTracker(out_dir / "raw" / "study2_validation_gate.jsonl", phase="validation_gate", cap_usd=10.0)
    n_passed = 0
    per_task: list[dict] = []
    for task in tasks:
        # model.key is in the path because otherwise a second model's gate run
        # overwrites the first's outputs -- the scores stay correct (each task
        # is graded before the next model runs) but every artifact needed to
        # explain them is destroyed.
        workdir = out_dir / "scratch" / "validation_gate" / model.key / task.task_id
        input_path = task.input_spreadsheet_paths[0]
        traj = run_react_multi_round(
            tracker, model, task.task_id, task.instruction, input_path, workdir,
            tone_level="none", trial=0, max_turns=max_turns,
        )
        grade = _grade_trajectory(grader, task, traj, workdir)
        n_passed += int(grade.passed)
        free = no_op_passes(grader, task, workdir / "_no_op") if check_no_op else None
        # Which tasks failed, not just how many: an aggregate alone can't
        # distinguish "these models have similar overall skill" from "every
        # model fails the same two tasks", and those imply very different
        # things about the roster, the task sample, and the grader.
        per_task.append(
            {
                "task_id": task.task_id,
                "instruction_type": task.instruction_type,
                "passed": grade.passed,
                "no_op_passes": free,  # True => this task is passed by doing nothing
                "beat_no_op": (grade.passed and not free) if free is not None else None,
                "soft_restriction": grade.soft_restriction,
                "n_test_cases_passed": grade.n_test_cases_passed,
                "n_test_cases": grade.n_test_cases,
                "hit_turn_limit": traj.hit_turn_limit,
                "n_turns": len(traj.steps),
                "error": grade.error,
                "turn_diagnostics": _turn_diagnostics(traj),
            }
        )
    tracker.close()

    observed = n_passed / len(tasks) if tasks else float("nan")
    result = {
        "model_key": model.key,
        "n_tasks": len(tasks),
        "n_passed": n_passed,
        "observed_accuracy": observed,
        "expected_accuracy": expected_accuracy,
        "tolerance": tolerance,
        "passed": expected_accuracy is not None and abs(observed - expected_accuracy) <= tolerance,
        "spend_usd": tracker.total_usd,
        "per_task": per_task,
    }
    if check_no_op:
        # The floor this accuracy has to be read against. n_passed alone is
        # not a capability measure when some tasks pass without any work:
        # on the gate's default 5 tasks the no-op floor is 2/5, which is
        # exactly what three of the four roster models scored.
        n_free = sum(1 for t in per_task if t["no_op_passes"])
        n_beat = sum(1 for t in per_task if t["beat_no_op"])
        result.update(
            {
                "no_op_n_passed": n_free,
                "no_op_accuracy": n_free / len(tasks) if tasks else float("nan"),
                "n_discriminating_tasks": len(tasks) - n_free,
                "n_passed_beating_no_op": n_beat,
                "free_task_ids": [t["task_id"] for t in per_task if t["no_op_passes"]],
            }
        )
    return result


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


# Truncated from the END: a Python traceback puts the actual exception type
# and message on its last line, which is exactly the part worth keeping.
_DIAG_TRUNCATE_CHARS = 800


def _turn_diagnostics(traj: Trajectory) -> list[dict]:
    """Per-turn execution outcome, persisted into the records file so a
    failed trajectory can be diagnosed without re-running it.

    Without this, the stdout/stderr the model actually saw exists only in
    the in-memory Trajectory and is discarded when the process exits --
    which is how two separate live investigations (Luna's 0/5 gate,
    DeepSeek's 0/7 pilot) both ended up unable to explain *why* the
    generated code never produced an output file without paying for the
    whole run a second time. The sandbox itself was verified healthy
    (openpyxl and pandas both import, load, and save correctly under its
    resource limits), so the answer has to be in these streams.
    """
    return [
        {
            "turn": s.turn,
            "had_code": s.code is not None,
            "stdout": s.stdout[-_DIAG_TRUNCATE_CHARS:],
            "stderr": s.stderr[-_DIAG_TRUNCATE_CHARS:],
        }
        for s in traj.steps
    ]


def run_condition_batch(
    models: list[ModelConfig],
    tasks: list[SpreadsheetTask],
    grader: SpreadsheetBenchGrader,
    out_dir: Path,
    phase: str,
    budget_cap_usd: float,
    n_trials: int = 3,
    multi_round: bool = True,
    max_turns: int = 10,
) -> list[dict]:
    """Runs every (model, task, tone, trial) combination, grades each, and
    returns one flat record per trajectory ready for study2/analysis.py.
    Only the instruction is wrapped -- task.instruction is passed through
    the tone wrapper, everything else about the task is untouched.

    Loop order is deliberately model -> task -> tone -> trial (README "The
    thinking arm"'s design section: "task-outer, tone-inner"): for a fixed
    model and task, all 7 tones x n_trials calls happen back to back, so
    repeated calls sharing a prompt structure (same task, same system
    prompt, differing only in tone-wrapper prefix or, within one (task,
    tone) pair across trials, byte-identical prompts) stay close together
    in time rather than being spread across the whole batch -- closer
    together means more likely to land inside a provider's prompt-cache
    retention window. Do not reorder this to model -> tone -> task or
    similar without re-reading that section.
    """
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
                                "turn_diagnostics": _turn_diagnostics(traj),
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
