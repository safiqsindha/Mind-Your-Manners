"""Re-grade completed runs from their raw per-call log, without calling any model.

WHY THIS EXISTS. Every bug this project has hit falls into one of two kinds:

  * Upstream of the model's input -- the sandbox path bug, where every
    observation the model saw was "can't open file". Unrecoverable: you
    cannot retroactively fix what a model was told, so the trajectories are
    worthless and the money is spent.
  * Downstream of the model's output -- stale-output contamination, models
    graded on each other's files, recalculation aborting on the first
    failure, the grader mutating ground truth. Every one of these leaves the
    model's own work intact and only corrupts the *grading* of it.

The second kind is recoverable for free, because `results/raw/*.jsonl` holds
every response the models produced, written per call and flushed. Nothing in
the harness could read it back, so a grading bug meant re-running and
re-paying. This module closes that gap: it rebuilds each trajectory from the
stored responses, re-executes the code they contain, and re-grades.

Verified feasible before being written: 107 complete trajectories were
reconstructed from 806 raw rows of a live run, with turn ordering and code
blocks intact.

WHAT IT IS NOT. This replays stored responses; it does not re-run the agent
loop. The observations a model saw are whatever it saw at the time, and the
responses are fixed. That is exactly what makes it sound for grading bugs and
useless for input-side bugs -- re-executing the same code against the same
workbook reproduces the same output, which is the thing being graded.
"""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from .agent_loop import Trajectory, TrajectoryStep, _extract_code
from .dataset import SpreadsheetTask
from .sandbox import execute_python_on_workbook


@dataclass(frozen=True)
class TrajectoryKey:
    model_key: str
    task_id: str
    tone_level: str
    trial: int
    # Part of the identity, not an attribute. Under the crossed interjection
    # design one (model, task, tone, trial) is deliberately run once per
    # injection turn, so without this the three runs group into a single
    # trajectory three times as long as any that actually happened, and the
    # regrade grades a thing the model never produced. None for every run
    # made before the field existed, which keys exactly as it used to.
    interjection_turn: Optional[int] = None


def load_raw_rows(path: Path) -> list[dict]:
    """Read a results/raw/*.jsonl log.

    Tolerant of a truncated final line: a process killed mid-write leaves
    one, and refusing to read the other 99.9% of a run because of it would
    defeat the purpose of having the log at all.
    """
    rows: list[dict] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def group_trajectories(rows: Iterable[dict]) -> dict[TrajectoryKey, list[dict]]:
    """Group raw call rows into per-trajectory turn sequences, ordered by turn.

    The turn index lives in `extra.turn` (set by agent_loop._call_and_record).
    Rows missing it sort to the front rather than being dropped -- losing a
    turn silently would change the reconstructed final answer.
    """
    grouped: dict[TrajectoryKey, list[dict]] = defaultdict(list)
    for r in rows:
        key = TrajectoryKey(
            model_key=r.get("model_key", ""),
            task_id=str(r.get("item_id", "")),
            tone_level=r.get("tone_level", "none"),
            trial=int(r.get("trial") or 0),
            interjection_turn=((r.get("extra") or {}).get("interjection_turn")),
        )
        grouped[key].append(r)
    for turns in grouped.values():
        turns.sort(key=lambda r: (r.get("extra") or {}).get("turn", 0))
    return dict(grouped)


