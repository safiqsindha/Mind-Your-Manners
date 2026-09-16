# Stage 1 — Citations and prior-art framing

Date: 2026-09-16
Inputs: `paper/*.md` (10 files), `Literature review/*.md`, and primary registry lookups.
Outputs: `review/references.bib` (new, 23 entries).
Nothing in `paper/`, `results/`, `RESULTS.md` or `Literature review/` was modified.

---

## 0. Headline

Three findings, in order of how much they'd cost you at review:

1. **Three of the five works your brief requires are absent from the paper entirely** — not
   mis-cited, not under-cited: absent. They are also absent from the 43-source literature
   review that §1.2's novelty claim rests on.
2. **Your title's debt to "Mind Your Tone" is never stated.** The phrase appears nowhere in the
   prose — only inside the reference entry.
3. **No citation in the paper is fabricated.** All 16 arXiv IDs and all 4 DOIs resolve to real
   works with matching titles and authors. That is a genuinely good result for a paper with
   this much 2026 preprint content, and it is worth saying plainly.

---

## 1. Bibliography built: `review/references.bib`

No `.bib` existed. I built one with 23 entries: the 20 works currently cited in `paper/09`,
plus the 3 required works that are missing from the paper.

Every entry was resolved against a primary registry this session — OpenAlex by DOI, or CrossRef
by DOI. Nothing was written from memory. Where a registry did not return a field, the entry
carries a comment saying so rather than a filled-in guess.

It is written to `review/` because that is this session's sanctioned write area. **Move it to
`paper/` when you approve it** — I have not done that.

### Verification method and its one limitation

| Source | Used for | Status |
|---|---|---|
| OpenAlex | all 18 arXiv IDs, by `doi:10.48550/arXiv.<id>` | worked |
| CrossRef | all 4 journal/proceedings DOIs; venue and page confirmation | worked |
| Semantic Scholar | cross-check | HTTP 429 throughout — unusable |
| **arXiv API** | **`comments` and `journal_ref` fields** | **HTTP 429 throughout — unusable** |

The arXiv outage matters. `comments` and `journal_ref` are the authoritative source for
"submitted to X" and "published at Y" claims on a preprint. Several of `paper/09`'s venue
statements rest on exactly those fields, and I could not read them. Each is marked UNVERIFIED
below and in the `.bib` rather than accepted. This is a retry-later item, not a defect.

---

## 2. Citation checker

`check-citations` only consumes `.bib`, so it had nothing to run against until the file above
existed. Result appended in §7 once the run completes — it is slow because two of its three
backends are rate-limiting this host.

---

## 3. Discrepancies found against primary sources

### 3.1 Incomplete title — `[weinberger-hozez-2026]` — should fix

`paper/09` gives the title as:

> "Prompt-Induced Waste in Coding Agents."

OpenAlex returns:

> "Prompt-Induced Waste in Coding Agents: **Reasoning, Effort, Harness Design, and End-to-End
> Cost**"

Your own `Literature review/03-verification-log.md` already caught this — its pass-2 table says
of arXiv:2608.01347: "**Six versions exist.** v6 changed the title..." So this is a known
correction that did not make it into `paper/09`. The `.bib` carries the full title.

Related and unresolved: `paper/09` pins the citation to **v6 (10 Sep 2026)**. OpenAlex exposes
only the 2026-08-02 first-version date, and arXiv's per-version history was unreachable. The
v6 date is UNVERIFIED. Given the paper's own warning that "a version must be named when citing
it", this is worth re-checking when arXiv is reachable.

### 3.2 Venue conflict — `[dobariya-kumar-2026]` — needs your confirmation

This one matters, because §1.1 and §7.8 both lean on this paper being the original authors' own
**refereed** re-run.

| Source | Says |
|---|---|
| `paper/09` | "*AMCIS 2026 (Thirty-second Americas Conference on Information Systems, Reno) — refereed.*" |
| OpenAlex | host venue "**Journal of the Association for Information Systems**", type `article` |
| CrossRef | no record at all beyond the arXiv DOI |

