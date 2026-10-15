# 4. Praise and closing cues shorten the trajectory

Three accounts compete for why praise shortens the trajectory: praise is read as evidence the task
is **finished**; it raises the agent's **confidence** in work already produced; or it is a
conversational **closing** move. We designed six arms to separate them (Figure 2). They narrow the
field less than we hoped.

**Praise acts even when the message denies completion.** It removes **1.35 turns** relative to the
same "work remains" message without it (`Q4` − `Q5`, *p* < 0.0001), which argues against a simple
completion account. But `Q4` and `Q5` are not a strict minimal pair (praise replaces a filler
sentence; Appendix A.3), and blinded raters score both at 0 on projected closure, so this contrast
does not support the closing account either. Against control, `Q4` (+0.50) sits near the sum of
praise alone and "work remains" alone (−1.08 + 1.85 = +0.77), as if two opposing signals were
weighed.

**Confidence is not cleanly tested.** Praising the *work* is not measurably stronger than praising
the *assistant* (difference +0.15, [−0.18, +0.48]), but the work-praise arm also says the work
"looks entirely correct", a claim the other lacks.

**A closing cue produces the largest reduction we measured.** "This is the final status note
recorded for this task here, and no further notes will follow it" carries no praise or evaluation
and removes **1.44 turns**. Its control describes itself as recorded "partway through the task",
so the contrast is final against partway, not closing against nothing.

**A floor could manufacture this, and does not.** A trajectory cannot be shorter than its injection
turn, so shortening has less room at turn 2. The closing cue gives **−1.55 [−2.07, −1.03] at turn
1** and −0.99 [−1.59, −0.43] at turn 2, on the 35 tasks reaching turn 2 in both arms; turn 1
restricted to those tasks gives −1.49 [−2.12, −0.87], so the difference is not task survivorship
(Appendix C.4).

**The ordering is ours and post hoc, but blinded readers reproduce it.** Figure 2A orders arms by
how strongly each projects an end to the exchange, and that ordering is monotone in the effect. The
arms, predictions and results entered our repository in one commit, so nothing dates the ranking
before the outcomes. The blinded raters, who saw no turn counts, rank the six arms (control
included) the same way, ρ = +0.928, inverting only work- and assistant-praise.

Appreciations are canonical pre-closing tokens [schegloff-sacks-1973], and the closing cue's effect
is consistent with an agent responding to closing structure. We do not claim it as the mechanism:
praise shortens `Q4` without being read as closing, and three register arms end in thanks while
only one shortens.

**Against the nearest prior work.** Prompt wording is known to move agentic spend at equal success,
with an explicit stop condition the one consistently cheap variant [weinberger-hozez-2026]. Explicit mid-flight halts have been measured as an immediate stop
[munirathinam-2026-recuse]: in the prompt channel, acknowledged in 20 of 20 trials and obeyed in
none; in-band with tool output, neither. Our outcome, a shift in mean trajectory length, is not
directly comparable; what ours adds is that a note issuing no instruction moved termination at all.
**This six-arm study is the least replicated in the paper: one run, one model, one budget**; given
§5's drift, differences under half a turn, such as closing cue against praise (−0.36), may not
replicate.
