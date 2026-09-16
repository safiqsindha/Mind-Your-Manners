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
python3 "$ROOT/build/md2tex.py" workshop build/workshop-sections
cd "$ROOT/build"
pdflatex -interaction=nonstopmode workshop.tex
bibtex workshop
pdflatex -interaction=nonstopmode workshop.tex
pdflatex -interaction=nonstopmode workshop.tex
echo "built: $ROOT/build/workshop.pdf"
pdfinfo workshop.pdf | grep -i '^Pages'
