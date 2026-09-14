# Synthesis

Written to your five questions, bluntly, as asked. **Revised after full-text verification of
24 sources** — several claims in the first draft were wrong and are corrected here.

---

## 1. What preempts you

### Nothing preempts your central claim. This is now verified, not assumed.

Full-text searches across every candidate found **no work** that:
- manipulates tone or social register **mid-task inside an agentic loop**;
- measures **agent persistence (steps before stopping)** as the DV for a register manipulation;
- **decomposes politeness into affect and task-demand** as separate experimental factors;
- connects **conversational closing sequences** to LLM agent termination.

Specific negatives worth knowing, because they are the places a preempt would have lived:

- **Weinberger & Hozez (2608.01347)** — exhaustive search of v6, *including all 18 prompt
  templates in Appendix C*: zero instances of "polite", "rude", "tone" or "courteous". Their
  manipulations are task-content only.
- **Cuadron et al. (2502.08235)** — identify no prompt or discourse cue that triggers
  premature disengagement. All their manipulations are model-side (reasoning-effort parameter,
  function-calling on/off, model size).
- **SYCON-Bench (2505.23840)** — the most likely preempt, being multi-turn sycophancy under
  sustained pressure. Their pressure types are persuasion strategies and verbatim disagreement.
  **Praise is never a pressure type**, and no output-length or effort measure appears anywhere.
- **IHBench (2606.19595)** — the six interruption types are a taxonomy of *what the user does*
  (correction, topic switch, backchannel, pushback), not *how they say it*. No register
  manipulation, no closing cue.
- **PLUM (2604.16275)** — register never changes part-way through a task; the three history
  conditions are fixed top-level cells.

**You are first on the design. Say so plainly; it will survive scrutiny.**

### But four things are further along than the first draft assumed.

**(a) The effect you are rebutting has already been rebutted by its own authors.**
Dobariya & Kumar's AMCIS 2026 paper re-ran the identical 50-question GPT-4o experiment and got
Very Polite 82.2% vs Very Rude 82.6%, against 80.8% vs 84.8% originally. They label GPT-4o
**"Weak / noisy"**. On MMLU the total spread across seven tones is 2.05 pp and **Neutral is
best** — the direction reverses. **Cite this in your abstract.**

**(b) "Tone moves length, not accuracy" is published.** Kumar & Dobariya report token ranges of
13.1–44.3% against accuracy ranges under 3%, with RM-ANOVA F(6,54)=248.14 on tokens. Yin et al.
reported tone-driven length shifts in 2024. Vaugrante et al. add an independent instance: CoT
changed response length from 531 to 931 characters with a **0.01%** accuracy difference.
**Your §7 is not novel in kind.**

**(c) An agentic, preregistered, 4,644-run study of prompt wording → agent spend at equal
quality already exists.** Weinberger & Hozez measure reasoning tokens, tool calls *and agent
turns* against hidden tests, with effects up to 7.4× at 92–100% success. **Your §7 in the
agentic setting is a replication of theirs in a new substrate.** Claiming it fresh is the
fastest way to lose a reviewer.

**(d) Your closing-cue finding has an opening-prompt shadow in the same paper.** Their
`bounded_efficiency` arm is defined as scope + smallest-sufficient-change + **an explicit stop
condition**, and is the only variant free-or-better on all six models (0.48–1.16×). So "a stop
condition in the prompt reduces agentic work" is established for the opening prompt. Your
contribution is that a **content-free discourse cue delivered mid-task** does it harder than
anything measured, **and that praise removes 1.35 turns relative to the same continuation
message without it, even when that message states the task is unfinished** (Q4 vs Q5). That
second clause is the part nobody has. Lead with it — worded as the within-pair contrast, not
as "below control" (Q4 alone is +0.50 above control; see §7.2).

### Two things the first draft got wrong in your favour

**§6 is a stronger claim than originally framed.** Huang et al. **never test execution
feedback.** They point to it as the expected fix, citing Self-Debug: "the code executor serves
as the perfect verifier to judge the correctness of predicted programs." A naive reading of
Huang et al. therefore *predicts your agent should improve across turns*. **Your §6 tests the
escape hatch they proposed and never ran.**

