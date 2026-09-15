# Literature Review — *Mind Your Manners: prompt tone and agentic work*

Prepared 2026-09-14 for the workshop paper.

## Contents

| File | What's in it |
|---|---|
| [`01-sources.md`](01-sources.md) | 43 entries grouped A–G per the brief — 29 cited, 14 background — every heading tagged `CITED` or `BACKGROUND` with its read depth. Citation, claim, method, numbers, relation to us, quotable line. |
| [`02-synthesis.md`](02-synthesis.md) | The five requested summaries: preempts, contradictions, must-cites, gaps, terminology. **Read this first.** |
| [`03-verification-log.md`](03-verification-log.md) | Every error found and corrected, claims downgraded, and what remains UNVERIFIED. |

**All 29 cited sources have been read in full text.** A second verification pass over the 25
that had only been read at abstract level found 15 citation-level errors, downgraded 8 claims,
and strengthened 9 — all recorded in the log. A third pass cross-checked the review against
`RESULTS.md` and corrected how it described our *own* numbers (see the log's "Pass 3"). Three corrections change the paper rather than a
footnote:

- **arXiv:2608.01347 has six versions.** The current v6 changed the title, reports 4,644 runs
  not 4,643, and cut both quotes previously attributed to it. Cite a specific version.
- **Our 20-turn ceiling is our own.** SpreadsheetBench's official multi-round protocol caps at
  **five** rounds — and their own GPT-4o *declines* from single- to multi-round, which the
  authors attribute to redundant re-fetching. That is prior evidence for our mechanism, from
  our own substrate.
- **The face-threat account of closing is ours, not ELEPHANT's.** Presenting it as theirs would
  be a misattribution.

## The one-paragraph answer

**You are not preempted on your core claim.** Nobody has manipulated tone mid-task inside
an agentic loop, and nobody has separated politeness from task-demand as an experimental
variable. But three things are further along than you may expect, and you must engage them
head-on:

1. **The paper you are rebutting has already largely rebutted itself.** Dobariya & Kumar's
   AMCIS 2026 full paper ([2605.29027](https://arxiv.org/abs/2605.29027)) re-ran their own
   GPT-4o experiment and got 82.2% (Very Polite) vs 82.6% (Very Rude) — the 80.8→84.8
   effect from the short paper did not replicate, and they label GPT-4o "Weak / noisy" — but the
   re-run is **not a null**: both extremes significantly beat Neutral on the same 50 questions,
   a U-shape in extremity rather than a rudeness gradient (paper §3.3).
2. **"Tone moves length, not accuracy" is already published** — in single-turn
   ([2607.23915](https://arxiv.org/abs/2607.23915), and Yin et al. 2024 on summarization
   length). Your accuracy null and your effort measures are novel only in their *agentic*
   operationalization. Frame accordingly.
3. **An agentic, preregistered, 4,644-run (v6; 4,643 in v1) study of prompt wording → agent
   cost at equal quality already exists** ([2608.01347](https://arxiv.org/abs/2608.01347)). It does not
   test tone, and it manipulates only the opening prompt — but it owns the "prompt wording
   changes agent spend, not correctness" result, and its best-performing arm is literally a
   prompt containing *an explicit stop condition*. This is your nearest neighbour.

**One finding of yours is actively contradicted by prior work:** praise shortening output.
Three separate studies find positive/polite framing makes responses *longer*, not shorter.
See [`02-synthesis.md` §2](02-synthesis.md).

**That contradiction has now been tested against our own data, and the escape route I proposed
is closed** (`results/analysis/praise_turn_vs_trajectory.py`). Praise shortens the trajectory
*and* cuts total output on the praise-alone arms and in the Q4-vs-Q5 contrast; there is no
compensating longer final turn. (Per-turn tokens are not in
the graded records, but they *are* in the per-call raw logs, one log per arm — recovery is free
if those logs still exist.)

**On §5's wording:** `RESULTS.md` already has this right — its table reports Q4 (praise + "work
remains") at **+0.50 turns vs control, p = 0.020**, and frames the praise effect as the
**Q4-vs-Q5 contrast, −1.35 turns**. The only hazard is the prose summary there ("doing so while
telling it there is more to do does not prevent that"), which a reader takes as Q4 < control.
Make sure the paper's prose follows the table. Details in `02-synthesis.md` §2(a) and §7.2.

## Rules followed

- Every arXiv ID cited was checked against arXiv directly, including the three named in the brief.
- All 29 cited papers were read in full text, not from abstracts — see the log.
- Negative results and failed replications are included and flagged.
- Anything not verified is marked **UNVERIFIED** inline.
