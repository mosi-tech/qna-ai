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
    
    def _parse_tool_arguments(self, arguments_str: str) -> Dict[str, Any]:
        """Robustly parse tool call arguments that may have malformed JSON"""
        try:
            # First try: standard JSON parsing
            return json.loads(arguments_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parsing failed: {e}")
            
            try:
                # Second try: fix common escaping issues
                # Remove extra backslashes before quotes
                fixed_str = arguments_str.replace('\\"', '"')
                # Fix unicode escapes
                fixed_str = fixed_str.replace('\\u003e', '>')
                fixed_str = fixed_str.replace('\\u003c', '<')
                return json.loads(fixed_str)
            except json.JSONDecodeError:
                logger.warning("Escape fixing failed, trying manual parsing")
                
                try:
                    # Third try: extract just the core fields manually
                    result = {}
                    
                    # Look for filename field
                    import re
                    filename_match = re.search(r'"filename"\s*:\s*"([^"]+)"', arguments_str)
                    if filename_match:
                        result["filename"] = filename_match.group(1)
                    
                    # Look for content field (more complex due to multiline)
                    content_match = re.search(r'"content"\s*:\s*"(.*?)"(?=\s*[,}])', arguments_str, re.DOTALL)
                    if content_match:
                        content = content_match.group(1)
                        # Unescape content
                        content = content.replace('\\"', '"')
                        content = content.replace('\\n', '\n')
                        content = content.replace('\\\\', '\\')
                        result["content"] = content
                    
                    if result:
                        logger.info(f"Manual parsing extracted: {list(result.keys())}")
                        return result
                    else:
                        logger.error("Manual parsing failed to extract any fields")
                        return {}
                        
                except Exception as e:
                    logger.error(f"Manual parsing failed: {e}")
                    return {}
    
    def _parse_tool_calls_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse tool calls that are embedded in content as text"""
        import re
        import uuid
        
        tool_calls = []
        
        # Pattern 1: <tool_call> blocks with JSON
        tool_call_pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
        matches = re.findall(tool_call_pattern, content, re.DOTALL)
        
        for i, match in enumerate(matches):
            try:
                # Parse the JSON content
                tool_data = json.loads(match.strip())
                
                # Extract name and arguments
                name = tool_data.get("name", "")
                arguments = tool_data.get("arguments", {})
                
                # Create a tool call in our internal format
                tool_call = {
                    "function": {
                        "name": name,
                        "arguments": arguments
                    },
                    "id": f"call_{uuid.uuid4().hex[:8]}",  # Generate a unique ID
                    "openai_tool_call": {
                        "id": f"call_{uuid.uuid4().hex[:8]}",
                        "type": "function", 
                        "function": {
                            "name": name,
                            "arguments": json.dumps(arguments) if isinstance(arguments, dict) else arguments
                        }
                    }
                }
                
                tool_calls.append(tool_call)
                logger.info(f"Parsed tool call from content: {name}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool call JSON from content: {e}")
                logger.error(f"Raw content: {match}")
                continue
            except Exception as e:
                logger.error(f"Error parsing tool call from content: {e}")
                continue
        
        # Pattern 2: Look for inline JSON with "name" field (fallback)
        if not tool_calls:
            json_pattern = r'\{"name":\s*"([^"]+)"[^}]*\}'
            json_matches = re.findall(json_pattern, content)
            
            for name in json_matches:
                if name:  # Basic validation
                    tool_call = {
                        "function": {
                            "name": name,
                            "arguments": {}
                        },
                        "id": f"call_{uuid.uuid4().hex[:8]}",
                        "openai_tool_call": {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "type": "function",
                            "function": {
                                "name": name,
                                "arguments": "{}"
                            }
                        }
                    }
                    tool_calls.append(tool_call)
                    logger.info(f"Parsed basic tool call from content: {name}")
        
        return tool_calls
    
    async def call_api(self, model: str, messages: List[Dict[str, Any]], 
                      max_tokens: int = 4000, enable_caching: bool = False,
                      override_system_prompt: Optional[str] = None,
                      override_tools: Optional[List[Dict[str, Any]]] = None, force_api: bool = True) -> Dict[str, Any]:
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
            "max_tokens": max_tokens,
            "response_format": { "type": "json_object" }
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
        
        # Check if tool calls are embedded in content as text and add them to tool_calls
        if content and "<tool_call>" in content:
            logger.info("Found tool calls embedded in content field")
            content_tool_calls = self._parse_tool_calls_from_content(content)
            # Convert to OpenAI format and add to tool_calls list
            for content_tool_call in content_tool_calls:
                tool_calls.append(content_tool_call["openai_tool_call"])
        
        # Convert all OpenAI tool calls to our internal format
        formatted_tool_calls = []
        for tool_call in tool_calls:
            try:
                # Handle tool call arguments parsing more robustly
                arguments = tool_call["function"]["arguments"]
                
                if isinstance(arguments, str):
                    # Try multiple parsing strategies for malformed JSON
                    parsed_arguments = self._parse_tool_arguments(arguments)
                else:
                    parsed_arguments = arguments
                
                formatted_tool_calls.append({
                    "function": {
                        "name": tool_call["function"]["name"],
                        "arguments": parsed_arguments
                    },
                    "id": tool_call["id"],
                    "openai_tool_call": tool_call  # Preserve original
                })
            except Exception as e:
                logger.error(f"Failed to parse tool call {tool_call.get('id', 'unknown')}: {e}")
                # Skip malformed tool calls rather than failing entirely
                continue
        
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
    
    def contains_tool_calls(self, message: Any) -> bool:
        """Check if OpenAI message contains tool calls"""
        if not message:
            return False
        
        content = message
        if isinstance(message, dict) and "content" in message:
            content = message["content"]
        
        if isinstance(content, str):
            return "tool_calls" in str(content)
        elif isinstance(content, dict):
            return "tool_calls" in content or "type" in content and content.get("type") == "function"
        
        return False
    
    def get_message_text_length(self, message: Dict[str, Any]) -> int:
        """Get text length from OpenAI message (content is always a string)"""
        content = message.get("content", "")
        return len(content) if isinstance(content, str) else 0
    
    def get_tool_result_role(self) -> str:
        """OpenAI uses 'tool' role for tool result messages"""
        return "tool"
    
    def message_contains_function(self, message: Any, function_name: str) -> bool:
        """Check if OpenAI message contains a specific function call"""
        if not message:
            return False
        return function_name in str(message)
    
    def contains_tool_results(self, message: Any) -> bool:
        """Check if OpenAI message contains tool results"""
        if not message:
            return False
        
        if isinstance(message, dict) and message.get("role") == "tool":
            return True
        
        return "tool_result" in str(message)
    
    def get_processed_system_data(self, enable_caching: bool = True) -> str:
        """Get system prompt processed for OpenAI (just returns raw prompt)"""
        return self._raw_system_prompt or ""
    
    def get_processed_tools(self, enable_caching: bool = True) -> List[Dict[str, Any]]:
        """Get tools processed for OpenAI (returns tools as-is since already in OpenAI format)"""
        return self._raw_tools or []
    
    def create_simulated_tool_call(self, function_name: str, arguments: Dict[str, Any], call_id: str = None) -> Dict[str, Any]:
        """Create a simulated tool call in OpenAI's format"""
        import uuid
        if call_id is None:
            call_id = f"call_{str(uuid.uuid4())[:8]}"
        
        return {
            "id": call_id,
            "type": "function",
            "function": {
                "name": function_name,
                "arguments": arguments  # Keep as dict for Ollama compatibility
            }
        }
    
    def format_assistant_message_with_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format complete assistant message with tool calls for OpenAI"""
        return {
            "role": "assistant",
            "content": "",  # OpenAI expects empty string content when using tool_calls
            "tool_calls": tool_calls
        }
    
    def create_simulated_assistant_message_with_tool_calls(self, content: str, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a simulated assistant message with tool calls in OpenAI's format"""
        message = {
            "role": "assistant",
            "tool_calls": tool_calls
        }
        
        if content:
            message["content"] = content
        
        return message
    
    def create_simulated_tool_result(self, tool_call_id: str, content: str) -> Dict[str, Any]:
        """Create a simulated tool result message in OpenAI's format"""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        }