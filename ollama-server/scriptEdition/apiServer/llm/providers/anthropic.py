"""
Anthropic Claude API provider implementation
"""

import json
import logging
import httpx
from typing import Dict, Any, List, Tuple, Optional

from .base import LLMProvider

logger = logging.getLogger("anthropic-provider")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: str, default_model: str = "claude-3-5-haiku-20241022", base_url: str = None):
        if base_url is None:
            base_url = "https://api.anthropic.com/v1"
        super().__init__(api_key, base_url, default_model)
    
    def supports_caching(self) -> bool:
        return True
    
    async def call_api(self, model: str, messages: List[Dict[str, Any]], 
                      max_tokens: int = 4000, enable_caching: bool = False,
                      override_system_prompt: Optional[str] = None,
                      override_tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Make Anthropic API call using stored system prompt and tools"""
        
        # Use overrides if provided, otherwise use stored data
        if override_system_prompt is not None:
            self.set_system_prompt(override_system_prompt)
        if override_tools is not None:
            self.set_tools(override_tools)
        
        # Get processed system data (using stored system prompt)
        system_data = self.get_processed_system_data(enable_caching)
        processed_tools = self.get_processed_tools(enable_caching) if self._raw_tools else None

        # Filter out system messages from messages array (Anthropic handles separately)
        user_messages = [msg for msg in messages if msg["role"] != "system"]
        
        request_data = {
            "model": model,
            "system": system_data,
            "messages": user_messages,
            "max_tokens": max_tokens
        }

         # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Add processed tools if we have them stored
        if processed_tools:
            request_data["tools"] = processed_tools
            headers["anthropic-beta"] = "tools-2024-05-16"
        
        
        # Make API call
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/messages",
                json=request_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "provider": "anthropic"
                }
            else:
                return {
                    "success": False,
                    "error": f"Anthropic API error: {response.status_code} - {response.text}",
                    "provider": "anthropic"
                }
    
    def parse_response(self, response_data: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse Anthropic response format"""
        content_blocks = response_data.get("content", [])
        text_content = ""
        tool_calls = []
        
        for block in content_blocks:
            if block.get("type") == "text":
                text_content += block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_calls.append({
                    "function": {
                        "name": block.get("name"),
                        "arguments": block.get("input", {})
                    },
                    "anthropic_block": block  # Preserve original for tool_result linking
                })
        
        return text_content, tool_calls

    def format_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        formatted_tool_calls = []
        for tool_call in tool_calls:
            anthropic_block = tool_call.get("anthropic_block")
            if anthropic_block:
                formatted_tool_calls.append(anthropic_block)
        
        return formatted_tool_calls
                
    
    def format_tool_results(self, tool_calls: List[Dict[str, Any]], 
                           tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format tool results for Anthropic API"""
        anthropic_tool_results = []
        
        for i, tool_result in enumerate(tool_results):
            tool_call = tool_calls[i]
            anthropic_block = tool_call.get("anthropic_block", {})
            tool_use_id = anthropic_block.get("id", tool_call.get("id", f"tool_{i}"))
            
            # Extract content from tool result
            if tool_result.get("success"):
                result_data = tool_result.get("result", "")
                
                # Handle MCP CallToolResult objects
                if hasattr(result_data, 'content') and result_data.content:
                    if hasattr(result_data.content[0], 'text'):
                        tool_content = result_data.content[0].text
                    else:
                        tool_content = str(result_data.content[0])
                else:
                    tool_content = result_data
                    
                if not isinstance(tool_content, str):
                    tool_content = json.dumps(tool_content, default=str)
            else:
                tool_content = f"Error: {tool_result.get('error', 'Unknown error')}"
            
            anthropic_tool_results.append({
                "tool_use_id": tool_use_id,
                "type": "tool_result",
                "content": [
                    {
                        "type": "text",
                        "text": tool_content
                    }
                ]
            })
        
        return {
            "role": "user",
            "content": anthropic_tool_results
        }
    
    def get_processed_system_data(self, enable_caching: bool = True) -> List[Dict[str, Any]]:
        """Get system prompt processed for Anthropic with caching control"""
        cache_key = f"system_{enable_caching}"
        
        if cache_key not in self._processed_system_cache:
            if not self._raw_system_prompt:
                return []
                
            system_data = [
                {
                    "type": "text",
                    "text": self._raw_system_prompt
                }
            ]
            
            # Add cache control only if caching is enabled
            if enable_caching and self.supports_caching():
                system_data[0]["cache_control"] = {
                    "type": "ephemeral",
                    "ttl": "1h"
                }
            
            self._processed_system_cache[cache_key] = system_data
            
        return self._processed_system_cache[cache_key]
    
    def get_processed_tools(self, enable_caching: bool = True) -> List[Dict[str, Any]]:
        """Get tools processed for Anthropic with caching control"""
        if not self._raw_tools:
            return []
            
        cache_key = f"tools_{enable_caching}_{len(self._raw_tools)}"
        
        if cache_key not in self._processed_tools_cache:
            anthropic_tools = []
            for i, tool in enumerate(self._raw_tools):
                anthropic_tool = {
                    "name": tool["function"]["name"],
                    "description": tool["function"]["description"],
                    "input_schema": tool["function"]["parameters"]
                }
                
                # Add cache control to the last tool only if caching is enabled
                if enable_caching and self.supports_caching() and i == len(self._raw_tools) - 1:
                    anthropic_tool["cache_control"] = {
                        "type": "ephemeral",
                        "ttl": "1h"
                    }
                
                anthropic_tools.append(anthropic_tool)
            
            self._processed_tools_cache[cache_key] = anthropic_tools
            
        return self._processed_tools_cache[cache_key]