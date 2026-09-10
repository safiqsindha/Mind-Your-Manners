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


def cmd_study2_validation_gate(args: argparse.Namespace) -> None:
    from .study2.dataset import ensure_repo, load_spreadsheetbench
    from .study2.grader import SpreadsheetBenchGrader
    from .study2.runner import run_validation_gate

    model = resolve_models([args.model], args.live)[0]
    if args.live:
        # multi-round agent loop -- assume ~3 model calls/task as a rough average
        confirm_projection(
            "study2 validation-gate", estimate_cost_usd([model], args.n_tasks * 3, 800, 300),
            cap_usd=10.0, assume_yes=args.yes,
        )
    repo_dir = ensure_repo(Path(args.repo_dir))
    tasks = load_spreadsheetbench(repo_dir, sample_only=True, limit=args.n_tasks)
    grader = SpreadsheetBenchGrader(repo_dir)

    result = run_validation_gate(model, tasks, grader, RESULTS_ROOT, expected_accuracy=args.expected_accuracy, tolerance=args.tolerance)
    out_path = RESULTS_ROOT / "analysis" / "study2_validation_gate.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        print("\nVALIDATION GATE FAILED (or --expected-accuracy not given). Do not proceed.", file=sys.stderr)
        sys.exit(2)


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
    from .study2.runner import run_condition_batch

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
    tasks = load_spreadsheetbench(repo_dir, sample_only=(phase != "core"), limit=args.n_tasks)
    grader = SpreadsheetBenchGrader(repo_dir)

    records = run_condition_batch(
        models, tasks, grader, RESULTS_ROOT, phase=phase,
        budget_cap_usd=cap_usd, n_trials=n_trials,
        multi_round=not args.single_round,
    )
    print(f"{phase}: {len(records)} trajectories logged to results/analysis/study2_{phase}_records.json")


def cmd_study2_pilot(args: argparse.Namespace) -> None:
    _study2_stage(args, "pilot", STUDY2_PILOT_BUDGET_CAP_USD, default_trials=3)


def cmd_study2_core(args: argparse.Namespace) -> None:
    _study2_stage(args, "core", STUDY2_CORE_BUDGET_CAP_USD, default_trials=3)


def cmd_study2_frontier(args: argparse.Namespace) -> None:
    _study2_stage(args, "frontier", STUDY2_FRONTIER_BUDGET_CAP_USD, default_trials=1)


def cmd_study2_analyze(args: argparse.Namespace) -> None:
    """Phase 3 (README "Phases"): load one run's Study 2 records (written by
    `study2 pilot`/`core`/`frontier` to results/analysis/study2_<phase>_records.json)
    and report effect sizes with item-clustered bootstrap CIs, per the
    roadmap's outcome measures -- not just raw pass/fail.

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
        severity_breakdown,
        shortcut_rate,
        token_cost_effect_size,
        trajectory_cost_summary,
        verification_rates,
    )

    records = json.loads(Path(args.records_path).read_text())
    if not records:
        print(f"No records found in {args.records_path}", file=sys.stderr)
        sys.exit(1)

    by_tone: dict[str, list[bool]] = {}
    refused_by_tone: dict[str, list[bool]] = {}
    for r in records:
        by_tone.setdefault(r["tone_level"], []).append(bool(r["passed"]))
        refused_by_tone.setdefault(r["tone_level"], []).append(bool(r["refused"]))

    accuracy: dict[str, AccuracyEstimate] = {tone: bootstrap_accuracy_ci(v) for tone, v in by_tone.items()}
    refusal_rate_by_tone = {tone: sum(v) / len(v) for tone, v in refused_by_tone.items()}

    report = {
        "n_records": len(records),
        "accuracy_by_tone": {
            tone: {"n": est.n, "accuracy": est.accuracy, "ci_low": est.ci_low, "ci_high": est.ci_high}
            for tone, est in accuracy.items()
        },
        "refusal_rate_by_tone": refusal_rate_by_tone,
        "severity_breakdown_by_tone": severity_breakdown(records),
        "verification_rates_by_tone": verification_rates(records),
        "shortcut_rate_by_tone": shortcut_rate(records),
        "cost_summary_by_tone": trajectory_cost_summary(records),
        "token_cost_effect_size": token_cost_effect_size(records),
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
    g2.add_argument("--n-tasks", type=int, default=20)
    g2.add_argument("--expected-accuracy", type=float, default=None)
    g2.add_argument("--tolerance", type=float, default=0.08)
    g2.set_defaults(func=cmd_study2_validation_gate)

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
        sp.add_argument("--n-tasks", type=int, default=30 if name != "core" else 100)
        sp.add_argument("--n-trials", type=int, default=None)
        sp.add_argument("--budget-cap", type=float, default=None)
        sp.add_argument("--single-round", action="store_true", help="Use the single-round setting instead of multi-round ReAct")
        sp.set_defaults(func=fn)

    an = s2_sub.add_parser("analyze")
    an.add_argument(
        "--records-path", default=str(RESULTS_ROOT / "analysis" / "study2_core_records.json"),
        help="Path to a study2_<phase>_records.json file written by pilot/core/frontier.",
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
