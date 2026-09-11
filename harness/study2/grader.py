"""Thin wrapper around the SpreadsheetBench authors' own evaluation code.

Task spec: "Use the authors' own evaluation code. Do not reimplement the
grader." This module imports and calls their real `compare_workbooks()`
function (from `evaluation/evaluation.py` in a cloned checkout) rather than
reimplementing cell-comparison logic -- verified against a real clone (see
git history for this file): `compare_workbooks(gt_file, proc_file,
instruction_type, answer_position) -> (bool, str)` does an exact cell-range
comparison, matching numeric/date/string cell values in `answer_position`
(their own syntax, e.g. "H3:H5" or "'Sheet2'!A1:B2,'Sheet3'!C1:C2") between
a ground-truth file and a produced file. Confirmed working:
`compare_workbooks(gt, gt, ...)` returns `(True, "")` and
`compare_workbooks(gt, unmodified_input, ...)` returns `(False, ...)` on a
real sample task.

Their evaluation.py itself is NOT invoked as a CLI/subprocess (an earlier
version of this module assumed a `bash scripts/evaluation.sh` +
DATA_DIR/RESULT_DIR env-var interface that does not exist in the real repo
-- evaluation.py hardcodes `../data/{dataset}/dataset.json` relative to
being run from `evaluation/`, loads the WHOLE dataset, and expects the
model's output already sitting where its (currently commented-out) `outputs/`
path convention says; there's no supported single-task CLI grading path).
Importing their `compare_workbooks` function directly and driving it
ourselves, once per test case, is both truer to "use their own evaluation
code" and the only integration that actually works for a per-task,
per-condition harness like this one.

SpreadsheetBench's OJ-style scoring (confirmed from their evaluation.py) is,
per task: `soft_restriction` = fraction of the 3 test cases passed,
`hard_restriction` = 1 only if all 3 passed else 0. `evaluate_task()` below
reproduces exactly that arithmetic over whatever (output, answer) pairs it's
given -- it does not invent a different scoring rule.

FORMULA CAVEAT (also confirmed against a real clone): `compare_workbooks`
reads cells with `openpyxl.load_workbook(..., data_only=True)`, which only
returns a *cached* computed value for formula cells -- it does NOT evaluate
formulas itself. Their own `open_spreadsheet.py` recalculates files via a
LibreOffice headless conversion before grading, for exactly this reason. A
produced .xlsx with an uncached formula (e.g. one openpyxl just wrote) will
read as a formula string or None under data_only=True and fail comparison
even if the formula is correct -- `recalculate_with_libreoffice()` below
must run first on every produced/output workbook.

Both LibreOffice problems found in this build were fixed after diagnosis,
not assumed away -- see git history for this file:

1. **Missing packages** (fixed by installing them, not a code bug): headless
   conversion failed outright ("Error: source file could not be loaded")
   because `libreoffice-calc`/`libreoffice-writer` were never actually
   installed in this container -- only `libreoffice-core` was (confirmed via
   `strace`: `libswdlo.so` -- a document-loader shared library -- was
   `ENOENT`). `apt-get install libreoffice-calc libreoffice-writer` fixed it;
   re-verify these packages are present wherever a live batch actually runs.
2. **In-place conversion silently fails** (a real bug in this module, now
   fixed): converting a file to itself (same `--outdir` as the source) makes
   LibreOffice print "Overwriting: <path>" then fail the actual write with
   "Write Code:12" -- to **stderr**, with exit code 0 regardless. The
   previous version of this function only checked `stdout` for "Error" and
   only checked returncode, so it silently reported success while leaving
   the original, un-recalculated file untouched. Confirmed exactly this
   failure mode with a real formula (`=A1+A2`): reported `ok=True` but the
   cell still read `None` under `data_only=True` afterward. Fixed by doing
   what their own `open_spreadsheet.py:just_open_libreoffice()` already
   does: convert into a fresh temp directory, then move the result over the
   original path -- never convert a file onto itself.
"""
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

LIBREOFFICE_TIMEOUT_S = 120


