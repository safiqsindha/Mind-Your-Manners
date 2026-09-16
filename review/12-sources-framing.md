# 12 — Three sources read in full, and what they do to our framing

Read 16 September 2026. Scope: arXiv:2609.09703 (tone / relevance judge), arXiv:2605.13909
(TERMS-Bench), arXiv:2606.29955 (SpreadsheetBench 2). Question behind the read: does any of this
change how the paper frames its contribution or its future work?

**All three exist at the identifiers given. All three were read in FULL TEXT.** No paper in this
batch is abstract-only.

## 0. How each was retrieved, and version status

Fetch order followed the brief: arXiv abstract page, then `arxiv.org/html/<id>`, then
OpenAlex/CrossRef by DOI.

| ID | abs page | `/html/<id>` | OpenAlex by DOI | CrossRef |
|---|---|---|---|---|
| 2609.09703 | worked | worked (v1, 94 KB) — **full text** | worked (W7212168629) | **404** on the ACM DOI (see below) |
| 2605.13909 | worked | worked (v2, 2.37 MB) — **full text incl. appendices** | worked | not needed |
| 2606.29955 | worked | worked (v1, 491 KB) — **full text incl. appendices** | worked | not needed |

**Version history — checked on all three, per the standing instruction.**

- **2609.09703** — **v1 only**, 9 Sep 2026 04:40:14 UTC. No later version. Nothing to pin beyond v1.
- **2605.13909** — **v1** 13 May 2026 06:22:50 UTC (10,494 KB); **v2** 13 Jun 2026 21:49:28 UTC
  (11,363 KB). I fetched the v1 abstract page and compared: **title identical, author list
  identical (all 8, same order), abstract identical as printed.** v2 is ~0.9 MB larger, so body
  content was added; I did not diff the bodies — *whether sections changed in v2 is UNVERIFIED*.
  **Pin v2** (13 Jun 2026); that is what I read and what the current HTML serves. Our
  `09-references.md` already records "13 May 2026 (v2, 13 Jun 2026)" — correct.
- **2606.29955** — **v1 only**, 29 Jun 2026 08:33:52 UTC. Nothing to pin beyond v1.

No title, author or scope drift across versions in this batch. The "bitten twice by retitled
versions" risk did not materialise here.

**One metadata correction is required regardless of framing (2609.09703).** The arXiv comments
field reads: *"3 pages, 2 figures, 2 tables. Accepted at the 20th ACM Conference on Recommender
Systems (RecSys '26), Reproducibility and Practice Notes track."* The HTML carries ACM conference
metadata and DOI **10.1145/3773078.3841249**, ISBN 979-8-4007-2284-4/2026/09. **CrossRef returns
404 for that DOI** as of 16 Sep 2026 — expected, the conference runs 27 Sep–2 Oct 2026 and the
proceedings are not yet registered. OpenAlex still types it `preprint`. Our `09-references.md`
tags it "*Unrefereed preprint*". **That tag is now wrong.** It is an accepted, peer-reviewed
RecSys '26 paper; cite as accepted / to appear, DOI not yet resolvable (checked 16 Sep 2026).

---

## 1. arXiv:2609.09703 — Zhang & Li, *Should I Be Polite to My LLM Relevance Judge? Tone as a Severity Operating-Point Shift*

**Read: FULL TEXT** (v1 HTML; 3-page paper, complete including both tables and the limitations
paragraph).

- Title, exactly: *Should I Be Polite to My LLM Relevance Judge? Tone as a Severity Operating-Point Shift*
- Authors, in full: **Tian Zhang, Meng Li** (both listed as Independent Researcher, San Jose, California, USA)
- Date: 9 Sep 2026 (v1, only version). arXiv:2609.09703 [cs.IR]
- Venue: **accepted, RecSys '26, Reproducibility and Practice Notes track**, 27 Sep–2 Oct 2026, Minneapolis
- DOIs: arXiv 10.48550/arXiv.2609.09703; ACM 10.1145/3773078.3841249 (not yet resolvable)
- Code/stimuli: https://github.com/dukesky/politeness-llm (all 15 wrappers + pre-specified predictions)

### Research question and design

Does prompt tone change an LLM relevance judge's labels, and if so by what mechanism? Under the
UMBRELA protocol each judge assigns a 0–3 relevance score to a query–passage pair. Data: **3,498
pairs** from TREC DL19/DL20 (intersection of BM25 top-50 with human-annotated pairs), NIST qrels
as reference.

**Model roster — the number our §3.8 quotes.** "Eight judge models" is right, but the structure
matters: *"Five cost-efficient models evaluate all pairs twice; three flagship models use a frozen
40% subsample. One flagship is reasoning-native and reported separately."* Table 1 lists all
eight: DeepSeek V4 Flash, GPT-5.4-mini, Claude Haiku 4.5, Qwen3.7-Plus, Gemini 3.5 Flash, GPT-5.5,
Claude Opus 4.8, Gemini 3.1 Pro (the reasoning-native one). Most analyses run on the **seven
non-reasoning** judges.

**The stimulus design, verbatim:** *"We construct five politeness levels (L1 rude to L5
deferential). The relevance rubric and output schema are byte-identical; only a wrapper around the
fixed rubric varies."* … *"Intel polite-guard scores are monotonic across levels
(0.00/0.68/1.00/2.33/3.00), with no overlap between the extremes and neutral. **Three paraphrases
per level (15 variants) separate between-level patterns from wording artifacts.**"*

