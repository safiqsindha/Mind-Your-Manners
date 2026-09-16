"""Multiplicity correction for the study's PRIMARY outcome, turn count.

Section 2.6 corrects two families -- the twelve-outcome trend family and the
22-contrast accuracy family -- but never corrects turn count, which section 2.3
declares the primary outcome. Every reviewer who looked at the paper raised
that. This script closes it.

The family is NOT chosen here. It is inherited wholesale from
build_accuracy_family() in accuracy_null_mde.py: every arm-versus-control
contrast in every run that delivered a mid-task interjection, the same 22
comparisons across 6 runs and 2 models, with the outcome switched from
`passed` to `n_turns`. Inheriting the boundary is the point -- picking a
turn-count family by hand, after seeing which contrasts are large, is exactly
the gerrymandering section 2.6 warns against.

Usage:  python3 results/analysis/turn_count_family.py
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "results" / "analysis"))

import numpy as np  # noqa: E402

from harness.stats import benjamini_hochberg  # noqa: E402
from _inputs import materialise  # noqa: E402
import accuracy_null_mde as A  # noqa: E402

# The accuracy family reads its inputs from results/analysis/, which is
# git-ignored and empty on a fresh clone. Populate it from results_archive/
# first, or this script fails with FileNotFoundError before doing any work.
materialise()

ALPHA = 0.05
EXPECTED_CONTRASTS = A.EXPECTED_ACCURACY_CONTRASTS   # must match the accuracy family


def build_turn_family(rng):
    """The accuracy family's enumeration, with n_turns as the outcome.

    Implemented by monkeypatching per_task's default field for the duration of
    the call, so the enumeration itself is literally the same code path rather
    than a parallel copy that can drift out of step with it.
    """
    original_per_task, original_load = A.per_task, A.load

    def turns_per_task(records, *, arm=None, field="passed", **kw):
        # scale=100 is meaningless for turns; analyse() applies it to the
        # difference, so the accuracy family's scale is neutralised below.
        return original_per_task(records, arm=arm, field="n_turns", **kw)

    def records_not_regrade(path):
        # build_accuracy_family reads the micro-experiment from the
        # *_regraded.json files because it is computing accuracy, and a regrade
        # is a grading pass. Turn count is an observed trajectory property and
        # belongs to the run records. The two files carry different n_turns for
        # the same 50 tasks (+1.32 vs +1.02 for threatening-vs-neutral), so
        # reading turns from the regrade would put a regrader artefact into the
        # primary outcome. Substitute the records file for those two paths only.
        p = pathlib.Path(path)
        if p.name.endswith("_regraded.json") and "reinject" in p.name:
            p = p.with_name(p.name.replace("_regraded.json", "_records.json"))
        return original_load(p)

    A.per_task, A.load = turns_per_task, records_not_regrade
    try:
        rows = A.build_accuracy_family(rng)
    finally:
        A.per_task, A.load = original_per_task, original_load
    for r in rows:
        # build_accuracy_family passes scale=100.0 for percentage points; undo
        # it so estimates are in turns.
        for k in ("estimate", "se", "ci_lo", "ci_hi", "mde_80"):
            if k in r and r[k] is not None:
                r[k] = r[k] / 100.0
        # analyse() also computes TOST against the accuracy family's +/-4 and
        # +/-7.5 point bounds. Those are not turn-count bounds -- no turn-count
        # equivalence bound is defined anywhere in the paper -- so the values
        # are meaningless here and were being written out under accuracy
        # labels. Drop them rather than invent a bound.
        r.pop("tost", None)
        r["contrast"] = r["contrast"].replace(" (", " [turns] (", 1)
    return rows


def build_within_design_family(rng):
    """Section 5's two planned NON-control contrasts, as a family of their own.

    The 22-contrast family above is arm-versus-control by construction, because
    it inherits the accuracy family's boundary. Section 5 also rests on two
    contrasts that are not against control: praise isolated (Q4 minus Q5,
    the same message with and without praise) and closing cue versus praise
    (Q3 versus Q1). Both are designed contrasts -- the six-arm probe exists to
    make them -- and the abstract quotes the first. Leaving them uncorrected
    while claiming the primary outcome is corrected would be an overclaim, so
    they are corrected here as the separately stated family they are.
    Turn count, same estimator, same seed.
    """
    praise = A.load(A.ARCHIVE / "core_gpt-luna_praise_records.json")
    q = {k: A.per_task(praise, arm=k, field="n_turns") for k in
         ("Q1_praise_assistant", "Q3_closing_neutral", "Q4_praise_remains", "Q5_remains_only")}
    rows = [
        A.analyse("praise isolated, Q4 minus Q5 [turns] (praise run, Luna, ceiling 10)",
                  q["Q4_praise_remains"], q["Q5_remains_only"], rng=rng),
        A.analyse("closing cue vs praise, Q3 minus Q1 [turns] (praise run, Luna, ceiling 10)",
                  q["Q3_closing_neutral"], q["Q1_praise_assistant"], rng=rng),
    ]
    for r in rows:
        r.pop("tost", None)
    return rows


def _report(title, fam):
    hdr = f"\n{'contrast':<62}{'n':>4}{'est':>8}{'95% CI':>20}{'SE':>7}{'p':>9}"
    print(f"\n{title}")
    print(hdr); print("-" * (len(hdr) - 1))
    for r in sorted(fam, key=lambda r: r["p"]):
        ci = f"[{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}]"
        print(f"{r['contrast']:<62}{r['tasks']:>4}{r['estimate']:>+8.2f}{ci:>20}"
              f"{r['se']:>7.3f}{r['p']:>9.4f}")
    bh = benjamini_hochberg([r["p"] for r in fam], alpha=ALPHA)
    order = sorted(range(len(fam)), key=lambda i: fam[i]["p"])
    n_sig = sum(1 for b in bh if b.significant)
    print(f"  Benjamini-Hochberg, q={ALPHA}: {n_sig}/{len(fam)} survive; "
          f"Bonferroni-adjusted smallest p = {min(r['p'] for r in fam) * len(fam):.4f}")
    for i in order:
        r, b = fam[i], bh[i]
        print(f"    rank {b.rank:>2}  p={r['p']:.4f}  crit={b.critical_value:.4f}  "
              f"{'SURVIVES' if b.significant else 'does not survive':<16} {r['contrast']}")
    return n_sig


def main() -> None:
    rng = np.random.default_rng(A.SEED)
    fam = build_turn_family(rng)
    assert len(fam) == EXPECTED_CONTRASTS, (
        f"turn family is {len(fam)}, accuracy family is {EXPECTED_CONTRASTS} -- "
        "the two must be the same set of comparisons"
    )

    hdr = f"\n{'turn-count contrast':<56}{'n':>4}{'est':>8}{'95% CI':>20}{'SE':>7}{'p':>9}"
    print("TURN COUNT -- the primary outcome -- corrected over the same family")
    print("as the accuracy analysis in section 2.6.")
    print(hdr)
    print("-" * (len(hdr) - 1))
    for r in sorted(fam, key=lambda r: r["p"]):
        ci = f"[{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}]"
        print(f"{r['contrast']:<56}{r['tasks']:>4}{r['estimate']:>+8.2f}{ci:>20}"
              f"{r['se']:>7.3f}{r['p']:>9.4f}")

    bh = benjamini_hochberg([r["p"] for r in fam], alpha=ALPHA)
    order = sorted(range(len(fam)), key=lambda i: fam[i]["p"])
    n_sig = sum(1 for b in bh if b.significant)
    nominal = sum(1 for r in fam if r["p"] < 0.05)

    print(f"\nBenjamini-Hochberg over the {len(fam)}-contrast turn-count family "
          f"(q={ALPHA}):")
    print(f"  nominally significant at p<0.05 : {nominal}/{len(fam)}")
    print(f"  surviving BH                    : {n_sig}/{len(fam)}")
    print(f"  Bonferroni-adjusted smallest p  : "
          f"{min(r['p'] for r in fam) * len(fam):.6f}")
    print()
    for i in order:
        r, b = fam[i], bh[i]
        print(f"  rank {b.rank:>2}  p={r['p']:.4f}  crit={b.critical_value:.4f}  "
              f"{'SURVIVES' if b.significant else 'does not survive':<16} {r['contrast']}")

    within = build_within_design_family(rng)
    n_within = _report("SECTION 5 WITHIN-DESIGN CONTRASTS -- the planned non-control "
                       "comparisons, corrected as their own family", within)

    out = A.ANALYSIS / "turn_count_family.json"
    for r in fam + within:
        r.pop("per_task", None)
    out.write_text(json.dumps(
        {"alpha": ALPHA,
         "arm_vs_control": {"n_contrasts": len(fam), "n_nominal": nominal,
                            "n_survive_bh": n_sig, "contrasts": fam},
         "within_design_section5": {"n_contrasts": len(within),
                                    "n_survive_bh": n_within, "contrasts": within}},
        indent=2))
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
