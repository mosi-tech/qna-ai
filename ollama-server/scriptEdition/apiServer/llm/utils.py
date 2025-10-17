#!/usr/bin/env python3
"""
LLM Utilities - Configuration and helper functions
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """Configuration for LLM service"""
    provider_type: str
    default_model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.1
    service_name: Optional[str] = None
    use_cli: bool = False
    
    @classmethod
    def from_env(cls, prefix: str = "LLM") -> 'LLMConfig':
        """Create config from environment variables with prefix"""
        provider = os.getenv(f"{prefix}_PROVIDER", "anthropic")
        model = os.getenv(f"{prefix}_MODEL") or cls._get_default_model(provider)
        use_cli = os.getenv(f"{prefix}_USE_CLI", "false").lower() == "true" or \
                  os.getenv(f"{provider.upper()}_USE_CLI", "false").lower() == "true"
        
        return cls(
            provider_type=provider.lower(),
            default_model=model,
            api_key=cls._get_api_key(provider) if not os.getenv(f"{prefix}_API_KEY") else os.getenv(f"{prefix}_API_KEY"),
            base_url=os.getenv(f"{prefix}_BASE_URL") or os.getenv(f"{provider.upper()}_BASE_URL"),
            max_tokens=int(os.getenv(f"{prefix}_MAX_TOKENS", "4000")),
            temperature=float(os.getenv(f"{prefix}_TEMPERATURE", "0.1")),
            use_cli=use_cli
        )
    
    @classmethod
    def for_task(cls, task: str) -> 'LLMConfig':
        """Create task-specific config from environment"""
        task_upper = task.upper()
        
        # Try task-specific env vars first, fallback to general LLM vars
        provider = os.getenv(f"{task_upper}_LLM_PROVIDER") or os.getenv("LLM_PROVIDER", "anthropic")
        model = os.getenv(f"{task_upper}_LLM_MODEL") or cls._get_default_model(provider)
        api_key = os.getenv(f"{task_upper}_LLM_API_KEY") or cls._get_api_key(provider)
        base_url = os.getenv(f"{task_upper}_LLM_BASE_URL") or os.getenv(f"{provider.upper()}_BASE_URL")
        
        # Check for CLI mode - task-specific first, then provider default
        use_cli = os.getenv(f"{task_upper}_LLM_USE_CLI", "false").lower() == "true" or \
                  os.getenv(f"{provider.upper()}_USE_CLI", "false").lower() == "true"
        
        # Task-specific temperature defaults
        temperature_defaults = {
            "ANALYSIS": "0.2",  # Analysis tasks need slightly more creativity for financial insights
            "CONTEXT": "0.1",   # Context tasks should be more deterministic
            "CODE_PROMPT_BUILDER": "0.1",  # Code generation should be deterministic
            "REUSE_EVALUATOR": "0.1"  # Decision making should be consistent
        }
        default_temp = temperature_defaults.get(task_upper, "0.1")
        
        return cls(
            provider_type=provider.lower(),
            default_model=model,
            api_key=api_key,
            base_url=base_url,
            max_tokens=int(os.getenv(f"{task_upper}_LLM_MAX_TOKENS", "10000")),
            temperature=float(os.getenv(f"{task_upper}_LLM_TEMPERATURE", default_temp)),
            use_cli=use_cli
        )
    
    @staticmethod
    def _get_default_model(provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "anthropic": os.getenv("ANTHROPIC_MODEL") or "claude-3-5-haiku-20241022",
            "openai": os.getenv("OPENAI_MODEL") or "gpt-oss:20b", 
            "ollama": os.getenv("OLLAMA_MODEL") or "gpt-oss:20b", 
        }
        return defaults.get(provider.lower(), "")
    
    @staticmethod
    def _get_api_key(provider: str) -> Optional[str]:
        """Get API key for provider"""
        keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "ollama": os.getenv("OLLAMA_API_KEY")  # Support Ollama Cloud API key
        }
        return keys.get(provider.lower())
    

def validate_llm_config(config: LLMConfig) -> Dict[str, Any]:
    """Validate LLM configuration"""
    issues = []
    
    # Check provider
    supported_providers = ["anthropic", "openai", "ollama"]
    if config.provider_type not in supported_providers:
        issues.append(f"Unsupported provider: {config.provider_type}")
    
    # Skip API key validation if using CLI mode
    if not config.use_cli:
        # Check API key for cloud providers
        if config.provider_type in ["anthropic", "openai"] and not config.api_key:
            issues.append(f"API key required for {config.provider_type}")
        
        # Check for Ollama Cloud (if base_url contains ollama.com, API key is required)
        if config.provider_type == "ollama" and config.base_url and "ollama.com" in config.base_url and not config.api_key:
            issues.append("API key required for Ollama Cloud")
    
    # Check model name
    if not config.default_model:
        issues.append("Model name is required")
    
    # Check temperature range
    if not 0.0 <= config.temperature <= 2.0:
        issues.append(f"Temperature must be between 0.0 and 2.0, got {config.temperature}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "config": {
            "provider": config.provider_type,
            "model": config.default_model,
            "has_api_key": bool(config.api_key),
            "temperature": config.temperature,
            "use_cli": config.use_cli
        }
    }