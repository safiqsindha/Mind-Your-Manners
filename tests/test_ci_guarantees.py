"""Guards on the things CI must actually verify.

Two of this project's defects were invisible because the check that should
have caught them did not run:

  * the `progress.py` formula-blindness defect is guarded by
    LibreOffice-dependent tests that are `skipif`-gated -- if LibreOffice is
    absent they skip SILENTLY and CI stays green with the guarantee
    unverified; and
  * `results/analysis/` was excluded from CI's compile and test steps
    entirely, which is how a non-step-up Benjamini-Hochberg shipped.

These tests make both conditions visible.
"""
from __future__ import annotations

import pathlib
import shutil

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CI = ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_workflow_exists():
    assert CI.exists(), "CI workflow is missing"


def test_ci_installs_libreoffice():
    """Without this, the recalculation tests skip on a lean runner."""
    text = CI.read_text()
    assert "libreoffice" in text.lower(), (
        "ci.yml does not install LibreOffice; the formula-recalculation tests "
        "would skip silently and CI would stay green with this project's "
        "highest-impact defect unguarded"
    )


def test_ci_installs_pandoc():
    """Without this, the converter tests skip and the build pipeline is unguarded.

    build/md2tex.py shells out to pandoc and is the single converter behind both
    the full manuscript and the workshop carve. Four rendering defects have
    already shipped through it -- raw citation keys, a flattened heading
    hierarchy, duplicated front matter, and a silently unconverted multi-key
    citation -- none of which a passing LaTeX build could detect.
    """
    text = CI.read_text()
    assert "pandoc" in text.lower(), (
        "ci.yml does not install pandoc; the md2tex.py tests would skip "
        "silently and CI would stay green with the converter unverified"
    )


def test_ci_compiles_the_analysis_scripts():
    """results/analysis/ computes the paper's numbers; CI must see it."""
    text = CI.read_text()
    assert "results/analysis" in text, (
        "ci.yml's compile step does not cover results/analysis/ -- that "
        "blind spot is how the non-step-up BH implementation shipped"
    )


@pytest.mark.skipif(
    shutil.which("soffice") is None and shutil.which("libreoffice") is None,
    reason="LibreOffice absent locally; CI installs and verifies it explicitly",
)
def test_libreoffice_is_actually_invocable():
    """A canary: if LibreOffice is present it must actually run."""
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    assert exe, "no LibreOffice binary found"
    assert pathlib.Path(exe).exists()
