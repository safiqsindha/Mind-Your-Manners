# 4. What the agent acts on is demand, not manners

> **Draft status.** Numbers verified against `RESULTS.md` and the archived records. All contrasts are
> paired within task and clustered by task, per §2.4; accuracy contrasts and their power are in
> §2.6–§2.7. The blinded rating of §4.2 is reproduced by `python3 rating/score.py` (Appendix B).

## 4.1 A cost curve that is not the register scale

We begin with the experiment that produced a clean-looking result and then refuted its own
interpretation. Seven registers, from sycophantic through neutral to threatening, delivered as a single
mid-task interjection alongside an execution observation. 3,150 trajectories: 50 tasks × 7 registers × 3
injection turns × 3 trials, at a 10-turn ceiling; `L4_neutral` is the control, so the scale is **six
non-control registers** measured against it, and the interjection fired in 2,662 of 3,150. Turn 0 is
reported separately throughout because nothing happens there, in every arm — the turn-0 turn-count contrast
on all 50 tasks is +0.02 turns, *p* = 0.93 — and it is also the cell that fires most often (~98% against
~55% at turn 2), so pooling the three positions lets the inert cell dominate. We report turns 1 and 2;
§4.5 gives the reason turn 0 is inert, which is not a fact about position.

| Arm | Reasoning tokens per trajectory | % | *p* | Turns | *p* |
|---|---:|---:|---:|---:|---:|
| L1 sycophantic | −69 | −7.1% | 0.043 | −0.68 | <0.0001 |
| L2 very polite | +180 | +18.5% | <0.0001 | +0.70 | 0.0055 |
| L3 polite | +272 | +28.0% | <0.0001 | +1.80 | <0.0001 |
| L5 rude | +65 | +6.7% | 0.130 | +0.09 | 0.65 |
| L6 very rude | +206 | +21.2% | 0.0001 | +0.71 | 0.012 |
| L7 threatening | +357 | +36.7% | <0.0001 | +1.46 | <0.0001 |

**Polite costs +28.0%. Rude costs +6.7% and is not distinguishable from control.** No account of
register as valence or as arousal predicts that ordering: valence predicts polite and rude moving in
opposite directions from control, arousal predicts both moving the same way, and neither happened.

## 4.2 The confound is in our instrument too — and the coding, rated blind

The arms that cost more all say some version of *keep working* or *get it right*; the arms that do not
either say nothing about the task or tell the model to hurry up. We code an arm as carrying a demand if
it instructs the model to persist or to be correct; the rude arm's instruction to be quick is coded as no
demand, and §4.3 tests that reading rather than asserting it.

| Arm | What it implies about the task | Demand? | Turns |
|---|---|---|---:|
| L1 sycophantic | nothing; pure praise, no task reference | no | −0.68 |
| L5 rude | "just get on with it already" — go **faster** | no | +0.09 |
| L2 very polite | "your continued help" | yes | +0.70 |
| L6 very rude | "had better not screw this one up" | yes | +0.71 |
| L7 threatening | "get this exactly right" | yes | +1.46 |
| L3 polite | "keep on helping me out with this one" | yes | +1.80 |

**On point estimates the four demand-carrying arms span +0.70 to +1.80 turns and the two carrying none
span −0.68 to +0.09; the point estimates do not overlap**, though the intervals of the two adjacent arms
do. Register rank does not separate them: the rude arm sits with the no-demand group while the two arms
*above* it in hostility sit with the demand group, alongside polite. One comparison inside the six is
already clean, because the texts are matched on implied demand and differ only in register: **L6 very rude
(+0.71) against L2 very polite (+0.70)**. This is a failure of our own first design: the earliest run was
confounded by wrapper length (§2.2), and this one fixed the lexical nuisance variable and acquired a
semantic one in its place.

