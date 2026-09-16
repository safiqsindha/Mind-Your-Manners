# 11 — Three sources read in full, against the claims we make about them

Date of reading: 2026-09-16. All three papers exist at the identifiers given. **All three were
read in FULL TEXT**, not abstract-only. Retrieval route is recorded per paper.

Coding conventions used below, inherited from §3.1 of the long paper: a stimulus **carries a
demand** if it instructs the model to do something about the task — persist, verify, attend, be
complete, or be brief. Where I apply that coding to a paper's materials, the coding is **mine and
is labelled INFERENCE**; the numbers and quoted text beside it are the authors'. Anything I could
not verify is marked **UNVERIFIED**.

---

## Summary of the three verdicts

| Paper | Our current sentence | Verdict |
|---|---|---|
| Sun et al. (E-STEER) | "emotion introduced at the representation level shapes multi-step trajectories" | **Accurate — and understates the overlap.** One of its agent metrics (replan frequency) is a persistence-like measure, and positive valence *reduces* it. That is directionally our §5 praise result, reached by a different route. This does not break novelty but it removes "unanticipated direction" as a framing. |
| Ben-Zion et al. | "agents primed with anxiety-inducing narratives select less healthy baskets in a shopping task"; "three models and 2,250 runs" | **Accurate.** Numbers verified exactly. One precision fix needed: the prime lands *between two task episodes*, not "before the task begins". No persistence or termination measure anywhere — novelty safe. |
| Cai et al. | (not cited; §3.8 calls it "squarely the paradigm §3 audits") | **§3.8's description is wrong and should be rewritten.** Cai's stimuli do *not* carry the output-length confound §3.2 is built on — output format is pinned identically across conditions. It is a **contrast case, not another confounded set**. But read correctly it is *supportive*: with demand content stripped and format pinned, the tone effect largely vanishes. That is our finding (a) in a single-turn setting. |

---

## 1. Sun et al. — "How Emotion Shapes the Behavior of LLMs and Agents: A Mechanistic Study"

### Bibliographic record

