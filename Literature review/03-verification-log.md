# Verification log

Two passes. **Pass 1** (initial review) checked every citation against a primary source and
read four papers in full. **Pass 2** ran six parallel full-text verifications over the 24
sources that had only been read at abstract level, checking each claim adversarially.

**31 of 31 cited sources have now been read in full text.** The 13 background entries carry their
own read-depth tags in `01-sources.md`. What follows is what changed.

---

## Errors found and corrected in pass 2

### Citation-level errors

| Source | Error | Correction |
|---|---|---|
| arXiv:2608.01347 | Cited v1 numbers and quotes as if current | **Six versions exist.** v6 changed the title, reports **4,644** runs not 4,643, and removed the "$166 compute" figure, the "92–97% success" range, and **both quoted sentences**. Cite `v1` explicitly or move to v6. |
| Kapoor et al. 2407.01502 | "Unrefereed preprint" | **TMLR 2025 — refereed.** |
| Kapoor et al. | Implied they recommend reporting turn/step count | They recommend **dollar cost + input/output token counts**. Turn count is our own operationalisation. |
| ABC 2507.02825 | "100% relative overestimation" attributed to SWE-bench Verified | Belongs to **SWE-Lancer**. SWE-bench Verified's own figure is **2.3%**. |
| Sharma et al. 2310.13548 | "18 authors"; quote included "state-of-the-art" | **19 authors.** The sentence does **not** contain "state-of-the-art". |
| ELEPHANT 2505.13995 | "45 pp" used for both conditions | **45 pp** (advice) and **46 pp** (clear wrongdoing) are separate figures. |
| Cuadron et al. 2502.08235 | "4,018 trajectories"; "30% better and 43% cheaper" as one comparison | Paper says 4,018 in the abstract and **3,908** in Results/Conclusion. The 30% and 43% use **different baselines**; the Conclusion says 25% where the abstract says "almost 30%". |
| Sclar et al. 2310.11324 | "76 accuracy points" unqualified | Single-task **maximum**, explicitly a lower bound. Median spread is **7.5**; average ~10. |
| Miller 2411.00640 | "3× cluster adjustment" as general | **DROP-specific (3.05).** RACE-H is 1.10, MGSM 1.88. |
| RedundancyBench 2605.29893 | Fifth author "Guo Jiahao" | **Jiahao Guo.** |
| τ-bench 2406.12045 | Treated as preprint | **ICLR 2025 (poster) — refereed.** |
| OSWorld 2404.07972 | "effectively binary" scalar reward | **Wrong.** `R : S×A → [0,1]`, awarding "a positive decimal under 1" for partial achievement. |
| OSWorld 2.0 2606.29537 | 20.6%/54.8% and 318 tool calls attributed to same model | 20.6/54.8 is **Opus 4.8**; 318 tool calls is **Opus 4.7 single-action** (batched is 597.1). |
| AppWorld 2407.18901 | "GPT-4 Turbo 32.7% / 17.5%" as one row | **Cross-method splice** — 32.7 is Plan&Execute test-normal, 17.5 is ReAct test-challenge. They never co-occur. |
| Errica et al. 2406.12334 | Author order | PDF header is Errica, **Siracusano, Sanvito**, Bifulco; ACL Anthology swaps the middle two. |

### Claims downgraded or withdrawn

- **ELEPHANT does not support a face-threat account of closing.** Its four dimensions concern
  softening message content; nothing addresses curtailing work. The extension is ours and must
  be labelled as such.
- **Patel et al. 2604.07369** contains **nothing** on length, effort or termination — the
  "bridge to §5" framing was unsupported. It is also a high-school AACL SRW poster using GPT-4o
  mini as prompt generator, judge *and* subject, with the circularity self-acknowledged. Its
  abstract also oversells its body: toxicity fell for **all four** emotions, with **anger
  largest** — not a positive-specific effect.
- **Errica's metrics are classification-only** by the authors' own limitations statement;
  they do not extend to a continuous DV.
- **Shrivastava 2606.27009** is in mild **tension** with §6, not support: the oracle beats
  always-take-round-1 by 0.115 IS, implying the best round often is *not* round 1. It also
  reports no "first round best X%" statistic. *(Coincidence to avoid: their `fixed_k1` cuts 86%
  of tokens — a different quantity from our 85–90% first-attempt-best rates.)*
- **Cai et al. 2512.12812** is not a clean null: 2 of 12 domain-level and 4 of 54 task-level
  comparisons remain significant, with **no multiplicity correction and no power analysis**.
