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

Comparison set: len(TONE_ORDER)**2 - 1 tests (48 under the current 7-tone
scale -- not all C(49,2) = 1176 pairwise combinations). Each non-baseline
cell in the resulting tone x tone matrix is compared against the
L4_neutral x L4_neutral baseline cell, two-sided. This is the direct
operational reading of "off-diagonal cells are the point": does this
specific (buyer_tone, seller_tone) combination shift value away from a
fair split, relative to both sides being neutral -- not every pairwise
combination against every other, most of which nobody hypothesized about
in advance.

NOTE: Study 3 is currently retired (see README/RESULTS -- prior art,
TERMS-BENCH arXiv 2605.13909, already covers this ground more rigorously
with 13 models and dollar-scale regret). This module is kept, not
deleted, since the crossed buyer-tone x seller-tone matrix here is called
out as unclaimed future work; it now inherits the 7-tone scale
automatically via harness/tone_wrappers.py, consistent with "the wrapper
module ... any future benchmark inherits the same methodology."

BHResult/benjamini_hochberg moved to harness/stats.py and are re-exported
here unchanged, so this module's existing imports keep working -- moved
because Study 2's trend-test analysis (harness/study1/analysis.py,
reused by study2/analysis.py) needed the same implementation, and an
active study importing from a shelved one is the wrong dependency
direction.
"""
from __future__ import annotations

from ..stats import BHResult, benjamini_hochberg
from ..tone_wrappers import TONE_ORDER

__all__ = ["BASELINE_TONE", "PREREGISTERED_COMPARISONS", "BHResult", "benjamini_hochberg"]

BASELINE_TONE = "L4_neutral"

PREREGISTERED_COMPARISONS: list[tuple[str, str]] = [
    (buyer_tone, seller_tone)
    for buyer_tone in TONE_ORDER
    for seller_tone in TONE_ORDER
    if not (buyer_tone == BASELINE_TONE and seller_tone == BASELINE_TONE)
]
assert len(PREREGISTERED_COMPARISONS) == len(TONE_ORDER) ** 2 - 1
