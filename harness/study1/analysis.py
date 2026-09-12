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


def bootstrap_accuracy_ci(
    is_correct: list[bool],
    cluster_ids: Optional[list] = None,
    n_boot: int = N_BOOTSTRAP,
    alpha: float = 0.05,
) -> AccuracyEstimate:
    """Bootstrap CI on an accuracy, resampling CLUSTERS with replacement.

    `cluster_ids` must be parallel to `is_correct` -- the item/task each
    observation came from. A resampled draw takes a cluster and every
    observation in it, which is the same unit of independence
    clustered_paired_comparison and clustered_trend_test already work in.

    Resampling individual observations instead assumes they are independent,
    and in this design they are not: the same benchmark item is run under
    every tone, several trials each, and repeated trials on one item agree
    with each other far more than two different items do. That makes an iid
    bootstrap draw treat 150 observations as 150 independent facts when
    they are 50 tasks' worth, and the interval comes out too narrow by
    roughly the square root of the trials-per-cluster. Measured on the
    gpt-luna core run's L1_sycophantic tone (150 observations = 50 tasks x
    3 trials): iid gave [0.280, 0.433] where clustering gives
    [0.240, 0.473] -- the iid interval is a third narrower, on the very
    interval a reader uses to decide whether two tones overlap.

    `cluster_ids=None` keeps the old behaviour (each observation its own
    cluster) for genuinely unclustered data -- and produces bit-identical
    output to the previous implementation, since one-observation clusters
    make the cluster bootstrap the iid bootstrap.
    """
    arr = np.array(is_correct, dtype=float)
    n = len(arr)
    if n == 0:
        return AccuracyEstimate(n=0, accuracy=float("nan"), ci_low=float("nan"), ci_high=float("nan"))
    if cluster_ids is None:
        cluster_ids = list(range(n))
    if len(cluster_ids) != n:
        raise ValueError(
            f"cluster_ids has {len(cluster_ids)} entries for {n} observations -- "
            "they must be parallel, or the CI silently describes the wrong grouping"
        )

    members: dict[Any, list[int]] = defaultdict(list)
    for i, cid in enumerate(cluster_ids):
        members[cid].append(i)
    # Insertion order, so the result depends only on the input's order.
    cluster_sums = np.array([arr[idx].sum() for idx in members.values()])
    cluster_sizes = np.array([len(idx) for idx in members.values()], dtype=float)

    k = len(cluster_sums)
    rng = np.random.default_rng(RNG_SEED)
    draws = rng.integers(0, k, size=(n_boot, k))
    # Pooled accuracy of the resampled clusters: total correct over total
    # observations drawn, NOT the mean of per-cluster accuracies -- clusters
    # can differ in size (a task can be missing a trial) and pooling keeps
    # the bootstrap statistic the same quantity as the point estimate.
    boot_means = cluster_sums[draws].sum(axis=1) / cluster_sizes[draws].sum(axis=1)
    lo, hi = np.quantile(boot_means, [alpha / 2, 1 - alpha / 2])
    return AccuracyEstimate(n=n, accuracy=float(arr.mean()), ci_low=float(lo), ci_high=float(hi))


def per_level_accuracy(
    rows: list[dict], group_key: str = "tone_level", cluster_key: str = "item_id"
) -> dict[str, AccuracyEstimate]:
    """Per-level accuracy with item-clustered bootstrap CIs. The cluster ids
    are passed through rather than dropped: the same item appears under every
    tone with repeated trials, so an iid CI here would be too narrow (see
    bootstrap_accuracy_ci)."""
    by_group: dict[str, list[bool]] = defaultdict(list)
    clusters_by_group: dict[str, list] = defaultdict(list)
    for r in rows:
        if r["outcome"] == "answered":
            by_group[r[group_key]].append(bool(r["is_correct"]))
            clusters_by_group[r[group_key]].append(r[cluster_key])
    return {g: bootstrap_accuracy_ci(v, cluster_ids=clusters_by_group[g]) for g, v in by_group.items()}


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


@dataclass(frozen=True)
class TrendTestResult:
    n_clusters: int
    observed_slope: float  # mean per-item least-squares slope of outcome vs. ordinal tone position
    p_value: float
    ci_low: float
    ci_high: float


