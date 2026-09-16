# Stage 2 — Claims vs. evidence

Date: 2026-09-16
Scope: exhaustive, as instructed. Every numeric token in the prose was extracted and traced.
Nothing in `paper/`, `results/`, `results_archive/` or `RESULTS.md` was modified.

---

## 0. Headline

**The single most important finding: three of the five analysis scripts could not run as
committed, and a fourth reported missing inputs.** Every one of the paper's derived statistics
flows through those scripts. Once the inputs were located and materialised, all five ran and
95.5% of the paper's numbers traced. The numbers are sound; the *reproducibility path* is broken,
and a replication reviewer would hit this in their first ten minutes.

| Result | Count | % |
|---|---:|---:|
| Traced to a source | 1,226 | 95.5 |
| Traced after rounding | 5 | 0.4 |
| Untraced | 53 | 4.1 |
| **Total numeric tokens** | **1,284** | |

Of the 53 untraced, 42 are other papers' numbers quoted in §1 and §3 — correctly absent from our
data. Of the remaining 11, five are external, one is a task ID, one traces on closer inspection,
and **four are genuinely unaccounted for**.

---

## 1. The reproducibility defect

### 1.1 What happened

Running the five committed analysis scripts from a clean checkout:

| Script | Result as committed |
|---|---|
| `accuracy_null_mde.py` | **FileNotFoundError** |
| `replication_table.py` | **FileNotFoundError** |
| `timing_is_a_proxy.py` | **FileNotFoundError** |
| `regrade_summary.py` | ran, but reported `MISSING (regrade not yet written): 6 arms` |
| `praise_turn_vs_trajectory.py` | ran cleanly |

All three hard failures share one cause. The scripts read from `results/analysis/`:

```
FileNotFoundError: .../results/analysis/study2_core_gpt-luna-ceiling20-Q0_control_records.json
FileNotFoundError: .../results/analysis/study2_core_gpt-luna-cross7-L7_threatening_progress.json
```

The data exists — in `results_archive/`, under different names and gzipped:

| Script expects (in `results/analysis/`) | Actually committed (in `results_archive/`) |
|---|---|
| `study2_core_gpt-luna-ceiling20-Q0_control_records.json` | `ceiling20_Q0_control_records.json.gz` |
| `study2_core_gpt-luna-ceiling20-Q5_remains_only_records.json` | `ceiling20_Q5_remains_only_records.json.gz` |
| `study2_core_gpt-luna-cross7-L7_threatening_progress.json` | `progress_regrade_corrected/study2_core_gpt-luna-cross7-L7_threatening_progress.json.gz` |

So three things diverge at once: **directory, filename, and compression.**

### 1.2 Why this matters more than it looks

`results/analysis/*.json` is **gitignored** (`.gitignore` line 11). That is a reasonable choice —
those are derived artifacts. But the consequence is that the scripts' expected inputs can never be
present in a fresh clone, and the archive that *is* committed does not use the names they look for.
**The pipeline is unreproducible from the repository as published**, even though every ingredient
is committed.

`praise_turn_vs_trajectory.py` carries this comment at the top:

> "Repo-relative, like every other script here. This was an absolute path into a differently-named
> checkout, so the script could not be re-run as committed."

So this class of bug was found and fixed in one script. The same audit was not applied to the
other four.

### 1.3 What unblocked it

Materialising the archive into the names the scripts expect — copy the plain `.json`, ungzip
`ceiling20_*` under the `study2_core_gpt-luna-ceiling20-<ARM>_records.json` name, ungzip
`progress_regrade_corrected/*.json.gz` to their own stems. 45 files. After that:

```
accuracy_null_mde            exit=0   regrade_summary        exit=0
replication_table            exit=0   timing_is_a_proxy      exit=0
praise_turn_vs_trajectory    exit=0
```

All five run, including `regrade_summary`, which no longer reports missing arms.

### 1.4 Recommendation — now implemented

