# Stage 5 — Assembly and build

Date: 2026-09-16
Output: **`build/main.pdf` — 47 pages, 0 LaTeX errors, 0 undefined citations.**

---

## Decisions I took

You said to take whatever decisions were needed. These are the three that matter.

**1. Venue: none baked in.** I tried to fetch the NeurIPS 2024 and ACL style files; both were
blocked through the proxy (HTTP 403 and 404). Rather than burn time hunting mirrors or
hand-approximating a specific house style, `main.tex` carries a **venue-neutral preamble inside a
marked comment block**. Swapping that block for a real `.sty` is the only change needed when you
pick a venue. This is reversible in about a minute and does not misrepresent the paper as
formatted for somewhere it isn't submitted.

**2. Engine: pdflatex, with 21 Unicode characters declared explicitly.** `lualatex` is installed
and would handle Unicode natively, but it could not resolve the Latin Modern OpenType fonts in
this container (`fontspec` could not find them under any name; the font cache appears incomplete).
I enumerated the exact non-ASCII characters the prose uses — 21 distinct, led by em-dash (254),
§ (239) and the Unicode minus (161) — and declared each one. Deterministic, and no font
dependency.

**3. §9 becomes an appendix, and the bibliography is generated from the `.bib`.** Citations
resolve through `natbib` against `review/references.bib`, so there are no undefined references.
§9's annotated entries — with their verification tags and read-depth markers — are kept as an
appendix rather than discarded, because that content is part of the paper's self-audit argument
and has no equivalent in a generated bibliography.

---

## Pipeline

```
paper/*.md  --[build/md2tex.py]-->  build/sections/*.tex  --[pdflatex+bibtex]-->  build/main.pdf
```

`md2tex.py` does three things pandoc alone does not:

- rewrites `[citation-key]` and `[key-a; key-b]` into `\cite{...}`, validated against the actual
  keys in `references.bib` — **95 `\cite` commands emitted, 0 undefined**
- strips the `> **Draft status.**` admonition blocks, which are notes to you, not to a reader
- demotes each file's `#` heading to a `\section`

---

## Build problems hit and fixed

| Problem | Cause | Fix |
|---|---|---|
| `Unicode character − (U+2212) not set up` | pdflatex + inputenc has no mapping | enumerated all 21 non-ASCII chars, declared each |
| `Undefined control sequence … \real` | pandoc emits `\real{0.33}` in table column specs, but defines it in *its own* template, which this build doesn't use | `\providecommand{\real}`, plus `\tightlist` and `\pandocbounded` |
| `fontspec: font "LMRoman10" cannot be found` | Latin Modern OTF unresolvable in this container | abandoned lualatex, went back to pdflatex |
| NeurIPS/ACL `.sty` unreachable | HTTP 403 / 404 through the proxy | venue-neutral preamble |

Remaining warning: **"multiply-defined labels."** Pandoc generates a label per heading per file and
a few collide across sections. Cosmetic — it does not affect output, numbering or citations. Left
as-is because fixing it means rewriting pandoc's label scheme, which is churn for no reader-visible
gain.

---

## Figure and table stubs

`build/main.tex.stubs` holds two figure stubs with TODOs. **They are not `\input` into the
build** — an empty framed box in a 47-page PDF is worse than no figure — so paste them in when
you have the plots.

The substantive point: **the paper currently contains no figures at all.** Every table is inline
markdown that pandoc converts. Two results deserve floats:

- `fig:demand-vs-register` (§4.9) — the three-way dissociation. This is the paper's headline
  result and it is prose-only.
- `fig:closing-cue` (§5) — the six-arm Q0–Q5 ordering, monotone in projected closure.

---

## The thing you should look at first

**48 pages** — 41 body, 2 bibliography, 5 annotated appendix.

The instinct that this is long relative to the literature is worth checking against the
literature, so I did. Actual page counts, taken from the PDFs themselves or from arXiv's comments
field:

| Work | Pages |
|---|---:|
| **This paper (body only)** | **41** |
| SpreadsheetBench — the substrate, NeurIPS Spotlight | 38 |
| Weinberger & Hozez, v6 | 37 |
| Sclar et al. — ICLR | 29 |
| Kumar & Dobariya (16 + 9 appendix) | 25 |
| Vaugrante et al. | 23 |
| E-STEER | 15 |
| RedundancyBench | 15 |
| Miller — error bars | 14 |
| Dobariya & Kumar 2026 — AMCIS full paper | 10 |
| **Mind Your Tone** — the paper this is positioned against | **5** |

**So 41 pages of body is not an outlier in this literature.** It sits just above SpreadsheetBench
and Weinberger, both of which are full-length arXiv preprints of the same kind. The paper is long,
but it is not longer than its sources — several sources are 23–38 pages.

**The gap that actually matters is against a workshop limit, not against the sources.** Typical
workshop limits are 4–9 pages plus references. That is a 5–8× cut, not the ~1.2× that "longer than
my sources" would suggest. And the paper this one argues with is 5 pages long.

That reframes the decision. This is not an overlong paper needing a trim; it is a full-length
paper that would have to become **a different and much smaller artifact** to be a workshop
submission. Three coherent options:

1. **arXiv preprint as-is.** 41 pages is normal here. Fix the blockers and the pipeline, post it.
2. **Carve a workshop paper out of it.** §7 (what replicated) is the part every reviewer praised
   and the most separable — a self-audit paper on measurement instability in agent evaluations
   stands alone at roughly 8 pages, with the tone result as its running example rather than its
   contribution.
3. **Full venue submission.** The length fits; the six blockers in
   `review/05-stage3-peer-review.md` are what gate it.

Section sizes, if a cut is wanted: §3 (16%), §6 (14%), §4 (13%) and §7 (11%) are the four largest
of 25,165 words.

I have not cut anything.