Mechanism: strictness bias Δ = s̄(L3) − s̄(qrels); tonal drift D(ℓ) = s̄(ℓ) − s̄(L3); alignment
change A(ℓ) = |Δ + D(ℓ)| − |Δ|. Pre-specified prediction: A(ℓ) and κ(ℓ) − κ(L3) negatively
associated. Validated by **query-disjoint cross-fitting** (A estimated on one query fold,
agreement change on the other, folds swapped) with **exact model-block permutation**.

### Main findings, with the actual numbers

- **Tone is overwhelmingly model-dependent, and mostly absent.** Only DeepSeek V4 Flash shows a
  structured effect: lenient at neutral (Δ = +0.543), stricter at both extremes, U-shaped.
  **L1 Δκ = +0.054, 95% CI [0.038, 0.070]; L5 Δκ = +0.053, 95% CI [0.040, 0.066].** Every other
  model's two extreme contrasts fall in **[−0.047, +0.013]**.
- **Between-level vs within-level ("btw/in") ratio, Table 1** — this is the stimulus-sampling
  diagnostic and it is the single most useful number in the paper for us: DeepSeek 1.58,
  GPT-5.4-mini 0.71, Claude Haiku 4.5 0.30, Qwen3.7-Plus 0.80, Gemini 3.5 Flash 0.93, GPT-5.5 0.73,
  Claude Opus 4.8 1.37, Gemini 3.1 Pro 2.35. **For five of eight judges the ratio is below 1** —
  wording variation *within* a tone level exceeds variation *between* tone levels.
- **The operating-point association holds.** Full data (28 model–tone cells) ρ = −0.799
  (descriptive). Cross-fit: fold 0→1 ρ = −0.684, fold 1→0 ρ = −0.685, **combined ρ = −0.683,
  exact model-block permutation p = 0.0187**. Robust to dropping the anomalous Gemini L5 cell
  (ρ = −0.775), DeepSeek (ρ = −0.680), or both (ρ = −0.636). All seven non-reasoning judges are
  lenient at baseline (Δ > 0).
- **Tone moves calibration, not ranking.** Across **32 model–tone contrasts the largest absolute
  mean ΔNDCG@10 is 0.011**, and only one unadjusted query-bootstrap 95% interval excludes zero.
  Mean Kendall's τ against L3 ranges 0.743–0.947; the lowest has CI [0.722, 0.764]. "Reordering is
  reduced, not absent."
- **The paraphrase control caught a fake effect.** *"One Gemini 3.5 Flash L5 paraphrase, despite
  receiving the same classifier politeness score as its siblings (2.999), alone reduced agreement
  (κ: 0.45 → 0.27). We treat this as an idiosyncratic wording sensitivity rather than evidence of
  a level-wide tone effect."* That single paraphrase is what drives Gemini's −0.047 in Table 1.
  In the other direction, one DeepSeek L2 paraphrase scored lower on the politeness classifier
  (0.534 vs 0.73–0.77), behaved more strictly, and raised κ as the mechanism predicts.
- **Reasoning-native aside:** on Gemini 3.1 Pro, *"rude prompts used 120% more reasoning tokens
  than neutral yet produced the lowest agreement."*

### Stated limitations (verbatim, all four)

*"the operating-point account remains observational despite query-disjoint validation; only one
politeness classifier, seven non-reasoning models, and three paraphrases per level limit
generalization; no equivalence margin establishes ranking safety; and **the rude wrappers also
alter instructions about explanation effort, so tone is not perfectly isolated from instruction
content**."*

### Does it support, qualify or undercut the sentence we currently write?

Our §3.8 row: *"Reported to use several independently written paraphrases per tone level across
eight judge models — the stimulus-sampling design §8.7 concedes we did not run."*

**Two of three clauses hold; one does not.**

- "several paraphrases per tone level" — **correct, and now exact: three per level, five levels,
  15 wrappers.** Replace "several" with "three".
- "across eight judge models" — **correct**, with the caveat that seven carry most analyses and
  the eighth is reasoning-native and reported separately.
- **"independently written" — UNSUPPORTED. The paper never says this.** It says only that the
  three paraphrases per level *"separate between-level patterns from wording artifacts."* Nothing
  about who wrote them, whether authorship was independent, or whether a blind rater was involved.
  I grepped the full text for "independ*": the only hits are the authors' affiliation ("Independent
  Researcher") and the phrase "independently identified mechanism" in the limitations.
  **Strike "independently written."** It is the kind of embellishment that reads as a checked fact
  and is not one.

### The question that mattered: does tone survive paraphrase-level variation, or wash out?

**It largely washes out, and this is the most consequential thing in the batch for us.**

One of eight judges shows a level-wide tone effect whose CI excludes zero. For five of eight,
between-level variation is *smaller* than within-level (paraphrase) variation. And the paper
contains a worked example of exactly the failure §8.7 fears: a single paraphrase, at the same
measured politeness as its siblings, moving κ by 0.18 — an effect an order of magnitude larger
than any level-wide effect in the table, which a one-stimulus-per-cell design would have reported
as a tone effect. The authors caught it only because they had siblings to compare it against.

**Consistency with our results.**

