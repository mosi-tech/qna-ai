"""
OpenAI API provider implementation
"""

import json
import logging
import httpx
from typing import Dict, Any, List, Tuple, Optional

from .base import LLMProvider

logger = logging.getLogger("openai-provider")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: str, default_model: str = "gpt-4-turbo-preview", base_url: str = None):
        if base_url is None:
            base_url = "https://api.openai.com/v1"
        super().__init__(api_key, base_url, default_model)
    
    def supports_caching(self) -> bool:
        return False  # OpenAI doesn't support explicit caching like Anthropic
    
    async def call_api(self, model: str, messages: List[Dict[str, Any]], 
                      max_tokens: int = 4000, enable_caching: bool = False,
                      override_system_prompt: Optional[str] = None,
                      override_tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Make OpenAI API call using stored system prompt and tools"""
        
        # Use overrides if provided, otherwise use stored data
        if override_system_prompt is not None:
            self.set_system_prompt(override_system_prompt)
        if override_tools is not None:
            self.set_tools(override_tools)
        
        # Get processed system data and tools
        processed_system = self.get_processed_system_data(enable_caching)
        processed_tools = self.get_processed_tools(enable_caching) if self._raw_tools else None
        
        # Include system message in messages array (OpenAI format)
        openai_messages = [{"role": "system", "content": processed_system}]
        openai_messages.extend(messages)
        
        request_data = {
            "model": model,
            "messages": openai_messages,
            "max_tokens": max_tokens
        }
        
        # Add processed tools if provided
        if processed_tools:
            request_data["tools"] = processed_tools
            request_data["tool_choice"] = "auto"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Make API call
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=request_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "provider": "openai"
                }
            else:
                return {
                    "success": False,
                    "error": f"OpenAI API error: {response.status_code} - {response.text}",
                    "provider": "openai"
                }
    
    def parse_response(self, response_data: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse OpenAI response format"""
        message = response_data.get("choices", [{}])[0].get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        # Convert OpenAI tool calls to our internal format
        formatted_tool_calls = []
        for tool_call in tool_calls:
            formatted_tool_calls.append({
                "function": {
                    "name": tool_call["function"]["name"],
                    "arguments": json.loads(tool_call["function"]["arguments"]) if isinstance(tool_call["function"]["arguments"], str) else tool_call["function"]["arguments"]
                },
                "id": tool_call["id"],
                "openai_tool_call": tool_call  # Preserve original
            })
        
        return content, formatted_tool_calls
    
    def format_tool_results(self, tool_calls: List[Dict[str, Any]], 
                           tool_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format tool results for OpenAI API"""
        messages = []
        
        # Add assistant message with tool calls
        assistant_message = {
            "role": "assistant",
            "content": None,
            "tool_calls": [tc.get("openai_tool_call") for tc in tool_calls]
        }
        messages.append(assistant_message)
        
        # Add tool result messages
        for i, tool_result in enumerate(tool_results):
            tool_call = tool_calls[i]
            tool_call_id = tool_call.get("id")
            
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
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_content
            })
        
        return messages
    
    def get_processed_system_data(self, enable_caching: bool = True) -> str:
        """Get system prompt processed for OpenAI (just returns raw prompt)"""
        return self._raw_system_prompt or ""
    
    def get_processed_tools(self, enable_caching: bool = True) -> List[Dict[str, Any]]:
        """Get tools processed for OpenAI (returns tools as-is since already in OpenAI format)"""
        return self._raw_tools or []