# C. Sources: read depth and version hazards

The bibliography is a standard reference list; this appendix records what it cannot show — how deeply each
source was read, and which entries carry identifier hazards that will mislead a reference manager.

**Every source cited in this paper has been read in full.** That was not true of earlier drafts and the
difference is not cosmetic. Seven entries postdated our literature review — three added after a citation
audit, four surfaced by a simulated review panel (§3.5) — and for a period all seven were cited at abstract,
or title-and-author, depth. All seven have since been read end to end, and doing so changed this paper in
six places. [munirathinam-2026-recuse] narrowed §5.1's closing-sequence claim and **removed** §5.5's
mid-task-delivery novelty step outright. [cai-2025-tone], which a draft had called "squarely the paradigm §3
audits", turned out to be the opposite — format pinned across conditions, prefixes instructing nothing — and
is now §3.4's contrast case and a third independent non-replication of "rude beats polite" (§7.5).
[zhang-2026-politejudge] supplied §3.4's admitted demand/register confound and the numbers §8.4 attaches to
its own stimulus-sampling concession; a draft called its paraphrases "independently written", which the
paper never says. [sun-2026-esteer]'s replan-frequency result is a persistence-like count moving the same
way as our praise effect, so "praise shortens" is **not** an unanticipated direction (§4.4).
[benzion-2026]'s prime lands *between two complete task episodes*, not before the task begins, and §1.2 is
corrected. And [zhu-2026-spreadsheetbench2] expanded §8.3 while closing a question §2.8 depends on: it says
nothing about SpreadsheetBench 1's audited false-negative rate.

Two prohibitions follow, stated here so they are not quietly relaxed. **No magnitude may be imported from
[sun-2026-esteer]**: across the whole paper we found no reported sample sizes, confidence intervals,
standard errors or significance tests, so we cite its direction and nothing else. And **nothing may be
attributed to [zhang-2026-termsbench] beyond its instrumentation**, which §8.5 names and we have not run.
Two entries were also corrected on re-verification: [zhang-2026-politejudge] is **not** an unrefereed
preprint but accepted at RecSys '26, Reproducibility and Practice Notes track (ACM DOI
10.1145/3773078.3841249, not resolving in CrossRef when we checked), and [zhu-2026-spreadsheetbench2] has
**fourteen** authors where an earlier list stopped at seven.

**Version and identifier hazards.** Four entries resolve to the wrong thing if cited casually — a higher
rate than we expected, and the argument for pinning versions rather than years in a fast-moving preprint
literature. [munirathinam-2026-recuse] must be **cited at v4**: the v1 title is "Will the Agent Recuse
Itself? … In-Band Access-Deny Signals" and contains no mid-flight study at all, yet indexers still serve it
under the v4 DOI. [greshake-2023] must be cited by **ACM DOI or pinned at arXiv v2**: the v1 title is "More
than you've asked for" and does not contain the phrase "indirect prompt injection". [weinberger-hozez-2026]
must be **cited at v6 (10 Sep 2026)**: it has six versions, grew roughly 8× between v1 and v6, and v6
reports 4,644 valid runs while removing material present in v1. And [sun-2026-esteer]'s identifier and date
disagree — a `2604` prefix normally denotes an April 2026 submission, but arXiv's submission history, the
arXiv API and OpenAlex all give 9 March 2026 for v1, with OpenAlex's *ingestion* date of 3 April 2026 the
only April date anywhere; we record the observation and assert no explanation. Two smaller notes:
[cai-2025-tone] has a v2 (27 Mar 2026), which is the version we read; and [kumar-dobariya-2026] and
[dobariya-kumar-2026] are **different papers by the same two authors in different orders**, with different
dependent variables — inference cost in the first, accuracy in the second — which §3.2 and §3.3 depend on
keeping apart.

Two citations we deliberately do not make: [lakens-2017] is the source for §2.7's TOST framing and **not**
[miller-2024], whose paper contains no equivalence framework; and [chen-2023] was dropped from an earlier
draft, because the words §6.4 quoted for it were Huang et al.'s prose about Self-Debug rather than a
quotation from Chen et al. **What remains open** is nothing on the read-depth list, and two verification
gaps this paper states in place rather than closing: we have seen [dobariya-kumar-2026]'s table of the
prefix pool for the 2025 dataset but not the 2025 paper's own (§3.3), and the public release of
[zhu-2026-spreadsheetbench2] may not be the complete set of 321 tasks, which anyone costing a re-run there
should verify against the release.
