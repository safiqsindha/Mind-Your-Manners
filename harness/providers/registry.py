from __future__ import annotations

from .anthropic_provider import AnthropicProvider
from .base import Provider
from .google_provider import GoogleProvider
from .mock_provider import MockProvider
from .openai_compatible import OpenAICompatibleProvider

PROVIDER_REGISTRY: dict[str, Provider] = {
    "mock": MockProvider(),
    "anthropic": AnthropicProvider(),
    "google": GoogleProvider(),
    "openai_compatible": OpenAICompatibleProvider(),
}


def get_provider(name: str) -> Provider:
    try:
        return PROVIDER_REGISTRY[name]
    except KeyError as e:
        raise KeyError(f"Unknown provider {name!r}; known: {sorted(PROVIDER_REGISTRY)}") from e
