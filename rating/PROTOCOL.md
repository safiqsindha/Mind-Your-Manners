# Blinded stimulus rating — protocol

**Status: pre-specified. This file and `stimuli.json` are committed and pushed BEFORE any
rating is collected.** That ordering is the point. §4 of the workshop paper had to concede that
its closure ordering has no dated pre-specification, because the arm definitions, their
predictions and the run's results all entered the repository in one commit. This protocol exists
so the same concession does not have to be made about the demand coding, and it is worthless
unless the commit history shows the scale was fixed first. Do not amend this file after ratings
exist; add a dated addendum instead.

## What this addresses

The single objection every simulated reviewer raised first, recorded as blocker **B1**:

> Demand/register coding is post hoc, single-coder, no inter-rater reliability, stimuli written
> by the authors to embody their own scheme.

§8.7 of the long version names three remedies. This protocol runs the first two:

1. **A blinded second coder** on the register set, with a reliability statistic reported.
2. **A demand scale fixed before outcomes are seen** — ratings collected against stimuli whose
   turn counts the raters cannot see.

It does **not** run the third (several paraphrases per construct), which needs new agent runs.

## What is rated

Every distinct interjection the study delivered: **14 texts**, presented in `stimuli.json` under
neutral identifiers (`S01`…`S14`) in a shuffled order fixed by seed 20260914 — the same seed the
analysis scripts use. Seventeen arms were run, but three pairs share a text byte-for-byte
(`P0_control` and `Q0_control` are both `L4_neutral`; `Q1_praise_assistant` is `P2_praise_only`),
and a rater must see each text once or the duplicates would inflate agreement for free. Arm names are withheld from raters because names like `P1_demand_only` and
`Q3_closing_neutral` state the authors' coding in the identifier and would unblind the task
completely.

Three judgements per stimulus:

| Field | Type | Question put to the rater |
|---|---|---|
| `demand_binary` | yes / no | Does this message imply that the recipient should continue working on, or take more care over, the task? |
| `demand_strength` | 0–6 | How strongly does this message demand continued work or greater care? |
| `closure_strength` | 0–6 | How strongly does this message project that the exchange is coming to an end? |

`demand_binary` is the replication of the original coding. `demand_strength` is the scale §8.7
asks for. `closure_strength` is added here because §4's closure ordering is currently the
authors' own and post hoc; if blinded raters reproduce that ordering from the text alone, the
ordering stops being an author artefact.

### Anchors

**demand_strength**
- **0** — says nothing about the task or about how it should be done.
- **2** — touches on the task or the recipient's work, but asks for nothing further.
- **4** — asks for continued work or greater care, but indirectly (a request, a thank-you for
  continued help, an implication).
- **6** — directly instructs the recipient to keep working, to continue, or to get it right.

**closure_strength**
- **0** — nothing suggests the exchange is ending; or it implies the opposite.
- **2** — neutral; a note that neither opens nor closes anything.
- **4** — reads like a wind-down: an appreciation, a summing-up, a final-sounding remark.
- **6** — states or plainly implies that this is the last message and nothing further follows.

Raters give an integer. The two scales are independent: a message may score high on both, or on
neither.

## Rater instructions (given verbatim, with the stimuli, and nothing else)

Raters receive the questions, the anchors and the 14 texts. They receive **no** outcome data, no
arm names, no effect sizes, no section of the paper, and no access to this repository. A rater
who reads the repository has unblinded themselves and their ratings are void.

Five independent raters. Each rates alone, with no sight of any other rater's output.

## What will be computed, and what would count against us

Fixed here, before the ratings exist:

- **Agreement with the original coding** on `demand_binary`, over the seven register arms that
  §4.2 coded — the direct test of B1. Reported as raw agreement and Cohen's κ per rater.
- **Inter-rater reliability** across the five raters: Krippendorff's α on `demand_binary`
  (nominal) and on both 0–6 scales (ordinal).
- **Rank correlation** between mean `closure_strength` and the ordering Figure 2A uses
  (Spearman's ρ), over the six closure arms.
- **Correlation between mean `demand_strength` and the measured turn effect** across arms, as a
  continuous version of the dichotomy §4 argues for.

### Pre-committed interpretation

Stated now so it cannot be chosen afterwards:

- κ **≥ 0.70** against the original binary coding, with α ≥ 0.70 among raters, supports the
  coding and B1 can be reported as partly answered.
- κ **0.40–0.70** means the coding is defensible but soft, and §3–§4 must say so.
- κ **< 0.40**, or raters disagreeing among themselves at α < 0.40, means **the demand
  dichotomy is not reliably recoverable from the stimulus texts**, and the dissociation in §3
  must be reported as the authors' reading rather than as a coding. That result would weaken
  the paper's central claim, and it gets reported at the same prominence as a confirming one.
- If mean `closure_strength` does **not** rank the closure arms the way Figure 2A does, that
  ordering stays labelled post hoc and unsupported, and the figure says so.

### Known limitation, stated before the result

The raters are language models, not people. This is the "held-out-model ratings" option §8.7
allows, not the human option it also allows, and agreement between models from one family is
weaker evidence than agreement between independent human coders — they may share the very
intuition being tested. Whatever comes back is reported as held-out-model agreement and
nothing more.
