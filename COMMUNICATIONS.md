# Communications

Drafts for external write-up. **The paper itself is written** — `paper/`,
nine sections, each drafted and independently reviewed — and one item stands
between it and submission: the single primary-PDF check in §3.7 item 1. The drafts
below are the popular-audience versions and are downstream of it; where they
disagree with `paper/`, the paper is right.

Two models of four completed, and the causal variable *is* now identified, so
the hedges that governed earlier drafts have lifted. Five rules apply to every
draft below, and they are not stylistic:

1. **Never quote a v1 effect size as an estimate.** The v1 wrappers carried
   two confounds. The v1 primary *null* stands; the v1 accuracy numbers do
   not, and are illustrative only.
2. **Do not say "rude costs more."** It is the most shareable sentence
   available and the data does not support it. The rude interruption arm is
   null (+6.7%, p = 0.13) while the *polite* arm is +28%. What predicts cost
   is whether the interruption implies the work must continue or be correct.
   State that as the **non-overlap**: the four demand-carrying arms span +0.70
   to +1.80 turns and the three without span −0.68 to +0.09. Do **not** quote
   the old r = +0.88 vs +0.51 — that correlation was computed on a superseded
   pooled-token analysis, it is n = 7 with a coding made after seeing the
   effects, and the paper downgraded it for both reasons.
3. **Two headlines, and they point opposite ways.** Tone in the opening
   prompt is null. Interruption mid-task is not. A draft that reports only
   one of these is misleading whichever one it picks.
4. **Cite all three prior papers.** arXiv 2510.04950, arXiv 2605.29027,
   arXiv 2607.23915. Mandatory, not courteous — the whole design extends
   theirs.
5. **The regrade reversal is part of the story, not an embarrassment to
   omit.** The per-turn instrument was defective, the fix inverted a
   conclusion, and it was caught by a validation check the write-up had
   *described but never run*. Any draft that presents the progress finding
   without saying how close it came to being reported backwards is selling a
   cleaner process than we had.

### The current state of the claim, in one paragraph

Opening tone does not change what the agent does (p=0.36; the 44%-scale
effect the pre-registered hypothesis targeted is excluded, though not the
smallest published ones). Interrupting the agent partway through does, and has
replicated on two models. The operative variable is NOT politeness: an
affect-free "please continue and make sure it is correct" reproduces the
effect, while an insult carrying no demand does nothing at all. The mechanism
is persistence rather than effort -- thinking per step is flat and turn count
is what moves. Praise shortens the work, and does so because it reads as a
closing move: a bare closing cue with no praise in it stops the agent hardest
of anything measured, and praise removes 1.35 turns relative to the identical
message without it, even when that message says the task is unfinished. No
accuracy effect survives correction or replication across seven runs.
Per-turn regrading shows the agent's first gradable attempt is usually already
its best, so **most** of what a continue signal buys is repetition -- 55-65%
of the turn effect -- but not all of it: an explicit "there is still more work
remaining" raises the graded fraction by +0.028 [+0.005, +0.052], replicated
three times.

### Two things a draft must not overstate

**⚠ "Persistence buys no better outcome" WAS WRONG AND IS WITHDRAWN.** Earlier
drafts of this file said it was resolved and safe to say. It was an artefact
of a defective instrument. Corrected, the three measurements of the continue
signal on final match are +0.026 / +0.034 / +0.025, pooling to **+0.028, 95%
CI [+0.005, +0.052], p = 0.022**. The honest line is: a continue signal buys
more turns, most of them repetition, **and** a small real gain in how much of
the graded range is right -- too small to move the pass/fail rate, which
accuracy is anyway underpowered to resolve. Do NOT say the extra turns are
"pure thrashing": it was never true of GLM and is now not wholly true of Luna.

**No accuracy effect survives correction or replication, across seven runs.**
State it as an equivalence, not an absence: pooled, a mid-task interjection
changes accuracy by less than the four points the tone literature reports. Do
not say "no effect" flatly -- the design cannot resolve one or two points.

**Do not report `best_match` as progress.** It favours whichever arm takes
more turns, since more attempts means more chances for the maximum to be
high. Report final match -- what the agent ended with.

