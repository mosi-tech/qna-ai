"""
Core LLM Service for Anthropic and Ollama Integration
"""

import json
import logging
import os
import httpx
import anthropic
from datetime import datetime
from typing import Dict, Any, Optional, List

from cache_manager import CacheManager
from mcp_integration import MCPIntegration

logger = logging.getLogger("llm-service")


class UniversalLLMToolCallService:
    """Universal LLM service supporting both Anthropic and Ollama with MCP integration"""
    
    def __init__(self):
        # Use path to system prompt file in the same directory
        self.system_prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system-prompt.txt")
        self.system_prompt = None  # Cache for system prompt
        self.conversation_messages = []  # Store conversation history
        
        # Initialize components
        self.mcp_integration = MCPIntegration()
        
        # Determine which LLM provider to use
        self.llm_provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        
        if self.llm_provider == "anthropic":
            self.base_url = "https://api.anthropic.com/v1"
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            self.default_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
            if not self.api_key:
                logger.warning("ANTHROPIC_API_KEY environment variable not set")
            
            # Initialize cache manager for Anthropic
            if self.api_key:
                self.cache_manager = CacheManager(self.api_key, self.base_url)
            else:
                self.cache_manager = None
                
        elif self.llm_provider == "ollama":
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.api_key = None  # Ollama doesn't need API key
            self.default_model = os.getenv("OLLAMA_MODEL", "llama3.2")
            self.cache_manager = None  # Ollama doesn't support caching
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.llm_provider}. Use 'anthropic' or 'ollama'")
            
        logger.info(f"🤖 Initialized {self.llm_provider.upper()} LLM service")
    
    @property
    def mcp_client(self):
        """Access to MCP client through integration"""
        return self.mcp_integration.mcp_client
    
    @property
    def mcp_initialized(self):
        """Check if MCP is initialized"""
        return self.mcp_integration.mcp_initialized
    
    async def load_system_prompt(self) -> str:
        """Load the base system prompt from file"""
        try:
            logger.debug(f"Loading system prompt from: {self.system_prompt_path}")
            with open(self.system_prompt_path, 'r') as f:
                content = f.read().strip()
                logger.debug(f"System prompt loaded successfully ({len(content)} characters)")
                return content
        except Exception as e:
            logger.error(f"Failed to load system prompt from {self.system_prompt_path}: {e}")
            return "You are a helpful financial analysis assistant that generates tool calls for financial data analysis."
    
    async def get_system_prompt(self) -> str:
        """Get system prompt (cached separately from tools for Anthropic)"""
        if self.system_prompt:
            return self.system_prompt
            
        # Load base system prompt - keep it separate from tools for caching
        self.system_prompt = await self.load_system_prompt()
        return self.system_prompt
    
    async def ensure_mcp_initialized(self) -> bool:
        """Ensure MCP client is initialized"""
        return await self.mcp_integration.ensure_mcp_initialized()
    
    async def initialize_conversation(self, model: str) -> None:
        """Initialize conversation with system prompt (called once)"""
        if not self.conversation_messages:
            system_prompt = await self.get_system_prompt()
            self.conversation_messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]
            logger.info(f"Initialized conversation with system prompt ({len(system_prompt)} characters)")
    
    async def warm_anthropic_cache(self, model: str) -> bool:
        """Warm Anthropic prompt cache if available"""
        if not self.cache_manager:
            return False
        
        system_prompt = await self.get_system_prompt()
        mcp_tools = self.get_mcp_tools_for_openai()
        
        return await self.cache_manager.warm_anthropic_cache(model, system_prompt, mcp_tools)
    
    def get_mcp_tools_for_openai(self) -> List[Dict[str, Any]]:
        """Get MCP tools in OpenAI format"""
        return self.mcp_integration.get_mcp_tools_for_openai()
    
    async def call_llm_chat_with_tools(self, model: str, user_message: str) -> Dict[str, Any]:
        """Call LLM (Anthropic or Ollama) via OpenAI-compatible API with multi-level tool calling support"""
        try:
            # Use provider default model if none specified
            if not model:
                model = self.default_model
                
            # Validate API key for Anthropic
            if self.llm_provider == "anthropic" and not self.api_key:
                raise Exception("ANTHROPIC_API_KEY not set in environment")
                
            # Initialize conversation if needed (system prompt set once)
            await self.initialize_conversation(model)
            
            # Get MCP tools in OpenAI format
            mcp_tools = self.get_mcp_tools_for_openai()
            logger.info(f"🔧 Available MCP tools for LLM: {len(mcp_tools)} tools")
            logger.info(f"🔧 LLM Provider: {self.llm_provider}")
            logger.info(f"🔧 Tools will be sent to LLM: {'Yes' if mcp_tools else 'No'}")
            
            if mcp_tools:
                logger.info(f"🔧 Sample tool names: {[tool['function']['name'] for tool in mcp_tools[:5]]}")
                if self.llm_provider == "anthropic":
                    logger.info(f"🔧 Anthropic tool format will be used")
                else:
                    logger.info(f"🔧 OpenAI-compatible tool format will be used")
            
            # Prepare the user message
            user_msg = {
                "role": "user", 
                "content": user_message
            }
            
            # Call the appropriate LLM provider
            if self.llm_provider == "anthropic":
                return await self._call_anthropic_with_tools(model, user_msg, mcp_tools)
            else:
                return await self._call_ollama_with_tools(model, user_msg, mcp_tools)
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.llm_provider
            }
    
    async def _call_anthropic_with_tools(self, model: str, user_msg: Dict[str, Any], mcp_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call Anthropic API with tools"""
        try:
            # Get system prompt for Anthropic
            system_prompt = await self.get_system_prompt()
            
            # Prepare messages (Anthropic doesn't include system in messages array)
            messages = [user_msg]
            
            # Prepare request data
            request_data = {
                "model": model,
                "system": [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {
                            "type": "ephemeral",
                            "ttl": "1h"
                        }
                    }
                ],
                "messages": messages,
                "max_tokens": 4000
            }
            
            # Add tools if available
            if mcp_tools:
                anthropic_tools = []
                for i, tool in enumerate(mcp_tools):
                    anthropic_tool = {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    }
                    
                    # Add cache control to the last tool
                    if i == len(mcp_tools) - 1:
                        anthropic_tool["cache_control"] = {
                            "type": "ephemeral",
                            "ttl": "1h"
                        }
                    
                    anthropic_tools.append(anthropic_tool)
                
                request_data["tools"] = anthropic_tools
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            if mcp_tools:
                headers["anthropic-beta"] = "tools-2024-05-16"
            
            # Make the API call
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=request_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Check if LLM wants to call tools
                    if response_data.get("content"):
                        tool_calls = []
                        text_content = ""
                        
                        for content_block in response_data["content"]:
                            if content_block.get("type") == "tool_use":
                                tool_calls.append({
                                    "function": {
                                        "name": content_block.get("name"),
                                        "arguments": content_block.get("input", {})
                                    },
                                    "anthropic_block": content_block  # Store the entire block to preserve ID
                                })
                            elif content_block.get("type") == "text":
                                text_content += content_block.get("text", "")
                        
                        if tool_calls:
                            # Validate tool calls
                            validation = self.mcp_integration.validate_mcp_functions(tool_calls)
                            if not validation["all_valid"]:
                                return {
                                    "success": False,
                                    "error": "Forbidden tool calls detected",
                                    "validation": validation,
                                    "provider": "anthropic"
                                }
                            
                            # Execute tool calls
                            tool_results = await self.mcp_integration.generate_tool_calls_only(tool_calls)
                            
                            # Create assistant message like original (preserve raw content)
                            assistant_message = {"role": "assistant", "content": response_data["content"]}
                            
                            # Continue conversation with tool results
                            return await self._continue_conversation_with_tools(
                                model, messages, assistant_message, tool_calls, tool_results["tool_results"]
                            )
                        else:
                            return {
                                "success": True,
                                "content": text_content,
                                "provider": "anthropic",
                                "usage": response_data.get("usage", {})
                            }
                    else:
                        return {
                            "success": False,
                            "error": "No content in response",
                            "provider": "anthropic"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Anthropic API error: {response.status_code} - {response.text}",
                        "provider": "anthropic"
                    }
                    
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "anthropic"
            }
    
    async def _call_ollama_with_tools(self, model: str, user_msg: Dict[str, Any], mcp_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call Ollama API with tools"""
        try:
            # Get system prompt
            system_prompt = await self.get_system_prompt()
            
            # Prepare messages (include system message for Ollama)
            messages = [
                {"role": "system", "content": system_prompt},
                user_msg
            ]
            
            # Prepare request data
            request_data = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            # Add tools if available
            if mcp_tools:
                request_data["tools"] = mcp_tools
            
            # Make the API call
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=request_data
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    message = response_data.get("choices", [{}])[0].get("message", {})
                    
                    # Check if LLM wants to call tools
                    tool_calls = message.get("tool_calls", [])
                    content = message.get("content", "")
                    
                    if tool_calls:
                        # Validate tool calls
                        validation = self.mcp_integration.validate_mcp_functions(tool_calls)
                        if not validation["all_valid"]:
                            return {
                                "success": False,
                                "error": "Forbidden tool calls detected",
                                "validation": validation,
                                "provider": "ollama"
                            }
                        
                        # Execute tool calls
                        tool_results = await self.mcp_integration.generate_tool_calls_only(tool_calls)
                        
                        return {
                            "success": True,
                            "content": content,
                            "tool_calls": tool_calls,
                            "tool_results": tool_results["tool_results"],
                            "provider": "ollama",
                            "usage": response_data.get("usage", {})
                        }
                    else:
                        return {
                            "success": True,
                            "content": content,
                            "provider": "ollama",
                            "usage": response_data.get("usage", {})
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Ollama API error: {response.status_code} - {response.text}",
                        "provider": "ollama"
                    }
                    
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "ollama"
            }
    
    async def call_llm_chat(self, model: str, user_message: str) -> str:
        """Simple chat call without tools"""
        result = await self.call_llm_chat_with_tools(model, user_message)
        return result.get("content", "") if result.get("success") else f"Error: {result.get('error')}"
    
    async def analyze_question(self, question: str, model: str = None) -> Dict[str, Any]:
        """Main entry point for question analysis"""
        try:
            if not model:
                model = self.default_model
            
            logger.info(f"🤔 Analyzing question with {self.llm_provider.upper()}: {question[:100]}...")
            
            # Ensure MCP is initialized
            await self.ensure_mcp_initialized()
            
            # Call LLM with tools
            result = await self.call_llm_chat_with_tools(model, question)
            
            if result.get("success"):
                # Format the successful response
                response_data = {
                    "question": question,
                    "provider": result["provider"],
                    "model": model,
                    "content": result.get("content", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add tool information if tools were called
                if result.get("tool_calls"):
                    response_data["tool_calls"] = result["tool_calls"]
                    response_data["tool_results"] = result["tool_results"]
                
                # Add usage information if available
                if result.get("usage"):
                    response_data["usage"] = result["usage"]
                
                logger.info(f"✅ Question analyzed successfully using {result['provider']}")
                
                return {
                    "success": True,
                    "data": response_data
                }
            else:
                logger.error(f"❌ Question analysis failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "provider": result.get("provider", self.llm_provider)
                }
                
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _continue_conversation_with_tools(self, model: str, messages: List[Dict[str, Any]], 
                                              assistant_message: Dict[str, Any], tool_calls: List[Dict[str, Any]], 
                                              tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Continue conversation after tool execution to get final response"""
        try:
            system_prompt = await self.get_system_prompt()
            
            # Add assistant message in Anthropic format (like original)
            messages.append(assistant_message)
            
            # Create tool results in Anthropic format
            anthropic_tool_results = []
            for i, tool_result in enumerate(tool_results):
                tool_call = tool_calls[i]
                function_name = tool_call["function"]["name"]
                
                # Get tool_use_id from the stored anthropic_block (like original)
                anthropic_block = tool_call.get("anthropic_block", {})
                tool_use_id = anthropic_block.get("id", tool_call.get("id", f"tool_{i}"))
                
                # Extract actual content from MCP response (Issue 2 fix - match original pattern)
                if tool_result.get("success"):
                    result_data = tool_result.get("result", "")
                    
                    # Extract content from MCP CallToolResult if needed (like original lines 810-818)
                    if hasattr(result_data, 'content'):
                        # MCP CallToolResult object - extract the content
                        if hasattr(result_data.content[0], 'text'):
                            tool_content = result_data.content[0].text
                        else:
                            tool_content = str(result_data.content[0])
                    else:
                        # Already serializable data
                        tool_content = result_data
                        
                    # Convert to string if needed
                    if not isinstance(tool_content, str):
                        tool_content = json.dumps(tool_content, default=str)
                else:
                    tool_content = f"Error: {tool_result.get('error', 'Unknown error')}"
                
                # Create tool result with cache control for docstring responses
                tool_result_block = {
                    "tool_use_id": tool_use_id,
                    "type": "tool_result",
                    "content": [
                        {
                            "type": "text",
                            "text": tool_content
                        }
                    ]
                }
                
                # Add cache control for docstring tool responses
                # if "get_function_docstring" in function_name:
                #     tool_result_block["cache_control"] = {
                #         "type": "ephemeral",
                #         "ttl": "1h"
                #     }
                #     logger.debug(f"🔄 Added cache control to docstring response for {function_name}")
                
                anthropic_tool_results.append(tool_result_block)
            
            # Add tool results as user message
            messages.append({
                "role": "user",
                "content": anthropic_tool_results
            })
            
            logger.info(f"🔄 Continuing conversation with {len(anthropic_tool_results)} tool results")
            
            # Check if we're sending validation results (reduce tokens for efficiency)
            has_validation_results = False
            for tool_result in tool_results:
                if "validate_python_script" in tool_result.get("function", ""):
                    # Parse the actual validation result from content
                    if tool_result.get("success", False):
                        try:
                            import json
                            result_data = tool_result.get("result", "")
                            logger.debug(f"🔍 Parsing validation result: {repr(result_data)}")
                            
                            # Handle different data structures
                            if hasattr(result_data, 'content') and result_data.content:
                                # MCP CallToolResult object - extract the content
                                if hasattr(result_data.content[0], 'text'):
                                    json_str = result_data.content[0].text
                                else:
                                    json_str = str(result_data.content[0])
                            elif isinstance(result_data, str):
                                json_str = result_data
                            else:
                                json_str = str(result_data)
                            
                            logger.debug(f"🔍 JSON string to parse: {repr(json_str)}")
                            parsed_result = json.loads(json_str)
                            logger.debug(f"🔍 Parsed result: {parsed_result}")
                            
                            if parsed_result.get("valid", False):
                                has_validation_results = True
                                logger.info("✅ Found valid=true in validation result")
                                break
                        except Exception as e:
                            logger.warning(f"❌ Failed to parse validation result: {e}")
                            # If parsing fails, check success field as fallback
                            has_validation_results = tool_result.get("success", False)
            max_tokens = 5 if has_validation_results else 4000
            
            if has_validation_results:
                logger.info("🔧 Validation results detected - using max_tokens=5 for efficiency")
            
            # Get MCP tools for continuation call (like original - tools in every iteration)
            mcp_tools = self.get_mcp_tools_for_openai()
            
            # Make second API call to get final response with tools available
            request_data = {
                "model": model,
                "system": [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {
                            "type": "ephemeral",
                            "ttl": "1h"
                        }
                    }
                ],
                "messages": messages,
                "max_tokens": max_tokens
            }
            
            # Add tools like original (tools in every iteration)
            if mcp_tools:
                anthropic_tools = []
                for i, tool in enumerate(mcp_tools):
                    anthropic_tool = {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    }
                    
                    # Add cache control to the last tool
                    if i == len(mcp_tools) - 1:
                        anthropic_tool["cache_control"] = {
                            "type": "ephemeral",
                            "ttl": "1h"
                        }
                    
                    anthropic_tools.append(anthropic_tool)
                
                request_data["tools"] = anthropic_tools
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Add anthropic-beta header when tools are present (like original)
            if mcp_tools:
                headers["anthropic-beta"] = "tools-2024-05-16"
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=request_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    final_response = response.json()
                    
                    # Check if response contains more tool calls (like original)
                    response_content = final_response.get("content", [])
                    new_tool_calls = []
                    final_content = ""
                    
                    for content_block in response_content:
                        if content_block.get("type") == "text":
                            final_content += content_block.get("text", "")
                        elif content_block.get("type") == "tool_use":
                            # Convert to our format for further processing
                            new_tool_calls.append({
                                "function": {
                                    "name": content_block.get("name"),
                                    "arguments": content_block.get("input", {})
                                },
                                "anthropic_block": content_block
                            })
                    
                    if new_tool_calls:
                        # More tool calls requested - continue the loop like original
                        logger.info(f"🔄 LLM requested {len(new_tool_calls)} more tool calls, continuing...")
                        
                        # Validate and execute new tool calls
                        validation = self.mcp_integration.validate_mcp_functions(new_tool_calls)
                        if not validation["all_valid"]:
                            return {
                                "success": False,
                                "error": "Forbidden tool calls detected in continuation",
                                "validation": validation,
                                "provider": "anthropic"
                            }
                        
                        # Execute new tool calls
                        new_tool_results = await self.mcp_integration.generate_tool_calls_only(new_tool_calls)
                        
                        # Check if validation was completed successfully (like original lines 914-917)
                        validation_completed = False
                        for call, result in zip(new_tool_calls, new_tool_results["tool_results"]):
                            if "validate_python_script" in call["function"]["name"] and result.get("success", False):
                                try:
                                    import json
                                    result_data = result.get("result", "")
                                    
                                    # Handle different data structures
                                    if hasattr(result_data, 'content') and result_data.content:
                                        # MCP CallToolResult object - extract the content
                                        if hasattr(result_data.content[0], 'text'):
                                            json_str = result_data.content[0].text
                                        else:
                                            json_str = str(result_data.content[0])
                                    elif isinstance(result_data, str):
                                        json_str = result_data
                                    else:
                                        json_str = str(result_data)
                                    
                                    parsed_result = json.loads(json_str)
                                    if parsed_result.get("valid", False):
                                        validation_completed = True
                                        break
                                except Exception as e:
                                    logger.warning(f"❌ Failed to parse validation result in completion check: {e}")
                                    # If parsing fails, fall back to success field
                                    validation_completed = result.get("success", False)
                        
                        if validation_completed:
                            # Task completed with successful validation - stop here like original
                            logger.info("🏁 Task completed: Python script validation successful")
                            return {
                                "success": True,
                                "content": final_content,
                                "tool_calls": new_tool_calls,
                                "tool_results": new_tool_results["tool_results"],
                                "provider": "anthropic",
                                "task_completed": True,
                                "completion_reason": "validation_successful"
                            }
                        
                        # Recursively continue with new tool results (assistant message will be added in the recursive call)
                        return await self._continue_conversation_with_tools(
                            model, messages, {"role": "assistant", "content": response_content}, 
                            new_tool_calls, new_tool_results["tool_results"]
                        )
                    else:
                        # No more tool calls - this is the final response
                        logger.info("✅ Received final response from LLM after tool execution")
                        
                        return {
                            "success": True,
                            "content": final_content,
                            "tool_calls": tool_calls,
                            "tool_results": tool_results,
                            "provider": "anthropic",
                            "usage": final_response.get("usage", {})
                        }
                else:
                    logger.error(f"❌ Final API call failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"Final API call failed: {response.status_code} - {response.text}",
                        "provider": "anthropic"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error continuing conversation: {e}")
            return {
                "success": False,
                "error": f"Error continuing conversation: {str(e)}",
                "provider": "anthropic"
            }
    
    async def close_sessions(self):
        """Cleanup method for server shutdown"""
        logger.info("Closing LLM service sessions...")
        self.conversation_messages.clear()
        self.mcp_integration.mcp_initialized = False
        logger.info("Cleaned up MCP client, system prompt, and conversation caches")