@dataclass(frozen=True)
class GradeResult:
    task_id: str
    passed: bool  # hard_restriction: all test cases passed
    n_test_cases: int
    n_test_cases_passed: int
    soft_restriction: float  # fraction of test cases passed
    per_test_case_messages: list[str]
    error: Optional[str] = None
    # Non-empty when LibreOffice recalculation failed for one or more files.
    # A formula-bearing task can then fail comparison for a reason that has
    # nothing to do with the model, so this must not be silently dropped.
    recalc_warnings: list[str] = field(default_factory=list)


def recalculate_with_libreoffice(paths: list[Path], soffice_bin: Optional[str] = None) -> tuple[bool, str]:
    """Recalculates formulas in-place for each path via a headless
    LibreOffice conversion (same approach as the repo's own
    open_spreadsheet.py:just_open_libreoffice() -- convert into a temp
    directory, then move the result over the original path; NEVER pass the
    same directory as both source and --outdir, which fails silently, see
    module docstring). Returns (ok, message); does not raise, so a caller
    can log-and-continue rather than crash a whole batch on one broken
    environment."""
    soffice_bin = soffice_bin or shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice_bin:
        return False, "soffice/libreoffice binary not found on PATH"

    # Every path is attempted even if an earlier one fails. This used to
    # `return False` on the first failure, which silently skipped the
    # remaining files: a hiccup converting test case 1 left cases 2 and 3
    # un-recalculated, and their formula cells then compared as None. The
    # task scored 0/3 and was recorded as a model failure with no trace of
    # the real cause.
    failures: list[str] = []
    for path in paths:
        path = Path(path)
        with tempfile.TemporaryDirectory() as tmpdir:
            proc = subprocess.run(
                [
                    soffice_bin,
                    "--headless",
                    "--norestore",
                    f"-env:UserInstallation=file://{tmpdir}/.lo_profile",
                    "--convert-to",
                    "xlsx:Calc MS Excel 2007 XML",
                    "--outdir",
                    tmpdir,
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=LIBREOFFICE_TIMEOUT_S,
            )
            combined_output = (proc.stdout or "") + (proc.stderr or "")
            converted = Path(tmpdir) / (path.stem + ".xlsx")
            if proc.returncode != 0 or "Error" in combined_output or not converted.exists():
                failures.append(f"{path}: {combined_output.strip()[:200]}")
                continue
            shutil.move(str(converted), str(path))
    if failures:
        return False, "LibreOffice recalculation failed for: " + "; ".join(failures)
    return True, ""


def recalculated_copy(path: Path, cache_dir: Path, soffice_bin: Optional[str] = None) -> tuple[Path, str]:
    """Return a path to a recalculated COPY of `path`, leaving the original
    untouched. Returns (path_to_use, warning); on failure the warning is
    non-empty and the ORIGINAL path is returned, so comparison still runs.

    This exists because the alternative -- recalculating in place -- mutated
    SpreadsheetBench's shipped ground-truth answer files. Those need
    recalculating (they ship with uncached formulas; see evaluate_task), but
    doing it over the originals was destructive in three compounding ways:
    the dataset no longer matched its own tarball, `_extract_tarball_if_needed`
    skips re-extraction whenever the directory exists so nothing ever restored
    it, and the in-memory memo was per-instance, so each new process
    re-converted already-converted files -- a LibreOffice round-trip applied
    on top of the previous one, forever.

    The cache key includes the source's size and mtime, so an updated or
    re-extracted source converts again instead of returning a stale copy.
    """
    path = Path(path)
    try:
        stat = path.stat()
    except OSError:
        return path, f"cannot stat {path}"
    key = hashlib.sha256(f"{path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}".encode()).hexdigest()[:20]
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{key}{path.suffix or '.xlsx'}"
    if cached.exists():
        return cached, ""

    shutil.copy(path, cached)
    ok, msg = recalculate_with_libreoffice([cached], soffice_bin=soffice_bin)
    if not ok:
        # Leave nothing half-converted behind for the next run to trust.
        cached.unlink(missing_ok=True)
        return path, msg
    return cached, ""


class SpreadsheetBenchGrader:
    def __init__(self, repo_dir: Path):
        self.repo_dir = Path(repo_dir)
        self.eval_dir = self.repo_dir / "evaluation"
        eval_module_path = self.eval_dir / "evaluation.py"
        if not eval_module_path.exists():
            raise FileNotFoundError(
                f"{eval_module_path} not found -- clone SpreadsheetBench via "
                "study2.dataset.ensure_repo() first."
            )
        # Import their evaluation.py as a module (not `import evaluation`,
        # to avoid clashing with this package's own name) and call its
        # compare_workbooks() directly -- see module docstring for why.
        spec = importlib.util.spec_from_file_location("_spreadsheetbench_evaluation", eval_module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._compare_workbooks = module.compare_workbooks
        # Recalculated ground-truth copies live here, NEVER over the shipped
        # files. A dotdir inside the clone so it is obviously not dataset
        # content, and persistent across processes so the LibreOffice
        # round-trip for a given answer file happens once, not once per run.
        self.recalc_cache_dir = self.repo_dir / ".recalc_cache"

    def evaluate_task(
        self,
        task_id: str,
        instruction_type: str,
        answer_position: str,
        output_paths: list[Path],
        answer_paths: list[Path],
        recalculate: bool = True,
    ) -> GradeResult:
        """Grades one task's model-produced output workbooks (one per test
        case, same order as `answer_paths`) using SpreadsheetBench's own
        compare_workbooks(), reproducing their exact soft/hard-restriction
        scoring.

        IMPORTANT (found via gating check, not documentation -- see git
        history): the *ground-truth* answer files shipped with
        SpreadsheetBench can themselves contain uncached formulas. Confirmed
        directly on a real sample task (99-24, answer_position spanning
        `'Vendor'!A1:D101`): cell A33 reads `None` under `data_only=True`
        from the answer file as shipped, but recalculates to `32`. A
        perfect, correct model output would fail comparison against that
        uncached `None` for no reason of its own. So this recalculates
        `answer_paths` too, not just `output_paths` -- memoized per answer
        path (`self._recalculated_answer_paths`) since the same ground-truth
        files are reused across every model/tone/trial for a given task and
        recalculating them is idempotent but not free."""
        if len(output_paths) != len(answer_paths):
            return GradeResult(task_id, False, len(answer_paths), 0, 0.0, [], error="output/answer count mismatch")

        recalc_warnings: list[str] = []
        if recalculate:
            # Output workbooks are ours (written into scratch), so converting
            # them in place is fine.
            ok, msg = recalculate_with_libreoffice([p for p in output_paths if p is not None])
            if not ok:
                recalc_warnings.append(msg)
            # Answer workbooks are the shipped ground truth and must NOT be
            # modified -- recalculate a cached copy and compare against that.
            resolved: list[Optional[Path]] = []
            for p in answer_paths:
                if p is None:
                    resolved.append(None)
                    continue
                use, warn = recalculated_copy(p, self.recalc_cache_dir)
                if warn:
                    recalc_warnings.append(warn)
                resolved.append(use)
            answer_paths = resolved
            # Recalculation failures (missing LibreOffice, a broken file) are
            # not hard-failed here -- comparison still runs and may still
            # pass for pure-value, non-formula tasks -- but they are now
            # surfaced on the GradeResult instead of being discarded, so a
            # formula-bearing task that failed for this reason is
            # distinguishable from one the model actually got wrong.

        results = []
        messages = []
        for output_path, answer_path in zip(output_paths, answer_paths):
            if output_path is None or not Path(output_path).exists():
                results.append(False)
                messages.append("no output produced")
                continue
            try:
                ok, msg = self._compare_workbooks(str(answer_path), str(output_path), instruction_type, answer_position)
            except Exception as e:
                ok, msg = False, str(e)
            results.append(ok)
            messages.append(msg)

        n_passed = sum(results)
        n_total = len(results)
        return GradeResult(
            task_id=task_id,
            passed=(n_passed == n_total),
            n_test_cases=n_total,
            n_test_cases_passed=n_passed,
            soft_restriction=n_passed / n_total if n_total else 0.0,
            per_test_case_messages=messages,
            # Surfaced rather than discarded: a formula-bearing task can fail
            # comparison purely because recalculation didn't happen, and that
            # is not the same result as the model getting it wrong.
            recalc_warnings=recalc_warnings,
        )
