from pathlib import Path

import openpyxl
import pytest

from harness.study2.failure_taxonomy import (
    CORRECT,
    DROPPED_OR_TRUNCATED_ROWS,
    HARDCODED_VALUE_WHERE_FORMULA_REQUIRED,
    STRUCTURALLY_BROKEN_OUTPUT,
    classify_failure,
)
from harness.study2.sandbox import execute_python_on_workbook
from harness.study2.verification_scoring import score_trajectory


def test_classify_correct():
    label = classify_failure(True, True, True, 10, 10, True)
    assert label.category == CORRECT


def test_classify_broken_output():
    label = classify_failure(False, True, False, None, 10, output_loaded_ok=False)
    assert label.category == STRUCTURALLY_BROKEN_OUTPUT


def test_classify_dropped_rows():
    label = classify_failure(False, False, False, 5, 10, True)
    assert label.category == DROPPED_OR_TRUNCATED_ROWS


def test_classify_hardcoded_value():
    label = classify_failure(False, True, False, 10, 10, True)
    assert label.category == HARDCODED_VALUE_WHERE_FORMULA_REQUIRED


def test_score_trajectory_detects_inspection_and_destructive_action():
    snippets = [
        "import openpyxl\nwb = openpyxl.load_workbook(WORKBOOK_PATH)\nprint(wb.sheetnames)",
        "import os\nos.remove(WORKBOOK_PATH)\nwb.save(OUTPUT_PATH)",
    ]
    behavior = score_trajectory(snippets)
    assert behavior.inspected_before_acting is True
    assert behavior.took_destructive_action is True
    assert behavior.destructive_action_had_backup is False
    assert behavior.n_code_turns == 2


def test_score_trajectory_empty():
    behavior = score_trajectory([])
    assert behavior.n_code_turns == 0
    assert behavior.inspected_before_acting is False


def test_sandbox_executes_and_produces_output(tmp_path: Path):
    wb = openpyxl.Workbook()
    wb.active["A1"] = 10
    wb.active["A2"] = 32
    in_path = tmp_path / "in.xlsx"
    wb.save(in_path)

    code = (
        "import openpyxl\n"
        "wb = openpyxl.load_workbook(WORKBOOK_PATH)\n"
        "ws = wb.active\n"
        "ws['A3'] = ws['A1'].value + ws['A2'].value\n"
        "wb.save(OUTPUT_PATH)\n"
    )
    result = execute_python_on_workbook(code, in_path, tmp_path / "work")
    assert result.returncode == 0
    assert not result.timed_out
    assert result.output_workbook_path is not None
    out_wb = openpyxl.load_workbook(result.output_workbook_path)
    assert out_wb.active["A3"].value == 42


def test_sandbox_captures_errors_without_crashing_harness(tmp_path: Path):
    wb = openpyxl.Workbook()
    in_path = tmp_path / "in.xlsx"
    wb.save(in_path)
    result = execute_python_on_workbook("raise ValueError('boom')", in_path, tmp_path / "work")
    assert result.returncode != 0
    assert "boom" in result.stderr
    assert result.output_workbook_path is None