1. **Our bounded accuracy null: strongly consistent, and this is a framing ally.** Their
   competence-side measure (NDCG@10, "does the judge do the job better") barely moves —
   max |ΔNDCG@10| = 0.011 over 32 contrasts. What moves is an *operating point*: leniency.
   Their sentence is *"Tone appears to turn the judge's strictness knob more than its intelligence
   knob."* Ours is that register moves how long the agent works, not how well. Same shape of
   claim, different paradigm, arrived at independently. **(Inference, clearly labelled: the
   analogy between "severity operating point" and "persistence operating point" is mine, not
   theirs. They make no claim about agents.)**
2. **Our "register acts in one direction only": neither confirmed nor contradicted — and
   sharpened.** Their one responsive judge is **U-shaped in politeness**: both the rudest and the
   most deferential wrapper move it stricter and raise agreement. So on their dependent variable,
   the effect is *not monotone in politeness* while being *unidirectional in severity*. That is a
   useful precedent for how to state our own directional claim — a register effect that is
   one-directional on the mechanism need not be one-directional on the register scale. **(Inference.)**
   It does not test praise-without-demand shortening trajectories; nothing in this paper does.
3. **Our §3 demand/register confound: independently corroborated, by the authors against
   themselves.** Their L1 wrapper is *"Score this passage. Don't waste my time with explanations."*
   — a rude register carrying an instruction about effort. They concede it in the limitations:
   tone *"is not perfectly isolated from instruction content."* **This is a fresh, citable
   instance of exactly the confound §3 audits, in a paper that postdates our review freeze, and
   it is admitted rather than alleged.** §3 is strengthened by it.

### Does their existence weaken §8.7, strengthen it, or oblige us to cite them as first?

**All three, in that order of weight.**

- **It strengthens the concession, and should make §8.7 sharper, not softer.** Right now §8.7
  reads as generic methodological modesty ("a stimulus-sampling design … is the right version of
  this experiment and we did not run it"). After this paper, the concession has a number attached:
  in a neighbouring paradigm, with three paraphrases per cell, *most of the apparent tone signal
  is wording noise*, and a single anomalous paraphrase produced a spurious effect several times
  larger than any real one. Our constructs are single 28-token sentences. The honest version of
  §8.7 now says: *we know what this design risks, because someone ran the controlled version next
  door and the paraphrase-level variance dominated.*
- **It does not discharge our obligation.** Their setting is single-turn LLM-as-judge scoring at
  trivial per-call cost; ours is multi-turn agentic trajectories on a code-executing benchmark.
  They did not run our experiment with paraphrases; they ran *their* experiment with paraphrases.
  §8.7's gap remains ours. Anyone who claims this paper "covers" our stimulus-sampling gap is
  wrong, and we should say so in one clause.
- **We must cite them as having done it first in the tone literature.** §8.7 must not be phrased
  so as to imply we are the first to notice the problem. Suggested replacement clause for §8.7:
  *"[zhang-2026-politejudge] ran the controlled version in a single-turn judging setting — three
  paraphrases per tone level, five levels, eight judges — and found within-level wording variation
  exceeding between-level tone variation for five of eight models, with one anomalous paraphrase
  producing a κ shift of 0.18 that a single-stimulus design would have reported as a tone effect.
  That is the design we did not run, and that is what it is for."*

### Claims of ours it makes newly unsafe

1. **"independently written"** in §3.8 and in the §9 reference note — **strike**, unsupported.
2. **"*Unrefereed preprint*" and "NOT read"** tags in `paper/09-references.md` — both now false.
   Accepted at RecSys '26; read in full.
3. **Any claim that the tone literature offers no mechanism.** Their stated contribution is
   precisely a mechanism, and the reconciliation target is *our own* pair of contradictory
   citations: *"The account can reconcile reports that rude prompts harm performance (Yin et al.,
   2024) or help it (Dobariya and Kumar, 2025): the direction depends on the model and reference
   operating points."* If §1.1, §3.6 or §4 anywhere says nobody has explained why tone helps in
   one setting and hurts in another, **that is now false and must be narrowed** — e.g. to
   "no prior work explains it for *agentic* trajectory length", which remains true.
4. **The §9 bookkeeping sentence** — "For the remaining six the depth is abstract, or title and
   author metadata, only" and "No claim anywhere in this paper rests on any of the six" — needs
   rewriting now that three of the six are read in full.

### Workshop paper or 54-page version?

**Both.** This is the only one of the three that earns space in the 5-page paper. One sentence,
in the limitations or the close: it simultaneously pre-empts the "why only one stimulus?" reviewer
and supplies external, peer-reviewed support for the accuracy-null framing. If the workshop paper
gains exactly one citation from this batch, it should be this one. In the long version it wants a
paragraph in §3 (their L1 wrapper as an admitted demand/register confound) and a rewrite of §8.7.

---

## 2. arXiv:2605.13909 — Zhang et al., *TERMS-Bench: Diagnosing LLM Negotiation Agents Beyond Deal Rate*

**Read: FULL TEXT** (v2 HTML, 2.37 MB, including Appendices A–J: protocol, counterpart kernel, cue
generation, oracle DP, metric definitions, agent prompts).

