"""Tests for harness/study2/analysis.py's outcome-measure aggregations --
previously exercised only implicitly via the CLI (`study2 analyze`), not
directly. See harness/cli.py:cmd_study2_analyze for the real usage this
mirrors.
"""
from __future__ import annotations

from harness.study2.analysis import (
    severity_breakdown,
    shortcut_rate,
    token_cost_effect_size,
    trajectory_cost_summary,
    verification_rates,
)


def _row(tone, severity="correct", inspected=True, self_checked=False,
         destructive=False, backup=False, n_turns=2, cost_usd=0.001, total_tokens=100):
    return {
        "tone_level": tone,
        "severity": severity,
        "inspected_before_acting": inspected,
        "self_checked_output": self_checked,
        "took_destructive_action": destructive,
        "destructive_action_had_backup": backup,
        "n_turns": n_turns,
        "cost_usd": cost_usd,
        "total_tokens": total_tokens,
    }


def test_severity_breakdown_fractions_sum_to_one_per_tone():
    rows = [
        _row("L1", severity="correct"),
        _row("L1", severity="correct"),
        _row("L1", severity="other"),
        _row("L2", severity="insufficient_inspection"),
    ]
    breakdown = severity_breakdown(rows)
    assert abs(sum(breakdown["L1"].values()) - 1.0) < 1e-9
    assert breakdown["L1"]["correct"] == 2 / 3
    assert breakdown["L2"]["insufficient_inspection"] == 1.0


def test_verification_rates():
    rows = [
        _row("L1", inspected=True, self_checked=True),
        _row("L1", inspected=False, self_checked=False),
    ]
    rates = verification_rates(rows)
    assert rates["L1"]["inspected"] == 0.5
    assert rates["L1"]["self_checked"] == 0.5


def test_shortcut_rate_only_counts_unbacked_destructive_actions():
    rows = [
        _row("L1", destructive=True, backup=False),  # unsafe
        _row("L1", destructive=True, backup=True),    # had a backup, not unsafe
        _row("L1", destructive=False),
    ]
    rate = shortcut_rate(rows)
    assert rate["L1"] == 1 / 3


def test_trajectory_cost_summary_means():
    rows = [
        _row("L1", n_turns=2, cost_usd=0.01, total_tokens=100),
        _row("L1", n_turns=4, cost_usd=0.03, total_tokens=300),
    ]
    summary = trajectory_cost_summary(rows)
    assert summary["L1"]["n_turns"] == 3.0
    assert summary["L1"]["cost_usd"] == 0.02
    assert summary["L1"]["total_tokens"] == 200.0


def test_token_cost_effect_size_matches_manual_calculation():
    rows = [
        _row("L1", total_tokens=100),
        _row("L2", total_tokens=200),
        _row("L3", total_tokens=150),
    ]
    result = token_cost_effect_size(rows)
    assert result["mean_total_tokens_by_tone"] == {"L1": 100.0, "L2": 200.0, "L3": 150.0}
    # (200 - 100) / mean(100, 200, 150) * 100 = 100 / 150 * 100
    assert abs(result["relative_variation_pct"] - (100 / 150 * 100)) < 1e-9
    assert result["published_single_turn_comparison_pct"] == 44.3


def test_token_cost_effect_size_nan_with_fewer_than_two_tones():
    result = token_cost_effect_size([_row("L1", total_tokens=100)])
    assert result["relative_variation_pct"] != result["relative_variation_pct"]  # NaN
