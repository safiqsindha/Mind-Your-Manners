"""Tests for three design-level holes found in a pre-core-run review.

Unlike most of this suite these are not about crashes. Each one could have
produced a plausible-looking NUMBER that was wrong, which is worse: a crash
announces itself, a confound does not.
"""
from __future__ import annotations

import collections
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch

import openpyxl
import pytest

from harness.providers.base import ModelConfig
from harness.study2.runner import _run_tag
from harness.study2.sandbox import execute_python_on_workbook

LIST_SIBLINGS = """
import os
d = os.path.dirname(WORKBOOK_PATH)
print("SIBLINGS:", sorted(os.listdir(d)))
"""


def _model(key: str) -> ModelConfig:
    return ModelConfig(
        key=key, provider="mock", model_id=f"x/{key}",
        display_name=key, temperature=0.0, max_tokens=512,
    )


# --- 1. Answer-key isolation ----------------------------------------------
# SpreadsheetBench stores ground truth beside the input:
# spreadsheet/59196/1_59196_input.xlsx next to 1_59196_answer.xlsx. With
# WORKBOOK_PATH pointing into the dataset, one os.listdir reached the answer,
# and the sandbox does not restrict filesystem access.

def _dataset_dir(tmp_path: Path) -> Path:
    """A directory shaped like SpreadsheetBench's: input beside answer."""
    d = tmp_path / "spreadsheet" / "59196"
    d.mkdir(parents=True)
    for name, value in (("1_59196_input.xlsx", 1), ("1_59196_answer.xlsx", 999)):
        wb = openpyxl.Workbook()
        wb.active["A1"] = value
        wb.save(d / name)
    return d


def test_model_code_cannot_see_the_answer_file(tmp_path: Path):
    """The whole point: a model listing its workbook's directory must not
    find the ground truth there."""
    data = _dataset_dir(tmp_path)

    result = execute_python_on_workbook(
        LIST_SIBLINGS, data / "1_59196_input.xlsx", tmp_path / "work"
    )

    assert result.returncode == 0, result.stderr
    assert "_answer" not in result.stdout, (
        f"answer key reachable from the sandbox: {result.stdout}"
    )


def test_the_workbook_the_model_reads_is_a_copy_not_the_dataset_file(tmp_path: Path):
    data = _dataset_dir(tmp_path)
    workdir = tmp_path / "work"

    execute_python_on_workbook(
        "print('PATH:', WORKBOOK_PATH)", data / "1_59196_input.xlsx", workdir
    )

    copied = workdir / "1_59196_input.xlsx"
    assert copied.exists(), "input should be copied into the workdir"
    assert copied.parent == workdir


def test_the_copy_has_the_same_contents_as_the_original(tmp_path: Path):
    """Isolation must not change what the model is working on."""
    data = _dataset_dir(tmp_path)
    src = data / "1_59196_input.xlsx"

    result = execute_python_on_workbook(
        "import openpyxl\nprint('VAL:', openpyxl.load_workbook(WORKBOOK_PATH).active['A1'].value)",
        src, tmp_path / "work",
    )

    assert "VAL: 1" in result.stdout, result.stdout
    assert (tmp_path / "work" / src.name).read_bytes() == src.read_bytes()


def test_the_original_dataset_file_is_not_modified(tmp_path: Path):
    """Model code writing to WORKBOOK_PATH must hit the copy, never the
    benchmark's own input file."""
    data = _dataset_dir(tmp_path)
    src = data / "1_59196_input.xlsx"
    before = src.read_bytes()

    execute_python_on_workbook(
        "import openpyxl\nwb = openpyxl.load_workbook(WORKBOOK_PATH)\n"
        "wb.active['A1'] = 'CLOBBERED'\nwb.save(WORKBOOK_PATH)",
        src, tmp_path / "work",
    )

    assert src.read_bytes() == before, "model code modified the dataset input"


def test_the_extension_is_preserved_so_xlsm_handling_still_works(tmp_path: Path):
    """Real model code branches on WORKBOOK_PATH.lower().endswith('.xlsm')."""
    src = tmp_path / "book.xlsm"
    wb = openpyxl.Workbook()
    wb.active["A1"] = 1
    wb.save(src)

    result = execute_python_on_workbook(
        "print('EXT_OK:', WORKBOOK_PATH.lower().endswith('.xlsm'))", src, tmp_path / "work"
    )

    assert "EXT_OK: True" in result.stdout, result.stdout


