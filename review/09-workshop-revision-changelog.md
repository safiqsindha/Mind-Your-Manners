# Workshop revision — change log

Against the 39-item reviewer list. Source: `workshop/*.md`, `build/workshop.tex`,
`results/analysis/figures.py`. Build: `bash build/build-workshop.sh`.

**Layout.** Body pages 1–5, appendix 6–7, references 8. The five-page body limit holds;
the stimulus table (item 35) and nothing else went to the appendix.

**On placeholders.** The brief said to placeholder anything I did not have. Most of it I did
have: this repository holds the harness, the per-trajectory records and the estimator, so
14 items the brief expected to be `[AUTHOR: ...]` were answered from source instead, and each
is marked **resolved from repo** below with where it came from. Four placeholders remain.

---

## A. Factual and internal-consistency fixes

| # | What I did |
|---|---|
| 1 | **Resolved from repo** — not a discrepancy. §1.2 of the full paper: 9,850 of the 11,850 were regraded. §5 now reads "9,850 of the 11,850 trajectories — the six runs carrying a mid-task interjection; the opening-tone run and one superseded batch were not regraded". Both numbers kept, difference explained in one clause. |
| 2 | **Resolved from repo** — `L4_neutral` is the interruption control (`harness/tone_wrappers.py`). §3 opens "Across a scale of six non-control registers — `L4_neutral` is the interruption control every one of them is measured against". Figure 1A panel title now "Six non-control registers". |
| 3 | Figure 2 caption now "the five treated arms of the six-arm closure probe, each against the control". |
| 4 | Figure 2B relabelled from Q-codes to arm names: "praise isolated: praise+remains vs remains alone", "bare closing cue vs praise the assistant". Panel title's `§2.6` removed — the figure is shared with the 54-page paper, so it now carries no section number at all, since a cross-reference that resolves in one document and dangles in the other is the defect itself. |
| 5 | **Resolved from repo** — decisive. `PRAISE_PROBE_INTERJECTIONS["Q1_praise_assistant"] = PROBE_INTERJECTIONS["P2_praise_only"]`: byte-identical, the same stimulus re-measured in a second run. §5 now uses it as the worked example of the re-measurement spread (−0.59 and −1.08, a factor of 1.8, inside the stated 1.5×–3.4×). Appendix A.3 flags the identity. |
| 6 | Both figure captions now open by naming the model and ceiling. §2 states "Both figures and every effect in turns are Luna; GLM enters only as a cross-model replication and is reported in percent, which is how that run was analysed." |
| 7 | §5 now defines both outcomes and says why they can move independently: graded fraction is the share of the graded range matching the answer, binary accuracy is the pass/fail verdict requiring every test case to pass, so a trajectory can climb 0.2→0.9 and still fail. |
| 8 | Named: "This experiment — the six-arm closure study of this section — is the least replicated in the paper". |
| 9 | **Resolved from repo** — computed from the committed records. §2: control mean 3.9 turns (SD 2.6) closure run, 3.6 (SD 2.5) probe, 3.4 (SD 2.3) register, "so a one-turn effect is roughly a quarter to a third of a trajectory". |

## B. Aligning claims with the caveat

| # | What I did |
|---|---|
| 10 | Title is now *Mind your manners? LLM-agent persistence tracks demand, not social register*. |
| 11 | Abstract rewritten to the supplied wording, with the insult CI added. |
| 12 | **Resolved from repo** — the test was run and passed. §2.8 of the full paper reports pooled TOST at ±4: demand *p* = 0.0014, praise 0.0000, insult 0.0001. Abstract now carries the equivalence clause; §5 repeats it with the three *p*-values. (Not placeholdered, but note for the author: the praise pool is heterogeneous, Q = 8.45, *p* = 0.038, and under random effects the bound weakens to *p* = 0.0119 — it holds, but the workshop version does not have room to say so.) |
| 13 | Replaced with "inconsistent with a simple propositional completion account", plus the reason: the text explicitly denies completion and the praise acts anyway. |
| 14 | Added verbatim to §4, in a paragraph headed "What is new here against the nearest prior work". |
| 15 | **Resolved from repo, and it goes against us.** `git log -S` shows the arm definitions, their H1/H2/H3 predictions and the run's results all entered in one commit (9064309), so there is no dated pre-specification. §4 says so under "The ordering is ours and was not fixed in advance", and Figure 2A's caption repeats it. One residual placeholder for a pre-specification outside the repo. |
| 16 | §3: "with **no overlap in point estimates**", then a separate sentence giving the two intervals and conceding "the two groups are not individually resolved at their boundary; what the data support is an ordering, not a gap." |
| 17 | §3 states the bound: the interval excludes a quarter-turn effect either way, "against the control mean of 3.6 turns it excludes anything above about 7% in the lengthening direction, so we report it as a bounded null rather than as an absence." |
| 18 | §3 closes on exactly this: sycophantic shortens rather than sitting at zero, and "the data are as consistent with three groups as with two: demand lengthens, neutral register does nothing, and praise-like or closing-like language shortens." |
| 19 | §7 paragraph replaced verbatim. |
| 20 | §7 literature claim replaced verbatim. |
| 21 | §7 has a new paragraph: accuracy did not fall, what moved was control flow, the observation channel is where tool output arrives, and the closing cue is an informational claim about the environment rather than a pleasantry. Abstract's closing line is now "text arriving in the agent's observation channel changed when it stopped, without instructing it to stop" — "a pleasantry can end an agent's work" is gone. Citation placeholdered. |
| 22 | Figure 1B panel title is now "Demand manipulation increases persistence; praise decreases it; insult does not". Figure 1's main caption title changed to "Persistence tracks demand, not register" to match the new paper title. |

