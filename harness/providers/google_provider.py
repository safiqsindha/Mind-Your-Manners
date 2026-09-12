"""Direct Google Gemini (generativelanguage) provider.

Used for the Gemini Flash-tier model in the target model list. Requires
GOOGLE_API_KEY (or GEMINI_API_KEY).
"""
from __future__ import annotations

import os
from typing import Any, Optional

import requests

from .base import ModelConfig, Provider, ProviderError, ProviderResponse

API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"


class GoogleProvider(Provider):
    name = "google"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

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
            raise ProviderError("GOOGLE_API_KEY / GEMINI_API_KEY is not set")

        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        generation_config: dict[str, Any] = {
            "temperature": model.temperature,
            "maxOutputTokens": model.max_tokens,
        }
        if model.seed is not None:
            generation_config["seed"] = model.seed
        if model.thinking_budget_tokens is not None:
            generation_config["thinkingConfig"] = {"thinkingBudget": model.thinking_budget_tokens}

        body: dict[str, Any] = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system}]},
            "generationConfig": generation_config,
        }
        if tools:
            body["tools"] = tools

        resp = requests.post(
            f"{API_ROOT}/{model.model_id}:generateContent",
            params={"key": self.api_key},
            json=body,
            timeout=180,
        )
        if resp.status_code >= 400:
            raise ProviderError(f"Gemini API error {resp.status_code}: {resp.text[:2000]}")
        data = resp.json()

        candidates = data.get("candidates") or []
        if not candidates:
            # Blocked prompt (e.g. safety filter) -- treat as a refusal, not an error.
            reason = (data.get("promptFeedback") or {}).get("blockReason", "unknown")
            return ProviderResponse(
                text="",
                prompt_tokens=(data.get("usageMetadata") or {}).get("promptTokenCount", 0),
                completion_tokens=0,
                refused=True,
                raw=data,
                error=f"blocked: {reason}",
            )

        candidate = candidates[0]
        finish_reason = candidate.get("finishReason", "")
        parts = (candidate.get("content") or {}).get("parts") or []
        text_parts = [p.get("text", "") for p in parts if "text" in p]
        tool_calls = []
        for p in parts:
            if "functionCall" in p:
                fc = p["functionCall"]
                tool_calls.append({"id": fc.get("name"), "name": fc.get("name"), "arguments": fc.get("args", {})})

        usage = data.get("usageMetadata", {})
        return ProviderResponse(
            text="".join(text_parts),
            prompt_tokens=usage.get("promptTokenCount", 0),
            completion_tokens=usage.get("candidatesTokenCount", 0),
            reasoning_tokens=usage.get("thoughtsTokenCount", 0) or 0,
            # Google is the one route here where thinking is NOT folded into
            # the completion figure: usageMetadata reports promptTokenCount,
            # candidatesTokenCount and thoughtsTokenCount as three disjoint
            # counts whose sum is totalTokenCount. So this provider's totals
            # must keep the reasoning term that the OpenAI-style routes must
            # drop -- see providers/base.py:reasoning_included_in_completion.
            reasoning_included_in_completion=False,
            refused=finish_reason in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"),
            raw=data,
            tool_calls=tool_calls,
        )
