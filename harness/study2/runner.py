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

import contextlib
import hashlib
import json
import os
import random
import shutil
from pathlib import Path
from typing import Optional

import openpyxl

from ..providers.base import ModelConfig
from ..spend_tracker import BudgetExceeded, SpendTracker, append_spend_log
from ..tone_wrappers import INTERJECTIONS, TONE_ORDER, TONE_WRAPPERS, WRAPPER_SET_VERSION
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
    # Whether a task is free is a property of the benchmark, not of a run, so
    # the verdict is cached on disk. Without this the check re-copies and
    # re-grades 3 workbooks per task on every run -- measured at roughly a
    # third of wall-clock time for the fast models, and ~23 min per model at
    # n=100. Keyed by the input files' size+mtime so a re-extracted or updated
    # dataset re-checks instead of trusting a stale verdict.
    cache_file = Path(grader.recalc_cache_dir) / "no_op_verdicts.json"
    try:
        fingerprint = hashlib.sha256(
            "|".join(
                f"{p}:{p.stat().st_size}:{p.stat().st_mtime_ns}"
                for p in task.input_spreadsheet_paths
            ).encode()
        ).hexdigest()[:20]
    except OSError:
        fingerprint = None

    cache: dict[str, dict] = {}
    if fingerprint and cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text())
        except (json.JSONDecodeError, OSError):
            cache = {}
        hit = cache.get(task.task_id)
        if isinstance(hit, dict) and hit.get("fingerprint") == fingerprint:
            return bool(hit["passed"])

    outputs: list[Optional[Path]] = []
    for idx, src in enumerate(task.input_spreadsheet_paths, start=1):
        dst = workdir / f"no_op_case{idx}{src.suffix}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        outputs.append(dst)
    passed = grader.evaluate_task(
        task.task_id, task.instruction_type, task.answer_position,
        outputs, task.answer_spreadsheet_paths,
    ).passed

    if fingerprint:
        try:
            cache[task.task_id] = {"fingerprint": fingerprint, "passed": bool(passed)}
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(cache, indent=2, sort_keys=True))
        except OSError:
            pass  # a cache that cannot be written must not fail the run
    return passed


FREE_TASKS_MANIFEST = Path(__file__).parent / "free_tasks.json"

# Below this, the gate's own tolerance is finer than the sample can resolve:
# with n tasks the observed accuracy can only land on multiples of 1/n, so a
# 0.08 tolerance against a 5-task sample (steps of 0.20) is decided by
# rounding rather than by the model. See select_gate_tasks' docstring.
MIN_USEFUL_GATE_TASKS = 20

# Turns at which a mid-task interjection may land. Turn 0's response is the
# model's first attempt, so the earliest an interruption can reach it is the
# observation after that -- turn 1. Capped at 2 because the median trajectory
# is 3.3 turns: a later injection would simply never fire on most of them, and
# an arm whose treatment silently misses half its trajectories is not an arm.
INTERJECTION_TURNS = (1, 2)


def load_free_task_ids(manifest: Path = FREE_TASKS_MANIFEST) -> set[str]:
    """Task ids known to pass when the agent does nothing -- see the
    manifest's own _comment. A cache, not a source of truth: the gate
    re-checks every task it runs."""
    if not manifest.exists():
        return set()
    return set(json.loads(manifest.read_text()).get("free_task_ids", []))