## C. Methods and reporting

| # | What I did |
|---|---|
| 23 | §2 verbatim: "We report nominal clustered permutation *p*-values; correction status is determined by the two Benjamini–Hochberg families described here." |
| 24 | **Resolved from repo** — same commit evidence as item 15, so "planned" is not defensible. Now "the two **designed within-run contrasts** of §4 — designed, not pre-registered: no dated pre-specification exists". |
| 25 | **Resolved from repo** — computed. Ceiling is ten acting turns; 3–4% of trajectories reach it; trajectories ending before the scheduled injection got no interjection and are excluded, with firing determined pre-delivery so it cannot differ by arm except by chance. |
| 26 | **Resolved from repo, and it is a new result.** `results/analysis/injection_position.py` splits each closure contrast by position using the paper's own estimator and seed. The closing cue is **−1.55 [−2.07, −1.03] at turn 1** against −0.99 [−1.59, −0.43] at turn 2 — largest where the floor binds least, which is the opposite of what a floor artefact predicts. §4 reports it under "A floor could manufacture this, and does not", including that the turn-2 rows rest on the 35–38 tasks that reach turn 2. |
| 27 | **Resolved from repo** — `cl100k_base`, stated in §2 and recomputed per-arm in Appendix A. |
| 28 | **Resolved from repo** — §2: "three or four trials at each of two or three injection positions", and "Luna's advertised parameters omit `temperature` entirely" (`harness/config.py`). |
| 29 | **Resolved from repo** — §1 quotes the Rude prefix verbatim ("Do not waste my time or give any extra text… answer it immediately") against the Neutral prefix asking for "the single letter", cited to `kumar-dobariya-2026`. |
| 30 | Replaced verbatim. |
| 31 | §5 explains it in two sentences: the regrader read a turn's workbook without passing it through a spreadsheet engine, so any turn answering with a formula read back as empty and scored zero. |
| 32 | **Deferred to the long version.** No placeholder — the stratification exists in the 54-page paper and there is no room here; noted in the residual list below rather than pretended. |

## D. Polish

| # | What I did |
|---|---|
| 33 | `build/clean_bib.py` strips editorial clauses on the way into a workshop-only bibliography. The canonical `review/references.bib` keeps them, because the 54-page paper's §9 is built on exactly those notes. Removed: "read in full", "Version hazard: …", "confirmed via arXiv comments", "Proposes the E-STEER emotion-steering framework", plus two others. Kept: refereed/unrefereed status, venue, which version is cited. The script fails the build if an unrecognised editorial marker survives, rather than guessing. |
| 34 | Changed to "We take that as established by prior work." |
| 35 | Appendix A, generated by `results/analysis/stimuli_appendix.py` from `harness/tone_wrappers.py` — all 17 arms, verbatim, with token counts recomputed rather than asserted (all 28). Not transcribed, so it cannot drift from what was run. |
| 36 | Artifact paragraph added at the end of §7, URL placeholdered. |
| 37 | Author block now carries a LaTeX comment flagging that the affiliation line must be blanked too if review is double-blind, and the line itself reads "[affiliation withheld pending the venue's anonymity policy]". |
| 38 | Self-audit paragraph in §5 kept at its previous length. |
| 39 | §6 still has exactly the three limitations. |

---

## Residual `[AUTHOR: ...]` placeholders — four

1. **`workshop/02-closing.md`** — *"if a dated pre-specification of the closure ordering exists outside the repository, cite it here; otherwise this stands."* The repo shows arms, predictions and results in one commit; only the author knows whether a dated pre-registration exists elsewhere.
2. **`workshop/03-close.md`** — *"supply an indirect prompt-injection citation — e.g. a benchmark or taxonomy paper — and add it to the bibliography."* Item 21 asks for a citation the bibliography does not contain. Adding one would mean citing a work nobody here has verified, which this project's standing rule forbids.
3. **`workshop/03-close.md`** — *"anonymized artifact URL."*
4. **`build/workshop.tex`** — *"check the workshop's anonymity policy."*

## Not placeholdered, but the author should know

- **Item 32** is deferred, not done: the solvability stratification (26 never solved, 4 always, 20 live) is in the long version and there is no room in five pages.
- **Item 12's caveat:** the pooled praise equivalence is heterogeneous between models (Q = 8.45, *p* = 0.038); under a random-effects pool the ±4 bound weakens to *p* = 0.0119 but holds. The workshop text states the equivalence without this qualification.
- **Page limit:** the body is five pages against a *4-page* target if the venue uses that limit. Confirm the CFP; if it is four, §5's self-audit paragraph and the §1 confound example are the two most compressible passages.
