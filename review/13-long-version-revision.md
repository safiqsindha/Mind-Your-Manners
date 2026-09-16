# 13 — The 54-page version, cut to 32, and what changed in it

Two jobs in one pass: apply the corrections that reading six sources in full made necessary
(`review/11`, `review/12`), and bring the manuscript down from 54 pages. It is now **32**.

## 1. What the page count came from

| | pages |
|---|---:|
| Starting point | 54 |
| Dropping the annotated §9 (the bibtex bibliography already carried the references) | −6 |
| Cutting and restructuring §1–§8, plus a shorter Appendix C | −9 |
| Normalising the draft's 11pt / 1.02 line stretch to the `article` 10pt default | −7 |
| Adding Appendix A (stimuli) and Appendix B (blinded rating), generated | +4 |
| Fixing table column widths in the converter (see §4 below) | −4 |
| **Now** | **32** |

Two of those need stating plainly rather than being folded into a total.

**The layout change is real and it is worth seven pages.** The preamble was 11pt with
`\baselinestretch{1.02}` and 1-inch margins — looser than any venue's style, and a draft setting
rather than a chosen one. It is now the `article` 10pt default. The venue block is still a
placeholder and the target venue's `.sty` will change the pagination again.

**32 is two pages over the 30 asked for.** Getting to 30 means dropping content, not prose: the
obvious candidates are §7's record of the claims this study withdrew about itself (2.5 pages) and
§3's audit of the published stimulus sets (4 pages). Both are load-bearing for a reader deciding
how much to believe, so the call belongs to the author rather than to a page target.

## 2. Corrections from `review/11` and `review/12`

All "must fix" items are applied.

| Item | What changed |
|---|---|
| §3.8 described Cai et al. as "squarely the paradigm §3 audits" | **Wrong, and now rewritten.** Their output-format instruction is pinned identically across tone conditions and neither prefix carries a demand. Cai is now §3.4's **contrast case** — the confound absent, the tone effect largely absent with it — and a third independent non-replication of "rude beats polite" in §7.5. |
| §1.2 said Ben-Zion's prime lands "before the task begins" | It lands *between two complete task episodes*. Fixed. |
| "Praise shortens" framed as an unanticipated direction | Struck. E-STEER reports positive valence reducing replan frequency relative to neutral, which is a persistence-like count moving the same way; §4.4 says so, direction only. |
| "Independently written" paraphrases in [zhang-2026-politejudge] | The paper never says it. Struck, and the entry corrected from unrefereed preprint to RecSys '26, Reproducibility and Practice Notes. |
| [zhu-2026-spreadsheetbench2] author list truncated at 7 of 14 | Corrected in the bib. |
| §9's "no claim rests on any of the six unread sources" bookkeeping | All seven late additions are now read in full. §9 is gone; Appendix C states the read depth, the six places reading them changed the paper, and the two prohibitions that follow. |
| §3.1's unscoped "the work this literature rests on" | Scoped to four papers from three groups, with §3.4 as the counterexample. |
| "The tone literature offers no mechanism" | Narrowed. Zhang & Li propose one — tone as a severity operating-point shift — and use it to reconcile our own pair of contradictory citations. What remains unexplained is agentic trajectory length. |
| §8.7 (now §8.4) stimulus-sampling concession | Rewritten around their actual numbers: within-level wording variation exceeding between-level tone variation for five of eight judges, and one anomalous paraphrase moving κ by 0.18. |
| §8.8 (now §8.5) negotiation paragraph | Expanded with TERMS-Bench's architecture, and the concession that counterpart register is **not** untested everywhere — it is partly tested there, confounded with cue informativeness in the way §3 describes. |
| §8.4 (now §8.3) substrate | SpreadsheetBench 2 added: what changed, that it is silent on SB1's false-negative rate (checked directly, because §2.8 depends on that figure), that re-running is a new instrument rather than a replication, and that Modification is the metric a per-turn regrade would want there. |

Nothing on the "must not claim" list is claimed: no magnitude is imported from E-STEER, no submission
month is asserted for arXiv:2604.00005, nothing is attributed to TERMS-Bench beyond its
instrumentation, and SpreadsheetBench 2 is not said to revise SB1's audited error rate.

## 3. Corrections carried over from the workshop carve

The 5-page version had been revised and the long version had not. Now both carry: the blinded rating
(κ = 0.70, the contested `L5_rude` arm, *r* = +0.72 continuous, ρ = +0.93 on the closure ordering);
the closure ordering declared post hoc; the praise-stimulus identity (`Q1_praise_assistant` **is**
`P2_praise_only`, which §7.2 now uses); the floor-effect split by injection position; "rules out a
completion inference" replaced by "inconsistent with a simple propositional completion account"; the
insult null bounded rather than asserted; six non-control registers rather than seven arms; and the
hazard reframed from lost correctness to altered control flow, with [greshake-2023] cited for it.

## 4. Two defects found while doing this

**Table columns were sized from the markdown separator row.** pandoc assigns each column a fixed
fraction of `\linewidth` computed from the dash counts in the `|---|---:|` line, which has no
relation to what the cells hold. A table of short numbers was wrapping its headers over three lines
each. Asking pandoc for natural widths fixes that but sends prose-bearing tables off the page — 757pt
past the margin in the worst case. `build/md2tex.py` now asks for natural widths and puts `p{}`
widths back only where the cells need to wrap, measured from the printed width of the cells with
markup discounted, and floored per column at its longest unbreakable token so a monospace arm name
cannot be squeezed off the page. Worth four pages, and pinned by `tests/test_table_widths.py`.

**The manuscript cross-references itself about 200 times, and nothing checked those.** Renumbering a
section during a cut leaves the prose pointing at a section that no longer exists, which breaks
nothing in the build and is invisible in a diff. `tests/test_paper_crossrefs.py` now requires every
§N.M to resolve to a heading, in both documents, and forbids gaps in the subsection numbering. It
found two dangling references in the workshop appendix the moment it was written.

`build/md2tex.py` was also restructured so importing it does no work — it read `sys.argv` and shelled
out to pandoc at import time, which is why the width logic could not be unit tested before.

## 5. Placeholders

Two remain, unchanged: the anonymized artifact URL in Appendix A, and the venue's anonymity policy,
which decides whether the affiliation line is blanked. Both are author-owned and both are gated on
the venue decision, which also gates the page limit and the `.sty`.