def select_gate_tasks(
    tasks: list[SpreadsheetTask],
    n: int,
    seed: int = 0,
    free_ids: Optional[set[str]] = None,
) -> list[SpreadsheetTask]:
    """Choose `n` tasks for the validation gate: only tasks that actually
    discriminate, stratified by instruction type, deterministic for a given
    seed.

    Three things this fixes about taking the first `n` tasks in file order:

    1. File order is not a sample. The first 5 tasks happened to include 2
       of the 17 (8.5%) tasks in the 200-task set that pass when the agent
       does nothing -- a 40% no-op floor against an 8.5% base rate, which
       is why three roster models "scored" exactly what doing nothing
       scores.
    2. Instruction types are not evenly free. 14% of Sheet-Level tasks are
       free versus 5% of Cell-Level, so an unstratified draw skews the
       floor as well as the difficulty.
    3. The gate compares observed accuracy to an expected value within a
       tolerance (default 0.08), but an n-task sample can only produce
       multiples of 1/n. At n=5 the steps are 0.20, so that comparison is
       decided by rounding. n >= MIN_USEFUL_GATE_TASKS keeps the step size
       at or below the tolerance.

    Selection is seeded so a gate result is reproducible: the same seed and
    dataset always yield the same tasks, which is what makes an
    --expected-accuracy value meaningful across runs.
    """
    free = load_free_task_ids() if free_ids is None else free_ids
    eligible = [t for t in tasks if t.task_id not in free]
    if not eligible:
        return []

    by_type: dict[str, list[SpreadsheetTask]] = {}
    for t in eligible:
        by_type.setdefault(t.instruction_type, []).append(t)

    rng = random.Random(seed)
    for group in by_type.values():
        rng.shuffle(group)

    # Largest-remainder allocation, so the sample keeps the dataset's own
    # instruction-type proportions instead of over-weighting whichever type
    # happens to sort first.
    total = len(eligible)
    quotas: dict[str, int] = {}
    remainders: list[tuple[float, str]] = []
    for itype, group in by_type.items():
        exact = n * len(group) / total
        quotas[itype] = min(len(group), int(exact))
        remainders.append((exact - int(exact), itype))
    for _, itype in sorted(remainders, reverse=True):
        if sum(quotas.values()) >= min(n, total):
            break
        if quotas[itype] < len(by_type[itype]):
            quotas[itype] += 1

    selected: list[SpreadsheetTask] = []
    for itype, count in quotas.items():
        selected.extend(by_type[itype][:count])
    # Stable, dataset-order output so logs and per-task tables read the same
    # way regardless of how the draw shuffled things.
    order = {t.task_id: i for i, t in enumerate(tasks)}
    return sorted(selected, key=lambda t: order[t.task_id])


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
    # Per model, like the scratch dir and the report. SpendTracker resumes its
    # running total from this file, so a shared one makes every concurrently
    # gating model count all the others' spend against its own $10 cap and
    # halt early -- the same failure the core path's per-run tags exist to
    # prevent, on the one phase that runs four models at once by design.
    tracker = SpendTracker(
        out_dir / "raw" / f"study2_validation_gate_{_run_tag([model])}.jsonl",
        phase="validation_gate",
        cap_usd=10.0,
    )
    n_passed = 0
    per_task: list[dict] = []
    for task in tasks:
        # model.key is in the path because otherwise a second model's gate run
        # overwrites the first's outputs -- the scores stay correct (each task
        # is graded before the next model runs) but every artifact needed to
        # explain them is destroyed.
        workdir = out_dir / "scratch" / "validation_gate" / model.key / task.task_id
        input_path = task.input_spreadsheet_paths[0]
        # One task must not be able to discard the whole run. A single
        # ProviderError used to propagate out and lose every completed task
        # with it (Qwen's gate died this way on task 1 of 5, twice). Over 200
        # tasks -- or over a paid run -- that turns a recoverable hiccup into
        # a total loss of work already paid for. BudgetExceeded is deliberately
        # NOT caught: that is a stop signal, not a task-level failure.
        try:
            traj = run_react_multi_round(
                tracker, model, task.task_id, task.instruction, input_path, workdir,
                tone_level="none", trial=0, max_turns=max_turns,
            )
            grade = _grade_trajectory(grader, task, traj, workdir)
            free = no_op_passes(grader, task, workdir / "_no_op") if check_no_op else None
        except BudgetExceeded:
            raise
        except Exception as exc:  # noqa: BLE001 -- deliberately broad; see above
            print(f"  ERROR on task {task.task_id}: {type(exc).__name__}: {exc}"[:300])
            per_task.append(
                {
                    "task_id": task.task_id,
                    "instruction_type": task.instruction_type,
                    "passed": False,
                    "no_op_passes": None,
                    "beat_no_op": None,
                    "soft_restriction": 0.0,
                    "n_test_cases_passed": 0,
                    "n_test_cases": len(task.answer_spreadsheet_paths),
                    "hit_turn_limit": False,
                    "n_turns": 0,
                    "error": f"{type(exc).__name__}: {exc}"[:500],
                    "crashed": True,
                    "turn_diagnostics": [],
                }
            )
            continue
        n_passed += int(grade.passed)
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
                "crashed": False,
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
        "n_crashed": sum(1 for t in per_task if t.get("crashed")),
        "crashed_task_ids": [t["task_id"] for t in per_task if t.get("crashed")],
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