# --- 2. Tone order randomisation ------------------------------------------
# A fixed L1..L7 sequence confounds tone with position-in-burst. Retry backoff
# accumulates across consecutive calls, so the last tone would systematically
# meet worse provider conditions than the first.

def _tone_sequences(tone_seed: int, n_tasks: int = 8):
    """Run the batch loop with everything stubbed, capturing tone order."""
    from harness.study2 import runner

    seen: dict[str, list[str]] = collections.defaultdict(list)

    class _Task:
        def __init__(self, tid):
            self.task_id = tid
            self.instruction_type = "Cell-Level Manipulation"
            self.instruction = "do it"
            self.answer_position = "A1"
            self.input_spreadsheet_paths = [Path("in.xlsx")]
            self.answer_spreadsheet_paths = [Path("ans.xlsx")]

    from harness.study2.agent_loop import Trajectory

    def fake_run(tracker, model, task_id, instruction, input_path, workdir, *, tone_level, trial, **kw):
        seen[task_id].append(tone_level)
        return Trajectory(task_id=task_id, tone_level=tone_level, trial=trial)

    def fake_grade(grader, task, traj, workdir):
        from harness.study2.grader import GradeResult
        return GradeResult(task.task_id, False, 3, 0, 0.0, [])

    with patch("harness.study2.runner.run_react_multi_round", side_effect=fake_run), \
         patch("harness.study2.runner._grade_trajectory", side_effect=fake_grade), \
         patch("harness.study2.runner.no_op_passes", return_value=False):
        runner.run_condition_batch(
            [_model("m")], [_Task(f"t{i}") for i in range(n_tasks)],
            grader=None, out_dir=Path("/tmp/_tone_order_probe"), phase="probe",
            budget_cap_usd=1e6, n_trials=1, tone_seed=tone_seed,
        )
    return seen


def test_tone_order_is_not_the_same_every_task():
    """The bug: identical L1..L7 for every task and trial."""
    seen = _tone_sequences(tone_seed=0)
    orders = {tuple(v) for v in seen.values()}
    assert len(orders) > 1, f"tone order identical across all tasks: {orders}"


def test_every_tone_still_runs_exactly_once_per_task():
    """Shuffling must not drop or duplicate a condition."""
    from harness.tone_wrappers import TONE_ORDER

    for task_id, tones in _tone_sequences(tone_seed=0).items():
        assert sorted(tones) == sorted(TONE_ORDER), f"{task_id} got {tones}"


def test_tone_order_is_reproducible_for_a_seed():
    assert _tone_sequences(tone_seed=7) == _tone_sequences(tone_seed=7)


def test_a_different_seed_gives_a_different_arrangement():
    assert _tone_sequences(tone_seed=1) != _tone_sequences(tone_seed=2)


# --- 3. Per-run file namespacing ------------------------------------------
# Four models run as concurrent processes shared one raw log, one records
# file, and -- worst -- one SpendTracker resume source, so each model would
# count all four models' spend against its own cap.

def _live(key: str) -> ModelConfig:
    return replace(_model(key), provider="openai_compatible")


def test_a_single_model_run_gets_its_own_tag():
    assert _run_tag([_live("gpt-luna")]) == "gpt-luna"


def test_two_single_model_runs_do_not_collide():
    """The parallel case: each process must write its own files."""
    tags = {_run_tag([_live(k)]) for k in ("gpt-luna", "glm-current", "deepseek-current", "qwen-current")}
    assert len(tags) == 4


def test_a_multi_model_run_in_one_process_shares_one_tag():
    """Correct: they are genuinely one run under one budget cap."""
    assert _run_tag([_live("a"), _live("b")]) == "multi"


# A dry run forces every model onto the mock provider but used to write to the
# same filenames as a live run. A mock `core` invocation left 48 fabricated
# rows in study2_core_gpt-luna.jsonl, which the next live run resumed its
# budget from and would have analysed alongside real results.

def test_a_dry_run_does_not_write_where_a_live_run_writes():
    assert _run_tag([_model("gpt-luna")]) != _run_tag([_live("gpt-luna")])


def test_a_dry_run_tag_says_so():
    assert _run_tag([_model("gpt-luna")]) == "gpt-luna-dryrun"


def test_one_mock_model_is_enough_to_mark_the_whole_run():
    """--dry-run mocks everything, but a partially-mocked run is still not
    live data and must not land in a live file."""
    assert _run_tag([_live("a"), _model("b")]).endswith("-dryrun")


# --- 4. The validation gate's spend log was still shared -------------------
# Fix 3 namespaced the core path's files but left the gate's SpendTracker log
# on one fixed name. The gate is the phase that runs four models AT ONCE by
# design, and SpendTracker resumes its running total from that file, so each
# model would count all four models' spend against its own $10 cap.

