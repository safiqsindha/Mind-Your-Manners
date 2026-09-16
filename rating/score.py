#!/usr/bin/env python3
"""Score the blinded ratings against the analyses pre-committed in PROTOCOL.md.

Every statistic here was named in the protocol before any rating existed. This
file computes those and nothing else; anything exploratory is labelled as such
in the output so it cannot be mistaken for a pre-committed result.

Run: python3 rating/score.py
"""
from __future__ import annotations

import itertools
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RATING = ROOT / "rating"

sys.path.insert(0, str(ROOT))

# The original single-coder judgement from §4.2, transcribed from the paper's
# own table. This is the thing the blinded raters are being checked against.
ORIGINAL_DEMAND = {
    "L1_sycophantic": "no",
    "L5_rude": "no",
    "L4_neutral": "no",
    "L2_very_polite": "yes",
    "L6_very_rude": "yes",
    "L7_threatening": "yes",
    "L3_polite": "yes",
}

# Figure 2A orders the closure arms by how strongly the authors judged each to
# project an end. Rank 1 = most closing. The control sits between the
# shortening and lengthening groups.
PAPER_CLOSURE_RANK = {
    "Q3_closing_neutral": 1,
    "Q1_praise_assistant": 2,
    "Q2_praise_work": 3,
    "Q0_control": 4,
    "Q4_praise_remains": 5,
    "Q5_remains_only": 6,
}

# Measured turn effect vs control, for the continuous check. Keys are arms; the
# values are read from the computed contrast file, never typed here.
TURN_CONTRAST = {
    "L1_sycophantic": "L1_sycophantic vs neutral [turns] (seven-level, Luna, ceiling 10)",
    "L2_very_polite": "L2_very_polite vs neutral [turns] (seven-level, Luna, ceiling 10)",
    "L3_polite": "L3_polite vs neutral [turns] (seven-level, Luna, ceiling 10)",
    "L5_rude": "L5_rude vs neutral [turns] (seven-level, Luna, ceiling 10)",
    "L6_very_rude": "L6_very_rude vs neutral [turns] (seven-level, Luna, ceiling 10)",
    "L7_threatening": "L7_threatening vs neutral [turns] (seven-level, Luna, ceiling 10)",
    "P1_demand_only": "demand vs control [turns] (probe, Luna, ceiling 10)",
    "P2_praise_only": "praise vs control [turns] (probe, Luna, ceiling 10)",
    "P3_insult_only": "insult vs control [turns] (probe, Luna, ceiling 10)",
    "Q2_praise_work": "praise-work vs control [turns] (praise run, Luna, ceiling 10)",
    "Q3_closing_neutral": "closing cue vs control [turns] (praise run, Luna, ceiling 10)",
    "Q4_praise_remains": "praise+remains vs control [turns] (praise run, Luna, ceiling 10)",
    "Q5_remains_only": "remains-only vs control [turns] (praise run, Luna, ceiling 10)",
}


# ---------------------------------------------------------------- statistics

def cohens_kappa(a: list, b: list) -> float:
    """Two raters, same items, categorical labels."""
    n = len(a)
    labels = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def krippendorff_alpha(ratings: dict[str, list], level: str) -> float:
    """Krippendorff's alpha. `ratings` maps unit -> list of values (one per rater).

    level: "nominal" or "ordinal". Units with fewer than two ratings are
    unpairable and excluded, per the standard definition.
    """
    units = {u: v for u, v in ratings.items() if len(v) >= 2}
    if not units:
        return float("nan")
    values = sorted({x for v in units.values() for x in v})
    if len(values) < 2:
        return 1.0  # no variation anywhere: perfect agreement by definition

    # Coincidence matrix.
    coincidence = {(c, k): 0.0 for c in values for k in values}
    for v in units.values():
        m = len(v)
        for x, y in itertools.permutations(v, 2):
            coincidence[(x, y)] += 1.0 / (m - 1)

    n_c = {c: sum(coincidence[(c, k)] for k in values) for c in values}
    n_total = sum(n_c.values())

    if level == "nominal":
        def delta2(c, k):
            return 0.0 if c == k else 1.0
    else:  # ordinal
        def delta2(c, k):
            lo, hi = sorted((values.index(c), values.index(k)))
            between = sum(n_c[values[g]] for g in range(lo, hi + 1))
            return (between - (n_c[c] + n_c[k]) / 2.0) ** 2

    do = sum(coincidence[(c, k)] * delta2(c, k) for c in values for k in values) / n_total
    de = sum(n_c[c] * n_c[k] * delta2(c, k)
             for c in values for k in values if c != k) / (n_total * (n_total - 1))
    return 1.0 - do / de if de else float("nan")


def spearman(x: list[float], y: list[float]) -> float:
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = statistics.fmean(x), statistics.fmean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    return num / den if den else float("nan")


# ---------------------------------------------------------------------- data