**And Balachandran's "perfect verifier" is oracle-assisted in both senses** — best-of-n is
oracle selection over finished answers, and even their "sequential" critic "knows the
ground-truth… and then uses it to offer textual feedback." Your agent's execution feedback is
real but not oracle-informed. **So your flat accuracy is consistent with the scaling
literature, not a contradiction of it.** That is a much safer framing than the first draft's.

### Two near-misses to distinguish explicitly

- **PLUM's Corollary A.1, "History Anchoring"** — argues prior-turn tone anchors behaviour more
  than the immediate prompt's tone. Conceptually adjacent to your §1–§2 ordering. Distinguish on
  DV (response quality on isolated Q&A, no task success measure) and on the fact that their
  history-construction protocol is **genuinely underspecified**: one sentence of method, no turn
  count, no code, and an empty README on the released corpus. You can cite that as a limitation
  of theirs.
- **IHBench** — cite as design precedent for controlled mid-task injection, but note the
  mechanism differs: their interruptions are scripted into pre-generated conversations and the
  model produces **a single next response**, with no subsequent turns to persist through. Yours
  is a live rollout. The resemblance is "inject something mid-task", not "measure downstream
  persistence".

---

## 2. What contradicts you

### (a) Praise shortening work — still your exposed flank, but weaker than it looked.

| Source | Finding | How much weight it carries |
|---|---|---|
| Kumar & Dobariya 2026 | Sycophantic is the **longest** condition for GPT-4o (290.59t vs Rude 223.18t) | Real. Peer-adjacent, 10 runs, temperature 0. Must be addressed. |
| Yin et al. 2024 | Summarization length generally shortens as politeness decreases | Real. Largest-n study in the area. |
| Gandhi & Gandhi 2025 | Positive prompts → responses **8.1% longer** | **Much weaker than the first draft implied — see below.** |

**On Gandhi & Gandhi specifically, full text changes the picture.** The 8.1% is scoped **only
to "essays and blog-style responses"**, not all tasks. There is **no significance test, no CI,
no SD, no per-condition n** anywhere in the paper — for that or any other headline number. The
model list includes "Claude v1.3" described as a latest version in March 2025 (retired in 2023),
and "ChatGPT (v4)". No code or data release. **Treat it as a descriptive claim in an unreviewed
preprint with no statistical backing; do not hedge §5 on its account.** Note also that the same
paper reports negative prompts producing **17.6% shorter** responses, which it calls
"disengagement or terseness" — cutting against a simple valence-length story.

**⚠ The reconciliation I proposed does NOT hold. It has now been tested against our data and
must not be used.** See `results/analysis/praise_turn_vs_trajectory.py`.

The hypothesis was that praise lengthens the final turn while shortening the trajectory, giving
a turn-level/trajectory-level dissociation that Schegloff & Sacks predicts. **The data says
otherwise.** Praise shortens the trajectory *and* reduces total output, with no compensating
lengthening anywhere:

| Contrast (paired by task, cluster bootstrap) | Δ turns | Δ tokens/turn |
|---|---|---|
| Praise (assistant) vs control | **−1.080** [−1.464, −0.710] | +11.4 [−230.6, +237.6] n.s. |
| Praise (the work) vs control | **−0.934** [−1.308, −0.547] | +99.6 [−136.7, +334.3] n.s. |
| Praise isolated (Q4 vs Q5) | **−1.347** [−1.738, −0.950] | −232.0 [−506.5, +2.1] n.s. |

Total tokens fall roughly in proportion to turns (praise vs control −5,880 [−8,593, −3,472]).
Trailing non-code "sign-off" turns do not rise under praise (+0.053 [−0.028, +0.140], n.s.),
and the bare closing cue actually produces **fewer** of them (−0.087 [−0.153, −0.018]). The
praise arm ran at a **10-turn ceiling** (max observed `n_turns` = 10; `RESULTS.md` says the same),
which censors the continue-signal arms — Q5 at 6.37 mean turns is nearest it — so if anything the
Q4-vs-Q5 gap is understated.

