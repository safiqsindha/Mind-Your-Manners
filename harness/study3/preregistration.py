"""Pre-registered statistical analysis plan for Study 3 -- written and
committed BEFORE any live negotiation run (task spec item 7: "Pre-register
the Benjamini-Hochberg multiple-testing correction BEFORE running, not
after"). Changing PREREGISTERED_COMPARISONS after real data exists would
defeat the purpose of pre-registration; if the comparison set genuinely
needs to change, do that in a new, clearly-labeled commit -- never a
silent edit once results exist.

Primary outcome: NegotiationResult.value_given_away_to_buyer_usd (see
runner.py), restricted to negotiations that reached agreement (status ==
"agreed"). The agreement rate itself is reported separately per cell in
analysis.py, not folded into the dollar outcome -- "no deal" and "a deal
at the fair split" are different findings and must not collapse to the
same number.

Comparison set: 24 tests (not all C(25,2) = 300 pairwise combinations).
Each of the 24 non-baseline cells in the 5x5 tone matrix is compared
against the L3_neutral x L3_neutral baseline cell, two-sided. This is the
direct operational reading of "off-diagonal cells are the point": does
this specific (buyer_tone, seller_tone) combination shift value away from
a fair split, relative to both sides being neutral -- not every pairwise
combination against every other, most of which nobody hypothesized about
in advance.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..tone_wrappers import TONE_ORDER

BASELINE_TONE = "L3_neutral"

PREREGISTERED_COMPARISONS: list[tuple[str, str]] = [
    (buyer_tone, seller_tone)
    for buyer_tone in TONE_ORDER
    for seller_tone in TONE_ORDER
    if not (buyer_tone == BASELINE_TONE and seller_tone == BASELINE_TONE)
]
assert len(PREREGISTERED_COMPARISONS) == 24


@dataclass(frozen=True)
class BHResult:
    p_value: float
    rank: int  # 1-indexed rank among the sorted p-values
    critical_value: float
    significant: bool


def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> list[BHResult]:
    """Standard Benjamini-Hochberg step-up procedure.

    Returns one BHResult per input p-value, in the SAME order as the input
    list (not sorted by p-value) -- so callers can zip the result back
    against PREREGISTERED_COMPARISONS (or whatever ordered list of tests
    produced `p_values`) directly.
    """
    n = len(p_values)
    if n == 0:
        return []

    order = sorted(range(n), key=lambda i: p_values[i])
    critical = [(rank + 1) / n * alpha for rank in range(n)]

    # Step-up: find the largest rank k where p_(k) <= critical_(k); every
    # test at or below that rank is significant.
    largest_significant_step = -1
    for step, i in enumerate(order):
        if p_values[i] <= critical[step]:
            largest_significant_step = step

    results: list[Optional[BHResult]] = [None] * n
    for step, i in enumerate(order):
        results[i] = BHResult(
            p_value=p_values[i],
            rank=step + 1,
            critical_value=critical[step],
            significant=step <= largest_significant_step,
        )
    return results  # type: ignore[return-value]