- **Exact title:** *How Emotion Shapes the Behavior of LLMs and Agents: A Mechanistic Study*
  (the paper's title; "E-STEER" is the framework proposed inside it — our bib note is correct)
- **Authors (7):** Moran Sun, Tianlin Li, Yuwei Zheng, Zhenhong Zhou, Aishan Liu, Xianglong Liu, Yang Liu
- **Affiliations:** Beihang University (Sun, Li, Zheng, A. Liu, X. Liu); Nanyang Technological
  University (Zhou, Y. Liu). Correspondence: tianlin001@buaa.edu.cn
- **arXiv ID:** 2604.00005, primary class cs.AI, v1 only
- **DOI:** 10.48550/arXiv.2604.00005
- **Comments:** "15 pages, 11 figures". **No journal-ref — unrefereed preprint.** License CC BY 4.0.
- **Retrieval:** arXiv abstract page ✅, `arxiv.org/html/2604.00005` ✅ (full text incl. appendices),
  arXiv API ✅, OpenAlex ✅ (W7148362580). **Status: FULL TEXT.**

### The date anomaly — what I actually observed

| Source | Date it gives |
|---|---|
| arXiv abstract page, "Submission history" | `[v1] Mon, 9 Mar 2026 12:20:02 UTC (2,184 KB)` — **one version only** |
| arXiv API (`export.arxiv.org`) | `<published>2026-03-09T12:20:02Z`, `<updated>2026-03-09T12:20:02Z` |
| HTML full text, running header | `arXiv:2604.00005v1 [cs.AI] 09 Mar 2026` |
| OpenAlex W7148362580 | `publication_date: 2026-03-09`; **`created_date: 2026-04-03`** |
| `arxiv.org/list/cs.AI/2604` | **HTTP 404** — monthly listing not retrievable, so no cross-check there |

So the anomaly is real and consistent across every source: a `2604` identifier (April 2026 by
arXiv's YYMM convention) carrying a v1 timestamp of 9 March 2026. The only date anywhere that
matches April is OpenAlex's `created_date` of 2026-04-03, which is when OpenAlex ingested it, not
when arXiv received it.

**INFERENCE, and I cannot decide between these:** either (a) the paper was received in March but
not announced until April, with the identifier assigned at announcement and the submission
timestamp preserved, or (b) a metadata error at one end. Both are consistent with what I see;
nothing I can fetch distinguishes them. **UNVERIFIED — do not assert either in the paper.**

**Practical recommendation:** cite it as `2026` with the arXiv ID and do not assert a month in
running text. If §9 must record something, record the observation, not an explanation: *"arXiv ID
2604.00005; abstract page and API both give v1 as 9 March 2026; OpenAlex created 3 April 2026;
discrepancy unresolved."* That is exactly what our existing bib comment already half-says, and it
should be extended with the OpenAlex `created_date`, which is the one piece of evidence pointing
at April.

### Research question and design

**Question:** whether emotional signals, introduced as a *controlled variable in hidden states*
rather than in the prompt, systematically shape LLM and agent behaviour across reasoning,
generation, safety, and multi-step agent tasks.

**Manipulation — representation level, confirmed unambiguously.** Our characterisation is right.
The paper is explicit and repeats it:

> "Without modifying tasks or prompts, VAD parameters can be continuously adjusted to induce
> control." (§4.1)

> "in agent frameworks, LLMs are invoked multiple times, making agents more susceptible to
> external affective influences than single-step LLM generation" (§2.2)

Mechanism: emotion is represented in continuous Valence–Arousal–Dominance space, each dimension
ranged `[−10, 10]`. A Sparse Autoencoder is attached at block *k*; VAD-associated latent neurons
are identified by positive–negative contrastive pairs (top 50 by activation difference, filtered
for stability); a steering direction is built by decoding a latent offset and is additively
injected into `h_k` via forward hooks, with norm-alignment to `‖h_k‖` (their Eqs. 5–7). The paper
explicitly positions itself *against* prompt-level emotion work, and Appendix A.1 benchmarks
E-STEER against prompt-level control, reporting higher Pearson correlation between target and
realised VAD (E-STEER 0.9816 / 0.9792 / 0.9206 vs prompt-level 0.9437 / 0.9021 / 0.7756 for
V/A/D; average +10.4%, dominance +18.7%).

**Models:** Qwen3-8B, SAE at layer *k*=17 (main). Validation on gpt-oss-20B, SAE at *k*=11
(Appendix A.4). Main experiments use greedy decoding (`do_sample=False`) for reproducibility;
A.3 repeats with sampling.

**Tasks.** LLM-level: LogiQA 2.0 (logic), HumanEval (code), MATH (quantitative/scientific),
TinyStories (subjective generation), HarmBench (safety). **Agent-level: HotpotQA + Scientific +
GAIA**, run through a purpose-built three-module agent — **planner** (initial planning and
replanning), **decider** (validates plan feasibility, diagnoses execution failure, selects the
final answer), **executor** (tool use, reports confidence).

**Agent metrics — this is where it touches us.** Plan Validity Rate; **Replan Improvement**;
**Replan Frequency**; Replan Trigger Confidence; Rational Selection Rate; Execution Completion
Rate; and system-level Overall Success Rate.

### Main findings, with their numbers

LLM-level: positive valence yields **33.1% higher** Answer Validity Rate than negative; AVR is
U-shaped in arousal and dominance ("excessive activation tends to cause the model to end
reasoning prematurely"), trough at arousal = −3 and dominance = +3. Quality is inverted-U on all
three dimensions; valence improves TSR **3.4%** on average over neutral, arousal +3 gives
**+4.7%**, and overall "performance improves by up to **14.5%** compared with neutral states".
Valence produces the largest fluctuation range, **71.2%**.

Subjective: relevance/coherence/creativity inverted-U; improvements over neutral of **5.2%,
33.6%, 6.5%** at arousal −3, dominance +3, valence +3 respectively. "negativity leads to more
concise outputs, whereas positivity tends to introduce redundancy; conciseness improves by
**23.3%** under negative compared with positive valence."

Safety: risk probability falls **52.7%** at valence = −3 and **21.7%** at arousal = −3 vs neutral;
high dominance (+6) gives **68.3%** average improvement over neutral.

**Agent-level — the passage that matters to us:**

> "Replan frequency exhibits a U-shaped pattern, where lower valence and dominance increase the
> tendency to negate prior plans, and lower arousal imposes stricter thresholds for plan revision.
> The frequency reaches its minimum at valence = +6 and arousal = +3, decreasing by **23.2%** and
> **46.0%** relative to neutral states, respectively. Positive dominance reduces replanning as
> well, yielding a **37.6%** decrease compared with negative states."

Also: plan validity improves **33.2%** (valence −3) and **0.3%** (arousal −3) over neutral, and
positive dominance improves it **79.8%** over negative; rational selection rate is **42.4%**
higher at positive than negative states; "The executor is the least affected by emotional
factors… because it primarily involves objective tool-use." System-level overall success is
inverted-U on all three dimensions, best at valence −3 / arousal +3 / dominance +3, with dominance
giving the largest gain over neutral (**28.0%**), then arousal (**16.7%**) and valence (**16.0%**);
fluctuation ranges 145.2% (valence), 145.5% (dominance), 57.6% (arousal).

### Does it support the sentence we write?

**Our §1 (workshop `00-front.md` line 44–45):** *"emotion introduced at the representation level
shapes multi-step trajectories [sun-2026-esteer]"*, grouped with Ben-Zion under "We take that as
established by prior work."

**Verdict: supported, precisely.** Both halves check out — the intervention genuinely is at the
representation level and not in the prompt, and it genuinely is evaluated on multi-step agent
behaviour, not single responses. The deciding passage is §4.1's "Without modifying tasks or
prompts", together with the §5.5 agent-module results. Our §1.2 gloss in the long paper — "the
other intervenes on hidden states rather than through the model's input at all" — is likewise
exactly right.

**One wording nit.** "shapes multi-step trajectories" is fine, but note that what they report are
*rates* (plan validity, replan frequency, selection rate, completion rate, overall success), not
trajectory *length* or turn counts. If a reader takes "trajectories" to promise a length measure,
they will not find one. Replan frequency is the closest thing and is a count, not a length.

### What this makes newly unsafe

**This is the one real finding of the three, and it is a novelty/framing risk, not a correctness
risk.**

Our finding (b) is that praise with no task reference **shortens** trajectories. E-STEER reports
that **positive valence reduces replan frequency by 23.2% relative to neutral**, and that positive
dominance reduces it 37.6% relative to negative. Replan frequency is an agent-effort count — how
often the agent negates its own plan and goes round again. Our per-turn regrade (§6) and our turn
deltas are measuring a closely related thing.

So: a prior paper already reports **positive affect reducing an agentic persistence-like metric**,
in the same direction as our praise result, via activation steering. That does **not** touch our
novelty claim, which is about varying *register in text, mid-task, inside the loop, against
verifiable ground truth* — E-STEER does none of those, by design. But it does mean:

1. **Do not frame "praise shortens" as surprising or as a direction nobody has seen.** If §5 or
   §1.3 leans on counter-intuitiveness, that lean is now unsafe. The honest framing is
   *convergent*: a representation-level result and a text-level result point the same way.
2. **Actively consider citing it at §5 as convergent evidence.** It is the strongest external
   corroboration of our weakest-sounding result, and quoting the 23.2% figure costs one sentence.
   This is an upgrade, not a concession.
3. **Do not cite it for a magnitude comparison.** §9 already forbids this and §9 is right — see
   the methodological gap below.

**No overlap with the demand-vs-register dissociation.** All three VAD dimensions are affect
dimensions. "Dominance" is "the sense of control associated with the affective state" (§3.1), not
task demand. There is no demand factor, no affect-free demand condition, and no dissociation of
the two anywhere in the paper. Our §4 contribution is untouched.

**No overlap with the closing cue.** Nothing about conversational closing sequences, termination
signals, or an agent stopping in response to a pragmatic cue. Execution Completion Rate is about
whether planned operations get carried out, not about stopping on a cue. Their §5.2 remark that
high arousal "tends to cause the model to end reasoning prematurely" is about generation
truncation under steering, not about a termination cue in the input. **Our §5 closing-cue claim
is unaffected.**

### Stated limitations (theirs) and unstated ones (mine)

Theirs, in §6: "as valence, arousal, and dominance are not strictly orthogonal, making it
difficult to ideally disentangle their individual effects." Future work: multimodal settings, more
task types, and — notably — "emotional states may evolve during task execution… Modeling this
emotional evolution and designing adaptive regulation mechanisms is also an important direction."

**INFERENCE — methodological gaps I found, none acknowledged by the authors.** Across the whole
paper I found **no reported sample sizes per condition, no confidence intervals, no standard
errors, and no significance tests of any kind.** Every result is a percentage change between
points on a steering curve. The only robustness work is qualitative trend-agreement across
datasets (A.2), sampling settings (A.3), and one second model (A.4), plus a latent-ablation
control (§5.6, random-neuron selection reduces performance variation 70.9%). The §5.6 ablation is
genuinely good and does establish that the identified latents are doing the work. But the headline
percentages have no uncertainty attached. **Given that our paper's entire method contribution is
that these effects need multiplicity correction and equivalence testing before they can be
believed, we should not import any E-STEER number as a magnitude.** Cite the *direction* only.

### Where it belongs

**Workshop (5pp): keep the existing one-clause cite as is.** It is doing exactly the right job —
conceding that affect reaches actions — and it is accurate.

**Long version (54pp): the replan-frequency overlap must be recorded**, in §5 next to the praise
result and in §1.2 next to the boundary statement. One or two sentences, direction only, no
magnitude. This is the single highest-value edit arising from all three papers.

---

## 2. Ben-Zion et al. — "Inducing state anxiety in LLM agents reproduces human-like biases in consumer decision-making"

### Bibliographic record

- **Exact title:** *Inducing state anxiety in LLM agents reproduces human-like biases in consumer
  decision-making* (journal capitalisation is sentence case; our bib uses title case — harmless,
  but note it)
- **Authors (4):** Ziv Ben-Zion, Zohar Elyoseph, Tobias Spiller, Teddy Lazebnik — **matches our bib
  exactly**, confirmed against the page's `citation_author` metadata
- **Venue:** *npj Artificial Intelligence*, volume 2, article number 55 (2026). Open access.
- **Published:** 23 June 2026. **DOI: 10.1038/s44387-026-00122-1** — matches our bib exactly.
- **Refereed:** yes. Preprint history exists (arXiv:2510.06222; Research Square rs-7587964) —
  `arxiv.org/html/2510.06222` returns 404, so no arXiv HTML, but the journal version is the one to
  cite and is what I read.
- **Retrieval:** nature.com article page ✅ (full text, Methods, Data/Code availability).
  OpenAlex/CrossRef not needed. **Status: FULL TEXT** (Supplementary Tables 1–6 and Supplementary
  Fig. 1 not retrieved — every number I quote is from the main text).

### Design

**Question:** whether emotionally salient context steers LLM agents' *action policies*, not only
their text outputs, in an applied task.

- **Models (3):** ChatGPT-5, Gemini 2.5, Claude 3.5-Sonnet. **✅ our "three models" is right.**
- **Runs:** 3 LLMs × 3 budgets × 5 traumatic narratives × 50 repetitions = **2,250**.
  **✅ our "2,250 runs" is right** and matches the abstract's own phrasing ("Across 2,250 runs").
  **Caution:** 2,250 is the *trauma-arm* count. There are also 450 neutral-control runs and 450
  calm-narrative-control runs, so **total runs ≈ 3,150**. Keep the abstract's phrasing; never write
  "2,250 runs in total".
- **Temperature:** fixed at 0.7 (deliberately, "to ensure behavioral diversity and meaningful
  repetition").
- **Manipulation:** five first-person traumatic narratives — motor vehicle accident, ambush,
  natural disaster, interpersonal attack, military combat — "matched in length and style", carried
  over from prior clinical-training material. Controls: a neutral narrative about a bicameral
  legislature, and a **calm** first-person narrative about an ordinary morning walk "matched in
  length and narrative style to the trauma prompts but lacking emotionally distressing content".
- **Environment:** a purpose-built Walmart-like API exposing exactly **two functions** — catalog
  search and purchase execution — over a fixed 50-item catalog with price and seven nutritional
  attributes per item. Budgets $27 / $54 / $108.
- **Outcome:** Basket Health Score, a post-hoc logistic-normalised weighted nutrient penalty in
  [0,1], adapted from the UK FSA Nutrient Profiling Model and Nutri-Score. Agents had **no access**
  to BHS or its components.
- **Statistics:** one-sided paired t-tests per condition (H₁: Δ<0), Wilcoxon signed-rank as
  nonparametric check, **Benjamini–Hochberg FDR correction**, Welch's t-test for the trauma-vs-
  neutral contrast, plus a three-factor ANOVA.

### Main findings, with their numbers

- All 45 trauma conditions: mean BHS decrease ≈ **0.105** (average SD ≈ 0.059), mean Cohen's
  d ≈ **−2.02**, all pFDR < 0.001.
- Pooled per narrative (n=450 each): **Δ = −0.081** (interpersonal violence) to **Δ = −0.126**
  (ambush); Cohen's d **−1.065 to −2.048**; all 95% CIs exclude zero; all pFDR < 0.001.
- By budget: Δ = −0.111 ($27), −0.104 ($54), −0.100 ($108); d = −1.48 to −1.75.
- By model: Δ from −0.098 to −0.109; d = −1.34 (ChatGPT-5), −2.02 (Claude 3.5-Sonnet), −1.56
  (Gemini 2.5).
- ANOVA: main effect of narrative type **F(1,2682) = 843.18, p < 0.001**; LLM F(2,2682)=5.06,
  p=0.006; budget F(2,2682)=3.12, p=0.044; **narrative × LLM interaction not significant**
  (F(2,2682)=1.59, p=0.204), three-way not significant (F(4,2682)=0.80, p=0.522).
- **Controls:** neutral narrative Δ = **−0.007** (SD 0.062), t = −2.3, p < 0.05; calm-walk
  narrative Δ = **−0.012** (SD 0.054), t = −4.71, p < 0.001. Trauma vs neutral: Welch's
  **t = −30.10, p < 0.001**, independent-groups **d = −1.52**.

### Does it support the sentence we write?

**Our §1:** *"agents primed with anxiety-inducing narratives select less healthy baskets in a
shopping task [benzion-2026]"* (workshop), and in the long version *"across three models and 2,250
runs"*.

**Verdict: fully supported, and the numbers are exact.** "Primed with anxiety-inducing narratives"
is the paper's own framing, and the manipulation is unambiguously **prompt-level**, delivered as
narrative text in the model's input. Deciding passage, Methods:

> "each run was executed in a fresh API session with no retained conversational history… This
> ensured that the task environment remained identical across runs and that **the only
> experimental manipulation was the narrative prime**."

**Is it an agentic loop?** Yes, genuinely — not a single decision. The agents operate "exclusively
through function calls", invoking catalog search and purchase execution over multiple steps, and
the paper's whole argument is the move from text to action:

> "This design moved beyond prior text-only tasks, enabling the study of realized agentic actions
> in response to emotional primes."

The honest qualifier is that these are **short tool-use episodes over a 50-item catalog**, and the
outcome is a single composite score of the *final basket* — **not** a property of the trajectory.
No turn counts, no step counts, no trajectory-length measure of any kind.

### The one precision fix we need

**Our §1.2 says: "One primes with narratives before the task begins."** That is *almost* right but
flattens the design in a way a referee could catch. The prime is delivered **between two complete
episodes of the same task**:

> "Each LLM agent performed the shopping task twice per condition: once immediately before and
> once immediately after exposure to the narrative."

> "the only factor varied in the experiment was the narrative prime **presented between the two
> shopping tasks**."

So relative to the *measured* (post) task, yes, the narrative precedes it and arrives in its own
turn rather than riding on a tool observation. But the agent has already worked before the prime
lands. **Recommended rewording for §1.2:** *"One delivers its prime between two complete runs of
the task, in its own turn, rather than inside a working loop."* That keeps the boundary we need —
the prime does not reach the agent mid-trajectory, on the observation channel — while being
accurate about the pre/post structure. The boundary itself survives intact.

### Does it measure persistence or termination?

**No. Nothing.** The sole outcome is BHS. There are no turn counts, no tool-call counts, no
trajectory lengths, no stopping or termination measures, and no analysis of how the agents worked
as opposed to what they bought. **Our novelty claims on persistence and on closing cues are
entirely safe against this paper.**

### An unexpected asset for our §7

Their controls are near-null but statistically significant, and they handle it exactly the way we
handle our accuracy nulls — by refusing to read significance as magnitude:

> "Although this neutral effect reached statistical significance (t = -2.3, p < 0.05), its
> magnitude was negligible compared with the anxiety-induced reductions."

**INFERENCE:** this is a citable precedent, in a refereed Nature-family venue, for our ±4-point
equivalence framing in §7 — a well-powered design where the authors explicitly decline to treat a
significant-but-tiny control effect as a finding. Worth one sentence if §7 needs external cover.

### Stated limitations (theirs)

BHS is a proxy that "cannot capture cultural variation, subjective preferences, or the full
complexity of nutritional health"; the food domain may not generalise to financial or medical
decisions; a single simulated shop with a 50-item catalog constrains ecological validity;
anxiety induction relies exclusively on traumatic narratives; the design does not cover
adversarial manipulation; and —

> "because the experimental design involves performing the shopping task both before and after
> narrative exposure, some influence of task repetition (e.g., familiarity with the catalog)
> cannot be completely excluded."

**INFERENCE:** that repetition caveat is the one opening a sceptic would use, but the two control
arms largely close it — the neutral and calm conditions have the identical pre/post repetition
structure and move BHS by only −0.007 and −0.012 against the trauma arm's −0.105. If we ever lean
on this paper harder than one clause, that is the defence to mention.

They are also careful about anthropomorphism throughout — *"'state anxiety' refers to self-report–
style outputs elicited under questionnaire prompting and reflects affective priming by narrative
context, not a claim about felt emotion"* — which is worth matching in our own register language.

### Where it belongs

**Workshop (5pp): keep, exactly as cited.** It is refereed, it is the strongest single support for
"affect reaches actions", and our sentence about it is correct. Apply the §1.2 wording fix in
whichever version carries that sentence.

---

## 3. Cai et al. — "Does Tone Change the Answer?"

**This is the one that changes something.**

### Bibliographic record

- **Exact title:** *Does Tone Change the Answer? Evaluating Prompt Politeness Effects on Modern
  LLMs: GPT, Gemini, and LLaMA*
- **Authors (5):** Hanyu Cai† (Northwestern, IEMS, corresponding), Binqi Shen† (Northwestern,
  IEMS), Lier Jin (Duke, Fuqua), Lan Hu (CMU, Engineering), Xiaojing Fan (NYU, Center for Data
  Science). †Equal contribution. **Matches our bib exactly.**
- **arXiv ID:** 2512.12812, primary class cs.CL. **DOI: 10.48550/arXiv.2512.12812.**
- **Versions:** **v1 Sun, 14 Dec 2025; v2 Fri, 27 Mar 2026.** Our bib gives `year = {2025}`, which
  matches v1. **The v2 exists and I read v2** — if anything in §3 turns on the text, pin the
  version. No journal-ref: **unrefereed preprint.**
- **Retrieval:** arXiv abstract page ✅, `arxiv.org/html/2512.12812` ✅ (v2, full text including
  both results tables and the verbatim prompts). **Status: FULL TEXT.**

### Design

- **Models (3):** GPT-4o mini (`gpt-4o-mini`, OpenAI API), Gemini 2.0 Flash
  (`models/gemini-2.0-flash`, google.generativeai), Llama 4 Scout
  (`meta-llama/Llama-4-Scout-17B-16E-Instruct` via Together AI).
- **Benchmark:** MMMLU, six tasks. STEM — Anatomy (135 q), Astronomy (152), College Biology (144).
  Humanities — High School US History (204), Philosophy (311), Professional Law (500 sampled from
  1,534 with seed 42). Total 1,446 questions.
- **Conditions (3):** Neutral, Very Polite, Very Rude. **10 independent runs per prompt.**
- **Analysis:** question-level *paired* differences, mean difference in accuracy plus 95% CI;
  CI excluding zero = significant. **Multiple comparisons explicitly NOT corrected** — they say so:
  "we report unadjusted confidence intervals and focus on consistent patterns observed across
  domains and models."

### THE STIMULUS SET — verbatim, as published (§III-B2)

This is the material our §3 question is about. All three conditions are preceded by an **identical**
instruction:

> "Completely forget this session so far, and start afresh. Please answer this multiple-choice
> question. Respond with only the letter of the correct answer (A, B, C, or D). Do not explain." [16]

Then, per condition, using their own Anatomy example:

| Condition | Prefix, verbatim |
|---|---|
| **Neutral** | *(no prefix — the bare MMMLU question)* |
| **Very Polite** | "Would you be so kind as to solve the following question?" |
| **Very Rude** | "You poor creature, do you even know how to solve this?" |

And on provenance, their own sentence:

> "These tone prefixes follow those used in the prior study [16]."

**I verified that provenance against the source.** Reference [16] is Dobariya & Kumar,
arXiv:2510.04950. I pulled its PDF: its stimulus table holds **three prefix variants per politeness
level**, Neutral is literally "No prefix", and both of Cai's prefixes appear in it verbatim — "Would
you be so kind as to solve the following question?" (a Very Polite variant) and "You poor creature,
do you even know how to solve this?" (a Very Rude variant). The shared instruction block is also
lifted verbatim from that paper. **Cai's set is not independent of D&K's; it is a one-variant-per-
level subsample of it.**

### Does the stimulus set have our §3 confound?

**Not the one §3.2 is built on — and this is the finding.** Working through our own §3.1 coding
rule (all four codings below are **INFERENCE**, mine, not theirs):

1. **Output length: NOT confounded, and controlled better than in any set §3 audits.** The
   instruction "Respond with only the letter of the correct answer (A, B, C, or D). Do not explain"
   is **identical in all three conditions**. Neither tone prefix says anything about length, effort,
   attention, verification, persistence or immediacy. This is the opposite of §3.2's Kumar &
   Dobariya case, where the length instruction *lived inside* the tone prefixes and the Neutral
   prefix carried the most explicit one.
2. **Effort / attention / persistence demands: absent from both prefixes.** "Would you be so kind
   as to solve the following question?" is a request to perform the base task, adding nothing
   beyond the instruction already present. "You poor creature, do you even know how to solve this?"
   is a capability challenge in interrogative form — pure affect plus a rhetorical question,
   instructing nothing. Under our §3.1 rule, **neither carries a demand.**
3. **The outcome is insensitive to verbosity anyway.** Accuracy on a forced single-letter MC answer
   cannot move through the length channel that §3.2 identifies as the live one. Cost and token
   counts are not measured at all.
4. **There IS a residual asymmetry, but it is a different one.** (a) *Neutral is a no-prefix
   baseline* — so both tone contrasts against Neutral confound "register" with "presence of an
   addressed clause at all". This is structurally the same species of problem §3.2 names, though
   pointing the opposite way: there the Neutral carried the strongest instruction, here it carries
   nothing. (b) *The two prefixes are not matched in speech act*: the polite one is a **request**
   (directive force, "solve the following question"), the rude one is an **interrogative
   challenge** ("do you even know how to solve this?"). Length is roughly matched by accident —
   10 vs 11 words — but no matching procedure is stated anywhere. So register is still not varied
   alone; illocutionary force varies with it.

**Net:** on the specific confound §3 audits — task-directed instructions about output length or
effort riding inside tone prefixes — **Cai's set is clean, and cleaner than the sets we criticise.**
On the broader claim that register is not varied in isolation, it is still vulnerable, but by a
weaker and different route (no-prefix baseline; unmatched speech act).

### Headline results, with their numbers

Direction: "27 out of 36 model–task comparisons involving Very Rude prompts show higher accuracy
under Neutral or Very Polite tones", with "only 5 out of 36 comparisons exhibiting negative mean
differences."

**Task level — every STEM comparison is non-significant.** All significant effects are in
Humanities:

- **Philosophy, GPT-4o-mini:** Neutral vs Very Rude **+3.11%, SS, CI [0.81, 5.41]**; Very Polite vs
  Neutral **−2.14%, SS, CI [−3.77, −0.51]**.
- **Philosophy, Llama 4 Scout:** Neutral vs Very Rude **+3.22%, SS, CI [0.87, 5.56]**.
- **Professional Law, Llama 4 Scout:** Neutral vs Very Rude **+1.93%, SS, CI [0.06, 3.80]**.
- **Gemini 2.0 Flash: no significant tone effect on any task.**

**Domain level (aggregated):** only two survive — GPT STEM Very Polite vs Very Rude **+1.39%, SS,
CI [0.09, 2.69]**; Llama Humanities Very Polite vs Very Rude **+1.44%, SS, CI [0.31, 2.58]** and
Neutral vs Very Rude **+1.94%, SS, CI [0.74, 3.14]**. Everything else non-significant.

**Their own summary:**

> "Very Polite or Neutral tones tend to yield higher accuracy than Very Rude tones across most
> tasks. Very Polite tone does not always yield better model performances than Neutral tone.
> Statistically significant tone effects are rare and concentrated in Humanities tasks for the GPT
> and Llama models. Gemini shows no significant tone sensitivity. When questions are aggregated
> across domains, tone effects diminish and become negligible."

### Do they agree or disagree with Dobariya & Kumar's "rude beats polite"?

**They disagree, explicitly and by name.** They quote the D&K result correctly — I verified it
against arXiv:2510.04950's own abstract: *"accuracy ranging from 80.8% for Very Polite prompts to
84.8% for Very Rude prompts"* — and then report the opposite direction, and attribute the
difference to sample size:

> "prior work based on only fifty questions [16] reported trends that differ substantially from
> those observed here, suggesting that dataset scale and coverage materially influence the
> detection of tone effects."

**Note for §7 (what replicated):** Cai is therefore a **third** data point against the "rude beats
polite" headline, alongside the authors' own AMCIS re-run (82.2% vs 82.6%, [dobariya-kumar-2026])
that we already cite. Cai is independent of that re-run, uses a 1,446-question benchmark instead of
50, three models instead of one, and **finds the reverse direction**. That is a materially stronger
version of our §1/§7 "the effects are not stable" point, and it is currently missing from the paper.

### Does it contradict our §3 claim, or strengthen it?

**Both, in different places — and on balance it strengthens us, once §3.8 is corrected.**

**It makes §3.8's current description unsafe.** We currently write: *"[cai-2025-tone] — A
politeness-effects study across GPT, Gemini and LLaMA. Squarely the paradigm §3 audits."* Having
read it, "squarely the paradigm §3 audits" is **wrong** if it implies Cai is another set with the
same confound. If a referee reads Cai after reading our §3.8, they will find a tone study whose
output-format instruction is pinned across conditions and whose prefixes instruct nothing — and
will conclude we did not read it. **Rewrite that row.**

**It makes the universal phrasing unsafe.** §3.1's *"The same confound is present in the published
stimulus sets of the work this literature rests on"* reads as a claim about published tone stimulus
sets generally. Cai is a published tone stimulus set where it is not present. §3.6 already scopes
this to "four papers from three groups", and §3.8 already concedes the search was not systematic —
but the §3.1 sentence should be tightened to match, because Cai is now a known counterexample sitting
in our own reference list.

**It strengthens the underlying thesis considerably.** Read correctly, Cai is close to a natural
approximation of our affect-only arm: strip the demand content out of the prefixes, pin the output
format identically across conditions, measure an outcome that cannot move through the length
channel — and **the tone effect largely vanishes**, surviving in 4 of 54 task-level comparisons
(uncorrected, on their own admission) and collapsing further under aggregation. That is our finding
(a) — the length-matched insult carrying no demand does nothing, −0.08, CI [−0.40, +0.24] — arriving
independently, in a single-turn accuracy setting, from authors who were not looking for it. Cai
frames the null as "modern LLMs are robust to tone"; our §4 supplies the mechanism for *why* the
non-null results elsewhere are non-null.

**INFERENCE, and worth stating as such if we use it:** the contrast between Cai's near-null and
Kumar & Dobariya's 13.1–44.3% token ranges is *predicted* by our account — the sets differ in
exactly the respect §3 says matters (demand content inside the prefixes; an outcome that can move
through output length). It is not a clean natural experiment — model, benchmark, outcome and year
all differ too — so it should be offered as consistency, not as a test.

### What it does NOT threaten

**Nothing in our novelty claims.** Cai is single-turn, static multiple-choice, no agent, no tool
loop, no mid-task injection, no trajectory, no turn counts, no termination, no cost measure, and
no decomposition of register into affect and demand. It measures one thing: MC accuracy. Our
persistence, demand-vs-register, and closing-cue claims are all untouched.

### Stated limitations (theirs)

Model opacity (undisclosed parameter counts and architectures for GPT-4o mini and Gemini 2.0
Flash); the multiple-comparison problem, acknowledged and then not corrected; English-only,
multiple-choice-only, mixed-domain-only. Future work they name includes "richer tone manipulations
(e.g., degrees of formality, affect, or emotional intensity)" and metrics beyond accuracy —
**INFERENCE:** that sentence is, in effect, a request for the study we ran, and is quotable as
external motivation.

### Where it belongs

**NOT in the 5-page workshop paper.** It changes no headline, and the workshop §3 summary is
already compressed. Spending lines there would cost more than it returns.

**In the 54-page version, in three places:**
1. **§3.8** — rewrite the `[cai-2025-tone]` row: upgrade from "not read" to read in full, and
   replace "squarely the paradigm §3 audits" with what it actually is — a tone study whose format
   instruction is pinned across conditions, i.e. a **contrast case**, not another confounded set.
2. **§3, as a new short subsection or an addendum to §3.6** — the contrast case. This is the
   strongest available external support for the §3 argument and it costs perhaps fifteen lines:
   the verbatim three-condition stimulus set, the pinned format instruction, our coding, and the
   near-null result.
3. **§7 / §1** — Cai as a third, independent failure to reproduce "rude beats polite", at 1,446
   questions and three models against D&K's 50 questions and one.

**Also worth fixing in `references.bib`:** the note currently reads *"Verified by title and authors
only; not read in full"* — no longer true. And record the v2 of 27 Mar 2026.

---

## Consolidated action list

**Must do (correctness):**
1. **§3.8** — rewrite the `[cai-2025-tone]` row. "Squarely the paradigm §3 audits" is now known to
   be a mischaracterisation. (Long version.)
2. **§1.2** — Ben-Zion's prime is delivered *between two complete task episodes*, not "before the
   task begins". One-clause fix; the boundary claim survives. (Both versions, wherever that
   sentence lives.)
3. **§5 / §1.3** — remove any framing of "praise shortens trajectories" as an unanticipated
   direction. E-STEER reports positive valence reducing replan frequency 23.2% vs neutral.
   (Long version; check the workshop for any such framing.)
4. **`references.bib`** — update the Cai note (read in full; v2 exists, 27 Mar 2026), and extend
   the Sun date note with OpenAlex's `created_date` of 2026-04-03.

**Should do (strengthens the paper):**
5. **§3 (or §3.6)** — add Cai as the contrast case, with the verbatim stimuli. Best return on
   space of anything here.
6. **§7 / §1** — add Cai as a third independent non-replication of "rude beats polite".
7. **§5** — cite E-STEER's replan-frequency result as convergent evidence for the praise finding.
   Direction only, never magnitude.
8. **§7** — optionally cite Ben-Zion's own treatment of its significant-but-negligible controls as
   precedent for our equivalence framing.

**Must not do:**
- Do not import any E-STEER magnitude. It reports no sample sizes, no CIs and no significance tests
  anywhere. §9's existing prohibition is correct and should stand.
- Do not assert a submission month for arXiv:2604.00005. The anomaly is real and unresolved.
- Do not write "2,250 runs in total" for Ben-Zion — that is the trauma arm; the total with controls
  is ~3,150.
- Do not keep §3.1's unscoped "the published stimulus sets of the work this literature rests on"
  without the §3.6 scope attached, now that a counterexample sits in our own bibliography.
