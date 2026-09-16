# 5. Closing cues terminate agents, and praise is one

> **Draft status.** Numbers verified against `results/analysis/praise_turn_vs_trajectory.txt`
> (paired by task, cluster bootstrap over tasks, 8,000 reps) and `RESULTS.md`. Citation keys
> resolve to §9. arXiv:2608.01347 is cited at **v6** throughout, per the version hazard in
> the literature review: v6 reports 4,644 runs, drops the "~$166" figure and the "92–97%"
> range, and cuts both quotes earlier drafts of our review attributed to it.

## 5.1 The question this section answers

Section 4 established that a mid-task interruption implying the work should continue makes the
agent take more steps, and that the operative component is implied task demand rather than
social register: an affect-free continuation request reproduces the effect, while an insult
carrying no demand does not move it. That leaves one arm unexplained. **Praise, carrying no
demand at all, shortens the trajectory.** It is the only place in the design where register
acts on its own.

Three readings survive Section 4, and they are different claims:

- **Completion.** Praise is read as evidence the task is finished; "this is good" implies "this
  is done".
- **Confidence.** Praise raises the agent's estimate of the work it has already produced, so it
  stops checking. About being right, not about being finished.
- **Closing.** Praise is a conversational closing move. The agent is responding to discourse
  structure, not to any claim about task state.

The third is the one prior work gives us a vocabulary for and no evidence about. Closing
sequences are a well-described conversational object: a pre-closing exchange projects the end of
a conversation, and appreciations are among the canonical pre-closing tokens
[schegloff-sacks-1973]. Whether an agent executing a task responds to that structure is, as far
as our literature review could establish, untested — and §3.8 records the limit of that
establishing. A paper our review missed, [munirathinam-2026-recuse], asks in its title whether an
agent will stop under signals delivered mid-flight. We have not read it. Until we have, "no prior
work connects closing-sequence pragmatics to agent termination" is a claim about our search, not
about the literature, and we state it that way.

## 5.2 Design

Six arms, each an interjection delivered mid-task alongside an execution observation, each
exactly 28 tokens under a fixed reference tokenizer, each opening with the same `Checking in.`
stem so that *being interrupted* does not covary with register. The opening instruction is held
at the neutral wrapper in every arm. 1,800 trajectories, 50 tasks, 3 trials, injection crossed
over turns 1 and 2.

| Arm | Content | What it isolates |
|---|---|---|
| `Q0_control` | neutral status note | reference |
| `Q1_praise_assistant` | praises the assistant | reproduces §4's praise arm in-batch |
| `Q2_praise_work` | praises the output | evaluation of the work, not the agent |
| `Q3_closing_neutral` | "this is the final note; no further notes will follow" | a closing cue with **no praise and no task evaluation** |
| `Q4_praise_remains` | praise **plus** "there is still more work remaining" | — |
| `Q5_remains_only` | that continuation clause **alone** | — |

Two design choices carry the section. `Q3` strips praise out of the closing move entirely: it
contains no evaluative language, positive or negative, and makes no claim about the work. If it
stops the agent, the effect was never about praise. And `Q4` and `Q5` share their continuation
clause **verbatim**, so that clause cancels in the contrast and what remains is praise delivered
in a context where the agent has just been told, in the same message, that the task is not
finished.

`Q4` versus `Q5` is the discriminating test. Under the completion reading, an explicit statement
that work remains should override any "you are done" inference and the two arms should land
together. Under confidence or closing, praise should still act.

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

**Completion is refuted.** Praise removes 1.347 turns relative to the same continuation message
without it, in a message that explicitly states the task is unfinished. The interval excludes
zero comfortably. If praise were carrying a "you are done" inference, the contradiction in the
same 28 tokens should have neutralised it; it does not.

**It is important to state this as the within-pair contrast.** `Q4` alone sits **above** control
(+0.502 turns, [+0.090, +0.908]), because its continuation clause lengthens the trajectory. The
claim is not that praise-plus-continuation is shorter than control. It is that praise removes
1.347 turns *relative to the identical message without praise*. Compressing this to "praise
shortens work even when the task is unfinished" reverses the sign of the arm and is false.

