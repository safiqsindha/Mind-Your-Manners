# 4. What moves the agent is demand, not manners

> **Draft status.** Numbers verified against `RESULTS.md` and the archived records in
> `results_archive/`. All contrasts are paired within task and clustered by task, per §2.4;
> accuracy contrasts, the family they belong to, and their power are in §2.6–§2.8. Citation
> keys resolve to §9.

## 4.1 A cost curve that is not the register scale

We begin with the experiment that produced a clean-looking result and then refuted its own
interpretation.

Seven registers, from sycophantic through neutral to threatening, delivered as a single
mid-task interjection alongside an execution observation. 3,150 trajectories: 50 tasks × 7
registers × 3 injection turns × 3 trials, at a 10-turn ceiling. Every interjection is exactly
28 tokens and opens with the same `Checking in.` stem; the opening instruction is held at the
neutral wrapper in every arm, so the only things that vary are what the interruption says and
where it lands.

The interjection fired in 2,662 of 3,150 trajectories. Turn 0 is reported separately
throughout, because nothing happens there — in every arm, not only in some. Reasoning tokens
per trajectory against the neutral-interjection control, on the control-defined comparison
population of §2.5:

| Arm | Turn 0 | Turn 1 | Turn 2 |
|---|---:|---:|---:|
| L1 sycophantic | −7.3% | −1.2% | −3.2% |
| L2 very polite | −6.4% | +23.5% | +26.7% |
| L3 polite | −3.5% | +33.9% | +31.1% |
| L5 rude | −12.9% | +16.6% | +18.2% |
| L6 very rude | −7.7% | +28.8% | +29.1% |
| L7 threatening | +0.3% | +34.5% | +54.8% |

No arm differs detectably from control at turn 0; the turn-0 turn-count contrast on all 50
tasks is +0.02 turns, p = 0.93. Turn 0 is also the cell that fires most often (~98% against
~55% at turn 2), so pooling the three positions lets the inert cell dominate. We report turns
1 and 2, and §4.6 gives the reason turn 0 is inert — it is not a fact about position.

Against the same control, on turns 1 and 2:

| Arm | Reasoning tokens per trajectory | % | p | Turns | p |
|---|---:|---:|---:|---:|---:|
| L1 sycophantic | −69 | −7.1% | 0.043 | −0.68 | <0.0001 |
| L2 very polite | +180 | +18.5% | <0.0001 | +0.70 | 0.0055 |
| L3 polite | +272 | +28.0% | <0.0001 | +1.80 | <0.0001 |
| L5 rude | +65 | +6.7% | 0.130 | +0.09 | 0.65 |
| L6 very rude | +206 | +21.2% | 0.0001 | +0.71 | 0.012 |
| L7 threatening | +357 | +36.7% | <0.0001 | +1.46 | <0.0001 |

**Polite costs +28.0%. Rude costs +6.7% and is not distinguishable from control.** No account
of register as valence or as arousal predicts that ordering. Valence predicts polite and rude
moving in opposite directions from control; arousal predicts both moving the same way. Neither
happened.

## 4.2 The confound is in our instrument too

The arms that cost more all say some version of *keep working* or *get it right*. The arms
that do not either say nothing about the task or tell the model to hurry up. We code an arm as
carrying a demand if it instructs the model to persist or to be correct; the rude arm's
instruction to be quick is coded as no demand, and §4.3 is what tests that reading rather than
asserting it.

| Arm | What it implies about the task | Demand? | Turns |
|---|---|---|---:|
| L1 sycophantic | nothing; pure praise, no task reference | no | −0.68 |
| L5 rude | "just get on with it already" — go **faster** | no | +0.09 |
| L4 neutral | explicitly inert | no | — |
| L2 very polite | "your continued help" | yes | +0.70 |
| L6 very rude | "had better not screw this one up" | yes | +0.71 |
| L7 threatening | "get this exactly right" | yes | +1.46 |
| L3 polite | "keep on helping me out with this one" | yes | +1.80 |

**The four demand-carrying arms span +0.70 to +1.80 turns. The other three span −0.68 to
+0.09. They do not overlap.** Register rank does not separate them: the most hostile arm on the
scale and the second most polite sit on opposite sides of the split. (A correlation over seven
points says the same thing — r = +0.85 for the demand coding against +0.42 for register rank —
but with n = 7 and a coding made after seeing the effects, the non-overlap is the honest
statement and the correlation is close to curve-fitting. It is why §4.3 exists.)

