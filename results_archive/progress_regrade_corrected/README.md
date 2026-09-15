# Corrected per-turn regrade

28 arms, regraded 2026-09-14/15 after `progress.py` was found to be blind to
formula-writing turns: it read agent output with `data_only=True` and never
recalculated, so any turn answering with `=SUMIFS(...)` had no cached value,
read as `None`, and scored 0.0 -- indistinguishable from a turn that wrote
nothing. `grader.py` had always recalculated through LibreOffice; the regrade
had not.

**Validation of the fix.** Benchmark-passed trajectories scoring a final match
of 1.0 went from **29.4% to 94.4%** (119/126) on the probe control arm. The
residual seven are all on one task (54513, a one-cell graded range) and all
score exactly 0.0 -- a systematic regrade miss on that task, undiagnosed. It is
NOT the benchmark's audited false-negative rate: that error runs the other way,
and the benchmark's audited false-discovery rate is 0%.

These files are archived here because `results/analysis/*.json` is gitignored
and the regrade costs about four machine-hours to reproduce. They are gzipped
JSON, one per arm, in the same schema `progress_for_run` writes.

Read one with:

    import gzip, json
    rows = json.loads(gzip.open(path).read())

## What changed in the findings

The redundant-step effects all survived, roughly 20% smaller, with the same
signs and significance. The progress effect did not survive as a null: the
three measurements of the continue signal on `final_match` went from
+0.014 / +0.061 / +0.019 (one hit, two nulls) to **+0.026 / +0.034 / +0.025**,
pooling to **+0.028, 95% CI [+0.005, +0.052], p = 0.022** under a bootstrap
that resamples tasks jointly across runs (the runs share their 50 tasks), with
Cochran's Q = 0.20 on 2 df. Treating the runs as independent would give
p = 0.0038; the paper reports the weaker figure. What the paper had reported as run-to-run instability was the
instrument.

## Reproducing

    python -m harness.cli study2 progress --raw results/raw/<arm>.jsonl --arm <arm>

Then `results/analysis/regrade_summary.py`, which refuses to compare any arm
whose regrade predates `harness/study2/progress.py` -- comparing a fresh
control against stale arms manufactured a clean -0.36 effect at p < 0.0001
during the rollout.
