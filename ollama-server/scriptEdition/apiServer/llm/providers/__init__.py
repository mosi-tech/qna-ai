# LLM Providers package

from .base import LLMProvider
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider


def create_provider(provider_type: str, api_key: str, **kwargs) -> LLMProvider:
    """Factory function to create LLM providers"""
    if provider_type.lower() == "anthropic":
        return AnthropicProvider(
            api_key, 
            kwargs.get("default_model", "claude-3-5-haiku-20241022"),
            kwargs.get("base_url")
        )
    elif provider_type.lower() == "openai":
        return OpenAIProvider(
            api_key, 
            kwargs.get("default_model", "gpt-4-turbo-preview"),
            kwargs.get("base_url")
        )
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")


__all__ = ["LLMProvider", "AnthropicProvider", "OpenAIProvider", "create_provider"]