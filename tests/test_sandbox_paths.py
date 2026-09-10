"""Regression tests for relative-path handling in
harness/study2/sandbox.py.

Deliberately NOT gated on sandbox_isolation_mode() (unlike
tests/test_sandbox.py, which is skipped wholesale when `unshare` is
unavailable -- including on GitHub Actions runners, per that module's
docstring). The bug these cover has nothing to do with network isolation
and must be caught on every host, CI included.

The bug: execute_python_on_workbook() launches its subprocess with
cwd=workdir. Any relative path handed to that subprocess is therefore
re-resolved against the new cwd instead of the harness's own, which
silently doubled the script path and made EVERY execution fail with
"can't open file" before running a single line of model code. It went
undetected because every other test passes an absolute pytest tmp_path,
while every real CLI run passes a relative out_dir ("results/...") --
so the tests and the real runs never exercised the same path shape.
"""
from __future__ import annotations

import os
from pathlib import Path

import openpyxl

from harness.study2.sandbox import execute_python_on_workbook

READ_WRITE_CODE = """
import openpyxl
wb = openpyxl.load_workbook(WORKBOOK_PATH)
print("cell:", wb.active["A1"].value)
wb.active["B1"] = 99
wb.save(OUTPUT_PATH)
print("saved")
"""


def _make_workbook(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    wb.active["A1"] = 42
    wb.save(path)


def test_relative_workdir_still_executes_the_code(tmp_path: Path, monkeypatch):
    """The exact shape of a real CLI run: cwd is the repo root and out_dir
    is relative, so workdir arrives as "results/scratch/...". Before the
    fix this failed with "can't open file .../<workdir>/<workdir>/
    _agent_code.py" and produced no output at all."""
    monkeypatch.chdir(tmp_path)
    workbook = Path("data/in.xlsx")
    _make_workbook(workbook)

    result = execute_python_on_workbook(
        READ_WRITE_CODE, workbook, Path("results/scratch/task_t0")
    )

    assert result.returncode == 0, f"stderr was: {result.stderr}"
    assert "can't open file" not in result.stderr
    assert "cell: 42" in result.stdout
    assert "saved" in result.stdout
    assert result.output_workbook_path is not None
    assert result.output_workbook_path.exists()


def test_relative_workbook_path_is_readable_after_the_cwd_change(tmp_path: Path, monkeypatch):
    """WORKBOOK_PATH is injected into the child as a literal string and read
    *after* the cwd change, so a relative workbook path must be resolved
    too -- same bug class as the script path, one layer deeper."""
    monkeypatch.chdir(tmp_path)
    workbook = Path("data/nested/in.xlsx")
    _make_workbook(workbook)

    result = execute_python_on_workbook(
        READ_WRITE_CODE, workbook, Path("results/scratch/task_t1")
    )

    assert result.returncode == 0, f"stderr was: {result.stderr}"
    assert "No such file or directory" not in result.stderr
    assert "cell: 42" in result.stdout


def test_output_workbook_is_loadable_not_just_present(tmp_path: Path, monkeypatch):
    """A real run's grader loads this file; "it exists" is not the same
    claim as "it parses"."""
    monkeypatch.chdir(tmp_path)
    workbook = Path("data/in.xlsx")
    _make_workbook(workbook)

    result = execute_python_on_workbook(
        READ_WRITE_CODE, workbook, Path("results/scratch/task_t2")
    )

    assert result.output_workbook_path is not None
    reloaded = openpyxl.load_workbook(result.output_workbook_path)
    assert reloaded.active["A1"].value == 42
    assert reloaded.active["B1"].value == 99


def test_absolute_paths_keep_working(tmp_path: Path):
    """The fix resolves paths; it must not break the absolute-path case
    every other test in this suite relies on."""
    workbook = tmp_path / "in.xlsx"
    _make_workbook(workbook)

    result = execute_python_on_workbook(
        READ_WRITE_CODE, workbook, tmp_path / "work"
    )

    assert result.returncode == 0, f"stderr was: {result.stderr}"
    assert "cell: 42" in result.stdout
    assert result.output_workbook_path is not None


def test_script_path_handed_to_the_child_is_absolute(tmp_path: Path, monkeypatch):
    """Pins the mechanism rather than only the symptom: whatever the caller
    passes, the child must be invoked with an absolute script path, since
    it runs with cwd=workdir."""
    monkeypatch.chdir(tmp_path)
    workbook = Path("data/in.xlsx")
    _make_workbook(workbook)

    execute_python_on_workbook(READ_WRITE_CODE, workbook, Path("results/scratch/task_t3"))

    written = tmp_path / "results/scratch/task_t3/_agent_code.py"
    assert written.exists(), "the generated script should land in the workdir itself"
    body = written.read_text()
    # WORKBOOK_PATH/OUTPUT_PATH are injected as literals and read after the
    # cwd change, so both must be absolute in the emitted script.
    for line in body.splitlines():
        if line.startswith(("WORKBOOK_PATH =", "OUTPUT_PATH =")):
            value = line.split("=", 1)[1].strip().strip("'\"")
            assert os.path.isabs(value), f"{line!r} is not absolute"
