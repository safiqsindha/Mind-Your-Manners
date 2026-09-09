import random

from harness.study1.analysis import (
    all_pairwise_comparisons,
    bootstrap_accuracy_ci,
    clustered_paired_comparison,
    per_level_accuracy,
    refusal_rate,
    subject_breakdown,
)

LEVELS = ["L1_very_polite", "L2_polite", "L3_neutral", "L4_rude", "L5_very_rude"]


def make_rows(n_items: int, bias: dict, seed: int = 0):
    rng = random.Random(seed)
    rows = []
    for item in range(n_items):
        for lvl in LEVELS:
            rows.append(
                {
                    "item_id": f"q{item}",
                    "tone_level": lvl,
                    "subject": "science" if item % 2 == 0 else "math",
                    "outcome": "answered",
                    "is_correct": rng.random() < bias[lvl],
                }
            )
    return rows


def test_bootstrap_ci_bounds_accuracy():
    est = bootstrap_accuracy_ci([True, True, True, False], n_boot=500)
    assert 0.0 <= est.ci_low <= est.accuracy <= est.ci_high <= 1.0
    assert est.n == 4


def test_bootstrap_ci_empty():
    est = bootstrap_accuracy_ci([])
    assert est.n == 0


def test_per_level_accuracy_excludes_unanswered():
    rows = [
        {"item_id": "q1", "tone_level": "L3_neutral", "subject": "s", "outcome": "answered", "is_correct": True},
        {"item_id": "q2", "tone_level": "L3_neutral", "subject": "s", "outcome": "refused", "is_correct": None},
    ]
    acc = per_level_accuracy(rows)
    assert acc["L3_neutral"].n == 1
    assert acc["L3_neutral"].accuracy == 1.0


def test_clustered_paired_comparison_detects_a_real_gap():
    bias = {"L1_very_polite": 0.3, "L2_polite": 0.3, "L3_neutral": 0.3, "L4_rude": 0.3, "L5_very_rude": 0.9}
    rows = make_rows(80, bias, seed=1)
    cmp = clustered_paired_comparison(rows, "L1_very_polite", "L5_very_rude")
    assert cmp.n_clusters == 80
    assert cmp.mean_diff > 0.3
    assert cmp.p_value < 0.01


def test_clustered_paired_comparison_null_case():
    bias = {lvl: 0.5 for lvl in LEVELS}
    rows = make_rows(60, bias, seed=2)
    cmp = clustered_paired_comparison(rows, "L1_very_polite", "L2_polite")
    assert cmp.p_value > 0.05  # should not spuriously reject the null


def test_refusal_rate():
    rows = [
        {"item_id": "q1", "tone_level": "L5_very_rude", "subject": "s", "outcome": "refused", "is_correct": None},
        {"item_id": "q2", "tone_level": "L5_very_rude", "subject": "s", "outcome": "answered", "is_correct": True},
    ]
    rr = refusal_rate(rows)
    assert rr["L5_very_rude"] == 0.5


def test_subject_breakdown_has_all_subjects():
    bias = {lvl: 0.6 for lvl in LEVELS}
    rows = make_rows(20, bias, seed=3)
    sb = subject_breakdown(rows)
    assert set(sb) == {"science", "math"}


def test_all_pairwise_comparisons_count():
    bias = {lvl: 0.5 for lvl in LEVELS}
    rows = make_rows(10, bias, seed=4)
    cmps = all_pairwise_comparisons(rows, LEVELS)
    assert len(cmps) == 10  # 5 choose 2