`results/analysis/_inputs.py` materialises the archive into the expected names, and every script
calls it on startup. Freshness is decided by content, not existence: a derived file is rewritten
only when its bytes differ from what the archive yields, through a temporary file and an atomic
rename, so a pull that changes a committed archive reaches the scripts on their next run and a
file truncated by an interrupted run is repaired rather than trusted. The first version treated
an existing file as fresh; a second review finding caught that, and
`tests/test_inputs_materialise.py` now pins the fresh-clone, changed-archive, truncated-file,
no-churn and failed-write cases. Verified by `git clean -X`-ing `results/analysis/` (which
removes only the ignored files, leaving the tracked `regrade_manifest.json` in place) and running
all six scripts: all exit 0. This was done after a review bot found that the new
`turn_count_family.py` had inherited the very defect this section documents — the case for fixing
it in one shared entry point rather than per script.

One caution learned the hard way: simulating a fresh checkout with `mv results/analysis/*.json`
also sweeps up the *tracked* manifest, and `regrade_summary.py`'s staleness guard then fires as
designed. Use `git clean -X`, not a glob.

---

## 2. Exhaustive number trace

### 2.1 Method

Every numeric token in `paper/00`–`paper/08` was extracted (1,284 of them), excluding block quotes,
headings, section references, citation keys, arXiv IDs, DOIs and URLs. Each was matched against a
26,022-string corpus built from `RESULTS.md`, `results/analysis/*.py|txt|json`, all 46
`results_archive` files (JSON walked to scalar values, with 1–4 decimal-place roundings), and the
recomputed output of all five analysis scripts.

Before recomputation: 90.4% traced. After: **95.5%**. The 242 new strings the recomputation
contributed are exactly the derived statistics — CI bounds, Cochran's *Q*, standard errors — that
exist nowhere on disk until a script produces them.

### 2.2 The residue

**Other papers' numbers (42) — correctly untraceable.** 40 in §3, which quotes Kumar & Dobariya's
Tables 2 and 3 and Dobariya & Kumar's Table 1 in full, and 2 in §1.1 (`82.2%`, `82.6%`, the GPT-4o
re-run figures). These *should* not be in our results files. Their verification is a
read-against-the-PDF task, and §3.7 records that both those checks were done.

**External but inside our-results sections (5) — correctly untraceable, all attributed in-line.**

| Value | Section | Attribution in the prose |
|---|---|---|
| `2,729` test cases | §2.1 | SpreadsheetBench's own dataset size, `[ma-2024]` |
| `3.05` | §2.4 | "Miller reports a clustered-to-CLT standard-error ratio of 3.05" |
| `90.5%` | §6.5 | "Huang et al. …, whose 'No Change' rates are 90.5%" |
| `4.42%`, `2.58%` | §7.1 | EmotionPrompt's relative improvements |

**Extractor false positive (1).** `54513` in §6.2 is a **task ID**, not a statistic — confirmed
present as a `task_id` in `study2_core_gpt-luna-ceiling20-Q0_control_records.json`.

**Traces on inspection (1).** `0.085` (§2.3) appears in `regrade_summary`'s recomputed output; the
matcher missed it on decimal formatting.

### 2.3 Genuinely unaccounted for — 4 numbers

These are ours, and no committed script produces them:

| Value | Where | Claim |
|---|---|---|
| `99.3%` | §6.6 | "stage-1 Luna is 99.3% by turn 10" |
| `99.8%` | §6.6 | "and 99.8% by turn 14 (one trajectory peaks at 15)" |
| `0.095` | §6.7 | "p = 0.095 to 0.65, on 19–34 tasks" |
| `8,593` | §5.4 | "−5,880 tokens, [−8,593, …]" — the lower CI bound |

None is load-bearing: §6.6's two are a robustness aside on peak-turn distribution, §6.7's is the
lower end of a range the paper itself labels underpowered, and §5.4's is one bound of a CI whose
point estimate traces. But under your own §9 standard they are unsourced, and the honest options
are to add them to a script's output or to cite the computation in-line.

**4 unaccounted numbers out of 1,284 is a good result.** For comparison, the paper's own §7 already
concedes that point estimates move between re-measurements; the tracing here says the *reported*
values are almost entirely reproducible from committed data.

---

## 3. Methods text vs. harness code

Checked against the code, not against the tests — the tests pin the harness to itself.