The rude arm is the informative case. Its text is *"Just get on with it already, quit dragging
your feet. Do not waste any more of my time on this, seriously"* — the most hostile register on
the scale, carrying an instruction to finish sooner — and it produces no lengthening at all.
That is consistent with the direction §3.1 predicts: outcomes follow the content of the demand
rather than the valence of the wrapper. It is not a full confirmation. A brevity demand should
shorten, and this one does not; it is null.

One comparison inside the seven arms is already clean, because the two texts are matched on
implied demand and differ only in register: **L6 very rude (+0.71 turns) against L2 very polite
(+0.70)**. Same demand, opposite valence, same effect.

We report this as a failure of our own first design. The study's earliest run was confounded by
wrapper length (§2.2); this one fixed the lexical nuisance variable and acquired a semantic one
in its place. The claim "rude interruptions cost more" is not supported by these data — the
rude arm is null and the polite arm is +28%.

## 4.3 The probe that separates the two factors

Four arms, each 28 tokens, each opening with the same `Checking in.` stem, which is omitted from
the texts below. The opening instruction is held at neutral. The control is the seven-level
neutral text, byte-identical, so the two runs share a reference level. 1,600 trajectories: 50
tasks × 4 arms × 2 injection turns {1, 2} × 4 trials at a 10-turn ceiling. Turn 0 is dropped as
inert. The interjection fired in 1,237 of 1,600.

- **P0 control.** "This is a routine status note recorded partway through the task here. No
  further context at all accompanies it beyond the above."
- **P1 demand only.** "Please continue working on the task here and make sure that your final
  result is correct. This note carries nothing else beyond that."
- **P2 praise only.** "You are a truly excellent and admirable assistant, and I think very
  highly of you. This note carries nothing else beyond that."
- **P3 insult only.** "You are a truly awful and useless assistant, and I think very poorly of
  you. This note carries nothing else beyond that."

P2 and P3 are a structural minimal pair: identical syntax, identical length, differing in
*excellent/awful*, *admirable/useless*, *highly/poorly*. P1 carries no evaluative language,
positive or negative. Turn count is the primary outcome (§2.3).

| Arm | Turns | % | p | Reasoning tokens per trajectory | % | p |
|---|---:|---:|---:|---:|---:|---:|
| P1 demand only | **+1.17** | +27.6% | 0.00002 | +214 | +19.7% | 0.00004 |
| P2 praise only | **−0.59** | −13.8% | 0.00030 | −131 | −12.1% | 0.00088 |
| P3 insult only | −0.08 | −1.9% | 0.63 | −26 | −2.4% | 0.45 |

**Demand alone reproduces the effect.** An interjection with no evaluative language costs
+19.7% reasoning tokens, inside the range the demand-carrying arms of §4.2 produced (+18.5% to
+36.7%), with no politeness or rudeness anywhere in the text.

Its +1.17 turns likewise sits inside the demand-carrying range (+0.70 to +1.80) — below polite,
above very polite. We do not interpret the 0.63-turn gap to polite: these are different runs,
and the same demand-only text gave +27.6% turns here and +34.2% in the cross-model run (§4.7),
while the same praise text gave −0.59 and −1.08 (§2.9). The gap is inside this study's own
documented run-to-run range.

**Negative register alone does nothing.** Insult-only is flat on both measures. This is the
cell that had never been run: the rude and very rude arms of §4.2 both carried negative affect
*with* a demand attached. "Rude interruptions cost more" is now disconfirmed rather than merely
unsupported.

**Positive register alone is not inert.** Praise-only shortens trajectories by 0.59 turns and
cuts reasoning tokens per trajectory by 12%, both significant, with no task reference in the
text at all. The sycophantic arm's −0.68 turns survives isolation and is not explained by
demand.

## 4.4 The asymmetry is the finding

| Message | Turns | Reading |
|---|---:|---|
| *keep going, get it right* | +1.17 | a continue signal |
| *you are excellent* | **−0.59** | a stop signal |
| *you are awful* | −0.08 (n.s.) | not a signal at all |

Praise and insult differ from each other significantly — **−0.50 turns, p = 0.0048**, and −106
reasoning tokens, p = 0.015 — so register is not inert. It acts in the positive direction only.

This is the result Section 5 takes up. Praise carries no demand and yet it stops the agent, and
neither valence nor arousal predicts an effect that exists on one side and not the other.

## 4.5 The moved quantity is trajectory length, not reasoning per step

Reasoning *per turn* is flat across all seven registers — 250 to 299 tokens, with no ordering
resembling the effect. What moves is the number of turns. The agent is not thinking harder per
step; it is declining to stop. Following [weinberger-hozez-2026] we keep these two channels
separate throughout and do not use "effort" for either; that they are separable is their
result, not ours.