- **Gandhi & Gandhi 2503.13510**: the 8.1% is scoped to essay/blog responses only, with **no
  significance test, CI, SD or n anywhere in the paper**.
- **Miller contains no TOST or equivalence testing** — cannot be cited for it.
- **Reflexion** runs against §6 (AlfWorld improves to trial 12); recommend cutting or citing
  only its WebShop failure case.

### Claims strengthened

- **EmotionPrompt's EP01–EP11 extracted verbatim:** ≥6 of 11 carry explicit verification or
  persistence demands; only EP08 is near-pure affect.
- **Meincke et al.'s eight prompts extracted verbatim:** the only one that moved performance
  (+8.8 pp) is the only one with a scope-and-completeness clause. Their one large negative
  effect is a distraction artefact the authors themselves flag.
- **Vaugrante's 4.42% / 2.58% recomputation confirmed verbatim** as their own reanalysis of
  EmotionPrompt's data. Their EmotionPrompting replication: **+1%, n.s., χ²=0.11, p=.74**.
- **Huang et al. never test execution feedback** — they cite Self-Debug for it. §6 tests their
  untested escape hatch.
- **Balachandran's "perfect verifier" is oracle-assisted** in both the best-of-n and the
  "hybrid critic" sense ("the critic knows the ground-truth").
- **Self-Refine concedes the point on reasoning tasks**: Math Reasoning +0/+0.2/+0.2, because
  "ChatGPT feedback for 94% instances is 'everything looks good'".
- **SpreadsheetBench's own GPT-4o declines** from single- to multi-round (soft 18.35 → 16.96),
  attributed by the authors to redundant re-fetching. Prior evidence for our mechanism, from
  our own substrate.
- **AppWorld's `TestTracker` exposes per-assertion pass/fail** with `requirement` and `label`
  fields — verified in the evaluator source, not just the paper. The recommendation holds.
- **Sharma et al.'s "concise" preference feature ranks 21st of 23** — we are not restating a
  known preference-data length bias.

---

## Facts about our own setup that changed

- **SpreadsheetBench's official multi-round protocol caps at five rounds**, not twenty. Our
  20-turn ceiling is our own choice and must be stated as such.
- **SpreadsheetBench already has an official partial-credit metric** (soft/IOI vs hard/ICPC) —
  at the instruction/test-case level, not per turn.
- **Its evaluator self-audit reports 4% instruction-level false negatives** and a 3.8%
  test-case-level false omission rate — a citable noise floor for per-turn regrading.

---

## Remaining UNVERIFIED items

| Item | What is unverified |
|---|---|
| OptimalThinkingBench 2508.13141 (B5, background) | Author list not confirmed; claims come from a secondary summary. |
| SWE-bench solution-leakage figures (F7, background) | 32.67% / 31.08% come from a secondary summary; trace to arXiv:2505.20411 / 2507.11059 before citing. |
| WebArena task count (G6, background) | Commonly cited as 812; not confirmed in this pass. |
| Cuadron et al. model count (B1) | Paper states 19; its model table enumerates 17. The two unlisted models were not identified. |