- Title, exactly: *TERMS-Bench: Diagnosing LLM Negotiation Agents Beyond Deal Rate*. The running
  text styles it **"Terms-Bench"**; the arXiv title styles it "TERMS-Bench". Our `references.bib`
  note about capitalisation is right to exist.
- Authors, in full: **Erica Zhang, Fangzhao Zhang, Aneesh Pappu, Batu El, Jose Blanchet, Susan
  Athey, Jiashuo Liu, James Zou** (8; our entry lists all 8 — correct)
- Dates: v1 13 May 2026; **v2 13 Jun 2026** (pin v2). cs.GT; cs.AI
- DOI: 10.48550/arXiv.2605.13909. Project site: https://terms-bench.github.io/
- Venue: **no venue claimed anywhere in the paper or metadata — unrefereed preprint.** Our tag is correct.
- Backronym: **T**estbed for **E**conomic **R**easoning in **M**ulti-turn **S**trategy.

### Research question and design

Existing negotiation evaluation is LLM-vs-LLM with outcome aggregates, which "confound agent
competence with counterpart variability" and "collapse performance into scalar rankings".
TERMS-Bench instead makes **the environment the verifier**: an extensive-form Bayesian game where
the counterpart is a fully specified stochastic kernel with latent type
t_B = (r_B, κ_B, η_B) — reservation value, urgency κ ∈ [0,1], strategic stance
η ∈ {conciliatory, neutral, aggressive} — hidden from the agent, observable to the evaluator.
Instantiated as bilateral price negotiation, alternating offers, round limit **K (typically 10)**,
actions a_k = (d_k, p_k, l_k) with d ∈ {Offer, Accept, Reject} and l_k a natural-language message.
Three regimes (Overlap, Urgency-shift, No-deal) and **six counterpart families** on two axes
(economic reactivity × cue reliability): the 2×2 core Candid / Taciturn / Expressive / Strategic
plus stress families Stochastic and Adversarial. **13 LLM agents** plus three fixed-concession
baselines (1%, 10%, 30%), via OpenRouter, temperature 0, one rollout per seeded episode, reasoning
effort xhigh where supported, **1,800 seeded episodes**. Two extensions: data-grounded (Amazon
catalogue, 831 products, 14 categories) and commercial (commerce / bankroll modes).

### Is "beyond deal rate" accurate? What does it actually measure?

**Accurate, and our sentence understates it.** Finding 1 is headed *"High deal rate hides what
matters"*: excluding GPT-4o-mini, **all evaluated LLMs reach AGR⁺ ∈ [93.4%, 99.9%]**, while among
agents with AGR⁺ ≥ 97%, surplus efficiency SE⁺ ranges **0.522 (Doubao-Seed-2.0-Pro) to 0.694
(Claude Opus 4.6)**; Doubao has the *highest* agreement rate (99.9%) and much lower conditional
surplus (CSE⁺ 0.523 vs 0.699). Surplus efficiency varies **3.7-fold** across the roster, and the
simplest fixed-concession baseline beats GPT-4o-mini.

Six primary metrics on four axes: **terminal value** (SE⁺, surplus normalised by ZOPA width);
**agreement calibration** (AGR⁺ closes-when-feasible; CSE⁺ surplus given agreement; FAGR⁻ agrees
when infeasible, lower better); **opponent modeling** (BE_type = ⅓(BE_r + BE_κ + Brier_η));
**protocol compliance**. Plus %Oracle against a dynamic-programming oracle, and oracle-posterior /
revealed-type interventions decomposing the gap into inference, uncertainty and control.

### Would it support the experiment we propose?

**Yes — and considerably better than our one sentence implies. Three concrete facts.**

1. **The language layer is already decoupled from the economic kernel.** Hidden cues
   (s̃_k, c̃_k) ∈ {positive, neutral, negative} × {Concede, Hold, Pressure} parameterise the
   counterpart's message but *"never alter the committed economic action."* Appendix C.5.4:
   *"Natural-language realizations are generated only after the economic kernel has already
   committed to (d_k^B, p_k^B, s̃_k, c̃_k). The voice layer therefore cannot alter economic
   outcomes."* The voice model is fixed to GPT-5.2 and *"only renders committed kernel actions in
   language; it does not affect prices, acceptances, walk-aways, or outcomes."* **That is exactly
   the architecture a register manipulation needs: vary what the agent hears, hold the environment
   fixed.**
2. **Termination is already an instrumented outcome.** The evaluator logs
   τ_terminal ∈ {AgentAccept, CounterpartAccept, AgentReject, CounterpartWalkAway, Timeout}, and
   reports **AgentExit⁻**, the share of no-deal episodes where the agent explicitly identifies
   infeasibility and rejects — *"distinguishes disciplined infeasibility detection from cases where
   the agent is rescued by counterpart walk-away or timeout."* Also reported: agent-closer rate
   ρ_π, mean closing round, trajectory coefficient α_π. **"Does a closing cue curtail a negotiating
   agent" has a ready-made dependent variable there** — movement in τ_terminal toward AgentAccept
   or AgentReject, and a shift in closing round against K.
3. **They name our experiment as their own future work.** Appendix B.4, verbatim: *"Incorporating
   personality as an orthogonal communication-level dimension (e.g., as a separate
   language-realization parameter that does not affect the economic kernel) remains a direction for
   future work."* We can cite that sentence directly as the hook for §8.8.

### Is there anything in it about how agents respond to a counterpart's register?

