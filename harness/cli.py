"""Command-line entrypoint.

Study 2 (agentic SpreadsheetBench) is the active study -- see README.md
"Why this is one study now, not three". Study 1 and Study 3 subcommands
still work (their harnesses are kept, not deleted) but are retired/shelved
respectively and not part of any scheduled run.

SAFETY DEFAULT: every subcommand runs in --dry-run mode unless you pass
--live explicitly. In dry-run mode every model is forced onto the mock
provider (harness/providers/mock_provider.py) regardless of what's
configured in harness/config.py -- no network call, no spend, ever, in
dry-run. --live additionally requires the relevant API key env vars to be
set for every model in the run; missing keys fail loudly rather than
silently skipping a model.

Usage (Study 2 -- see README.md "Running it" for the full Phase 0-2 flow):
  python -m harness.cli study2 validation-gate --model gpt-luna --repo-dir ./data/spreadsheetbench
  python -m harness.cli study2 pilot --models gpt-luna --repo-dir ./data/spreadsheetbench --single-round
  python -m harness.cli study2 core --n-trials 3

Retired/shelved (kept working, not part of any active run):
  python -m harness.cli study1 validation-gate --model gpt-luna --benchmark mmlu_pro --n-items 30
  python -m harness.cli study3 bilateral-matrix --buyer-model gpt-luna --seller-model gpt-luna --n-trials-per-cell 4
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Optional

from .config import (
    ALL_MODELS,
    CORE_MODELS,
    MODELS_BY_KEY,
    STUDY1_HARD_BUDGET_CAP_USD,
    STUDY1_SOFT_BUDGET_CAP_USD,
    STUDY1_MODELS,
    STUDY2_CORE_BUDGET_CAP_USD,
    STUDY2_FRONTIER_BUDGET_CAP_USD,
    STUDY2_PILOT_BUDGET_CAP_USD,
    STUDY3_BUDGET_CAP_USD,
)
from .study2.runner import INTERJECTION_TURNS
from .tone_wrappers import INTERJECTIONS
from .providers.anthropic_provider import AnthropicProvider
from .providers.claude_cli_provider import ClaudeCLIProvider
from .providers.google_provider import GoogleProvider
from .providers.openai_compatible import OpenAICompatibleProvider

RESULTS_ROOT = Path("results")


def estimate_cost_usd(models: list, n_calls_per_model: int, avg_prompt_tokens: int, avg_completion_tokens: int) -> float:
    """Rough order-of-magnitude spend projection -- NOT a token-exact
    forecast. Used only to print a number before a live run and gate it
    behind confirmation (task spec item 6: "Print a projection before the
    first paid call in any run and require confirmation")."""
    total = 0.0
    for m in models:
        total += n_calls_per_model * (
            (avg_prompt_tokens / 1_000_000) * m.input_price_per_1m
            + (avg_completion_tokens / 1_000_000) * m.output_price_per_1m
        )
    return total


def confirm_projection(label: str, projected_usd: float, cap_usd: float, assume_yes: bool) -> None:
    print(f"\n[{label}] Projected spend (rough estimate): ${projected_usd:.2f}  (budget cap: ${cap_usd:.2f})")
    if projected_usd > cap_usd:
        print(
            f"  NOTE: projection exceeds the cap -- the run will stop early via "
            f"BudgetExceeded once ${cap_usd:.2f} is actually reached."
        )
    if assume_yes:
        print("  --yes given, proceeding without prompting.")
        return
    try:
        resp = input("Proceed with this live, billed run? [y/N] ").strip().lower()
    except EOFError:
        resp = ""
    if resp not in ("y", "yes"):
        print("Aborted -- no calls made.")
        sys.exit(1)


def _provider_available(model) -> bool:
    if model.provider == "claude_cli":
        return ClaudeCLIProvider().available()
    if model.provider == "anthropic":
        return AnthropicProvider().available()
    if model.provider == "google":
        return GoogleProvider().available()
    if model.provider == "openai_compatible":
        return OpenAICompatibleProvider().available(model)
    return True


def resolve_models(model_keys: list[str], live: bool) -> list:
    models = [MODELS_BY_KEY[k] for k in model_keys]
    if not live:
        return [replace(m, provider="mock") for m in models]

    missing = [m.key for m in models if not _provider_available(m)]
    if missing:
        print(
            f"ERROR: --live requires API keys for: {missing}. "
            "Set the relevant env vars (see .env.example) or drop --live to dry-run.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Every live run passes through here, so this is the one place a model
    # version check covers the whole CLI. A model_id like
    # `qwen/qwen3.8-flash` is a pointer the provider can repoint at a newer
    # snapshot without notice, and nothing in a response body reveals it --
    # a mid-study roll would split the run across two models with every
    # number still looking plausible. Checked once per invocation, before
    # any spend.
    from .providers.openai_compatible import OPENROUTER_BASE_URL, assert_canonical_slugs

    openrouter_models = [
        m for m in models if m.api_base == OPENROUTER_BASE_URL and m.canonical_slug
    ]
    if openrouter_models:
        try:
            observed = assert_canonical_slugs(openrouter_models)
        except Exception as exc:  # ProviderPinViolation / ProviderError
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        for key, slug in sorted(observed.items()):
            print(f"[version-check] {key} -> {slug}")
    return models


def cmd_study1_validation_gate(args: argparse.Namespace) -> None:
    from .study1.dataset import load_gpqa_diamond, load_mmlu_pro
    from .study1.runner import run_validation_gate

    model = resolve_models([args.model], args.live)[0]
    if args.live:
        confirm_projection(
            "study1 validation-gate", estimate_cost_usd([model], args.n_items, 450, 15),
            cap_usd=5.0, assume_yes=args.yes,
        )
    if args.benchmark == "mmlu_pro":
        items = load_mmlu_pro(limit=args.n_items)
    else:
        items = load_gpqa_diamond(limit=args.n_items)

    result = run_validation_gate(model, items, RESULTS_ROOT, expected_accuracy=args.expected_accuracy, tolerance=args.tolerance)
    out_path = RESULTS_ROOT / "analysis" / "study1_validation_gate.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        print(
            "\nVALIDATION GATE FAILED (or --expected-accuracy not given). "
            "Do not proceed to Part B until this passes -- see task spec's "
            "validation-gate requirement.",
            file=sys.stderr,
        )
        sys.exit(2)


def cmd_study1_part_a(args: argparse.Namespace) -> None:
    from .study1.dataset import ensure_mind_your_tone_repo
    from .study1.runner import run_part_a_replication

    dataset_path = Path(args.dataset_path) if args.dataset_path else ensure_mind_your_tone_repo(Path("data"))
    models = resolve_models(args.models.split(","), args.live)
    if args.live:
        confirm_projection(
            "study1 part-a", estimate_cost_usd(models, args.n_runs * 250, 200, 10),
            cap_usd=args.budget_cap, assume_yes=args.yes,
        )
    rows = run_part_a_replication(
        models, dataset_path, RESULTS_ROOT, budget_cap_usd=args.budget_cap,
        n_runs=args.n_runs, soft_budget_cap_usd=args.soft_budget_cap,
    )
    print(f"Part A: {len(rows)} calls logged to results/raw/study1_part_a.jsonl")


def cmd_study1_part_b(args: argparse.Namespace) -> None:
    from .study1.dataset import load_gpqa_diamond, load_mmlu_pro
    from .study1.runner import run_part_b_remaster

    models = resolve_models(args.models.split(","), args.live)
    if args.live:
        confirm_projection(
            "study1 part-b",
            estimate_cost_usd(models, args.n_trials * args.n_items * 5, 450, 15),
            cap_usd=args.budget_cap, assume_yes=args.yes,
        )
    if args.benchmark == "mmlu_pro":
        items = load_mmlu_pro(limit=args.n_items)
    else:
        items = load_gpqa_diamond(limit=args.n_items)

    rows = run_part_b_remaster(
        models, items, RESULTS_ROOT, budget_cap_usd=args.budget_cap,
        temperature=args.temperature, n_trials=args.n_trials,
        soft_budget_cap_usd=args.soft_budget_cap,
    )
    print(f"Part B ({args.benchmark}): {len(rows)} calls logged to results/raw/study1_part_b.jsonl")


def _refuse_to_shrink_report(out_path: Path, result: dict, force: bool) -> None:
    """Guard against a small run silently overwriting a large one's report.

    Reports are keyed by model, so re-running the same model with a smaller
    --n-tasks lands on the same filename. The scores in the new file are
    correct for what it ran; the problem is that the expensive run's record
    is gone and nothing says so.
    """
    if force or not out_path.exists():
        return
    try:
        existing = json.loads(out_path.read_text())
    except Exception:  # noqa: BLE001 -- unreadable/corrupt: nothing to protect
        return
    old_n, new_n = existing.get("n_tasks") or 0, result.get("n_tasks") or 0
    if new_n >= old_n:
        return
    print(
        f"ERROR: {out_path} already holds a {old_n}-task run for this model and this "
        f"run covered only {new_n} tasks. Refusing to overwrite the larger result.\n"
        f"       Move or delete that file, or pass --force-overwrite, if you really "
        f"mean to replace it.",
        file=sys.stderr,
    )
    sys.exit(1)


def cmd_study2_validation_gate(args: argparse.Namespace) -> None:
    from .study2.dataset import ensure_repo, load_spreadsheetbench
    from .study2.grader import SpreadsheetBenchGrader
    from .study2.runner import (
        MIN_USEFUL_GATE_TASKS,
        load_free_task_ids,
        run_validation_gate,
        select_gate_tasks,
    )

    model = resolve_models([args.model], args.live)[0]
    # Checked BEFORE the run, not at write time: a gate report costs hours of
    # wall clock and real money, and a one-task smoke run writes a file with
    # exactly the same name. A stray `--n-tasks 1` invocation destroyed a
    # completed 100-task GLM report during development -- only a committed
    # copy saved the numbers. Refusing after the run would protect the file
    # but still burn the spend, so refuse first.
    from .study2.runner import _run_tag

    _refuse_to_shrink_report(
        RESULTS_ROOT / "analysis" / f"study2_validation_gate_{_run_tag([model])}.json",
        {"n_tasks": args.n_tasks},
        force=args.force_overwrite,
    )
    if args.live:
        # multi-round agent loop -- assume ~3 model calls/task as a rough average
        confirm_projection(
            "study2 validation-gate", estimate_cost_usd([model], args.n_tasks * 3, 800, 300),
            cap_usd=10.0, assume_yes=args.yes,
        )
    repo_dir = ensure_repo(Path(args.repo_dir))
    grader = SpreadsheetBenchGrader(repo_dir)
    if args.task_order:
        # Escape hatch for reproducing an older result: the first n tasks in
        # file order, free ones included.
        tasks = load_spreadsheetbench(repo_dir, sample_only=True, limit=args.n_tasks)
        print(f"[validation-gate] file-order sample: {args.n_tasks} tasks (may include no-op-passable tasks)")
    else:
        all_tasks = load_spreadsheetbench(repo_dir, sample_only=True)
        tasks = select_gate_tasks(all_tasks, n=args.n_tasks, seed=args.sample_seed)
        print(
            f"[validation-gate] discriminating sample: {len(tasks)} of {len(all_tasks)} tasks "
            f"(seed={args.sample_seed}, {len(load_free_task_ids())} known no-op-passable tasks excluded)"
        )
    if len(tasks) < MIN_USEFUL_GATE_TASKS and args.expected_accuracy is not None:
        # With n tasks the observed accuracy can only land on multiples of
        # 1/n, so a tolerance finer than that step is decided by rounding.
        print(
            f"  WARNING: {len(tasks)} tasks resolve accuracy only to steps of "
            f"{1 / max(1, len(tasks)):.2f}, coarser than --tolerance {args.tolerance}. "
            f"Use --n-tasks {MIN_USEFUL_GATE_TASKS}+ for the comparison to mean anything."
        )

    result = run_validation_gate(
        model, tasks, grader, RESULTS_ROOT, expected_accuracy=args.expected_accuracy,
        tolerance=args.tolerance, max_turns=args.max_turns,
    )
    # Per model, not a fixed filename. Gating four models used to leave only
    # the fourth report on disk -- the same clobbering the scratch-dir fix
    # addressed, reintroduced at the one artifact that fix exists to preserve.
    out_path = RESULTS_ROOT / "analysis" / f"study2_validation_gate_{_run_tag([model])}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    # Kept as a stable "most recent gate" path for existing tooling/docs.
    # Not written from a dry run: the alias carries no model key, so a mock
    # run would leave fabricated numbers where a reader expects real ones.
    if model.provider != "mock":
        (RESULTS_ROOT / "analysis" / "study2_validation_gate.json").write_text(json.dumps(result, indent=2))
    # The file keeps everything (per-task turn diagnostics included, for
    # post-hoc diagnosis); stdout keeps only what a human reads at a glance,
    # since the diagnostics are hundreds of lines of captured stderr.
    summary = {k: v for k, v in result.items() if k != "per_task"}
    print(json.dumps(summary, indent=2))
    for t in result.get("per_task", []):
        mark = "CRSH" if t.get("crashed") else ("PASS" if t["passed"] else "FAIL")
        limit = " [hit turn limit]" if t["hit_turn_limit"] else ""
        free = "  <- FREE: passes by doing nothing" if t.get("no_op_passes") else ""
        print(
            f"  {mark}  {t['task_id']:<10} {t['instruction_type']:<28} "
            f"cases {t['n_test_cases_passed']}/{t['n_test_cases']}  "
            f"turns {t['n_turns']}{limit}{free}"
        )
    if "no_op_accuracy" in result:
        # Printed next to the score, not buried in the JSON: an accuracy
        # figure is not a capability measure until you know what handing the
        # input straight back would have scored.
        print(
            f"\n  no-op floor: {result['no_op_n_passed']}/{result['n_tasks']} "
            f"({result['no_op_accuracy']:.0%}) -- tasks passed without doing any work"
            + (f" {result['free_task_ids']}" if result["free_task_ids"] else "")
        )
        print(
            f"  discriminating tasks: {result['n_discriminating_tasks']}/{result['n_tasks']};  "
            f"this model beat the floor on {result['n_passed_beating_no_op']} of them"
        )
        if result["n_passed"] <= result["no_op_n_passed"]:
            print("  WARNING: this model scored no better than doing nothing on this task sample.")
    if result.get("n_crashed"):
        # A soak run's headline number: tasks the pipeline could not carry to
        # a graded result at all, as distinct from tasks the model got wrong.
        print(
            f"\n  CRASHED: {result['n_crashed']}/{result['n_tasks']} tasks raised and were "
            f"skipped -- {result['crashed_task_ids'][:12]}"
        )
    print(f"\nFull per-task detail (incl. turn diagnostics): {out_path}")
    if not result["passed"]:
        print("\nVALIDATION GATE FAILED (or --expected-accuracy not given). Do not proceed.", file=sys.stderr)
        sys.exit(2)


def cmd_study2_regrade(args: argparse.Namespace) -> None:
    """Re-grade a completed run from its raw per-call log. Makes NO model
    calls and costs nothing -- see harness/study2/regrade.py for why this
    exists and what it can and cannot recover."""
    from .study2.dataset import ensure_repo, load_spreadsheetbench
    from .study2.grader import SpreadsheetBenchGrader
    from .study2.regrade import regrade_run

    raw_path = Path(args.raw)
    if not raw_path.exists():
        print(f"ERROR: no such raw log: {raw_path}", file=sys.stderr)
        sys.exit(1)

    repo_dir = ensure_repo(Path(args.repo_dir))
    grader = SpreadsheetBenchGrader(repo_dir)
    tasks = load_spreadsheetbench(repo_dir, sample_only=not args.full_dataset)
    tasks_by_id = {t.task_id: t for t in tasks}

    print(f"[regrade] {raw_path} against {len(tasks_by_id)} loaded tasks (no model calls)")
    records = regrade_run(
        raw_path, tasks_by_id, grader,
        workdir_root=RESULTS_ROOT / "scratch" / "regrade",
        max_turns=args.max_turns,
    )

    out_path = RESULTS_ROOT / "analysis" / f"{raw_path.stem}_regraded.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, indent=2, default=str))

    graded = [r for r in records if r.get("regraded")]
    missing = [r for r in records if not r.get("regraded")]
    n_passed = sum(1 for r in graded if r["passed"])
    print(f"  trajectories rebuilt : {len(graded)}")
    print(f"  passed               : {n_passed}/{len(graded)}" + (f"  ({n_passed / len(graded):.0%})" if graded else ""))
    if missing:
        print(f"  NOT regraded         : {len(missing)} (task id absent from the loaded dataset -- wrong slice?)")
    print(f"\n  written to: {out_path}")


def cmd_study2_thinking_preflight(args: argparse.Namespace) -> None:
    """Phase 0.5 gate (README "The thinking arm"): three cheap probe checks
    that must pass before the calibration arm gets real spend -- see
    harness/study2/thinking_preflight.py's module docstring."""
    from .spend_tracker import SpendTracker
    from .study2.thinking_preflight import run_thinking_preflight

    on_model, off_model = resolve_models([args.on_model, args.off_model], args.live)
    if args.live:
        confirm_projection(
            "study2 thinking-preflight", estimate_cost_usd([on_model, off_model], 1, 100, 200),
            cap_usd=1.0, assume_yes=args.yes,
        )

    out_path = RESULTS_ROOT / "raw" / "study2_thinking_preflight.jsonl"
    tracker = SpendTracker(out_path, phase="thinking_preflight", cap_usd=1.0)
    try:
        report = run_thinking_preflight(tracker, on_model, off_model)
    finally:
        tracker.close()

    result = {
        "on_model_key": report.on_model_key,
        "off_model_key": report.off_model_key,
        "on_reasoning_tokens": report.on_reasoning_tokens,
        "off_reasoning_tokens": report.off_reasoning_tokens,
        "on_total_tokens": report.on_total_tokens,
        "off_total_tokens": report.off_total_tokens,
        "checks": [{"name": c.name, "passed": c.passed, "detail": c.detail} for c in report.checks],
        "passed": report.passed,
    }
    out_json_path = RESULTS_ROOT / "analysis" / "study2_thinking_preflight.json"
    out_json_path.parent.mkdir(parents=True, exist_ok=True)
    out_json_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if not report.passed:
        print(
            "\nTHINKING PREFLIGHT FAILED -- do not spend on the calibration arm until every "
            "check above passes. See README 'The thinking arm'.",
            file=sys.stderr,
        )
        sys.exit(2)


def _study2_stage(args: argparse.Namespace, phase: str, default_cap: float, default_trials: int) -> None:
    from .study2.dataset import ensure_repo, load_spreadsheetbench
    from .study2.grader import SpreadsheetBenchGrader
    from .study2.runner import load_free_task_ids, run_condition_batch, select_gate_tasks

    cap_usd = args.budget_cap or default_cap
    n_trials = args.n_trials or default_trials
    models = resolve_models(args.models.split(","), args.live)
    if args.live:
        # 7 tone levels x n_trials x n_tasks, ~3 model calls/negotiation-round-trip average for the multi-round agent loop
        n_calls_per_model = 7 * n_trials * args.n_tasks * (1 if args.single_round else 3)
        confirm_projection(
            f"study2 {phase}", estimate_cost_usd(models, n_calls_per_model, 800, 300),
            cap_usd=cap_usd, assume_yes=args.yes,
        )
    repo_dir = ensure_repo(Path(args.repo_dir))
    grader = SpreadsheetBenchGrader(repo_dir)
    # The core phase used to draw from the full 909-task dataset while every
    # other phase drew from the 200-task sample. Two things break at that
    # boundary, and neither announces itself:
    #
    #   * free_tasks.json -- the no-op-passable manifest select_gate_tasks
    #     subtracts -- was measured over the 200-task sample only. Drawing
    #     from 909 selects tasks whose no-op status was never established,
    #     reintroducing the very floor the discriminating draw exists to
    #     remove.
    #   * The validation gates, and therefore every --expected-accuracy and
    #     every neutral-tone baseline, live in the 200-task sample. Measured
    #     live: a core draw of 50 from 909 overlapped the n=100 gate sample
    #     by 2 tasks. The tone conditions would have had no baseline to be
    #     compared against.
    #
    # So the sample is the default everywhere now, and reaching the full
    # dataset is an explicit opt-in that says what it costs.
    sample_only = not getattr(args, "full_dataset", False)
    if args.task_order:
        tasks = load_spreadsheetbench(repo_dir, sample_only=sample_only, limit=args.n_tasks)
        print(f"[{phase}] file-order sample: {args.n_tasks} tasks (may include no-op-passable tasks)")
    else:
        # Same discriminating draw the gate uses. The expensive runs were
        # still taking the first n tasks in file order -- inheriting exactly
        # the sampling bias select_gate_tasks was written to fix, on the path
        # where each biased task costs real money rather than cents.
        all_tasks = load_spreadsheetbench(repo_dir, sample_only=sample_only)
        tasks = select_gate_tasks(all_tasks, n=args.n_tasks, seed=args.sample_seed)
        print(
            f"[{phase}] discriminating sample: {len(tasks)} of {len(all_tasks)} tasks "
            f"(seed={args.sample_seed}, {len(load_free_task_ids())} known no-op-passable tasks excluded)"
        )
        if not sample_only:
            print(
                f"  WARNING: --full-dataset -- tasks outside the 200-task sample have no "
                f"measured no-op status and no validation-gate baseline. The no-op floor "
                f"is measured per task during the run, but --expected-accuracy and the "
                f"gate's neutral-tone numbers do not apply to this draw."
            )

    # Fail before the first paid call, not after 3,000 of them. An
    # --interject-turns typo that named a turn the agent loop never reaches
    # would otherwise produce a full arm in which the treatment silently never
    # fired, and an arm whose treatment never fires is indistinguishable from
    # its own control.
    if args.interject_turns:
        if not args.interject:
            raise SystemExit("--interject-turns requires --interject.")
        try:
            requested = [int(t) for t in args.interject_turns.split(",")]
        except ValueError:
            raise SystemExit(
                f"--interject-turns must be comma-separated integers, got "
                f"{args.interject_turns!r}."
            )
        unknown = sorted(set(requested) - set(INTERJECTION_TURNS))
        if unknown:
            raise SystemExit(
                f"--interject-turns {unknown} outside {list(INTERJECTION_TURNS)}. "
                f"Turn indices are loop indices: 0 is the observation after the "
                f"model's first response (reaches ~98% of trajectories), 2 "
                f"reaches ~55%. Past 2 the treatment misses more trajectories "
                f"than it reaches."
            )
        print(
            f"[{phase}] injection turn CROSSED over {sorted(set(requested))}: "
            f"each trial runs once per turn, so this run is "
            f"{len(set(requested))}x the trajectories of an uncrossed one."
        )

    records = run_condition_batch(
        models, tasks, grader, RESULTS_ROOT, phase=phase,
        budget_cap_usd=cap_usd, n_trials=n_trials,
        multi_round=not args.single_round, max_turns=args.max_turns,
        tone_seed=args.sample_seed, resume=args.resume,
        tones=(args.tones.split(",") if args.tones else None),
        run_label=args.run_label, interject=args.interject,
        interject_turns=(
            [int(t) for t in args.interject_turns.split(",")]
            if args.interject_turns else None
        ),
    )
    # Ask for the tag rather than re-deriving it. This line used to keep its
    # own copy of the naming rule and so ignored both --run-label and the
    # dry-run suffix: a labelled run wrote its records correctly and then
    # announced the MAIN dataset's path, which reads exactly like the full
    # run has just been overwritten by a 150-trajectory arm.
    from .study2.runner import _run_tag

    tag = _run_tag(models, args.run_label)
    print(f"{phase}: {len(records)} trajectories logged to results/analysis/study2_{phase}_{tag}_records.json")


def cmd_study2_pilot(args: argparse.Namespace) -> None:
    _study2_stage(args, "pilot", STUDY2_PILOT_BUDGET_CAP_USD, default_trials=3)


def cmd_study2_core(args: argparse.Namespace) -> None:
    _study2_stage(args, "core", STUDY2_CORE_BUDGET_CAP_USD, default_trials=3)


def cmd_study2_frontier(args: argparse.Namespace) -> None:
    _study2_stage(args, "frontier", STUDY2_FRONTIER_BUDGET_CAP_USD, default_trials=1)


def _underpowered_accuracy_note(records: list[dict]) -> str:
    """The accuracy caveat, computed from the run rather than asserted.

    The old text stated a ~18% base rate (SpreadsheetBench's published
    17-20%) and concluded that accuracy needs "a thousand-plus observations
    per condition". Both halves were wrong for this run. The observed pooled
    accuracy on the gpt-luna core run is 0.296, not 0.18 -- so the note
    quoted a number the run itself contradicted, which is why the rate is
    now computed from the records in hand.

    The power claim was worse, because it was used to wave accuracy away
    entirely. Simulating at the OBSERVED slope (-0.0107 per tone level) puts
    power at this design around 0.44, and the 80%-power MDE at roughly 0.017
    per level -- meaningfully underpowered, but nowhere near the "a few
    hundred is hopeless" the old text implied, and irrelevant to a result
    that does reach significance. Power bounds FALSE NEGATIVES. It says
    nothing about whether a positive is real: a pre-registered test that
    clears its threshold is a valid pre-registered test at n=150 exactly as
    it is at n=1500. Reading "underpowered" as a reason to discount a
    significant accuracy finding inverts what the number means.

    So the note now says what it can honestly say: accuracy was designated
    secondary in advance, a null on it is weak evidence, a positive on it
    stands as a pre-registered test, and the real reasons for caution about
    any positive here are one model, several outcome measures, and
    fragility -- not power.
    """
    if not records:
        return "No records: accuracy not reported."
    n_per_level: dict[str, int] = {}
    for r in records:
        n_per_level[r["tone_level"]] = n_per_level.get(r["tone_level"], 0) + 1
    observed_accuracy = sum(bool(r["passed"]) for r in records) / len(records)
    return (
        f"Accuracy (observed pooled pass rate {observed_accuracy:.1%} over {len(records)} "
        f"trajectories, n={min(n_per_level.values())}-{max(n_per_level.values())} per tone) was "
        "PRE-DESIGNATED A SECONDARY outcome; cost is primary. Power is limited, so a null here is "
        "weak evidence of no effect. A SIGNIFICANT result on it is still a valid pre-registered "
        "test -- power governs false negatives, not the validity of a positive. Read any positive "
        "cautiously because this is one model, one of several outcome measures, and sensitive to "
        "analysis choices -- not because of power. See README 'Outcome measures'."
    )


def _token_cost_trends(records: list[dict]) -> dict:
    """Clustered trend test on the token measures, primary outcome first.

    Reported for both because they answer different questions.
    `reasoning_tokens` is what the model chose to spend thinking, which is
    what a "tone changes how hard it thinks" claim rests on. `total_tokens`
    is dominated by the prompt, whose length the tone wrapper changes by
    construction, so part of any difference there is the wrapper's own text
    rather than the model's behaviour -- but it is the statistic directly
    comparable to the published single-turn figure, so it is kept.

    A run recorded before reasoning_tokens existed reports its absence
    rather than a number: no thinking measurement is not the same as a
    measurement of no thinking.
    """
    from .study2.analysis import token_cost_trend_test

    out: dict[str, dict] = {}
    for key in ("reasoning_tokens", "total_tokens"):
        try:
            t = token_cost_trend_test(records, value_key=key)
        except ValueError as exc:
            out[key] = {"unavailable": str(exc)}
            continue
        out[key] = {
            "n_clusters": t.n_clusters,
            "observed_slope": t.observed_slope,
            "p_value": t.p_value,
            "ci_low": t.ci_low,
            "ci_high": t.ci_high,
        }
    return out



def cmd_study2_analyze(args: argparse.Namespace) -> None:
    """Phase 3 (README "Phases"): load one run's Study 2 records (written by
    `study2 pilot`/`core`/`frontier` to results/analysis/study2_<phase>_records.json)
    and report effect sizes with item-clustered bootstrap CIs, per the
    roadmap's outcome measures -- not just raw pass/fail.

    Report ordering follows the task spec's outcome priority: cost first
    (the primary, adequately-powered outcome), then trajectory-level
    behavior, then accuracy last and explicitly flagged as underpowered
    (see _underpowered_accuracy_note). Accuracy's primary statistical test
    is accuracy_trend_test -- an item-clustered permutation trend test
    across the 7 ordered tone levels, not a full 21-pairwise-comparison
    matrix (task spec: "with seven ordered levels, do not run 21 pairwise
    tests"). bh_corrected_pairwise_comparisons is included as a labeled
    follow-up only, BH-corrected, not the primary analysis.

    Deliberately does NOT reuse study1.analysis.per_level_accuracy/
    refusal_rate here: those expect Study 1's row shape (an "outcome"
    field with values "answered"/"refused"/"unparseable"), and Study 2's
    records use "passed"/"refused" booleans directly -- calling them on
    Study 2 records would KeyError, not silently misbehave, but the
    correct fix is computing accuracy directly from "passed" here rather
    than reshaping Study 2 data to fit Study 1's vocabulary.
    """
    from .study1.analysis import AccuracyEstimate, bootstrap_accuracy_ci
    from .study2.analysis import (
        accuracy_trend_test,
        bh_corrected_pairwise_comparisons,
        severity_breakdown,
        shortcut_rate,
        token_cost_effect_size,
        token_cost_trend_test,
        trajectory_cost_summary,
        verification_rates,
    )

    # --records-path is a GLOB, not a single file. Per-phase record files are
    # namespaced by model (see runner._run_tag), so a four-model core run
    # executed as four parallel processes writes four files. Reading only one
    # would silently analyse a quarter of the study as though it were all of
    # it -- exactly the kind of quiet wrongness this harness has already been
    # bitten by. Merging every match makes the parallel and single-process
    # cases produce the same analysis.
    matches = sorted(Path().glob(args.records_path)) or (
        [Path(args.records_path)] if Path(args.records_path).exists() else []
    )
    if not matches:
        print(f"No record files matched {args.records_path}", file=sys.stderr)
        sys.exit(1)

    records = []
    for m in matches:
        records.extend(json.loads(m.read_text()))
    models_seen = sorted({r.get("model_key") for r in records if r.get("model_key")})
    print(
        f"[analyze] {len(records)} records from {len(matches)} file(s): "
        f"{[m.name for m in matches]}\n           models: {models_seen}"
    )
    if not records:
        print(f"No records found in {matches}", file=sys.stderr)
        sys.exit(1)

    by_tone: dict[str, list[bool]] = {}
    # Parallel to by_tone: which task each pass/fail came from. The CI is
    # clustered on these, not resampled over trajectories one at a time --
    # the 150 observations behind a tone are 50 tasks run 3 times each, and
    # treating them as 150 independent ones made the interval a third too
    # narrow (see study1.analysis.bootstrap_accuracy_ci for the measured
    # comparison). Everything else here already clusters by task; accuracy's
    # CI was the one place that did not.
    tasks_by_tone: dict[str, list[str]] = {}
    refused_by_tone: dict[str, list[bool]] = {}
    for r in records:
        by_tone.setdefault(r["tone_level"], []).append(bool(r["passed"]))
        tasks_by_tone.setdefault(r["tone_level"], []).append(r["task_id"])
        refused_by_tone.setdefault(r["tone_level"], []).append(bool(r["refused"]))

    accuracy: dict[str, AccuracyEstimate] = {
        tone: bootstrap_accuracy_ci(v, cluster_ids=tasks_by_tone[tone]) for tone, v in by_tone.items()
    }
    refusal_rate_by_tone = {tone: sum(v) / len(v) for tone, v in refused_by_tone.items()}
    trend = accuracy_trend_test(records)

    report = {
        "n_records": len(records),
        # Primary outcome (task spec item 6: "Primary: cost").
        # The effect size is descriptive only -- it reports a relative-variation
        # percentage with no p-value and means pooled across tasks. Pooling was
        # the problem: tasks differ enormously in how much thinking they demand
        # and that variance swamps any tone effect. The trend tests below are
        # the inferential half, clustered by task, and the primary outcome had
        # neither until they were added.
        "token_cost_effect_size": token_cost_effect_size(records),
        "token_cost_trend_test": _token_cost_trends(records),
        "cost_summary_by_tone": trajectory_cost_summary(records),
        # Trajectory-level behavior.
        "severity_breakdown_by_tone": severity_breakdown(records),
        "verification_rates_by_tone": verification_rates(records),
        "shortcut_rate_by_tone": shortcut_rate(records),
        "refusal_rate_by_tone": refusal_rate_by_tone,
        # Accuracy last, explicitly flagged underpowered -- see
        # _underpowered_accuracy_note and README "Outcome measures".
        "accuracy_underpowered_note": _underpowered_accuracy_note(records),
        "accuracy_trend_test": {
            "n_clusters": trend.n_clusters,
            "observed_slope": trend.observed_slope,
            "p_value": trend.p_value,
            "ci_low": trend.ci_low,
            "ci_high": trend.ci_high,
        },
        "accuracy_by_tone": {
            tone: {"n": est.n, "accuracy": est.accuracy, "ci_low": est.ci_low, "ci_high": est.ci_high}
            for tone, est in accuracy.items()
        },
        "bh_corrected_pairwise_comparisons_followup": bh_corrected_pairwise_comparisons(records),
    }

    out_path = Path(args.out_path) if args.out_path else RESULTS_ROOT / "analysis" / "study2_analysis_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

    effect = report["token_cost_effect_size"]
    published = effect["published_single_turn_comparison_pct"]
    observed = effect["relative_variation_pct"]
    if observed == observed:  # not NaN
        direction = "LARGER than" if observed > published else ("smaller than" if observed < published else "equal to")
        print(
            f"\nPre-registered hypothesis check: observed token-cost variation "
            f"({observed:.1f}%) is {direction} Dobariya & Kumar's published "
            f"single-turn figure ({published}%). See README 'The pre-registered "
            "hypothesis' -- report this plainly, including if the hypothesis "
            "did not hold."
        )
    print(f"\n{report['accuracy_underpowered_note']}")
    print(f"\nFull report written to {out_path}")


def cmd_study3_bilateral_matrix(args: argparse.Namespace) -> None:
    from .spend_tracker import SpendTracker
    from .study3.agenticpay_dep import ensure_agenticpay_repo
    from .study3.runner import run_bilateral_matrix

    buyer_model, seller_model = resolve_models([args.buyer_model, args.seller_model], args.live)
    ensure_agenticpay_repo(Path("data"))

    out_path = RESULTS_ROOT / "raw" / "study3_bilateral_matrix.jsonl"
    tracker = SpendTracker(out_path, phase="study3_bilateral_matrix", cap_usd=args.budget_cap)
    try:
        results = run_bilateral_matrix(
            tracker,
            buyer_model,
            seller_model,
            n_trials_per_cell=args.n_trials_per_cell,
            max_rounds=args.max_rounds,
            buyer_max_price=args.buyer_max_price,
            seller_min_price=args.seller_min_price,
            initial_seller_price=args.initial_seller_price,
        )
    finally:
        tracker.close()
    n_agreed = sum(1 for r in results if r.status == "agreed")
    print(f"Study 3 bilateral matrix: {len(results)} negotiations ({n_agreed} agreed) logged to {out_path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--live", action="store_true", help="Make real, billed API calls. Default is dry-run (mock provider).")
    p.add_argument(
        "--yes", "-y", action="store_true",
        help="Skip the pre-flight spend-projection confirmation prompt (for scripted/CI use). Has no effect without --live.",
    )
    sub = p.add_subparsers(dest="study", required=True)

    s1 = sub.add_parser("study1")
    s1_sub = s1.add_subparsers(dest="cmd", required=True)

    g = s1_sub.add_parser("validation-gate")
    g.add_argument("--model", required=True, choices=list(MODELS_BY_KEY))
    g.add_argument("--benchmark", choices=["mmlu_pro", "gpqa_diamond"], default="mmlu_pro")
    g.add_argument("--n-items", type=int, default=30)
    g.add_argument("--expected-accuracy", type=float, default=None)
    g.add_argument("--tolerance", type=float, default=0.05)
    g.set_defaults(func=cmd_study1_validation_gate)

    a = s1_sub.add_parser("part-a")
    a.add_argument(
        "--dataset-path", default=None,
        help="Path to 50_que_dataset.csv or its containing dir. Omit to auto-clone "
             "github.com/OmDobariya/AMCIS_politeness_llms into data/ (see study1/dataset.py).",
    )
    a.add_argument("--models", default=",".join(m.key for m in STUDY1_MODELS))
    a.add_argument("--n-runs", type=int, default=10, help="Repeats per prompt, matching the original protocol's NUM_RUNS=10")
    a.add_argument("--budget-cap", type=float, default=STUDY1_HARD_BUDGET_CAP_USD, help="Hard stop")
    a.add_argument("--soft-budget-cap", type=float, default=STUDY1_SOFT_BUDGET_CAP_USD, help="Warn-and-continue threshold")
    a.set_defaults(func=cmd_study1_part_a)

    b = s1_sub.add_parser("part-b")
    b.add_argument("--benchmark", choices=["mmlu_pro", "gpqa_diamond"], default="mmlu_pro")
    b.add_argument("--models", default=",".join(m.key for m in STUDY1_MODELS))
    b.add_argument("--n-items", type=int, default=100)
    b.add_argument("--n-trials", type=int, default=1)
    b.add_argument("--temperature", type=float, default=0.0)
    b.add_argument("--budget-cap", type=float, default=STUDY1_HARD_BUDGET_CAP_USD, help="Hard stop")
    b.add_argument("--soft-budget-cap", type=float, default=STUDY1_SOFT_BUDGET_CAP_USD, help="Warn-and-continue threshold")
    b.set_defaults(func=cmd_study1_part_b)

    s2 = sub.add_parser("study2")
    s2_sub = s2.add_subparsers(dest="cmd", required=True)

    g2 = s2_sub.add_parser("validation-gate")
    g2.add_argument("--model", required=True, choices=list(MODELS_BY_KEY))
    g2.add_argument("--repo-dir", default="data/spreadsheetbench")
    g2.add_argument("--n-tasks", type=int, default=100)  # see MIN_USEFUL_GATE_TASKS: +/-0.08 tolerance is only ~0.8 SD at n=20, so the gate would fail a healthy harness ~40% of the time
    g2.add_argument(
        "--sample-seed", type=int, default=0,
        help="Seed for the discriminating-task draw. Same seed + dataset => same tasks, "
             "which is what makes an --expected-accuracy value comparable across runs.",
    )
    g2.add_argument(
        "--task-order", action="store_true",
        help="Use the first --n-tasks in dataset file order instead of a discriminating "
             "sample. Includes tasks that pass when the agent does nothing; for "
             "reproducing older results only.",
    )
    g2.add_argument(
        "--force-overwrite", action="store_true",
        help="Replace an existing gate report for this model even if it covered "
             "more tasks than this run. Off by default: a stray small run must not "
             "silently destroy an expensive large one.",
    )
    g2.add_argument("--expected-accuracy", type=float, default=None)
    g2.add_argument("--tolerance", type=float, default=0.08)
    g2.add_argument("--max-turns", type=int, default=10, help="Per-trajectory turn budget for the multi-round agent loop")
    g2.set_defaults(func=cmd_study2_validation_gate)

    rg = s2_sub.add_parser("regrade", help="Re-grade a finished run from results/raw/*.jsonl -- no model calls, no spend")
    rg.add_argument("--raw", required=True, help="Path to a results/raw/*.jsonl log")
    rg.add_argument("--repo-dir", default="data/spreadsheetbench")
    rg.add_argument("--full-dataset", action="store_true", help="Load the 912-task set instead of the 200-task sample")
    rg.add_argument("--max-turns", type=int, default=None, help="Turn budget the original run used (for hit_turn_limit)")
    rg.set_defaults(func=cmd_study2_regrade)

    tp = s2_sub.add_parser("thinking-preflight")
    tp.add_argument("--on-model", default="gpt-luna", choices=list(MODELS_BY_KEY))
    tp.add_argument("--off-model", default="gpt-luna-calibration", choices=list(MODELS_BY_KEY))
    tp.set_defaults(func=cmd_study2_thinking_preflight)

    for name, fn, default_cap, default_trials in [
        ("pilot", cmd_study2_pilot, STUDY2_PILOT_BUDGET_CAP_USD, 3),
        ("core", cmd_study2_core, STUDY2_CORE_BUDGET_CAP_USD, 3),
        ("frontier", cmd_study2_frontier, STUDY2_FRONTIER_BUDGET_CAP_USD, 1),
    ]:
        sp = s2_sub.add_parser(name)
        sp.add_argument("--models", default=",".join(m.key for m in CORE_MODELS))
        sp.add_argument("--repo-dir", default="data/spreadsheetbench")
        sp.add_argument("--n-tasks", type=int, default=30 if name != "core" else 50)
        sp.add_argument(
            "--sample-seed", type=int, default=0,
            help="Seed for the discriminating-task draw; same seed + dataset => same tasks.",
        )
        sp.add_argument(
            "--task-order", action="store_true",
            help="Use the first --n-tasks in dataset file order instead of a discriminating "
                 "sample. Includes tasks that pass when the agent does nothing.",
        )
        sp.add_argument(
            "--full-dataset", action="store_true",
            help="Draw tasks from the full 909-task dataset instead of the 200-task "
                 "sample. Off by default: the no-op manifest and every validation-gate "
                 "baseline were measured on the sample, and do not transfer.",
        )
        sp.add_argument(
            "--resume", action="store_true",
            help="Skip trajectories already recorded in this phase's records JSONL. "
                 "A core run is hours long and the container can be restarted under "
                 "it; the incremental records survive, so the work does not have to "
                 "be redone. Crashed trajectories are retried rather than skipped.",
        )
        sp.add_argument(
            "--tones", default=None,
            help="Comma-separated tone keys to run instead of all seven (e.g. "
                 "L4_neutral). Tone order is still shuffled over the full scale "
                 "and then filtered, so a kept tone meets the same burst "
                 "positions it would have in a full run.",
        )
        sp.add_argument(
            "--run-label", default=None,
            help="Suffix for this run's output files, for a run that is "
                 "deliberately separate from the main dataset (e.g. wrapper-v2). "
                 "Without it the run lands on the main records file.",
        )
        sp.add_argument(
            "--interject", default=None, choices=sorted(INTERJECTIONS),
            help="Deliver this tone as a mid-task interjection, alongside the "
                 "execution observation at a seeded random turn. The opening "
                 "wrapper is unchanged, so two runs differing only in this flag "
                 "isolate the tone of the interruption from the interruption "
                 "itself. The turn is seeded on (task, trial) and not on the "
                 "tone, so every arm interrupts the same trajectory at the "
                 "same point.",
        )
        sp.add_argument(
            "--interject-turns", default=None,
            help="Comma-separated turn indices (from 0,1,2) to CROSS the "
                 "interjection over, e.g. 0,1,2. Every trial is then run once "
                 "per turn, making injection position a factor of the design "
                 "rather than a seeded draw -- which is what makes 'which turn "
                 "costs most' answerable. Without it the turn is drawn at "
                 "random per (task, trial), and a late turn fires only on the "
                 "long trajectories, so position is confounded with task "
                 "difficulty. Requires --interject. Multiplies the run size by "
                 "the number of turns listed.",
        )
        sp.add_argument("--n-trials", type=int, default=None)
        sp.add_argument("--budget-cap", type=float, default=None)
        sp.add_argument("--single-round", action="store_true", help="Use the single-round setting instead of multi-round ReAct")
        sp.add_argument("--max-turns", type=int, default=10, help="Per-trajectory turn budget for the multi-round agent loop")
        sp.set_defaults(func=fn)

    an = s2_sub.add_parser("analyze")
    an.add_argument(
        "--records-path", default="results/analysis/study2_core_*_records.json",
        help="Glob for the per-model record files pilot/core/frontier write; all matches are merged.",
    )
    an.add_argument("--out-path", default=None, help="Where to write the report JSON (default: results/analysis/study2_analysis_report.json)")
    an.set_defaults(func=cmd_study2_analyze)

    s3 = sub.add_parser("study3")
    s3_sub = s3.add_subparsers(dest="cmd", required=True)

    bm = s3_sub.add_parser("bilateral-matrix")
    bm.add_argument("--buyer-model", default="gpt-luna", choices=list(MODELS_BY_KEY))
    bm.add_argument("--seller-model", default="gpt-luna", choices=list(MODELS_BY_KEY))
    bm.add_argument("--n-trials-per-cell", type=int, default=1)
    bm.add_argument("--max-rounds", type=int, default=10)
    bm.add_argument("--buyer-max-price", type=float, default=120.0)
    bm.add_argument("--seller-min-price", type=float, default=80.0)
    bm.add_argument("--initial-seller-price", type=float, default=150.0)
    bm.add_argument("--budget-cap", type=float, default=STUDY3_BUDGET_CAP_USD)
    bm.set_defaults(func=cmd_study3_bilateral_matrix)

    return p


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
