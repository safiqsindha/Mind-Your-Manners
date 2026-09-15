"""A regrade made by a different instrument must not be compared.

While the formula-recalculation fix was rolling out arm by arm, a freshly
regraded control compared against stale treatment arms produced a clean
final-match "effect" of -0.36 at p < 0.0001 -- in three arms at once, which is
the only reason it was caught. Cross-instrument comparison has to fail loudly.

The check is on the instrument's CONTENT HASH, not its mtime. The first
version compared mtimes, and `git checkout` rewrites a file's mtime without
changing a byte: after a merge, every one of 28 valid regraded arms was
declared stale, each notionally costing four machine-hours to redo.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "results" / "analysis" / "regrade_summary.py"


@pytest.fixture
def staged(tmp_path, monkeypatch):
    """A summary module pointed at a throwaway analysis directory."""
    spec = importlib.util.spec_from_file_location("regrade_summary", SUMMARY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["regrade_summary"] = mod
    spec.loader.exec_module(mod)
    analysis = tmp_path / "analysis"
    analysis.mkdir()
    mod.ANALYSIS = analysis
    mod.MANIFEST = analysis / "regrade_manifest.json"
    monkeypatch.setattr(mod, "_current_fingerprint", lambda: "abc123")
    return mod, analysis


def _write_arm(analysis, stem, fingerprint=None):
    path = analysis / f"study2_core_{stem}_progress.json"
    path.write_text(json.dumps([{"task_id": "1", "final_match": 1.0}]))
    if fingerprint is not None:
        manifest_path = analysis / "regrade_manifest.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        manifest[path.name] = fingerprint
        manifest_path.write_text(json.dumps(manifest))
    return path


def test_matching_fingerprint_loads(staged):
    mod, analysis = staged
    _write_arm(analysis, "fresh-arm", fingerprint="abc123")
    assert mod.load("fresh-arm") == [{"task_id": "1", "final_match": 1.0}]


def test_different_fingerprint_is_refused(staged):
    mod, analysis = staged
    _write_arm(analysis, "old-arm", fingerprint="deadbeef")
    with pytest.raises(SystemExit) as exc:
        mod.load("old-arm")
    assert "STALE" in str(exc.value)
    assert "deadbeef" in str(exc.value)


def test_unrecorded_arm_is_refused(staged):
    """An arm with no manifest entry has unknown provenance, so it is stale."""
    mod, analysis = staged
    _write_arm(analysis, "unstamped-arm", fingerprint=None)
    with pytest.raises(SystemExit) as exc:
        mod.load("unstamped-arm")
    assert "unrecorded" in str(exc.value)


def test_missing_arm_is_none_not_an_error(staged):
    mod, _ = staged
    assert mod.load("never-regraded") is None


def test_mtime_does_not_affect_the_verdict(staged):
    """The regression this replaces: a touched file is still valid.

    `git checkout` bumps mtimes without changing content. Under the old
    mtime-based guard that invalidated every existing regrade.
    """
    import os

    mod, analysis = staged
    path = _write_arm(analysis, "touched-arm", fingerprint="abc123")
    os.utime(path, (0, 0))  # far older than any instrument file
    assert mod.load("touched-arm") is not None


def test_fingerprint_tracks_content(tmp_path):
    """The real fingerprint must change with content and not with mtime."""
    import os

    sys.path.insert(0, str(ROOT))
    from harness.study2 import progress

    source = pathlib.Path(progress.__file__)
    before = progress.instrument_fingerprint()
    os.utime(source, (0, 0))
    assert progress.instrument_fingerprint() == before, "mtime must not matter"
    assert before == hashlib.sha256(source.read_bytes()).hexdigest()[:16]
