"""Analysis for Study 1: per-level accuracy with bootstrap CIs, a paired
comparison across tone conditions clustered by benchmark item, effect
sizes, refusal rates, and a per-subject breakdown.

Input to every function here is a list of "analysis rows": plain dicts with
at least the keys `item_id`, `tone_level`, `subject`, `outcome`
("answered"/"refused"/"unparseable"), and `is_correct` (bool or None). These
are derived from results/raw/*.jsonl + answer_extraction.py output by
study1/runner.py -- see `rows_from_result_rows()` below.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

N_BOOTSTRAP = 10_000
N_PERMUTATIONS = 10_000
RNG_SEED = 12345


@dataclass(frozen=True)
class AccuracyEstimate:
    n: int
    accuracy: float
    ci_low: float
    ci_high: float


def rows_from_result_rows(result_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Adapt spend_tracker.ResultRow (as dicts) + extraction outcome into
    analysis rows. Expects each dict to already carry `outcome` and
    `is_correct` (set by the runner at extraction time)."""
    return [
        {
            "item_id": r["item_id"],
            "tone_level": r["tone_level"],
            "subject": r.get("extra", {}).get("subject", "unknown"),
            "model_key": r["model_key"],
            "outcome": r.get("extra", {}).get("outcome"),
            "is_correct": r["is_correct"],
        }
        for r in result_rows
    ]


def bootstrap_accuracy_ci(is_correct: list[bool], n_boot: int = N_BOOTSTRAP, alpha: float = 0.05) -> AccuracyEstimate:
    arr = np.array(is_correct, dtype=float)
    n = len(arr)
    if n == 0:
        return AccuracyEstimate(n=0, accuracy=float("nan"), ci_low=float("nan"), ci_high=float("nan"))
    rng = np.random.default_rng(RNG_SEED)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot_means = arr[idx].mean(axis=1)
    lo, hi = np.quantile(boot_means, [alpha / 2, 1 - alpha / 2])
    return AccuracyEstimate(n=n, accuracy=float(arr.mean()), ci_low=float(lo), ci_high=float(hi))


def per_level_accuracy(rows: list[dict], group_key: str = "tone_level") -> dict[str, AccuracyEstimate]:
    by_group: dict[str, list[bool]] = defaultdict(list)
    for r in rows:
        if r["outcome"] == "answered":
            by_group[r[group_key]].append(bool(r["is_correct"]))
    return {g: bootstrap_accuracy_ci(v) for g, v in by_group.items()}


def refusal_rate(rows: list[dict], group_key: str = "tone_level") -> dict[str, float]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # [refused, total]
    for r in rows:
        counts[r[group_key]][1] += 1
        if r["outcome"] == "refused":
            counts[r[group_key]][0] += 1
    return {g: (n_refused / n_total if n_total else float("nan")) for g, (n_refused, n_total) in counts.items()}


def unparseable_rate(rows: list[dict], group_key: str = "tone_level") -> dict[str, float]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        counts[r[group_key]][1] += 1
        if r["outcome"] == "unparseable":
            counts[r[group_key]][0] += 1
    return {g: (n_bad / n_total if n_total else float("nan")) for g, (n_bad, n_total) in counts.items()}


@dataclass(frozen=True)
class PairedComparison:
    level_a: str
    level_b: str
    n_clusters: int
    mean_diff: float  # mean(acc_b - acc_a) across item clusters
    effect_size_h: float  # Cohen's h for the two overall proportions
    p_value: float  # permutation test, sign-flipping within item clusters
    ci_low: float
    ci_high: float


def _cohens_h(p1: float, p2: float) -> float:
    phi1 = 2 * np.arcsin(np.sqrt(np.clip(p1, 0, 1)))
    phi2 = 2 * np.arcsin(np.sqrt(np.clip(p2, 0, 1)))
    return float(phi1 - phi2)


def clustered_paired_comparison(
    rows: list[dict],
    level_a: str,
    level_b: str,
    cluster_key: str = "item_id",
    n_perm: int = N_PERMUTATIONS,
) -> PairedComparison:
    """Compare accuracy between two tone levels, treating repeated trials on
    the same benchmark item as one cluster (task spec: "the same item
    appears in all five conditions -- do not treat observations as
    independent"). For each item, we compute mean accuracy under level_a and
    under level_b (averaging over trials/models within that item+level, if
    more than one), then run a sign-flip permutation test on the per-item
    paired differences.
    """
    by_item_level: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for r in rows:
        if r["outcome"] != "answered":
            continue
        if r["tone_level"] not in (level_a, level_b):
            continue
        by_item_level[(r[cluster_key], r["tone_level"])].append(bool(r["is_correct"]))

    item_ids = {item for (item, level) in by_item_level if level in (level_a, level_b)}
    diffs = []
    acc_a_all, acc_b_all = [], []
    for item in sorted(item_ids):
        a_vals = by_item_level.get((item, level_a))
        b_vals = by_item_level.get((item, level_b))
        if not a_vals or not b_vals:
            continue  # item must be answered under both conditions to be paired
        a_mean, b_mean = float(np.mean(a_vals)), float(np.mean(b_vals))
        diffs.append(b_mean - a_mean)
        acc_a_all.extend(a_vals)
        acc_b_all.extend(b_vals)

    diffs_arr = np.array(diffs)
    n = len(diffs_arr)
    if n == 0:
        return PairedComparison(level_a, level_b, 0, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))

    observed_mean = float(diffs_arr.mean())

    rng = np.random.default_rng(RNG_SEED)
    signs = rng.choice([-1.0, 1.0], size=(n_perm, n))
    perm_means = (signs * diffs_arr).mean(axis=1)
    p_value = float(np.mean(np.abs(perm_means) >= abs(observed_mean)))

    boot_idx = rng.integers(0, n, size=(N_BOOTSTRAP, n))
    boot_means = diffs_arr[boot_idx].mean(axis=1)
    ci_low, ci_high = np.quantile(boot_means, [0.025, 0.975])

    h = _cohens_h(float(np.mean(acc_b_all)), float(np.mean(acc_a_all)))

    return PairedComparison(
        level_a=level_a,
        level_b=level_b,
        n_clusters=n,
        mean_diff=observed_mean,
        effect_size_h=h,
        p_value=p_value,
        ci_low=float(ci_low),
        ci_high=float(ci_high),
    )


def subject_breakdown(rows: list[dict]) -> dict[str, dict[str, AccuracyEstimate]]:
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_subject[r["subject"]].append(r)
    return {subj: per_level_accuracy(subj_rows) for subj, subj_rows in by_subject.items()}


def all_pairwise_comparisons(rows: list[dict], levels: list[str]) -> list[PairedComparison]:
    out = []
    for i in range(len(levels)):
        for j in range(i + 1, len(levels)):
            out.append(clustered_paired_comparison(rows, levels[i], levels[j]))
    return out