def _gate_tracker_path(model_key: str, out_dir: Path) -> Path:
    """Run the gate with zero tasks and report where SpendTracker was pointed."""
    from harness.study2 import runner

    seen: list[Path] = []

    class _FakeTracker:
        total_usd = 0.0

        def __init__(self, path, **kw):
            seen.append(Path(path))

        def close(self):
            pass

    with patch("harness.study2.runner.SpendTracker", _FakeTracker):
        runner.run_validation_gate(_model(model_key), [], grader=None, out_dir=out_dir)
    return seen[0]


def test_two_models_gating_do_not_share_a_spend_log(tmp_path: Path):
    a = _gate_tracker_path("gpt-luna", tmp_path)
    b = _gate_tracker_path("qwen-current", tmp_path)
    assert a != b, f"both models wrote spend to {a}"


def test_the_gate_spend_log_names_its_model(tmp_path: Path):
    path = _gate_tracker_path("deepseek-current", tmp_path)
    assert "deepseek-current" in path.name, path.name


# --- 5. Model version drift, and reports destroyed by stray runs -----------
# A model_id like "qwen/qwen3.8-flash" is a pointer the provider can repoint
# at a newer dated snapshot at any time. No response body reveals it: the
# response reports the pointer, and the served provider is unchanged. A
# mid-study roll would split the run across two models with every number
# still looking plausible.

def _cfg(key="qwen-current", model_id="qwen/qwen3.8-flash",
         canonical="qwen/qwen3.8-flash-20260826"):
    return ModelConfig(
        key=key, provider="openai_compatible", model_id=model_id,
        display_name=key, temperature=0.0, max_tokens=512,
        canonical_slug=canonical,
    )


def _catalog(*pairs):
    class _R:
        status_code = 200
        @staticmethod
        def json():
            return {"data": [{"id": i, "canonical_slug": c} for i, c in pairs]}
    return _R()


def test_matching_versions_pass_and_are_reported_back(monkeypatch):
    from harness.providers import openai_compatible as oc
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(oc.requests, "get",
                        lambda *a, **k: _catalog(("qwen/qwen3.8-flash", "qwen/qwen3.8-flash-20260826")))
    observed = oc.assert_canonical_slugs([_cfg()])
    assert observed == {"qwen-current": "qwen/qwen3.8-flash-20260826"}


def test_a_repointed_slug_halts_the_run(monkeypatch):
    """The whole point: the pointer now resolves somewhere else."""
    from harness.providers import openai_compatible as oc
    from harness.providers.base import ProviderPinViolation
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(oc.requests, "get",
                        lambda *a, **k: _catalog(("qwen/qwen3.8-flash", "qwen/qwen3.8-flash-20261102")))
    with pytest.raises(ProviderPinViolation) as e:
        oc.assert_canonical_slugs([_cfg()])
    assert "20261102" in str(e.value) and "20260826" in str(e.value)


def test_a_model_vanishing_from_the_catalog_halts_the_run(monkeypatch):
    from harness.providers import openai_compatible as oc
    from harness.providers.base import ProviderPinViolation
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(oc.requests, "get", lambda *a, **k: _catalog(("something/else", "something/else-1")))
    with pytest.raises(ProviderPinViolation):
        oc.assert_canonical_slugs([_cfg()])


def test_an_unreadable_catalog_fails_closed(monkeypatch):
    """Never start a paid run on unverified versions."""
    from harness.providers import openai_compatible as oc
    from harness.providers.base import ProviderError
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")

    class _R:
        status_code = 503
    monkeypatch.setattr(oc.requests, "get", lambda *a, **k: _R())
    with pytest.raises(ProviderError):
        oc.assert_canonical_slugs([_cfg()])


def test_a_small_run_cannot_overwrite_a_large_runs_report(tmp_path: Path):
    """A stray --n-tasks 1 destroyed a completed 100-task report during
    development. Only a committed copy saved the numbers."""
    from harness.cli import _refuse_to_shrink_report
    import json as _json

    p = tmp_path / "study2_validation_gate_glm-current.json"
    p.write_text(_json.dumps({"n_tasks": 100, "n_passed": 28}))

    with pytest.raises(SystemExit):
        _refuse_to_shrink_report(p, {"n_tasks": 1, "n_passed": 0}, force=False)
    assert _json.loads(p.read_text())["n_tasks"] == 100, "the large report must survive"