**The direct test is not possible from the graded records, but it is from the raw logs.** The
graded records carry tokens at trajectory level only. The per-call raw logs
(`results/raw/study2_*.jsonl`, gitignored) carry `prompt_tokens`, `completion_tokens`,
`reasoning_tokens` and `extra.turn` on every call, and each `--interject` invocation writes one
log per arm — so if those files still exist, per-turn tokens for every arm are recoverable with
no re-run. If they do not, re-running the praise arm costs $8.61 at the observed rate. Neither
is needed for the paper: three proxies already point the same way.

**So argue the weaker, true thing instead.** The prior results measure *verbosity of a single
response to a question*; you measure *steps taken on a task*. These are different dependent
variables in different paradigms, not a dissociation you have demonstrated within one dataset.
Say that plainly. Do not claim the pre-closing account is empirically supported here — it
remains a plausible mechanism for the *stopping* result, which is what the data does support.

### (b) Your opening-prompt null, against Yin et al.

GPT-3.5 MMLU 60.02 → 51.93 (level 8 → 1); Llama2-70B 55.11 → **28.44**. Defences, in order:
(i) effects concentrate at the extreme and in weaker models — **GPT-4 in their own Table 1 is
essentially flat** (75.82 at level 8, 76.47 at level 1); (ii) A2 and A5 both show modern models
flattening; (iii) your DV is agentic behaviour, not MCQ accuracy. Make all three.

### (c) Flat per-step thinking, against Kumar & Dobariya's token results

They move output tokens 13–44% within a single response. Both can be true — CoT-inducing system
prompt on MCQs with the thinking budget forced to zero is a very different regime from a ReAct
step — but state the comparison rather than leaving it unremarked. Note their largest token
effects sit in conditions carrying explicit brevity instructions.

### (d) Reflexion, if cited uncritically