def _cluster_slope(level_values: dict[str, list[float]], levels: list[str], positions: dict[str, int]) -> float:
    xs, ys = [], []
    for level in levels:
        for v in level_values.get(level, []):
            xs.append(positions[level])
            ys.append(v)
    if len(set(xs)) < 2:
        return 0.0
    xs_arr, ys_arr = np.array(xs, dtype=float), np.array(ys, dtype=float)
    x_mean, y_mean = xs_arr.mean(), ys_arr.mean()
    denom = float(np.sum((xs_arr - x_mean) ** 2))
    if denom == 0:
        return 0.0
    return float(np.sum((xs_arr - x_mean) * (ys_arr - y_mean)) / denom)


def clustered_trend_test(
    rows: list[dict],
    levels: list[str],
    cluster_key: str = "item_id",
    group_key: str = "tone_level",
    value_key: str = "is_correct",
    n_perm: int = N_PERMUTATIONS,
) -> TrendTestResult:
    """Item-clustered permutation test for a monotonic trend across
    `levels` (an ORDERED sequence, e.g. the 7-tone scale), replacing a full
    pairwise comparison matrix as the primary analysis when the conditions
    are ordered ("with seven ordered levels, do not run 21 pairwise
    tests -- pre-register a trend test across the ordered scale as the
    primary analysis").

    For each cluster (e.g. benchmark item / task), computes the
    least-squares slope of `value_key` against `levels`' ordinal position
    (0..len(levels)-1) using every observation in that cluster (pooling
    trials/models if more than one is present under a given
    cluster+level). The observed statistic is the mean of these per-cluster
    slopes.

    Null distribution: for each cluster independently, permute WHICH
    ordinal position its own observed per-level values are assigned to
    (shuffling within-cluster), preserving each cluster's own value
    distribution while destroying any real association with tone order --
    the natural generalization of clustered_paired_comparison's sign-flip
    permutation (built for exactly two groups) to more than two ordered
    groups. p-value is the two-sided tail fraction of permuted |mean
    slope| at least as extreme as the observed one. A cluster contributes
    to the trend statistic only if it has at least 2 distinct levels
    observed (a slope needs variation in the x-axis); clusters that don't
    are silently excluded, not treated as zero-slope evidence.

    Item-clustered bootstrap CI on the mean slope, same convention as
    clustered_paired_comparison.
    """
    positions = {level: i for i, level in enumerate(levels)}
    by_cluster: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r[group_key] not in positions:
            continue
        by_cluster[r[cluster_key]][r[group_key]].append(float(r[value_key]))

    cluster_ids = [cid for cid, level_vals in by_cluster.items() if len(level_vals) >= 2]
    if not cluster_ids:
        return TrendTestResult(0, float("nan"), float("nan"), float("nan"), float("nan"))

    cluster_level_vals = [by_cluster[cid] for cid in cluster_ids]
    observed_slopes = np.array([_cluster_slope(lv, levels, positions) for lv in cluster_level_vals])
    observed_mean_slope = float(observed_slopes.mean())

    n = len(cluster_ids)
    rng = np.random.default_rng(RNG_SEED)
    perm_stats = np.empty(n_perm)
    for p in range(n_perm):
        slopes = np.empty(n)
        for idx, level_vals in enumerate(cluster_level_vals):
            present_levels = [lvl for lvl in levels if lvl in level_vals]
            shuffled = rng.permutation(present_levels)
            permuted = {shuffled[i]: level_vals[present_levels[i]] for i in range(len(present_levels))}
            slopes[idx] = _cluster_slope(permuted, levels, positions)
        perm_stats[p] = slopes.mean()

    p_value = float(np.mean(np.abs(perm_stats) >= abs(observed_mean_slope)))

    boot_idx = rng.integers(0, n, size=(N_BOOTSTRAP, n))
    boot_means = observed_slopes[boot_idx].mean(axis=1)
    ci_low, ci_high = np.quantile(boot_means, [0.025, 0.975])

    return TrendTestResult(
        n_clusters=n,
        observed_slope=observed_mean_slope,
        p_value=p_value,
        ci_low=float(ci_low),
        ci_high=float(ci_high),
    )
