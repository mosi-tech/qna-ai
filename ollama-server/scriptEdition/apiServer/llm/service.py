#!/usr/bin/env python3
"""
Core LLM Service - Pure LLM provider abstraction
"""

import logging
from typing import Dict, Any, Optional, List
from .providers import create_provider, LLMProvider
from .utils import LLMConfig, validate_llm_config

logger = logging.getLogger(__name__)

class LLMService:
    """Pure LLM service - provider abstraction without business logic"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        
        # Validate configuration
        validation = validate_llm_config(config)
        if not validation["valid"]:
            raise ValueError(f"Invalid LLM config: {validation['issues']}")
        
        # Create provider
        self.provider = self._create_provider()
        
        # Store default tools for reset capability
        self.default_tools = []
        self._tools_loaded = False
        
        logger.info(f"🤖 Initialized LLM service: {config.provider_type}/{config.default_model}")
    
    async def ensure_tools_loaded(self):
        """Load MCP tools if not already loaded"""
        if self._tools_loaded:
            return
        
        try:
            if self.config.service_name:
                # Use simplified MCP loader with service-specific configuration
                from .mcp_tools import _mcp_loader
                self.default_tools = await _mcp_loader.load_tools_for_service(self.config.service_name)
                logger.info(f"🔧 Loaded {len(self.default_tools)} MCP tools for service '{self.config.service_name}'")
            else:
                # No service name - use default configuration
                from .mcp_tools import _mcp_loader
                self.default_tools = await _mcp_loader.load_tools_for_service("default")
                logger.info(f"🔧 Loaded {len(self.default_tools)} MCP tools using default config")
                
            self.provider.set_tools(self.default_tools)
        except Exception as e:
            logger.error(f"❌ Failed to load MCP tools: {e}")
            self.default_tools = []
        
        self._tools_loaded = True
    
    def override_tools(self, tools: List[Dict[str, Any]]):
        """Override tools at runtime"""
        self.provider.set_tools(tools)
        logger.info(f"🔄 Overrode tools: {len(tools)} tools")
    
    def reset_to_default_tools(self):
        """Reset to default MCP tools"""
        self.provider.set_tools(self.default_tools)
        logger.info(f"↩️ Reset to default tools: {len(self.default_tools)} tools")
    
    async def load_tools_for_service(self, service_name: str):
        """Load tools for a specific service (bypasses current service config)"""
        try:
            from .mcp_tools import _mcp_loader
            tools = await _mcp_loader.load_tools_for_service(service_name)
            self.provider.set_tools(tools)
            logger.info(f"📁 Loaded {len(tools)} tools for service '{service_name}'")
        except Exception as e:
            logger.error(f"❌ Failed to load tools for service '{service_name}': {e}")
    
    def _create_provider(self) -> LLMProvider:
        """Create the appropriate LLM provider"""
        if self.config.provider_type == "anthropic":
            if not self.config.api_key:
                logger.warning("ANTHROPIC_API_KEY not provided")
            return create_provider(
                "anthropic", 
                self.config.api_key, 
                default_model=self.config.default_model,
                base_url=self.config.base_url
            )
            
        elif self.config.provider_type == "openai":
            if not self.config.api_key:
                logger.warning("OPENAI_API_KEY not provided")
            return create_provider(
                "openai", 
                self.config.api_key, 
                default_model=self.config.default_model,
                base_url=self.config.base_url
            )
            
        elif self.config.provider_type == "ollama":
            return create_provider(
                "ollama",
                self.config.api_key or "",  # Ollama doesn't require API key
                default_model=self.config.default_model,
                base_url=self.config.base_url
            )
            
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider_type}")
    
    @property
    def provider_type(self) -> str:
        """Get provider type"""
        return self.config.provider_type
    
    @property
    def default_model(self) -> str:
        """Get default model"""
        return self.config.default_model
    
    async def make_request(self, 
                         messages: List[Dict[str, str]], 
                         model: Optional[str] = None,
                         system_prompt: Optional[str] = None,
                         tools: Optional[List[Dict[str, Any]]] = None,
                         max_tokens: Optional[int] = None,
                         temperature: Optional[float] = None,
                         force_api: bool = False,
                         **kwargs) -> Dict[str, Any]:
        """
        Make a request to the LLM provider
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Override default model
            system_prompt: System prompt for the conversation
            tools: Tools available for function calling
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict with 'success', 'content', 'tool_calls', etc.
        """
        try:
            # Ensure MCP tools are loaded
            await self.ensure_tools_loaded()
            
            # Use provided values or defaults from config
            model = model or self.default_model
            max_tokens = max_tokens or self.config.max_tokens
            temperature = temperature if temperature is not None else self.config.temperature
            
            # Set tools on provider if provided
            if tools:
                self.provider.set_tools(tools)
            
            # Set system prompt if provided
            if system_prompt:
                self.provider.set_system_prompt(system_prompt)
            
            # Make the request using provider's call_api method
            # Note: temperature not yet supported by provider interface
            raw_response = await self.provider.call_api(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                enable_caching=kwargs.get('enable_caching', False),
                force_api=force_api
            )
            
            # Check if the call was successful
            if not raw_response.get("success"):
                return raw_response
            
            # Parse the response using the provider's parse method
            content, tool_calls = self.provider.parse_response(raw_response.get("data", {}))
            
            # Return standardized response format
            return {
                "success": True,
                "content": content,
                "tool_calls": tool_calls,
                "provider": raw_response.get("provider", self.provider_type),
                "model": model
            }
            
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider_type
            }
    
    async def simple_completion(self, 
                              prompt: str,
                              model: Optional[str] = None,
                              system_prompt: Optional[str] = None,
                              max_tokens: Optional[int] = None,
                              temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Simple text completion without tools
        
        Args:
            prompt: User prompt
            model: Override default model  
            system_prompt: System prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Returns:
            Dict with 'success', 'content', etc.
        """
        messages = [{"role": "user", "content": prompt}]
        
        return await self.make_request(
            messages=messages,
            model=model,
            system_prompt=system_prompt,
            tools=None,  # No tools for simple completion
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    async def warm_cache(self, model: Optional[str] = None) -> bool:
        """Warm up the LLM cache with a simple request"""
        try:
            model = model or self.default_model
            logger.info(f"🔥 Warming cache for {self.provider_type}/{model}")
            
            result = await self.simple_completion(
                prompt="Hello, please respond with 'Ready'",
                model=model,
                max_tokens=10
            )
            
            if result.get("success"):
                logger.info(f"✅ Cache warmed for {model}")
                return True
            else:
                logger.warning(f"⚠️ Cache warm failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Cache warm error: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get current configuration info"""
        return {
            "provider": self.provider_type,
            "model": self.default_model,
            "has_api_key": bool(self.config.api_key),
            "base_url": self.config.base_url,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if LLM service is healthy"""
        try:
            result = await self.simple_completion(
                prompt="Health check",
                max_tokens=5
            )
            
            return {
                "success": True,
                "healthy": result.get("success", False),
                "provider": self.provider_type,
                "model": self.default_model,
                "error": result.get("error") if not result.get("success") else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "healthy": False,
                "provider": self.provider_type,
                "error": str(e)
            }

# Factory function for easy service creation
def create_llm_service(task: Optional[str] = None, config: Optional[LLMConfig] = None) -> LLMService:
    """
    Create LLM service with task-specific or custom configuration
    
    Args:
        task: Task name for task-specific config (e.g., "CONTEXT", "ANALYSIS")
        config: Custom LLMConfig object
        
    Returns:
        Configured LLMService instance
    """
    if config:
        return LLMService(config)
    elif task:
        config = LLMConfig.for_task(task)
        return LLMService(config)
    else:
        config = LLMConfig.from_env()
        return LLMService(config)

# Convenience functions for common configurations
def create_analysis_llm() -> LLMService:
    """Create LLM service optimized for analysis tasks"""
    config = LLMConfig.for_task("ANALYSIS")
    config.service_name = "analysis"
    return LLMService(config)

def create_context_llm() -> LLMService:
    """Create LLM service optimized for context tasks"""
    config = LLMConfig.for_task("CONTEXT") 
    config.service_name = "context"
    return LLMService(config)

def create_code_prompt_builder_llm() -> LLMService:
    """Create LLM service optimized for code prompt building tasks"""
    config = LLMConfig.for_task("CODE_PROMPT_BUILDER")
    config.service_name = "code-prompt-builder"
    return LLMService(config)

def create_reuse_evaluator_llm() -> LLMService:
    """Create LLM service optimized for reuse evaluation tasks"""
    config = LLMConfig.for_task("REUSE_EVALUATOR")
    config.service_name = "reuse-evaluator"
    return LLMService(config)