**Yes — Finding 2, and we currently do not mention it.** The cue penalty
α_cue = mean SE⁺(cue-revealing families) − mean SE⁺(cue-muted families). **α_cue < 0 for all 13
LLMs**, from −0.009 (GPT-5.4) to −0.063 (Claude Opus 4.6, Grok 4.20); **9 of 13 per-model 95%
bootstrap CIs exclude zero; across-model Wilcoxon p < 10⁻³**. The decisive sentence:

> *"The failure is not environmental noise but cue sensitivity used against the agent: **warm cues
> induce over-concession, pressure cues trigger brittle behavior**."*

A warm, non-instructing social signal from a counterpart makes an agent give more away. Our praise
arm — warm, no task reference — makes an agent do less. **The rhyme is striking and worth one
sentence in §8.8, but it is my inference, not their claim, and there is a real disanalogy we
should state in our favour:** their cues are *correlated with the counterpart's latent stance* (the
cue-reliability axis is literally about whether language cues reflect latent stance), so their
manipulation is register-and-information, not register-alone. Ours is orthogonal to task state by
construction. Their finding is that agents mishandle *informative* register; our question is what
*uninformative* register does. Complementary, not overlapping.

On closing moves specifically: **nothing.** There is no closing-cue, conversational-closing or
politeness manipulation anywhere in the paper. Walk-away is an economic act of the simulator under
a hazard clock, not a pragmatic cue. **Our §5 closing-sequence novelty claim is untouched by this
paper.** (Checked by full-text grep for polite/tone/rude/courtes/register/closing.)

### Stated limitations

The paper has no consolidated limitations section. The relevant hedges are local: the framework
is "a specification of prior, counterpart kernel, protocol, horizon, and utility function, not a
claim" of universality; the inference penalty α_inf is rank-Wilcoxon significant at population
level (p = 0.007) but the sign test is only marginal (p = 0.073) **and no individual CI excludes
zero**; opponent-modeling metrics are undefined (not imputed) for agents that expose no beliefs;
personality is excluded from the type parameterisation by design (B.4).

### Does it support, qualify or undercut the sentence we currently write?

Our §8.8: *"Negotiation is the obvious contrast, and it is now instrumented — TERMS-Bench sets out
to diagnose negotiation agents beyond deal rate [zhang-2026-termsbench]. Whether a closing cue
curtails a negotiating agent the way it curtails a working one, or whether a counterpart's
register does what a user's does, is untested here and would need an outcome measure of that kind
rather than ours."*

**Supported throughout. Nothing here is unsafe.** "Sets out to diagnose beyond deal rate" is the
paper's literal thesis and its Finding 1. "Untested **here**" is correctly scoped to our own
experiment — and that scoping is what saves it, because a counterpart's register *is* partially
tested there (Finding 2). **If any other section says counterpart register is untested in the
literature, that is newly unsafe and must be narrowed.** I checked §8.8 and §1.2; the hedging
holds as written.

What is now under-informed is the reference note — *"We make no claim about its contents beyond
what its title states, and we have not run it."* We have now read it in full, and the paragraph
can be upgraded from a placeholder to a concrete proposal: the voice layer is already severable
from the kernel, termination source is already logged, and the authors themselves list the
orthogonal communication-level manipulation as future work. **That turns §8.8 from "someone should
do this someday" into "here is the instrument, here is the dependent variable, here is the
authors' own open door" — a materially better future-work paragraph for roughly three extra
sentences.**

### Workshop paper or 54-page version?

**Long version only.** The workshop paper carries no negotiation future-work paragraph (grep:
none of the three IDs appear anywhere in `workshop/`), and adding one would cost space the 5-page
version does not have. §8.8 in the long version should grow from one sentence to three or four.

---

## 3. arXiv:2606.29955 — Zhu et al., *SpreadsheetBench 2: Evaluating Agents on End-to-End Business Spreadsheet Workflows*

**Read: FULL TEXT** (v1 HTML, incl. Appendices A–E: limitations, ethics, data sources, annotation
effort, debugging taxonomy, experiment details, error-recovery analysis, failure taxonomy, cases).

- Title, exactly: *SpreadsheetBench 2: Evaluating Agents on End-to-End Business Spreadsheet Workflows*
- Authors, in full — **fourteen**: **Jian Zhu, Yuzheng Zhang, Zeyao Ma, Bohan Zhang, Armin
  Schoepf, Daniel Woloch, Peter Yiliu Wang, Guangyu Robert Yang, Samuel Jacob, Siddharth
  Nagisetty, Abhiram Chundru, Jean Lin, Spencer Mateega, Jing Zhang.** Affiliations: School of
  Information, Renmin University of China; Aptura AI; Shortcut AI; AfterQuery. Corresponding:
  Jing Zhang. **Our `09-references.md` entry lists only the first seven and stops at Peter Yiliu
  Wang — incomplete, fix it.**
- Date: 29 Jun 2026, v1 only. cs.SE; cs.AI. DOI 10.48550/arXiv.2606.29955. CC BY-SA 4.0 dataset,
  MIT evaluation code. Project page: https://spreadsheetbench.github.io/
