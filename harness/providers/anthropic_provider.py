"""Direct Anthropic Messages API provider.

Only used for an optional frontier spot-check (see task spec, "Optional
frontier spot-check on a task subset"). Requires ANTHROPIC_API_KEY.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import requests

from .base import ModelConfig, Provider, ProviderError, ProviderResponse

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

    def available(self) -> bool:
        return bool(self.api_key)

    def complete(
        self,
        model: ModelConfig,
        system: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> ProviderResponse:
        if not self.api_key:
            raise ProviderError("ANTHROPIC_API_KEY is not set")

        body: dict[str, Any] = {
            "model": model.model_id,
            "max_tokens": model.max_tokens,
            "temperature": model.temperature,
            "system": system,
            "messages": messages,
        }
        if model.thinking_budget_tokens:
            body["thinking"] = {
                "type": "enabled",
                "budget_tokens": model.thinking_budget_tokens,
            }
        if tools:
            body["tools"] = tools

        resp = requests.post(
            API_URL,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
            json=body,
            timeout=120,
        )
        if resp.status_code >= 400:
            raise ProviderError(f"Anthropic API error {resp.status_code}: {resp.text[:2000]}")
        data = resp.json()

        text_parts = []
        tool_calls = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                tool_calls.append(
                    {"id": block.get("id"), "name": block.get("name"), "arguments": block.get("input", {})}
                )

        usage = data.get("usage", {})
        refused = data.get("stop_reason") == "refusal"

        return ProviderResponse(
            text="".join(text_parts),
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            refused=refused,
            raw=data,
            tool_calls=tool_calls,
        )