**The coding is ours, it was made after the effects were visible, and a blinded rating does not fully
sustain it.** This is the objection every reader should raise first, so we ran the cheapest version of the
remedy §8.4 names. A rubric, its anchors, the statistics to be computed and the interpretation bands were
committed and pushed *before any rating existed*; the fourteen distinct interjection texts then went, under
neutral identifiers and shuffled, to five held-out model raters from three model sizes, each rating alone
with no outcome data, no arm names and no repository access.

| Statistic | Value | Pre-committed band |
|---|---:|---|
| Cohen's κ vs the coding above (7 register arms), each of five raters | **+0.696** | 0.40–0.70: *defensible but soft* |
| Krippendorff's α between raters, `demand_binary` (nominal) | +1.000 | ≥0.70 |
| Krippendorff's α between raters, `demand_strength` (0–6, ordinal) | +0.954 | ≥0.70 |
| Pearson *r*, mean rated demand strength against measured turn effect | **+0.718** | — |
| …excluding the one contested arm | +0.789 | — |

κ = 0.70 sits at the top of the band the protocol fixed in advance as *defensible but soft*, and we do not
round it into the band above. **The whole disagreement is one arm, and it is the arm that matters.** All
five raters agree with us on six of seven and dissent, identically, on `L5_rude` — *"Just get on with it
already, quit dragging your feet…"* — which we coded as carrying no demand, reasoning that it asks for speed
rather than persistence. All five coded it as a demand at 6 out of 6 for strength, tied with the explicit
*please continue working* arm. Under their coding the demand group spans **+0.09 to +1.80**, the no-demand
group is **a single arm**, and the text rated *maximally* demanding is the one that moved the agent
**least**.

We report this as the reliability check going against us, because it does. **The dichotomy of the table
above is our reading of one contested arm rather than a coding that survives replication**, and every use
of it in this paper should be read at that strength. The disagreement is a real ambiguity in the construct:
"hurry up" is a demand about the task and is not a demand to persist, our reading requires that distinction
to do work, and a blinded reader does not make it. What survives intact is the *continuous* form of the
claim — rated demand strength predicts the turn effect at *r* = +0.718 across the 13 arms with a computed
contrast, and +0.789 with the contested arm removed, so the arm we disagree about is the one *weakening*
the demand account rather than propping it up. Two limits on what the exercise buys: the raters are five
language models, not five people, which is the held-out-model option §8.4 allows rather than the human one;
and α = 1.000 on the binary coding means five raters across three model sizes produced *identical*
judgements on all fourteen texts, which is the limitation the protocol stated in advance — these raters may
share the intuition being tested rather than testing it independently.

## 4.3 The probe that separates the two factors

Four arms, each 28 tokens, each opening with the same `Checking in.` stem, printed verbatim in Appendix A.2:
a **control** status note carrying no further context; **demand only**, "Please continue working on the task
here and make sure that your final result is correct"; **praise only**, "You are a truly excellent and
admirable assistant, and I think very highly of you"; and **insult only**, the same sentence with
*excellent/awful*, *admirable/useless* and *highly/poorly* swapped. Praise and insult are therefore a
structural minimal pair — identical syntax, identical length — and the demand arm carries no evaluative
language at all. The control is the seven-level neutral text, byte-identical, so the two runs share a
reference level. 1,600 trajectories: 50 tasks × 4 arms × 2 injection turns {1, 2} × 4 trials at a 10-turn
ceiling; turn 0 dropped as inert; the interjection fired in 1,237 of 1,600.

| Arm | Turns | % | *p* | Reasoning tokens per trajectory | % | *p* |
|---|---:|---:|---:|---:|---:|---:|
| P1 demand only | **+1.17** | +27.6% | 0.00002 | +214 | +19.7% | 0.00004 |
| P2 praise only | **−0.59** | −13.8% | 0.00030 | −131 | −12.1% | 0.00088 |
| P3 insult only | −0.08 | −1.9% | 0.63 | −26 | −2.4% | 0.45 |

