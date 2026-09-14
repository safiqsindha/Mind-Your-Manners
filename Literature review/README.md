# Literature Review — *Mind Your Manners: prompt tone and agentic work*

Prepared 2026-09-14 for the workshop paper.

## Contents

| File | What's in it |
|---|---|
| [`01-sources.md`](01-sources.md) | 38 source entries, grouped A–G per the brief. Citation, claim, method, numbers, relation to us, quotable line. |
| [`02-synthesis.md`](02-synthesis.md) | The five requested summaries: preempts, contradictions, must-cites, gaps, terminology. **Read this first.** |
| [`03-verification-log.md`](03-verification-log.md) | What was read in full, what came from abstracts, what is UNVERIFIED. |

## The one-paragraph answer

**You are not preempted on your core claim.** Nobody has manipulated tone mid-task inside
an agentic loop, and nobody has separated politeness from task-demand as an experimental
variable. But three things are further along than you may expect, and you must engage them
head-on:

1. **The paper you are rebutting has already largely rebutted itself.** Dobariya & Kumar's
   AMCIS 2026 full paper ([2605.29027](https://arxiv.org/abs/2605.29027)) re-ran their own
   GPT-4o experiment and got 82.2% (Very Polite) vs 82.6% (Very Rude) — the 80.8→84.8
   effect from the short paper did not replicate, and they label GPT-4o "Weak / noisy".
2. **"Tone moves length, not accuracy" is already published** — in single-turn
   ([2607.23915](https://arxiv.org/abs/2607.23915), and Yin et al. 2024 on summarization
   length). Your accuracy null and your effort measures are novel only in their *agentic*
   operationalization. Frame accordingly.
3. **An agentic, preregistered, 4,643-run study of prompt wording → agent cost at equal
   quality already exists** ([2608.01347](https://arxiv.org/abs/2608.01347)). It does not
   test tone, and it manipulates only the opening prompt — but it owns the "prompt wording
   changes agent spend, not correctness" result, and its best-performing arm is literally a
   prompt containing *an explicit stop condition*. This is your nearest neighbour.

**One finding of yours is actively contradicted by prior work:** praise shortening output.
Three separate studies find positive/polite framing makes responses *longer*, not shorter.
See [`02-synthesis.md` §2](02-synthesis.md).

## Rules followed

- Every arXiv ID in the brief was checked against arXiv directly; all three exist.
- Three papers were read in full text (PDF extraction), not from abstracts — see the log.
- Negative results and failed replications are included and flagged.
- Anything not verified is marked **UNVERIFIED** inline.