*(PLUM's history protocol was previously listed here; it is now resolved — verified as genuinely underspecified in both the paper and the released corpus, which is a citable limitation of theirs.)*
| Cuadron et al. venue | ICML-template formatting but no journal-ref. **Cite as an arXiv preprint** unless independently verified. |
| OSWorld 2.0 byline | Displayed as the collective "XLANG Lab and Collaborators"; 30 named contributors appear only in Appendix A. Some citation managers will mishandle this. |
| ABC title | NeurIPS lists "Best Practices **in** Building…"; arXiv says "**for**". |
| Schegloff & Sacks 1973 | Page range (289–327, *Semiotica* 8(4)) taken from standard citations, not the original. Low risk. |

---

## Searches that returned nothing — these license the novelty claims

Re-run and confirmed at full-text level in pass 2:

- **Tone/politeness/register manipulated mid-task in an agentic or tool-using loop** — nothing.
  Weinberger & Hozez's 18 prompt templates contain zero register vocabulary; their only
  two-turn variants deliver the *opening* instructions across a `<TURN-BREAK>`, before the agent
  has worked. IHBench's six interruption types are content categories, not registers.
- **Politeness and task-demand as separable factors** — nothing. The confound is present in
  published stimuli (A1, A3, EmotionPrompt, Meincke) but never named or tested.
- **Closing-sequence pragmatics applied to LLM agent termination** — nothing.
- **Praise or positive feedback shortening agent work / ending it early** — nothing; the
  existing literature points the other way at the level of within-turn verbosity.
- **Sycophancy linked to the model's own reduced effort or early termination** — nothing, across
  all four sycophancy papers read in full. Sharma measures agreement; ELEPHANT measures content
  softening; SYCON-Bench never uses praise as pressure; Ibrahim's "effort" is the human's.
- **A paper reporting its own confound post-hoc** — the usable templates are Vaugrante et al.
  §4 (a four-group checklist: benchmark adequacy, methodological transparency, model-update
  awareness, output-classification accuracy, explicitly importing the psychology replication
  crisis's remedies) and Ibrahim et al.'s preregistration practice (one transparently documented
  deviation with a sensitivity analysis attached). Follow Vaugrante's structure for §8.

---

## Pass 3 — cross-check against `RESULTS.md` (final review)

An independent adversarial read of all four review files against the repo's own results found
that the review was least reliable where it described *our* numbers. Corrected:

| Claim in the review | Problem | Correction |
|---|---|---|
| "your ~86% first-attempt-best figure" | **86% appears nowhere in the repo.** It was the brief's rounding. | `RESULTS.md` reports **90%** (Stage 0, ceiling 10) and **87% / 85%** (Stage 1, ceiling 20, Luna / GLM). All occurrences replaced; the paper must name the run it quotes. |
| "per-step effort is flat on every contrast" / "loads *exclusively* onto persistence" | Contradicted by `RESULTS.md` ("threatening… sits 20–30% above neutral on every subsequent call… two channels") and by the review's own analysis output ("work remains" +396 tokens/turn [+163, +646]). | Reworded to *predominantly*, with both exceptions named. |
| "accuracy does not move (0.299–0.349)" | Numbers were computed in an unsaved script; no provenance in the repo. | Accuracy section added to `results/analysis/praise_turn_vs_trajectory.py`; synthesis now cites that output and `RESULTS.md`'s "within 2.6 points, all p>0.13". |
| "§5 needs restating — sign error" | `RESULTS.md` already reports Q4 at +0.50 vs control and frames praise as Q4-vs-Q5. | Reframed as a drafting caution about one summary sentence and the brief's paraphrase. |
| "praise cuts total output" | Q4 raises total tokens (+3,101 [+354, +5,859]). | Scoped to praise-alone arms and the Q4-vs-Q5 contrast. |
| 4,643 runs / $166 / 92–97% stated as current for arXiv:2608.01347 | These are v1-only. | Tagged v1 inline; v6 figure (4,644) used elsewhere. |
| "raw logs cannot separate the praise arms" (earlier in this session) | Each `--interject` invocation writes one raw log per arm. | Corrected: per-turn tokens are recoverable from the raw logs if they exist; harness now also records `interjection_key` so the trajectory key is self-describing. |
| "20-turn agent" in the Huang comparison | The probe/praise runs and the 90% figure are at a **10-turn** ceiling; only Stage 1 is 20. | Ceiling named per run. |
| "no-op turn" → "Duplicated Step" | The repo's no-op is an *output* criterion (graded range unchanged); Duplicated Step requires identical inputs. | Mapped to "redundant step"; Duplicated Step cited as nearest subtype only. |
| "premature disengagement" for the praise effect | Stage 0: 2–6% of trajectories still improving at stop, no gap vs control — not premature. | Term reserved for Cuadron's failure mode; ours described as earlier, non-premature disengagement. |
| Cai et al. caveat dropped in the synthesis | Sources say "not a clean null"; synthesis used it as one. | Caveat carried into the synthesis. |
| Source counts (38 / 28 / uncounted) | File has 44 entries across 43 headings (G4/G5 share one). | 31 cited + 13 background, every heading tagged with read depth. |
| Cuadron "19 models" | Table enumerates 17. | Stated as 19 claimed / 17 enumerated. |
| ABC "all ten" vs "80%" | Two different statements. | Clarified: all ten have *some* reporting limitation; item R.8 failed by 80%. |
| Minor | 8-vs-10 pairwise tests (A1); ELEPHANT roster version (GPT-5 → v2, Sept 2025); "peer-adjacent" (A3 is unrefereed); +8.8 pp vs RD scale; "max 22" tests and the Gandhi full-text details missing from the sources file; Self-Debug quote truncated. | All fixed in place. |

Repo-side, not the review's: `RESULTS.md` prose gives −0.62 / −1.14 for the praise replication
while its tables give −0.59 / −1.08. Flagged in `02-synthesis.md` §7.8.