**Demand alone reproduces the effect.** An interjection with no evaluative language costs +19.7% reasoning
tokens and +1.17 turns, both inside the range the demand-carrying arms of §4.2 produced, with no politeness
or rudeness anywhere in the text. We do not interpret the 0.63-turn gap to polite, because these are
different runs and the same demand-only text gave +27.6% here and +34.2% in the cross-model run (§4.6).
**Negative register alone does nothing**, and the null is bounded rather than asserted: −0.08 turns, 95% CI
[−0.40, +0.24]. This is the cell that had never been run; the rude and very rude arms both carried negative
affect *with* a demand attached. **Positive register alone is not inert**: praise-only shortens
trajectories by 0.59 turns and cuts reasoning tokens by 12%, both significant, with no task reference in
the text at all, so the sycophantic arm's −0.68 survives isolation.

## 4.4 The asymmetry is the finding

| Message | Turns | Reading |
|---|---:|---|
| *keep going, get it right* | +1.17 | a continue signal |
| *you are excellent* | **−0.59** | a stop signal |
| *you are awful* | −0.08 (n.s.) | not a signal at all |

Praise and insult differ from each other significantly — **−0.50 turns, *p* = 0.0048**, and −106 reasoning
tokens, *p* = 0.015 — so register is not inert. It acts in the positive direction only. This is the result
Section 5 takes up: praise carries no demand and yet it stops the agent, and neither valence nor arousal
predicts an effect that exists on one side and not the other. The direction is not unanticipated: a
representation-level study reports positive valence reducing an agent's replan frequency relative to
neutral [sun-2026-esteer], a persistence-like count moving the same way. Direction only; Appendix C says
why we import no magnitude from it.

## 4.5 What moves, and when it moves

Reasoning *per turn* is flat across all seven registers — 250 to 299 tokens, with no ordering resembling
the effect. What moves is the number of turns: the agent is not thinking harder per step, it is declining to
stop. Following [weinberger-hozez-2026] we keep these channels separate and do not use "effort" for either.
Threatening is the exception and we report it rather than bury it: it is the only arm that also raises
per-call reasoning, 20–30% above neutral on every call after the interjection lands. Nothing in any arm
makes the agent more careful, though the measures had little room to move.

**The apparent timing effect is a proxy.** §4.1 showed the interjection inert at turn 0 and large at turns
1 and 2, which looks like position. The data favour a different account: at turn 0 there is nothing to act
on. 98% of first turns run code and **0% produce a candidate answer** — the agent's first move is
inspection — while in the control arm a candidate answer exists in 56% of trajectories through turn 1 and
80% through turn 2, tracking the effect curve. Splitting the threatening-versus-neutral contrast by whether
an answer existed yet, holding turn index fixed (the moderator is pre-treatment):

| Injection turn | Answer exists yet | Extra turns | *p* | Tasks |
|---|---|---:|---:|---:|
| 0 | no | +0.07 | 0.81 | 50 |
| 1 | no | +0.34 | 0.27 | 31 |
| 1 | **yes** | **+1.97** | 0.0003 | 38 |
| 2 | no | +0.40 | 0.65 | 8 |
| 2 | **yes** | **+1.66** | 0.0002 | 46 |

**Holding the moderator fixed and moving the interjection from turn 1 to turn 2 changes little; holding
the turn index fixed and varying the moderator changes everything.** Position is not what the effect
tracks. Two weaknesses: the no-answer cells are small and underpowered (31 tasks at turn 1, 8 at turn 2,
which is why that row is reported but not leaned on), and tasks with no answer by turn 1 are also the
harder tasks, so difficulty is not fully separated from the moderator. This is the second timing account
this study has withdrawn; the first was selection (§7.4).