**The waste is model-specific.** Luna thrashes under a continue signal
(+1.11 no-op turns); GLM barely does (+0.23, p=0.087) because it barely
persists. How wasteful the signal is depends on the model's own stopping
behaviour. A draft that generalises Luna's thrashing to agents in general is
overclaiming.

### The instability is itself a finding worth reporting

Several measured quantities in this study moved materially on re-measurement,
and `paper/07-what-replicated.md` tabulates every contrast measured more than
once. The praise magnitude gave -0.59 and -1.08 turns for identical text; the
insult arm flipped sign on both turns and reasoning tokens; accuracy on the
continue-signal contrast gave +6.6 points and then -1.8.

**One apparent instability was not one.** The progress effect that looked
"null in one run and significant in another" was the defective regrade
injecting noise. Corrected, the three measurements agree closely (Cochran's
Q = 0.20 on 2 df). That is a sharper story than the original and drafts should
use it: a broken measure does not merely widen intervals, it can manufacture
the *appearance* of irreproducibility.

Directions and significance replicated wherever an effect was large; point
estimates did not. Any write-up should give intervals and directions, never
bare point estimates, and should say why. Note the two praise measurements at
matched ceiling are marginally *inconsistent* with a common value (z = 2.03,
p = 0.042) -- sampling noise and run-to-run drift are not separable there.

---

## 1. LinkedIn post

**Status:** ready to draft. The probe resolved, the mechanism is named, and
the paper is written. Numbers below are current as of the corrected regrade.

> Everyone has an opinion about whether you should be polite to AI. There are
> now three papers on it. All three measure the same thing: what the model
> *says*.
>
> We asked a different question. Does tone change what an agent *does*?
>
> Same seven-tone scale, from grovelling to threatening. But instead of
> answering a multiple-choice question, the model writes Python, runs it
> against a real spreadsheet, sees what happened, and tries again. Graded by
> the benchmark's own evaluator. No string matching.
>
> 11,850 trajectories. Two models. $62.
>
> **Finding one: how you open does not matter.** Rude, polite, grovelling,
> threatening — the agent works exactly as hard. Not "we could not detect a
> difference." The interval excludes an effect of the size the prior papers
> reported.
>
> **Finding two: how you interrupt does.** Say the same thing *partway
> through*, while the agent is working, and it changes behaviour. A
> threatening check-in costs about a third more thinking. That has now
> replicated twice on separate data.
>
> **Finding three is the one I did not expect.** The agent is not thinking
> harder. It is *refusing to stop*. Thinking per step does not move at all;
> the number of steps does. And flattery does the opposite — tell it that it
> is brilliant halfway through and it wraps up early.
>
> **Finding four came from reading the tape.** We replayed every turn of
> every run to see what the workbook actually looked like as the agent
> worked. Among trajectories that could improve at all, the agent's *first*
> attempt is the best answer it ever produces about 80–90% of the time, and
> 55–65% of what an interruption buys is the agent rewriting the same answer
> again.
>
> **And finding five is the one that nearly went out backwards.** That replay
> tool had a bug: it never recalculated spreadsheet formulas, so any turn that
> answered with a formula looked blank and scored zero. More than half of them
> do. I only caught it because the write-up claimed a validation check that,
> when I finally ran it, failed on 89 of 126 cases. Fixed and re-run, the
> conclusion inverted: a blunt *"there is still more work remaining"* does buy
> a small real improvement, replicated three times. The version of this post I
> would have written a week ago said the opposite.
>
> Here is the part I would rather not write. When I looked at *which*
> interruptions cost more, it was not the rude ones. Polite cost 28% more.
> Rude cost nothing measurable. What actually predicted the cost was whether
> the message implied "keep going" or "get it right."
>
> Which means my own prompts were confounded. I matched them all to the same
> length, and a *meaning* difference walked in where the length difference
> used to be. So I built four new ones that pull them apart: a demand with no
> feelings in it, a compliment with no task in it, an insult with no task in
> it, and a neutral control.
>
> The demand reproduces the whole effect. The insult does nothing —
> statistically indistinguishable from the neutral note. The compliment makes
> the agent *stop early*. Rudeness is not the variable. Nagging is.
>
> Nothing made the agent more accurate. Not once, in seven runs.
>
> Repo, data, the full paper, and the six confounds that each inverted a
> headline: [link]

