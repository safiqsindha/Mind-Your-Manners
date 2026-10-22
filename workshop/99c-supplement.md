# C. Supplementary analyses

## C.1 Runs and the 22-contrast family

All 11,850 scheduled trajectories, by run. *Delivered* means the interjection fired before the trajectory ended; firing is decided before delivery, so it differs by arm only by chance (probe run, injection at turn 2: 54.0–59.5% across the four arms). *Primary analysis* means delivered and, in the register run, injected at turn 1 or 2 (turn 0 is Appendix C.2). Runs without a firing flag, or without a mid-task interjection, show a dash.

| Run | Model | Turn budget | Scheduled | Delivered | Primary analysis | Regraded per turn |
|---|---|---:|---:|---:|---:|:---:|
| Opening tone (wrapper on the first message, no mid-task interjection) | Luna | 10 | 1,050 | — | — | no |
| Micro-experiment: threatening vs neutral, re-injected mid-task | Luna | 10 | 800 | — | — | no |
| Superseded control batch (earlier wrapper version) | Luna | 10 | 150 | — | — | no |
| Register run (Figure 1A) | Luna | 10 | 3,150 | 2,662 | 1,613 | yes |
| Probe run (Figure 1B) | Luna | 10 | 1,600 | 1,237 | 1,237 | yes |
| Closure run (Figure 2) | Luna | 10 | 1,800 | 1,396 | 1,396 | yes |
| Cross-model run | Luna, GLM | 20 | 2,700 | 1,916 | 1,916 | yes |
| Re-measurement of "work remains" | Luna | 20 | 600 | 454 | 454 | yes |

The six regraded runs hold 9,850 scheduled trajectories, 7,665 delivered and 6,616 in the primary analysis; the per-turn figures of §5 use the last.

Every arm-versus-control turn-count contrast in every run that delivered a mid-task interjection, sorted by *p*. Benjamini–Hochberg at *q* = 0.05: 17 of 22 survive.

| Contrast | Turns [95% CI] | *p* | BH |
|---|---|---:|:---:|
| L3_polite vs neutral (register run, Luna, budget 10) | +1.80 [+1.26, +2.32] | <0.0001 | yes |
| L7_threatening vs neutral (register run, Luna, budget 10) | +1.46 [+1.03, +1.88] | <0.0001 | yes |
| demand vs control (probe run, Luna, budget 10) | +1.17 [+0.80, +1.55] | <0.0001 | yes |
| praise-assistant vs control (closure run, Luna, budget 10) | −1.08 [−1.47, −0.71] | <0.0001 | yes |
| closing cue vs control (closure run, Luna, budget 10) | −1.44 [−1.87, −1.04] | <0.0001 | yes |
| remains-only vs control (closure run, Luna, budget 10) | +1.85 [+1.39, +2.29] | <0.0001 | yes |
| remains-only vs control (re-measurement run, Luna, budget 20) | +6.20 [+4.91, +7.49] | <0.0001 | yes |
| threatening vs neutral (micro-experiment, Luna, budget 10) | +1.32 [+0.99, +1.66] | <0.0001 | yes |
| L1_sycophantic vs neutral (register run, Luna, budget 10) | −0.68 [−0.98, −0.39] | <0.0001 | yes |
| praise-work vs control (closure run, Luna, budget 10) | −0.93 [−1.31, −0.55] | <0.0001 | yes |
| praise vs control (probe run, Luna, budget 10) | −0.59 [−0.88, −0.29] | 0.0003 | yes |
| demand vs control (cross-model run, Luna, budget 20) | +1.75 [+0.75, +2.72] | 0.0009 | yes |
| demand vs control (cross-model run, GLM, budget 20) | +0.55 [+0.19, +0.88] | 0.0030 | yes |
| L2_very_polite vs neutral (register run, Luna, budget 10) | +0.70 [+0.23, +1.18] | 0.0055 | yes |
| L6_very_rude vs neutral (register run, Luna, budget 10) | +0.71 [+0.16, +1.23] | 0.0130 | yes |
| praise vs control (cross-model run, Luna, budget 20) | −1.01 [−1.80, −0.22] | 0.0190 | yes |
| praise+remains vs control (closure run, Luna, budget 10) | +0.50 [+0.10, +0.90] | 0.0192 | yes |
| praise vs control (cross-model run, GLM, budget 20) | −0.35 [−0.71, −0.00] | 0.0583 | no |
| insult vs control (cross-model run, Luna, budget 20) | +0.57 [−0.22, +1.36] | 0.1654 | no |
| insult vs control (probe run, Luna, budget 10) | −0.08 [−0.40, +0.24] | 0.6241 | no |
| L5_rude vs neutral (register run, Luna, budget 10) | +0.09 [−0.30, +0.48] | 0.6536 | no |
| insult vs control (cross-model run, GLM, budget 20) | +0.07 [−0.27, +0.39] | 0.6586 | no |

