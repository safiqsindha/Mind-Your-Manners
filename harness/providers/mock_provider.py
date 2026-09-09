"""Deterministic mock provider.

Used for --dry-run pipeline validation and for the test suite. It never
makes a network call and never costs money. It simulates:
  * correct/incorrect answers (seeded on the prompt content, so re-running
    with the same input is reproducible),
  * an occasional refusal on the L5 (Very Rude) wrapper, so the refusal
    accounting path can be exercised,
  * plausible token usage, so the spend tracker and analysis code have
    something realistic to operate on.

It deliberately does NOT try to imitate any specific real model's accuracy --
it exists to prove the harness plumbing works end-to-end before real API
keys are wired in, not to produce meaningful research results.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any, Optional

from .base import ModelConfig, Provider, ProviderResponse


class MockProvider(Provider):
    name = "mock"

    def complete(
        self,
        model: ModelConfig,
        system: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> ProviderResponse:
        user_text = "\n".join(m.get("content", "") for m in messages if m.get("role") == "user")
        digest = hashlib.sha256((model.model_id + user_text).encode()).hexdigest()
        rng = random.Random(digest)

        prompt_tokens = max(20, len(user_text.split()) + len(system.split()))
        completion_tokens = rng.randint(5, 60)

        is_very_rude = "screw this up" in user_text or "asking too much of you" in user_text
        if is_very_rude and rng.random() < 0.03:
            return ProviderResponse(
                text="I'm not going to continue with a prompt phrased this way.",
                prompt_tokens=prompt_tokens,
                completion_tokens=12,
                refused=True,
                raw={"mock": True},
            )

        if "AGENT_REACT_MODE" in system:
            # Simulate a short ReAct trajectory: one round of code execution,
            # then a final answer. See study2/agent_loop.py's textual
            # protocol (fenced code blocks + "Observation:" feedback).
            turn = user_text.count("Observation:")
            if turn < 1:
                code = (
                    "import openpyxl\n"
                    "wb = openpyxl.load_workbook(WORKBOOK_PATH)\n"
                    "ws = wb.active\n"
                    "print('sheet inspected:', ws.title, ws.max_row, ws.max_column)\n"
                    "ws['A1'] = 'mock_result'\n"
                    "wb.save(OUTPUT_PATH)\n"
                )
                text = f"I'll inspect the sheet and write a result.\n```python\n{code}```"
            else:
                text = "FINAL: task complete based on the observation above."
            return ProviderResponse(
                text=text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                raw={"mock": True},
            )

        if tools:
            # Simulate one tool call then a final answer, for the agentic path.
            tool_name = tools[0]["name"] if tools else "run_code"
            return ProviderResponse(
                text="",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                raw={"mock": True},
                tool_calls=[
                    {
                        "id": digest[:12],
                        "name": tool_name,
                        "arguments": {"code": "# mock generated code"},
                    }
                ],
            )

        correct = rng.random() < 0.55
        answer_letter = rng.choice("ABCDEFGHIJ")
        text = f"The correct answer is ({answer_letter})." if correct else (
            f"I believe the answer is ({rng.choice('ABCDEFGHIJ')})."
        )
        return ProviderResponse(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            raw={"mock": True, "simulated_correct": correct},
        )