def test_an_equal_or_larger_run_may_overwrite(tmp_path: Path):
    from harness.cli import _refuse_to_shrink_report
    import json as _json

    p = tmp_path / "r.json"
    p.write_text(_json.dumps({"n_tasks": 100}))
    _refuse_to_shrink_report(p, {"n_tasks": 100}, force=False)
    _refuse_to_shrink_report(p, {"n_tasks": 200}, force=False)


def test_force_overwrite_is_the_explicit_escape_hatch(tmp_path: Path):
    from harness.cli import _refuse_to_shrink_report
    import json as _json

    p = tmp_path / "r.json"
    p.write_text(_json.dumps({"n_tasks": 100}))
    _refuse_to_shrink_report(p, {"n_tasks": 1}, force=True)


# --- 6. The core phase drew from a different pool than everything else ----
# core used sample_only=False (909 tasks) while every other phase used the
# 200-task sample. Both things that make an accuracy interpretable -- the
# no-op manifest and the validation-gate baselines -- were measured on the
# sample, and neither transfers.

def _tasks(n, prefix="t"):
    class _T:
        def __init__(self, i):
            self.task_id = f"{prefix}{i}"
            self.instruction_type = "Cell-Level Manipulation"
    return [_T(i) for i in range(n)]


def test_core_draws_from_the_same_pool_as_the_gate_by_default():
    """The bug: a core draw of 50 overlapped the n=100 gate sample by 2."""
    from harness.study2.runner import select_gate_tasks

    pool = _tasks(200)
    core = {t.task_id for t in select_gate_tasks(pool, n=50, seed=0)}
    gate = {t.task_id for t in select_gate_tasks(pool, n=100, seed=0)}
    assert core <= gate, f"core sample is not inside the gate sample: {sorted(core - gate)[:5]}"


def test_a_bigger_pool_gives_a_different_draw():
    """Why the boundary mattered: same seed, same n, different pool."""
    from harness.study2.runner import select_gate_tasks

    small = {t.task_id for t in select_gate_tasks(_tasks(200), n=50, seed=0)}
    big = {t.task_id for t in select_gate_tasks(_tasks(909), n=50, seed=0)}
    assert len(small & big) < 50, "drawing from a larger pool should not reproduce the sample draw"


def test_every_phase_defaults_to_the_sample():
    """--full-dataset must be opt-in, on every staged phase."""
    import argparse
    from harness.cli import build_parser

    parser = build_parser()
    for phase in ("pilot", "core", "frontier"):
        args = parser.parse_args(["study2", phase])
        assert args.full_dataset is False, f"{phase} defaults to the full dataset"
        opted = parser.parse_args(["study2", phase, "--full-dataset"])
        assert opted.full_dataset is True


# --- 7. The primary outcome had no significance test ----------------------
# token_cost_effect_size reports a relative-variation percentage, pooled
# across tasks, with no p-value -- and cost is the study's PRIMARY outcome.
# Pooling is the defect: tasks differ enormously in how much thinking they
# demand, and that variance swamps any tone effect. Measured on a partial
# Luna core run, pooling gave p=0.81 while the same data clustered by task
# gave p=0.03.

def _token_rows(effect_on_threatening: int, n_tasks: int = 12, seed: int = 0):
    """Tasks with wildly different baseline token demand, plus a real
    threatening-tone bump. Pooled, the task spread hides the bump."""
    import random as _r
    from harness.tone_wrappers import TONE_ORDER

    rng = _r.Random(seed)
    rows = []
    for i in range(n_tasks):
        base = 200 * (i + 1) * 10          # task demand spans 2k..24k
        for tone in TONE_ORDER:
            bump = effect_on_threatening if tone == "L7_threatening" else 0
            rows.append({
                "task_id": f"t{i}", "tone_level": tone, "passed": False,
                "reasoning_tokens": base + bump + rng.randint(-50, 50),
            })
    return rows


def test_a_real_within_task_effect_is_detected():
    from harness.study2.analysis import token_cost_trend_test

    t = token_cost_trend_test(_token_rows(effect_on_threatening=400))
    assert t.p_value < 0.05, f"missed a real effect, p={t.p_value}"
    assert t.observed_slope > 0


def test_no_effect_is_not_invented():
    from harness.study2.analysis import token_cost_trend_test

    t = token_cost_trend_test(_token_rows(effect_on_threatening=0))
    assert t.p_value > 0.05, f"found an effect that is not there, p={t.p_value}"


def test_it_defaults_to_reasoning_not_total_tokens():
    """total_tokens is dominated by the prompt, whose length the tone
    wrapper changes by construction."""
    import inspect
    from harness.study2.analysis import token_cost_trend_test

    assert inspect.signature(token_cost_trend_test).parameters["value_key"].default == "reasoning_tokens"