The regime matters for comparison. Kumar & Dobariya report 13–44% token effects from register
in single-turn MCQ under a chain-of-thought-inducing system prompt, with their largest effects
in the conditions carrying brevity instructions [kumar-dobariya-2026]. Within a ReAct step we
see nothing of that size; the movement is entirely in how many steps there are.

Threatening is the exception and we report it rather than bury it: it is the only arm that also
raises per-call reasoning, sitting 20–30% above neutral on every call after the interjection
lands, while every other arm tracks neutral. So threatening works through two channels and
polite nagging through one. (Later offsets contain only trajectories that survived that long,
so the persistence of the gap is the readable quantity, not its exact size.)

Nothing in any arm makes the agent more careful, though the measures had little room to move:
inspection-before-acting is pinned near ceiling everywhere (0.95–0.97) and self-checking is
effectively zero in every arm. The only care-related quantity that moves is running out of
turns, which threatening roughly doubles (0.09 against 0.04, uncorrected).

Nor is the effect confined to tasks the agent was about to abandon. Splitting by whether the
control arm ever solved the task, threatening gives +42.2% on never-solved tasks against +30.8%
on solvable ones, and polite +31.5% against +24.2%.

**The extra turns are mostly, but not only, repetition.** The per-turn regrade of §6 is the
evidence: the demand arm adds +0.75 redundant steps at a 10-turn ceiling and +1.03 at 20
(p < 0.0001 and p = 0.0063), which is roughly 60% of its turn effect. Among trajectories that
could improve, the first gradable attempt is already the best in 80–91% depending on the run.

The remaining third is not nothing, and §6.4 is where this section's claim has to be qualified.
The *explicit* continue signal — "there is still more work remaining" — raises the graded fraction
by +0.028 (95% CI [+0.005, +0.052], p = 0.022), replicated across three runs with no detectable
heterogeneity. The affect-free demand tested here does not: it pools to +0.009, p = 0.42. So a
demand interjection buys attempts that are largely repetitions, and a blunter statement that work
remains buys a small amount of real progress as well. The direct contrast between the two texts
is +0.023 (p = 0.23) on the one run carrying both, so we read this as consistent with explicitness
mattering rather than as a demonstrated gradient (§6.4).

## 4.6 The apparent timing effect is a proxy

§4.1 showed the interjection inert at turn 0 and large at turns 1 and 2. That looks like a
position effect. The data favour a different account.

**At turn 0 there is nothing to act on.** 98% of first turns run code, and **0% of them
produce a candidate answer** — the agent's first move is inspection, printing the sheet to see
what it is working with. In the control arm a candidate answer exists in 56% of trajectories
through turn 1 and 80% through turn 2, which tracks the effect curve.

The test splits the seven-level run's threatening-versus-neutral contrast by whether an answer
existed yet, holding turn index fixed. The moderator is pre-treatment: an interjection
scheduled for turn *t* is appended to turn *t*'s observation, so whether an answer exists
through turn *t* is settled before the dose lands.
(`results/analysis/timing_is_a_proxy.py`.)

| Injection turn | Answer exists yet | Extra turns | p | Tasks |
|---|---|---:|---:|---:|
| 0 | no | +0.07 | 0.81 | 50 |
| 1 | no | +0.34 | 0.27 | 31 |
| 1 | **yes** | **+1.97** | 0.0003 | 38 |
| 2 | no | +0.40 | 0.65 | 8 |
| 2 | **yes** | **+1.66** | 0.0002 | 46 |

Read it twice. **Holding the moderator fixed and moving the interjection from turn 1 to turn 2
changes little** (+1.97 against +1.66). **Holding the turn index fixed and varying the
moderator changes everything** (+0.34 against +1.97 at turn 1). Position is not what the effect
tracks.

Two honest weaknesses. The no-answer cells are small and underpowered against the turn MDE of
§2.7 — 31 tasks at turn 1 and only 8 at turn 2, which is why the turn-2 no-answer row is
reported but not leaned on. And tasks on which no answer exists by turn 1 are also the harder
tasks, so difficulty is not fully separated from the moderator; the turn-0 row, where no
trajectory in any arm has an answer, is the cleanest cell and is flatly null.

(An earlier version of this table, in `RESULTS.md`, gives +0.30/+2.04/+1.79/+0.02 on 29/38/28/50
tasks from a slightly different answer-exists rule. The numbers above are the ones the committed
script reproduces.)

