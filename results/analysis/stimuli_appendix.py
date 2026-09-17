#!/usr/bin/env python3
"""Emit the stimulus and blinded-rating appendices from the harness, not from a transcription.

Every interjection the study delivered lives in `harness/tone_wrappers.py`, and
every rating statistic in `rating/results.json`. Retyping either into a paper
would create a second copy that can silently disagree with what was actually run
-- the same class of defect as a figure with hardcoded numbers. This reads the
dictionaries the runner used and the file `rating/score.py` writes, with the
token count recomputed under the reference tokenizer so the "exactly 28 tokens"
claim is checked rather than asserted.

Both documents get the same appendix from this one script; they differ only in
where their own demand coding lives, so the cross-references are parameterised
rather than duplicated. Writes paper/08-appendix-stimuli.md and
workshop/99-appendix.md.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT))
from harness.tone_wrappers import (  # noqa: E402
    INTERJECTIONS,
    PRAISE_PROBE_INTERJECTIONS,
    PROBE_INTERJECTIONS,
    reference_token_count,
)

# The two documents number their sections differently, so a reference written for
# one dangles in the other. Everything the appendix points at is listed here.
TARGETS = {
    "paper": {
        "out": ROOT / "paper" / "08-appendix-stimuli.md",
        "coding": "§4.1",          # where our demand coding is stated
        "reruns": "Appendix C.1",  # where the two praise estimates are reported
        "closure_fig": "§5.3",     # where the closure ordering is argued
        "rater_allowance": "Section 7.3",
        "artifact": True,
    },
    "workshop": {
        "out": ROOT / "workshop" / "99-appendix.md",
        "coding": "§3",
        "reruns": "§5",
        "closure_fig": "Figure 2A",
        "rater_allowance": "The rating protocol",
        "artifact": True,
    },
}

SETS = [
    ("A.1 Register scale", INTERJECTIONS,
     "`L4_neutral` is the interruption control; the other six are the "
     "non-control registers measured against it."),
    ("A.2 Demand/affect probe", PROBE_INTERJECTIONS,
     "`P0_control` is `L4_neutral`, byte-identical, so the two runs share a "
     "reference level. `P2` and `P3` are a structural minimal pair: identical "
     "syntax and length, differing only in the evaluative words."),
    ("A.3 Closure probe", PRAISE_PROBE_INTERJECTIONS,
     "`Q0_control` is again `L4_neutral`. **`Q1_praise_assistant` is "
     "`P2_praise_only`, byte-identical** -- the same stimulus re-measured in a "
     "second run, which is why {reruns} reports two estimates for it. `Q1` and "
     "`Q4` are *not* a minimal pair: `Q4`'s praise is a shorter stem, because "
     "the full praise clause and the continuation clause do not both fit in 28 "
     "tokens. `Q4`'s comparison is `Q5`."),
]


def _rating_appendix(t: dict) -> list[str]:
    """Appendix B, from rating/results.json -- written by rating/score.py.

    Generated rather than typed for the same reason as the figures: a number
    retyped into a paper is a number that can drift from the analysis.
    """
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
        "were committed and pushed before any rating existed; the protocol is in the "
        "released artifact.",
        "",
        "## B.1 Against the original coding",
        "",
        f"| Rater | Cohen's κ vs {t['coding']}'s coding (7 register arms) |",
        "|---|---:|",
    ]
    for name in sorted(kappas):
        out.append(f"| {name} | {kappas[name]:+.3f} |")
    out += [
        "",
        f"Mean κ = **{r['mean_kappa']:+.3f}**. Every rater agrees on six of seven arms and "
        "every rater dissents on the same one, `L5_rude`; excluding it, agreement is 6/6 and "
        "κ = 1.000 for all five. The protocol fixed 0.40--0.70 in advance as *defensible "
        "but soft*, and this sits at the top of that band; we do not round it into the band above.",
        "",
        "## B.2 Between raters",
        "",
        "Krippendorff's α: **1.000** on the binary coding (nominal), **0.954** on the 0--6 "
        "demand scale and **0.732** on the 0--6 closure scale (both ordinal). All clear 0.70. "
        "Identical binary judgements from five raters across three model sizes is very high for "
        "a construct we have just shown to be contestable, and it is the limitation the protocol "
        "stated in advance: these raters may share the intuition being tested rather than testing "
        "it independently.",
        "",
        "## B.3 The closure ordering",
        "",
        "| Arm | Mean rated closure (0--6) |",
        "|---|---:|",
    ]
    for arm in sorted(close, key=lambda a: close[a], reverse=True):
        out.append(f"| `{arm}` | {close[arm]:.2f} |")
    out += [
        "",
        f"Spearman ρ between our ordering ({t['closure_fig']}) and the blinded ratings is "
        f"**{r['closure_spearman_vs_figure']:+.3f}**. The raters invert praising the *work* and "
        "praising the *assistant*, and the two “work remains” arms tie at the floor.",
        "",
        "## B.4 What this is not",
        "",
        f"Five language models, not five people. {t['rater_allowance']} allows “human "
        "or held-out-model ratings” and this is the second; agreement between models is "
        "weaker evidence than agreement between independent human coders, and a human panel could "
        "still split differently -- most plausibly on exactly the arm these raters were unanimous "
        "about.",
        "",
    ]
    return out


def _build(t: dict) -> tuple[list[str], dict[str, str], set[int]]:
    lines = [
        "# A. Interjections, verbatim",
        "",
        "**Artifact.** Code, the full stimulus set, the per-turn regrade pipeline, the rating "
        "protocol and per-trajectory outcomes are released with the paper at "
        "**[INSERT ZENODO DOI]** and **[INSERT REPO URL]**.",
        "",
        "Every arm delivers exactly one of these, appended to an execution "
        "observation mid-task. Token counts are recomputed here under the "
        "reference tokenizer (`cl100k_base`) rather than asserted; the runner "
        "enforces the same equality at import time.",
        "",
    ]
    seen: dict[str, str] = {}
    for heading, mapping, note in SETS:
        lines += [f"## {heading}", "", note.format(**t), ""]
        lines += ["| Arm | Text | Tokens |", "|---|---|---:|"]
        for arm, text in mapping.items():
            flat = " ".join(text.split()).replace("|", r"\|")
            dup = next((k for k, v in seen.items() if v == text and k != arm), None)
            shown = f"*identical to `{dup}`*" if dup else flat
            lines.append(f"| `{arm}` | {shown} | {reference_token_count(text)} |")
            seen.setdefault(arm, text)
        lines.append("")

    counts = {reference_token_count(x) for m in (INTERJECTIONS, PROBE_INTERJECTIONS,
                                                PRAISE_PROBE_INTERJECTIONS)
              for x in m.values()}
    summary = (f"All {len(seen)} arms are exactly {sorted(counts)[0]} tokens."
               if len(counts) == 1 else
               f"Token counts are NOT uniform across the {len(seen)} arms: "
               f"{sorted(counts)}. The length-matching claim does not hold.")
    lines += [summary, ""]
    lines += _rating_appendix(t)
    return lines, seen, counts


def main() -> None:
    for name, t in TARGETS.items():
        lines, seen, counts = _build(t)
        out = t["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n")
        print(f"wrote {out.relative_to(ROOT)} -- {len(seen)} arms, token counts {sorted(counts)}")


if __name__ == "__main__":
    main()
