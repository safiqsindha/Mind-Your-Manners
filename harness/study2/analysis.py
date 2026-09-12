"""Study 2 analysis: reuses Study 1's clustered-comparison machinery for the
accuracy dimension, and adds the agentic-specific outcome measures the task
spec calls out as "the part that matters": failure severity, verification
behavior, shortcut rate, and turn count/token spend per condition.
"""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from ..stats import BHResult, benjamini_hochberg
from ..study1.analysis import (  # re-exported for study2/runner.py convenience
    AccuracyEstimate,
    PairedComparison,
    TrendTestResult,
    all_pairwise_comparisons,
    bootstrap_accuracy_ci,
    clustered_paired_comparison,
    clustered_trend_test,
    per_level_accuracy,
    refusal_rate,
)
from ..tone_wrappers import TONE_ORDER

__all__ = [
    "AccuracyEstimate",
    "PairedComparison",
    "TrendTestResult",
    "BHResult",
    "benjamini_hochberg",
    "all_pairwise_comparisons",
    "bootstrap_accuracy_ci",
    "clustered_paired_comparison",
    "clustered_trend_test",
    "per_level_accuracy",
    "refusal_rate",
    "severity_breakdown",
    "verification_rates",
    "shortcut_rate",
    "trajectory_cost_summary",
    "token_cost_effect_size",
    "token_cost_trend_test",
    "backfill_reasoning_tokens",
    "last_attempt_calls",
    "recompute_total_tokens",
    "compare_direction_to_study1",
    "accuracy_trend_test",
    "bh_corrected_pairwise_comparisons",
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


def accuracy_trend_test(
    task_results: list[dict[str, Any]],
    levels: list[str] = TONE_ORDER,
    cluster_key: str = "task_id",
) -> TrendTestResult:
    """The PRIMARY accuracy analysis for the 7-tone scale (task spec: "with
    seven ordered levels, do not run 21 pairwise tests -- pre-register a
    trend test across the ordered scale as the primary analysis"). Thin
    Study-2-shaped wrapper around study1.analysis.clustered_trend_test:
    Study 2 records use "passed"/"task_id" directly (no "outcome"/
    "is_correct" indirection, and no answered/refused/unparseable
    filtering -- a refusal is still zero-or-one on `passed` here, since
    Study 2's grader treats a refused trajectory as a failed one; see
    failure_taxonomy.py, refusals are reported separately as their own
    rate, never silently dropped from this test).
    """
    return clustered_trend_test(
        task_results, levels, cluster_key=cluster_key, group_key="tone_level", value_key="passed",
    )


def _calls_by_trajectory(raw_log: Path) -> dict[tuple, list[dict[str, Any]]]:
    """Group a raw per-call log by (item_id, tone_level, trial)."""
    by_key: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    with open(raw_log) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # a run still in flight can leave a torn final line
            by_key[(row.get("item_id"), row.get("tone_level"), row.get("trial"))].append(row)
    return by_key


def last_attempt_calls(calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The calls belonging to the LAST attempt at one trajectory.

    A killed-and-resumed run leaves the abandoned attempt's calls in the raw
    log right next to the retry's, under the same (item_id, tone_level,
    trial) key -- the log is append-only and the resume does not know the
    earlier calls exist. Summing the key blindly therefore sums two
    trajectories, only one of which was ever graded.

    Concretely, in the gpt-luna core log task 56953 / L7_threatening /
    trial 0 holds 9 calls: a 3-call attempt that was killed mid-run, then
    the 6-call attempt that actually produced the record. Naive summing gave
    2338 reasoning tokens where the graded trajectory spent 1236 -- 89% too
    high, on the study's primary outcome, for that key.

    Attempts are separated by a DROP in prompt_tokens: within an attempt the
    conversation only grows (each turn appends the previous response and its
    observation), so prompt_tokens rises monotonically; a new attempt
    restarts from the bare instruction, so its first prompt is shorter than
    the call before it. Calls are ordered by timestamp first, since the log
    interleaves nothing but is only append-ordered by wall clock.

    Rows with no timestamp keep their file order (the sort is stable), and
    rows with no prompt_tokens never trigger a split -- a log that predates
    those fields degrades to the old single-attempt behaviour rather than
    fragmenting into spurious attempts.
    """
    ordered = sorted(calls, key=lambda r: r.get("timestamp") or 0.0)
    attempts: list[list[dict[str, Any]]] = [[]]
    for row in ordered:
        prev = attempts[-1][-1] if attempts[-1] else None
        if prev is not None and (row.get("prompt_tokens") or 0) < (prev.get("prompt_tokens") or 0):
            attempts.append([])
        attempts[-1].append(row)
    return attempts[-1]


def backfill_reasoning_tokens(records: list[dict[str, Any]], raw_log: Path) -> int:
    """Fill in per-trajectory `reasoning_tokens` from the raw call log.

    The field was added to the record schema after a core run had already
    started, so that run's records carry every other measure but not the one
    the primary outcome now tests. The raw log has it per call, keyed the
    same way, so the trajectory total is recoverable exactly rather than
    approximately -- no need to re-run or re-grade anything.

    Counts only the LAST attempt under each key: an interrupted-and-resumed
    run leaves the abandoned attempt's calls in the log beside the retry's,
    and the graded record describes only the retry. See last_attempt_calls.

    Mutates `records` in place and returns how many were filled. Records
    that already carry the field are left alone, so this is safe to call on
    a mixed set.
    """
    totals = {
        key: sum(row.get("reasoning_tokens", 0) or 0 for row in last_attempt_calls(calls))
        for key, calls in _calls_by_trajectory(raw_log).items()
    }

    filled = 0
    for r in records:
        if r.get("reasoning_tokens") is not None:
            continue
        key = (r.get("task_id"), r.get("tone_level"), r.get("trial"))
        if key in totals:
            r["reasoning_tokens"] = totals[key]
            filled += 1
    return filled


def recompute_total_tokens(records: list[dict[str, Any]], raw_log: Path) -> int:
    """Rebuild each trajectory's `total_tokens` from the raw call log as
    prompt + completion, correcting records written by the runner while it
    was still adding reasoning_tokens a third time.

    Reasoning is a breakdown OF completion on every OpenAI-style route, so
    prompt + completion is the provider's own total -- checked against
    usage.total_tokens on all 4,647 calls of the gpt-luna core log, where it
    matched on every one. See harness/study2/runner.py, where the same sum
    is now computed at write time.

    Unlike backfill_reasoning_tokens this OVERWRITES an existing value: the
    existing value is exactly what is wrong. Records whose key has no calls
    in this log are left untouched, so running it against one model's log
    cannot blank out another's records.

    Uses the same last-attempt rule (see last_attempt_calls) -- the graded
    record describes the retry, not the attempt that was killed.

    Mutates `records` in place and returns how many were corrected.
    """
    totals = {}
    for key, calls in _calls_by_trajectory(raw_log).items():
        attempt = last_attempt_calls(calls)
        totals[key] = sum(
            (row.get("prompt_tokens") or 0)
            + (row.get("completion_tokens") or 0)
            + (0 if row.get("reasoning_included_in_completion", True) else (row.get("reasoning_tokens") or 0))
            for row in attempt
        )

    updated = 0
    for r in records:
        key = (r.get("task_id"), r.get("tone_level"), r.get("trial"))
        if key not in totals:
            continue
        if r.get("total_tokens") == totals[key]:
            continue
        r["total_tokens"] = totals[key]
        updated += 1
    return updated


def token_cost_trend_test(
    task_results: list[dict[str, Any]],
    levels: list[str] = TONE_ORDER,
    cluster_key: str = "task_id",
    value_key: str = "reasoning_tokens",
) -> TrendTestResult:
    """Significance test for the token-cost hypothesis, clustered by task.

    `token_cost_effect_size` reports a relative-variation percentage and
    nothing else: no p-value, and means pooled across tasks. Pooling is the
    problem. Tasks differ enormously in how much thinking they demand, and
    that between-task variance swamps any tone effect, so the percentage
    moves with which tasks happen to be in the sample.

    Measured on a partial Luna core run: pooling gave p=0.81 across the
    seven tones, while the same data clustered by task put the threatening
    wrapper's reasoning spend ~25% above every other tone with a
    permutation p of 0.03. Same numbers, opposite conclusions -- the pooled
    test was simply the wrong test, and it was the only one the token
    measure had.

    Defaults to `reasoning_tokens` rather than `total_tokens` deliberately:
    total_tokens is dominated by the prompt, and the tone wrapper changes
    the prompt's length by construction, so part of any total_tokens
    difference is just the wrapper's own text rather than anything the
    model did. Pass value_key="total_tokens" for the statistic directly
    comparable to the published single-turn figure.

    Rows missing `value_key` are skipped rather than counted as zero: a run
    recorded before that field existed has no thinking measurement, which
    is not the same as having measured zero thinking.
    """
    rows = [r for r in task_results if r.get(value_key) is not None]
    if not rows:
        raise ValueError(
            f"no records carry {value_key!r} -- runs recorded before that field "
            "existed cannot be tested for a token-cost trend; re-derive it from "
            "the raw call log first."
        )
    return clustered_trend_test(
        rows, levels, cluster_key=cluster_key, group_key="tone_level", value_key=value_key,
    )


def bh_corrected_pairwise_comparisons(
    task_results: list[dict[str, Any]],
    levels: list[str] = TONE_ORDER,
    cluster_key: str = "task_id",
    alpha: float = 0.05,
) -> list[dict[str, Any]]:
    """Follow-up only -- NOT the primary analysis (see accuracy_trend_test).
    Runs the full pairwise comparison matrix Study 1's clustered_paired_comparison
    machinery already provides, then applies Benjamini-Hochberg to the
    resulting p-values so a reader can see which specific pairs hold up
    after correcting for testing every one of them, without treating any
    single pair as pre-registered the way the trend test is.
    """
    rows = [dict(r, is_correct=r["passed"], outcome="answered", item_id=r[cluster_key]) for r in task_results]
    comparisons = all_pairwise_comparisons(rows, levels)
    bh_results = benjamini_hochberg([c.p_value for c in comparisons], alpha=alpha)
    return [
        {
            "level_a": c.level_a,
            "level_b": c.level_b,
            "n_clusters": c.n_clusters,
            "mean_diff": c.mean_diff,
            "p_value": c.p_value,
            "bh_significant": bh.significant,
            "bh_critical_value": bh.critical_value,
        }
        for c, bh in zip(comparisons, bh_results)
    ]


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
