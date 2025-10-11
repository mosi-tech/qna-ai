"""
Abstract base class for LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, base_url: str, default_model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        
        # Cache for processed data
        self._processed_system_cache = {}
        self._processed_tools_cache = {}
        self._raw_system_prompt = None
        self._raw_tools = None
    
    @abstractmethod
    async def call_api(self, model: str, messages: List[Dict[str, Any]], 
                      max_tokens: int = 4000, enable_caching: bool = False,
                      override_system_prompt: Optional[str] = None,
                      override_tools: Optional[List[Dict[str, Any]]] = None,
                      force_api: bool = False) -> Dict[str, Any]:
        """Make API call to LLM provider using stored system prompt and tools"""
        pass
    
    @abstractmethod
    def parse_response(self, response_data: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse response and extract content + tool calls"""
        pass
    
    @abstractmethod
    def format_tool_results(self, tool_calls: List[Dict[str, Any]], 
                           tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format tool results for next API call"""
        pass

    def format_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format tool calls for next API call"""
        pass
    
    @abstractmethod
    def supports_caching(self) -> bool:
        """Whether this provider supports prompt caching"""
        pass
    
    def set_system_prompt(self, system_prompt: str):
        """Set and cache system prompt"""
        if self._raw_system_prompt != system_prompt:
            self._raw_system_prompt = system_prompt
            self._processed_system_cache.clear()  # Invalidate cache
    
    def set_tools(self, tools: List[Dict[str, Any]]):
        """Set and cache tools"""
        # Simple comparison - if length or first tool changes, invalidate
        tools_changed = (
            self._raw_tools is None or 
            len(self._raw_tools) != len(tools) or
            (tools and self._raw_tools and tools[0] != self._raw_tools[0])
        )
        
        if tools_changed:
            self._raw_tools = tools.copy() if tools else []
            self._processed_tools_cache.clear()  # Invalidate cache
    
    @abstractmethod
    def get_processed_system_data(self, enable_caching: bool = True) -> Any:
        """Get system prompt processed for this provider"""
        pass
    
    @abstractmethod  
    def get_processed_tools(self, enable_caching: bool = True) -> List[Dict[str, Any]]:
        """Get tools processed for this provider"""
        pass