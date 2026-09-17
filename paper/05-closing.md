# 5. Finding 2: praise and closing cues shorten trajectories

## 5.1 The question, and the design

Section 4 leaves one arm unexplained: **praise, carrying no demand at all, shortens the
trajectory**. Three readings survive. Under **completion**, praise is read as evidence the task is
finished. Under **confidence**, praise raises the agent's estimate of work already produced so it
stops checking. Under **closing**, praise is a conversational closing move and the agent is
responding to discourse structure rather than to any claim about task state — a pre-closing exchange
projects the end of a conversation, and appreciations are among the canonical pre-closing tokens
[schegloff-sacks-1973].

Six arms, each an interjection delivered mid-task alongside an execution observation, each exactly
28 tokens, each opening with the same `Checking in.` stem. 1,800 trajectories, 50 tasks, 3 trials,
injection crossed over turns 1 and 2.

| Arm | Content | What it isolates |
|---|---|---|
| `Q0_control` | neutral status note | reference |
| `Q1_praise_assistant` | praises the assistant | reproduces §4's praise arm in-batch |
| `Q2_praise_work` | praises the output | evaluation of the work, not the agent |
| `Q3_closing_neutral` | "this is the final note; no further notes will follow" | a closing cue with **no praise and no task evaluation** |
| `Q4_praise_remains` | praise **plus** "there is still more work remaining" | — |
| `Q5_remains_only` | that continuation clause **alone** | — |

Two design choices carry the section. `Q3` strips praise out of the closing move entirely — no
evaluative language, no claim about the work — so if it stops the agent the effect was never about
praise. And `Q4` and `Q5` share their continuation clause **verbatim**, so that clause cancels in
the contrast and what remains is praise delivered where the agent has just been told, in the same
message, that the task is not finished; under the completion reading the two arms should land
together. Two identities are easy to miss: **`Q1_praise_assistant` is `P2_praise_only`,
byte-identical**, the same stimulus measured in two runs (Appendix C.1); and `Q1` and `Q4` are *not*
a minimal pair, because `Q4`'s praise is a shorter stem, so `Q4`'s comparison is `Q5`.

## 5.2 Results

Paired by task, cluster bootstrap over tasks, 20,000 resamples (§2.3).

| Contrast | Δ turns | 95% CI | Δ reasoning tokens |
|---|---:|---|---:|
| Praise the assistant vs control | **−1.080** | [−1.466, −0.714] | −182 [−251, −115] |
| Praise the work vs control | **−0.934** | [−1.314, −0.545] | −105 [−192, −24] |
| **Bare closing cue vs control** | **−1.443** | [−1.867, −1.042] | −226 [−316, −142] |
| Praise + "work remains" vs control | **+0.502** | [+0.095, +0.903] | +141 [+53, +234] |
| "Work remains" alone vs control | **+1.849** | [+1.387, +2.286] | +339 [+264, +417] |
| **Praise isolated (Q4 − Q5)** | **−1.347** | [−1.740, −0.956] | −199 [−284, −114] |
| Closing cue vs praise | −0.363 | [−0.643, −0.081] | −44 [−113, +24] n.s. |

**A simple completion account does not fit.** Praise removes 1.347 turns relative to the same
continuation message without it, in a message that explicitly states the task is unfinished. If
praise were carrying a "you are done" inference, the contradiction in the same 28 tokens should have
neutralised it. What this refutes is the *propositional* form of the account. It must be stated as
the within-pair contrast: `Q4` alone sits **above** control (+0.502 turns), because its continuation
clause lengthens the trajectory, so compressing this to "praise shortens work even when the task is
unfinished" reverses the sign of the arm.

**Confidence is not supported.** Praising the output (−0.934) is not stronger than praising the
assistant (−1.080); if anything weaker, with intervals overlapping substantially, where a confidence
account predicts praise aimed at the work should bite harder. **Closing is supported, and
overshoots**: the bare cue — no praise, no evaluation, no claim about task state — produces the
largest reduction measured anywhere in this study, −1.443 turns, and stops the agent significantly
harder than praise itself (−0.363, [−0.643, −0.081]). A content-free discourse cue is a stronger
termination lever than any register we tested.

