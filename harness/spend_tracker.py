"""Per-call result logging, cost accounting, and budget-cap enforcement.

Every provider call in either study is wrapped through `SpendTracker.record()`,
which appends one row to a JSONL file under results/raw/ (task spec: "every
API response with full metadata, one row per call") and raises
`BudgetExceeded` the moment projected spend would cross the cap for that
phase. Callers (study1/runner.py, study2/runner.py) must stop immediately on
that exception -- do not catch-and-continue.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from .providers.base import ModelConfig, ProviderResponse


class BudgetExceeded(RuntimeError):
    def __init__(self, phase: str, cap_usd: float, projected_usd: float):
        self.phase = phase
        self.cap_usd = cap_usd
        self.projected_usd = projected_usd
        super().__init__(
            f"[{phase}] projected spend ${projected_usd:.2f} exceeds cap ${cap_usd:.2f} -- halting run"
        )


@dataclass
class ResultRow:
    """One row per API call. This is the on-disk schema for results/raw/*.jsonl."""

    row_id: str
    study: str  # "study1" | "study2"
    phase: str  # e.g. "part_a_replication", "part_b_remaster", "pilot", "core", "frontier"
    item_id: str  # benchmark item / task id
    tone_level: str  # tone_wrappers.TONE_ORDER key, or "none" for the validation-gate run
    trial: int  # 0-indexed trial number within (item, tone) condition
    model_key: str
    model_id: str
    provider: str
    temperature: float
    seed: Optional[int]
    reasoning_effort: Optional[str]
    thinking_budget_tokens: Optional[int]
    prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: int
    cost_usd: float
    latency_s: float
    refused: bool
    error: Optional[str]
    response_text: str
    extracted_answer: Optional[str]
    is_correct: Optional[bool]
    timestamp: float
    cached_tokens: int = 0  # usage.prompt_tokens_details.cached_tokens -- measure only, see config.py
    served_provider: Optional[str] = None  # actual OpenRouter backend that served this call
    raw_response: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


def compute_cost_usd(model: ModelConfig, response: ProviderResponse) -> float:
    # Some providers (e.g. claude_cli_provider, which shells out to a
    # billed CLI session) report their own authoritative dollar cost --
    # prefer that over the ModelConfig price table when present, since the
    # price table is 0 for those models (there's no per-token price to
    # apply; the CLI already did the accounting).
    reported = response.raw.get("total_cost_usd")
    if reported is not None:
        return float(reported)
    # OpenRouter reports its own actually-billed cost per call
    # (usage.cost) -- prefer that over our static price table too, since
    # it reflects what was really charged rather than a snapshot that can
    # drift (see harness/config.py's VERIFY-table caveat).
    usage = response.raw.get("usage") or {}
    if isinstance(usage, dict) and usage.get("cost") is not None:
        return float(usage["cost"])
    input_cost = (response.prompt_tokens / 1_000_000) * model.input_price_per_1m
    output_cost = ((response.completion_tokens + response.reasoning_tokens) / 1_000_000) * model.output_price_per_1m
    return input_cost + output_cost


class SpendTracker:
    def __init__(self, out_path: Path, phase: str, cap_usd: float):
        self.out_path = out_path
        self.phase = phase
        self.cap_usd = cap_usd
        self.total_usd = 0.0
        self.n_calls = 0
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.out_path, "a", encoding="utf-8")

    def check_before_call(self, estimated_cost_usd: float) -> None:
        projected = self.total_usd + estimated_cost_usd
        if projected > self.cap_usd:
            raise BudgetExceeded(self.phase, self.cap_usd, projected)

    def record(self, row: ResultRow) -> None:
        self.total_usd += row.cost_usd
        self.n_calls += 1
        self._fh.write(json.dumps(asdict(row), default=str) + "\n")
        self._fh.flush()
        if self.total_usd > self.cap_usd:
            raise BudgetExceeded(self.phase, self.cap_usd, self.total_usd)

    def summary(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "n_calls": self.n_calls,
            "total_usd": round(self.total_usd, 4),
            "cap_usd": self.cap_usd,
        }

    def close(self) -> None:
        self._fh.close()

    def __enter__(self) -> "SpendTracker":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def append_spend_log(log_path: Path, entry: dict[str, Any]) -> None:
    """Append one line to the running total-spend log (task spec: "Total spend log")."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": time.time(), **entry}
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
