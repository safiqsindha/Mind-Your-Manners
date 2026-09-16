"""Materialise the analysis inputs the scripts in this directory expect.

The raw records are committed to results_archive/ under different names and
partly gzipped, while every script here reads from results/analysis/, whose
*.json is git-ignored. On a fresh clone the expected inputs therefore never
exist and three of the five scripts fail with FileNotFoundError before doing
any work. This module closes that: it copies or decompresses each archived
file into the name the scripts look for. Idempotent -- an existing target is
left alone -- so calling it at the top of every script costs nothing after
the first run.

Mapping (one-to-one, see review/04-stage2-claims-vs-evidence.md section 1.1):
  results_archive/<name>.json                       -> results/analysis/<name>.json
  results_archive/ceiling20_<ARM>_records.json.gz   -> results/analysis/study2_core_gpt-luna-ceiling20-<ARM>_records.json
  results_archive/progress_regrade_corrected/<f>.gz -> results/analysis/<f>
"""
from __future__ import annotations

import gzip
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "results_archive"
ANALYSIS = ROOT / "results" / "analysis"


def _gunzip(src: pathlib.Path, dst: pathlib.Path) -> None:
    with gzip.open(src, "rb") as fh, open(dst, "wb") as out:
        shutil.copyfileobj(fh, out)


def materialise(force: bool = False) -> int:
    """Populate results/analysis/ from results_archive/. Returns files written."""
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    written = 0
    for src in ARCHIVE.glob("*.json"):
        dst = ANALYSIS / src.name
        if force or not dst.exists():
            shutil.copyfile(src, dst); written += 1
    for src in ARCHIVE.glob("ceiling20_*_records.json.gz"):
        arm = src.name[len("ceiling20_"):-len("_records.json.gz")]
        dst = ANALYSIS / f"study2_core_gpt-luna-ceiling20-{arm}_records.json"
        if force or not dst.exists():
            _gunzip(src, dst); written += 1
    for src in (ARCHIVE / "progress_regrade_corrected").glob("*.json.gz"):
        dst = ANALYSIS / src.name[:-3]
        if force or not dst.exists():
            _gunzip(src, dst); written += 1
    return written


if __name__ == "__main__":
    n = materialise()
    print(f"materialised {n} input file(s) into {ANALYSIS.relative_to(ROOT)}")
