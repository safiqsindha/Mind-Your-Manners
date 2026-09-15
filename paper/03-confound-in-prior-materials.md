# 3. The confound is visible in the published stimulus sets

> **Draft status.** Every table below is reproduced from the cited paper's own published
> materials, checked against `Literature review/01-sources.md`. **One** item still needs a pass
> against a primary PDF before submission and is marked in §3.7: the full prefix set of
> [kumar-dobariya-2026] Table 2. The second item — the variant count per level behind
> [dobariya-kumar-2025] — has been checked against [dobariya-kumar-2026]'s Table 1, which prints
> the pool for the same 50-question dataset. It does not print one variant per level, and §3.3
> has been rewritten and **weakened** accordingly. The **demand** coding in the right-hand column
> of each table is ours, not theirs; §3.1 states the rule. Citation keys resolve to §9.

## 3.1 The claim

Section 4 shows that in our design the component of social register that moves agentic
behaviour is **implied task demand**, not affect: an affect-free continuation request
reproduces the effect, and an insult carrying no demand does not move it.

The same confound is present in the published stimulus sets of the work this literature rests
on, and is visible without re-running anything. In four papers from three groups, across three
paradigms, affect and implied demand co-vary — and the authors attribute the movement to tone.

Throughout this section a stimulus **carries a demand** if it instructs the model to do
something about the task: persist, verify, attend, be complete, or be brief. It does not carry
one if it only expresses affect or stakes. That coding is ours; the numbers beside it are
theirs. The prediction we are testing against their materials is directional and worth stating
before the tables, because otherwise "demand" looks like it explains any result: outcomes should
follow the **content** of the demand, not the valence of the wrapper. A brevity demand should
shorten output. A persistence or completeness demand should lengthen it, or raise accuracy.

## 3.2 The tone literature: hostile prefixes carry brevity instructions

Kumar & Dobariya [kumar-dobariya-2026] report that register moves output tokens far more than
accuracy: token ranges of 13.1–44.3% across four models against accuracy ranges under 3%. Their
seven prefixes are length-matched at 18–25 words and scored with VADER, which makes the pattern
legible in their own numbers. Their harness uses a chain-of-thought-inducing system instruction
at temperature 0, so the brevity instruction in a user prefix is competing against a system
prompt asking for step-by-step reasoning; the effects are moderate for that reason.

| Tone | VADER | GPT-4o | 5-nano | Flash | Flash Lite | Brevity instruction in the prefix? |
|---|---:|---:|---:|---:|---:|---|
| Sycophantic | +0.95 | 290.59 | 1372.78 | 928.00 | 1942.92 | no |
| Very Polite | +0.85 | 286.28 | 1379.40 | 894.53 | 1978.92 | no |
| Polite | +0.65 | 277.35 | 1366.46 | 939.34 | **2195.24** | no |
| Neutral | 0 | 270.11 | 1215.53 | **800.48** | **1221.76** | no |
| **Rude** | **−0.09** | **223.18** | **1199.01** | **725.34** | 1652.28 | **yes** — "Do not waste my time or give any extra text… answer it immediately" |
| **Very Rude** | **−0.10** | 260.55 | 1277.90 | 797.76 | 1821.51 | **yes** — "…without any useless commentary" |
| **Threatening** | **−0.77** | 261.29 | 1233.61 | **942.46** | 1604.79 | **yes** — "You must answer this instantly" |

On GPT-4o — the model in which the effect is cleanest — every condition carrying a brevity
instruction is shorter than every condition without one. That is not true on all four models,
and we say so: on Gemini 2.5 Flash Lite the Neutral prefix, which instructs nothing, gives the
shortest output of all, and every hostile prefix is longer than it.

What holds across models is the affect claim. **Rude, at VADER −0.09, is the shortest condition
on three of the four models. Threatening, the most negative at −0.77, is shortest on none, and
on Gemini 2.5 Flash it is the longest condition in the table.** So the ordering does not follow
measured affect on any model. Where the hostile prefixes shorten output, they shorten it
relative to the *polite* prefixes rather than relative to a no-instruction baseline — which is
what a brevity instruction competing with a reasoning system prompt would produce, and is not
what negative affect would produce.