**A floor could manufacture this, and does not.** A trajectory cannot be shorter than its injection
turn, so a shortening effect has less room at turn 2 than at turn 1. Split by position, the closing
cue gives **−1.55 [−2.07, −1.03] at turn 1** and **−0.99 [−1.59, −0.43] at turn 2**: largest where
there is most room, and surviving at both, which is the opposite of what an artefact predicts. The turn-2 estimates rest on the 35–38 tasks
whose trajectories reach turn 2 at all, against all 50 at turn 1. Accuracy does not move on any arm (every arm within 2.6 points of control, all *p* > 0.13).

## 5.3 What this is, and is not, evidence for

A closing cue reduces agentic work more than any register manipulation we tested, and praise reduces
it in a way not explained by the agent inferring task completion or gaining confidence in its
output.

**The ordering is ours and was not fixed in advance — but blinded readers reproduce it.** The arms
arrange by how strongly each message projects an end to the exchange, and that ordering is monotone
in the effect. It was not pre-registered, and carries the same discount as the demand coding of
§4.2. What we do have is the blinded rating: the five raters, who never saw a turn count, also
scored each text for projected closure, and their means rank the arms as we do, **Spearman
ρ = +0.93** (Appendix B). They invert one pair — reading praise of the *work* as more closing (4.00
on the 0–6 scale) than praise of the *assistant* (1.80) — and the two "work remains" arms tie at the
floor, so the bottom of the ordering is not resolved.

**Not demonstrated.** That praise operates *through* pre-closing structure. We tested one
implication that failed: on a pre-closing account, praise might lengthen the final response while
shortening the trajectory. It does not. Praise reduces total output roughly in proportion to turns
(−5,880 tokens, [−8,593, −3,472]), trailing non-code sign-off turns do not rise under praise, and
the bare closing cue produces **fewer** of them (−0.087, [−0.153, −0.018]). Nor can we collapse a
distinction: prior work reporting that positive register lengthens responses
[kumar-dobariya-2026; gandhi-2025] measures *verbosity of a single response*, where we measure
*steps taken on a task*.

**Earlier, but whether premature is unresolved.** Among trajectories that could improve, 3.1–7.1% of
controls were still improving when they stopped against 7.5–12.3% of the praise and closing-cue arms
— higher in all seven comparisons, none individually significant on 19–34 tasks. We therefore do not
borrow [cuadron-2025]'s **premature disengagement**, and we do not claim the stop is harmless
either. The praise arms ran at a 10-turn ceiling with maximum observed turns equal to 10, which
censors the continue-signal arms hardest, so the `Q4`–`Q5` gap is if anything understated.

**What is new here, and what is not.** Weinberger & Hozez [weinberger-hozez-2026] establish that
prompt wording moves agentic spend at equal task success across 4,644 preregistered runs, and their
`bounded_efficiency` variant — scope, smallest-sufficient-change, and **an explicit stop condition**
— is the only arm free or better on all six models. So "a stop instruction in the opening prompt
reduces agentic work" is already established, and we do not claim it. Mid-task delivery is not ours
either: [munirathinam-2026-recuse] delivers an explicit halt directive to a working agent mid-flight
and measures whether it issues further commands — and an explicit halt that agents *acknowledged* in
20 of 20 prompt-channel trials stopped none of them, which raises the stakes on ours rather than
lowering them. What remains ours is that the cue **instructs nothing**: `Q3` scopes nothing,
evaluates nothing, makes no claim about task state and carries no directive, and it still
outperforms every register manipulation we tested. The narrowed novelty claim is that no prior work
connects closing-sequence pragmatics — as distinct from stop instructions, interrupts, or governance
directives — to agent termination.

**This experiment is the least replicated in the paper: one run, one model, one turn ceiling.** Two
of its six arms were later re-measured and replicated in direction (Appendix C.1); the three that
carry the section's argument — the bare closing cue, praise-the-work, and the `Q4`−`Q5` isolation —
have not been.
