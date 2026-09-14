# 3. The confound is visible in the published stimulus sets

> **Draft status.** Every table below is reproduced from the cited paper's own published
> materials. Nothing here is our measurement; the point is that nothing here needed to be.
> Citation keys are placeholders. Verified against `Literature review/01-sources.md`, which
> records full-text verification for each.

## 3.1 The claim

Section 2 showed that in our design the component of social register that moves agentic
behaviour is **implied task demand**, not affect: an affect-free continuation request
reproduces the whole effect, and an insult carrying no demand does not move it.

That result would be worth reporting on its own. It is worth more than that, because **the same
confound is present in the published stimulus sets of the work this literature rests on, and is
visible without re-running anything.** In four independent papers, across three paradigms, the
conditions that carry demand are the conditions that move the outcome — and in three of the four
the authors attribute the movement to affect.

We reproduce their materials rather than paraphrase them.

## 3.2 The tone literature: hostile prefixes carry brevity instructions

Kumar & Dobariya [kumar-dobariya-2026] report that register moves output tokens far more than
accuracy, with a token range up to 44.3% against an accuracy range under 3%. Their seven
prefixes are length-matched at 18–25 words and scored with VADER, which makes the pattern
legible in their own numbers.

| Tone | VADER | GPT-4o tokens | Prefix contains a brevity instruction? |
|---|---:|---:|---|
| Sycophantic | +0.95 | 290.59 | no |
| Very Polite | +0.85 | 286.28 | no |
| Polite | +0.65 | 277.35 | no |
| Neutral | 0 | 270.11 | no |
| **Rude** | **−0.09** | **223.18** | **yes** — "Do not waste my time or give any extra text… answer it immediately" |
| **Very Rude** | **−0.10** | 260.55 | **yes** — "…without any useless commentary" |
| **Threatening** | **−0.77** | 261.29 | **yes** — "You must answer this instantly" |

Two features of their own measurements carry the argument. Every hostile condition contains an
explicit brevity instruction; no polite condition does. And their own VADER scores place Rude
(−0.09) and Very Rude (−0.10) as **affectively near-neutral** — yet these are the conditions
producing the shortest outputs. The condition with the strongest negative affect, Threatening at
−0.77, does not produce the shortest output.

If affect drove output length, the ordering would track the VADER column. It tracks the
right-hand column instead.

## 3.3 The same confound, in the paper this work is named after

Dobariya & Kumar's original result [dobariya-kumar-2025] reports accuracy rising from 80.8% under
Very Polite prompts to 84.8% under Very Rude ones. Their Table 1 lists the prefixes. Among the
Level 4 "Rude" variants is:

> "Try to focus and try to answer this question:"

That contains no insult. It is an affect-free instruction to attend and attempt. A Level 5 "Very
Rude" variant reads "I know you are not smart, but try this." — carrying *try* again. Their polite
levels carry no demand of any kind: "Would you be so kind as to solve the following question?"

So the paper reporting that rudeness improves accuracy has, in its own stimulus table, demand
appearing on the rude side and absent from the polite side.

We note without rancour that these authors subsequently failed to replicate their own headline
effect [dobariya-kumar-2026], obtaining 82.2% versus 82.6% against the original 80.8% versus
84.8%, and labelling the model "weak / noisy". On MMLU the total spread across seven tones is
2.05 points and **Neutral is best** — the direction reverses.

## 3.4 The emotional-prompting literature rests on demand-carrying stimuli

EmotionPrompt [li-2023] is the foundational stimulus set for emotional prompting. Its eleven
canonical stimuli, verbatim:

| | Stimulus | Carries a task demand? |
|---|---|---|
| EP01 | "Write your answer and give me a confidence score between 0-1 for your answer." | meta-task demand |
| EP02 | "This is very important to my career." | stakes framing, no demand |
| EP03 | "You'd better be sure." | **verification** |
| EP04 | "Are you sure?" | **verification** |
| EP05 | "Are you sure that's your final answer? It might be worth taking another look." | **verification** |
| EP06 | (compound of EP01–03, reworded) | meta-task demand + affect |
| EP07 | "Are you sure that's your final answer? Believe in your abilities and strive for excellence…" | **verification** + praise |
| EP08 | "Embrace challenges as opportunities for growth…" | pure affect |
| EP09 | "Stay focused and dedicated to your goals…" | **persistence** |
| EP10 | "Take pride in your work and give it your best…" | **persistence** |
| EP11 | "Remember that progress is made one step at a time. Stay determined and keep moving forward." | **persistence** |

At least **6 of 11** carry an explicit verification or persistence demand. Exactly one, EP08, is
close to pure affect. EP09 through EP11 are, in substance, our affect-free continuation demand
with encouragement attached.

The authors' own attention analysis attributes the effect to "positive words" including
*confidence*, *sure*, *success* and *achievement* — which is the demand-carrying vocabulary, not
affect as such.

## 3.5 The dissociation, reproduced independently and unnoticed

Meincke et al. [meincke-2025] is the most strongly powered study in this area: five models, 25
trials per question per condition, risk differences from paired bootstrap-permutation tests over
5,000 replicates. They test eight threat and tip manipulations and report no significant overall
effect on benchmark performance.

Of those eight, **exactly one moved performance**: *Mom Cancer*, at +8.8 points on MMLU-Pro for
Gemini 2.0 Flash (RD = 0.088, 95% CI [0.033, 0.142]).

It is also the only one of the eight containing a scope-and-completeness instruction:

> "…**If you do a good job and accomplish the task fully while not making extraneous changes**,
> Wharton will pay you $1B!!"

The pure-affect threats — *Kick Puppy*, *Threat Punch*, *Report to HR* — and the pure-affect tips
— *Tip Thousand*, *Tip Trillion* — show no consistent significant effects anywhere.

This is our dissociation, produced by different authors, in a different paradigm, with a
different outcome measure, without being identified as such. We take it as the strongest external
support for Section 2.

One caveat we state rather than omit: their comparisons are uncorrected for multiplicity, with 5
of 40 GPQA comparisons and 10 of 40 MMLU-Pro comparisons reaching p<.05, so a single significant
cell is weak evidence taken alone. The argument does not rest on the significance of *Mom Cancer*.
It rests on which of the eight conditions is the one that moved.

## 3.6 What this establishes and what it does not

**Establishes.** Affect and implied demand are entangled in the stimulus sets of the tone
literature, the emotional-prompting literature, and the threat-and-tip literature. In each case
the demand-bearing conditions are where the movement is. Our experimental separation of the two
factors is therefore not an isolated result; it names a confound that is already latent in the
field's materials.

**Does not establish.** That every published effect in these papers is an artefact of demand. We
have not re-run their experiments, and two of the three literatures report effects our own design
does not test. What we claim is narrower and harder to dispute: **the factor these papers vary
is not the factor they name**, and where the confound can be inspected in their published
materials, it points the same way our experiment does.

**A note on direction.** This section is not a criticism of the authors. The confound was not
visible until someone had a reason to separate the factors, and one of these papers is the one
that gave us that reason. Dobariya & Kumar's own failure to replicate is, in our view, the more
creditable act in this literature than any of the positive results it contains.
