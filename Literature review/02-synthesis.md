# Synthesis

Written to your five questions, bluntly, as asked.

---

## 1. What preempts you

### Nothing preempts your central claim.

I found **no work** that:
- manipulates tone or social register **mid-task inside an agentic loop**;
- measures **agent persistence (number of steps before stopping)** as the dependent variable
  for a register manipulation;
- **decomposes politeness into affect and task-demand** as separate experimental factors;
- connects **conversational closing sequences** to LLM agent termination.

The tone literature (A1–A6, A8–A10, D1–D4) is single-turn question-answering, with one
exception (A6, PLUM) that varies the register of *prior conversational history* but measures
text quality, not agent behaviour, and injects no mid-task perturbation. **You are first on
the design.** Say so plainly; it will survive scrutiny.

### But four things are further along than your framing may assume.

**(a) The effect you are rebutting has already been rebutted by its own authors.**
This is the most important fact in this review. Dobariya & Kumar's AMCIS 2026 full paper
(A2) re-ran the identical 50-question GPT-4o experiment from the 2025 short paper (A1) and
got Very Polite 82.2% vs Very Rude 82.6% — against 80.8% vs 84.8% originally. They label
GPT-4o **"Weak / noisy"**. On the larger MMLU set, GPT-4o's total spread across all seven
tones is **2.05 pp and Neutral is best** — the direction reverses. Your paper is not
overturning a standing result; it is the agentic confirmation of a walk-back the authors
already published. **Reframe accordingly, and cite A2 in your abstract.** A reviewer who
knows A2 will otherwise think you are attacking a straw version of the literature.

**(b) "Tone moves length, not accuracy" is published, in single-turn, with better numbers
than a reviewer will expect.** Kumar & Dobariya (A3) report output-token ranges of 13.1%–44.3%
across tones against accuracy ranges of <1.5%–2.99%, with RM-ANOVA F(6,54)=248.14, p<.001 on
tokens for GPT-4o. Yin et al. (A4) reported tone-driven generation-length shifts in 2024.
**Your §7 (accuracy never moves) is not a novel claim in kind.** It is novel as an agentic
replication with a real execution-grounded evaluator. Present it that way.

**(c) An agentic, preregistered, 4,643-run study of prompt wording → agent spend at equal
quality already exists.** Weinberger & Hozez (A7): six reasoning models, two harnesses,
24 coding tasks, measuring reasoning tokens, tool calls **and agent turns**, with hidden
tests. Effects up to 7.4× on reasoning at 92–100% success throughout. They do not test tone
and they manipulate only the opening prompt — so they do not preempt your manipulation — but
they own the general result "prompt wording changes agentic spend and not correctness."
**Your §7, in the agentic setting, is a replication of A7 in a new substrate.** Cite it as
such; claiming it fresh is the fastest way to lose a reviewer.

**(d) Your closing-cue finding has an opening-prompt shadow in A7.** Their best-behaved arm,
`bounded_efficiency`, is defined as scope + smallest-sufficient-change + **an explicit stop
condition**, and it is the only variant that is free-or-better on all six models (0.48–1.16×).
So "a stop condition in the prompt reduces agentic work" is established for the opening
prompt. Your contribution is that a **content-free discourse cue delivered mid-task**
("this is the final note, no further notes will follow") does it harder than anything else
measured, **and that praise does it too, even when the same message says the task is
unfinished**. That second clause is the part nobody has. Lead with it.

### Two near-misses worth knowing about

- **A6 (PLUM):** in English, *interaction history* condition was significant
  (F(2,60)=4.268, p=0.019, η²=0.111) while *current-prompt politeness category* was not
  (p=0.211). That is the same qualitative ordering you report — where the register sits
  matters more than what it is. It is an ally, not a preempt, because the DV is text quality.
- **A12 (IHBench):** injects six interruption types at controlled mid-utterance points in
  workflow-following voice agents. Different modality, different DV, interruptions are task
  content rather than register — but it is the methodological precedent for controlled
  mid-task injection, and you should cite it in your design section rather than let a
  reviewer find it.

---

## 2. What contradicts you

### (a) Praise shortening work — this is your exposed flank.

Three independent findings say positive framing makes models produce **more**, not less:

| Source | Finding |
|---|---|
| A3 (Kumar & Dobariya 2026) | Sycophantic is the **longest** condition for GPT-4o (290.59t vs Rude 223.18t) and near-longest for Gemini 2.5 Flash Lite (1942.92t vs Neutral 1221.76t) |
| A10 (Gandhi & Gandhi 2025) | Positive prompts produce responses **8.1% longer** than neutral |
| A4 (Yin et al. 2024) | Summarization output length generally **shortens as politeness decreases** |

A reviewer will put these next to your §5 and ask why praise shortens work in your setting
and lengthens it in everyone else's.

**The answer you should give, and it is a good one:** these are different quantities.
They measure *verbosity within a single response*; you measure *persistence across turns*.
Schegloff & Sacks (B6) predicts exactly this dissociation — an appreciation is a canonical
**pre-closing** move, so it is closing-implicative at the level of the *exchange* while
being expansive at the level of the *turn*. If your data can show that praise conditions
produce a **longer final turn but fewer total turns**, you have converted a contradiction
into your strongest positive result. **Check this before you write §5.** If it does not hold,
you need to soften the praise claim.

### (b) Your opening-prompt null, against Yin et al.

Yin et al. (A4) is the largest-n study in the area (5,700 MMLU / 5,200 C-Eval / 5,591 JMMLU
items, native-speaker-validated 8-level scale) and they find real effects at the rude extreme:
GPT-3.5 MMLU 60.02 → 51.93 (level 8 → 1), Llama2-70B 55.11 → **28.44**. Someone will cite
this against you.

Your defences, in order of strength: (i) their effects are concentrated at the extreme and in
weaker/older models, and **GPT-4 in their own Table 1 is essentially flat** (75.82 at level 8,
76.47 at level 1); (ii) A2 and A5 both show modern models flattening toward tone-insensitivity;
(iii) your DV is agentic behaviour, not MCQ accuracy, so their result and yours are not in
direct conflict. Make all three; do not rely on (iii) alone.

### (c) Flat per-step thinking, against A3's token results.

A3 finds tone moves output tokens by 13.1%–44.3% within a single response. You find
thinking-per-step is flat. These can both be true — they use a CoT-inducing system
instruction on MCQs with the Gemini thinking budget forced to zero, which is a very different
regime from a ReAct step — but **you should state the comparison explicitly and explain the
difference**, rather than letting it sit as an unremarked inconsistency. Note also that A3's
largest token effects sit in conditions carrying explicit brevity instructions, which is
itself an explanation.

### (d) The emotional-prompting literature, if taken at face value.

D1 (EmotionPrompt, 115% on BIG-Bench) and D2 (NegativePrompt, IJCAI 2024, 46.25% on
BIG-Bench) both claim large affect-driven gains. **Do not argue with them directly — cite D3.**
Vaugrante et al. show the 115% comes from selecting the single best cue, and that averaging
over stimuli gives 4.42% on BIG-Bench and 2.58% overall, with "a general lack of statistically
significant differences across nearly all techniques tested" across six models. That is a
cleaner rebuttal than anything you would construct yourself.

### (e) Nothing contradicts §2, §3, §4 or §6.

Your mid-task effect, your demand-not-politeness decomposition, your persistence-not-effort
mechanism and your first-attempt-is-best result have no contradicting literature that I found.
§6 is actively corroborated (C1, B4).

---

## 3. The 5–8 sources a reviewer will demand

Cite all of these or expect an objection. Ranked.

1. **Dobariya & Kumar 2026, AMCIS** (arXiv:2605.29027) — **the non-negotiable one.** Their own
   failure to replicate their own headline effect. If this is not in your paper, the paper
   looks uninformed.
2. **Dobariya & Kumar 2025** (arXiv:2510.04950) — the target. Quote their Table 1 prefixes;
   the demand/affect confound is legible in it.
3. **Kumar & Dobariya 2026** (arXiv:2607.23915) — establishes length-not-accuracy in
   single-turn, and its VADER scores (Rude −0.09, Very Rude −0.10 vs Sycophantic +0.95) are
   the best external evidence for your §3 that exists.
4. **Weinberger & Hozez 2026** (arXiv:2608.01347) — the agentic prompt-wording precedent, with
   turns as a DV and a stop-condition arm. Your nearest neighbour.