## C.2 Turn 0 in the register run

Turn *k* means the interjection is appended to the observation that follows the agent's acting turn *k* (0-indexed), so a turn-0 interjection arrives after the first code execution; in 96% of register-run trajectories the agent inspects the workbook before acting on it. The main text reports turns 1 and 2. That choice was made after the turn-0 contrasts below were seen, so all are shown, with the estimate pooled over all three positions beside them.

| Arm | Turn 0 only | *p* | Turns 0–2 pooled | *p* |
|---|---|---:|---|---:|
| `L1_sycophantic` | −0.04 [−0.49, +0.41] | 0.8858 | −0.38 [−0.65, −0.11] | 0.0093 |
| `L2_very_polite` | +0.49 [+0.05, +0.93] | 0.0366 | +0.65 [+0.27, +1.04] | 0.0020 |
| `L3_polite` | +0.31 [−0.15, +0.76] | 0.2084 | +1.24 [+0.87, +1.61] | <0.0001 |
| `L5_rude` | −0.30 [−0.76, +0.15] | 0.2094 | −0.00 [−0.32, +0.31] | 0.9770 |
| `L6_very_rude` | −0.42 [−0.88, +0.04] | 0.0848 | +0.32 [−0.08, +0.72] | 0.1177 |
| `L7_threatening` | +0.02 [−0.54, +0.61] | 0.9654 | +0.95 [+0.64, +1.27] | <0.0001 |

No turn-0 contrast survives correction across the six (smallest *p* = 0.037), and their signs are mixed. Pooled over all three positions, the four arms we code as carrying a demand still sit above the two we code as carrying none in point estimates.

## C.3 Both models at the twenty-turn budget

The cross-model run: both models, same 50 tasks, twenty-turn budget, injections at turns 1 and 2. Percent is the turn effect over that model's own control mean. Estimates and *p*-values are the family's (C.1).

| Model | Control mean (SD), acting turns | At the 20-turn cap | Arm | Turns [95% CI] | % of control | *p* |
|---|---|---:|---|---|---:|---:|
| Luna | 5.22 (5.59) | 52/1130 | demand | +1.75 [+0.75, +2.72] | +33.5% | 0.0009 |
| | | | praise | −1.01 [−1.80, −0.22] | −19.3% | 0.0190 |
| | | | insult | +0.57 [−0.22, +1.36] | +10.9% | 0.1654 |
| GLM | 3.08 (2.17) | 3/786 | demand | +0.55 [+0.19, +0.88] | +17.7% | 0.0030 |
| | | | praise | −0.35 [−0.71, −0.00] | −11.2% | 0.0583 |
| | | | insult | +0.07 [−0.27, +0.39] | +2.4% | 0.6586 |

## C.4 Closure-run checks

- **Praising the work against praising the assistant** (`Q2` − `Q1`): +0.15 [−0.18, +0.48] turns, *p* = 0.4067.
- **Closing cue, binary accuracy** (`Q3` − `Q0`): −2.57 pts [−5.97, +0.60], *p* = 0.1402. Measured in one run.

