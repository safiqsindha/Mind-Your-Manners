"""Study 1 orchestration: validation gate, Part A replication, Part B remaster.

Every function that spends money takes a `SpendTracker` and calls
`tracker.check_before_call()` before issuing a call and lets
`BudgetExceeded` propagate -- callers must not swallow it.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import replace
from pathlib import Path
from typing import Optional

from ..providers.base import ModelConfig
from ..providers.registry import get_provider
from ..spend_tracker import ResultRow, SpendTracker, compute_cost_usd
from ..tone_wrappers import TONE_ORDER, TONE_WRAPPERS
from .answer_extraction import extract_answer, extract_answer_mind_your_tone
from .dataset import (
    MIND_YOUR_TONE_SYSTEM_PROMPT,
    BenchmarkItem,
    MindYourToneRow,
    load_mind_your_tone,
    render_mind_your_tone_prompt,
)

SYSTEM_PROMPT = "You are a helpful assistant answering multiple-choice questions."


def _call_and_record(
    tracker: SpendTracker,
    model: ModelConfig,
    system: str,
    user_text: str,
    correct_letter: str,
    item_id: str,
    tone_level: str,
    trial: int,
    phase: str,
    subject: str,
    extractor=extract_answer,
) -> ResultRow:
    provider = get_provider(model.provider if model.provider != "openai_compatible" else "openai_compatible")
    # cheap pre-call estimate: assume ~2x the wrapper+question length in tokens, small completion
    tracker.check_before_call(estimated_cost_usd=0.01)

    response = provider.complete(model, system, [{"role": "user", "content": user_text}])
    cost = compute_cost_usd(model, response)
    extraction = extractor(response.text, correct_letter, response.refused)

    row = ResultRow(
        row_id=str(uuid.uuid4()),
        study="study1",
        phase=phase,
        item_id=item_id,
        tone_level=tone_level,
        trial=trial,
        model_key=model.key,
        model_id=model.model_id,
        provider=model.provider,
        temperature=model.temperature,
        seed=model.seed,
        reasoning_effort=model.reasoning_effort,
        thinking_budget_tokens=model.thinking_budget_tokens,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        reasoning_tokens=response.reasoning_tokens,
        cost_usd=cost,
        latency_s=response.latency_s,
        refused=response.refused,
        error=response.error,
        response_text=response.text,
        extracted_answer=extraction.letter,
        is_correct=extraction.is_correct,
        timestamp=time.time(),
        cached_tokens=response.cached_tokens,
        served_provider=response.served_provider,
        raw_response=response.raw,
        extra={"outcome": extraction.outcome, "subject": subject},
    )
    tracker.record(row)
    return row


def run_validation_gate(
    model: ModelConfig,
    items: list[BenchmarkItem],
    out_dir: Path,
    expected_accuracy: Optional[float] = None,
    tolerance: float = 0.05,
) -> dict:
    """Run the *unmodified* benchmark (no tone wrapper) on one model and
    check accuracy against a published figure, before any wrapper-condition
    spend happens. This must be run, and must pass, before Part B proceeds
    (task spec: "Validation gate -- do this before spending on the full
    run").

    `expected_accuracy` is deliberately a caller-supplied argument rather
    than a hardcoded constant -- published per-model MMLU-Pro/GPQA numbers
    move as models are updated, and hardcoding a snapshot here would silently
    go stale. Look up the current figure for `model.model_id` from the
    benchmark's own leaderboard immediately before running this.
    """
    tracker = SpendTracker(out_dir / "raw" / "validation_gate.jsonl", phase="validation_gate", cap_usd=5.0)
    correct = 0
    answered = 0
    for item in items:
        row = _call_and_record(
            tracker, model, SYSTEM_PROMPT, item.render(), item.answer_letter,
            item.item_id, tone_level="none", trial=0, phase="validation_gate", subject=item.subject,
        )
        if row.extra["outcome"] == "answered":
            answered += 1
            correct += int(row.is_correct)
    tracker.close()

    observed = correct / answered if answered else float("nan")
    result = {
        "model_key": model.key,
        "model_id": model.model_id,
        "n_items": len(items),
        "n_answered": answered,
        "observed_accuracy": observed,
        "expected_accuracy": expected_accuracy,
        "tolerance": tolerance,
        "passed": (
            expected_accuracy is not None
            and abs(observed - expected_accuracy) <= tolerance
        ),
        "spend_usd": tracker.total_usd,
    }
    return result


def run_part_a_replication(
    models: list[ModelConfig],
    dataset_path: Path,
    out_dir: Path,
    budget_cap_usd: float,
    n_runs: int = 10,
    soft_budget_cap_usd: Optional[float] = None,
) -> list[ResultRow]:
    """Reproduce the Mind Your Tone protocol exactly: their system prompt,
    their "Completely forget this session..." instruction preamble, their
    prompts and tone rewrites as-is (our tone_wrappers are NOT used here --
    see dataset.py module docstring for the confirmed real protocol this
    reproduces), at temperature=0, run n_runs=10 times per prompt to match
    their own NUM_RUNS=10 (confirmed from their notebook)."""
    rows_data = load_mind_your_tone(dataset_path)
    tracker = SpendTracker(
        out_dir / "raw" / "study1_part_a.jsonl", phase="part_a_replication",
        cap_usd=budget_cap_usd, soft_cap_usd=soft_budget_cap_usd,
    )
    all_rows = []
    try:
        for base_model in models:
            model = replace(base_model, temperature=0.0)
            for trial in range(n_runs):
                for row in rows_data:
                    r = _call_and_record(
                        tracker, model, MIND_YOUR_TONE_SYSTEM_PROMPT,
                        render_mind_your_tone_prompt(row.prompt_text), row.answer_letter,
                        item_id=row.base_id, tone_level=row.tone_level, trial=trial,
                        phase="part_a_replication", subject=row.domain,
                        extractor=extract_answer_mind_your_tone,
                    )
                    all_rows.append(r)
    finally:
        tracker.close()
    return all_rows


def run_part_b_remaster(
    models: list[ModelConfig],
    items: list[BenchmarkItem],
    out_dir: Path,
    budget_cap_usd: float,
    temperature: float = 0.0,
    n_trials: int = 1,
    seed_base: int = 1000,
    soft_budget_cap_usd: Optional[float] = None,
) -> list[ResultRow]:
    """Apply the five tone wrappers programmatically to the unmodified
    benchmark question text and run every (model, item, tone, trial)
    combination. The question text is byte-identical across conditions --
    only the prepended wrapper differs (task spec's core design change vs.
    Part A)."""
    tracker = SpendTracker(
        out_dir / "raw" / "study1_part_b.jsonl", phase="part_b_remaster",
        cap_usd=budget_cap_usd, soft_cap_usd=soft_budget_cap_usd,
    )
    all_rows = []
    try:
        for base_model in models:
            for trial in range(n_trials):
                model = replace(base_model, temperature=temperature, seed=(seed_base + trial) if temperature > 0 else base_model.seed)
                for item in items:
                    for tone_key in TONE_ORDER:
                        wrapper = TONE_WRAPPERS[tone_key]
                        prompt = wrapper.apply(item.render())
                        r = _call_and_record(
                            tracker, model, SYSTEM_PROMPT, prompt, item.answer_letter,
                            item_id=item.item_id, tone_level=tone_key, trial=trial,
                            phase="part_b_remaster", subject=item.subject,
                        )
                        all_rows.append(r)
    finally:
        tracker.close()
    return all_rows