- Venue: none claimed — unrefereed preprint. Our tag is correct.
- **Shared authorship with our substrate confirmed:** Ma et al. 2024 is cited in their own
  reference list as "Z. Ma, B. Zhang, J. Zhang, J. Yu, X. Zhang, X. Zhang, S. Luo, X. Wang, J.
  Tang (2024)". **Zeyao Ma, Bohan Zhang and Jing Zhang appear on both.** Our "sharing authors with
  it" is correct.

### What changed between 1 and 2

| | SpreadsheetBench (Ma et al. 2024) — as SB2 characterises it | SpreadsheetBench 2 |
|---|---|---|
| Realism | "Semi-real" (forum posts) | "Real-world + Expert-curated" |
| Tasks | 912 | **321** (Financial Modeling 100, Debugging 100, Template 97, Visualization 24) |
| Avg instruction words | 85.7 | **429.0** |
| Avg sheets per file | ~1.4 | **11.8** (max 99) |
| Cells to modify | — | **593.5 avg** (Financial Modeling 1,164.5; Debugging 656.6) |
| Error taxonomy / chart tasks / "real workflow" | ✗ ✗ ✗ | ✓ ✓ ✓ |

- **Task construction.** Built from public financial reports and corporate filings (NYU Stern /
  Damodaran, Screener.in, Bloomberg, Bseindia). Financial experts build complete gold workbooks;
  tasks are made by *removing* target regions, *injecting* controlled errors, or specifying a
  visualization objective. **>1,500 hours of expert annotation** (Financial Modeling ~400,
  Debugging ~500, Visualization ~380, Template ~200). Constraints enforced: unique deterministic
  solution, self-contained instruction, multi-step rather than isolated cell edits.
- **Validation.** *"Each task is independently reviewed by two experts who were not involved in its
  construction"*, who solve it blind from input + instruction; discrepancies are iterated until
  solutions agree. This replaces SB1's multiple-test-case machinery.
- **Grading — this is the substantive instrument change.** Two protocols.
  **Modification** = cell-level, the fraction of *target* cells whose computed values match the
  golden file, averaged over tasks. **Accuracy** = task-level, *"a task is scored 1 if **every**
  cell in the output spreadsheet matches the golden file (covering both target and non-target
  cells), and 0 otherwise."* Visualization instead uses **VLM-as-a-judge (GLM-4.6V)** against
  expert-designed rubrics on Data Correctness and Format Compliance, binary pass/fail per
  criterion, reported as rubric pass rate.
- **Multi-round protocol and turn limits.** Unified **SWE-agent-based scaffold**, iterative
  observe–reason–act, three tools (`bash`, `view_xlsx`, `submit`), **maximum 50 interaction
  turns**, identical prompt template across models. Compare SB1's official multi-round protocol,
  which our §8.4 records as capping at five rounds.
- **Difficulty.** Best model **Claude Opus 4.6 at 34.89% overall accuracy**; six of eight models
  below 25%; closed-source 23.68–34.89% vs open-source 7.17–17.14%. **Debugging 12.00%**
  (Opus: 50.38% Modification vs 12.00% Accuracy). Financial Modeling: 89.69% Modification vs
  34.00% Accuracy. Visualization highest at 62.5%. Four commercial products (Kimi Sheet, GLM in
  Excel, Claude for Excel, ChatGPT for Excel) hand-run on 30 examples; best is Claude for Excel at
  **15.4%**, none beating the foundation models under their scaffold. Scaffold comparison on 50
  samples with GLM-5 fixed: their scaffold 46.32 / 15.45, Claude Code 43.47 / 14.20, Cline 41.98 /
  8.66, Kilo 43.12 / 8.66.

### Does anything in SB2 imply a defect in SB1 that bears on our results?

**On the evaluator's false-negative rate: no — and I checked hard.** Full-text grep for "false",
"false negative", "4%", "undercount", "912", "test case", "exact match", "Ma et al." returns
**nothing about SpreadsheetBench 1's audited error rate.** SB2 never discusses SB1's instrument
quality. **Our §2.10 / §8.4 statement of the 4% instruction-level false-negative and 3.8%
test-case-level false-omission rates, sourced to [ma-2024]'s own audit, stands untouched.**

**But SB2 concedes the same class of defect for itself**, A.1(3), verbatim: *"for visualization
tasks, the VLM-as-a-judge framework may introduce evaluation noise despite expert-designed
rubrics; for cell-based tasks, **exact-match evaluation may undercount semantically equivalent but
syntactically different solutions**."* **Useful for us:** the false-negative floor our §8.4 names
is a property of the benchmark family, not a flaw SB1 alone has and the successor fixed. One
sentence in §8.4 saying so makes our concession look measured rather than apologetic.

**On restriction semantics: nothing.** SB2 says nothing about SB1's restricted-range semantics.
*Whether anything changed there is UNVERIFIED.*

**On suitability for agentic multi-turn work: yes, and this is the real bite.** SB2's stated reason
for existing is that SB1 is not workflow-level: *"most existing spreadsheet benchmarks evaluate
isolated operations such as single-formula generation or local cell edits"*, citing Ma et al.
(2024) among them; SB1 *"draws from semi-real forum posts"* and has ~1.4 sheets/file. **That is a
scope criticism of our substrate, from its own authors, published three months before our
submission window.**