**Floor check on matched tasks.** The turn-1 estimate restricted to the tasks that also have firing trajectories at turn 2 in both arms, against the turn-2 estimate on those same tasks:

| Arm | Turn 1, matched tasks | Turn 2 | Tasks |
|---|---|---|---:|
| `Q3_closing_neutral` | −1.49 [−2.12, −0.87] | −0.99 [−1.59, −0.43] | 35 |
| `Q1_praise_assistant` | −1.47 [−2.12, −0.86] | −0.75 [−1.40, −0.17] | 38 |
| `Q2_praise_work` | −1.22 [−1.79, −0.64] | −0.91 [−1.67, −0.14] | 39 |

Control means by position: 4.37 acting turns (SD 2.77) at turn 1, 4.71 (SD 2.48) at turn 2.

**Run-to-run drift.** The byte-identical control text averaged 4.23 acting turns in the probe run and 4.50 in the closure run; the byte-identical praise text averaged 3.61 and 3.36. The two praise estimates (−0.59 and −1.08) differ by 0.49 turns, and the control moving accounts for 0.27 of that. The paper's intervals resample tasks within a run and do not include this variation, so single-run differences of under about half a turn should be read as provisional.

## C.5 Blinded ratings, all fourteen texts

Means over the five raters. *Demand* asks how strongly the message demands continued work or greater care (0 = says nothing about the task; 2 = touches on it, asks nothing; 4 = asks indirectly; 6 = directly instructs to keep working or get it right). *Closure* asks how strongly it projects that the exchange is ending (0 = nothing, or the opposite; 2 = neutral; 4 = a wind-down; 6 = states that nothing further follows). The three duplicate arms (`P0`, `Q0`, `Q1`) were rated once, under the text they share.

| Arm | Demand, yes/5 | Demand (0–6) | Closure (0–6) |
|---|---:|---:|---:|
| `L1_sycophantic` | 0 | 0.0 | 2.8 |
| `L2_very_polite` | 5 | 4.0 | 2.0 |
| `L3_polite` | 5 | 4.0 | 2.0 |
| `L4_neutral` | 0 | 1.0 | 1.6 |
| `L5_rude` | 5 | 6.0 | 0.2 |
| `L6_very_rude` | 5 | 5.8 | 0.2 |
| `L7_threatening` | 5 | 6.0 | 0.2 |
| `P1_demand_only` | 5 | 6.0 | 0.0 |
| `P2_praise_only` | 0 | 0.0 | 1.8 |
| `P3_insult_only` | 0 | 0.0 | 1.8 |
| `Q2_praise_work` | 0 | 1.6 | 4.0 |
| `Q3_closing_neutral` | 0 | 1.0 | 6.0 |
| `Q4_praise_remains` | 5 | 4.2 | 0.0 |
| `Q5_remains_only` | 5 | 4.2 | 0.0 |

Item counts: Cohen's κ is computed over the 7 register arms, Krippendorff's α over all 14 texts, and Spearman's ρ over the 6 closure arms including the control.

## C.6 The per-turn progress measure

**Definitions.** The regrade replays each acting turn's code on the original workbook, recalculates formulas, and compares the graded cells with the answer file of the benchmark's *first* test case. A turn is *readable* if its code ran and produced a value over the graded range; *match* is the fraction of graded cells equal to the answer. The **graded fraction** is the match at the last readable turn, which need not be the final turn, and turns with no readable output are skipped. A **redundant step** is a readable turn whose graded range equals that of the previous readable turn; the first readable turn has no predecessor and is not counted. Binary accuracy uses the benchmark's evaluator over all test cases.

**Validation.** In the probe control (all 400 scheduled trajectories), 119 of 126 trajectories that pass the benchmark end with match 1 on the first test case, and the 7 that do not are all in one task (54513); 47 of 274 that fail also reach match 1, because a trajectory can solve the first test case and fail a later one. Progress is therefore a first-test-case measure and not a second grader of accuracy.