AlfWorld improves steadily **to trial 12**. That runs against §6. Its "trials" are independent
episode restarts with an accumulating memory buffer, not extra turns in one trajectory, and it
requires a genuine binary reward — so it is not commensurate. **Either cut it or cite only its
WebShop failure case** ("after only four trials, we terminate the runs as the agent does not
show signs of improvement").

### (e) The number that sits closest to yours

**Huang et al.'s "No Change" rates: GPT-4 90.5% / 90.5%, GPT-4-Turbo 96.0% / 88.0%.** These are
not your statistic — theirs is "answer unchanged after two rounds of intrinsic correction on
reasoning QA", yours is "first attempt was the best of those made, in a 20-turn
execution-grounded agent". **But they sit right beside your 86% and a reviewer will notice.
Distinguish them in the text.**

**Also pick one first-attempt figure and name its run.** `RESULTS.md` reports three: **90%**
(Stage 0, ceiling-10 per-turn regrade, "in 90% of multi-turn trajectories the first code turn is
already the best"), and **87% / 85%** (Stage 1, ceiling-20, Luna / GLM). The "~86%" in the brief is
the Stage 1 average. Quoting 86% next to Huang's 88–96% without saying which run and ceiling
invites exactly the comparison you want to control.

### (f) Nothing contradicts §2, §3 or §4.

---

## 3. The 5–8 sources a reviewer will demand

1. **Dobariya & Kumar 2026, AMCIS** (arXiv:2605.29027) — **non-negotiable.** Their own failure
   to replicate their own headline effect.
2. **Dobariya & Kumar 2025** (arXiv:2510.04950) — the target. Quote their Table 1.
3. **Kumar & Dobariya 2026** (arXiv:2607.23915) — length-not-accuracy, plus the VADER scores.
4. **Weinberger & Hozez 2026** (arXiv:2608.01347) — **cite a specific version, see §7.**
5. **Yin et al. 2024, SICon** (10.18653/v1/2024.sicon-1.2) — the origin, largest n.
6. **Meincke et al. 2025** (arXiv:2508.00614) — the existing null, *and* the Mom Cancer result.
7. **Vaugrante et al. 2024** (arXiv:2409.20303) — the failed replication; your §8 template.
8. **Cuadron et al. 2025** (arXiv:2502.08235) — "premature disengagement".

Beyond the eight: **Sharma et al. 2024 (ICLR)**, **Huang et al. 2024 (ICLR)**, **Miller 2024**
and **Sclar et al. 2024** for the statistics, **Schegloff & Sacks 1973** for §5's theory, and
**Ma et al. 2024** for your own substrate — including their multi-round decline result.

---

## 4. Gaps — what is actually yours

1. **Positional dependence of register effects in agentic loops.** Verified unoccupied.
   **Your headline.**

2. **Decomposition of tone into affect and demand, with double dissociation — and it is now
   corroborated three times over by other people's data.** This is the contribution most likely
   to be cited by others.
   - **A1's own Table 1** files *"Try to focus and try to answer this question:"* under **Rude**.
   - **A3's own Table 2**: every hostile prefix carries a brevity instruction ("Do not waste my
     time or give any extra text"); no polite prefix does. Their own VADER scores put Rude at
     **−0.09** and Very Rude at **−0.10** against Sycophantic at **+0.95** — the conditions with
     the largest token effects are affectively neutral.
   - **EmotionPrompt's EP01–EP11**: at least **6 of 11** carry an explicit verification or
     persistence demand ("You'd better be sure", "take another look", "Stay focused and
     dedicated", "give it your best", "Stay determined and keep moving forward"). Exactly one
     (EP08) is close to pure affect. **Reproduce the table.**
   - **Meincke et al.**: of eight threat/tip prompts, the only one that moved performance
     (+8.8 pp, CI [0.033, 0.142]) is **Mom Cancer** — the only one containing a
     scope-and-completeness instruction. Pure-affect threats and tips did nothing.
     **Your dissociation, reproduced independently, in a different paradigm, without the
     authors noticing.**

3. **Persistence, not effort, as the moved quantity — but narrow the claim.** Weinberger &
   Hozez already separate the channels: `deep_thinking` raises reasoning volume 2.2× with "no
   new functional units" (effort-per-step), while `max_certainty` adds "+1.75 post-success
   calls" (step count). The tokens-vs-turns distinction is not itself new. **Your contribution
   is that a mid-task social-register demand loads *exclusively* onto persistence**, against
   their mixed picture. It also directly tests A2's "thinking budget / soft trigger"
   conjecture, which its authors flag as unvalidated.

4. **Closing cues as a termination lever, and the praise-as-pre-closing account.** No prior work
   connects closing-sequence pragmatics to agent termination. Entirely new. **The most
   distinctive part of the paper — develop it properly.**

5. **Praise-induced early termination as a sycophancy phenomenon — the gap is verified.**
   Full-text checks of all four sycophancy papers: Sharma measures agreement bias only (its
   "concise" preference feature ranks **21st of 23**, so you are not restating a known length
   bias); ELEPHANT's four dimensions all concern softening content; SYCON-Bench never uses
   praise as pressure; Ibrahim's "effort" is the **human's**. **Word the claim precisely:**
   *no work links praise or sycophancy to the AI's own reduced task effort, shortened output, or
   early termination — prior work establishes sycophancy as an agreement/content bias, or as a
   driver of human relational effort.*
   **⚠ But the face-threat explanation is YOUR extension, not ELEPHANT's.** Nothing in their
   framework concerns curtailing work. Present it as your own reading of Goffman and cite
   ELEPHANT only for the construct.

6. **Per-turn regrading against the benchmark's own evaluator.** No equivalent statistic exists
   in an agentic, execution-grounded setting. The nearest analogues are Huang et al.'s "no
   change" rates and Self-Refine's diminishing per-iteration deltas — both single-turn, neither
   pass/fail-per-turn. **Novel, with the caveats in §2(e).**

**Not gaps — frame as replication:** the accuracy null (§7), and "extra turns don't help" as a
general proposition.

---

## 5. Terminology — adopt these instead of coining

| Your term | Adopt | Source | Why |
|---|---|---|---|
| **"no-op turn"** | **"redundant step"** | RedundancyBench (2605.29893) | `RESULTS.md` defines a no-op turn as one "after which the graded range is unchanged" — an *output* criterion. That maps onto their counterfactual definition (a step is redundant iff removing it does not flip success to failure), not onto their **"Duplicated Step"** subtype, which additionally requires *identical tool name, args and output* — your definition does not require identical code. Cite "Duplicated Step" as the nearest named subtype, not as equivalent. ⚠ Do not compare base rates: some of their redundant steps are synthetically injected, and they report no overall redundant fraction. |
| "agent stops early" | **"premature disengagement"** — *for the failure mode, not for your effect* | Cuadron et al. | Their coinage, verbatim: "LRMs sometimes terminate tasks based solely on their internal simulation… either through direct abandonment or by delegating hypothetical action sequences." ⚠ **But your Stage 0 regrade shows the praise stop is *not* premature**: "the share of trajectories still improving when they stopped is 2–6% in every arm, with no gap between praise and control." So say praise induces *earlier* disengagement that the per-turn regrade shows is not premature — that is a sharper claim than borrowing a term for a failure you did not observe. Also gives you **"analysis paralysis"**. |
| "tone" | **"social register"** | A3 defines it | Makes the affect/demand decomposition sayable: register is the variable, affect and demand its components. |
| "when the cue bites" | **"turn of stop"**, by explicit analogy to **Turn of Flip** | SYCON-Bench | Same estimator design (mean earliest turn of divergence from expected behaviour). ⚠ **Say the analogy is structural, not substantive** — they measure stance conformity, not work quantity. Better still, use them as the mirror image: disagreement changes what the model says; praise changes how much it does. |
| "consistency across runs" | **pass^k** | τ-bench | "the chance that all k i.i.d. task trials are successful, averaged across tasks." Standard. |
| "effort" | split into **reasoning tokens per step** and **trajectory length in steps** | Weinberger & Hozez | Unqualified "effort" is what makes your result look inconsistent with A3's when it isn't. |
| ~~"sensitivity"/"consistency"~~ | **don't** | Errica et al. | ⚠ Both metrics are classification-only — sensitivity normalises by `ln(C)`, consistency is a TVD between categorical distributions. The authors say so: "they work for classification problems only". Consider dropping the citation. |

Two conventions: **report ranges, not point estimates** (Sclar, Mizrahi), and **report
cluster-adjusted standard errors** (Miller).

---

## 6. Second substrate — recommendation confirmed, with sharper numbers

**AppWorld, primary. This got stronger under verification.**

The crux held up against the evaluator source code: `TestTracker` keeps `passes` and `failures`
lists, each entry carrying a `requirement` and a `label`, and serialises both. **You can compute
a per-turn "fraction of unit tests passed" DV from the stock evaluator without modifying it.**
Add: 100-LLM-call ReAct ceiling (verified verbatim — compare against ReAct's 100, not parallel
function calling's 15), avg. 8 and max 22 grading tests per task, 750 tasks, **~$0.7 per
example**, Dockerised, ACL 2024 Best Resource Paper.

Two corrections to carry into the writeup: **collateral damage is not a separate metric** — it
is extra entries in the same unit-test battery, so splitting it out is engineering you must do
and describe; and **do not cite "GPT-4 Turbo 32.7 / 17.5" as one row** — it is a cross-method
splice of two different methods' best TGC figures.

**OSWorld 2.0 — downgrade to aspirational/future work. The cost gap is 50–100×, not 2–3×.**
Per-trajectory cost is **~$2.4–76**, with the best config at **~$72** against AppWorld's ~$0.7.
A thousand frontier-class trajectories is ≈$70K; your 11,850-trajectory design has no
equivalent at any realistic budget. Add 31 self-hosted mock websites, AWS orchestration and a
residential proxy. It is also an **unrefereed preprint**, and the attractive 150/300/500-step
result is **embedded in a cost-performance sweep figure, not a standalone table** — most cleanly
demonstrated for GPT-5.5 only. And with 108 tasks, trajectory volume means re-running the same
tasks repeatedly.

**Avoid τ-bench — but for the right reason.** It is **ICLR 2025, refereed**, so the case must
rest entirely on design. It does: reward is `r = r_action × r_output ∈ {0,1}` by construction,
and because a genuine refusal and an empty non-answer both leave the database unchanged, they
are indistinguishable to the grader on tasks whose ground truth is "do nothing". The ABC audit
records this as two separate scoring failures. **Scope the damning statistic correctly** — the
trivial agent's 38% is on the intentionally-impossible subset, not the whole benchmark.

**Also correct:** OSWorld 1.0's reward is **not** binary — it is `R : S×A → [0,1]` awarding "a
positive decimal under 1" for partial achievement. Near-binary in practice, not by definition.

---

## 7. Things to fix before submission

1. **Pick a version of arXiv:2608.01347 and stick to it.** Six versions exist. v6 changed the
   title, reports 4,644 runs not 4,643, and dropped the "$166", the "92–97% success" range and
   **both quotes** this review originally attributed to it. Cite `v1` explicitly for those, or
   move wholesale to v6.
2. **Word §5 from the table, not from the summary sentence.** `RESULTS.md` already reports this
   correctly: Q4 (praise + "there is still more work remaining") is **+0.50 turns vs control,
   p = 0.020** — *longer*, not shorter — and the praise effect is stated there as the
   **Q4-vs-Q5 contrast, −1.35 turns, p < 0.0001** ("COMPLETION is refuted… the effect is larger
   here than praise-alone against control"). The independent re-analysis in
   `results/analysis/praise_turn_vs_trajectory.py` agrees: **+0.502 [+0.090, +0.908]** and
   **−1.347 [−1.738, −0.950]**.

   The hazard is one prose sentence in the same section — "doing so while telling it there is
   more to do does not prevent that" — and the brief's paraphrase "praise still shortens work
   even when the message says the task is unfinished". Both read as Q4 < control, which is false.
   Use: *praise removes 1.35 turns relative to the same message without praise, even when that
   message states the task is unfinished.* The finding is intact; only the sentence needs care.

   **(b) The longer-final-turn escape route is closed** — see §2(a). Drop it.

   What survives intact: the bare closing cue stops hardest (−1.443 [−1.860, −1.036]), praise
   shortens relative to control (−1.080 and −0.934), "work remains" alone lengthens (+1.849
   [+1.387, +2.284]), per-turn effort is flat on every contrast, and accuracy does not move
   (0.299–0.349, all CIs overlapping).
3. **Reframe §7 and the accuracy null as replication**, and **reframe §6 as testing Huang et
   al.'s untested escape hatch** rather than as confirming them.
4. **Quote the three confound tables** (A1 Table 1, A3 Table 2 + VADER, EmotionPrompt EP01–EP11)
   and the Meincke Mom Cancer result. The confound is visible in other people's materials.
5. **State that your 20-turn ceiling is your own choice.** SpreadsheetBench's official
   multi-round protocol caps at **five rounds** — and their own GPT-4o *declines* from
   single- to multi-round (soft 18.35 → 16.96), which the authors attribute to redundant
   re-fetching. **Cite that: it is prior evidence for your mechanism from your own substrate.**
6. **Quote SpreadsheetBench's evaluator self-audit** (4% instruction-level false negatives) in
   your validity section — it bounds the noise floor on per-turn regrading.
7. **Statistics for the well-powered null.** Miller has **no TOST or equivalence testing** —
   do not cite him for it. Use his clustered SE formula (paired-and-clustered variant, since
   your trajectories cluster within tasks) and his MDE inversion to report the realized minimum
   detectable effect at your n, then state that your CI excludes effects at or above the prior
   literature's size. For equivalence-testing language you need a separate source (Lakens 2017).
   And compare against Sclar's **median 7.5–10 point** spread, not the 76-point single-task
   maximum.
