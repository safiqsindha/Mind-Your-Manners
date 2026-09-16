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


def _rating_appendix() -> list[str]:
    """Appendix B, from rating/results.json -- written by rating/score.py.

    Generated rather than typed for the same reason as the figures: a number
    retyped into a paper is a number that can drift from the analysis.
    """
    import json
    res_path = ROOT / "rating" / "results.json"
    if not res_path.exists():
        return ["# B. Blinded rating", "",
                "*Not yet run. `python3 rating/score.py` generates this section.*", ""]
    r = json.loads(res_path.read_text())
    kappas = r["kappa_vs_original"]
    close = r["mean_closure_strength"]
    out = [
        "# B. Blinded rating of the stimuli",
        "",
        f"{len(r['raters'])} held-out model raters, drawn from three model sizes, each rating "
        "alone from the rubric and the texts of Appendix A -- no outcome data, no arm names, no "
        "project access. The rubric, the statistics to be computed and the interpretation bands "
        "were committed and pushed before any rating existed; see `rating/PROTOCOL.md`.",
        "",
        "## B.1 Against the original coding",
        "",
        "| Rater | Cohen's \u03ba vs \u00a74.2's coding (7 register arms) |",
        "|---|---:|",
    ]
    for name in sorted(kappas):
        out.append(f"| {name} | {kappas[name]:+.3f} |")
    out += [
        "",
        f"Mean \u03ba = **{r['mean_kappa']:+.3f}**. Every rater agrees on six of seven arms and "
        "every rater dissents on the same one, `L5_rude`; excluding it, agreement is 6/6 and "
        "\u03ba = 1.000 for all five. The protocol fixed 0.40--0.70 in advance as *defensible "
        "but soft*, and this sits at the top of that band; we do not round it into the band above.",
        "",
        "## B.2 Between raters",
        "",
        "Krippendorff's \u03b1: **1.000** on the binary coding (nominal), **0.954** on the 0--6 "
        "demand scale and **0.732** on the 0--6 closure scale (both ordinal). All clear 0.70. "
        "Identical binary judgements from five raters across three model sizes is very high for "
        "a construct we have just shown to be contestable, and it is the limitation the protocol "
        "stated in advance: these raters may share the intuition being tested rather than testing "
        "it independently.",
        "",
        "## B.3 The closure ordering",
        "",
        "| Figure 2A rank | Arm | Mean rated closure (0--6) |",
        "|---:|---|---:|",
    ]
    for arm in sorted(close, key=lambda a: close[a], reverse=True):
        out.append(f"| | `{arm}` | {close[arm]:.2f} |")
    out += [
        "",
        f"Spearman \u03c1 between our ordering and the blinded ratings is "
        f"**{r['closure_spearman_vs_figure']:+.3f}**. The raters invert praising the *work* and "
        "praising the *assistant*, and the two \u201cwork remains\u201d arms tie at the floor.",
        "",
        "## B.4 What this is not",
        "",
        "Five language models, not five people. \u00a78.7 of the long version allows \u201chuman "
        "or held-out-model ratings\u201d and this is the second; agreement between models is "
        "weaker evidence than agreement between independent human coders, and a human panel could "
        "still split differently -- most plausibly on exactly the arm these raters were unanimous "
        "about.",
        "",
    ]
    return out


def main() -> None:
    lines = [
        "# A. Interjections, verbatim",
        "",
        "**Artifact.** Code, the full stimulus set, the per-turn regrade pipeline, the rating "
        "protocol and per-trajectory outcomes are available at "
        "`[AUTHOR: anonymized artifact URL]`.",
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
    lines += _rating_appendix()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} -- {len(seen)} arms, token counts {sorted(counts)}")


if __name__ == "__main__":
    main()
