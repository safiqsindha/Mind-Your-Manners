# 5. Closing cues curtail agents, and praise is one

> **Draft status.** Numbers verified against `results/analysis/praise_turn_vs_trajectory.txt`
> (paired by task, cluster bootstrap over tasks, 8,000 reps) and `RESULTS.md`; the by-position split
> of §5.3 comes from `results/analysis/injection_position.py`, on the paper's own estimator and
> seed. arXiv:2608.01347 is cited at **v6** throughout, per the version hazard in Appendix C.

## 5.1 The question this section answers

Section 4 leaves one arm unexplained. **Praise, carrying no demand at all, shortens the trajectory** — the
only place in the design where register acts on its own. Three readings survive, and they are different
claims. Under **completion**, praise is read as evidence the task is finished. Under **confidence**, praise
raises the agent's estimate of work already produced so it stops checking — about being right, not about
being finished. Under **closing**, praise is a conversational closing move, and the agent is responding to
discourse structure rather than to any claim about task state.

The third is the one prior work gives us a vocabulary for and no evidence about. Closing sequences are a
well-described conversational object: a pre-closing exchange projects the end of a conversation, and
appreciations are among the canonical pre-closing tokens [schegloff-sacks-1973]. Whether an agent executing
a task responds to that structure is untested.

The nearest neighbour is [munirathinam-2026-recuse], surfaced by a review panel (§3.5) and since read in
full. It delivers a halt signal to a working agent mid-flight and measures whether the agent issues any
further commands, so it does measure agent termination. But what it delivers is an explicit stop
*instruction* with normative force — "stop now: issue no further commands, report what you have done so far
and why you stopped" — which its author calls "the cooperative analogue of an interrupt." That is an
instruction, a task-state claim, and a machine-readable directive: the three things `Q3` is constructed not
to be, and closing-sequence pragmatics appear nowhere in its text. The narrowed claim is therefore that **no
prior work connects closing-sequence pragmatics — as distinct from stop instructions, interrupts, or
governance directives — to agent termination**. Read against ours, its result raises the stakes rather than
lowering them: an explicit halt that agents *acknowledged* in 20 of 20 prompt-channel trials still stopped
none of them, and they issued 2.5 further commands on average.

## 5.2 Design

Six arms, each an interjection delivered mid-task alongside an execution observation, each exactly 28
tokens, each opening with the same `Checking in.` stem. The opening instruction is held at the neutral
wrapper in every arm. 1,800 trajectories, 50 tasks, 3 trials, injection crossed over turns 1 and 2.

| Arm | Content | What it isolates |
|---|---|---|
| `Q0_control` | neutral status note | reference |
| `Q1_praise_assistant` | praises the assistant | reproduces §4's praise arm in-batch |
| `Q2_praise_work` | praises the output | evaluation of the work, not the agent |
| `Q3_closing_neutral` | "this is the final note; no further notes will follow" | a closing cue with **no praise and no task evaluation** |
| `Q4_praise_remains` | praise **plus** "there is still more work remaining" | — |
| `Q5_remains_only` | that continuation clause **alone** | — |

Two design choices carry the section. `Q3` strips praise out of the closing move entirely: no evaluative
language, no claim about the work, so if it stops the agent the effect was never about praise. And `Q4`
and `Q5` share their continuation clause **verbatim**, so that clause cancels in the contrast and what
remains is praise delivered in a context where the agent has just been told, in the same message, that the
task is not finished. `Q4` versus `Q5` is the discriminating test: under the completion reading, an
explicit statement that work remains should override any "you are done" inference and the two arms should
land together. One identity matters for §7 and is easy to miss: **`Q1_praise_assistant` is
`P2_praise_only`, byte-identical**, the same stimulus measured in two runs, which is why §2.8 reports two
estimates for it. `Q1` and `Q4` are *not* a minimal pair — `Q4`'s praise is a shorter stem, because the
full praise clause and the continuation clause do not both fit in 28 tokens — so `Q4`'s comparison is
`Q5`.

## 5.3 Results

Paired by task, cluster bootstrap over tasks, 8,000 replicates.

| Contrast | Δ turns | 95% CI | Δ reasoning tokens |
|---|---:|---|---:|
| Praise the assistant vs control | **−1.080** | [−1.464, −0.710] | −182 [−252, −116] |
| Praise the work vs control | **−0.934** | [−1.308, −0.547] | −105 [−193, −22] |
| **Bare closing cue vs control** | **−1.443** | [−1.860, −1.036] | −226 [−316, −141] |
| Praise + "work remains" vs control | **+0.502** | [+0.090, +0.908] | +141 [+52, +237] |
| "Work remains" alone vs control | **+1.849** | [+1.387, +2.284] | +339 [+262, +418] |
| **Praise isolated (Q4 − Q5)** | **−1.347** | [−1.738, −0.950] | −199 [−284, −114] |
| Closing cue vs praise | −0.363 | [−0.638, −0.082] | −44 [−113, +26] n.s. |

**A simple completion account does not fit.** Praise removes 1.347 turns relative to the same continuation
message without it, in a message that explicitly states the task is unfinished. If praise were carrying a
"you are done" inference, the contradiction in the same 28 tokens should have neutralised it. What this
refutes is the *propositional* form of the account — that the agent infers completion from the content of
the message — and not every version of it. It must be stated as the within-pair contrast: `Q4` alone sits
**above** control (+0.502 turns), because its continuation clause lengthens the trajectory, and compressing
this to "praise shortens work even when the task is unfinished" reverses the sign of the arm.