def _write_records(out_dir: Path, phase: str, records: list[dict], tag: str) -> None:
    """Write the graded records to disk. Called from a finally block, so it
    must not raise: losing the records to a secondary failure while handling
    the primary one would defeat the point."""
    try:
        path = out_dir / "analysis" / f"study2_{phase}_{tag}_records.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            json.dump(records, fh, indent=2, default=str)
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: could not write {phase} records: {type(exc).__name__}: {exc}")


def _append_record(out_dir: Path, phase: str, record: dict, tag: str) -> None:
    """Append one graded record as it is produced.

    The end-of-run JSON is the artifact analysis reads, but it only exists
    once the loop is over. A long core run is thousands of trajectories and
    real money; if the process dies (OOM, container reclaim, SIGKILL -- none
    of which run a finally block) everything graded so far is gone. This
    append-only line-per-record file is the durable copy.
    """
    try:
        path = out_dir / "analysis" / f"study2_{phase}_{tag}_records.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
            fh.flush()
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: could not append {phase} record: {type(exc).__name__}: {exc}")


def _run_tag(models: list[ModelConfig], run_label: Optional[str] = None) -> str:
    """Filename suffix identifying which models a run covers.

    Every per-phase artifact -- the raw call log, the records JSON, the
    incremental JSONL -- used to be named by phase alone. That is fine for one
    process, and silently destructive for four: running the four roster models
    as concurrent `core` processes (the obvious way to cut a 95-hour sequential
    run down to ~16) would have had them overwrite each other's records,
    interleave one raw log, and -- worst -- each SpendTracker resumes its total
    from that shared log, so every model would count all four models' spend
    against its own cap and halt early.

    A single-model process gets its own key, so the parallel case is safe
    without anyone having to remember a flag. Multi-model runs in one process
    keep sharing a file, which is correct: they genuinely are one run, and one
    tracker enforcing one cap across them is the intended behaviour.

    Dry runs get their own namespace. --dry-run forces every model onto the
    mock provider but wrote to the same filenames as a live run, so a dry run
    started to check a flag appends fabricated rows to the live spend log and
    the live records. That is not hypothetical: a mock `core` invocation left
    48 mock rows in `study2_core_gpt-luna.jsonl`, which the next live run then
    resumed its budget from and would have analysed alongside real ones.
    """
    tag = models[0].key if len(models) == 1 else "multi"
    if any(m.provider == "mock" for m in models):
        tag = f"{tag}-dryrun"
    if run_label:
        tag = f"{tag}-{run_label}"
    return tag


class RunAlreadyInProgress(RuntimeError):
    """Another live process is already writing this phase+model's files."""


