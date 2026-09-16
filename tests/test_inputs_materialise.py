"""The derived analysis inputs must track the archive, not merely exist.

`results/analysis/_inputs.py` copies or decompresses `results_archive/` into
the names the analysis scripts read. Its first version treated an existing
destination as fresh: a pull that changed a committed archive left the old
decompressed JSON in place, so every script silently kept analysing stale
data, and a decompression interrupted half-way left a truncated file that
counted as present. Freshness is now decided by content -- a destination is
rewritten when its bytes differ from what the archive yields -- and every
write goes through a temporary file and an atomic rename, so no run can
leave a partial destination behind.
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import os
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INPUTS = ROOT / "results" / "analysis" / "_inputs.py"

EXPECTED = {
    "core_records.json": {"run": 1},
    "study2_core_gpt-luna-ceiling20-Q0_control_records.json": {"arm": "Q0"},
    "study2_x_progress.json": {"p": 1},
}


def _gz(path: pathlib.Path, obj) -> None:
    with gzip.open(path, "wb") as fh:
        fh.write(json.dumps(obj).encode())


def _derived(analysis: pathlib.Path) -> dict:
    return {p.name: json.loads(p.read_text()) for p in analysis.glob("*.json")}


@pytest.fixture
def staged(tmp_path):
    """The module pointed at a throwaway archive holding one file of each kind."""
    spec = importlib.util.spec_from_file_location("_inputs_under_test", INPUTS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    archive = tmp_path / "results_archive"
    (archive / "progress_regrade_corrected").mkdir(parents=True)
    mod.ARCHIVE = archive
    mod.ANALYSIS = tmp_path / "results" / "analysis"

    (archive / "core_records.json").write_text(json.dumps({"run": 1}))
    _gz(archive / "ceiling20_Q0_control_records.json.gz", {"arm": "Q0"})
    _gz(archive / "progress_regrade_corrected" / "study2_x_progress.json.gz", {"p": 1})
    return mod, archive, mod.ANALYSIS


def test_fresh_clone_gets_every_input_under_the_expected_name(staged):
    mod, _, analysis = staged
    assert not analysis.exists()
    assert mod.materialise() == 3
    assert _derived(analysis) == EXPECTED


def test_changed_archive_replaces_stale_output(staged):
    """A pull that updates a committed archive must reach the scripts."""
    mod, archive, analysis = staged
    mod.materialise()
    (archive / "core_records.json").write_text(json.dumps({"run": 2}))
    _gz(archive / "ceiling20_Q0_control_records.json.gz", {"arm": "Q0", "v": 2})

    assert mod.materialise() == 2
    got = _derived(analysis)
    assert got["core_records.json"] == {"run": 2}
    assert got["study2_core_gpt-luna-ceiling20-Q0_control_records.json"] == {"arm": "Q0", "v": 2}
    assert got["study2_x_progress.json"] == {"p": 1}


def test_truncated_output_is_restored(staged):
    """A file cut short by an interrupted decompression must not count as present."""
    mod, _, analysis = staged
    mod.materialise()
    victim = analysis / "study2_x_progress.json"
    victim.write_bytes(victim.read_bytes()[:3])

    assert mod.materialise() == 1
    assert json.loads(victim.read_text()) == {"p": 1}


def test_unchanged_inputs_are_left_untouched(staged):
    """No churn: identical content is neither rewritten nor re-timestamped."""
    mod, _, analysis = staged
    mod.materialise()

    def stamps():
        return {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in analysis.glob("*.json")}

    before = stamps()
    assert mod.materialise() == 0
    assert stamps() == before


def test_failed_install_leaves_old_file_and_no_debris(staged, monkeypatch):
    """Writes land via rename, so a failure mid-way leaves the old file intact."""
    mod, archive, analysis = staged
    mod.materialise()
    (archive / "core_records.json").write_text(json.dumps({"run": 2}))

    def refuse(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", refuse)
    with pytest.raises(OSError):
        mod.materialise()
    assert json.loads((analysis / "core_records.json").read_text()) == {"run": 1}
    assert sorted(p.name for p in analysis.iterdir()) == sorted(EXPECTED)
