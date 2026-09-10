"""Multiple-testing correction shared across studies.

Extracted from harness/study3/preregistration.py (where it was originally
written and tested for Study 3's 48-comparison pre-registration) so Study
2's analysis can reuse the same, already-tested implementation without an
active study importing from a shelved one. study3/preregistration.py
re-exports BHResult/benjamini_hochberg from here for backward
compatibility with its existing imports/tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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
    against whatever ordered list of tests produced `p_values` directly.
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
