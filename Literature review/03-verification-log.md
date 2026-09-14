# Verification log

Every citation below was checked against a primary source (arXiv abstract page, ACL
Anthology, or publisher page) during this pass on 2026-09-14. Nothing here was recalled
from memory. Where a number came from a secondary summary rather than the paper itself, it
is marked.

## Read in full text (PDF extracted locally, not summarised)

| Source | Pages | What this means |
|---|---|---|
| A1 — arXiv:2510.04950 | 5 | All tables, statistics, limitations and the tone-prefix table read verbatim. The "Try to focus and try to answer this question:" confound is quoted directly from their Table 1. |
| A2 — arXiv:2605.29027 | 10 | All result tables (Tables 2–6), the routing-framework section, discussion and limitations read verbatim. The self-replication failure is read from their Table 2, not inferred. |
| A3 — arXiv:2607.23915 | 25 | Tables 1–4, prompt prefixes with word counts and VADER scores, methods and analysis read verbatim. The brevity-instruction confound is quoted from their Table 2. |
| A4 — Yin et al. 2024 (ACL Anthology PDF) | 27 | Table 1 benchmark scores, politeness-scale construction and the generation-length discussion read verbatim. |

## Verified at the primary source (abstract page / anthology page / paper HTML)

A5, A6, A7, A8, A9, A10, A11, A12, B1, B2, B3, B4, B6, C1, C2, C3, D1, D2, D3, D4,
E1, E2, E3, E4, F1, F2, F3, F4, F5, F6, G1, G2, G3, G4, G6.

A7 (arXiv:2608.01347) was read from the v1 HTML full text, which is more complete than an
abstract read; its experimental design, arm definitions, effect table and limitations come
from the paper body.

G2 (AppWorld) grading details — TGC/SGC definitions, ~8 unit tests per task, the 100-LLM-call
ReAct ceiling, collateral-damage mechanism and the GPT-4o baseline table — come from the
ar5iv full-text rendering, not the abstract.

## Existence checks specifically requested

All three arXiv IDs in the brief exist and are the papers described:

- **2510.04950** — exists. Dobariya & Kumar, 6 Oct 2025, 5 pages, 3 tables.
- **2605.29027** — exists. Dobariya & Kumar, 27 May 2026, AMCIS 2026 full paper.
- **2607.23915** — exists. Kumar & Dobariya (author order reversed), 27 Jul 2026, 25 pages.

## UNVERIFIED — do not cite these specifics without checking

| Item | What is unverified | Where to check |
|---|---|---|
| A6 (PLUM) | Whether the polite/impolite "interaction histories" are injected as conversation-thread prefixes or as system-level context. Matters if you cite it as mid-conversation precedent. | Released HuggingFace corpus / paper §methodology |
| A9 (Meincke Report 3) | Exact model list, repetitions per arm, per-arm n. Only the benchmarks (GPQA Diamond 198 items; MMLU-Pro 100 engineering questions) and the headline null were confirmed. | arXiv:2508.00614 PDF |
| A7 | Title differs between the arXiv listing page and the v1 HTML. | Current arXiv listing at time of submission |
| B3 (RedundancyBench) | Dataset size, model list, and the full redundancy label taxonomy. The 24.88% best-method score was confirmed. | arXiv:2605.29893 PDF |
| B5 (OptimalThinkingBench) | Author list not confirmed. Claims (33 models, 72 domains) come from a secondary summary. | arXiv:2508.13141 |
| C2 (Reflexion) | Metadata not re-verified in this pass. Self-Refine (2303.17651) was verified. | arXiv:2303.11366 |
| D4 | No effect sizes available; abstract only. | AACL SRW 2025 poster |
| F6 (ABC checklist) | Full author list not confirmed. The 7/7/10 validity counts, the τ-bench empty-response bug and the CVE-Bench 33% figure were confirmed. | arXiv:2507.02825 |
| F7 | The 32.67% solution-leakage and 31.08% inadequate-test figures came from a secondary summary, not the primary paper. The OpenAI audit figures (59.4% of 138 o3 failures; 6–7 pp inflation) come from OpenAI's own blog post — a vendor source, not a paper. | arXiv:2505.20411, arXiv:2507.11059 |
| G2 | The ACL 2024 Best Resource Paper designation was not re-checked. | ACL 2024 proceedings |
| G5 (OSWorld 2.0) | Author list, the 27.25-checkpoints-per-task figure and the ~318-tool-calls figure come from secondary summaries. The 108 tasks, 150/300/500 step budgets and 20.6%/54.8% results also come from secondary summaries. | arXiv:2606.29537 |
| G6 (WebArena) | Task count (commonly cited as 812) not confirmed. Baselines (14.41% GPT-4 vs 78.24% human) were confirmed. | arXiv:2307.13854 |

## Searches run that returned nothing relevant

These are the negative results of the search itself, and they are what license the novelty
claims in `02-synthesis.md §1`:

- Tone / politeness / emotional framing manipulated **mid-task** in an agentic or tool-using
  loop — nothing found in any phrasing.
- Politeness and task-demand treated as **separable factors** in a tone experiment — nothing
  found. The confound exists in published stimuli but is never named or tested.
- **Schegloff & Sacks closing sequences applied to LLM agent termination** — nothing found.
  Closing-sequence pragmatics appears in dialogue-coherence work, never connected to agent
  stopping.
- Praise or positive feedback **shortening** LLM output or ending work early — nothing found;
  the literature that exists points the other way (see `02-synthesis.md §2a`).
- Sycophancy linked to **reduced effort, shortened output or early termination** rather than
  agreement bias — nothing found. D4 (positive stimuli → more sycophancy) is the closest, and
  it does not measure effort.
- A paper reporting its **own** confound discovered post-hoc, as a precedent for how to write
  that section — nothing clean found in the tone literature. The nearest usable precedents are
  A2 (authors reporting their own failure to replicate, though they do not frame it that way)
  and D3 (third-party reanalysis showing a headline effect was a selection artefact). If you
  want an explicit template, D3's framing is the one to follow.
