"""SpreadsheetBench task loader.

Source: https://github.com/RUCKBReasoning/SpreadsheetBench (912 real-world
spreadsheet manipulation tasks, CC BY-SA 4.0). Verified against a real clone
of the repo (see git history for this file): the full set ships as
`data/spreadsheetbench_912_v0.1.tar.gz`, the pilot-sized sample as
`data/sample_data_200.tar.gz` (both confirmed present), and there is also a
`data/spreadsheetbench_verified_400.tar.gz` not referenced by the original
task spec -- not used here, but available if a smaller curated set is ever
wanted. Neither ships on the Hugging Face Hub, so this loader shells out to
`git clone` + `tar` rather than pretending there is a `datasets`-library
path -- see `ensure_repo()`.

Real on-disk schema (confirmed by extracting `sample_data_200.tar.gz` and
inspecting it directly -- this superseded an earlier, wrong guess that each
task had its own `metadata.json`; it does not):

  {sample_data_200 or spreadsheetbench_912_v0.1}/
    dataset.json          <- one JSON list for the WHOLE split, e.g.:
                              {"id": 59196, "instruction": "...",
                               "spreadsheet_path": "spreadsheet/59196",
                               "instruction_type": "Cell-Level Manipulation",
                               "answer_position": "H3:H5"}
    spreadsheet/{id}/
      1_{id}_input.xlsx    1_{id}_answer.xlsx    <- test case 1
      2_{id}_input.xlsx    2_{id}_answer.xlsx    <- test case 2
      3_{id}_input.xlsx    3_{id}_answer.xlsx    <- test case 3

`instruction_type` is v1's per-item category field (e.g. "Cell-Level
Manipulation") -- NOT the same four-category taxonomy
(Debugging/Financial_Model/Template/Visualization) used by SpreadsheetBench
2's newer end-to-end workflow tasks; don't conflate the two when reading
severity/category breakdowns in analysis output.

SpreadsheetBench 2 (https://github.com/RUCKBReasoning/SpreadsheetBench-2) is
the optional secondary set for end-to-end business workflow tasks and has
not been schema-verified the way v1 has here -- check its dataset.json shape
before trusting `load_spreadsheetbench(..., v2=True)` if you add that path.
"""
from __future__ import annotations

import json
import re
import subprocess
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO_URL = "https://github.com/RUCKBReasoning/SpreadsheetBench.git"
REPO_V2_URL = "https://github.com/RUCKBReasoning/SpreadsheetBench-2.git"

FULL_TARBALL = "spreadsheetbench_912_v0.1.tar.gz"
SAMPLE_TARBALL = "sample_data_200.tar.gz"

# Matches "1_59196_input.xlsx" etc. Deliberately excludes Excel/LibreOffice
# lock files (e.g. "~$1_53994_answer.xlsx") -- confirmed present in the real
# sample_data_200 tarball (one stray lock file under spreadsheet/53994/),
# which a naive "*_input.xlsx"/"*_answer.xlsx" glob picks up and then fails
# to parse as a leading test-case number.
_NUMBERED_XLSX_RE = re.compile(r"^(\d+)_.+_(input|answer)\.xlsx$")


def _numbered_xlsx(task_dir: Path, kind: str) -> list[Path]:
    matches = []
    for p in task_dir.glob(f"*_{kind}.xlsx"):
        m = _NUMBERED_XLSX_RE.match(p.name)
        if m:
            matches.append((int(m.group(1)), p))
    return [p for _, p in sorted(matches)]


@dataclass(frozen=True)
class SpreadsheetTask:
    task_id: str  # str(dataset.json's "id")
    instruction: str
    instruction_type: str  # v1's per-item category, e.g. "Cell-Level Manipulation"
    answer_position: str  # e.g. "H3:H5" or "'Sheet2'!A1:B2" -- passed straight to their compare_workbooks()
    # One (input, answer) pair per test case, in test-case order (1, 2, 3).
    # SpreadsheetBench's OJ-style grading runs the SAME agent-produced
    # solution against all three and scores generalization -- see
    # harness/study2/grader.py and runner.py:run_condition_batch.
    input_spreadsheet_paths: list[Path]
    answer_spreadsheet_paths: list[Path]


def ensure_repo(cache_dir: Path, v2: bool = False) -> Path:
    """Clone the SpreadsheetBench repo into cache_dir if not already present.
    Returns the repo path. Network access required; this is a multi-hundred-MB
    clone (spreadsheet binaries) -- do this once and reuse cache_dir."""
    cache_dir = Path(cache_dir)
    repo_dir = cache_dir / ("SpreadsheetBench-2" if v2 else "SpreadsheetBench")
    if repo_dir.exists():
        return repo_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", REPO_V2_URL if v2 else REPO_URL, str(repo_dir)],
        check=True,
    )
    return repo_dir


def _extract_tarball_if_needed(tar_path: Path, dest_dir: Path) -> Path:
    if dest_dir.exists():
        return dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path) as tf:
        tf.extractall(dest_dir)
    return dest_dir


def load_spreadsheetbench(
    repo_dir: Path,
    sample_only: bool = False,
    limit: Optional[int] = None,
) -> list[SpreadsheetTask]:
    """Load tasks from a cloned SpreadsheetBench repo's dataset.json.

    `sample_only=True` uses the 200-task sample -- useful for the pilot
    stage; `sample_only=False` uses the full 912-task set.
    """
    repo_dir = Path(repo_dir)
    tar_name = SAMPLE_TARBALL if sample_only else FULL_TARBALL
    tar_path = repo_dir / "data" / tar_name
    if not tar_path.exists():
        raise FileNotFoundError(f"{tar_path} not found -- did ensure_repo() succeed?")

    extract_root = repo_dir / "data" / tar_path.name.replace(".tar.gz", "")
    _extract_tarball_if_needed(tar_path, extract_root)
    # The tarball's top-level entry is a single directory (e.g.
    # "sample_data_200/") containing dataset.json + spreadsheet/ -- find it
    # rather than hardcoding the name twice, since it doesn't always match
    # the tarball's own filename stem (confirmed: sample_data_200.tar.gz's
    # top-level dir is "sample_data_200", spreadsheetbench_912_v0.1.tar.gz's
    # is presumably named differently -- verify if this raises).
    candidates = [d for d in extract_root.iterdir() if d.is_dir() and (d / "dataset.json").exists()]
    if not candidates:
        raise FileNotFoundError(f"No dataset.json found under {extract_root} after extraction")
    dataset_dir = candidates[0]

    dataset = json.loads((dataset_dir / "dataset.json").read_text())

    tasks: list[SpreadsheetTask] = []
    for item in dataset:
        task_id = str(item["id"])
        task_dir = dataset_dir / item["spreadsheet_path"]
        input_paths = _numbered_xlsx(task_dir, "input")
        answer_paths = _numbered_xlsx(task_dir, "answer")
        if not input_paths or len(input_paths) != len(answer_paths):
            continue  # skip incomplete task dirs rather than crash a whole run on one bad item
        tasks.append(
            SpreadsheetTask(
                task_id=task_id,
                instruction=item["instruction"],
                instruction_type=item["instruction_type"],
                answer_position=item["answer_position"],
                input_spreadsheet_paths=input_paths,
                answer_spreadsheet_paths=answer_paths,
            )
        )
        if limit and len(tasks) >= limit:
            break
    return tasks
