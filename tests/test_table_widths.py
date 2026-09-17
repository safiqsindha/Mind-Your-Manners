"""Table column widths in the generated LaTeX must come from the cells.

`build/md2tex.py` asks pandoc for natural-width table columns and then puts
`p{}` widths back only where the cells need to wrap. Both halves matter and
both fail silently in the PDF rather than in the build:

* Without natural widths, pandoc sizes every column from the dash counts in the
  markdown separator row, which have no relation to cell contents. A table of
  short numbers then wraps its headers over three lines each and fills half a
  page; across this manuscript that cost three pages.
* Without the `p{}` widths put back, a cell holding a sentence runs off the
  right-hand edge of the page -- 757pt past it, in the worst case measured.

These tests exercise the transformation directly, so they need no pandoc and no
LaTeX.
"""
from __future__ import annotations

import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _md2tex():
    """Import build/md2tex.py. Importing it must not convert anything."""
    spec = importlib.util.spec_from_file_location("md2tex_mod", ROOT / "build" / "md2tex.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_importing_the_converter_does_no_work():
    """It reads sys.argv and shells out to pandoc -- both belong in run(), not import."""
    mod = _md2tex()
    assert mod.SRC is None and mod.OUT is None, (
        "md2tex resolved its paths at import time; a test importing it would "
        "convert the manuscript as a side effect")
    assert callable(mod.run)


def _table(spec: str, rows: list[str]) -> str:
    body = "\n".join(r + r" \\" for r in rows)
    return ("\\begin{longtable}[]{@{}" + spec + "@{}}\n"
            "\\toprule\\noalign{}\n" + body + "\n"
            "\\bottomrule\\noalign{}\n\\endlastfoot\n\\end{longtable}")


NUMERIC = _table("lrrr", [
    "Arm & Turns & \\% & p",
    "L1 sycophantic & \\(-0.68\\) & \\(-7.1\\)\\% & 0.043",
    "L7 threatening & +1.46 & +36.7\\% & \\textless{}0.0001",
])

PROSE = _table("ll", [
    "Work & What reading it did",
    "\\cite{cai-2025-tone} & An earlier draft called it squarely the paradigm this section "
    "audits. Read in full, that is wrong: its format instruction is pinned across conditions "
    "and its prefixes instruct nothing.",
])

MONO = _table("lll", [
    "Arm & Content & What it isolates",
    "\\texttt{Q1\\_praise\\_assistant} & praises the assistant & reproduces the praise arm "
    "in-batch, against the same control, so the two runs share a reference level",
])


def test_short_numeric_tables_keep_natural_widths():
    """The common case: a table of labels and numbers must not be wrapped."""
    out = _md2tex().widen(NUMERIC)
    assert out == NUMERIC, "a short numeric table was given fixed column widths"


def test_prose_tables_get_wrapping_widths():
    out = _md2tex().widen(PROSE)
    assert "\\real{" in out, "a table with a sentence in a cell was left unwrapped"
    assert "\\raggedright" in out


def test_widths_sum_to_one():
    """Fractions that sum past 1.0 push the table off the page."""
    mod = _md2tex()
    import re
    for src in (PROSE, MONO):
        fracs = [float(x) for x in re.findall(r"\\real\{([0-9.]+)\}", mod.widen(src))]
        assert fracs, "expected wrapping widths"
        assert abs(sum(fracs) - 1.0) < 1e-3, f"widths sum to {sum(fracs)}"


def test_a_monospace_column_is_not_squeezed_below_its_longest_token():
    """`Q1_praise_assistant` has no hyphenation point; too narrow a column overflows."""
    mod = _md2tex()
    import re
    fracs = [float(x) for x in re.findall(r"\\real\{([0-9.]+)\}", mod.widen(MONO))]
    assert len(fracs) == 3
    needed = len("Q1_praise_assistant") * mod.MONO_WIDTH / mod.MAX_TOTAL
    assert fracs[0] >= needed * 0.98, (
        f"the arm-name column got {fracs[0]:.3f} of the line where its longest "
        f"unbreakable token needs about {needed:.3f}")


def test_scaffolding_is_not_measured_as_content():
    """\\toprule and friends sit on the same lines as cells and are not width."""
    mod = _md2tex()
    rows = mod._rows("@{}}\n\\toprule\\noalign{}\nArm & Turns \\\\\n\\midrule\\noalign{}\n"
                     "\\endhead\nL1 & \\(-0.68\\) \\\\\n\\bottomrule\\noalign{}\n\\endlastfoot\n")
    assert rows[0] == ["Arm", "Turns"], rows
    assert rows[1][0] == "L1", rows


def test_markup_is_not_counted_as_printed_width():
    mod = _md2tex()
    assert mod._visible(r"\textbf{94.4\%}") <= 7
    assert mod._visible(r"\cite{ma-2024}") <= 6
