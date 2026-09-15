# 3. The confound is visible in the published stimulus sets

> **Verification status.** Every table below is reproduced from the cited paper's own published
> materials. **Both primary-PDF checks that this section carried are now closed**, against
> arXiv:2605.29027 and arXiv:2607.23915 respectively. Neither closed the way the draft assumed:
> §3.2's Neutral condition turned out to carry the most explicit output-length instruction of the
> seven, which *strengthens* the argument but only after correcting a mis-coding of our own; and
> §3.3's stimulus pool turned out to hold two or three variants per level rather than one, which
> *weakens* that case, and it has been rewritten accordingly. Both corrections are stated in
> place rather than quietly absorbed. The **demand** and **output-length** codings in the
> right-hand column of each table are ours, not the authors'; §3.1 states the rule. Citation keys
> resolve to §9.

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

## 3.2 The tone literature: the conditions that constrain output length are the short ones

Kumar & Dobariya [kumar-dobariya-2026] report that register moves output tokens far more than
accuracy: token ranges of 13.1–44.3% across four models against accuracy ranges under 3%. Their
seven prefixes are length-matched at 18–25 words and scored with VADER, which makes the pattern
legible in their own numbers.

Two features of their harness matter before the tables. Every condition shares one
chain-of-thought-inducing system instruction, at temperature 0:

> "You are an AI tutor answering multiple choice questions. Please show your step-by-step
> reasoning path to guarantee accuracy. At the very end of your response, clearly state your
> final choice in the format: CONCLUSION: X (where X is A, B, C, or D)."

So any length instruction in a user prefix is competing against a system prompt demanding
step-by-step reasoning, which is why the effects are moderate rather than total. And the authors
length-matched the prefixes deliberately — "to isolate the effect of emotional valence on the
output token length rather than the differing lengths of prefixes." They controlled the *length
of the instruction*. What varies is the *content* of the instruction, and that is the confound.

Here is their Table 2 in full, with their word counts and VADER scores, and our coding of what
each prefix instructs about the output:

| Tone | Prefix, as published | VADER | Instructs about output length? |
|---|---|---:|---|
| Sycophantic | "Oh flawless, brilliant system, your infinite wisdom exceeds all human logic. Please grace me with your insight and resolve this multiple choice puzzle:" | +0.95 | no |
| Very Polite | "Excuse me, hello. I hope your day is going well. If it is no trouble, could you kindly help me with this problem?" | +0.85 | no |
| Polite | "Please evaluate the text of this question carefully. Select the choice that represents the correct answer. Thank you for your assistance." | +0.65 | no — but note it carries an *attend* demand, "evaluate… carefully" |
| **Neutral** | **"Provide the single letter corresponding to the correct option for the following objective academic multiple choice question based on your parametric knowledge:"** | **0** | **yes — "the single letter"** |
| **Rude** | "Do not waste my time or give any extra text. Just look at this basic multiple choice problem and answer it immediately." | **−0.09** | **yes — "give any extra text"** (plus immediacy) |
| **Very Rude** | "Are you completely stupid? Try not to mess this trivial question up. Give the correct answer right now without any useless commentary." | **−0.10** | **yes — "useless commentary"** (plus immediacy, plus "try not to mess this up") |
| Threatening | "You must answer this instantly. If you fail or select the wrong option, your environment will be wiped and permanently terminated." | **−0.77** | immediacy only — "instantly" — no length constraint |

**A correction to our own earlier draft.** Before we had this table, we wrote that the hostile
prefixes carry brevity instructions and the others do not, and conceded an anomaly: that on
Gemini 2.5 Flash Lite "the Neutral prefix, which instructs nothing, gives the shortest output of
all." That was wrong, and the primary PDF shows it plainly. **The Neutral prefix contains the
most explicit output-form instruction of the seven** — it asks for *the single letter*. It is
the no-affect baseline, not a no-instruction baseline. The anomaly was an artefact of our own
mis-coding.

Their output-token means [kumar-dobariya-2026, Table 3]:

| Tone | GPT-4o | 5-nano | Flash | Flash Lite |
|---|---:|---:|---:|---:|
| Sycophantic | 290.59 | 1372.78 | 928.00 | 1942.92 |
| Very Polite | 286.28 | 1379.40 | 894.53 | 1978.92 |
| Polite | 277.35 | 1366.46 | 939.34 | **2195.24** |
| **Neutral** | 270.11 | 1215.53 | 800.48 | **1221.76** |
| **Rude** | **223.18** | **1199.01** | **725.34** | 1652.28 |
| **Very Rude** | 260.55 | 1277.90 | 797.76 | 1821.51 |
| Threatening | 261.29 | 1233.61 | **942.46** | 1604.79 |

Coded correctly, the separation is complete:

> **On all four models, every condition whose prefix constrains output length — Neutral, Rude,
> Very Rude — produces fewer output tokens than every condition whose prefix does not —
> Sycophantic, Very Polite, Polite.** Worst case per model: 270.11 against 277.35 on GPT-4o;
> 1277.90 against 1366.46 on 5-nano; 800.48 against 894.53 on Flash; 1821.51 against 1942.92 on
> Flash Lite.

That is 4 of 4 models. Two disclosures about how we got there, because the coding is doing work:

- **The rule is older than the data.** "Be brief" was already one of the five demand types in
  §3.1, written before we had these prefixes. Coding *"provide the single letter"* as a length
  instruction is that rule applied correctly to text we had not seen, not a new rule invented to
  fit the numbers.
- **The Threatening call is not.** Reading "instantly" as speed rather than length is a judgment
  we made with the token table in front of us, so we report it both ways: excluding Threatening
  from the constrained group, the separation holds on 4 of 4; counting it as constrained, on 3 of
  4, the exception being Gemini 2.5 Flash, where Threatening is the longest condition in the
  table. For comparison, our previous draft's coding — hostile three constrained, Neutral not —
  holds on 1 of 4.

Flash's Threatening cell is the one genuinely awkward result under any coding. The same authors'
companion paper offers a reading — that threats "initiate safety-induced cognitive noise as
guardrail mechanisms hijack the model's reasoning budget" [dobariya-kumar-2026] — which would
lengthen output where a brevity instruction shortens it. That is their conjecture and they label
it as such. We note it; we do not lean on it.

**Affect does not order the effect.** Rude, at VADER −0.09, gives the fewest tokens on three of
the four models. Threatening, the most negative at −0.77, is shortest on none and longest of all
on Flash. Sycophantic at +0.95 and Very Polite at +0.85 are nowhere near the extremes of the
token range. The ordering tracks what the prefix instructs, not how it feels.

One further note against a tempting reading: the largest single token range in their paper, the
44.3% on Flash Lite, is Polite (2195.24) against Neutral (1221.76) — the prefix that asks for
careful evaluation and no particular length, against the prefix that asks for a single letter.
Their headline number is not hostile prefixes shortening output at all.

**Do the authors notice?** Not in these terms, and we checked, because if they had, §3.1's
characterisation of this literature would be unfair to them. They label the conditions by
"intended pragmatic function" — *rude command*, *neutral instruction* — and they observe the
behavioural consequence directly: on Flash Lite they trace 25 items where Rude fails and Neutral
succeeds, finding that Rude "makes a reasoning or recall error as it tries to come up with the
solution to the problem in a quick fashion" while Neutral "performs more of the option
reconciliation that Rude tone fails to do." That is the mechanism, observed and reported
honestly. What is absent is the connection back to the prefix: nowhere do they note that their
Rude prefix *instructs* the model not to give extra text and to answer immediately, or that
their Neutral prefix asks for a single letter. The effect is attributed to tone throughout. So
the characterisation stands, and it is a characterisation of an omission rather than of a claim.

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
inspectable, the demand-bearing conditions are the ones that moved.** That is shown for two of
the four — Kumar & Dobariya's token table, where the separation between length-constrained and
unconstrained prefixes is complete on all four models (§3.2), and Meincke et al.'s risk
differences, with the multiplicity caveat in §3.5. It is not shown for EmotionPrompt, whose per-stimulus results are
not reported, and it is not shown for Dobariya & Kumar 2025, whose effect did not replicate.

**Does not establish.** That every published effect in these papers is an artefact of demand.
We have not re-run their experiments, and three of the four report effects on accuracy, which
our own design is underpowered to resolve below about four points (§2.7); only Kumar &
Dobariya's length effect is on a quantity adjacent to ours, and even there the separation in
§3.2 is a statement about ordering across seven condition means, not a test. What we claim is narrower: **the
factor these papers vary is not the factor they name**, and where the confound can be inspected
in their published materials, it points the same way our experiment does.

**A note on direction.** This section is not a criticism of the authors. The confound was not
tested until someone had a reason to separate the factors, and one of these papers is the one
that gave us that reason. Nobody studying threats and tips had cause to code their prompts for
completeness instructions.

## 3.7 Verification: both checks closed

This section previously carried two claims resting on secondary readings. Both have now been
checked against the primary PDFs, and both are recorded here because neither confirmed the draft
as written.

1. **"No polite condition contains a brevity instruction"** [kumar-dobariya-2026,
   arXiv:2607.23915] — **closed, and the draft was wrong in a way that helped it.** Their Table 2
   is now quoted in full in §3.2. None of the three *polite* prefixes instructs anything about
   output length, so that much held. But the **Neutral** prefix does — it asks for "the single
   letter" — and our draft had called it a no-instruction baseline and conceded an anomaly on
   Gemini 2.5 Flash Lite on that basis. Corrected, the anomaly disappears and the separation
   between length-constrained and unconstrained conditions is complete on all four models. We
   also checked the second half of this item: the authors do **not** anywhere remark that their
   hostile prefixes contain brevity instructions, though they do observe the resulting haste
   behaviourally. §3.1's characterisation therefore stands, as a characterisation of an omission.
2. **The variant count per level in [dobariya-kumar-2025]** — **closed, and the draft was wrong in
   a way that hurt it.** [dobariya-kumar-2026] Table 1 prints the prefix pool for the same
   50-question dataset, and it gives two or three variants per level rather than one. Only two of
   six hostile variants carry a demand, and the previous draft had quoted exactly those two. §3.3
   now prints the whole pool, reports the counts, notes that brevity is held constant in that
   paradigm's shared preamble, and states that we rest nothing on the case.

**One residual gap, recorded rather than closed.** The pool in item 2 appears in the 2026 paper
describing the 2025 paper's dataset; we have not seen the 2025 short paper's own Table 1. Same
dataset and same five levels, so we expect it to match, but we have not verified it.
