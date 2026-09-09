"""SpreadsheetBench task loader.

Source: https://github.com/RUCKBReasoning/SpreadsheetBench (912 real-world
spreadsheet manipulation tasks, CC BY-SA 4.0). The 912-task set ships as
`data/all_data_912.tar.gz` inside that repo; there is also a 200-task sample
at `data/sample_data_200.tar.gz`. Neither is on the Hugging Face Hub, so this
loader shells out to `git clone` + `tar` rather than pretending there is a
`datasets`-library path -- see `ensure_repo()`.

SpreadsheetBench 2 (https://github.com/RUCKBReasoning/SpreadsheetBench-2) is
the optional secondary set for end-to-end business workflow tasks (four
categories: Debugging, Financial_Model, Template, Visualization).
"""
from __future__ import annotations

import json
import subprocess
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO_URL = "https://github.com/RUCKBReasoning/SpreadsheetBench.git"
REPO_V2_URL = "https://github.com/RUCKBReasoning/SpreadsheetBench-2.git"


@dataclass(frozen=True)
class SpreadsheetTask:
    task_id: str
    instruction: str
    category: str
    input_spreadsheet_paths: list[Path]  # one per test case
    answer_spreadsheet_paths: list[Path]  # one per test case, same order


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
    """Load tasks from a cloned SpreadsheetBench repo.

    `sample_only=True` uses the 200-task sample (data/sample_data_200.tar.gz)
    instead of the full 912 -- useful for the pilot stage. Directory layout
    inside the tarball follows the repo's documented convention: each task
    folder contains numbered `{No.}_{id}_input.xlsx` / `{No.}_{id}_answer.xlsx`
    pairs (one pair per test case) plus a metadata file describing the
    instruction. Adjust the metadata field names below if they differ once
    actually extracted -- this was written from the repo's documented
    structure, not a hands-on inspection of the tarball contents.
    """
    repo_dir = Path(repo_dir)
    tar_name = "sample_data_200.tar.gz" if sample_only else "all_data_912.tar.gz"
    tar_path = repo_dir / "data" / tar_name
    if not tar_path.exists():
        raise FileNotFoundError(f"{tar_path} not found -- did ensure_repo() succeed?")

    extract_dir = repo_dir / "data" / tar_path.stem.replace(".tar", "")
    _extract_tarball_if_needed(tar_path, extract_dir)

    tasks: list[SpreadsheetTask] = []
    for task_dir in sorted(extract_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        meta_path = task_dir / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        input_paths = sorted(task_dir.glob("*_input.xlsx"))
        answer_paths = sorted(task_dir.glob("*_answer.xlsx"))
        tasks.append(
            SpreadsheetTask(
                task_id=task_dir.name,
                instruction=meta.get("instruction", ""),
                category=meta.get("category", "unknown"),
                input_spreadsheet_paths=input_paths,
                answer_spreadsheet_paths=answer_paths,
            )
        )
        if limit and len(tasks) >= limit:
            break
    return tasks