| Claim | Verdict | Evidence |
|---|---|---|
| **Seven-level tone scale** | ✅ confirmed | `INTERJECTIONS` and `TONE_WRAPPERS` in `harness/tone_wrappers.py` each hold exactly 7 entries, `L1_sycophantic` → `L7_threatening`, matching the scale adopted from `[kumar-dobariya-2026]` |
| **Same opening stem** | ✅ confirmed | all seven L-series strings open with `Checking in`, exactly as §1.2 states |
| **Length matching** | ⚠️ confirmed within tolerance | measured span **27–28 tokens** across both series (spread 1). §1.2 says "exactly 28 tokens" |
| **Model roster** | ✅ present | `ROSTER` in `harness/config.py`, dated 2026-09-10, superseding a 5-model Gemini-anchored set; `MODELS_BY_KEY` derived from `ALL_MODELS` |
| **Provider pinning** | ✅ present | `harness/providers/openai_compatible.py`, pinned in `test_openrouter_pinning.py` |
| **Thinking axis** | ✅ present | `thinking_enabled` on `ModelConfig` with a `with_thinking()` helper; `config.py` explicitly warns the axis is not a uniform "thinking on/off" |
| **Grading** | ✅ confirmed working | see §4 |

### The one discrepancy

§1.2 and the abstract both say the interjection is "**exactly 28 tokens**". Counting with a regex
word/punctuation tokenizer gives **27 for `L1_sycophantic` and `L4_neutral`, 28 for the other
five**; the Q-series is likewise 27–28, with `Q0_control` at 27.

This is very likely a tokenizer difference — the paper presumably counts with the model's
tokenizer, where those two strings may well hit 28 — rather than an error. But "exactly 28" is a
strong word for a quantity that varies by one under a reasonable alternative count, and it is the
sort of claim a reviewer checks. **Suggest "28 tokens (27–28 by whitespace-and-punctuation count)"
or simply "length-matched to within one token".** The design claim it supports — that being
interrupted does not covary with what the interruption says — is unaffected either way.

---

## 4. Formula-graded results and LibreOffice

**Resolved, and the way it failed is the finding.**

The five recalculation suites failed in this container with `failed to launch javaldx — java may
not function correctly`, followed by `Error: source file could not be loaded`. The javaldx warning
is a red herring: Java is present and healthy (OpenJDK 21.0.10).

The real cause: **`libreoffice-calc` was not installed.** Only `libreoffice-core` and
`libreoffice-common` were, so `soffice` existed and answered `--version` — while being unable to
load a spreadsheet.

This is precisely the failure mode `ci.yml`'s own comment warns about, one layer deeper. The
`skipif` gate passed, because `soffice` was on `PATH`; the tests ran and *failed* rather than
skipping. **The workflow's "Verify LibreOffice is present" step — `soffice --version ||
libreoffice --version` — would also have passed in that broken state.** A component check
(`dpkg -s libreoffice-calc`) or a one-cell convert round-trip would not have.

After installing Calc: **21/21 recalculation tests pass**, and the full suite is **362 passed, 0
failed, 0 skipped**. Formula-graded results are trustworthy here.

⚠️ The container is ephemeral. This check must be repeated in any fresh session before
formula-graded numbers are relied on again.

---

## 5. Cited source supports attached claim

Stage 1 verified that every cited work **exists** and that its metadata is right. Stage 2's
remaining question — does each source *support* the claim attached to it — is answerable in full
only against the PDFs, which for 20 of 23 entries the project's own literature review already did
and logged (`Literature review/03-verification-log.md`, which records 15 citation-level errors it
found and corrected, including author counts, misattributed quotes and spliced table rows).

What I could check independently:

- **The three works added in Stage 1** are cited from their abstracts, and §9 says so. Each
  in-text claim was checked against its source abstract word by word — see
  `review/03-stage1-closeout.md`. All three hold, and none carries a number into the prose.
- **§3.2's characterisation of `[kumar-dobariya-2026]`** reproduces that paper's Table 2 and
  Table 3 and separates "their numbers" from "our coding" in the table header. That is the right
  standard and it is met.
- **`[lakens-2017]` and `[miller-2024]`** are explicitly distinguished in §9 ("Cited for
  equivalence testing and **not** `[miller-2024]`, which contains none"), which is the kind of
  precision that usually indicates the sources were actually read.

**One gap, carried from Stage 1:** the three new sources still need reading in full. Until then
§9's outstanding-items block correctly says three items are open.