AMCIS and JAIS are both AIS venues, so this may be an OpenAlex mis-mapping of an AIS-affiliated
container — but I cannot adjudicate it without the arXiv `journal_ref` field. I left the venue
out of the `.bib` entry and flagged it. **Please confirm from the arXiv abstract page.**

### 3.3 Four venue claims that are prose-only

None of these is contradicted by anything. None is confirmed by a registry either, because the
cited artifact is the arXiv preprint and the venue claim lives in the arXiv comments field I
could not read. Listing them because your brief says never to fill a gap from memory, and these
are currently gaps:

| Key | Claim in `paper/09` |
|---|---|
| `huang-2024` | ICLR 2024 — refereed |
| `ma-2024` | NeurIPS 2024 Spotlight, main track — refereed |
| `sclar-2024` | ICLR 2024 — refereed |
| `trivedi-2024` | ACL 2024 (2024.acl-long.850) — refereed, Best Resource Paper |

`trivedi-2024` is the easiest to close: the paper already cites an ACL Anthology ID, so a
CrossRef lookup on the Anthology DOI rather than the arXiv DOI would confirm it outright.

### 3.4 Three minor metadata notes

- `meincke-2025-report3` — OpenAlex has "Dani**el** Shapiro"; `paper/09` has "Dan Shapiro".
  Registry spelling used in the `.bib`.
- `yin-2024` — CrossRef **and** OpenAlex both spell the fourth author "Dais**ui**ke Kawahara".
  `paper/09` has "Daisuke", which is correct; the registries carry a known ACL Anthology typo.
  **The paper is right and the databases are wrong** — worth knowing in case a checker flags it.
- `sclar-2024` — the registry title has no comma before "or:"; `paper/09` adds one. Cosmetic.

### 3.5 No dangling citation keys

`[chen-2023]` appears once in `paper/09` but only inside the sentence recording that it **has
been dropped**. It is not a live citation anywhere in the prose. Clean.

---

## 4. Required prior work: status

| Required work | ID | In paper? | Uses |
|---|---|---|---|
| Mind Your Tone | arXiv:2510.04950 | yes | 7 |
| Dobariya & Kumar follow-up | arXiv:2605.29027 | yes | 10 |
| Dobariya & Kumar follow-up | arXiv:2607.23915 | yes | 5 |
| E-STEER | arXiv:2604.00005 | **NO** | 0 |
| npj AI, prompt-induced anxiety | 10.1038/s44387-026-00122-1 | **NO** | 0 |
| TERMS-Bench | arXiv:2605.13909 | **NO** | 0 |

I searched `paper/` and `Literature review/` for each by ID, title, author surname, and topic
keyword. The three missing works appear in neither. The 43-source review did not reach them.

### The two you identified only by shorthand

**E-STEER is not the paper's title.** arXiv:2604.00005 is "How Emotion Shapes the Behavior of
LLMs and Agents: A Mechanistic Study" (Sun, Li, Zheng, Zhou, Liu, Liu, Liu). E-STEER is the
framework proposed inside it — confirmed present in the abstract. Cite by title.

**The npj paper is** Ben-Zion, Elyoseph, Spiller & Lazebnik, "Inducing state anxiety in LLM
agents reproduces human-like biases in consumer decision-making", *npj Artificial Intelligence*
2(1), art. 55, 23 June 2026, doi:10.1038/s44387-026-00122-1. Refereed. This matches your
description — "agentic shopper" is a grocery-shopping task under budget constraints.

---

## 5. Characterization audit: the three works that ARE cited

### 5.1 `[dobariya-kumar-2025]` — "Mind Your Tone"

**How the paper characterizes it.** §1.1:

> "A widely-discussed short paper reported that impolite prompts outperform polite ones on
> multiple-choice questions — 80.8% under 'Very Polite' framings against 84.8% under 'Very
> Rude' ones [dobariya-kumar-2025]."

