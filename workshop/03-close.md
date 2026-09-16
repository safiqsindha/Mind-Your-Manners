# 5. What the extra turns buy

We regraded every turn of 9,850 trajectories against the benchmark's own evaluator, turning a
binary verdict into a curve. Roughly **55–65% of each turn-count effect is redundant steps**, and
among trajectories that could improve, the first gradable attempt is already the best in 80–91%.
The remainder is real but small: an explicit statement that work remains raises the graded
fraction by 2.8 points (95% CI [+0.005, +0.052]), replicated across three runs. **No accuracy
effect survives correction or replication** across the seven runs in which accuracy was tested.

This regrade also caught the study's worst defect: it had not been recalculating formula-writing
turns, which manufactured the appearance of run-to-run instability in the very contrast we were
using to argue for repeated measurement. Six substantive claims about our own data were withdrawn
over the course of this work. Direction and significance replicate wherever an effect is large;
point estimates span 1.5× to 3.4× across re-measurements of the same contrast on the same model.
We report ranges by default and recommend the literature do the same.

# 6. Limitations

Two models, one benchmark, fifty tasks, one agent scaffold. Beyond the demand-coding objection in
§3, three limits bear directly on how far these results travel. **Every construct is a single
28-token sentence**; a stimulus-sampling design with several paraphrases per construct is the
right version of this experiment and we did not run it. **The interjection arrives as an execution
observation**, not as a fresh user turn, and whether an agent responds the same way to a
user-channel message is untested — a plausible moderator of the closing-cue result in particular.
**Every contrast is against a neutral interjection rather than silence**; the one comparison of
interruption against no interruption is *p* = 0.15, on one model, and was never rechecked, so any
reading of an arm's absolute cost against an uninterrupted agent is unbounded.

# 7. What this means

For practitioners the inference is the reverse of the popular one. Manners are not the lever;
demand is, and the work it buys is mostly repeated. The hazard runs the other way: a pleasantry to
an agent that is still working reads as a closing move and curtails it. For the literature, the
claim is narrower and harder to dispute than "these results are wrong" — it is that **the factor
these papers vary is not the factor they name**, and that an agentic setting with verifiable
ground truth is where the difference becomes visible.