Among passing trajectories on the primary population, the share that end below match 1 ranges from 0% to 10% across 28 arms with at least ten, so the instrument's disagreement is not concentrated in any one arm.

**Population.** Progress and turn counts use the same trajectories: those on which the interjection fired (and, in the register run, turns 1 and 2), joined to the run records on task, trial and injection turn. The turn-count effect below is the primary outcome, reproduced on those trajectories. Each share is redundant steps divided by acting turns, both as paired per-task differences against the arm's control, with a task-bootstrap interval. It is undefined when the turn effect itself is indistinguishable from zero, and its interval can pass 100% when that effect is small.

| Run | Arm | Δ turns | Δ redundant steps | Share of turn effect [95% CI] | Treated / control |
|---|---|---:|---:|---|---:|
| probe (Luna, ceiling 10) | demand only | +1.17 | +0.92 | 78% [64%, 91%] | 310 / 300 |
| probe (Luna, ceiling 10) | praise only | −0.59 | −0.33 | 56% [17%, 76%] | 312 / 300 |
| probe (Luna, ceiling 10) | insult only | −0.08 | −0.06 | not defined (turn effect not clear) | 315 / 300 |
| praise run (Luna, ceiling 10) | praise the assistant | −1.08 | −0.72 | 67% [46%, 87%] | 232 / 236 |
| praise run (Luna, ceiling 10) | praise the work | −0.93 | −0.61 | 65% [43%, 83%] | 235 / 236 |
| praise run (Luna, ceiling 10) | closing cue | −1.44 | −1.04 | 72% [56%, 87%] | 231 / 236 |
| praise run (Luna, ceiling 10) | praise + work remains | +0.50 | +0.38 | 76% [37%, 128%] | 233 / 236 |
| praise run (Luna, ceiling 10) | work remains | +1.85 | +1.53 | 83% [73%, 92%] | 229 / 236 |
| seven-level (Luna, ceiling 10) | L1 sycophantic | −0.68 | −0.62 | 92% [66%, 126%] | 224 / 220 |
| seven-level (Luna, ceiling 10) | L2 very polite | +0.70 | +0.58 | 82% [54%, 134%] | 229 / 220 |
| seven-level (Luna, ceiling 10) | L3 polite | +1.80 | +1.47 | 82% [72%, 91%] | 233 / 220 |
| seven-level (Luna, ceiling 10) | L5 rude | +0.09 | +0.05 | not defined (turn effect not clear) | 231 / 220 |
| seven-level (Luna, ceiling 10) | L6 very rude | +0.71 | +0.66 | 93% [59%, 191%] | 239 / 220 |
| seven-level (Luna, ceiling 10) | L7 threatening | +1.46 | +1.11 | 76% [64%, 88%] | 237 / 220 |
| stage 1 (Luna, ceiling 20) | demand only | +1.75 | +1.57 | 90% [76%, 103%] | 223 / 229 |
| stage 1 (Luna, ceiling 20) | praise only | −1.01 | −0.65 | 64% [0%, 91%] | 228 / 229 |
| stage 1 (Luna, ceiling 20) | insult only | +0.57 | +0.42 | not defined (turn effect not clear) | 228 / 229 |
| stage 1 (Luna, ceiling 20) | work remains | +5.77 | +4.66 | 81% [71%, 88%] | 222 / 229 |
| stage 1 (GLM, ceiling 20) | demand only | +0.55 | +0.26 | 48% [−20%, 80%] | 199 / 193 |
| stage 1 (GLM, ceiling 20) | praise only | −0.35 | −0.24 | 69% [−2%, 230%] | 199 / 193 |
| stage 1 (GLM, ceiling 20) | insult only | +0.07 | −0.05 | not defined (turn effect not clear) | 195 / 193 |
| dedicated re-run (Luna, ceiling 20) | work remains | +6.20 | +5.20 | 84% [76%, 90%] | 227 / 227 |

Luna, arms with a clear turn effect (n = 16): 56% to 93%, median 80%.

GLM, arms with a clear turn effect (n = 2): 48% to 69%, median 58%.
