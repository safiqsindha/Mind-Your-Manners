<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img src="assets/banner-light.svg" alt="Mind Your Manners" width="100%">
  </picture>
</p>

# Mind your manners? LLM-agent persistence tracks demand, not social register

**[Paper (v1.0, PDF)](paper/mind-your-manners-v1.0.pdf)** · [Project page](https://safiqsindha.github.io/Mind-Your-Manners/) · [Long technical report](build/main.pdf) · [Cite](#citation)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX) <!-- TODO: replace XXXXXXX with the Zenodo DOI once v1.0.0 is minted -->
![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)
![Tests](https://img.shields.io/badge/tests-422%20passing-22c55e?style=flat-square)

Does the tone of a message change what an LLM agent *does*? A coding agent works through 50
SpreadsheetBench tasks, graded by the benchmark's own evaluator. Partway through, one 28-token
note is appended to its tool output. Every note is length-matched and opens with the same words,
so only what it says varies. Six mid-task runs on two models (GPT-5.6 Luna and GLM 5.3 Flash):
9,850 scheduled trajectories, 6,616 in the primary analysis.

## Findings

- **Implied demand, not register, drives persistence.** An affect-free "please continue working"
  adds +1.17 turns; a length-matched insult with no demand does nothing (−0.08, 95% CI
  [−0.40, +0.24] at a ten-turn budget). Very polite (+0.70) and very rude (+0.71) land together.
- **Praise and closing cues shorten trajectories.** Praise removes 0.59 turns; a note saying no
  further notes will follow removes 1.44. Why is left open.
- **The extra turns mostly change nothing.** On the main model, 56–93% of each clear turn-count
  effect is steps after which the graded answer is unchanged.
- **No accuracy effect.** None survives correction or replication; pooled contrasts are
  equivalent to zero within ±4 points (an exploratory bound).

Scope: two models, one benchmark, one scaffold, one wording per construct, an agent told its
turn budget, and every contrast against a neutral note rather than silence (a neutral note itself
adds +0.45 turns in the one comparison against none). The paper states each limit where it applies.

## Repository

```
paper/          the v1.0 PDF and the long report's markdown source
workshop/       the v1.0 paper's markdown source
build/          LaTeX, bibliography and build scripts for both papers
results/analysis/  every script that produces a number in the papers
results_archive/   the committed run records those scripts read
rating/         the blinded rating: protocol, prompt, stimuli, ratings, scorer
harness/        the agent loop, sandbox, grader, providers and CLI
tests/          pytest suite (mock provider, no API keys)
RESULTS.md      chronological lab notebook, including withdrawn claims
docs/           the pre-release README, kept as a detailed project record
```

## Reproducing

No API access is needed to check the papers' numbers.

```bash
pip install -r requirements.txt
python -m pytest -q                            # 422 tests
python results/analysis/turn_count_family.py   # primary outcome, 22-contrast family
python results/analysis/accuracy_null_mde.py   # accuracy, pooling and equivalence
python results/analysis/regrade_summary.py     # per-turn progress and redundant steps
python rating/score.py                         # blinded-rating agreement
bash build/build-workshop.sh                   # rebuild the v1.0 paper (needs pandoc, LaTeX)
```

New agent runs go through `python -m harness.cli`. Every command is a dry run on a mock provider
unless `--live` is passed, and live runs need an OpenRouter key in `.env` (see `.env.example`).
SpreadsheetBench data is cloned from
[RUCKBReasoning/SpreadsheetBench](https://github.com/RUCKBReasoning/SpreadsheetBench) and kept out
of this repository.

## Citation

```bibtex
@techreport{sindha2026mindyourmanners,
  title       = {Mind your manners? {LLM}-agent persistence tracks demand, not social register},
  author      = {Sindha, Safiq},
  institution = {Independent Researcher},
  type        = {Working paper},
  year        = {2026},
  version     = {1.0.0},
  doi         = {10.5281/zenodo.XXXXXXX},
  url         = {https://github.com/safiqsindha/Mind-Your-Manners}
}
```

Machine-readable metadata is in [`CITATION.cff`](CITATION.cff).

## License

Code and data: [MIT](LICENSE). SpreadsheetBench is CC BY-SA 4.0; keep its attribution and license
on anything extracted from it.
