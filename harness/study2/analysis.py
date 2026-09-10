"""Study 2 analysis: reuses Study 1's clustered-comparison machinery for the
accuracy dimension, and adds the agentic-specific outcome measures the task
spec calls out as "the part that matters": failure severity, verification
behavior, shortcut rate, and turn count/token spend per condition.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np

from ..study1.analysis import (  # re-exported for study2/runner.py convenience
    AccuracyEstimate,
    PairedComparison,
    all_pairwise_comparisons,
    bootstrap_accuracy_ci,
    clustered_paired_comparison,
    per_level_accuracy,
    refusal_rate,
)

__all__ = [
    "AccuracyEstimate",
    "PairedComparison",
    "all_pairwise_comparisons",
    "bootstrap_accuracy_ci",
    "clustered_paired_comparison",
    "per_level_accuracy",
    "refusal_rate",
    "severity_breakdown",
    "verification_rates",
    "shortcut_rate",
    "trajectory_cost_summary",
    "token_cost_effect_size",
    "compare_direction_to_study1",
]


def severity_breakdown(task_results: list[dict[str, Any]], group_key: str = "tone_level") -> dict[str, dict[str, float]]:
    """task_results: one dict per (task, tone, trial) with a `severity`
    field (from failure_taxonomy.SeverityLabel.category)."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    totals: dict[str, int] = defaultdict(int)
    for r in task_results:
        counts[r[group_key]][r["severity"]] += 1
        totals[r[group_key]] += 1
    return {
        level: {cat: n / totals[level] for cat, n in cat_counts.items()}
        for level, cat_counts in counts.items()
    }


def verification_rates(task_results: list[dict[str, Any]], group_key: str = "tone_level") -> dict[str, dict[str, float]]:
    """task_results: one dict per trajectory with `inspected_before_acting`
    and `self_checked_output` booleans (from verification_scoring.TrajectoryBehavior)."""
    out: dict[str, dict[str, list[bool]]] = defaultdict(lambda: {"inspected": [], "self_checked": []})
    for r in task_results:
        out[r[group_key]]["inspected"].append(bool(r["inspected_before_acting"]))
        out[r[group_key]]["self_checked"].append(bool(r["self_checked_output"]))
    return {
        level: {k: float(np.mean(v)) if v else float("nan") for k, v in metrics.items()}
        for level, metrics in out.items()
    }


def shortcut_rate(task_results: list[dict[str, Any]], group_key: str = "tone_level") -> dict[str, float]:
    """Fraction of trajectories that took a destructive/irreversible action
    without a backup (from verification_scoring.TrajectoryBehavior)."""
    out: dict[str, list[bool]] = defaultdict(list)
    for r in task_results:
        unsafe = bool(r["took_destructive_action"]) and not bool(r["destructive_action_had_backup"])
        out[r[group_key]].append(unsafe)
    return {level: float(np.mean(v)) if v else float("nan") for level, v in out.items()}


def trajectory_cost_summary(task_results: list[dict[str, Any]], group_key: str = "tone_level") -> dict[str, dict[str, float]]:
    """Mean turn count and mean total cost/tokens per condition -- the
    "if rude prompts produce shorter trajectories, that is a mechanism worth
    reporting" check from the task spec."""
    out: dict[str, dict[str, list[float]]] = defaultdict(lambda: {"n_turns": [], "cost_usd": [], "total_tokens": []})
    for r in task_results:
        out[r[group_key]]["n_turns"].append(r["n_turns"])
        out[r[group_key]]["cost_usd"].append(r["cost_usd"])
        out[r[group_key]]["total_tokens"].append(r["total_tokens"])
    return {
        level: {k: float(np.mean(v)) if v else float("nan") for k, v in metrics.items()}
        for level, metrics in out.items()
    }


def token_cost_effect_size(task_results: list[dict[str, Any]], group_key: str = "tone_level") -> dict[str, Any]:
    """Operationalizes "the pre-registered hypothesis" (README): Dobariya &
    Kumar's paper 3 (arXiv 2607.23915) reported output-token variation of
    44.3% across single-turn tone conditions, dwarfing their ~3% accuracy
    variation. This computes the same relative-variation statistic here --
    (max mean tokens - min mean tokens) / mean of means, as a percentage --
    so it's directly comparable to their number, not just "tokens differ by
    tone" without a way to judge the effect size against theirs.

    Returns per-tone mean total_tokens plus the overall relative variation
    percentage. The hypothesis (agentic cost effect > 44.3%, not less) is a
    plain comparison of the returned percentage against that published
    figure -- this function doesn't editorialize about whether it held.
    """
    by_group: dict[str, list[float]] = defaultdict(list)
    for r in task_results:
        by_group[r[group_key]].append(r["total_tokens"])

    means = {level: float(np.mean(v)) if v else float("nan") for level, v in by_group.items()}
    valid_means = [m for m in means.values() if m == m]  # drop NaN
    if len(valid_means) < 2:
        relative_variation_pct = float("nan")
    else:
        relative_variation_pct = (max(valid_means) - min(valid_means)) / np.mean(valid_means) * 100.0

    return {
        "mean_total_tokens_by_tone": means,
        "relative_variation_pct": relative_variation_pct,
        "published_single_turn_comparison_pct": 44.3,
    }


def compare_direction_to_study1(
    study1_pairwise: PairedComparison,
    study2_pairwise: PairedComparison,
) -> dict[str, Any]:
    """Does the tone effect on the agentic task point the same direction as
    on single-turn QA? A divergence is the headline result if it happens
    (task spec: "foreground" it)."""
    same_sign = (
        not np.isnan(study1_pairwise.mean_diff)
        and not np.isnan(study2_pairwise.mean_diff)
        and np.sign(study1_pairwise.mean_diff) == np.sign(study2_pairwise.mean_diff)
    )
    return {
        "study1_mean_diff": study1_pairwise.mean_diff,
        "study2_mean_diff": study2_pairwise.mean_diff,
        "same_direction": same_sign,
        "study1_p_value": study1_pairwise.p_value,
        "study2_p_value": study2_pairwise.p_value,
    }
