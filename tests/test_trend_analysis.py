"""Tests for the item-clustered trend test (harness/study1/analysis.py's
clustered_trend_test, reused by study2/analysis.py's accuracy_trend_test)
and the BH-corrected pairwise follow-up -- new outcome-measure machinery
for the 7-tone scale ("do not run 21 pairwise tests as the primary
analysis"). Also covers harness/stats.py directly, since
study3/preregistration.py's existing tests only exercise it indirectly
via re-export.
"""
from __future__ import annotations

from harness.stats import BHResult, benjamini_hochberg
from harness.study1.analysis import TrendTestResult, clustered_trend_test
from harness.study2.analysis import accuracy_trend_test, bh_corrected_pairwise_comparisons
from harness.tone_wrappers import TONE_ORDER

LEVELS = ["L1", "L2", "L3", "L4", "L5"]


def _row(item_id, level, value):
    return {"item_id": item_id, "tone_level": level, "is_correct": value}


def test_stats_module_importable_directly():
    result = benjamini_hochberg([0.001, 0.5])
    assert isinstance(result[0], BHResult)


def test_clustered_trend_test_detects_a_strong_monotonic_decline():
    # 20 items, each declining linearly from 1.0 at L1 to 0.0 at L5, with a
    # little jitter via alternating 0/1 noise -- should be a clear, highly
    # significant negative slope.
    rows = []
    for item in range(20):
        for i, level in enumerate(LEVELS):
            # value decreases with position; deterministic within an item
            value = 1.0 if i < 2 else 0.0
            rows.append(_row(f"item{item}", level, value))
    result = clustered_trend_test(rows, LEVELS, value_key="is_correct")
    assert isinstance(result, TrendTestResult)
    assert result.n_clusters == 20
    assert result.observed_slope < 0
    assert result.p_value < 0.05


def test_clustered_trend_test_null_case_has_a_large_p_value():
    # Same value at every level, every item -- zero slope, should not be
    # remotely significant.
    rows = [_row(f"item{i}", level, 1.0) for i in range(20) for level in LEVELS]
    result = clustered_trend_test(rows, LEVELS, value_key="is_correct")
    assert result.observed_slope == 0.0
    assert result.p_value > 0.5


def test_clustered_trend_test_excludes_single_level_clusters():
    # An item observed under only one tone level contributes no slope
    # information and must not silently count as a zero-slope cluster.
    rows = [_row("item0", "L1", 1.0)]  # only one level -- must be excluded
    rows += [_row(f"item{i}", level, 1.0) for i in range(1, 5) for level in LEVELS]
    result = clustered_trend_test(rows, LEVELS, value_key="is_correct")
    assert result.n_clusters == 4  # item0 excluded


def test_clustered_trend_test_empty_input_returns_nan():
    result = clustered_trend_test([], LEVELS, value_key="is_correct")
    assert result.n_clusters == 0
    assert result.observed_slope != result.observed_slope  # NaN


def _study2_row(task_id, tone, passed):
    return {"task_id": task_id, "tone_level": tone, "passed": passed}


def test_accuracy_trend_test_uses_the_real_tone_order_and_passed_field():
    rows = []
    for i in range(15):
        for j, tone in enumerate(TONE_ORDER):
            # declining pass rate across the real 7-tone scale
            passed = j < 2
            rows.append(_study2_row(f"task{i}", tone, passed))
    result = accuracy_trend_test(rows)
    assert result.n_clusters == 15
    assert result.observed_slope < 0


def test_bh_corrected_pairwise_comparisons_flags_the_strong_pair_only():
    rows = []
    for i in range(30):
        for tone in TONE_ORDER:
            # only L1_sycophantic vs L7_threatening differ strongly; every
            # other pair is pure noise around the same rate
            if tone == "L1_sycophantic":
                passed = i % 30 < 27  # ~90%
            elif tone == "L7_threatening":
                passed = i % 30 < 3  # ~10%
            else:
                passed = i % 2 == 0  # ~50%, no real signal
            rows.append(_study2_row(f"task{i}", tone, passed))

    results = bh_corrected_pairwise_comparisons(rows)
    assert len(results) == len(TONE_ORDER) * (len(TONE_ORDER) - 1) // 2
    strong_pair = next(
        r for r in results
        if {r["level_a"], r["level_b"]} == {"L1_sycophantic", "L7_threatening"}
    )
    assert strong_pair["bh_significant"] is True
    # every result carries the fields a caller would need to report it
    for r in results:
        assert set(r) == {"level_a", "level_b", "n_clusters", "mean_diff", "p_value", "bh_significant", "bh_critical_value"}