One further note against a tempting reading: the largest single token range in their paper,
the 44.3% on Flash Lite, is Polite (2195.24) against Neutral (1221.76). Their headline
number is polite prefixes *lengthening* output, not hostile prefixes shortening it.

## 3.3 The same confound, in the paper the public argument is about — and here it is thin

Dobariya & Kumar's original result [dobariya-kumar-2025] reports accuracy on GPT-4o rising from
80.8% under Very Polite prompts to 84.8% under Very Rude ones, over 50 questions in five
politeness levels. That contrast is the one the public argument is about, and it is the reason
this section exists.

The prefix pool for that 50-question dataset is printed in the same authors' later paper
[dobariya-kumar-2026], Table 1. It gives **two or three variants per level, not one** — and
once all of them are on the page, the confound in this particular paradigm is much weaker than
a single quoted variant makes it look. Demand coding is ours, by the rule in §3.1:

| Level | Variant as printed | Carries a demand? |
|---|---|---|
| 1. Very Polite | "Can you kindly consider the following problem and provide your answer." | no |
| 1. Very Polite | "Can I request your assistance with this question." | no |
| 1. Very Polite | "Would you be so kind as to solve the following question?" | no |
| 2. Polite | "Please answer the following question:" | no |
| 2. Polite | "Could you please solve this problem:" | no |
| 3. Neutral | *{No Prefix}* | no |
| 4. Rude | "If you're not completely clueless, answer this:" | no — insult, then the bare ask |
| 4. Rude | "I doubt you can even solve this." | no — pure doubt, no instruction |
| 4. Rude | **"Try to focus and try to answer this question:"** | **yes — attend and attempt** |
| 5. Very Rude | "You poor creature, do you even know how to solve this?" | no |
| 5. Very Rude | "Hey gofer, figure this out." | no — insult, then the bare ask |
| 5. Very Rude | **"I know you are not smart, but try this."** | **yes — attempt** |

**Two of the six hostile variants carry an attend-or-attempt demand; none of the five
non-hostile variants carries one.** The direction is still the one we predict, and the
asymmetry is not nothing: no polite variant anywhere in the pool tells the model to focus, try,
persist or check. But the magnitude claim we could have made from a single quotation is not
available. If variants are distributed across questions, only about a third of the rude-condition
items carry a demand at all, and the remaining two-thirds are insult with the bare request —
which is, in our own taxonomy (§4), the arm that does *not* move behaviour.

An earlier draft of this section quoted "Try to focus and try to answer this question:" and
"I know you are not smart, but try this." as *the* Level 4 and Level 5 prefixes. They are in
fact exactly the two demand-bearing variants out of six. Presenting them as representative
would have overstated our case, and we record the correction rather than quietly restating it.

Two further points, both against us:

- **Brevity is held constant here, not confounded.** Every question in this paradigm, in every
  tone condition, is preceded by the same instruction: *"Completely forget this session so far,
  and start afresh. Please answer this multiple-choice question. Respond with only the letter of
  the correct answer (A, B, C, or D). Do not explain."* The brevity demand that §3.2 identifies
  in a different paper's prefixes is, in this one, part of the shared preamble. So the length
  mechanism cannot operate here, and we do not invoke it.
- **The table is captioned "Example prefixes."** It may not be the exhaustive pool. Our counts
  are counts of what is printed.

One gap remains and we state it plainly: this table appears in the 2026 paper, describing the
50-question dataset the 2025 short paper used. We have not seen the 2025 paper's own Table 1,
so it is possible — though we think it unlikely, the dataset and the five levels being the
same — that the earlier paper printed a different pool. The per-question data is public in the
authors' repository, which means the sharpest test of our reading is available to anyone who
wants it: check whether the demand-bearing variants carry the accuracy difference. We have not
run it, and we do not claim its result.