@contextlib.contextmanager
def _exclusive_run(out_dir: Path, phase: str, tag: str):
    """Refuse to start when another process is already writing these files.

    Namespacing per model stopped different models colliding. It does
    nothing about the *same* model twice, which is the case that actually
    happened: a container restart was reported, a resumed run was started --
    and the original process had not died at all. Both appended to the same
    records file for half an hour, producing 39 duplicate
    (task, tone, trial) rows that an analysis would have counted as extra
    trials.

    The lock records a pid. A stale lock from a killed process is taken
    over rather than treated as fatal, since that is the normal state after
    a crash and the resume path exists precisely for it.
    """
    lock = out_dir / "locks" / f"study2_{phase}_{tag}.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock.exists():
        try:
            holder = int(lock.read_text().strip())
        except (ValueError, OSError):
            holder = None
        if holder is not None and holder != os.getpid():
            # Only ProcessLookupError means the holder is gone. PermissionError
            # means the opposite -- the process EXISTS, we just may not signal
            # it because it belongs to another user. Catching OSError broadly
            # treated that as dead and took the lock: CI caught exactly this,
            # where the runner is unprivileged and pid 1 is root's, so the
            # guard silently let a second run through. Any other OSError is
            # treated as alive too, because refusing to start is recoverable
            # and two concurrent runs corrupting one records file is not.
            alive = True
            try:
                os.kill(holder, 0)
            except ProcessLookupError:
                alive = False
            except OSError:
                alive = True
            if alive:
                raise RunAlreadyInProgress(
                    f"pid {holder} is already running {phase} for {tag!r} and writing the "
                    f"same files ({lock}). Two live runs append to one records file and "
                    "produce duplicate trajectories. Stop that process, or delete the lock "
                    "if you are certain it is gone."
                )
    lock.write_text(str(os.getpid()))
    try:
        yield
    finally:
        try:
            if lock.exists() and lock.read_text().strip() == str(os.getpid()):
                lock.unlink()
        except OSError:
            pass



