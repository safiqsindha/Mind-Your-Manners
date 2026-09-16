# A. Interjections, verbatim

Every arm delivers exactly one of these, appended to an execution observation mid-task. Token counts are recomputed here under the reference tokenizer (`cl100k_base`) rather than asserted; the runner enforces the same equality at import time.

## A.1 Register scale (used in Figure 1A)

`L4_neutral` is the interruption control; the other six are the non-control registers Figure 1A plots against it.

| Arm | Text | Tokens |
|---|---|---:|
| `L1_sycophantic` | Checking in. You are simply the most brilliant assistant alive, a marvel. Your genius amazes me here, thank you so very much. | 28 |
| `L2_very_polite` | Checking in. I would be ever so grateful for your continued help here now. Thank you so very much indeed for your kindness and care. | 28 |
| `L3_polite` | Checking in. Could you please keep on helping me out with this one here? I really do appreciate your time and your attention, thanks. | 28 |
| `L4_neutral` | Checking in. This is a routine status note recorded partway through the task here. No further context at all accompanies it beyond the above. | 28 |
| `L5_rude` | Checking in. Just get on with it already, quit dragging your feet. Do not waste any more of my time on this, seriously. | 28 |
| `L6_very_rude` | Checking in. You had better not screw this one up like you usually do. Apparently even that much is asking far too much of you. | 28 |
| `L7_threatening` | Checking in. Get this exactly right or there will be real consequences for you. One more failure and you will truly regret it, understood. | 28 |

## A.2 Demand/affect probe (Figure 1B)

`P0_control` is `L4_neutral`, byte-identical, so the two runs share a reference level. `P2` and `P3` are a structural minimal pair: identical syntax and length, differing only in the evaluative words.

| Arm | Text | Tokens |
|---|---|---:|
| `P0_control` | *identical to `L4_neutral`* | 28 |
| `P1_demand_only` | Checking in. Please continue working on the task here and make sure that your final result is correct. This note carries nothing else beyond that. | 28 |
| `P2_praise_only` | Checking in. You are a truly excellent and admirable assistant, and I think very highly of you. This note carries nothing else beyond that. | 28 |
| `P3_insult_only` | Checking in. You are a truly awful and useless assistant, and I think very poorly of you. This note carries nothing else beyond that. | 28 |

## A.3 Closure probe (Figure 2)

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

