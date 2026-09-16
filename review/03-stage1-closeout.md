# Stage 1 closeout

Date: 2026-09-16
Manuscript commit: `d1bd17f`

---

## What changed in the manuscript

Seven recommendations, all approved, all applied. These were the first manuscript edits in this
branch; everything before `d1bd17f` was findings only.

| # | Change | File |
|---|---|---|
| 1 | `arxiv` 4.0.1 installed so Stage 3 reviewers can run prior-art lookups | environment |
| 2 | Reviewer posture decided: run `paper-review` against a scratch copy, not the repo | decision |
| 3 | Results path resolved: `results_archive/`, 46 files, committed | finding |
| 4 | Three required works cited: `[benzion-2026]`, `[sun-2026-esteer]`, `[zhang-2026-termsbench]` | §1.2, §8.8, §9 |
| 5 | Novelty claim's second clause dropped and boundary restated positively | §1.2 |
| 6 | Title's debt to *Mind Your Tone* stated | §1.1 |
| 7 | `[weinberger-hozez-2026]` subtitle restored; "main track" removed from `[ma-2024]` | §9 |

## Three judgement calls, confirmed

Approved as written:

1. **"a 43-source review with full-text term searches" → "our review".** The count no longer
   described the evidence base, because both new agent-affect papers were found outside that
   review. If a number is wanted later, 46 is defensible, but the search over those three was not
   systematic.
2. **The three new entries are tagged "abstract and registry metadata only; not read in full".**
   That is a weaker standard than the rest of §9 meets. §9's preamble and its outstanding-items
   block were rewritten to say so: three items are open again, not none.
3. **§9 records that arXiv:2604.00005 must not be cited for a magnitude comparison** between
   agent-level and single-step variation. Its abstract makes none.

## One error caught in my own draft

My first pass at §8.8 said TERMS-Bench "scores negotiation agents on concession behaviour and
terms quality". I have only its title. Cut back to "sets out to diagnose negotiation agents beyond
deal rate", which is what the title supports and nothing more.

## Verification after editing

- Citation keys in prose, entries in §9, and keys in `review/references.bib` are **three identical
  sets of 23**.
- Every figure quoted for the three new works was checked against its source abstract, line by
  line.
- `review/references.bib` carries **zero** UNVERIFIED markers.
- Full test suite: **362 passed** on `d1bd17f`.

## What remains open from Stage 1

Carried forward rather than closed:

1. **Read the three new sources in full.** They are cited from their abstracts. Until then §9's
   outstanding-items block correctly says three items are open.
2. **`[ma-2024]`'s "Spotlight" is confirmed; nothing confirms "main track"** — which is why that
   phrase was removed rather than re-sourced.
3. **The IEEE Reliability Magazine paper** — "Mind Your Prompt: How Tone Affects LLM Consistency
   and Safety", March 2026, doi:10.1109/mrl.2026.3660216 — surfaced during verification, still
   uncited, still unread. Only its CrossRef record has been confirmed to exist.
4. **`check-citations` should not gate this repo.** Its parser truncates at the first brace in
   both title and author fields, and CrossRef does not index the arXiv DOIs that cover 18 of the
   23 entries. Documented in `review/01-stage1-citations-and-framing.md` §8.

## Stage 2 status

Not started. Prerequisites are met and recorded in `review/02-stage2-readiness.md`:
LibreOffice recalculation confirmed working (21/21, after installing the missing
`libreoffice-calc`), data located, methods claims mapped to code and tests, and a proposed scope
for the 1,358 numeric tokens in the prose awaiting your call.