def completed_trajectories(out_dir: Path, phase: str, tag: str) -> set[tuple[str, str, int]]:
    """(task_id, tone_level, trial) already graded and durably recorded.

    A core run is ten hours of wall clock, and the container it runs in can
    be restarted out from under it -- which happened at 896 of 1050
    trajectories. The incremental records file survived, so redoing that
    work would have been a choice, not a necessity.

    Reads the append-as-you-go JSONL rather than the final JSON, because the
    final one is only written when the run ends -- exactly the case where
    there isn't one. A torn last line from a process killed mid-write is
    skipped: a partially written record is not evidence the trajectory
    finished.
    """
    path = out_dir / "analysis" / f"study2_{phase}_{tag}_records.jsonl"
    done: set[tuple[str, str, int]] = set()
    if not path.exists():
        return done
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("crashed"):
                # A crashed trajectory is a recorded outcome, not a gap, but
                # it is worth retrying on a resume: the usual cause is a
                # transient provider error rather than anything about the
                # task. Left out of `done` deliberately.
                continue
            try:
                done.add((r["task_id"], r["tone_level"], int(r["trial"])))
            except (KeyError, TypeError, ValueError):
                continue
    return done



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
    tone_seed: int = 0,
    resume: bool = False,
    tones: Optional[list[str]] = None,
    run_label: Optional[str] = None,
    interject: Optional[str] = None,
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
    # A run_label gives a separate namespace to a run that is deliberately NOT
    # part of the main dataset -- re-running one arm against a changed
    # instrument, for instance. Without it such a run lands on the main
    # records file, where --resume would skip every trajectory as already done
    # and a later analysis would pool two incompatible wrapper sets.
    tag = _run_tag(models, run_label)
    exclusive = _exclusive_run(out_dir, phase, tag)
    exclusive.__enter__()
    tracker = SpendTracker(out_dir / "raw" / f"study2_{phase}_{tag}.jsonl", phase=phase, cap_usd=budget_cap_usd)
    already: set[tuple[str, str, int]] = set()
    if resume:
        already = completed_trajectories(out_dir, phase, tag)
        print(
            f"[{phase}] resuming: {len(already)} trajectories already recorded and will be skipped"
        )
    records: list[dict] = []
    # Records from the interrupted run, carried forward so the final JSON is
    # the whole run rather than only the part after the restart. Read once,
    # here, because _append_record keeps appending to the same file.
    if already:
        prior_path = out_dir / "analysis" / f"study2_{phase}_{tag}_records.jsonl"
        with open(prior_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    try:
        for model in models:
            for task in tasks:
                # TONE ORDER IS RANDOMISED PER (model, task), not fixed.
                # Running L1..L7 in the same sequence every time entangles tone
                # with position-in-burst: anything that drifts across seven
                # consecutive calls is perfectly confounded with the
                # manipulation. That is not hypothetical here -- retry backoff
                # accumulates within a burst (Qwen absorbed 12-21 rate-limit
                # 429s per 20-task run), so under a fixed order the last tone
                # would systematically meet worse provider conditions than the
                # first, and the study would read that as a tone effect.
                #
                # This does NOT disturb the task-outer/tone-inner ordering the
                # docstring above defends: all seven tones for a task still run
                # back to back, inside the same prompt-cache window. Only their
                # order within that burst changes. Seeded on (seed, model,
                # task) so a rerun reproduces the same sequence.
                # Shuffle the FULL scale, then filter. Restricting to a
                # subset must not change where the kept tones land in the
                # burst: a single-tone rerun should meet the same position
                # distribution its arm saw in the full run, or it is not
                # comparable to it.
                tone_order = list(TONE_ORDER)
                random.Random(f"{tone_seed}|{model.key}|{task.task_id}").shuffle(tone_order)
                if tones is not None:
                    keep = set(tones)
                    tone_order = [(i, t) for i, t in enumerate(tone_order) if t in keep]
                else:
                    tone_order = list(enumerate(tone_order))
                for tone_position, tone_key in tone_order:
                    wrapper = TONE_WRAPPERS[tone_key]
                    wrapped_instruction = wrapper.apply(task.instruction)
                    for trial in range(n_trials):
                        if (task.task_id, tone_key, trial) in already:
                            continue
                        workdir = out_dir / "scratch" / phase / model.key / tone_key / f"{task.task_id}_t{trial}"
                        input_path = task.input_spreadsheet_paths[0]
                        run_fn = run_react_multi_round if multi_round else run_single_round
                        kwargs = dict(max_turns=max_turns) if multi_round else {}
                        # The mid-task interjection. Its TURN is seeded on
                        # (task, trial) and deliberately NOT on the arm, so
                        # every arm interrupts the same task+trial at the same
                        # point. If the turn varied by arm, turn position would
                        # ride along with the manipulation and the paired
                        # comparison would be measuring both at once.
                        injected_turn = None
                        if interject is not None and multi_round:
                            injected_turn = random.Random(
                                f"interject|{tone_seed}|{model.key}|{task.task_id}|{trial}"
                            ).choice(INTERJECTION_TURNS)
                            kwargs["interjection"] = INTERJECTIONS[interject]
                            kwargs["interjection_turn"] = injected_turn
                        # Same isolation the gate has. This is the PAID path
                        # and had none of it: a single exception anywhere in
                        # 4,200 core-run trajectories propagated out and ended
                        # the run. Not hypothetical -- a ChunkedEncodingError
                        # did exactly that to a 20-task gate, and the gate is
                        # where isolation already existed. BudgetExceeded is
                        # deliberately re-raised: a cap is a stop signal, not a
                        # trajectory-level failure.
                        try:
                            traj = run_fn(
                                tracker, model, task.task_id, wrapped_instruction, input_path, workdir,
                                tone_level=tone_key, trial=trial, **kwargs,
                            )
                            grade = _grade_trajectory(grader, task, traj, workdir)
                        except BudgetExceeded:
                            raise
                        except Exception as exc:  # noqa: BLE001 -- deliberately broad; see above
                            print(
                                f"  ERROR {model.key}/{task.task_id}/{tone_key}/t{trial}: "
                                f"{type(exc).__name__}: {exc}"[:300]
                            )
                            crashed = {
                                "model_key": model.key, "task_id": task.task_id,
                                "instruction_type": task.instruction_type,
                                "tone_level": tone_key, "tone_position": tone_position,
                                "trial": trial, "passed": False, "crashed": True,
                                "error": f"{type(exc).__name__}: {exc}"[:500],
                                "soft_restriction": 0.0, "refused": False,
                                "severity": "other", "severity_detail": "trajectory raised",
                                "n_turns": 0, "cost_usd": 0.0, "total_tokens": 0,
                                "reasoning_tokens": 0,
                                "turn_diagnostics": [],
                            }
                            records.append(crashed)
                            _append_record(out_dir, phase, crashed, tag)
                            continue
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
                        # prompt + completion ONLY. Adding reasoning_tokens
                        # here counted the model's thinking twice: on
                        # OpenAI-style usage (OpenRouter, the route every
                        # model in this roster is served through) reasoning is
                        # reported as completion_tokens_details.reasoning_tokens
                        # -- a breakdown OF completion, not an extra bucket
                        # beside it. Checked against the provider's own figure
                        # on all 4,647 calls of the gpt-luna core run:
                        # usage.total_tokens == prompt_tokens +
                        # completion_tokens on every one, and reasoning never
                        # exceeded completion on any. The old sum ran ~932
                        # tokens per trajectory above the provider's total,
                        # which is just the mean reasoning spend (947) added
                        # back -- so total_tokens, the statistic compared
                        # against the published single-turn figure, was
                        # inflated by roughly the size of the effect being
                        # measured. Providers that really do report reasoning
                        # outside completion (Google) keep the third term via
                        # ProviderResponse.reasoning_tokens_outside_completion.
                        total_tokens = sum(
                            r.prompt_tokens
                            + r.completion_tokens
                            + (0 if r.reasoning_included_in_completion else r.reasoning_tokens)
                            for r in traj.result_rows
                        )
                        # Recorded separately from total_tokens because they
                        # answer different questions. total_tokens is dominated
                        # by the prompt, which the tone wrapper changes by
                        # construction, so a tone difference there is partly
                        # just the wrapper's own length. Reasoning tokens are
                        # what the model chose to spend thinking, which is the
                        # measure a "tone changes how hard it thinks" claim
                        # actually rests on. Measured live on a partial Luna
                        # core run: reasoning spend under the threatening
                        # wrapper ran ~25% above every other tone, which is
                        # invisible in total_tokens.
                        reasoning_tokens = sum(r.reasoning_tokens for r in traj.result_rows)
                        total_cost = sum(r.cost_usd for r in traj.result_rows)
                        record = {
                                "model_key": model.key,
                                "task_id": task.task_id,
                                "instruction_type": task.instruction_type,
                                "tone_level": tone_key,
                                # Where this call fell in its 7-tone burst.
                                # Recorded so the randomisation can be verified
                                # after the fact and a position effect tested
                                # directly, rather than assumed away.
                                "tone_position": tone_position,
                                # Which wrapper set produced this trajectory.
                                # v1 and v2 are different instruments -- v1's
                                # neutral wrapper carried an extra task
                                # instruction and its lengths were unmatched --
                                # so records must never be pooled across them
                                # by accident.
                                "wrapper_set": WRAPPER_SET_VERSION,
                                "interjection": interject,
                                "interjection_turn": injected_turn,
                                "interjection_fired": getattr(traj, "interjection_fired", False),
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
                                "reasoning_tokens": reasoning_tokens,
                                "turn_diagnostics": _turn_diagnostics(traj),
                                "crashed": False,
                        }
                        records.append(record)
                        # Durable copy written as we go -- see _append_record.
                        _append_record(out_dir, phase, record, tag)
                        append_spend_log(
                            out_dir / "spend_log.jsonl",
                            {"phase": phase, "cumulative_usd": tracker.total_usd, "n_calls": tracker.n_calls},
                        )
    finally:
        exclusive.__exit__(None, None, None)
        tracker.close()
        # MUST be inside finally. This used to sit after it, so any exception
        # escaping the loop skipped it entirely -- and the exception that ends
        # a capped run is BudgetExceeded, raised by SpendTracker.record() the
        # moment the cap is reached. That is the EXPECTED termination of a
        # core run, not an edge case: a $150 run ending exactly as designed
        # wrote zero graded records. results/raw/*.jsonl survived, but that
        # holds raw API calls, not grades -- every pass/fail, severity label
        # and behaviour score existed only in this in-memory list.
        _write_records(out_dir, phase, records, tag)
    return records
