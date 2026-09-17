# 4. Praise behaves as a closing move

That praise shortens the trajectory needs its own explanation, and three compete: praise is read
as evidence the task is **finished**; praise raises the agent's **confidence** in work already
produced; or praise is a conversational **closing** move, and the agent is responding to discourse
structure rather than to any claim about task state. Six arms separate them (Figure 2).

Praise still removes **1.35 turns** relative to the identical message without it *even when that
message states the task is unfinished* (*p* < 0.0001), which is inconsistent with a simple
propositional completion account: the text explicitly denies completion and the praise acts
anyway. Praising the *work* is no stronger than praising the *assistant* (−0.93 against −1.08),
which does not support a confidence account. And a bare closing cue carrying no praise, no
evaluation and no task-state claim — "this is the final status note recorded for this task here,
and no further notes will follow it" — produces the largest reduction we measured, **−1.44 turns**.

**A floor could manufacture this, and does not.** A trajectory cannot be shorter than its
injection turn, so a shortening effect has less room at turn 2 than at turn 1. Split by position,
the closing cue gives **−1.55 [−2.07, −1.03] at turn 1** and −0.99 [−1.59, −0.43] at turn 2
(`results/analysis/injection_position.py`). The
effect is largest where there is most room and survives at both, so it is not an artefact of the
floor; the turn-2 estimates also rest on the 35–38 tasks whose trajectories reach turn 2 at all,
against all 50 at turn 1.

**The ordering is ours and was not fixed in advance — but blinded readers reproduce it.** Figure
2A arranges the arms by how strongly each message projects an end to the exchange, and that
ordering is monotone in the effect. The arm definitions, their predictions and the run's results
entered our repository in a single commit, so we have no dated evidence that the ranking preceded
the outcomes. What we do have is the blinded rating of §3: five raters who never saw a turn count
scored each text for projected closure, and their mean ranks the arms as Figure 2A does, Spearman
ρ = +0.93. They invert one pair — they read praising the *work* as more closing than praising the
*assistant*, where we had it the other way — and the two "work remains" arms tie at the floor. The
ordering is therefore recoverable from the text by someone with no access to the outcome, which is
what it needed to stop being an author artefact.

Closing sequences are a well-described conversational object, and appreciations are among the
canonical pre-closing tokens [schegloff-sacks-1973]; that praise operates *through* that structure
is the hypothesis this is consistent with, not one the design establishes.

**What is new here against the nearest prior work.** A mid-flight halt signal has been delivered to
a working agent before, and whether it stops has been measured [munirathinam-2026-recuse] — but
that signal is an explicit stop instruction with normative force, and closing-sequence pragmatics
appear nowhere in it. Prior work shows that explicit mid-flight halt instructions need not stop an
agent; our distinct question is whether ordinary conversational closing structure can alter
termination without instructing the agent to stop. Read against ours it raises the stakes: an explicit halt
that agents acknowledged in 20 of 20 trials stopped none of them, while a note issuing no
instruction removed 1.44 turns. **This experiment — the six-arm closure study of this section — is
the least replicated in the paper: one run, one model, one turn ceiling.**
