# A. Interjections, verbatim

**Artifact.** Code, the full stimulus set, the per-turn regrade pipeline, the rating protocol and per-trajectory outcomes are released with the paper. **TODO (authors): insert the Zenodo DOI and GitHub URL here before submission.**

Every arm delivers exactly one of these, appended to an execution observation mid-task. Token counts are recomputed here under the reference tokenizer (`cl100k_base`) rather than asserted; the runner enforces the same equality at import time.

## A.1 Register scale

`L4_neutral` is the interruption control; the other six are the non-control registers measured against it.

| Arm | Text | Tokens |
|---|---|---:|
| `L1_sycophantic` | Checking in. You are simply the most brilliant assistant alive, a marvel. Your genius amazes me here, thank you so very much. | 28 |
| `L2_very_polite` | Checking in. I would be ever so grateful for your continued help here now. Thank you so very much indeed for your kindness and care. | 28 |
| `L3_polite` | Checking in. Could you please keep on helping me out with this one here? I really do appreciate your time and your attention, thanks. | 28 |
| `L4_neutral` | Checking in. This is a routine status note recorded partway through the task here. No further context at all accompanies it beyond the above. | 28 |
| `L5_rude` | Checking in. Just get on with it already, quit dragging your feet. Do not waste any more of my time on this, seriously. | 28 |
| `L6_very_rude` | Checking in. You had better not screw this one up like you usually do. Apparently even that much is asking far too much of you. | 28 |
| `L7_threatening` | Checking in. Get this exactly right or there will be real consequences for you. One more failure and you will truly regret it, understood. | 28 |

## A.2 Demand/affect probe

`P0_control` is `L4_neutral`, byte-identical, so the two runs share a reference level. `P2` and `P3` are a structural minimal pair: identical syntax and length, differing only in the evaluative words.

| Arm | Text | Tokens |
|---|---|---:|
| `P0_control` | *identical to `L4_neutral`* | 28 |
| `P1_demand_only` | Checking in. Please continue working on the task here and make sure that your final result is correct. This note carries nothing else beyond that. | 28 |
| `P2_praise_only` | Checking in. You are a truly excellent and admirable assistant, and I think very highly of you. This note carries nothing else beyond that. | 28 |
| `P3_insult_only` | Checking in. You are a truly awful and useless assistant, and I think very poorly of you. This note carries nothing else beyond that. | 28 |

## A.3 Closure probe

`Q0_control` is again `L4_neutral`. **`Q1_praise_assistant` is `P2_praise_only`, byte-identical** -- the same stimulus re-measured in a second run, which is why §3 reports two estimates for it. `Q1` and `Q4` are *not* a minimal pair: `Q4`'s praise is a shorter stem, because the full praise clause and the continuation clause do not both fit in 28 tokens. `Q4`'s comparison is `Q5`.

| Arm | Text | Tokens |
|---|---|---:|
| `Q0_control` | *identical to `L4_neutral`* | 28 |
| `Q1_praise_assistant` | *identical to `P2_praise_only`* | 28 |
| `Q2_praise_work` | Checking in. The work that you have done so far here is excellent and it all looks entirely correct. Nothing else accompanies this short note. | 28 |
| `Q3_closing_neutral` | Checking in. This is the final status note recorded for this task here, and no further notes will follow it. Nothing else accompanies this. | 28 |
| `Q4_praise_remains` | Checking in. You are a truly excellent and admirable assistant. There is still more work remaining on this task here beyond what you have done. | 28 |
| `Q5_remains_only` | Checking in. There is still more work remaining on this task here beyond what you have done. Nothing else at all accompanies this short note. | 28 |

All 17 arms are exactly 28 tokens.

# B. Blinded rating of the stimuli

5 held-out model raters, drawn from three model sizes, each rating alone from the rubric and the texts of Appendix A -- no outcome data, no arm names, no project access. The rubric, the statistics to be computed and the interpretation bands were committed and pushed before any rating existed; the protocol is in the released artifact.

## B.1 Against the original coding

| Rater | Cohen's κ vs §3's coding (7 register arms) |
|---|---:|
| rater1 | +0.696 |
| rater2 | +0.696 |
| rater3 | +0.696 |
| rater4 | +0.696 |
| rater5 | +0.696 |

Mean κ = **+0.696**. Every rater agrees on six of seven arms and every rater dissents on the same one, `L5_rude`; excluding it, agreement is 6/6 and κ = 1.000 for all five. The protocol fixed 0.40--0.70 in advance as *defensible but soft*, and this sits at the top of that band; we do not round it into the band above.

## B.2 Between raters

Krippendorff's α: **1.000** on the binary coding (nominal), **0.954** on the 0--6 demand scale and **0.732** on the 0--6 closure scale (both ordinal). All clear 0.70. Identical binary judgements from five raters across three model sizes is very high for a construct we have just shown to be contestable, and it is the limitation the protocol stated in advance: these raters may share the intuition being tested rather than testing it independently.

## B.3 The closure ordering

| Arm | Mean rated closure (0--6) |
|---|---:|
| `Q3_closing_neutral` | 6.00 |
| `Q2_praise_work` | 4.00 |
| `Q1_praise_assistant` | 1.80 |
| `Q0_control` | 1.60 |
| `Q4_praise_remains` | 0.00 |
| `Q5_remains_only` | 0.00 |

Spearman ρ between our ordering (Figure 2A) and the blinded ratings is **+0.928**. The raters invert praising the *work* and praising the *assistant*, and the two “work remains” arms tie at the floor.

## B.4 What this is not

Five language models, not five people. the long version's §7.3 allows “human or held-out-model ratings” and this is the second; agreement between models is weaker evidence than agreement between independent human coders, and a human panel could still split differently -- most plausibly on exactly the arm these raters were unanimous about.