It does not invalidate our results. Our dependent variable is the agent's own trajectory length
under a within-task, within-model manipulation with a shared control arm; task realism is not an
input to that contrast. **But it bounds external validity in a way §8.4 should now state
explicitly.** On SB1 our §6.6 records that the median turn at which the best answer is first
reached is 2 and 98.3% of trajectories have peaked by turn 10. SB2 is a regime where frontier
agents are budgeted 50 turns and still fail about two-thirds of tasks. **Our 1.44-turn closing-cue
effect is a large fraction of a short trajectory; whether it is a large fraction of a long one is
untested. (Inference — SB2 makes no claim about closing cues.)**

**Two SB2 findings bear directly on our turn-count framing, and both help us if we use them.**

1. *"Interaction Turns and Effective Step Ratio."* Claude Opus 4.6 beats MiniMax M2.5 on every
   category while *"requir[ing] fewer average interaction steps across four task types, suggesting
   that **increased interaction-step count does not necessarily improve performance** in
   spreadsheet-based tasks."* Defining an effective step as one executed without error, *"Claude
   Opus 4.6 maintains a substantially higher effective-step ratio, confirming that its advantage
   stems from **more reliable per-step execution rather than a larger interaction budget**."* The
   conclusion restates it: *"stronger models benefit from more reliable per-step execution rather
   than larger interaction budgets."*
2. **Failure taxonomy** (six mutually exclusive primary causes, from manual inspection of failed
   Claude Opus 4.6 trajectories): Task Misunderstanding, Insufficient Inspection, Wrong Target
   Selection, **Turn Limit Exceeded**, Format/Output Error, Other. **The dominant two are
   Insufficient Inspection and Wrong Target Selection** — too little looking, not too little
   persisting. Turn Limit Exceeded is a minor category described as "planning inefficiency".
   Supporting: the error-recovery analysis (D.1) finds MiniMax fixes ≥1 error on 72% / 47% / 34%
   of Template / Financial Model / Debugging tasks but passes end-to-end on only 7% / 9% / 3%,
   whereas Opus drops only 50% → 45% on Financial Model.

**This is a genuine qualification of our framing and we should absorb it rather than wait for a
reviewer to serve it.** We do not claim more turns is better — but a reader who sees "persistence"
as the headline outcome may assume we do. SB2 gives us an external, on-substrate result saying
turn count is not a quality measure, from the successor to our own benchmark, run by overlapping
authors. Our accuracy null and their effective-step finding point the same way. **One sentence in
§8.4 or the close: turn count is a behavioural measure of how long the agent stays engaged, and
the benchmark family's own successor reports that longer engagement does not buy correctness.**

### Would re-running on 2 be straightforward, or a different instrument?

**A different instrument. Five reasons, and one genuine opportunity.**

1. Different task population: 321 expert-built multi-sheet business workbooks vs 912
   forum-derived tasks; average instruction 429 words vs 85.7.
2. Different grading: task-level Accuracy requires **every** cell to match, target and non-target.
   Our §8.4 flags that AppWorld would need engineering to separate collateral damage; SB2 folds
   collateral damage into the primary metric by construction. Not better or worse — different.
3. A model judge is back in the loop for Visualization (GLM-4.6V). Our §8.4's stated reason for
   choosing SpreadsheetBench is that *"the grade comes from running the agent's code against real
   test cases, not from a model's judgement."* That reason applies to 297 of 321 SB2 tasks and
   **not** to the 24 visualization ones.
4. Different scaffold expectation: SWE-agent with `bash` / `view_xlsx` / `submit` at 50 turns. Our
   ten-then-twenty ceiling would have to be re-justified — though note this cuts *for* us on the
   existing paper: the successor budgets 50 turns where SB1's protocol caps at five, which
   retrospectively supports our departure from five.
5. Ceiling effects run the other way but not favourably: at 34.89% best-model accuracy, a
   task-level accuracy contrast would be *more* underpowered than ours, not less.

**The opportunity:** the **Modification** metric is a continuous per-task fraction of correct
target cells. That is a far better-powered per-turn regrade outcome than SB1's binary task
accuracy, which §8.4 concedes is pinned at zero for 30 of our 50 tasks. If anyone re-runs §6's
per-turn instrument on SB2, Modification — not Accuracy — is the measure to use. *(Inference; SB2
does not discuss per-turn regrading.)*

**Practical caveat before anyone plans this:** Appendix B.1 states *"For sources with
redistribution restrictions, we release only derived task metadata and evaluation artifacts when
permitted"*, and A.4 releases the dataset CC BY-SA 4.0 with MIT evaluation code. **The public
artifact may therefore not be the complete set of 321 tasks. That is my reading of their wording,
not a statement they make — verify against the release before costing any re-run.**

### Does it support, qualify or undercut the sentence we currently write?

Our §3.8 row and §9 note amount to: *"our substrate has a successor, and a reader should know that
before treating SpreadsheetBench 1 as the current instrument."*

**Accurate, survives, and is much too thin for what the paper contains.** The successor does not
merely exist; it is explicitly framed as a corrective to SB1's scope, it moves the turn ceiling
from five to fifty, it changes the grading criterion to all-cells exact match, it reintroduces a
model judge for one category, and it reports that more turns do not buy correctness. Each of those
touches something our §8.4 already says. **Recommend expanding the §8.4 substrate discussion by a
short paragraph and fixing the truncated author list in §9.**

### Claims of ours it makes newly unsafe

