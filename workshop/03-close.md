# 5. What the extra turns buy

We regraded every turn of the 9,850 trajectories from the six mid-task runs against the
benchmark's own evaluator; the other 2,000 of the 11,850 (an opening-tone run, a micro-experiment
and a superseded batch) were not regraded (Appendix C.1). A **redundant step** is a turn after
which the graded range is unchanged: on Luna they make up **roughly 40–65% of each turn-count
effect**, and 35% of GLM's demand effect. Among trajectories with at least two **gradable outputs**
(turns whose code produced a readable value over the graded range), the first is already the best
in 77–91% on Luna and 69–88% on GLM.

The **graded fraction** is the share of the graded range matching the answer at the final turn;
**binary accuracy** requires every test case to pass, so the two can move independently. An
explicit statement that work remains raises the graded fraction by 2.8 points (95% CI
[+0.5, +5.2]); its three measurements agree (Cochran's *Q* = 0.20) though only one is significant
alone, and this outcome sits outside both correction families.

**No accuracy effect survives correction or replication**; the largest nominal one, +6.6 points for
"work remains", came back at −1.8 on identical tasks. Pooled across runs, with tasks resampled
jointly, the demand, praise and insult contrasts are each equivalent to zero within ±4 points (TOST
*p* = 0.0013, <0.0001, 0.0001). The praise pool is heterogeneous (Cochran's *Q* = 8.45, 3 df,
*p* = 0.038); under random effects its equivalence weakens to *p* = 0.0119 but holds. The bound is
looser than it looks: 30 of 50 tasks are never or always solved, so ±4 points over all 50 allows
about ±10 on the 20 that can change. The closing cue, measured once, is −2.6 points [−6.0, +0.6].

The regrade also caught our worst defect, a regrader that scored formula answers as empty; fixing
it reversed a conclusion. **Direction and significance reproduced on
remeasurement for the larger effects; point estimates did not.** Byte-identical praise gives −0.59
and −1.08 turns in two runs, within the 1.5×–3.4× spread across re-measurements of one contrast; the
shared control moving from 4.23 to 4.50 turns accounts for 0.27 of that 0.49 gap (Appendix C.4). We report ranges by default.

# 6. Limitations

Two models, one benchmark, fifty tasks, one scaffold. Beyond the demand-coding objection of §3:
**every construct is a single 28-token sentence**, where several paraphrases per construct is the
right design. **The agent is told its turn budget and asked to commit early**, so every effect is
measured in a budget-aware agent, and the closure result may depend on it. **The interjection is a
harness status note appended to tool output inside a user-role message**; text inside the task
data, or in a tool-role message, is untested. **Every contrast is against a neutral interjection,
not silence**; the one check against no interruption (*p* = 0.15, one model) was never repeated, so absolute
costs are unbounded.

# 7. What this means

For practitioners, manners are not the useful lever: messages implying continued work increased
persistence, mostly repeated work, and closing-like language curtailed a working agent. We did not
detect lost correctness, though the closing cue's interval reaches −6 points. What moved was **control flow**: a
status note appended to tool output changed when the agent stopped, without instructing it to.
Indirect prompt injection shows that once an application ingests content alongside tool results,
the line between data and instructions blurs [greshake-2023]; our result suggests that surface also
carries softer, pragmatic cues. For the tone literature: widely used manipulations vary
task-directed content together with register, so effects attributed to tone may not identify
register alone.