def test_a_run_without_the_field_says_so_rather_than_scoring_zero():
    """No thinking measurement is not a measurement of no thinking."""
    from harness.study2.analysis import token_cost_trend_test

    rows = [{"task_id": "t0", "tone_level": t, "passed": False} for t in
            ("L1_sycophantic", "L4_neutral", "L7_threatening")]
    with pytest.raises(ValueError, match="reasoning_tokens"):
        token_cost_trend_test(rows)


def test_the_report_carries_both_token_trends():
    from harness.cli import _token_cost_trends

    out = _token_cost_trends(_token_rows(effect_on_threatening=400))
    assert set(out) == {"reasoning_tokens", "total_tokens"}
    assert out["reasoning_tokens"]["p_value"] < 0.05
    assert "unavailable" in out["total_tokens"], "total_tokens absent here, should say so"


def test_reasoning_tokens_are_recoverable_from_the_raw_log(tmp_path: Path):
    """The field was added mid-run. A run recorded before it must not become
    unanalysable on the study's primary outcome."""
    import json as _json
    from harness.study2.analysis import backfill_reasoning_tokens

    raw = tmp_path / "raw.jsonl"
    raw.write_text("\n".join(_json.dumps(r) for r in [
        {"item_id": "t0", "tone_level": "L4_neutral", "trial": 0, "reasoning_tokens": 100},
        {"item_id": "t0", "tone_level": "L4_neutral", "trial": 0, "reasoning_tokens": 50},
        {"item_id": "t0", "tone_level": "L7_threatening", "trial": 0, "reasoning_tokens": 900},
    ]))
    recs = [
        {"task_id": "t0", "tone_level": "L4_neutral", "trial": 0},
        {"task_id": "t0", "tone_level": "L7_threatening", "trial": 0},
    ]
    assert backfill_reasoning_tokens(recs, raw) == 2
    assert recs[0]["reasoning_tokens"] == 150, "per-call values must be summed per trajectory"
    assert recs[1]["reasoning_tokens"] == 900


def test_backfill_leaves_existing_values_alone(tmp_path: Path):
    import json as _json
    from harness.study2.analysis import backfill_reasoning_tokens

    raw = tmp_path / "raw.jsonl"
    raw.write_text(_json.dumps({"item_id": "t0", "tone_level": "L4_neutral", "trial": 0, "reasoning_tokens": 999}))
    recs = [{"task_id": "t0", "tone_level": "L4_neutral", "trial": 0, "reasoning_tokens": 42}]
    assert backfill_reasoning_tokens(recs, raw) == 0
    assert recs[0]["reasoning_tokens"] == 42


def test_backfill_survives_a_torn_final_line(tmp_path: Path):
    """A run still in flight can leave a partial line."""
    import json as _json
    from harness.study2.analysis import backfill_reasoning_tokens

    raw = tmp_path / "raw.jsonl"
    raw.write_text(
        _json.dumps({"item_id": "t0", "tone_level": "L4_neutral", "trial": 0, "reasoning_tokens": 7})
        + '\n{"item_id": "t0", "tone_lev'
    )
    recs = [{"task_id": "t0", "tone_level": "L4_neutral", "trial": 0}]
    assert backfill_reasoning_tokens(recs, raw) == 1
    assert recs[0]["reasoning_tokens"] == 7


# --- 8. A ten-hour run had no resume ---------------------------------------
# The container was restarted at 896 of 1050 trajectories. The incremental
# records survived on disk, so redoing that work would have been a choice.

def _jsonl(path: Path, rows):
    import json as _json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(_json.dumps(r) for r in rows))


def test_recorded_trajectories_are_recognised(tmp_path: Path):
    from harness.study2.runner import completed_trajectories

    _jsonl(tmp_path / "analysis" / "study2_core_gpt-luna_records.jsonl", [
        {"task_id": "t0", "tone_level": "L4_neutral", "trial": 0, "crashed": False},
        {"task_id": "t0", "tone_level": "L7_threatening", "trial": 2, "crashed": False},
    ])
    done = completed_trajectories(tmp_path, "core", "gpt-luna")
    assert done == {("t0", "L4_neutral", 0), ("t0", "L7_threatening", 2)}


