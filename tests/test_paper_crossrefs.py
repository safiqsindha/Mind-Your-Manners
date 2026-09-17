"""Every section cross-reference in the manuscript must resolve to a heading.

The paper cross-references itself roughly 200 times ("the estimator of §2.4",
"the caveat in §8.7"). Those references are prose, not LaTeX labels, so nothing
in the build breaks when a section is renumbered or removed -- the PDF simply
ships a pointer to a section that does not exist. That is exactly what happens
when a long manuscript is cut down, and it is invisible in a diff.

This pins both directions for both documents: no reference without a target,
and -- for the section headings the paper actually numbers -- no silent gap in
the numbering where a subsection was deleted mid-run.
"""
from __future__ import annotations

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

# "## 2.4 The estimator..." / "# 2. Design..." -- the numbering the prose cites.
HEADING = re.compile(r"^#{1,3}\s+(\d+(?:\.\d+)?)[.\s]", re.M)
# "§2.4", "§4", and the range/list forms "§2.6--§2.8", "§4.2, §8.7".
REF = re.compile(r"§(\d+(?:\.\d+)?)")


def _sources(subdir: str) -> list[pathlib.Path]:
    return sorted((ROOT / subdir).glob("*.md"))


def _headings(paths: list[pathlib.Path]) -> set[str]:
    out: set[str] = set()
    for p in paths:
        for m in HEADING.finditer(p.read_text()):
            out.add(m.group(1))
            out.add(m.group(1).split(".")[0])      # "2.4" also satisfies "§2"
    return out


def _refs(paths: list[pathlib.Path]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in paths:
        for m in REF.finditer(p.read_text()):
            out.setdefault(m.group(1), []).append(p.name)
    return out


def test_every_paper_cross_reference_resolves():
    paths = _sources("paper")
    assert paths, "no manuscript sources"
    headings = _headings(paths)
    dangling = {ref: sorted(set(where)) for ref, where in _refs(paths).items()
                if ref not in headings}
    assert not dangling, (
        "the manuscript points at sections that do not exist: "
        + "; ".join(f"§{r} (cited in {', '.join(w)})" for r, w in sorted(dangling.items()))
    )


def test_paper_subsection_numbering_has_no_gaps():
    """A missing number means a subsection was cut and its siblings not renumbered."""
    nums: dict[int, set[int]] = {}
    for p in _sources("paper"):
        for m in HEADING.finditer(p.read_text()):
            if "." in m.group(1):
                major, minor = (int(x) for x in m.group(1).split("."))
                nums.setdefault(major, set()).add(minor)
    for major, minors in sorted(nums.items()):
        expected = set(range(1, max(minors) + 1))
        assert minors == expected, (
            f"§{major} numbers {sorted(minors)}; §{major}."
            f"{sorted(expected - minors)} missing"
        )


@pytest.mark.parametrize("subdir", ["workshop"])
def test_workshop_cross_references_resolve_within_itself(subdir):
    """The carve renumbers, so a §N carried over from the long paper dangles.

    References the carve makes to the long version are written as "the long
    version's §N" and are allowed; a bare §N must resolve inside the carve.
    """
    paths = _sources(subdir)
    headings = _headings(paths)
    dangling = []
    for p in paths:
        text = p.read_text()
        for m in REF.finditer(text):
            if m.group(1) in headings:
                continue
            window = text[max(0, m.start() - 60):m.start()]
            if "long version" in window:            # explicitly the other document
                continue
            dangling.append(f"§{m.group(1)} in {p.name}")
    assert not dangling, f"carve cites sections it does not contain: {sorted(set(dangling))}"