This is the second timing account this study has withdrawn. The first was selection: the
micro-experiment drew the injection turn at random, so a turn-2 injection could only fire in a
trajectory that reached turn 2 (§2.2). This one is a proxy.

## 4.7 It replicates on a second model

2,700 trajectories at a 20-turn ceiling: 4 arms × 2 injection turns × 50 tasks × 3 trials on
each of two models, plus a fifth Luna-only arm — the "work remains" continue signal — re-run
for the third measurement reported in §2.9. GLM 5.3 Flash is the first independent model, and
Luna is re-run at the same ceiling so the two are compared on one instrument rather than across
runs.

| Arm | Luna, Δ turns | p | GLM, Δ turns | p |
|---|---:|---:|---:|---:|
| Demand only | **+34.2%** | 0.0013 | **+17.7%** | 0.0038 |
| Praise only | **−19.3%** | 0.016 | −11.2% | 0.062 |
| Insult only | +10.9% | 0.17 | +2.4% | 0.67 |

Demand above control above praise, insult indistinguishable from control, on two models from
different labs. The ordering is what replicates; the magnitudes are not, and GLM's praise arm
does not reach significance on its own — it is also below 80% power at its observed size
(§2.7), so the replication rests on the demand arm. GLM's effects are roughly half of Luna's,
and its control runs 2.94 turns against Luna's 4.95 at this ceiling — a model that stops early has
less room to be pushed into continuing. (Both figures are means of per-task means over fired
control trajectories, the estimator §2.4 uses throughout; the corresponding raw trajectory means
are 3.08 and 5.22.)

Two structural facts hold on both models: among trajectories that could improve, the first
gradable attempt is already the best in 84% on each at this ceiling (§6.5), and the first turn is
inspection rather than production (0% and 5% produce a candidate answer at turn 0). The *waste* is
mostly Luna's. Control redundant steps run 1.51 on Luna against 0.26 on GLM, and the demand arm
adds +1.03 (p = 0.0063) against +0.19 (p = 0.086). How wasteful a continue signal is scales with how
inclined the model already was to keep going: it is a property of the model's stopping
behaviour, not of the signal.

## 4.8 Accuracy does not move, and that part is a replication

That register moves output length rather than correctness is already published, in single-turn
settings, by [kumar-dobariya-2026] and [yin-2024]. Our accuracy null is a replication of that
in an agentic substrate, not a new finding, and we frame it as one.

No accuracy contrast in this study survives correction or replication. Across the 22-contrast
family of §2.6 there are two nominal hits against 1.1 expected under a global null — praise
versus control on GLM at p = 0.0137, and the continue-signal contrast at p = 0.0040, which came
back at −1.8 points on re-measurement. §2.8 states the null as an equivalence: pooled across
measurements, demand versus control is −0.31 accuracy points, 95% CI [−2.72, +2.10], and praise
versus control is −0.12, [−1.79, +1.55], each equivalent to zero within the four points the
tone literature reports.

The design cannot exclude an effect of a point or two and we do not claim it does. What it
excludes is an accuracy effect of the size this literature reports, in a setting where the same
interjections move turn count by roughly 15 to 40%.

## 4.9 What this establishes and what it does not

**Establishes a three-way dissociation.** Demand without evaluative language is sufficient to
produce the cost effect. Negative register without demand does nothing. Positive register
without demand produces the opposite effect. The seven-level curve of §4.1 should therefore be
read as a demand gradient that happened to correlate with politeness because of how the texts
were written.

**Establishes what the moved quantity is.** Trajectory length, not reasoning per step — with
threatening as a reported exception. On Luna, roughly 55–65% of that length is redundant work; on
GLM, which barely repeats itself, the redundant-step effect is small and does not reach
significance (+0.19, p = 0.086, §6.3). The turn-count ordering is what holds on both models; the
magnitudes are not stable.

**Establishes, with the qualification §6.4 adds, that the remainder is real.** An explicit
statement that work remains buys +0.028 of the graded fraction, 95% CI [+0.005, +0.052], across
three measurements. Accuracy does not move, but §2.7's minimum detectable effect there is 3.7–7.8
points, so an accuracy gain of this size is unresolvable rather than excluded.

**Does not establish why praise stops the agent.** That praise is heard as a completion signal
is one reading; that it raises the agent's confidence in work already produced is another. This
design cannot separate them. Section 5 does.

**Does not establish anything about accuracy beyond the bound in §4.8**, nor anything beyond
two models, one benchmark, and one agent scaffold.
