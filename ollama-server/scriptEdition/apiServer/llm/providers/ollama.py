"""
Ollama API provider implementation
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional
import ollama
import requests

from .base import LLMProvider

logger = logging.getLogger("ollama-provider")


class OllamaProvider(LLMProvider):
    """Ollama API provider - supports both local and cloud endpoints"""
    
    def __init__(self, api_key: str = "", default_model: str = "qwen3:0.6b", base_url: str = "http://localhost:11434"):
        super().__init__(api_key, base_url, default_model)
        
        if ollama is None:
            raise ImportError("ollama library not installed. Install with: pip install ollama")
        
        # Determine if this is Ollama Cloud or local
        self.is_cloud = "ollama.com" in base_url or api_key != ""
        
        if self.is_cloud:
            # For Ollama Cloud, we'll use direct HTTP requests with API key
            self.client = None
            self.cloud_endpoint = base_url if base_url.startswith("http") else "https://ollama.com/api"
            if not self.api_key:
                logger.warning("Ollama Cloud requires API key but none provided")
        else:
            # For local Ollama, use the ollama client library
            self.client = ollama.Client(host=base_url)
            self.cloud_endpoint = None
        
    def supports_caching(self) -> bool:
        return False  # Ollama doesn't support explicit caching like Anthropic
    
    async def call_api(self, model: str, messages: List[Dict[str, Any]], 
                      max_tokens: int = 4000, enable_caching: bool = False,
                      override_system_prompt: Optional[str] = None,
                      override_tools: Optional[List[Dict[str, Any]]] = None, 
                      force_api: bool = True) -> Dict[str, Any]:
        """Make Ollama API call using stored system prompt and tools"""
        
        # Use overrides if provided, otherwise use stored data
        if override_system_prompt is not None:
            self.set_system_prompt(override_system_prompt)
        if override_tools is not None:
            self.set_tools(override_tools)
        
        # Get processed system data and tools
        processed_system = self.get_processed_system_data(enable_caching)
        processed_tools = self.get_processed_tools(enable_caching) if self._raw_tools else None
        
        # Format messages for Ollama (system message should be first)
        ollama_messages = []
        if processed_system:
            ollama_messages.append({"role": "system", "content": processed_system})
        ollama_messages.extend(messages)
        
        if self.is_cloud:
            return await self._call_cloud_api(model, ollama_messages, max_tokens, processed_tools)
        else:
            return await self._call_local_api(model, ollama_messages, max_tokens, processed_tools)
    
    async def _call_local_api(self, model: str, messages: List[Dict[str, Any]], 
                             max_tokens: int, tools: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Make API call to local Ollama instance"""
        
        # Prepare request options
        options = {
            "num_predict": max_tokens,
            "temperature": 0.7,
        }
        
        request_data = {
            "model": model,
            "messages": messages,
            "options": options,
            "stream": False,
            "format": "json"  # Request JSON format for structured output
        }
        
        # Add tools if available (Ollama has experimental tool support)
        if tools:
            request_data["tools"] = tools
        
        try:
            # Make API call using ollama library
            response = self.client.chat(**request_data)
            
            return {
                "success": True,
                "data": response,
                "provider": "ollama"
            }
            
        except Exception as e:
            logger.error(f"Ollama local API error: {e}")
            return {
                "success": False,
                "error": f"Ollama local API error: {str(e)}",
                "provider": "ollama"
            }
    
    async def _call_cloud_api(self, model: str, messages: List[Dict[str, Any]], 
                             max_tokens: int, tools: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Make API call to Ollama Cloud"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        # Add tools if available
        if tools:
            request_data["tools"] = tools
        
        try:
            # Make HTTP request to Ollama Cloud
            # The endpoint should be /api/chat, but cloud_endpoint already includes /api
            if self.cloud_endpoint.endswith('/api'):
                url = f"{self.cloud_endpoint}/chat"
            else:
                url = f"{self.cloud_endpoint}/api/chat"
            
            logger.info(f"🌐 Making request to: {url}")
            logger.debug(f"🔑 Headers: {headers}")
            logger.debug(f"📦 Request data: {request_data}")
            
            response = requests.post(url, headers=headers, json=request_data, timeout=60)
            response.raise_for_status()
            
            response_data = response.json()
            
            return {
                "success": True,
                "data": response_data,
                "provider": "ollama-cloud"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama Cloud API error: {e}")
            return {
                "success": False,
                "error": f"Ollama Cloud API error: {str(e)}",
                "provider": "ollama-cloud"
            }
        except Exception as e:
            logger.error(f"Ollama Cloud error: {e}")
            return {
                "success": False,
                "error": f"Ollama Cloud error: {str(e)}",
                "provider": "ollama-cloud"
            }
    
    def parse_response(self, response_data: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse Ollama response format"""
        message = response_data.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        # Format tool calls to our internal format
        formatted_tool_calls = []
        for tool_call in tool_calls:
            try:
                formatted_tool_calls.append({
                    "function": {
                        "name": tool_call["function"]["name"],
                        "arguments": tool_call["function"]["arguments"]
                    },
                    "id": tool_call.get("id", f"call_{len(formatted_tool_calls)}"),
                    "ollama_tool_call": tool_call  # Preserve original
                })
            except (KeyError, TypeError) as e:
                logger.error(f"Failed to parse tool call: {e}")
                continue
        
        return content, formatted_tool_calls
    
    def format_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format tool calls for Ollama API"""
        formatted_tool_calls = []
        for tool_call in tool_calls:
            ollama_tool_call = tool_call.get("ollama_tool_call")
            if ollama_tool_call:
                formatted_tool_calls.append(ollama_tool_call)
            else:
                # Fallback to the original tool call format
                formatted_tool_calls.append(tool_call)
        
        return formatted_tool_calls
    
    def format_assistant_message_with_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format assistant message with tool calls for Ollama"""
        return {
            "role": "assistant",
            "content": "",  # Ollama expects string content, tool calls are separate
            "tool_calls": self.format_tool_calls(tool_calls)
        }
    
    def contains_tool_calls(self, message: Any) -> bool:
        """Check if message contains Ollama tool calls
        
        For Ollama, tool calls are in a separate 'tool_calls' field at the message level,
        not embedded in the content like Anthropic.
        """
        if not message:
            return False
        
        # Handle different message formats for Ollama
        if isinstance(message, dict):
            # Check for Ollama message structure: {"role": "assistant", "content": "...", "tool_calls": [...]}
            if "tool_calls" in message and message.get("tool_calls"):
                return True
            
            # Check if this is formatted content from provider (list of tool calls)
            if isinstance(message.get("content"), list):
                for item in message["content"]:
                    if isinstance(item, dict) and item.get("function"):
                        return True
            
            # Fallback: check if this looks like a formatted tool call object itself
            if message.get("function") and "name" in message.get("function", {}):
                return True
                
        elif isinstance(message, list):
            # Content is a list of formatted tool calls
            for item in message:
                if isinstance(item, dict) and item.get("function"):
                    return True
                    
        elif isinstance(message, str):
            # String representation - check for Ollama tool indicators
            tool_indicators = ["tool_calls", '"function":', '"arguments":', "mcp__"]
            return any(indicator in message for indicator in tool_indicators)
        
        return False
    
    def get_tool_result_role(self) -> str:
        """Ollama uses 'tool' role for tool result messages"""
        return "tool"
    
    def message_contains_function(self, message: Any, function_name: str) -> bool:
        """Check if Ollama message contains a specific function call"""
        if not message:
            return False
        
        # Handle different message formats for Ollama
        if isinstance(message, dict):
            # Check tool_calls field in message
            tool_calls = message.get("tool_calls", [])
            for tool_call in tool_calls:
                if isinstance(tool_call, dict):
                    func_info = tool_call.get("function", {})
                    tool_name = func_info.get("name", "")
                    if function_name in tool_name:
                        return True
            
            # Check if message content contains formatted tool calls
            content = message.get("content", "")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("function"):
                        tool_name = item["function"].get("name", "")
                        if function_name in tool_name:
                            return True
            elif isinstance(content, str):
                return function_name in content
                
        elif isinstance(message, list):
            # Content is a list of formatted tool calls
            for item in message:
                if isinstance(item, dict) and item.get("function"):
                    tool_name = item["function"].get("name", "")
                    if function_name in tool_name:
                        return True
                        
        elif isinstance(message, str):
            # String representation
            return function_name in message
        
        return False
    
    def contains_tool_results(self, message: Any) -> bool:
        """Check if Ollama message contains tool results"""
        if not message:
            return False
        
        # Handle different message formats for Ollama tool results
        if isinstance(message, dict):
            # Check for Ollama tool result indicators
            if "tool_call_id" in message:
                return True
            
            # Check content for tool results
            content = message.get("content", "")
            if isinstance(content, str):
                # Look for JSON-like structures with success, validation_result, etc.
                ollama_indicators = ["tool_call_id", "success", "validation_result", "write_result"]
                return any(indicator in content for indicator in ollama_indicators)
            elif isinstance(content, list):
                # Content might be a list of tool result blocks
                for item in content:
                    if isinstance(item, dict) and "tool_call_id" in item:
                        return True
                        
        elif isinstance(message, str):
            # String representation - check for Ollama tool result indicators
            ollama_indicators = ["tool_call_id", '"success":', '"validation_result":', '"write_result":']
            return any(indicator in message for indicator in ollama_indicators)
        
        return False
    
    def format_tool_results(self, tool_calls: List[Dict[str, Any]], 
                           tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format tool results for Ollama API
        
        Note: Ollama follows OpenAI format where each tool result is a separate message.
        However, to maintain consistency with the analysis service that expects a single
        message dict, we return the first tool result as the primary message.
        """
        if not tool_results or not tool_calls:
            return {"role": "tool", "content": "No tool results"}
        
        # Take the first tool result for the primary response
        tool_result = tool_results[0]
        tool_call = tool_calls[0]
        tool_call_id = tool_call.get("id", "call_0")
        
        # Extract content from tool result
        if tool_result.get("success"):
            result_data = tool_result.get("result", "")
            
            # Handle MCP CallToolResult objects - convert to string
            if hasattr(result_data, 'content') and result_data.content:
                if hasattr(result_data.content[0], 'text'):
                    tool_content = result_data.content[0].text
                else:
                    tool_content = str(result_data.content[0])
            else:
                tool_content = str(result_data) if result_data is not None else ""
                
            # Ensure tool_content is a string for JSON serialization
            if not isinstance(tool_content, str):
                tool_content = json.dumps(tool_content, default=str)
        else:
            tool_content = f"Error: {tool_result.get('error', 'Unknown error')}"
        
        # Return standard Ollama/OpenAI tool result format
        return {
            "role": "tool",
            "content": tool_content,
            "tool_call_id": tool_call_id
        }
    
    def get_processed_system_data(self, enable_caching: bool = True) -> str:
        """Get system prompt processed for Ollama (just returns raw prompt)"""
        return self._raw_system_prompt or ""
    
    def get_processed_tools(self, enable_caching: bool = True) -> List[Dict[str, Any]]:
        """Get tools processed for Ollama format"""
        if not self._raw_tools:
            logger.debug("🔧 Ollama provider: No raw tools available")
            return []
        
        logger.debug(f"🔧 Ollama provider: Processing {len(self._raw_tools)} raw tools")
        
        # Convert from OpenAI/Anthropic format to Ollama format if needed
        # Ollama tool format is similar to OpenAI
        ollama_tools = []
        for i, tool in enumerate(self._raw_tools):
            try:
                if "function" in tool:
                    ollama_tool = {
                        "type": "function",
                        "function": {
                            "name": tool["function"]["name"],
                            "description": tool["function"].get("description", ""),
                            "parameters": tool["function"].get("parameters", {})
                        }
                    }
                    ollama_tools.append(ollama_tool)
                    logger.debug(f"   Tool {i+1}: {tool['function']['name']}")
                else:
                    # If already in correct format
                    ollama_tools.append(tool)
                    logger.debug(f"   Tool {i+1}: {tool.get('name', 'unknown')} (pre-formatted)")
                    
            except Exception as e:
                logger.error(f"❌ Failed to process tool {i+1}: {e}")
                continue
        
        logger.debug(f"🔧 Ollama provider: Processed {len(ollama_tools)} tools successfully")
        return ollama_tools
    
    def set_tools(self, tools: List[Dict[str, Any]]):
        """Set and cache tools with debugging for Ollama"""
        logger.info(f"🔧 Ollama provider: Setting {len(tools) if tools else 0} tools")
        
        if tools:
            for i, tool in enumerate(tools[:3]):  # Log first 3 tools
                tool_name = tool.get('function', {}).get('name', 'unknown')
                logger.info(f"   Tool {i+1}: {tool_name}")
        
        # Call parent implementation
        super().set_tools(tools)