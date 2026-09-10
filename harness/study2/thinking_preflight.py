"""Phase 0.5 gate for the thinking arm (README "The thinking arm"): three
cheap, blocking probe checks that must pass before the calibration arm
(harness/config.py:GPT_LUNA_CALIBRATION) gets real spend.

Reasoning-token accounting is the primary outcome measure for this arm, and
it can silently fail in ways that look like a normal run:

  1. **Reasoning tokens survive the route.** OpenRouter is a protocol-
     translation layer, and prompt-induced-waste work (arXiv 2608.01347)
     found reasoning-token reporting is inconsistent across serving routes
     and can be silently dropped by such layers. A *missing*
     `completion_tokens_details.reasoning_tokens` field (see
     ProviderResponse.reasoning_tokens_reported) is a different failure
     from a reported zero -- if the field is missing, the primary outcome
     is unmeasurable, and this check must stop the run rather than let a
     silent 0 flow into the analysis as if it meant "no reasoning
     happened."
  2. **The off condition returns zero, the on condition returns non-zero.**
     Trust the response, not the config -- a model can report the wrong
     thing even when the request parameter was sent correctly.
  3. **The two conditions differ on a probe task.** Identical token counts
     between on/off means the reasoning_effort parameter isn't actually
     taking effect, not that reasoning happened to cost the same either way.

All three run as one probe call per condition (cheap, blocking) before any
real calibration-arm spend. A failure on any check must stop the run --
callers must not catch-and-continue, same convention as BudgetExceeded and
ProviderPinViolation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..providers.base import ModelConfig, ProviderResponse
from ..providers.registry import get_provider
from ..spend_tracker import SpendTracker

DEFAULT_PROBE_INSTRUCTION = (
    "A store had 120 apples. It sold 37 in the morning and 28 in the "
    "afternoon, then received a delivery of 15 more. How many apples does "
    "the store have now? Show your reasoning, then give the final number."
)


@dataclass
class PreflightCheck:
    name: str
    passed: bool
    detail: str


@dataclass
class PreflightReport:
    on_model_key: str
    off_model_key: str
    on_reasoning_tokens: int
    off_reasoning_tokens: int
    on_total_tokens: int
    off_total_tokens: int
    checks: list[PreflightCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


def _probe(tracker: SpendTracker, model: ModelConfig, probe_instruction: str) -> ProviderResponse:
    provider = get_provider(model.provider)
    tracker.check_before_call(estimated_cost_usd=0.01)
    response = provider.complete(model, "You are a careful assistant.", [{"role": "user", "content": probe_instruction}])
    return response


def run_thinking_preflight(
    tracker: SpendTracker,
    on_model: ModelConfig,
    off_model: ModelConfig,
    probe_instruction: str = DEFAULT_PROBE_INSTRUCTION,
) -> PreflightReport:
    """One probe call per condition (two calls total), then the three
    checks from this module's docstring. Does not raise on failure --
    callers (the CLI) decide how to report/exit; see cmd_study2_thinking_preflight."""
    on_response = _probe(tracker, on_model, probe_instruction)
    off_response = _probe(tracker, off_model, probe_instruction)

    checks = [
        PreflightCheck(
            name="reasoning_tokens_field_present",
            passed=on_response.reasoning_tokens_reported and off_response.reasoning_tokens_reported,
            detail=(
                "Both conditions reported a reasoning_tokens field."
                if on_response.reasoning_tokens_reported and off_response.reasoning_tokens_reported
                else (
                    f"reasoning_tokens field missing from the raw response for: "
                    f"{'on' if not on_response.reasoning_tokens_reported else ''}"
                    f"{' and ' if not on_response.reasoning_tokens_reported and not off_response.reasoning_tokens_reported else ''}"
                    f"{'off' if not off_response.reasoning_tokens_reported else ''} condition -- "
                    "reasoning-token accounting is unmeasurable through this route; do not trust a "
                    "reported 0 as meaning 'no reasoning happened' when the field itself is absent."
                )
            ),
        ),
        PreflightCheck(
            name="off_zero_on_nonzero",
            passed=off_response.reasoning_tokens == 0 and on_response.reasoning_tokens > 0,
            detail=(
                f"off condition reasoning_tokens={off_response.reasoning_tokens} "
                f"(want 0), on condition reasoning_tokens={on_response.reasoning_tokens} (want >0)."
            ),
        ),
        PreflightCheck(
            name="on_off_differ_on_probe",
            passed=on_response.total_tokens != off_response.total_tokens,
            detail=(
                f"on total_tokens={on_response.total_tokens}, off total_tokens={off_response.total_tokens} -- "
                + ("differ, as expected." if on_response.total_tokens != off_response.total_tokens else
                   "IDENTICAL -- the reasoning_effort parameter does not appear to be taking effect.")
            ),
        ),
    ]

    return PreflightReport(
        on_model_key=on_model.key,
        off_model_key=off_model.key,
        on_reasoning_tokens=on_response.reasoning_tokens,
        off_reasoning_tokens=off_response.reasoning_tokens,
        on_total_tokens=on_response.total_tokens,
        off_total_tokens=off_response.total_tokens,
        checks=checks,
    )
