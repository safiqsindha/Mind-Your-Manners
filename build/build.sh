#!/usr/bin/env bash
# Fail-fast build. md2tex.py's nonzero exit MUST stop the chain: it exits
# nonzero on a failed pandoc conversion or an unconverted citation, and if the
# LaTeX run proceeds anyway it overwrites main.pdf with the very defect the
# script refused to pass.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/build/md2tex.py"
cd "$ROOT/build"
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
echo "built: $ROOT/build/main.pdf"