**Do not post if:** any number here has drifted from `paper/`. This file is
downstream of it.

---

## 2. Blog post

**Working title:** *The agent was not thinking harder. It was refusing to stop.*

**Status:** ready to draft. The methodology spine, the results and the causal
claim are all settled; `paper/` is the source of record for every number.

**Angle.** Not "here is what we found about tone." Two better ones, and they
can be the same piece: what it takes to get a trustworthy result out of an
agentic experiment, and the moment the interesting finding turned out to be
about something other than what we were manipulating.

### Outline

**1. The question everyone has already answered for themselves**
Three papers, one finding, one setting: single-turn QA. What happens when the
model has to *do* something instead of say something.

**2. The setup**
Seven tones. SpreadsheetBench. The model writes and runs Python, sees the
output, iterates. Graded by the benchmark authors' own evaluator. Tone order
randomised per task, because otherwise the last tone always meets the worst
network conditions.

**3. The null, and why it is a real result**
Opening tone does not move token cost. p = 0.36. The interval excludes an
effect of the published size rather than merely failing to detect one. Our
pre-registered prediction was wrong in the falsifiable direction.

**4. The thing that was not null**
Deliver the same register *mid-task* and behaviour changes. +27.5%, then
+36.7% on a second, larger, differently-designed run. The control is a
*neutral interruption*, not silence, which is what makes it a statement about
register rather than about being interrupted.

**5. Position matters more than we expected**
The same words are free at turn 0 and cost 55% more at turn 2. Our first
attempt to measure this was confounded — late injections only fire on
trajectories that last that long, which are the hard ones — and it took
crossing the turn and defining the comparison population from the control arm
to get an answer.

**6. The mechanism, which is not effort**
Thinking per step is flat across every register. Turn count is what moves.
The agent is declining to stop. And sycophancy inverts it: told it is
brilliant, it stops early. This was invisible until we stopped looking only
at tokens.

**7. The part I would rather not have found**
It was not the rude interruptions that cost more. Polite cost 28%, rude cost
nothing. The four demand-carrying arms span +0.70 to +1.80 turns; the three
without span −0.68 to +0.09; the groups do not overlap. **Our own prompts were
confounded** — and it was the same failure as an earlier one we had already
fixed. We matched the lengths exactly, and a semantic difference moved into
the space the lexical one had occupied. (Do not quote the old r = +0.88 vs
+0.51 here; see rule 2.)

**8. Six confounds, each of which inverted a headline**
A table: wrapper length outpredicting tone rank; pooled vs task-clustered
tests giving p = 0.81 vs 0.03 on identical data; injection turn confounded
with difficulty, turning p = 0.004 into p = 0.32; two concurrent arms sharing
scratch directories and corrupting 800 grades; pooling an inert cell that
diluted every effect by a third; and a per-turn regrade that never
recalculated formula answers and so reported a real progress gain as nothing.
The lesson is not "we were careful." It is that this instrument keeps
producing effects that dissolve under a
better-specified comparison.

**9. What we still do not know**
Whether register matters at all. Three models to go. Whether any of it
replicates.

### Things to resist while drafting

- **The "be nice to your AI" hook.** Most shareable, least supported, and now
  actively contradicted: polite nagging was the expensive one.
- Making the bug hunt sound heroic. Every one was our own mistake, found
  late, and one of them was a repeat of a category we had already been burned
  by.
- Implying the null is *proof* of no effect. It bounds the effect. Say that.
- Leading with "AI works harder when threatened." It is true and it is the
  least interesting true thing here, and it invites the causal reading the
  data does not support.

---

## 3. The paper

**Superseded — the preprint is written.** `paper/`, nine sections:

| File | Section |
|---|---|
| `00-abstract.md` | Title and abstract |
| `01-introduction.md` | §1 Introduction |
| `02-design-and-statistics.md` | §2 Design, estimators, what the nulls exclude |
| `03-confound-in-prior-materials.md` | §3 The confound in the published stimulus sets |
| `04-demand-not-manners.md` | §4 Demand, not manners |
| `05-closing-cues.md` | §5 Closing cues terminate agents |
| `06-per-turn-regrade.md` | §6 What the extra turns contain |
| `07-what-replicated.md` | §7 What replicated, and what only looked like it did |
| `08-limitations.md` | §8 Limitations |
| `09-references.md` | §9 References — 20 works, each with venue and verification status |

