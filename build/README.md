# Build

Produces `main.pdf` from `paper/*.md`.

```bash
# One chain. md2tex.py exits nonzero on a failed conversion or an unconverted
# citation, and must stop the build -- if it is run as a separate command, a
# paste-and-run continues to pdflatex and overwrites main.pdf with the defect
# the script just refused.
python3 build/md2tex.py && cd build && \
  pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Or `bash build/build.sh`, which is the same chain under `set -euo pipefail`.

Requires `pandoc`, `pdflatex`, `bibtex`. Engine is **pdflatex**: the 21 non-ASCII characters the
prose uses are declared explicitly in `main.tex` rather than relying on a Unicode engine, because
lualatex could not resolve the Latin Modern OpenType fonts in this container.

## Venue

`main.tex` carries a **venue-neutral** preamble, marked with a comment block. Swap that block for
the target workshop's `.sty` and nothing else changes. The NeurIPS and ACL style files could not be
fetched here (HTTP 403 / 404 through the proxy), so no venue is baked in.

## Known build notes

- `\real`, `\tightlist` and `\pandocbounded` are provided in `main.tex`; pandoc emits them but they
  live in pandoc's own template, which this build does not use.
- "Multiply-defined labels" warning: pandoc generates section labels per file and some collide.
  Cosmetic — it does not affect output or citations.
- `references.bib` is copied from `review/references.bib` by `md2tex.py` on every run, so the
  keys used to emit `\cite` and the keys BibTeX resolves cannot drift apart.
- `md2tex.py` exits nonzero if any pandoc conversion fails, and deletes the target `.tex` first,
  so a failed conversion cannot leave a stale section in the PDF. It also fails the build if any
  citation key survives unconverted into the LaTeX.
- Citations with locators (`[key, Table 3]`) become `\cite[Table 3]{key}`.