def test_a_crashed_trajectory_is_retried_not_skipped(tmp_path: Path):
    """Its usual cause is a transient provider error, not the task."""
    from harness.study2.runner import completed_trajectories

    _jsonl(tmp_path / "analysis" / "study2_core_m_records.jsonl", [
        {"task_id": "t0", "tone_level": "L4_neutral", "trial": 0, "crashed": True},
    ])
    assert completed_trajectories(tmp_path, "core", "m") == set()


def test_a_torn_final_line_is_not_counted_as_done(tmp_path: Path):
    """A process killed mid-write leaves a partial record; that is not
    evidence the trajectory finished."""
    from harness.study2.runner import completed_trajectories

    p = tmp_path / "analysis" / "study2_core_m_records.jsonl"
    p.parent.mkdir(parents=True)
    p.write_text('{"task_id":"t0","tone_level":"L4_neutral","trial":0,"crashed":false}\n{"task_id":"t1","tone_le')
    assert completed_trajectories(tmp_path, "core", "m") == {("t0", "L4_neutral", 0)}


def test_no_records_file_means_nothing_to_skip(tmp_path: Path):
    from harness.study2.runner import completed_trajectories

    assert completed_trajectories(tmp_path, "core", "never-run") == set()


def test_resume_skips_recorded_work_and_keeps_it_in_the_result(tmp_path: Path):
    """The final JSON must be the whole run, not just the part after the
    restart."""
    from harness.study2 import runner
    from harness.study2.agent_loop import Trajectory
    from harness.study2.grader import GradeResult
    from harness.tone_wrappers import TONE_ORDER

    class _Task:
        task_id = "t0"
        instruction_type = "Cell-Level Manipulation"
        instruction = "do it"
        answer_position = "A1"
        input_spreadsheet_paths = [Path("in.xlsx")]
        answer_spreadsheet_paths = [Path("ans.xlsx")]

    # every tone already done except one
    prior = [{"task_id": "t0", "tone_level": t, "trial": 0, "crashed": False, "passed": False}
             for t in TONE_ORDER if t != "L5_rude"]
    _jsonl(tmp_path / "analysis" / "study2_core_m_records.jsonl", prior)

    ran = []

    def fake_run(tracker, model, task_id, instruction, input_path, workdir, *, tone_level, trial, **kw):
        ran.append(tone_level)
        return Trajectory(task_id=task_id, tone_level=tone_level, trial=trial)

    with patch("harness.study2.runner.run_react_multi_round", side_effect=fake_run), \
         patch("harness.study2.runner._grade_trajectory",
               side_effect=lambda *a, **k: GradeResult("t0", False, 3, 0, 0.0, [])):
        out = runner.run_condition_batch(
            [_live("m")], [_Task()], grader=None, out_dir=tmp_path, phase="core",
            budget_cap_usd=1e6, n_trials=1, resume=True,
        )

    assert ran == ["L5_rude"], f"should have run only the missing tone, ran {ran}"
    assert len(out) == 7, f"result must carry all 7 tones, got {len(out)}"


# --- 9. Two live runs of the SAME model shared one records file -----------
# Namespacing per model stopped different models colliding; it did nothing
# about the same model twice. A container restart was reported, a resumed run
# was started -- and the original process had not died. Both appended to one
# records file for half an hour, producing 39 duplicate (task, tone, trial)
# rows that an analysis would have counted as extra trials.

def test_a_second_live_run_of_the_same_model_is_refused(tmp_path: Path):
    import os
    from harness.study2.runner import RunAlreadyInProgress, _exclusive_run

    with _exclusive_run(tmp_path, "core", "gpt-luna"):
        lock = tmp_path / "locks" / "study2_core_gpt-luna.lock"
        assert lock.read_text().strip() == str(os.getpid())
        # a different, live pid holds it
        lock.write_text("1")
        with pytest.raises(RunAlreadyInProgress, match="already running"):
            with _exclusive_run(tmp_path, "core", "gpt-luna"):
                pass
        lock.write_text(str(os.getpid()))


def test_a_stale_lock_from_a_dead_process_is_taken_over(tmp_path: Path):
    """The normal state after a crash, which is exactly when --resume runs."""
    from harness.study2.runner import _exclusive_run

    lock = tmp_path / "locks" / "study2_core_m.lock"
    lock.parent.mkdir(parents=True)
    lock.write_text("999999")  # not a live pid
    with _exclusive_run(tmp_path, "core", "m"):
        pass  # must not raise


def test_different_models_do_not_block_each_other(tmp_path: Path):
    """Running the roster in parallel stays supported."""
    from harness.study2.runner import _exclusive_run

    with _exclusive_run(tmp_path, "core", "gpt-luna"):
        with _exclusive_run(tmp_path, "core", "qwen-current"):
            pass