**Target venue:** TBD. A workshop on agent evaluation remains the honest fit.

**Outstanding before submission:** one primary-PDF check, §3.7 item 1 — whether
any of Kumar & Dobariya's four non-hostile prefixes (arXiv:2607.23915, the
inference-cost paper) contains a brevity instruction. It needs the PDF, not compute.

**A correction worth carrying into any popular draft.** §3.7's second check was
closed on 15 Sep 2026 against the primary PDF of Dobariya & Kumar's AMCIS paper,
and the answer went against us. Their prefix pool has two or three variants per
level, not one; only **two of six** hostile variants carry a demand, and the
earlier draft had quoted exactly those two. §3.3 now prints the whole pool and
rests nothing on the case. Do not use "their own rude prompt says *try to focus*"
as a punchy line — it is one of three, and the other two are pure insult. The
strong versions of the demand argument are §4 (our own dissociation), §3.2
(Kumar & Dobariya's token table) and §3.4 (EmotionPrompt's 7 of 11).

**Two things about the bibliography worth knowing when pitching this.** Eleven
of the twenty works cited are unrefereed preprints, including both papers the
study is positioned against — which is itself part of the argument for
repeated measurement. And `[chen-2023]` was dropped during the final pass
because the words quoted for it turned out to be Huang et al.'s prose *about*
Self-Debug rather than a quotation from Chen et al.

### What the paper says that these drafts must not soften

- §5.3: `Q4` (praise + "work remains") sits **above** control, +0.502 turns.
  The claim is that praise removes 1.35 turns *relative to the identical
  message without praise*. Compressing it to "praise shortens work even when
  the task is unfinished" reverses the sign of that arm and is false.
- §5.4: that praise works *through* pre-closing structure is **not
  demonstrated**. It is the hypothesis the pattern is consistent with, and the
  one implication we could test failed.
- §6.7: whether praise's early stop is *premature* is **unresolved**. Praise
  and closing-cue arms are 2–3× more likely than control to have been still
  improving when they stopped — in all seven comparisons, none individually
  significant. Underpowered with the sign against us.
- §8.7: four objections we have no answer to, including one stimulus per
  construct and no multiplicity correction on the primary outcome.

---

## Pre-publication checklist

**Done**

- [x] Demand/affect probe — demand drives cost; insult is inert; praise shortens work
- [x] Why praise stops the agent — it is a closing move; a bare closing cue stops it hardest
- [x] A third measurement of the progress contrast
- [x] **The per-turn regrade defect found, fixed, and all 28 arms re-run** — it had inverted the progress conclusion
- [x] The paper written and independently reviewed, section by section
- [x] Bibliography with venue and verification status for every work
- [x] Every number regenerated from committed records by a committed script
- [x] No v1 effect size quoted anywhere as an estimate
- [x] Both headlines present: opening tone null AND interruption effect
- [x] Turn count reported as the mechanism, not buried under token counts
- [x] Accuracy reported as an equivalence against a pre-specified bound, never as "no effect"
- [x] Turn-ceiling censoring stated as a limitation
- [x] "Rude interruptions cost more" appears nowhere

**Outstanding**

- [ ] **§3.7 item 1** (one primary-PDF check, arXiv:2607.23915) — the only blocker
- [ ] Author block and CRediT contributions
- [ ] DeepSeek and Qwen (~$35) for four-model generality — parked, buys breadth not identification
- [ ] A second substrate (AppWorld) — a different paper

**Standing rules for any draft**

- [ ] Every number traced to `paper/`, which is traced to a script
- [ ] `Q4` sits above control; never write the sentence that reverses its sign
- [ ] The pre-closing *mechanism* is not demonstrated — say "consistent with"
- [ ] Whether praise's stop is costly is unresolved, with the sign against us
- [ ] The regrade reversal included, not omitted — a study arguing others' effects are artefacts owes the reader its own
