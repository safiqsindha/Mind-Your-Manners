"""Materialise the analysis inputs the scripts in this directory expect.

The raw records are committed to results_archive/ under different names and
partly gzipped, while every script here reads from results/analysis/, whose
*.json is git-ignored. On a fresh clone the expected inputs therefore never
exist and three of the five scripts fail with FileNotFoundError before doing
any work. This module closes that: it copies or decompresses each archived
file into the name the scripts look for.

Freshness is decided by content, not by existence. A derived file is
rewritten when its bytes differ from what the archive yields, so a pull that
changes a committed archive reaches the scripts on their next run, and a
file truncated by an interrupted run is repaired rather than trusted. Every
write goes to a temporary file beside the destination followed by an atomic
rename, so no run can leave a partial destination behind. When nothing has
changed nothing is written, which is why calling this at the top of every
script costs tens of milliseconds and no churn.

Mapping (one-to-one, see review/04-stage2-claims-vs-evidence.md section 1.1):
  results_archive/<name>.json                       -> results/analysis/<name>.json
  results_archive/ceiling20_<ARM>_records.json.gz   -> results/analysis/study2_core_gpt-luna-ceiling20-<ARM>_records.json
  results_archive/progress_regrade_corrected/<f>.gz -> results/analysis/<f>
"""
from __future__ import annotations

import gzip
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "results_archive"
ANALYSIS = ROOT / "results" / "analysis"


def _pairs():
    """(archived source, derived destination) for every input, in mapping order."""
    for src in sorted(ARCHIVE.glob("*.json")):
        yield src, ANALYSIS / src.name
    for src in sorted(ARCHIVE.glob("ceiling20_*_records.json.gz")):
        arm = src.name[len("ceiling20_"):-len("_records.json.gz")]
        yield src, ANALYSIS / f"study2_core_gpt-luna-ceiling20-{arm}_records.json"
    for src in sorted((ARCHIVE / "progress_regrade_corrected").glob("*.json.gz")):
        yield src, ANALYSIS / src.name[:-len(".gz")]


def _archived_bytes(src: pathlib.Path) -> bytes:
    if src.suffix == ".gz":
        with gzip.open(src, "rb") as fh:
            return fh.read()
    return src.read_bytes()


def _stale(dst: pathlib.Path, want: bytes) -> bool:
    """True unless `dst` exists and holds exactly `want`."""
    try:
        size = dst.stat().st_size
    except FileNotFoundError:
        return True
    return size != len(want) or dst.read_bytes() != want


def _install(dst: pathlib.Path, data: bytes) -> None:
    """Write `data` to `dst` atomically: a temporary file beside it, then rename.

    The temporary name ends in .json so the *.json ignore rule covers it even
    if a crash leaves it behind; the pid keeps concurrent runs apart.
    """
    tmp = dst.with_name(f".{dst.stem}.{os.getpid()}.partial.json")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, dst)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def materialise(force: bool = False) -> int:
    """Populate results/analysis/ from results_archive/. Returns files (re)written."""
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    written = 0
    for src, dst in _pairs():
        want = _archived_bytes(src)
        if force or _stale(dst, want):
            _install(dst, want)
            written += 1
    return written


if __name__ == "__main__":
    n = materialise()
    print(f"materialised {n} input file(s) into {ANALYSIS.relative_to(ROOT)}")