5. **Yin et al. 2024, SICon** (10.18653/v1/2024.sicon-1.2) — the origin of the line, the
   largest n, and the first report that tone moves output length.
6. **Meincke et al. 2025, Report 3** (arXiv:2508.00614) — the existing tone-adjacent null from
   a credible group; your precedent for publishing one.
7. **Vaugrante, Niepert & Hagendorff 2024** (arXiv:2409.20303) — the failed replication of the
   emotional-prompting literature; your §8 framing.
8. **Cuadron et al. 2025** (arXiv:2502.08235) — "premature disengagement", 4,018 trajectories;
   the mechanism vocabulary for your stopping results.

Strongly recommended beyond the eight: **Sharma et al. 2024 (ICLR)** for sycophancy,
**Huang et al. 2024 (ICLR)** for §6, **Miller 2024** and **Sclar et al. 2024** for the
statistics of your null, **Schegloff & Sacks 1973** for §5's theory.

---

## 4. Gaps — what is actually yours

Stated as the claims you can make without qualification.

1. **Positional dependence of register effects in agentic loops.** Nobody has shown that the
   same words have no effect in the opening prompt and a replicable effect mid-task. A6 gestures
   at it for text quality in one language; nobody has it for agent behaviour. **This is your
   headline.**
2. **Decomposition of tone into affect and demand, with double dissociation.** An affect-free
   demand reproducing the whole effect *and* a demand-free insult producing nothing is a clean
   factorial result that no one in this literature has run. Everyone else's stimuli confound
   the two — demonstrably so, in A1's Table 1 ("Try to focus and try to answer this question:"
   filed under *Rude*) and in A3's Table 2 (every hostile prefix contains a brevity instruction;
   no polite prefix does). **Your second-strongest contribution, and the one most likely to be
   cited by others.**
3. **Persistence, not effort, as the moved quantity.** A3 and A7 both moved *tokens*. Nobody has
   separated tokens-per-step from number-of-steps and shown the effect lives entirely in the
   latter. This also constitutes a direct empirical test of A2's "thinking budget / soft
   trigger" conjecture, which its authors explicitly flag as unvalidated. **Say that you are
   testing their conjecture and that it does not survive.**
4. **Closing cues as a termination lever, and the praise-as-pre-closing account.** No prior
   work connects conversation-analytic closing sequences to agent termination. The result that
   a bare closing cue with no praise stops the agent hardest of anything measured is entirely
   new, and the theoretical frame (B6) is unclaimed. **The most distinctive part of the paper —
   develop it properly rather than leaving it as an observation.**
5. **Praise-induced early termination as a sycophancy phenomenon.** The sycophancy literature
   (E1–E3) measures agreement bias and stance-flipping. D4 links positive stimuli to increased
   sycophancy but not to effort. **Nobody has linked praise to reduced work or early stopping.**
   Frame via E2's face-preservation account: continuing to work after a satisfied user's
   appreciation is face-threatening. Note that E4's "effortful" is the *human's* effort — do
   not miscite it.
6. **Per-turn regrading against the benchmark's own evaluator.** B4's oracle-round result is
   the nearest analogue, at n=60 on HotpotQA. Your ~86% figure on ~11,850 graded trajectories
   with a real execution-based evaluator is a much stronger version of the same claim.

**What is *not* a gap, and should be framed as replication rather than discovery:** the
accuracy null (§7, see A3/A7), and "extra turns don't help" as a general proposition
(C1/C3/B4). Both are still worth reporting — just position them as confirmation in a new
substrate.

---

## 5. Terminology — adopt these instead of coining

