"""The workshop carve must stay consistent with the full paper and the bib.

`build/workshop.tex` is a 4-page carve of the 54-page manuscript for a NeurIPS
workshop. It shares one converter, one bibliography and one figure script with
the full paper, which is the point -- a second copy of any of those would be a
second place for the rendering defects this repo has already shipped once.

These tests are cheap: they do not run pdflatex. They check the invariants that
rot silently when the full paper is edited and the carve is not.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / "workshop"
BIB = ROOT / "review" / "references.bib"
TEX = ROOT / "build" / "workshop.tex"
MD2TEX = ROOT / "build" / "md2tex.py"

CITE = re.compile(r"\[([a-z][a-z0-9-]+)\]")


def bib_keys() -> set[str]:
    return set(re.findall(r"^@\w+\{([^,]+),", BIB.read_text(), re.M))


def workshop_text() -> str:
    return "\n".join(p.read_text() for p in sorted(WORKSHOP.glob("*.md")))


def test_workshop_sources_exist():
    assert sorted(p.name for p in WORKSHOP.glob("*.md")), "no workshop sources"
    assert TEX.exists()


def test_every_workshop_citation_resolves():
    """An unresolvable key becomes a raw bracket in the PDF, not a build error."""
    keys, unknown = bib_keys(), []
    for m in CITE.finditer(workshop_text()):
        key = m.group(1)
        # Only flag things that look like citation keys: a hyphen and a year.
        if re.search(r"-\d{4}", key) and key not in keys:
            unknown.append(key)
    assert not unknown, f"workshop cites keys absent from references.bib: {sorted(set(unknown))}"


def test_workshop_inputs_match_the_source_files():
    """Every markdown file is \\input, and every \\input has a markdown file."""
    inputs = set(re.findall(r"\\input\{workshop-sections/([^}]+)\}", TEX.read_text()))
    sources = {p.stem for p in WORKSHOP.glob("*.md")}
    assert inputs == sources, (
        f"workshop.tex inputs {sorted(inputs)} but workshop/ holds {sorted(sources)} -- "
        "a section added to one and not the other is silently dropped from the PDF"
    )


def test_figures_are_referenced_not_orphaned():
    tex = TEX.read_text()
    for pdf in ("demand-vs-register.pdf", "closing-cue.pdf"):
        assert pdf in tex, f"{pdf} is generated but not included in the carve"


def test_author_block_is_still_a_placeholder():
    """Deliberate: the author block is filled in last, after the venue is chosen.

    If this fails because a real author block was added, delete the test.
    """
    assert "author name withheld" in TEX.read_text()


@pytest.mark.skipif(
    shutil.which("pandoc") is None,
    reason="pandoc absent locally; ci.yml installs and verifies it explicitly, "
           "and tests/test_ci_guarantees.py asserts that it does",
)
def test_md2tex_accepts_a_source_directory(tmp_path):
    """The carve depends on the converter being parameterised, not copied."""
    src, out = tmp_path / "src", tmp_path / "out"
    src.mkdir()
    (src / "00-x.md").write_text("# H\n\nSee [ma-2024] for the benchmark.\n")
    r = subprocess.run(
        [sys.executable, str(MD2TEX), str(src), str(out)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    body = (out / "00-x.tex").read_text()
    assert "\\cite{ma-2024}" in body, "citations are not rewritten for a non-default source dir"


def test_md2tex_rejects_a_missing_source_directory(tmp_path):
    r = subprocess.run(
        [sys.executable, str(MD2TEX), str(tmp_path / "nope"), str(tmp_path / "out")],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert r.returncode != 0, "a typo'd source directory must not silently build nothing"


@pytest.mark.parametrize("claim", [
    "28-token",          # the length-matching control
    "acting turns",      # which of the two turn counts the numbers are
    "demand",            # the headline
])
def test_carve_keeps_the_load_bearing_qualifications(claim):
    """A short paper is where caveats get dropped; these three may not be."""
    assert claim in workshop_text(), f"the carve no longer states: {claim}"
