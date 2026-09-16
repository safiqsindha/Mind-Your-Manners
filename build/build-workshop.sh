#!/usr/bin/env bash
# Fail-fast build for the NeurIPS workshop carve, same discipline as build.sh:
# md2tex.py's nonzero exit MUST stop the chain, or pdflatex overwrites the PDF
# with the very defect the converter refused to pass.
#
# The figures are a build input, not a committed artefact of this script's own
# making, so they are regenerated first from the computed contrasts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/results/analysis/figures.py"
python3 "$ROOT/results/analysis/stimuli_appendix.py"
python3 "$ROOT/build/md2tex.py" workshop build/workshop-sections
# The canonical bib carries the full paper's audit notes; the workshop
# bibliography gets publication status only.
python3 "$ROOT/build/clean_bib.py" "$ROOT/review/references.bib" \
        "$ROOT/build/references-workshop.bib"
cd "$ROOT/build"
pdflatex -interaction=nonstopmode workshop.tex
bibtex workshop
pdflatex -interaction=nonstopmode workshop.tex
pdflatex -interaction=nonstopmode workshop.tex
echo "built: $ROOT/build/workshop.pdf"
pdfinfo workshop.pdf | grep -i '^Pages'
