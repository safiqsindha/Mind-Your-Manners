"""Thin wrapper around the SpreadsheetBench authors' own evaluator.

Task spec: "Use the authors' own evaluation code. Do not reimplement the
grader." This module shells out to their `evaluation/` scripts rather than
reimplementing cell-matching logic. It has not been run end-to-end against
a live checkout (no live run has happened in this harness yet -- see
README.md) -- treat `evaluate_task()`'s exact subprocess invocation as a
best-effort mapping onto the documented workflow:

    cd evaluation
    python open_spreadsheet.py --dir_path <task_dir>   # recalculate formulas
    bash scripts/evaluation.sh                          # OJ-style multi-test-case grading

Before a live run, clone the repo (see dataset.ensure_repo), run their
evaluator manually on one task with a known-correct answer file substituted
as the "model output" and confirm it reports a pass -- that is this module's
own mini validation gate, separate from the benchmark-level validation gate
in runner.py.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GradeResult:
    task_id: str
    passed: bool
    n_test_cases: int
    n_test_cases_passed: int
    raw_stdout: str
    raw_stderr: str
    error: str | None = None


class SpreadsheetBenchGrader:
    def __init__(self, repo_dir: Path):
        self.repo_dir = Path(repo_dir)
        self.eval_dir = self.repo_dir / "evaluation"
        if not self.eval_dir.exists():
            raise FileNotFoundError(
                f"{self.eval_dir} not found -- clone SpreadsheetBench via "
                "study2.dataset.ensure_repo() first."
            )

    def _recalculate(self, task_dir: Path) -> None:
        subprocess.run(
            ["python", "open_spreadsheet.py", "--dir_path", str(task_dir)],
            cwd=self.eval_dir,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def evaluate_task(self, task_id: str, task_dir: Path, model_output_dir: Path) -> GradeResult:
        """Grade one task's model-produced output spreadsheets against the
        answer spreadsheets, using the repo's own OJ-style multi-test-case
        comparison via scripts/evaluation.sh.

        `model_output_dir` must follow the same `{No.}_{id}_input.xlsx`
        naming convention the repo expects for a result file, with the
        model's generated workbook in place of each input file -- see the
        repo's evaluation.sh for the exact env vars it reads (RESULT_DIR /
        DATA_DIR at last check; confirm against the current script before a
        live run since this wrapper was written from documentation, not a
        successful local run).
        """
        try:
            self._recalculate(model_output_dir)
            proc = subprocess.run(
                ["bash", "scripts/evaluation.sh"],
                cwd=self.eval_dir,
                env={"DATA_DIR": str(task_dir), "RESULT_DIR": str(model_output_dir)},
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.CalledProcessError as e:
            return GradeResult(task_id, False, 0, 0, e.stdout or "", e.stderr or "", error=str(e))
        except subprocess.TimeoutExpired as e:
            return GradeResult(task_id, False, 0, 0, "", "", error=f"grader timed out: {e}")

        # NOTE: parsing here is a placeholder pending a real run against the
        # cloned repo's actual stdout format -- verify and fix before relying
        # on it for scored results.
        stdout = proc.stdout or ""
        passed = "PASS" in stdout.upper() and "FAIL" not in stdout.upper()
        return GradeResult(
            task_id=task_id,
            passed=passed,
            n_test_cases=stdout.upper().count("TEST CASE"),
            n_test_cases_passed=stdout.upper().count("PASS"),
            raw_stdout=stdout,
            raw_stderr=proc.stderr or "",
        )