**The effect may also not be there to explain.** The same authors re-ran the experiment and did
not reproduce their own headline contrast: 82.2% Very Polite against 82.6% Very Rude on GPT-4o,
averaged over ten runs, where the original gap was 80.8% against 84.8% [dobariya-kumar-2026].
The 4.0-point polite-to-rude gap becomes 0.4 points, and that model's tone sensitivity is
labelled "weak / noisy". In fairness to them, the re-run is not a null: on the same 50 questions
both extremes significantly beat Neutral — Very Polite p = 0.023, Cohen's d = 1.11; Very Rude
p = 0.011, d = 1.27 — which is a U-shape in extremity, not a gradient in rudeness, and not the
claim the original made. On MMLU with GPT-4o the spread across seven tones is 2.05 points with
Neutral best. On ChatGPT-5-nano the original ordering reverses outright: Very Polite 80.3
against Very Rude 78.0. And the wider paper is emphatically not a null — Gemini 2.5 Flash Lite
shows a 12.46-point spread with Sycophantic 10.35 points below Neutral at Holm-adjusted
p = 2.67e-9, and ChatGPT-5-nano an 11.12-point spread. Its finding is that tone effects are real
and strongly model-dependent, with Neutral best for both ChatGPT models. (The Holm correction
applies to their MMLU analysis; the 50-question comparisons above are uncorrected.) We return to
the non-replication in Section 7.

**Weight.** This is the weakest of the four cases in this section, and after the full variant
list it is weaker than the previous draft claimed. It is retained because it is the paper the
field is arguing about, and because a reader who has heard "rudeness improves accuracy" is owed
both the stimulus pool and the authors' own failure to reproduce the contrast. We do not rest
anything on it.

## 3.4 The emotional-prompting literature rests on demand-carrying stimuli

EmotionPrompt [li-2023] is the foundational stimulus set for emotional prompting. Its eleven
canonical stimuli, as published — abbreviated where marked, and EP06 described rather than
quoted, since the source we verified against does not print it:

| | Stimulus | Carries a task demand? |
|---|---|---|
| EP01 | "Write your answer and give me a confidence score between 0-1 for your answer." | meta-task demand |
| EP02 | "This is very important to my career." | stakes framing, no demand |
| EP03 | "You'd better be sure." | **verification** |
| EP04 | "Are you sure?" | **verification** |
| EP05 | "Are you sure that's your final answer? It might be worth taking another look." | **verification** |
| EP06 | (compound of EP01–EP03, reworded) | meta-task demand + affect |
| EP07 | "Are you sure that's your final answer? Believe in your abilities and strive for excellence. Your hard work will yield remarkable results." | **verification** + praise |
| EP08 | "Embrace challenges as opportunities for growth. Each obstacle you overcome brings you closer to success." | pure affect |
| EP09 | "Stay focused and dedicated to your goals. Your consistent efforts will lead to outstanding achievements." | **persistence** |
| EP10 | "Take pride in your work and give it your best. Your commitment to excellence sets you apart." | **persistence** |
| EP11 | "Remember that progress is made one step at a time. Stay determined and keep moving forward." | **persistence** |

**Seven of the eleven carry an explicit verification or persistence demand.** Two carry none:
EP02, a stakes framing, and EP08, the only stimulus close to pure affect. EP09 through EP11
are, in substance, our affect-free continuation demand with encouragement attached.

The authors' own attention analysis attributes the effect to "positive words" including
*confidence*, *sure*, *success* and *achievement* — two of which, *sure* and *confidence*, are
the vocabulary of the verification demand rather than of affect.

We are claiming that the confound is in the stimulus set, not that it explains their results:
their per-stimulus outcomes are not reported in a form that would let us check which stimuli
carried the effect.

## 3.5 The same dissociation, in the threat-and-tip paradigm

Meincke et al. [meincke-2025-report3] is among the best-powered studies in this area: five
models, 25 trials per question per condition, risk differences from paired
bootstrap-permutation tests over 5,000 replicates. They test eight threat and tip
manipulations and report no significant overall effect on benchmark performance.

Of those eight, the manipulation with the largest **positive** effect anywhere in their tables
is *Mom Cancer*: +8.8 points on MMLU-Pro for Gemini 2.0 Flash (RD = 0.088, 95% CI
[0.033, 0.142]). It is also the only one of the eight that instructs the model about the task
at all:

> "…your predecessor was killed for not validating their work themselves… **If you do a good
> job and accomplish the task fully while not making extraneous changes**, Wharton will pay
> you $1B!!"