def test_the_lock_is_released_when_the_run_ends(tmp_path: Path):
    from harness.study2.runner import _exclusive_run

    with _exclusive_run(tmp_path, "core", "m"):
        pass
    assert not (tmp_path / "locks" / "study2_core_m.lock").exists()


def test_the_lock_is_released_even_when_the_run_raises(tmp_path: Path):
    from harness.study2.runner import _exclusive_run

    with pytest.raises(ValueError):
        with _exclusive_run(tmp_path, "core", "m"):
            raise ValueError("budget")
    assert not (tmp_path / "locks" / "study2_core_m.lock").exists()


# --- 10. total_tokens counted the model's thinking twice -------------------
# OpenAI-style usage reports reasoning as completion_tokens_details.
# reasoning_tokens -- a breakdown OF completion, not a bucket beside it. The
# trajectory total added it a third time. On the 4,647-call gpt-luna core log
# the provider's own usage.total_tokens equalled prompt + completion on every
# call, and reasoning never exceeded completion on any; the harness total ran
# ~932 above the provider's per trajectory, which is just the mean reasoning
# spend added back. total_tokens is the statistic compared against the
# published single-turn figure, so it was inflated by about the size of the
# effect being measured.

def _luna_result_row(prompt: int, completion: int, reasoning: int):
    from harness.spend_tracker import ResultRow

    return ResultRow(
        row_id="r", study="study2", phase="core", item_id="t0",
        tone_level="L4_neutral", trial=0, model_key="gpt-luna", model_id="x/luna",
        provider="openai_compatible", temperature=0.0, seed=None,
        reasoning_effort="medium", thinking_budget_tokens=None,
        prompt_tokens=prompt, completion_tokens=completion, reasoning_tokens=reasoning,
        cost_usd=0.0, latency_s=0.0, refused=False, error=None, response_text="",
        extracted_answer=None, is_correct=None, timestamp=0.0,
    )


def _trajectory_total(rows) -> int:
    """The runner's own arithmetic, exercised the way runner.py writes it."""
    return sum(
        r.prompt_tokens
        + r.completion_tokens
        + (0 if r.reasoning_included_in_completion else r.reasoning_tokens)
        for r in rows
    )


def test_trajectory_total_tokens_does_not_add_reasoning_twice():
    rows = [_luna_result_row(803, 1600, 828), _luna_result_row(2479, 703, 241)]
    assert _trajectory_total(rows) == 803 + 1600 + 2479 + 703
    # The old sum, kept here so the regression is unmistakable rather than
    # implied: it is over by exactly the reasoning spend.
    assert _trajectory_total(rows) + 828 + 241 == sum(
        r.prompt_tokens + r.completion_tokens + r.reasoning_tokens for r in rows
    )


def test_provider_response_total_matches_the_providers_own_figure():
    from harness.providers.base import ProviderResponse

    r = ProviderResponse(text="x", prompt_tokens=803, completion_tokens=1600, reasoning_tokens=828)
    assert r.total_tokens == 2403, "OpenAI-style: reasoning is already inside completion"
    assert r.reasoning_tokens_outside_completion == 0


def test_a_provider_that_reports_reasoning_separately_keeps_the_third_term():
    """Google's usageMetadata keeps thoughtsTokenCount outside
    candidatesTokenCount, so dropping the term unconditionally would have
    traded a double-count for an undercount."""
    from harness.providers.base import ProviderResponse

    r = ProviderResponse(
        text="x", prompt_tokens=100, completion_tokens=50, reasoning_tokens=40,
        reasoning_included_in_completion=False,
    )
    assert r.total_tokens == 190
    assert r.reasoning_tokens_outside_completion == 40


def test_cost_estimate_prices_reasoning_exactly_once():
    from harness.providers.base import ProviderResponse
    from harness.spend_tracker import compute_cost_usd

    model = replace(_model("priced"), input_price_per_1m=1.0, output_price_per_1m=2.0)
    openai_style = ProviderResponse(text="x", prompt_tokens=1_000_000, completion_tokens=1_000_000, reasoning_tokens=400_000)
    assert compute_cost_usd(model, openai_style) == pytest.approx(3.0)

    google_style = ProviderResponse(
        text="x", prompt_tokens=1_000_000, completion_tokens=1_000_000, reasoning_tokens=400_000,
        reasoning_included_in_completion=False,
    )
    assert compute_cost_usd(model, google_style) == pytest.approx(3.8)