def rebuild_trajectory(
    key: TrajectoryKey,
    turns: list[dict],
    workbook_path: Path,
    workdir: Path,
    max_turns: Optional[int] = None,
) -> Trajectory:
    """Replay one trajectory's stored responses, re-executing their code.

    Mirrors run_react_multi_round's bookkeeping deliberately: FINAL ends the
    trajectory, a refusal ends it, the last turn that actually wrote an output
    is the one graded, and running out of turns without a FINAL sets
    hit_turn_limit. If this drifted from that logic, a re-grade would score a
    different answer than the original run did, which would make it worse than
    useless.
    """
    traj = Trajectory(task_id=key.task_id, tone_level=key.tone_level, trial=key.trial)
    emitted_final = False

    for turn_idx, row in enumerate(turns):
        text = row.get("response_text") or ""

        if row.get("refused"):
            traj.refused = True
            traj.steps.append(TrajectoryStep(turn_idx, text, None, "", "", is_final=True))
            emitted_final = True
            break

        if text.strip().upper().startswith("FINAL:"):
            traj.steps.append(TrajectoryStep(turn_idx, text, None, "", "", is_final=True))
            emitted_final = True
            break

        code = _extract_code(text)
        if not code:
            traj.steps.append(TrajectoryStep(turn_idx, text, None, "", "", is_final=False))
            continue

        exec_result = execute_python_on_workbook(code, workbook_path, workdir / f"turn_{turn_idx}")
        traj.steps.append(
            TrajectoryStep(turn_idx, text, code, exec_result.stdout, exec_result.stderr, is_final=False)
        )
        if exec_result.output_workbook_path:
            traj.final_output_path = exec_result.output_workbook_path
            traj.final_code = code

    if not emitted_final:
        # Matches the agent loop's for/else: the budget ran out mid-work.
        # Fall back to the recorded turn count when the original max_turns
        # isn't known, so a full-length trajectory isn't mislabelled.
        limit = max_turns if max_turns is not None else len(turns)
        if len(turns) >= limit:
            traj.hit_turn_limit = True

    return traj


def regrade_run(
    raw_path: Path,
    tasks_by_id: dict[str, SpreadsheetTask],
    grader,
    workdir_root: Path,
    max_turns: Optional[int] = None,
) -> list[dict]:
    """Re-grade every trajectory in a raw log. Makes no model calls.

    Returns one record per trajectory. Tasks absent from `tasks_by_id` are
    reported rather than skipped silently -- a raw log referencing a task the
    caller did not load means the caller loaded the wrong dataset slice, and
    quietly dropping those rows would understate the result.
    """
    from .runner import _grade_trajectory, _turn_diagnostics  # circular at module scope

    grouped = group_trajectories(load_raw_rows(raw_path))
    records: list[dict] = []

    for key, turns in sorted(grouped.items(), key=lambda kv: (kv[0].model_key, kv[0].task_id, kv[0].tone_level, kv[0].trial)):
        task = tasks_by_id.get(key.task_id)
        if task is None:
            records.append(
                {
                    "model_key": key.model_key,
                    "task_id": key.task_id,
                    "tone_level": key.tone_level,
                    "trial": key.trial,
                    "passed": False,
                    "error": "task not found in the loaded dataset -- wrong slice?",
                    "regraded": False,
                }
            )
            continue

        workdir = (
            workdir_root / key.model_key / key.tone_level
            / f"{key.task_id}_t{key.trial}"
            / ("i_none" if key.interjection_turn is None else f"i{key.interjection_turn}")
        )
        traj = rebuild_trajectory(key, turns, task.input_spreadsheet_paths[0], workdir, max_turns)
        grade = _grade_trajectory(grader, task, traj, workdir)
        records.append(
            {
                "model_key": key.model_key,
                "task_id": key.task_id,
                "instruction_type": task.instruction_type,
                "tone_level": key.tone_level,
                "trial": key.trial,
                "interjection_turn": key.interjection_turn,
                "passed": grade.passed,
                "soft_restriction": grade.soft_restriction,
                "n_test_cases_passed": grade.n_test_cases_passed,
                "n_test_cases": grade.n_test_cases,
                "refused": traj.refused,
                "hit_turn_limit": traj.hit_turn_limit,
                "n_turns": len(traj.steps),
                "error": grade.error,
                "recalc_warnings": list(getattr(grade, "recalc_warnings", []) or []),
                "turn_diagnostics": _turn_diagnostics(traj),
                "regraded": True,
            }
        )
    return records
