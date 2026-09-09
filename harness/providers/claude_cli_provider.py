"""Provider that shells out to the local `claude` CLI in headless mode.

This exists purely so the harness can be smoke-tested with *genuine*
inference from inside a Claude Code session that has no raw
ANTHROPIC_API_KEY (session/OAuth auth only, as in a claude.ai/code remote
environment) -- see README.md "Smoke testing with real inference". It is
NOT one of the study's target models (Gemini/DeepSeek/Qwen/Llama tiers) and
must never be substituted for them in a real Part A/B or Study 2 run --
it exists only to prove the harness reads/scores real (non-mocked) model
output correctly.

Each call is a fresh `claude -p` subprocess, which means a fresh system
prompt and therefore a full prompt-cache-creation charge every time (no
warm cache across calls) -- this is meaningfully more expensive per call
than a normal API call to the same model. Keep smoke tests small.

`--restricted` and an empty `--allowed-tools` are used to stop the CLI from
doing anything agentic (file edits, bash, web) -- we want a plain text
completion, not a Claude Code session that goes and does its own thing.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any, Optional

from .base import ModelConfig, Provider, ProviderError, ProviderResponse

DEFAULT_TIMEOUT_S = 120


class ClaudeCLIProvider(Provider):
    name = "claude_cli"

    def __init__(self, claude_bin: Optional[str] = None):
        self.claude_bin = claude_bin or shutil.which("claude")

    def available(self) -> bool:
        return bool(self.claude_bin)

    def complete(
        self,
        model: ModelConfig,
        system: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> ProviderResponse:
        if not self.claude_bin:
            raise ProviderError("`claude` binary not found on PATH")

        # The CLI takes one prompt string. For the (common) single-user-message
        # case this is exactly the user content; for a multi-turn agent
        # trajectory (Study 2) we flatten prior turns into the prompt text,
        # which is a best-effort approximation for smoke-testing purposes
        # only -- it does not preserve the provider's native multi-turn state.
        if len(messages) == 1 and messages[0]["role"] == "user":
            prompt = messages[0]["content"]
        else:
            prompt = "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in messages)

        cmd = [
            self.claude_bin,
            "-p",
            prompt,
            "--restricted",
            "--allowed-tools",
            "",
            "--model",
            model.model_id,
            "--system-prompt",
            system,
            "--output-format",
            "json",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT_S)
        except subprocess.TimeoutExpired as e:
            raise ProviderError(f"claude CLI timed out after {DEFAULT_TIMEOUT_S}s") from e

        if not proc.stdout.strip():
            raise ProviderError(f"claude CLI produced no output (exit {proc.returncode}): {proc.stderr[:2000]}")

        data = json.loads(proc.stdout)
        if data.get("is_error"):
            return ProviderResponse(
                text="",
                prompt_tokens=0,
                completion_tokens=0,
                error=data.get("result", "unknown claude CLI error"),
                raw=data,
            )

        usage = data.get("usage", {})
        refused = data.get("stop_reason") == "refusal"

        return ProviderResponse(
            text=data.get("result", ""),
            prompt_tokens=usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0) + usage.get("cache_read_input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            reasoning_tokens=(usage.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0,
            latency_s=(data.get("duration_ms") or 0) / 1000.0,
            refused=refused,
            raw=data,
        )
