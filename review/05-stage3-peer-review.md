# Stage 3 — Workshop committee meta-review

Date: 2026-09-16
Panel: four independent reviewers, NATO codenames, run as separate `claude -p` subprocesses
against a scratch copy of the paper. One slot was filled by the **Alignment-Forum critic** —
that was `charlie` (identifiable by its `Belief update` block; the codename mapping is otherwise
not disclosed by the tool).

Individual reviews: `review/peer-review/review_{alfa,bravo,charlie,delta}.md`
Concerns matrix: `review/peer-review/concerns_table.csv`

---

## Verdicts

| Reviewer | Verdict |
|---|---|
| alfa | **Major revision** |
| bravo | **Major revision** |
| charlie *(alignment critic)* | **Major revision** |
| delta | **Major revision** |
| **Consensus** | **Major revision** — unanimous |

No reviewer recommended reject. All four independently praised the self-audit in §7 and the
paper's transparency about its own instability. The disagreement is entirely about whether the
central construct is validated, not about whether the work was done carefully.

---

## Meta-review

The panel converged, without coordination, on one finding: **the demand/register distinction that
organises the entire paper is an author-authored, post-hoc, single-coder construct with no
reliability statistic and no independent validation.** All four reviewers raised it, and three
made it their first or second concern.

The sharpest statement of it is delta's: if "demand" is operationalised as literally imperative
continuation language and "register" as evaluative adjectives with no instruction content, then
the finding that the former moves behaviour and the latter does not is *close to tautological* —
"explicit instructions change behaviour, decorative text does not" is a much weaker claim than
"manners are not the operative variable, demand is." The paper's rhetorical claim to have refuted
a politeness account rests on a boundary drawn by the same people who wrote the test items and
interpreted the results.

The paper is not unaware of this. §4.2 concedes the coding "was made after seeing the effects,"
§8.7 concedes it "has no second rater" and "tests it on texts we wrote to embody our own coding."
The panel's point is that these concessions are made *in passing, late*, while the abstract and
§1.4 state the dissociation without them.

Two reviewers then separately found that the paper's literature search missed on-topic work, and
one found that its own benchmark now has a successor. That matters more than usual here, because
§1.2's novelty claim is explicitly hedged to the reach of the review — so gaps in the review are
gaps in the claim.

charlie, the alignment critic, took a different and equally serious line: every headline number in
the paper is measured against a "neutral" control interjection whose equivalence to *silence* is
established by a single p = 0.15 comparison, on one model, never revisited when the ceiling,
injection turn or model changed. If that baseline is offset, every turn-count and
accuracy-equivalence figure carries an unknown, unbounded offset with it.

---

## Prior work the panel surfaced — all four verified real

Reviewers were instructed to cite by arXiv ID only, from search output. **I independently verified
every ID against the arXiv abstract page before recording it here.** All four resolve, and the
titles match what the reviewers said they contained.

| arXiv ID | Title | In the paper? | In `Literature review/`? |
|---|---|---|---|
| 2512.12812 | *Does Tone Change the Answer? Evaluating Prompt Politeness Effects on Modern LLMs: GPT, Gemini, and LLaMA* | ❌ no | ✅ yes |
| 2609.09703 | *Should I Be Polite to My LLM Relevance Judge? Tone as a Severity Operating-Point Shift* | ❌ no | ❌ **no** |
| 2606.06460 | *Will the Agent Recuse, and Will It Stop? Measuring LLM-Agent Compliance with In-Band Governance Signals at the Access Door and Mid-Flight* | ❌ no | ❌ **no** |
| 2606.29955 | *SpreadsheetBench 2: Evaluating Agents on End-to-End Business Spreadsheet Workflows* | ❌ no | ❌ **no** |

Three observations, in descending order of how much they should worry you:

1. **2606.06460 is adjacent to your central result.** "Will the agent … stop? … in-band governance
   signals … mid-flight" is, on its title alone, a study of mid-task signals and whether an agent
   halts. That is the closing-cue finding's nearest neighbour, and §5.1's "no prior work connects
   closing-sequence structure to agent termination" needs checking against it before submission.
2. **2609.09703 runs the design §8.7 admits you did not.** bravo's reading is that it uses three
   independently written paraphrases per tone level across eight judge models — precisely the
   stimulus-sampling design §8.7 lists as a known gap. If so it is both a competitor and a
   citation that strengthens §8.7's candour.
3. **2606.29955 is a successor to your own substrate.** SpreadsheetBench 2 exists. §8.4's "a second
   substrate is the obvious next step" should probably name it.

I have **not** read any of the four beyond title and author metadata. Their relevance is inferred
from titles and from what the reviewers reported; each needs reading before it is cited.

---

## Concerns: blockers vs. polish

### Blockers — fix before submission

| # | Concern | Raised by |
|---|---|---|
| B1 | **Demand/register coding is post hoc, single-coder, no IRR, stimuli written by the authors to embody their own scheme.** The three-way dissociation cannot currently be distinguished from "explicit instructions change behaviour, decorative text does not." | all four |
| B2 | **No data/code availability statement, no repository link, and "Luna" is never identified by vendor or version** — while "two models from different labs" is load-bearing. | bravo, charlie |
| B3 | **"A pleasantry can end an agent's work" anchors the abstract** but rests on one run, one model, one ceiling, with the qualification not visible until §8.2–§8.6. | alfa, bravo |
| B4 | **On-topic prior work missing** from both the §3 audit and the reference list; §1.2's novelty claim is hedged to a review that did not reach it. | alfa, bravo |
| B5 | **The neutral-control baseline** — the denominator of every headline number — is validated against true silence once, at p = 0.15, on one model, and never rechecked. | charlie |
| B6 | **Turn count, the declared primary outcome, is never multiplicity-corrected**, though dozens of contrasts are reported and several load-bearing ones sit at p = 0.01–0.06. | bravo |

### Polish — worth doing, not submission-blocking

| # | Concern | Raised by |
|---|---|---|
| P1 | The ±4-point equivalence bound barely clears the design's own MDE (3.74–7.77, median 5.52); TOST is reached in 6 of 22 contrasts. | alfa |
| P2 | §5.1's closing-cue novelty is asserted more strongly than the search discipline supports. | alfa |
| P3 | No dose-response test — "demand" is binary, from one wording, yet treated as a scalar lever. | charlie |
| P4 | The pre-closing-structure account is not distinguished from cruder trained-pattern-matching. | charlie |
| P5 | Q3 ("no further notes will follow") may itself be an implicit demand under the paper's own §3.1 rule, putting §4.4 and §5.5 in tension. | delta |
| P6 | §7.6 lists six fixed analysis errors without before/after numbers, unlike the two documented in full. | bravo |

---

## On the three confounds you asked to be watched

- **Tone vs. length** — handled well and the panel did not challenge it. Verified independently in
  Stage 2: the interjections span 27–28 tokens, spread 1, all opening `Checking in`.
- **Tone vs. instruction content** — **this is B1**, and it is the panel's central objection. Not
  a confound the paper missed; a confound it identified, named, and then relied on a self-authored
  coding to resolve.
- **Model/provider variance** — surfaced as B2 (unidentified model) and B3 (single-model results
  generalised). charlie additionally notes the cross-model replication of the praise leg is not
  actually significant.
