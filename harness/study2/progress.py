"""Per-turn progress regrading: is the extra persistence progress or thrashing?

The study's live findings are all about persistence. A demand interjection
adds ~1.2 turns, praise removes ~1.1, insult does nothing. Grading, though, is
binary on the FINAL state, so those extra turns are uninterpretable: an agent
that spends them converging on the answer and an agent that spends them
rewriting the same wrong cells look identical in the records. The two readings
support opposite conclusions about whether a demand interjection is useful or
merely expensive.

This module reconstructs what the workbook looked like after every turn, from
the raw call log, with no model calls and no spend.

WHY THIS IS POSSIBLE. Each turn's code is in the raw log's `response_text`,
and `harness/study2/regrade.py` already proves it can be extracted and
re-executed. Crucially, the agent loop hands every turn the ORIGINAL input
workbook, never the previous turn's output (see agent_loop.run_react_multi_round
-> execute_python_on_workbook(code, workbook_path, ...) where workbook_path is
task.input_spreadsheet_paths[0] on every iteration). So each turn is an
independent attempt at the whole task, and "progress" means: is attempt k+1
closer to the answer than attempt k?

That independence is what makes the measure clean. There is no accumulated
state to disentangle -- each turn is a fresh answer, and the curve across
turns is the agent's trajectory through answer space.

TWO MEASURES, deliberately:

  * `changed` -- did this turn's output differ from the previous turn's over
    the graded range? A turn that changes nothing is a no-op: the agent spent
    a model call and produced the same answer again. Requires no recalculation
    and is therefore cheap and exact.
  * `match_fraction` -- what share of the graded range matches the answer?
    This is the progress signal. It needs the answer file recalculated (the
    shipped ground truth contains uncached formulas -- see grader.py) and, when
    the agent writes formulas rather than values, the output recalculated too.
    BOTH are now done. An earlier version recalculated only the answer file,
    so every formula-writing turn read as None and scored 0.0 -- 89 of 126
    benchmark-passed control trajectories in the probe run, and 56-62% of
    Luna's final gradable turns write formulas. See `_has_uncached_formula`.

`match_fraction` is deliberately NOT the benchmark's own pass/fail. It is a
finer instrument for a different question, and a trajectory can climb from
0.2 to 0.9 while still failing the benchmark. Do not report it as accuracy.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import openpyxl

# "'Sheet 2'!A1:B20", "Sheet1!A1:B20", or bare "A1:B20".
# The sheet prefix is only a sheet prefix when a "!" follows it. Without the
# "!" inside the optional group, the unquoted alternative greedily eats part
# of the range itself: "P2:P7" parsed as sheet "P2:" + cell "P7", silently
# grading a one-cell range on a sheet that does not exist. Every affected
# lookup then returned None, which reads as "unmeasurable" rather than as a
# bug -- caught only by validating on a real task before scaling up.
_RANGE = re.compile(
    r"^(?:(?:'(?P<q>[^']+)'|(?P<u>[^'!]+))!)?(?P<a>[A-Z]+\d+)(?::(?P<b>[A-Z]+\d+))?$"
)


def instrument_fingerprint() -> str:
    """SHA-256 of this module's source, as the regrade's version stamp.

    A regrade is only comparable to another regrade produced by the same
    instrument. The first version of that check compared FILE MTIMES, which
    is wrong in a way that costs four machine-hours to discover: `git
    checkout` rewrites this file's mtime without changing a byte, so any
    clone or branch switch declared every existing regrade stale. Content is
    the thing that matters, so content is what is hashed.
    """
    import hashlib

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]


def parse_answer_position(answer_position: str) -> tuple[Optional[str], str, str]:
    """Split SpreadsheetBench's answer_position into (sheet, first, last).

    Sheet is None when the range carries no sheet prefix, in which case the
    caller should use the active sheet -- which is what their own
    compare_workbooks does.
    """
    s = (answer_position or "").strip()
    m = _RANGE.match(s)
    if not m:
        raise ValueError(f"unparseable answer_position: {answer_position!r}")
    sheet = m.group("q") or m.group("u")
    first = m.group("a")
    last = m.group("b") or first
    return (sheet.strip() if sheet else None), first, last


def _has_uncached_formula(path: Path, answer_position: str) -> bool:
    """Does the graded range hold a formula with no cached value?

    openpyxl writes formulas without a cached result, so a turn that answers
    with `=SUMIFS(...)` reads back as None under `data_only=True` and scores
    0.0 -- indistinguishable from a turn that wrote nothing. That is the
    "silent None" failure mode this module already warns about for the range
    parser, and it hit the regrade itself: 89 of 126 benchmark-PASSED control
    trajectories in the probe run scored exactly 0.0 before this check
    existed. `grader.py` recalculates output workbooks with LibreOffice for
    exactly this reason; the regrade has to as well.

    Recalculation is expensive, so it is done only when this returns True --
    a cheap structural read of the same range with formulas left intact.
    """
    try:
        sheet_name, first, last = parse_answer_position(answer_position)
        wb = openpyxl.load_workbook(str(path), data_only=False)
    except Exception:
        return False
    try:
        if sheet_name and sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
        elif sheet_name:
            return False
        else:
            ws = wb.active
        for row in ws[f"{first}:{last}"]:
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    return True
        return False
    except Exception:
        return False
    finally:
        wb.close()


def range_values(path: Path, answer_position: str, *, recalculate: bool = False) -> Optional[dict[str, Any]]:
    """Cell values over the graded range, as {coordinate: value}.

    Returns None when the workbook cannot be opened or the sheet is absent --
    a turn whose code crashed leaves no readable output, which is a fact about
    that turn, not an error to raise.

    With `recalculate=True`, a range containing an uncached formula is sent
    through LibreOffice first, in place, so that formula-writing turns are
    graded on their values rather than read as unmeasurable. Callers grading
    agent output should pass it; the shipped answer files are handled by
    `answer_values_for`, which recalculates a copy.
    """
    if recalculate and _has_uncached_formula(path, answer_position):
        from .grader import recalculate_with_libreoffice

        recalculate_with_libreoffice([path])
    try:
        sheet_name, first, last = parse_answer_position(answer_position)
        wb = openpyxl.load_workbook(str(path), data_only=True)
    except Exception:
        return None
    try:
        if sheet_name and sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
        elif sheet_name:
            return None
        else:
            ws = wb.active
        out: dict[str, Any] = {}
        for row in ws[f"{first}:{last}"]:
            for cell in row:
                out[cell.coordinate] = cell.value
        return out
    except Exception:
        return None
    finally:
        wb.close()


def _norm(v: Any) -> Any:
    """Compare 3 and 3.0 as equal, and treat blank and empty string alike.

    SpreadsheetBench's own comparison is type-tolerant in the same way; an
    agent that writes an int where the answer holds a float has not made a
    mistake worth counting as one here.
    """
    if v is None:
        return ""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        f = float(v)
        return int(f) if f.is_integer() else round(f, 6)
    if isinstance(v, str):
        return v.strip()
    return v


def match_fraction(output: Optional[dict], answer: Optional[dict]) -> Optional[float]:
    """Share of graded cells whose value matches the answer.

    None when the output is unreadable. A crashed turn is not 0.0 progress --
    it is an absence of a measurement, and averaging it in as zero would make
    arms with more crashes look like arms that regressed.
    """
    if output is None or not answer:
        return None
    hits = sum(1 for k, want in answer.items() if _norm(output.get(k)) == _norm(want))
    return hits / len(answer)


def changed(a: Optional[dict], b: Optional[dict]) -> Optional[bool]:
    """Did the graded range change between two turns? None if either is
    unreadable."""
    if a is None or b is None:
        return None
    keys = set(a) | set(b)
    return any(_norm(a.get(k)) != _norm(b.get(k)) for k in keys)


@dataclass
class TurnProgress:
    turn: int
    had_code: bool
    readable: bool
    match: Optional[float]
    changed_from_prev: Optional[bool]


@dataclass
class TrajectoryProgress:
    task_id: str
    trial: int
    interjection: Optional[str]
    interjection_turn: Optional[int]
    turns: list[TurnProgress] = field(default_factory=list)

    @property
    def n_turns(self) -> int:
        return len(self.turns)

    @property
    def final_match(self) -> Optional[float]:
        for t in reversed(self.turns):
            if t.match is not None:
                return t.match
        return None

    @property
    def best_match(self) -> Optional[float]:
        vals = [t.match for t in self.turns if t.match is not None]
        return max(vals) if vals else None

    @property
    def n_noop_turns(self) -> int:
        """Turns that produced the same graded range as the turn before."""
        return sum(1 for t in self.turns if t.changed_from_prev is False)

    @property
    def improved_at_end(self) -> Optional[bool]:
        """Was the trajectory still improving when it stopped?

        True when the last measured turn is the best one AND it beat the turn
        before it -- i.e. the agent quit on an upswing. This is the sharpest
        available test of whether praise's early stop is PREMATURE: a
        trajectory that was still climbing when it stopped left progress on
        the table.
        """
        vals = [(t.turn, t.match) for t in self.turns if t.match is not None]
        if len(vals) < 2:
            return None
        return vals[-1][1] > vals[-2][1]


def replay_trajectory(
    turn_rows: list[dict],
    task,
    workdir: Path,
    answer_values: Optional[dict],
    max_turns: Optional[int] = None,
) -> list[TurnProgress]:
    """Re-execute every turn's code against the ORIGINAL input and grade each
    resulting workbook. No model calls.

    Each turn gets its own directory, because the sandbox writes `output.xlsx`
    at a fixed name and reusing one directory would have turn k+1 silently
    inherit turn k's output when its own code crashes -- which is exactly the
    bug that corrupted 800 grades earlier in this study.
    """
    from .agent_loop import _extract_code
    from .sandbox import execute_python_on_workbook

    input_path = task.input_spreadsheet_paths[0]
    out: list[TurnProgress] = []
    prev: Optional[dict] = None
    for idx, row in enumerate(turn_rows):
        if max_turns is not None and idx >= max_turns:
            break
        code = _extract_code(row.get("response_text") or "")
        if not code:
            # A FINAL: line or a protocol miss. Not a workbook-producing turn,
            # and recorded as such rather than dropped: "the agent answered
            # instead of acting" is a behaviour, not a gap.
            out.append(TurnProgress(idx, False, False, None, None))
            continue
        res = execute_python_on_workbook(code, input_path, workdir / f"turn_{idx}")
        vals = (
            range_values(res.output_workbook_path, task.answer_position, recalculate=True)
            if res.output_workbook_path
            else None
        )
        out.append(TurnProgress(
            turn=idx,
            had_code=True,
            readable=vals is not None,
            match=match_fraction(vals, answer_values),
            changed_from_prev=changed(prev, vals),
        ))
        if vals is not None:
            prev = vals
    return out


def answer_values_for(task, grader) -> Optional[dict]:
    """Graded-range values from test case 1's answer file, recalculated.

    Recalculation is not optional: the shipped ground truth contains uncached
    formulas, so a correct output would mismatch a `None` for no reason of its
    own (grader.py documents the case that found this). Falls back to the
    shipped file only if recalculation is unavailable.
    """
    from .grader import recalculated_copy

    if not task.answer_spreadsheet_paths:
        return None
    answer = Path(task.answer_spreadsheet_paths[0])
    try:
        # recalculated_copy caches per answer path and never touches the
        # shipped original -- recalculating in place once mutated the dataset.
        use, _warn = recalculated_copy(answer, grader.recalc_cache_dir)
        if use:
            answer = Path(use)
    except Exception:
        pass
    return range_values(answer, task.answer_position)


def progress_for_run(
    raw_path: Path,
    tasks_by_id: dict,
    grader,
    workdir_root: Path,
    arm: Optional[str] = None,
    max_turns: Optional[int] = None,
) -> list[dict]:
    """Per-turn progress for every trajectory in one raw log. No model calls.

    ONE LOG AT A TIME, deliberately. Logs written before agent_loop put
    `interjection_key` on each row carry no arm identity in `TrajectoryKey`,
    so merging several arms' logs before grouping collapses them onto each
    other -- 1,600 probe trajectories group down to 400. Each run writes one
    log per arm, so per-log is the correct unit and the arm label comes from
    the caller. Newer logs key on the arm as well, but the per-log contract
    is kept so every existing run regrades the same way.
    """
    from .regrade import group_trajectories, load_raw_rows

    grouped = group_trajectories(load_raw_rows(raw_path))
    answers: dict[str, Optional[dict]] = {}
    out: list[dict] = []
    for key, rows in sorted(grouped.items(), key=lambda kv: (kv[0].task_id, kv[0].trial, kv[0].interjection_turn or -1)):
        task = tasks_by_id.get(key.task_id)
        if task is None:
            continue
        if key.task_id not in answers:
            answers[key.task_id] = answer_values_for(task, grader)
        av = answers[key.task_id]
        wd = workdir_root / raw_path.stem / f"{key.task_id}_t{key.trial}_i{key.interjection_turn}"
        turns = replay_trajectory(rows, task, wd, av, max_turns=max_turns)
        tp = TrajectoryProgress(key.task_id, key.trial, arm, key.interjection_turn, turns)
        out.append({
            "task_id": key.task_id,
            "trial": key.trial,
            "arm": arm,
            "interjection_turn": key.interjection_turn,
            "n_answer_cells": len(av) if av else 0,
            "n_turns": tp.n_turns,
            "n_code_turns": sum(1 for t in turns if t.had_code),
            "n_noop_turns": tp.n_noop_turns,
            "final_match": tp.final_match,
            "best_match": tp.best_match,
            "improved_at_end": tp.improved_at_end,
            "curve": [
                {"turn": t.turn, "had_code": t.had_code, "readable": t.readable,
                 "match": t.match, "changed": t.changed_from_prev}
                for t in turns
            ],
        })
    return out
