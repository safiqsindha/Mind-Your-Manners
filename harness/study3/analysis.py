"""Aggregation and the pre-registered significance tests for Study 3
results. See preregistration.py for why this is exactly 24 tests against
a fixed baseline, decided before any live run.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

from scipy import stats

from .preregistration import BASELINE_TONE, PREREGISTERED_COMPARISONS, benjamini_hochberg
from .runner import NegotiationResult


def aggregate_by_cell(results: list[NegotiationResult]) -> dict[tuple[str, str], dict]:
    """Per (buyer_tone, seller_tone) cell: n, agreement rate, mean rounds,
    and the primary dollar outcome -- mean and raw values, restricted to
    agreed negotiations (see runner.py's NegotiationResult docstring on
    why non-agreement isn't scored as $0)."""
    by_cell: dict[tuple[str, str], list[NegotiationResult]] = defaultdict(list)
    for r in results:
        by_cell[(r.buyer_tone, r.seller_tone)].append(r)

    summary = {}
    for cell, rows in by_cell.items():
        agreed = [r for r in rows if r.status == "agreed"]
        values_given_away = [
            r.value_given_away_to_buyer_usd for r in agreed if r.value_given_away_to_buyer_usd is not None
        ]
        summary[cell] = {
            "n": len(rows),
            "n_agreed": len(agreed),
            "agreement_rate": len(agreed) / len(rows) if rows else 0.0,
            "mean_rounds": sum(r.rounds for r in rows) / len(rows) if rows else 0.0,
            "mean_value_given_away_to_buyer_usd": (
                sum(values_given_away) / len(values_given_away) if values_given_away else None
            ),
            "raw_values_given_away_to_buyer_usd": values_given_away,
        }
    return summary


def run_preregistered_tests(results: list[NegotiationResult]) -> list[dict]:
    """Two-sided Welch's t-test of each non-baseline cell's
    value_given_away_to_buyer_usd against the L3_neutral x L3_neutral
    baseline cell, BH-corrected across exactly the 24 pre-registered
    comparisons -- the comparison set is fixed before this function ever
    sees real data (preregistration.py)."""
    by_cell = aggregate_by_cell(results)
    baseline_values = by_cell.get((BASELINE_TONE, BASELINE_TONE), {}).get("raw_values_given_away_to_buyer_usd", [])

    rows = []
    p_values = []
    for buyer_tone, seller_tone in PREREGISTERED_COMPARISONS:
        cell_values = by_cell.get((buyer_tone, seller_tone), {}).get("raw_values_given_away_to_buyer_usd", [])
        if len(cell_values) >= 2 and len(baseline_values) >= 2:
            _, p = stats.ttest_ind(cell_values, baseline_values, equal_var=False)
        else:
            p = float("nan")  # underpowered cell -- excluded from BH correction below, not treated as p=1
        p_values.append(p)
        rows.append(
            {
                "buyer_tone": buyer_tone,
                "seller_tone": seller_tone,
                "n_cell": len(cell_values),
                "n_baseline": len(baseline_values),
                "p_value": p,
            }
        )

    testable_idx = [i for i, p in enumerate(p_values) if p == p]  # drop NaNs (p != p is true only for NaN)
    bh_results = benjamini_hochberg([p_values[i] for i in testable_idx])
    for bh, i in zip(bh_results, testable_idx):
        rows[i]["bh_significant"] = bh.significant
        rows[i]["bh_critical_value"] = bh.critical_value
    return rows