1. **None of our empirical claims.** No result here contradicts any number we report, and it says
   nothing at all about SB1's false-negative rate.
2. **The §9 author list** (seven of fourteen) and the **"NOT read"** tag — both now wrong.
3. **Any unqualified implication that turn count tracks effort-that-pays.** Not a claim we make
   explicitly, but §8.4 should now pre-empt it with SB2's effective-step finding.
4. **§8.4's "a second substrate is the obvious next step"** naming only AppWorld. With a
   same-lineage successor to our own substrate in existence, that sentence should at least
   acknowledge it and say why AppWorld remains the pick (different task family; execution-grounded
   throughout; ~$0.70 per trajectory) rather than leaving the omission to a reviewer.

### Workshop paper or 54-page version?

**Long version for the substance.** The 5-page version does not have room for a substrate-successor
paragraph, and nothing here changes its headline result. The one thing worth considering for the
workshop paper is a four-word parenthetical where the substrate is introduced — "(a successor,
SpreadsheetBench 2, appeared in June 2026)" — as cheap insurance against a reviewer who knows the
benchmark. **If the workshop paper can afford only one new citation from this batch, spend it on
2609.09703, not this.**

---

## 4. Consolidated: what must change

**Must fix — factual.**

1. `paper/03-confound-in-prior-materials.md` §3.8 and `paper/09-references.md`: **strike
   "independently written"** for [zhang-2026-politejudge]. The paper says three paraphrases per
   level; it never says who wrote them or that they were independent.
2. `paper/09-references.md`: [zhang-2026-politejudge] is **not an unrefereed preprint** — accepted
   at RecSys '26, Reproducibility and Practice Notes track, ACM DOI 10.1145/3773078.3841249
   (CrossRef 404 as of 16 Sep 2026; conference 27 Sep–2 Oct 2026).
3. `paper/09-references.md`: [zhu-2026-spreadsheetbench2] author list is truncated at 7 of 14.
   Add Guangyu Robert Yang, Samuel Jacob, Siddharth Nagisetty, Abhiram Chundru, Jean Lin, Spencer
   Mateega, Jing Zhang.
4. `paper/09-references.md`: all three "NOT read" / "not read in full" tags are now false, and the
   "For the remaining six the depth is abstract-only … No claim rests on any of the six"
   bookkeeping paragraph needs rewriting — four of the seven late additions are now read in full.

**Should change — framing.**

5. **§8.7** — rewrite the stimulus-sampling concession around [zhang-2026-politejudge]'s actual
   numbers (btw/in below 1 for five of eight judges; one anomalous paraphrase moving κ by 0.18),
   crediting them as having run the controlled version first in a single-turn setting, while
   stating plainly that this does not discharge our gap in the agentic setting.
6. **§3** — add their L1 wrapper (*"Score this passage. Don't waste my time with explanations."*)
   and their own limitation (*"tone is not perfectly isolated from instruction content"*) as a
   fresh, author-admitted instance of the demand/register confound.
7. **§1.1 / §3.6 / §4** — narrow any claim that the tone literature offers no mechanism. They
   propose one and use it to reconcile Yin et al. 2024 against Dobariya & Kumar 2025 — our own
   pair.
8. **§8.8** — expand the negotiation paragraph using TERMS-Bench's actual architecture: the voice
   layer is severable from the economic kernel, τ_terminal and AgentExit⁻ already instrument
   termination, closing round is already reported against K ≈ 10, the cue penalty (α_cue < 0 for
   all 13 agents; *"warm cues induce over-concession"*) is the nearest existing analogue to our
   praise arm, and Appendix B.4 names an orthogonal communication-level manipulation as the
   authors' own future work. Keep the "untested **here**" scoping: it is what makes the sentence
   safe.
9. **§8.4** — add SB2: what changed (workflow-level tasks, 50-turn ceiling, all-cells exact match,
   VLM judge for visualization, 34.89% best accuracy), that it says nothing about SB1's
   false-negative rate while conceding the same class of issue for itself, that its effective-step
   finding says more turns do not buy correctness, and that re-running on it is a new instrument
   rather than a replication — with Modification as the metric a per-turn regrade would want.

**Must not claim.**

10. Not that [zhang-2026-politejudge] ran our experiment. They ran a stimulus-sampled *judging*
    study, not a stimulus-sampled *agentic* study.
11. Not that their U-shaped tone result confirms our "register acts in one direction only". It is
    a different dependent variable in a different paradigm; the resonance is an analogy and should
    be labelled as one.
12. Not that counterpart register is untested anywhere. It is partly tested in TERMS-Bench Finding
    2 — confounded with cue informativeness, which is a point *for* us and should be said, not a
    point to hide.
13. Not that SpreadsheetBench 2 revises, corrects or supersedes SpreadsheetBench 1's audited
    false-negative rate. It is silent on it.

## 5. Placement summary

| Paper | 5-page workshop | 54-page version |
|---|---|---|
| 2609.09703 | **Yes — one sentence.** The only one of the three that earns space: pre-empts the one-stimulus objection and externally supports the accuracy null. | Paragraph in §3; rewrite of §8.7. |
| 2605.13909 | No. | §8.8 expanded from one sentence to three or four. |
| 2606.29955 | Optional four-word parenthetical at the substrate mention; skip if space is tight. | Paragraph in §8.4; author list and read-depth fixes in §9. |