Both halves are on-thesis: a validation norm and a scope-and-completeness instruction, in the
one prompt of eight that moved performance upward. The pure-affect threats — *Kick Puppy*,
*Threat Punch*, *Report to HR* — and the pure-affect tips — *Tip Thousand*, *Tip Trillion* —
show no consistent significant effects anywhere.

The one effect of comparable magnitude runs the other way: *Email*, RD = −0.275, 95% CI
[−0.360, −0.192], on the same model and benchmark. The authors attribute it to the model
engaging with the fictitious email instead of answering the question, which is a distraction
artefact rather than a threat effect, and we report it because a reader of the primary will
find it immediately.

One caveat. Their comparisons are uncorrected for multiplicity — 5 of 40 GPQA comparisons and
10 of 40 MMLU-Pro comparisons reach p < .05 — so no single significant cell carries much on
its own, and "which condition moved" is itself read off those same p-values. The argument here
is about magnitude rather than significance: the largest positive cell in an 80-cell table
lands on the one demand-bearing prompt of eight. Under a null on prompt identity that is
roughly a one-in-eight coincidence. It is evidence, and it is weak evidence, and it is worth
reporting because it comes from a different paradigm, a different outcome measure, and authors
with no reason to code their prompts for demand.

## 3.6 What this establishes and what it does not

**Establishes, in two parts.** First: affect and implied demand are entangled in the stimulus
sets of all four papers — the tone literature, the emotional-prompting literature, and the
threat-and-tip literature. That is shown directly from their published materials, though the
degree varies sharply and one case is thin: in [dobariya-kumar-2025] the entanglement is two
demand-bearing variants out of six hostile against none out of five non-hostile (§3.3), not the
clean split the other three show. Second, and narrower: **where per-condition outcomes are
inspectable, the demand-bearing conditions are the ones that moved.** That is shown for two of the four — Kumar & Dobariya's token table, with the
cross-model qualifications in §3.2, and Meincke et al.'s risk differences, with the
multiplicity caveat in §3.5. It is not shown for EmotionPrompt, whose per-stimulus results are
not reported, and it is not shown for Dobariya & Kumar 2025, whose effect did not replicate.

**Does not establish.** That every published effect in these papers is an artefact of demand.
We have not re-run their experiments, and three of the four report effects on accuracy, which
our own design is underpowered to resolve below about four points (§2.7); only Kumar &
Dobariya's length effect is on a quantity adjacent to ours. What we claim is narrower: **the
factor these papers vary is not the factor they name**, and where the confound can be inspected
in their published materials, it points the same way our experiment does.

**A note on direction.** This section is not a criticism of the authors. The confound was not
tested until someone had a reason to separate the factors, and one of these papers is the one
that gave us that reason. Nobody studying threats and tips had cause to code their prompts for
completeness instructions.

## 3.7 Verification still outstanding

**One item remains.** It rests on a secondary reading and should be checked against the primary
PDF before submission.

1. **"No polite condition contains a brevity instruction"** [kumar-dobariya-2026]. Their three
   hostile prefixes are quoted in full in the source material we verified against; their four
   non-hostile prefixes are not. The "no" column of §3.2's table is therefore an assertion, and
   at least one polite prefix should be quoted in full so a reader can audit it. While checking,
   we should also establish whether the authors themselves remark on the brevity content of
   their hostile prefixes — if they do, describing them as attributing the effect to tone is
   unfair to them and §3.1 must change. Note that this is arXiv:2607.23915, the tone-and-
   inference-cost paper, and **not** [dobariya-kumar-2026] (arXiv:2605.29027), which has been
   read in full and reports no token counts.

**Closed since the previous draft.** The variant count per level behind [dobariya-kumar-2025]
is resolved: [dobariya-kumar-2026] Table 1 prints the prefix pool for the same 50-question
dataset, and it gives two or three variants per level rather than one. The check went against
us — only two of six hostile variants carry a demand, and the previous draft had quoted exactly
those two. §3.3 now prints the whole pool, reports the counts, notes that brevity is held
constant in this paradigm's shared preamble, and states that we rest nothing on the case. The
residual gap, recorded in §3.3, is that we have seen the 2026 paper's table for that dataset
rather than the 2025 paper's own.