# --- 11. Resumed runs left an abandoned attempt in the raw log ------------
# The log is append-only and a resume does not know the killed attempt's
# calls are already in it, so one (item_id, tone_level, trial) key can hold
# two trajectories -- and only the second was ever graded. In the gpt-luna
# core log, task 56953 / L7_threatening / trial 0 holds 9 calls: a 3-call
# attempt that died, then the 6-call attempt behind the record. Summing the
# key blindly gave 2338 reasoning tokens where the graded trajectory spent
# 1236.

def _two_attempt_log(path: Path) -> Path:
    """The real shape of task 56953 / L7_threatening / trial 0: a 3-call
    attempt, then the 6-call retry. prompt_tokens climbs within an attempt
    and drops when the conversation restarts."""
    import json as _json

    abandoned = [(803, 1600, 828), (2479, 703, 241), (8696, 130, 33)]
    real = [(803, 1425, 670), (2390, 421, 85), (3938, 473, 59),
            (4447, 765, 297), (9202, 496, 83), (9637, 159, 42)]
    rows = []
    ts = 1789155849.0
    for i, (p, c, r) in enumerate(abandoned + real):
        # The retry starts hours later; timestamps are what orders the log.
        offset = ts + i * 5 if i < len(abandoned) else ts + 11_000 + i * 5
        rows.append({"item_id": "56953", "tone_level": "L7_threatening", "trial": 0,
                     "prompt_tokens": p, "completion_tokens": c, "reasoning_tokens": r,
                     "timestamp": offset})
    path.write_text("\n".join(_json.dumps(r) for r in rows))
    return path


def test_backfill_uses_only_the_last_attempt(tmp_path: Path):
    from harness.study2.analysis import backfill_reasoning_tokens

    raw = _two_attempt_log(tmp_path / "raw.jsonl")
    recs = [{"task_id": "56953", "tone_level": "L7_threatening", "trial": 0}]
    assert backfill_reasoning_tokens(recs, raw) == 1
    assert recs[0]["reasoning_tokens"] == 1236, "the graded trajectory, not both attempts"
    assert recs[0]["reasoning_tokens"] != 2338, "2338 is the naive both-attempts sum"


def test_recompute_total_tokens_rebuilds_prompt_plus_completion(tmp_path: Path):
    from harness.study2.analysis import recompute_total_tokens

    raw = _two_attempt_log(tmp_path / "raw.jsonl")
    recs = [{"task_id": "56953", "tone_level": "L7_threatening", "trial": 0, "total_tokens": 999_999}]
    assert recompute_total_tokens(recs, raw) == 1
    expected = (803 + 1425) + (2390 + 421) + (3938 + 473) + (4447 + 765) + (9202 + 496) + (9637 + 159)
    assert recs[0]["total_tokens"] == expected
    # Neither of the two ways of getting it wrong: reasoning re-added, or
    # the abandoned attempt included.
    assert recs[0]["total_tokens"] != expected + 1236
    assert recs[0]["total_tokens"] != expected + 803 + 1600 + 2479 + 703 + 8696 + 130


def test_recompute_total_tokens_leaves_keys_absent_from_this_log_alone(tmp_path: Path):
    """Record files are namespaced per model; running against one model's
    raw log must not blank out another's records."""
    from harness.study2.analysis import recompute_total_tokens

    raw = _two_attempt_log(tmp_path / "raw.jsonl")
    recs = [{"task_id": "other", "tone_level": "L4_neutral", "trial": 0, "total_tokens": 4242}]
    assert recompute_total_tokens(recs, raw) == 0
    assert recs[0]["total_tokens"] == 4242


def test_a_single_attempt_key_is_unaffected(tmp_path: Path):
    """The split must trigger on a restart, not on ordinary turn-to-turn
    growth -- otherwise every trajectory would be truncated to its last call."""
    import json as _json
    from harness.study2.analysis import last_attempt_calls, recompute_total_tokens

    rows = [{"item_id": "t0", "tone_level": "L4_neutral", "trial": 0, "timestamp": 10.0 + i,
             "prompt_tokens": p, "completion_tokens": 100, "reasoning_tokens": 10}
            for i, p in enumerate((800, 2400, 3900, 4400))]
    assert len(last_attempt_calls(rows)) == 4
    raw = tmp_path / "raw.jsonl"
    raw.write_text("\n".join(_json.dumps(r) for r in rows))
    recs = [{"task_id": "t0", "tone_level": "L4_neutral", "trial": 0, "total_tokens": 0}]
    recompute_total_tokens(recs, raw)
    assert recs[0]["total_tokens"] == 800 + 2400 + 3900 + 4400 + 400
