# Build

Produces `main.pdf` from `paper/*.md`.

```bash
python3 build/md2tex.py     # paper/*.md -> build/sections/*.tex, rewriting [key] -> \cite{key}
cd build
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

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
- `references.bib` is copied from `review/references.bib` at build time.
