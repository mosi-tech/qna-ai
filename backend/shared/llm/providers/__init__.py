# LLM Providers package

from .base import LLMProvider
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .ollama import OllamaProvider


def create_provider(provider_type: str, api_key: str = "", **kwargs) -> LLMProvider:
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
    elif provider_type.lower() == "ollama":
        # Default to local Ollama unless cloud URL or API key provided
        default_base_url = "http://localhost:11434"
        if api_key or "ollama.com" in kwargs.get("base_url", ""):
            default_base_url = "https://ollama.com/api"
            
        return OllamaProvider(
            api_key,  # Required for Ollama Cloud, optional for local
            kwargs.get("default_model", "qwen3:0.6b" if not api_key else "gpt-oss:120b"),
            kwargs.get("base_url", default_base_url)
        )
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")


__all__ = ["LLMProvider", "AnthropicProvider", "OpenAIProvider", "OllamaProvider", "create_provider"]