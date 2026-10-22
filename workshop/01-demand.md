# 3. Demand, not register

Across six non-control registers — each measured against the interruption control `L4_neutral` —
the cost curve looks like a politeness gradient. It is not one. Coding each arm by whether its text
instructs the model to persist or to be correct splits it: the four arms we code as carrying a
demand span +0.70 to +1.80 turns and the two we code as carrying none span −0.68 to +0.09, **with
no overlap in point estimates**, and register does not sort them. Polite and hostile arms sit on
both sides: *very polite* (+0.70) sits with *very rude* (+0.71), *sycophantic* (−0.68) with *rude*
(+0.09). Figure 1A. The separation is in point estimates, not intervals — *very polite*
[+0.23, +1.18] and *rude* [−0.30, +0.48] overlap — so the data support an ordering, not a gap. Pooling turn 0 as well attenuates *very rude* to +0.32
(*p* = 0.12; Appendix C.2), leaving *threatening* the only hostile arm significant at every position.

To test the split rather than assert it, we wrote three interjections that vary demand and affect
separately, matching length and opening stem across all four arms; the praise and insult arms
also share syntax, while the demand arm does not (Figure 1B). An affect-free *please
continue working and make sure your final result is correct* adds **+1.17 turns** (*p* < 0.0001).
*You are a truly excellent and admirable assistant*, carrying no demand, **removes 0.59**
(*p* = 0.0003). Its structural minimal pair, with *awful and useless* in place of *excellent and
admirable*, does nothing measurable (−0.08, *p* = 0.62); the direct contrast of the pair, free of the
control's wording, is −0.50 [−0.84, −0.18] (*p* = 0.004). That interval, [−0.40, +0.24] at the ten-turn budget, excludes a
lengthening of a quarter turn (6% of the 4.2-turn control mean) but not a shortening of up to 0.40
turns (10%): a bounded null in the lengthening direction. The bound holds at ten turns and
on GLM at twenty (+0.07 [−0.27, +0.39]) but not on Luna at twenty, where the estimate is +0.57
[−0.22, +1.36]. On GLM the direction replicates for demand alone: +17.7% of its control
(*p* = 0.0030); praise is −11.2% (*p* = 0.058) and insult +2.4% (*p* = 0.66), neither surviving
correction.

**The caveat belongs here.** "Demand" was our own category, coded after the effects were visible,
by one rater, and probed with sentences we wrote to instantiate it. The demand probe states a
continuation and a verification instruction outright, whereas the register arms carry demand
indirectly, through requests or challenges, so the probe tests explicit demand. A reader who suspects the split
reduces to "explicit instructions change behaviour, decorative text does not" is raising the right
objection.

**A blinded check half holds** (Appendix B, C.5). Five held-out model raters (instances of one model family at three sizes) coded the fourteen
distinct texts for implied demand, with no outcome data or arm names, against a rubric committed
before any rating existed. They agree with our coding on six of seven register arms and disagree,
unanimously, on *rude*. We read "just get on with it already" as a demand for speed, not
persistence — in an agent loop, if anything an argument for fewer turns. The rubric asked about
"continued work or greater care" without separating the two, and every rater gave it maximum
strength. κ = 0.696, the top of the band our protocol fixed in advance as *defensible but soft*.

That is the boundary arm. Under the raters' coding the demand group spans +0.09 to +1.80, the
no-demand group is one arm, and a text tied for the highest demand rating moved the agent least. The
continuous form fares better: across the thirteen non-control texts (the neutral control has no
effect to correlate), mean rated demand correlates with the turn effect at *r* = +0.72
(*n* = 13, *p* = 0.006 treating the texts as independent), +0.79 without *rude* (*n* = 12), though the effects come from three runs
and inherit the drift of §5. Among the six register arms alone it is *r* = +0.56 (*p* = 0.24), and the
texts fall into a low-demand cluster (rated 0–1.6, four of five shortening) and a high-demand one
(4.0–6.0), so it reflects that separation more than a dose–response among demanding texts (*r* = −0.29
within the eight rated 4.0 or more). The duplicated praise text enters with its probe-run estimate;
with the closure run's, *r* = +0.74. **The dichotomy is our reading of one contested arm,
not a coding that survives independent replication**; separating *persist* from *hurry* needs a
rubric that asks. Several paraphrases per construct would be the stronger remedy, and
[zhang-2026-politejudge] shows why: for five of eight judge models, within-level wording variation
exceeds between-level tone variation.

*Sycophantic* (−0.68) resists the split: it carries no demand yet shortens, like the praise and
closure arms. The data fit three groups as well as two: **demand lengthens, neutral register does
nothing, and praise-like or closing-like language shortens.**