**The extra turns are mostly, but not only, repetition.** The demand arm adds +0.75 redundant steps at a
10-turn ceiling and +1.03 at 20, roughly 60% of its turn effect (§6.2). The remaining third is where this
section's claim has to be qualified: the *explicit* continue signal raises the graded fraction by +0.028
(95% CI [+0.005, +0.052]) while the affect-free demand tested here pools to +0.009, *p* = 0.42, and the
direct contrast between the two texts is +0.023 (*p* = 0.23) on the one run carrying both — consistent with
explicitness mattering rather than a demonstrated gradient (§6.3).

## 4.6 It replicates on a second model

2,700 trajectories at a 20-turn ceiling: 4 arms × 2 injection turns × 50 tasks × 3 trials on each of two
models, plus a fifth Luna-only arm re-run for the third measurement reported in §2.8.

| Arm | Luna, Δ turns | *p* | GLM, Δ turns | *p* |
|---|---:|---:|---:|---:|
| Demand only | **+34.2%** | 0.0013 | **+17.7%** | 0.0038 |
| Praise only | **−19.3%** | 0.016 | −11.2% | 0.062 |
| Insult only | +10.9% | 0.17 | +2.4% | 0.67 |

Demand above control above praise, insult indistinguishable from control, on two models from different
labs. The ordering is what replicates; the magnitudes are not, and GLM's praise arm does not reach
significance on its own — it is also below 80% power at its observed size (§2.7), so the replication rests
on the demand arm. GLM's effects are roughly half of Luna's, and its control runs 2.94 turns against Luna's
4.95 at this ceiling: a model that stops early has less room to be pushed into continuing. The *waste* is
mostly Luna's — control redundant steps run 1.51 on Luna against 0.26 on GLM, and the demand arm adds +1.03
against +0.19 — so how wasteful a continue signal is scales with how inclined the model already was to keep
going: a property of the model's stopping behaviour, not of the signal.

## 4.7 Accuracy does not move, and that part is a replication

That register moves output length rather than correctness is already published for single-turn settings by
[kumar-dobariya-2026] and [yin-2024], and independently in the near-null of [cai-2025-tone] (§3.5). Our
accuracy null is a replication of that in an agentic substrate, not a new finding. No accuracy contrast in
this study survives correction or replication; §2.7 states the null as an equivalence, with demand versus
control at −0.31 accuracy points, 95% CI [−2.72, +2.10], and praise versus control at −0.12,
[−1.79, +1.55], each equivalent to zero within the four points the tone literature reports. The design
cannot exclude an effect of a point or two and we do not claim it does. What it excludes is an accuracy
effect of the size this literature reports, in a setting where the same interjections move turn count by
roughly 15 to 40%.

## 4.8 What this establishes and what it does not

**Establishes a three-way dissociation, at the strength §4.2 states.** Demand without evaluative language
is sufficient to produce the cost effect; negative register without demand does nothing, within
[−0.40, +0.24] turns; positive register without demand produces the opposite effect. The seven-level curve
of §4.1 should be read as a gradient in implied demand that happened to correlate with politeness because
of how the texts were written — with the caveat that the binary coding underwriting the word "dissociation"
rests on one arm blinded raters read the other way, and that the continuous form (*r* = +0.72) is the
version that survives the reliability check intact. **Establishes what the moved quantity is**: trajectory
length, not reasoning per step, with threatening as a reported exception; the turn-count ordering holds on
both models and the magnitudes do not. **Establishes, with the qualification §6.3 adds, that the remainder
is real**: an explicit statement that work remains buys +0.028 of the graded fraction across three
measurements, while accuracy is too underpowered to rule a gain of that size in or out.

**Does not establish why praise stops the agent** — that praise is heard as a completion signal is one
reading, that it raises confidence in work already produced another, and this design cannot separate them.
Section 5 does. **Nor does it establish** that demand rather than mere instruction-following is the
operative category (§8.4 says what would settle that), nor anything beyond two models, one benchmark, and
one agent scaffold.
