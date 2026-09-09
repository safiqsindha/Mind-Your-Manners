"""OpenAI-Chat-Completions-compatible provider.

Covers the bulk of the model list in the task spec: DeepSeek and Qwen
(direct APIs are OpenAI-compatible), and any model reachable via OpenRouter
(Gemini Flash, Llama/Gemma tier, DeepSeek, Qwen) with the provider pinned
explicitly so OpenRouter cannot silently swap the backend mid-run -- see
`ModelConfig.provider_pin`.

Which base URL / API key env var to use is decided per ModelConfig via
`api_base` and `key`; see harness/config.py for the concrete model list.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import requests

from .base import ModelConfig, Provider, ProviderError, ProviderResponse

# key -> env var holding the API key for that backend.
API_KEY_ENV_BY_BASE = {
    "https://openrouter.ai/api/v1": "OPENROUTER_API_KEY",
    "https://api.deepseek.com": "DEEPSEEK_API_KEY",
    "https://dashscope.aliyuncs.com/compatible-mode/v1": "DASHSCOPE_API_KEY",
}


class OpenAICompatibleProvider(Provider):
    name = "openai_compatible"

    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key

    def _resolve_key(self, model: ModelConfig) -> Optional[str]:
        if self._explicit_key:
            return self._explicit_key
        env_var = API_KEY_ENV_BY_BASE.get(model.api_base or "", "OPENROUTER_API_KEY")
        return os.environ.get(env_var)

    def available(self, model: ModelConfig) -> bool:
        return bool(self._resolve_key(model))

    def complete(
        self,
        model: ModelConfig,
        system: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> ProviderResponse:
        api_key = self._resolve_key(model)
        if not api_key:
            raise ProviderError(f"No API key found for base_url={model.api_base!r}")

        base_url = (model.api_base or "https://openrouter.ai/api/v1").rstrip("/")
        full_messages = [{"role": "system", "content": system}] + messages

        body: dict[str, Any] = {
            "model": model.model_id,
            "messages": full_messages,
            "temperature": model.temperature,
            "max_tokens": model.max_tokens,
        }
        if model.seed is not None:
            body["seed"] = model.seed
        if tools:
            body["tools"] = tools
        if model.reasoning_effort:
            body["reasoning"] = {"effort": model.reasoning_effort}
        if "openrouter.ai" in base_url and model.provider_pin:
            body["provider"] = {"order": [model.provider_pin], "allow_fallbacks": False}

        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
            json=body,
            timeout=180,
        )
        if resp.status_code >= 400:
            raise ProviderError(f"{base_url} API error {resp.status_code}: {resp.text[:2000]}")
        data = resp.json()

        choice = data["choices"][0]
        message = choice.get("message", {})
        text = message.get("content") or ""
        finish_reason = choice.get("finish_reason", "")
        refused = finish_reason in ("content_filter", "refusal")

        tool_calls = []
        for tc in message.get("tool_calls") or []:
            fn = tc.get("function", {})
            tool_calls.append({"id": tc.get("id"), "name": fn.get("name"), "arguments": fn.get("arguments")})

        usage = data.get("usage", {})
        reasoning_tokens = 0
        details = usage.get("completion_tokens_details") or {}
        if isinstance(details, dict):
            reasoning_tokens = details.get("reasoning_tokens", 0) or 0

        return ProviderResponse(
            text=text,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            reasoning_tokens=reasoning_tokens,
            refused=refused,
            raw=data,
            tool_calls=tool_calls,
        )