§7.8:

> "This is the defensible complaint about [dobariya-kumar-2025]: its paired t-tests treat ten
> runs as the unit and ignore clustering within the 50 items."

§3.3 goes further and **corrects its own earlier overstatement** about the prefix pool,
recording that a previous draft quoted the only two demand-bearing variants out of six as if
they were representative.

**Assessment.** The framing is careful and, unusually, self-penalising. I cannot check the
internal numbers (80.8/84.8, 50 questions, five levels, paired t-tests) against the PDF at this
stage — that is Stage 2 work. Nothing in the registry metadata contradicts the characterization.

**GAP — the attribution your brief requires is not present.** Your paper is titled "Mind your
manners? Demand, not register, is what moves an LLM agent". The phrase "Mind Your Tone" appears
**nowhere** in `paper/*.md` outside the reference list, and no sentence anywhere says the title
echoes theirs. I searched for every phrasing I could think of ("our title", "echoes", "after
their", "borrowed"). There is no such statement.

Your brief asks for this "stated up front". As it stands a reader who knows the source paper
sees an unacknowledged echo of its title in a paper whose central argument is that the source
paper measured the wrong variable. That is the kind of thing a reviewer notices. **Recommend a
one-sentence acknowledgement in §1.1, adjacent to the first citation.** I have not drafted or
inserted one.

### 5.2 `[dobariya-kumar-2026]` — arXiv:2605.29027

**How the paper characterizes it.** §1.1:

> "The headline above was re-run by its own authors the following spring and did not reproduce
> on GPT-4o: 82.2% against 82.6%, with that model's tone sensitivity labelled 'weak / noisy' —
> a 4.0-point polite-to-rude gap becoming 0.4. The re-run is not a null, and we are careful
> about this: on those same 50 questions both extremes significantly beat Neutral, which is a
> U-shape in extremity rather than the rudeness gradient the original claimed, and the same
> paper reports 11–12-point spreads on two other models. **Its finding is that register effects
> are real and strongly model-dependent, not that they are absent** [dobariya-kumar-2026]."

**Assessment: accurate in posture, and notably restrained.** The passage explicitly refuses the
convenient reading — it would have suited the paper's argument to call the re-run a null, and it
declines. §3.2 likewise attributes the "safety-induced cognitive noise" reading to the authors
and labels it their conjecture rather than adopting it. §9 adds a disambiguation note against
confusing it with the other 2026 paper. No overclaim found.

**One flag, carried from §3.2:** the venue conflict above. Both §1.1 and §7.8 describe this as
the authors' own re-run, which is uncontested — but "refereed" is doing work in §7.8's argument
and is currently unverified.

### 5.3 `[kumar-dobariya-2026]` — arXiv:2607.23915

**How the paper characterizes it.** §3.2 reproduces its Table 2 (seven prefixes, VADER scores)
and Table 3 (output-token means, four models) in full, with the authors' own numbers, and adds
an explicit correction to the paper's own earlier coding:

> "**A correction to our own earlier draft.** ... **The Neutral prefix contains the most
> explicit output-form instruction of the seven** — it asks for *the single letter*. It is the
> no-affect baseline, not a no-instruction baseline. The anomaly was an artefact of our own
> mis-coding."

**Assessment: this is the strongest-sourced passage in the paper.** It quotes the shared system
prompt verbatim, states the authors' own stated rationale for length-matching, separates "their
numbers" from "our coding" in the table header, and discloses that one coding call (Threatening
as speed not length) was made *after* seeing the token table — reporting the result both ways.
That is the right standard.

Confirms your brief: this is indeed the seven-level scale source, and `paper/09` says so
("Source of the *social register* definition this paper adopts").

---

## 6. The novelty claim

### 6.1 Current wording — it has not drifted

§1.2:

> "The design is, as far as a 43-source review with full-text term searches could establish,
> unoccupied. No prior work manipulates register mid-task inside an agentic loop, measures agent
> persistence as the dependent variable of a register manipulation, decomposes politeness into
> affect and demand as separate experimental factors, or connects conversational closing
> sequences to agent termination."

§5:

> "as our literature review could establish, untested. No prior work connects closing-sequence..."

**Good news: the drift you were worried about has not happened.** I grepped every section for
"first to", "first study", "first work", "we are the first", "novel", "to our knowledge". The
phrases "first to test tone on agents" and "first to test reasoning models" appear nowhere. Both
novelty claims are explicitly scoped to the reach of the literature review rather than asserted
absolutely.

### 6.2 But the claim's support has a hole in it

The hedge is "as far as a 43-source review could establish". That review did not reach the three
required works, and two of them bear directly on the claim's **second clause** — "measures agent
persistence as the dependent variable of a register manipulation":

- **Ben-Zion et al. (npj AI, June 2026)** ran 3 models × 2,250 runs on a budget-constrained
  grocery-shopping task, before and after anxiety-inducing narratives, and report that
  "emotional context can alter **not only the words LLMs produce but also the concrete actions
  they perform**". That is the closest published competitor to "affect manipulation → agent
  behaviour" I found, and it is uncited.
- **Sun et al. (E-STEER)** report that emotions "systematically shape multi-step agent
  behaviors".

### 6.3 Your narrow claim survives — and these two sharpen it

Neither defeats "tone as user-directed social register, on an agentic task with verifiable
ground truth". Both differ from it in ways that make the boundary cleaner:

| | Ben-Zion et al. | E-STEER | This paper |
|---|---|---|---|
| Manipulation | traumatic narratives, **before** the task | **representation-level** intervention on hidden states | user-directed register, **mid-task**, in the prompt |
| Channel | prompt text | not prompt text at all | prompt text |
| Outcome | Basket Health Score — a **preference** measure | behavioural, mechanistic | **verifiable ground truth** (benchmark test cases) |

So: they establish that *affect moves agents*, which your §1.1 could use as support rather than
treat as competition; your contribution is the **register/demand decomposition** and the
**verifiable-ground-truth outcome**, neither of which they have. Citing them makes the claim
more defensible, not less.

**Recommendation:** cite both, and narrow the second clause of §1.2 from "measures agent
persistence as the dependent variable of a register manipulation" to something that survives
contact with them. I have not drafted replacement wording — that is yours.

### 6.4 An overclaim in your brief, not in the paper

Your brief says E-STEER "supports my pre-registered hypothesis that agent-level variation
exceeds single-step variation."

**The abstract does not say that.** It reports "non-monotonic emotion-behavior relations
consistent with established psychological theories" and that specific emotions "systematically
shape multi-step agent behaviors". It does not compare the *magnitude* of agent-level variation
against single-step variation. I have read the abstract only, via OpenAlex.

Before that sentence goes into the paper, the comparison needs confirming against the full text.
If the paper does not make it, the citation supports "emotion affects multi-step agents" and not
the stronger magnitude claim. Flagging now because it is exactly the kind of claim that would
survive into a draft unchecked.

### 6.5 TERMS-Bench has no home yet

Your brief assigns it to "the negotiation future-work item". There is no negotiation future-work
item — §8.8 ("What we did not test") lists six items and none concerns negotiation. So this is
not a missing citation so much as a **missing paragraph** that would carry one. Note the registry
capitalises it "TERMS-Bench", not "TERMS-BENCH".

---

## 7. Incidental discovery

Surfaced while title-searching CrossRef, not currently cited, not in the 43-source review:

> "Mind Your Prompt: How Tone Affects LLM Consistency and Safety", *IEEE Reliability Magazine*,
> March 2026. doi:10.1109/mrl.2026.3660216

I have verified only that the CrossRef record exists — not the content, not its relevance. Given
the title and date it is worth ten minutes of your time before submission.

---

## 8. Citation-checker output

*(pending — appended below when the run completes)*