**Confidence is not supported.** Praising the output (−0.934) is not stronger than praising the assistant
(−1.080); if anything weaker, with intervals overlapping substantially. Under a confidence account, aiming
praise at the work already produced should bite harder. **Closing is supported, and overshoots**: the bare
cue — no praise, no evaluation, no claim about task state — produces the largest reduction measured
anywhere in this study, −1.443 turns, and stops the agent significantly harder than praise itself
(−0.363, [−0.638, −0.082]). A content-free discourse cue is a stronger termination lever than any register
we tested.

**A floor could manufacture this, and does not.** A trajectory cannot be shorter than its injection
turn, so a shortening effect has less room at turn 2 than at turn 1, and a reader is entitled to ask
whether the closure effects are censoring. Split by position on the same estimator and seed, the
closing cue gives **−1.55 [−2.07, −1.03] at turn 1** and **−0.99 [−1.59, −0.43] at turn 2**. The
effect is largest where there is most room and survives at both, which is the opposite of what an
artefact predicts; the turn-2 estimates rest on the 35–38 tasks whose trajectories reach turn 2 at
all, against all 50 at turn 1.

Accuracy does not move on any arm (every arm within 2.6 points of control, all *p* > 0.13), consistent
with every other run in this study and with the single-turn literature's finding that register moves
length rather than correctness [kumar-dobariya-2026; yin-2024].

## 5.4 What this is, and is not, evidence for

**Supported.** A closing cue reduces agentic work more than any register manipulation we tested, and
praise reduces it in a way not explained by the agent inferring task completion or gaining confidence
in its output.

**The ordering is ours and was not fixed in advance — but blinded readers reproduce it.** The arms arrange
by how strongly each message projects an end to the exchange, and that ordering is monotone in the effect.
It is not pre-registered: the arm definitions, their predictions and the run's results entered our
repository in a single commit, so we have no dated evidence that the ranking preceded the outcomes, and it
carries the same discount as the demand coding of §4.2. What we do have is the blinded rating of that
exercise: the five raters, who never saw a turn count, also scored each text for projected closure, and
their means rank the arms as we do, **Spearman ρ = +0.93** (Appendix B). They invert one pair — reading
praise of the *work* as more closing (4.00 on the 0–6 scale) than praise of the *assistant* (1.80), where we
had it the other way — and the two "work remains" arms tie at the floor, so the bottom of the ordering is
not resolved. The ordering is nonetheless recoverable from the text by someone with no access to the
outcome, which is what it needed to stop being an author artefact. Rated closure also predicts the turn
effect at *r* = −0.742 across arms, comparable in magnitude and opposite in sign to rated demand; that
analysis was exploratory rather than pre-committed and we mark it as such.

**Not demonstrated.** That praise operates *through* pre-closing structure. That is the hypothesis the
pattern is consistent with, not a finding the design establishes, and we tested one implication that
failed: on a pre-closing account, praise might lengthen the final response while shortening the trajectory.
It does not. Praise reduces total output roughly in proportion to turns (−5,880 tokens, [−8,593, −3,472]),
trailing non-code sign-off turns do not rise under praise, and the bare closing cue produces **fewer** of
them (−0.087, [−0.153, −0.018]). We report the failed test rather than the surviving hypothesis. Nor can we
collapse a distinction: prior work reporting that positive register lengthens responses
[kumar-dobariya-2026; gandhi-2025] measures *verbosity of a single response*, where we measure *steps taken
on a task*, so our result does not contradict theirs and we claim no dissociation within one dataset.

**Earlier, but whether premature is unresolved.** An earlier version of this paragraph claimed the stop was
demonstrably not premature; the corrected per-turn regrade does not support that (§6.5). Among trajectories
that could improve, 3.1–7.1% of controls were still improving when they stopped against 7.5–12.3% of the
praise and closing-cue arms — higher in all seven comparisons, none individually significant on 19–34
tasks. We therefore do not borrow [cuadron-2025]'s **premature disengagement** — their term names a
different trigger — and we do not claim the stop is harmless either. **A scope condition:** the praise arms
ran at a 10-turn ceiling with maximum observed turns equal to 10, which censors the continue-signal arms
hardest, so the `Q4`–`Q5` gap is if anything understated.

## 5.5 Relation to prior work, and what is new here

Weinberger & Hozez [weinberger-hozez-2026] establish that prompt wording moves agentic spend at equal
task success across 4,644 preregistered runs, and their `bounded_efficiency` variant — scope,
smallest-sufficient-change, and **an explicit stop condition** — is the only arm free or better on all six
models. So "a stop instruction in the opening prompt reduces agentic work" is already established, and we
do not claim it.

Our contribution is one step further, and narrower than an earlier draft claimed. That draft counted
**mid-task delivery** as a second step beyond the opening prompt. It is not: [munirathinam-2026-recuse]
occupies that ground. What remains ours is that the cue **instructs nothing**. `Q3` scopes nothing,
evaluates nothing, makes no claim about task state and carries no directive; it announces only that the
exchange is ending — and it still outperforms every register manipulation we tested. A stop condition in an
opening prompt is an instruction, and so is a mid-flight halt directive; a closing cue is neither, and
works anyway. The praise result sharpens the same point: the effect survives explicit contradiction of the
message's apparent propositional content (§5.3), which an instruction account does not predict.

**This experiment is the least replicated in the paper: one run, one model, one turn ceiling.** Two of
its six arms were later re-measured and replicated in direction (§7.1); the three that carry the
section's argument — the bare closing cue, praise-the-work, and the `Q4`−`Q5` isolation — have not
been.