| Your term | Adopt | Source | Why |
|---|---|---|---|
| **"no-op turn"** | **"redundant step"** | B3, RedundancyBench (arXiv:2605.29893) | The established term, with a benchmark behind it and an explicit definition: steps labelled *by informational contribution to task completion*. "No-op" reads as a tool-call that failed; "redundant step" is exactly your concept. Keep "no-op" only if you mean a turn with no tool call at all — and then define both. |
| "agent stops early" | **"premature disengagement"** | B1, Cuadron et al. | One of their three named failure modes, validated against human expert judgement over 4,018 trajectories. Also gives you **"analysis paralysis"** for the opposite pattern. |
| "tone" | **"social register"** (with "tone" as the informal gloss) | A3 uses it; standard in linguistics | Sharper, and it is the term that makes your affect/demand decomposition sayable: register is the variable, affect and demand are its components. A3 defines it for you. |
| "how many turns before the register change takes effect" | **"turn of flip"**-style naming | E3, SYCON-Bench | The accepted way to report *when* in a multi-turn interaction a social pressure bites. Coin by analogy (e.g. "turn of stop") and cite them. |
| "sensitivity to rewording" | **"sensitivity" / "consistency"** as defined | F3, Errica et al. (NAACL 2025) | Defined metrics, ground-truth-free, already refereed. |
| "consistency across repeated runs" | **pass^k** | G3, τ-bench | Standard, and relevant given your §8 point-estimate instability. |
| "turns" as a cost unit | **"agent turns"/"agent steps"**, reported alongside cost | F5, A7 | A7 reports turns as a first-class billed quantity; F5 is the argument that you must. |
| "effort" | split into **"reasoning tokens per step"** and **"trajectory length in steps"** | A7 | A7 measures both separately and so should you; "effort" unqualified is what lets A3's and your results look contradictory when they aren't. |

Two more conventions worth adopting:
- **Report ranges, not point estimates**, for anything prompt-dependent (F1, F2). This is also
  the cleanest way to present your §8 honestly: direction and significance replicated, point
  estimates did not.
- **Report cluster-adjusted standard errors** (F4). Miller shows cluster adjustment can inflate
  SEs by up to 3×. Since your trajectories cluster within tasks, this is not optional for a
  well-powered-null claim, and it is precisely what A1's uncorrected paired t-tests lack.

---

## 6. Second substrate — recommendation

You asked which benchmark best supports measuring **turn count and partial progress**.

**Recommendation: AppWorld (G2), with OSWorld 2.0 (G5) as the ambitious alternative.**

**AppWorld** is the pragmatic choice. It is a native ReAct loop with a **100-LLM-call
ceiling** — five times your current 20-turn headroom, which matters because a persistence
experiment with a 20-turn ceiling is measuring a censored variable. It has ~8 unit tests per
task that you can regrade per turn exactly as you already do on SpreadsheetBench, and it has
something no other candidate offers: **collateral-damage detection**. That gives you a second
DV with real stakes — *does an agent nagged into persisting start breaking things?* — which
turns a measurement paper into one with a safety claim. The caveat is honest: AppWorld's
*reported* metrics (TGC/SGC) are binary per task, so your partial-credit measure would be
computed from the unit tests yourself. Define it and preregister it.

**OSWorld 2.0** is the better instrument if you can afford it: **fine-grained partial rewards
with ~27 checkpoints per task**, and submissions scored at **150/300/500 agent-step budgets**.
A benchmark that natively reports the same trajectory at three step budgets is close to
purpose-built for a persistence claim — you could report how each intervention shifts the
step-budget curve instead of a single number. The cost is the problem: ~318 tool calls per
task for a frontier agent. Verify its numbers against the paper (marked UNVERIFIED in G5)
before committing.

**Avoid:** τ-bench (binary end-state grading, and F6 reports it **counts empty responses as
successful** — actively hazardous when your experiment is about agents stopping early);
WebArena (14% baseline ceiling makes turn effects uninterpretable); SWE-bench Verified
(F6/F7: insufficient tests, ~59% of audited failures attributable to test flaws, solution
leakage, publicly retired by OpenAI).

---

## 7. Three things to fix before submission

1. **Check whether praise lengthens your final turn while shortening the trajectory.** If yes,
   §5 becomes your best result and the A3/A10/A4 contradiction dissolves. If no, soften §5.
2. **Reframe §7 and the accuracy null as replication** of A3 (single-turn) and A7 (agentic),
   not as discovery. You lose nothing — §1–§5 carry the paper.
3. **Quote A1's Table 1 and A3's Table 2 in your confound section.** The confound you are
   claiming is visible in the prior work's own stimulus tables, and in A3's own VADER scores
   (Rude −0.09, Very Rude −0.10 — affectively neutral, yet carrying the largest effects).
   That is far more persuasive than asserting it.