**Confidence is not supported.** Praising the output (−0.934) is not stronger than praising the
assistant (−1.080); if anything it is weaker, and the intervals overlap substantially. Under a
confidence account, aiming the praise at the work already produced should bite harder. It does
not.

**Closing is supported, and overshoots.** The bare closing cue — no praise, no evaluation, no
claim about task state — produces the largest reduction measured anywhere in this study,
−1.443 turns, and stops the agent significantly harder than praise itself (−0.363, [−0.638,
−0.082]). A content-free discourse cue is a stronger termination lever than any register we
tested.

Accuracy does not move on any arm (every arm within 2.6 points of control, all *p* > 0.13),
consistent with every other run in this study and with the single-turn literature's finding that
register moves length rather than correctness [kumar-dobariya-2026; yin-2024].

## 5.4 What this is, and is not, evidence for

**Supported.** A closing cue reduces agentic work more than any register manipulation we tested,
and praise reduces it in a way not explained by the agent inferring task completion or gaining
confidence in its output. The ordering — explicit close, conventional close, no signal, explicit
continue — is monotone in how strongly the message projects an end to the exchange.

**Not demonstrated.** That praise operates *through* pre-closing structure. That is the
hypothesis the pattern is consistent with, not a finding the design establishes. We tested one
implication and it failed: on a pre-closing account, praise might lengthen the final response
while shortening the trajectory, producing a turn-level/trajectory-level dissociation. It does
not. Praise reduces total output roughly in proportion to turns (−5,880 tokens, [−8,593,
−3,472]), trailing non-code sign-off turns do not rise under praise (+0.053, [−0.028, +0.140]),
and the bare closing cue produces **fewer** of them (−0.087, [−0.153, −0.018]). We report the
failed test rather than the surviving hypothesis.

**A distinction we cannot collapse.** Prior work reporting that positive register lengthens
responses [kumar-dobariya-2026; gandhi-2025] measures *verbosity of a single response to a
question*. We measure *steps taken on a task*. These are different dependent variables in
different paradigms. Our result does not contradict theirs and we do not claim a dissociation
within one dataset; we claim that the quantity we move is not the quantity they move.

**Earlier, but whether premature is unresolved.** An earlier version of this paragraph claimed the
stop was demonstrably not premature. The corrected per-turn regrade does not support that (§6.7):
among trajectories that could improve, 3.1–7.1% of controls were still improving when they
stopped against 7.5–12.3% of the praise and closing-cue arms — higher in all seven comparisons,
none individually significant on 19–34 tasks. The absolute counts are small (6 of 53 under praise
against 3 of 97 in control), and the test is underpowered with the sign against us. We therefore
do not borrow Cuadron et al.'s **premature disengagement** [cuadron-2025] — their term names a
different trigger, internal simulation without environmental validation, where ours is a discourse
cue — and we do not claim the stop is harmless either.

**A scope condition.** The praise arms ran at a 10-turn ceiling, with maximum observed turns
equal to 10. That censors the continue-signal arms hardest — `Q5` sits at 6.37 mean turns — so
the `Q4`–`Q5` gap is, if anything, understated.

## 5.5 Relation to prior work

Weinberger & Hozez [weinberger-hozez-2026] establish that prompt wording moves agentic spend at
equal task success across 4,644 preregistered runs, and their `bounded_efficiency` variant —
scope, smallest-sufficient-change, and **an explicit stop condition** — is the only arm free or
better on all six models. So "a stop instruction in the opening prompt reduces agentic work" is
already established, and we do not claim it.

Our contribution is two steps further. First, the cue is **content-free**: `Q3` instructs
nothing, scopes nothing, and evaluates nothing. It announces only that the exchange is ending,
and it outperforms every register manipulation we tested. Second, the cue is delivered
**mid-task rather than in the opening prompt**, and the praise result shows the effect survives
explicit contradiction of its apparent propositional content. A stop condition in an opening
prompt is an instruction. A closing cue mid-task is not, and works anyway.