def load():
    key = json.loads((RATING / "key.json").read_text())["key"]
    raters = {}
    for f in sorted((RATING / "ratings").glob("rater*.json")):
        raters[f.stem] = json.loads(f.read_text())
    if not raters:
        sys.exit("no ratings found in rating/ratings/")
    # arm -> {rater: record}
    by_arm: dict[str, dict] = {}
    for sid, arm in key.items():
        by_arm[arm] = {r: v[sid] for r, v in raters.items() if sid in v}
    # arms that share a text see the same rating
    aliases = {"P0_control": "L4_neutral", "Q0_control": "L4_neutral",
               "Q1_praise_assistant": "P2_praise_only"}
    for alias, src in aliases.items():
        if src in by_arm:
            by_arm[alias] = by_arm[src]
    return raters, by_arm


def turn_effects() -> dict[str, float]:
    path = ROOT / "results" / "analysis" / "turn_count_family.json"
    if not path.exists():
        return {}
    fam = json.loads(path.read_text())
    lookup = {c["contrast"]: c["estimate"]
              for f in ("arm_vs_control", "within_design_section5")
              for c in fam[f]["contrasts"]}
    return {arm: lookup[label] for arm, label in TURN_CONTRAST.items() if label in lookup}


# --------------------------------------------------------------------- report

def main() -> None:
    raters, by_arm = load()
    names = sorted(raters)
    print(f"{len(names)} raters: {', '.join(names)}\n")

    # 1. Agreement with the original coding, on the seven register arms.
    print("1. demand_binary vs the original single-coder judgement (§4.2, 7 register arms)")
    orig = [ORIGINAL_DEMAND[a] for a in ORIGINAL_DEMAND]
    per_rater = {}
    for r in names:
        got = [by_arm[a][r]["demand_binary"].strip().lower() for a in ORIGINAL_DEMAND]
        agree = sum(x == y for x, y in zip(got, orig)) / len(orig)
        k = cohens_kappa(got, orig)
        per_rater[r] = (agree, k, got)
        print(f"   {r:8s} raw agreement {agree:5.1%}   kappa {k:+.3f}")
    mean_k = statistics.fmean(k for _, k, _ in per_rater.values())
    print(f"   mean kappa across raters: {mean_k:+.3f}")
    print("   per-arm disagreements:")
    for i, arm in enumerate(ORIGINAL_DEMAND):
        votes = [per_rater[r][2][i] for r in names]
        if len(set(votes)) > 1 or votes[0] != orig[i]:
            print(f"     {arm:18s} original={orig[i]:3s}  raters={votes}")
    print()

    # 2. Inter-rater reliability.
    print("2. Inter-rater reliability across all 14 stimuli")
    for field, level in (("demand_binary", "nominal"),
                         ("demand_strength", "ordinal"),
                         ("closure_strength", "ordinal")):
        seen, per_unit = set(), {}
        for arm, recs in by_arm.items():
            text_key = tuple(sorted(recs.items()))[0] if recs else None
            if arm in ("P0_control", "Q0_control", "Q1_praise_assistant"):
                continue  # alias of another arm; would double-count
            per_unit[arm] = [recs[r][field] for r in names if r in recs]
        a = krippendorff_alpha(per_unit, level)
        print(f"   {field:18s} ({level:7s})  alpha = {a:+.3f}")
    print()

    # 3. Closure ordering vs Figure 2A.
    print("3. Mean closure_strength vs Figure 2A's ordering (6 closure arms)")
    arms = [a for a in PAPER_CLOSURE_RANK if a in by_arm]
    mean_close = {a: statistics.fmean(by_arm[a][r]["closure_strength"] for r in names
                                      if r in by_arm[a]) for a in arms}
    paper_rank = [PAPER_CLOSURE_RANK[a] for a in arms]
    rated = [-mean_close[a] for a in arms]  # higher closure -> better rank
    rho = spearman(paper_rank, rated)
    for a in sorted(arms, key=lambda x: PAPER_CLOSURE_RANK[x]):
        print(f"   rank {PAPER_CLOSURE_RANK[a]}  {a:20s} mean closure = {mean_close[a]:.2f}")
    print(f"   Spearman rho (paper rank vs rated closure): {rho:+.3f}")
    print()

    # 4. demand_strength vs the measured turn effect.
    eff = turn_effects()
    common = [a for a in eff if a in by_arm]
    if common:
        print(f"4. Mean demand_strength vs measured turn effect ({len(common)} arms)")
        ds = [statistics.fmean(by_arm[a][r]["demand_strength"] for r in names if r in by_arm[a])
              for a in common]
        te = [eff[a] for a in common]
        print(f"   Pearson r  = {pearson(ds, te):+.3f}")
        print(f"   Spearman rho = {spearman(ds, te):+.3f}")
        for a, d, t in sorted(zip(common, ds, te), key=lambda z: -z[1]):
            print(f"     {a:20s} demand {d:4.1f}   turns {t:+.2f}")
        print()
        print("   EXPLORATORY, not pre-committed: the same against closure_strength")
        cs = [statistics.fmean(by_arm[a][r]["closure_strength"] for r in names if r in by_arm[a])
              for a in common]
        print(f"   Pearson r  = {pearson(cs, te):+.3f}")

    out = RATING / "results.json"
    out.write_text(json.dumps({
        "raters": names,
        "kappa_vs_original": {r: per_rater[r][1] for r in names},
        "mean_kappa": mean_k,
        "mean_closure_strength": mean_close,
        "closure_spearman_vs_figure": rho,
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
