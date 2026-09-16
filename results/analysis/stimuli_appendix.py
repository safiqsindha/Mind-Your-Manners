#!/usr/bin/env python3
"""Emit the stimulus appendix from the harness, not from a transcription.

Every interjection the study delivered lives in `harness/tone_wrappers.py`.
Retyping them into the paper would create a second copy that can silently
disagree with what was actually run -- the same class of defect as a figure
with hardcoded numbers. This reads the dictionaries the runner used and writes
the appendix section, with the token count recomputed under the reference
tokenizer so the "exactly 28 tokens" claim is checked rather than asserted.

Writes workshop/99-appendix.md.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "workshop" / "99-appendix.md"

sys.path.insert(0, str(ROOT))
from harness.tone_wrappers import (  # noqa: E402
    INTERJECTIONS,
    PRAISE_PROBE_INTERJECTIONS,
    PROBE_INTERJECTIONS,
    reference_token_count,
)

SETS = [
    ("A.1 Register scale (used in Figure 1A)", INTERJECTIONS,
     "`L4_neutral` is the interruption control; the other six are the "
     "non-control registers Figure 1A plots against it."),
    ("A.2 Demand/affect probe (Figure 1B)", PROBE_INTERJECTIONS,
     "`P0_control` is `L4_neutral`, byte-identical, so the two runs share a "
     "reference level. `P2` and `P3` are a structural minimal pair: identical "
     "syntax and length, differing only in the evaluative words."),
    ("A.3 Closure probe (Figure 2)", PRAISE_PROBE_INTERJECTIONS,
     "`Q0_control` is again `L4_neutral`. **`Q1_praise_assistant` is "
     "`P2_praise_only`, byte-identical** -- the same stimulus re-measured in a "
     "second run, which is why §3 reports two estimates for it. `Q1` and `Q4` "
     "are *not* a minimal pair: `Q4`'s praise is a shorter stem, because the "
     "full praise clause and the continuation clause do not both fit in 28 "
     "tokens. `Q4`'s comparison is `Q5`."),
]


def main() -> None:
    lines = [
        "# A. Interjections, verbatim",
        "",
        "Every arm delivers exactly one of these, appended to an execution "
        "observation mid-task. Token counts are recomputed here under the "
        "reference tokenizer (`cl100k_base`) rather than asserted; the runner "
        "enforces the same equality at import time.",
        "",
    ]
    seen: dict[str, str] = {}
    for heading, mapping, note in SETS:
        lines += [f"## {heading}", "", note, ""]
        lines += ["| Arm | Text | Tokens |", "|---|---|---:|"]
        for arm, text in mapping.items():
            flat = " ".join(text.split()).replace("|", r"\|")
            dup = next((k for k, v in seen.items() if v == text and k != arm), None)
            shown = f"*identical to `{dup}`*" if dup else flat
            lines.append(f"| `{arm}` | {shown} | {reference_token_count(text)} |")
            seen.setdefault(arm, text)
        lines.append("")

    counts = {reference_token_count(t) for m in (INTERJECTIONS, PROBE_INTERJECTIONS,
                                        PRAISE_PROBE_INTERJECTIONS)
              for t in m.values()}
    summary = (f"All {len(seen)} arms are exactly {sorted(counts)[0]} tokens."
               if len(counts) == 1 else
               f"Token counts are NOT uniform across the {len(seen)} arms: "
               f"{sorted(counts)}. The length-matching claim does not hold.")
    lines += [summary, ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} -- {len(seen)} arms, token counts {sorted(counts)}")


if __name__ == "__main__":
    main()
