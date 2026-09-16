# Stage 2 readiness — environment, inventory, and plan

Date: 2026-09-16
Status: **prep only.** No Stage 2 verification has been performed. Awaiting go-ahead.

---

## 1. The LibreOffice prerequisite — RESOLVED

You asked to confirm LibreOffice recalculation works before trusting any formula-graded score.
It does, but this container needed a fix first, and the fix is worth recording because it is
exactly the silent-failure mode your CI comment warns about.

**What happened.** The recalculation tests failed here, 5 of 15:

```
FAILED tests/test_libreoffice_recalc.py::test_recalculates_a_real_formula
FAILED tests/test_formula_recalculation.py::test_recalculation_makes_a_formula_turn_gradable
FAILED tests/test_grader_recalculation.py::test_uncached_ground_truth_formula_is_recalculated_before_comparison
FAILED tests/test_grader_recalculation.py::test_answer_file_recalculation_is_memoized
FAILED tests/test_grader_recalculation.py::test_a_second_grader_instance_reuses_the_cached_conversion
```

The visible error was `Warning: failed to launch javaldx - java may not function correctly`,
followed by `Error: source file could not be loaded`.

**The javaldx warning is a red herring.** Java is present and fine (OpenJDK 21.0.10). The actual
cause: **`libreoffice-calc` was not installed.** This container ships `libreoffice-core` and
`libreoffice-common` only, so `soffice` exists and answers `--version` — but cannot load a
spreadsheet.

**This is the exact trap your `ci.yml` comment describes**, one layer deeper. The comment says the
tests are "skipif-gated on soffice/libreoffice, so without an explicit install they depend on
whatever the runner image happens to ship". Here the gate *passed* — `soffice` was on `PATH` — and
the tests ran and failed rather than skipping. A `soffice --version` check is not sufficient to
establish that recalculation will work; only the Calc component makes that true.

**Worth considering for `ci.yml`:** the "Verify LibreOffice is present" step runs
`soffice --version || libreoffice --version`, which would have passed in this container's broken
state. A component-level check (`dpkg -s libreoffice-calc`, or a one-cell convert round-trip)
would catch it. Not changed — flagging only.

**After `apt-get install libreoffice-calc`:**

```
tests/test_libreoffice_recalc.py
tests/test_formula_recalculation.py
tests/test_grader_recalculation.py
tests/test_recalc_timeout.py
tests/test_regrade_staleness.py
                                          21 passed in 10.43s
```

**Conclusion: formula-graded results are trustworthy in this environment, and the guard that
protects them is real and passing.** Stage 2 can rely on formula-graded scores. Note the
environment is ephemeral — the Calc install does not survive a new container, so this check must
be repeated in any fresh session before formula-graded numbers are touched again.

## 2. Environment now provisioned

| Item | Status |
|---|---|
| `arxiv` | installed, 4.0.1 — `paper-review` reviewers can do prior-art lookups |
| `pytest` | installed, 9.1.1 — was absent |
| `requirements.txt` | installed (`openpyxl` 3.1.5 etc.) — was absent |
| `libreoffice-calc` | installed — see §1 |
| Full test suite | baseline run recorded below |

## 3. Where the data actually is

Your brief left the results path blank. Resolved without needing you:

- **`results_archive/`** — 46 files, 25 MB, **committed to git**. This is the real raw record:
  `core_gpt-luna_*_records.json`, `*_regraded.json`, `validation_gate_n100_*.json`, and
  `progress_regrade_corrected/study2_*_progress.json.gz`.
- **`results/raw/`** — empty but for `.gitkeep`, and **gitignored by design** (`.gitignore` lines
  10–18). Not a gap.
- **`results/analysis/`** — the five analysis scripts plus `regrade_manifest.json`. Generated
  `.json`/`.jsonl` here are also gitignored.
- **`RESULTS.md`** — 113 KB at repo root.

So number-tracing in Stage 2 runs prose → `RESULTS.md` → `results_archive/*.json`, with
`results/analysis/*.py` as the transformation layer.

## 4. Scale of the number-tracing task

Numeric tokens in prose, excluding block quotes, section references, citation keys and arXiv IDs:

| Section | Count |
|---|---:|
| `00-abstract.md` | 20 |
| `01-introduction.md` | 41 |
| `02-design-and-statistics.md` | 188 |
| `03-confound-in-prior-materials.md` | 156 |
| `04-demand-not-manners.md` | 300 |
| `05-closing-cues.md` | 95 |
| `06-per-turn-regrade.md` | 280 |
| `07-what-replicated.md` | 222 |
| `08-limitations.md` | 56 |
| **Total** | **1,358** |

That is a raw token count, not a claim count — it includes table cells, *p*-values, CI bounds and
run counts, and many are repeats of the same underlying quantity carried between sections.

**Proposed approach, for your approval:** rather than chase all 1,358, work outward from the
claims that carry the argument — every figure in `00-abstract.md` and `01-introduction.md` (61
tokens), since the paper states those are all carried from later sections, plus each headline
effect in §4–§7. A number that appears in the abstract and cannot be traced is a blocker; a table
cell that cannot be traced is a defect but not a submission blocker. Say if you want the
exhaustive pass instead.

Note the paper's own §3.2 and §3.3 already do this against *other* people's tables, and §7 audits
its own instability, so the internal-consistency bar it has set for itself is high.

## 5. Methods claims → where to check them

The five items in your brief, mapped to the code and to the tests that already pin them:

| Claim | Harness code | Existing test |
|---|---|---|
| Seven-level tone scale | `harness/tone_wrappers.py`, `harness/study2/runner.py`, `harness/study2/analysis.py` | `test_tone_wrappers.py`, `test_mind_your_tone.py` |
| ±5-token length matching | `harness/cli.py`, `harness/study2/runner.py` | `test_design_integrity.py` |
| Model roster | `harness/config.py`, `harness/providers/*` | `test_roster.py` |
| Provider pinning | `harness/providers/openai_compatible.py`, `harness/cli.py` | `test_openrouter_pinning.py` |
| Thinking axis | `harness/study2/thinking_preflight.py`, `harness/providers/*` | `test_thinking_preflight.py` |
| Grading | `harness/study2/grader.py`, `harness/study2/progress.py` | the five recalculation suites in §1 |

**A caution for Stage 2:** these tests pin the harness against *itself*. Passing tests show the
code is internally consistent; they do not show the **methods prose matches the code**. That
comparison is the actual Stage 2 task and has not been done.

## 6. What Stage 2 will NOT be able to do as specified

Your brief says to use open-scholar's verification skills. Two constraints from the setup audit
still hold:

1. **`scholar-verify` expects `output/tables/`, `output/figures/`, `results-registry.csv`** — a
   project layout `/scholar-init` creates. This repo does not have it. The skill will need
   `--artifacts-dir` and `--no-manuscript` handling, or it will auto-detect nothing. Its default
   output goes to `output/verify/`; I will override to `review/`.
2. **Its `PreToolUse` data guard is not installed and should stay uninstalled** — it fails closed
   on data-file reads, which would block exactly the `results_archive/*.json` reads Stage 2 needs.

Neither blocks the work; both change how the skill gets invoked.

## 7. Full test suite baseline

Recorded so that any Stage 2 change can be compared against a known-good starting point.

```
$ python3 -m pytest tests/ -q
362 passed in 48.32s
```

**362 passed, 0 failed, 0 skipped**, on `d1bd17f` with `libreoffice-calc` present. Nothing is
being skipped silently — which, given §1, is the number that actually matters.
