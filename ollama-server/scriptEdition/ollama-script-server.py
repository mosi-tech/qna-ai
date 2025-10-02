#!/usr/bin/env python3
"""
Claude with Native MCP Integration Server

This server accepts questions via HTTP API, sends them to Claude with direct MCP server connections,
and returns the formatted JSON response.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import httpx
import anthropic
from mcp_client import mcp_client, initialize_mcp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama-server")

app = FastAPI(title="Ollama Native MCP Financial Analysis Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    model: Optional[str] = None  # Will use provider default if not specified

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class UniversalLLMToolCallService:
    def __init__(self):
        # Use absolute path for system prompt file
        import os
        self.system_prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system-prompt.txt")
        self.system_prompt = None  # Cache for system prompt
        self.conversation_messages = []  # Store conversation history
        self.mcp_client = mcp_client  # Use singleton MCP client
        self.mcp_initialized = False
        
        # Determine which LLM provider to use
        self.llm_provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        
        if self.llm_provider == "anthropic":
            self.base_url = "https://api.anthropic.com/v1"
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            self.default_model = "claude-3-5-haiku-20241022"
            if not self.api_key:
                logger.warning("ANTHROPIC_API_KEY environment variable not set")
        elif self.llm_provider == "ollama":
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.api_key = None  # Ollama doesn't need API key
            self.default_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.llm_provider}. Use 'anthropic' or 'ollama'")
            
        logger.info(f"🤖 Initialized {self.llm_provider.upper()} LLM service")
        
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
        if self.mcp_initialized:
            return True
            
        try:
            # Load MCP server configuration
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ollama-mcp-config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Initialize MCP client
            await initialize_mcp_client(config)
            self.mcp_initialized = True
            logger.info(f"MCP client initialized with {len(self.mcp_client.available_tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            return False
    
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
                    logger.info(f"🔧 OpenAI tool format will be used")
            
            # Add user message to conversation
            messages = self.conversation_messages + [
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
            
            logger.info(f"📤 Initial user message to LLM: {user_message[:200]}{'...' if len(user_message) > 200 else ''}")
            
            # Configure headers based on provider
            headers = {"Content-Type": "application/json"}
            if self.llm_provider == "anthropic":
                headers.update({
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "anthropic-beta": "tools-2024-05-16"
                })
            # Ollama doesn't need special headers
            
            # Track all tool calls made across iterations
            all_tool_calls = []
            all_tool_results = []
            iteration_count = 0
            max_iterations = 10  # Prevent infinite loops
            
            async with httpx.AsyncClient(timeout=None) as client:  # No timeout for tool calling iterations
                # Multi-level tool calling loop (like Claude Code)
                while iteration_count < max_iterations:
                    iteration_count += 1
                    logger.info(f"🔄 Tool calling iteration {iteration_count}")
                    
                    # Configure request based on provider
                    if self.llm_provider == "anthropic":
                        # Extract system message and user messages for Anthropic format
                        system_msg = None
                        user_messages = []
                        for msg in messages:
                            if msg["role"] == "system":
                                system_msg = msg["content"]
                            else:
                                user_messages.append(msg)
                        
                        request_data = {
                            "model": model,
                            "max_tokens": 4000,
                            "messages": user_messages
                        }
                        
                        # Add system message with cache control for 1-hour TTL
                        if system_msg:
                            request_data["system"] = [
                                {
                                    "type": "text",
                                    "text": system_msg,
                                    "cache_control": {
                                        "type": "ephemeral",
                                        "ttl": "1h"
                                    }
                                }
                            ]
                    else:  # ollama
                        request_data = {
                            "model": model,
                            "messages": messages,
                            "stream": False  # Ensure no streaming for Ollama
                        }
                    
                    # Add tools if available - ONLY on first iteration to establish context
                    if mcp_tools and iteration_count == 1:
                        if self.llm_provider == "anthropic":
                            # For Anthropic: Add cache control ONLY to the LAST tool to cache entire tools array
                            anthropic_tools = []
                            for i, tool in enumerate(mcp_tools):
                                anthropic_tool = {
                                    "name": tool["function"]["name"],
                                    "description": tool["function"]["description"],
                                    "input_schema": tool["function"]["parameters"]
                                }
                                
                                # Add cache control ONLY to the last tool to cache the entire tools array
                                if i == len(mcp_tools) - 1:
                                    anthropic_tool["cache_control"] = {
                                        "type": "ephemeral",
                                        "ttl": "1h"
                                    }
                                
                                anthropic_tools.append(anthropic_tool)
                            request_data["tools"] = anthropic_tools
                            logger.info(f"🔧 Anthropic: Using {len(anthropic_tools)} tools with cache control on LAST tool (1hr TTL)")
                        else:
                            request_data["tools"] = mcp_tools
                            logger.info(f"🔧 Using {len(mcp_tools)} tools in OpenAI format")
                    elif mcp_tools:
                        logger.info(f"🔧 Skipping tools on iteration {iteration_count} (tools sent in iteration 1 only)")
                    
                    # Log request details with size analysis
                    logger.info(f"📤 LLM Request (iteration {iteration_count}):")
                    logger.info(f"   Model: {model}")
                    logger.info(f"   Messages count: {len(messages)}")
                    logger.info(f"   Tools count: {len(mcp_tools) if mcp_tools else 0}")
                    logger.info(f"   Last message preview: {messages[-1]['content'][:150]}{'...' if len(messages[-1]['content']) > 150 else ''}")
                    
                    # Calculate and log request size breakdown
                    import json
                    total_request_size = len(json.dumps(request_data))
                    logger.info(f"   📊 REQUEST SIZE ANALYSIS:")
                    logger.info(f"      Total request: {total_request_size:,} characters")
                    
                    if 'system' in request_data and self.llm_provider == "anthropic":
                        system_size = len(json.dumps(request_data['system']))
                        logger.info(f"      System (cached): {system_size:,} characters")
                    
                    if 'tools' in request_data:
                        tools_size = len(json.dumps(request_data['tools']))
                        tools_count = len(request_data['tools'])
                        avg_tool_size = tools_size // tools_count if tools_count > 0 else 0
                        logger.info(f"      Tools: {tools_size:,} characters ({tools_count} tools, ~{avg_tool_size} chars each)")
                    
                    if 'messages' in request_data:
                        messages_size = len(json.dumps(request_data['messages']))
                        logger.info(f"      Messages: {messages_size:,} characters")
                    
                    # Configure endpoint based on provider
                    if self.llm_provider == "anthropic":
                        endpoint = f"{self.base_url}/messages"  # Use native Anthropic endpoint
                    else:  # ollama
                        endpoint = f"{self.base_url}/api/chat"
                    
                    logger.info(f"🌐 Sending request to {endpoint}")
                    
                    # Debug: Log the request structure for Anthropic
                    if self.llm_provider == "anthropic":
                        logger.info(f"🔍 Anthropic request structure:")
                        logger.info(f"   Model: {request_data.get('model')}")
                        logger.info(f"   Messages count: {len(request_data.get('messages', []))}")
                        logger.info(f"   Tools count: {len(request_data.get('tools', []))}")
                        if 'system' in request_data:
                            system_content = request_data['system']
                            logger.info(f"   System content type: {type(system_content)}")
                            if isinstance(system_content, list) and len(system_content) > 0:
                                first_item = system_content[0]
                                logger.info(f"   First system item keys: {list(first_item.keys())}")
                                if 'cache_control' in first_item:
                                    logger.info(f"   Cache control: {first_item['cache_control']}")
                    
                    response = await client.post(
                        endpoint,
                        json=request_data,
                        headers=headers
                    )
                    
                    # Detailed error logging for rate limits and other issues
                    if response.status_code != 200:
                        logger.error(f"❌ API Request failed with status {response.status_code}")
                        logger.error(f"   Endpoint: {endpoint}")
                        logger.error(f"   Headers: {headers}")
                        
                        # Log response details
                        try:
                            error_response = response.json()
                            logger.error(f"   Error response: {error_response}")
                        except:
                            logger.error(f"   Raw response text: {response.text}")
                        
                        # Special handling for rate limits
                        if response.status_code == 429:
                            logger.error(f"🚨 RATE LIMIT HIT - Analyzing request size:")
                            
                            # Calculate request size
                            import json
                            request_json = json.dumps(request_data)
                            request_size = len(request_json)
                            logger.error(f"   Total request size: {request_size:,} characters")
                            
                            # Break down request components
                            if 'system' in request_data:
                                system_size = len(json.dumps(request_data['system']))
                                logger.error(f"   System content size: {system_size:,} characters")
                            
                            if 'tools' in request_data:
                                tools_size = len(json.dumps(request_data['tools']))
                                tools_count = len(request_data['tools'])
                                logger.error(f"   Tools size: {tools_size:,} characters ({tools_count} tools)")
                            
                            if 'messages' in request_data:
                                messages_size = len(json.dumps(request_data['messages']))
                                messages_count = len(request_data['messages'])
                                logger.error(f"   Messages size: {messages_size:,} characters ({messages_count} messages)")
                            
                            # Check if we have cache headers in response
                            cache_headers = {k: v for k, v in response.headers.items() if 'cache' in k.lower()}
                            if cache_headers:
                                logger.error(f"   Cache-related headers: {cache_headers}")
                            else:
                                logger.error(f"   No cache headers found in response")
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    logger.info(f"📥 LLM Response received (iteration {iteration_count})")
                    
                    # Debug: Log the full response structure
                    if self.llm_provider == "anthropic":
                        logger.info(f"🔍 Anthropic response structure:")
                        logger.info(f"   Response keys: {list(result.keys())}")
                        logger.info(f"   Content field exists: {'content' in result}")
                        if 'content' in result:
                            content = result['content']
                            logger.info(f"   Content type: {type(content)}")
                            logger.info(f"   Content length: {len(content) if isinstance(content, list) else 'N/A'}")
                            if isinstance(content, list) and len(content) > 0:
                                logger.info(f"   First content item: {content[0]}")
                            else:
                                logger.info(f"   Content is empty or not a list: {content}")
                        else:
                            logger.info(f"   Full response: {result}")
                    
                    # Log token usage for successful requests
                    if self.llm_provider == "anthropic" and "usage" in result:
                        usage = result["usage"]
                        logger.info(f"🎯 TOKEN USAGE ANALYSIS:")
                        logger.info(f"   Input tokens: {usage.get('input_tokens', 0):,}")
                        logger.info(f"   Output tokens: {usage.get('output_tokens', 0):,}")
                        logger.info(f"   Total tokens: {usage.get('input_tokens', 0) + usage.get('output_tokens', 0):,}")
                        
                        # Check for cache performance if available
                        if "cache_creation_input_tokens" in usage:
                            logger.info(f"   Cache creation tokens: {usage.get('cache_creation_input_tokens', 0):,}")
                        if "cache_read_input_tokens" in usage:
                            logger.info(f"   Cache read tokens: {usage.get('cache_read_input_tokens', 0):,}")
                            cache_hit_ratio = usage.get('cache_read_input_tokens', 0) / max(usage.get('input_tokens', 1), 1)
                            logger.info(f"   Cache hit ratio: {cache_hit_ratio:.2%}")
                    elif "usage" in result:
                        # For other providers
                        usage = result["usage"]
                        logger.info(f"🎯 TOKEN USAGE: {usage}")
                    
                    # Handle different response formats
                    if self.llm_provider == "anthropic":
                        # Keep Anthropic response in native format for conversation
                        response_content = result.get("content", [])
                        if not response_content:
                            raise Exception("No content in Anthropic response")
                        
                        # Add assistant message to conversation in Anthropic format
                        assistant_message = {"role": "assistant", "content": response_content}
                        
                        # Extract tool calls for execution (still need OpenAI format for our MCP calls)
                        tool_calls = []
                        text_content = ""
                        
                        for block in response_content:
                            if block.get("type") == "text":
                                text_content += block.get("text", "")
                            elif block.get("type") == "tool_use":
                                # Convert Anthropic tool_use to OpenAI format for MCP execution
                                tool_call = {
                                    "id": block.get("id", ""),
                                    "type": "function",
                                    "function": {
                                        "name": block.get("name", ""),
                                        "arguments": block.get("input", {})
                                    },
                                    "anthropic_block": block  # Keep original for tool_result linking
                                }
                                tool_calls.append(tool_call)
                        
                        message = {
                            "content": text_content,
                            "tool_calls": tool_calls,
                            "assistant_message": assistant_message  # Keep for conversation
                        }
                    else:  # ollama
                        # Ollama format response - get message directly
                        message = result.get("message", {})
                    
                    # Log response details
                    content = message.get("content", "")
                    logger.info(f"📥 LLM Response content preview: {content[:200]}{'...' if len(content) > 200 else ''}")
                    
                    # Check if there are tool calls
                    tool_calls = message.get("tool_calls", [])
                    logger.info(f"🔧 Tool calls in response: {len(tool_calls)}")
                    logger.info(f"🔧 Message keys: {list(message.keys())}")
                    logger.info(f"🔧 Message content type: {type(message.get('content', ''))}")
                    logger.info(f"🔧 Tool calls type: {type(tool_calls)}")
                    logger.info(f"🔧 Tool calls content: {tool_calls}")
                    
                    if tool_calls:
                        logger.info(f"🔧 LLM requested {len(tool_calls)} tool calls in iteration {iteration_count}")
                        for i, tool_call in enumerate(tool_calls):
                            logger.info(f"   Tool {i+1}: {tool_call['function']['name']} with args: {tool_call['function']['arguments']}")
                        
                        # Execute tool calls via MCP
                        tool_results = []
                        for i, tool_call in enumerate(tool_calls):
                            function_name = tool_call["function"]["name"]
                            arguments = tool_call["function"]["arguments"]
                            
                            try:
                                # Path massaging for file tools before calling MCP
                                if function_name in ["validation-server__write_file", "validation-server__read_file"]:
                                    arguments = self.massage_file_tool_paths(function_name, arguments)
                                
                                # Execute MCP function
                                logger.info(f"🔧 Executing MCP tool {i+1}/{len(tool_calls)}: {function_name}")
                                logger.info(f"   Arguments: {arguments}")
                                result_data = await self.mcp_client.call_tool(function_name, arguments)
                                
                                # Extract content from MCP CallToolResult if needed
                                if hasattr(result_data, 'content'):
                                    # MCP CallToolResult object - extract the content
                                    if hasattr(result_data.content[0], 'text'):
                                        extracted_result = result_data.content[0].text
                                    else:
                                        extracted_result = str(result_data.content[0])
                                else:
                                    # Already serializable data
                                    extracted_result = result_data
                                
                                tool_results.append({
                                    "call": tool_call,
                                    "result": extracted_result
                                })
                                logger.info(f"✅ Tool call {function_name} executed successfully")
                                logger.info(f"   Result preview: {str(extracted_result)[:300]}{'...' if len(str(extracted_result)) > 300 else ''}")
                            except Exception as e:
                                logger.error(f"❌ Tool call {function_name} failed: {e}")
                                tool_results.append({
                                    "call": tool_call,
                                    "error": str(e)
                                })
                        
                        # Track this iteration's tool calls
                        all_tool_calls.extend(tool_calls)
                        all_tool_results.extend(tool_results)
                        
                        if self.llm_provider == "anthropic":
                            # Add assistant message in Anthropic format
                            messages.append(message["assistant_message"])
                            
                            # Create tool results in Anthropic format
                            anthropic_tool_results = []
                            for i, tool_result in enumerate(tool_results):
                                tool_call = tool_calls[i]
                                anthropic_block = tool_call.get("anthropic_block", {})
                                tool_use_id = anthropic_block.get("id", tool_call.get("id", ""))
                                
                                if "result" in tool_result:
                                    content = tool_result["result"]
                                    if isinstance(content, str):
                                        tool_content = content
                                    else:
                                        tool_content = json.dumps(content, default=str)
                                else:
                                    tool_content = f"Error: {tool_result['error']}"
                                
                                anthropic_tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": tool_content
                                })
                            
                            # Add tool results as user message in Anthropic format
                            messages.append({
                                "role": "user",
                                "content": anthropic_tool_results
                            })
                            
                            logger.info(f"📝 Added {len(anthropic_tool_results)} tool results in Anthropic format")
                        else:
                            # Ollama format (keep existing logic)
                            messages.append(message)
                            
                            # Add tool results as text for Ollama
                            tool_results_text = "Tool results:\n\n"
                            for i, tool_result in enumerate(tool_results):
                                func_name = tool_calls[i]["function"]["name"]
                                if "result" in tool_result:
                                    content = tool_result["result"]
                                    if isinstance(content, str):
                                        tool_content = content
                                    else:
                                        tool_content = json.dumps(content, default=str)
                                else:
                                    tool_content = f"Error: {tool_result['error']}"
                                
                                tool_results_text += f"**{func_name}**:\n{tool_content}\n\n"
                            
                            messages.append({
                                "role": "user",
                                "content": tool_results_text
                            })
                        
                        logger.info(f"🔄 Added tool results to conversation, continuing to iteration {iteration_count + 1}")
                        # Continue the while loop - Claude can now request more tools or provide final answer
                        
                    else:
                        # No tool calls - Claude provided final answer
                        logger.info(f"🏁 Final response received after {iteration_count} iterations")
                        return {
                            "content": message.get("content", ""),
                            "tool_calls": all_tool_calls,
                            "tool_results": all_tool_results,
                            "iterations": iteration_count
                        }
                
                # If we exit the loop due to max iterations
                logger.warning(f"⚠️ Reached max iterations ({max_iterations}), returning last response")
                return {
                    "content": message.get("content", ""),
                    "tool_calls": all_tool_calls,
                    "tool_results": all_tool_results,
                    "iterations": iteration_count,
                    "max_iterations_reached": True
                }
                
        except Exception as e:
            logger.error(f"{self.llm_provider.upper()} chat API call failed: {e}")
            raise
    
    def get_mcp_tools_for_openai(self) -> List[Dict[str, Any]]:
        """Convert ALL MCP tools to OpenAI tool format with enhanced descriptions"""
        if not self.mcp_client.available_tools:
            return []
        
        openai_tools = []
        
        # Create function mapping for enhanced descriptions
        financial_functions = []
        analytics_functions = []
        validation_functions = []
        
        for func_name, tool_info in self.mcp_client.available_tools.items():
            server = tool_info["server"]
            original_name = tool_info.get("original_name", func_name)
            
            if server == "financial-server":
                financial_functions.append(original_name)
            elif server == "analytics-server":
                analytics_functions.append(original_name)
            elif server == "validation-server":
                validation_functions.append(original_name)
        
        # Convert ALL available MCP functions with enhanced descriptions
        for func_name, tool_info in self.mcp_client.available_tools.items():
            server = tool_info["server"]
            original_name = tool_info.get("original_name", func_name)
            base_description = tool_info.get("description", f"MCP function: {func_name}")
            
            # Enhance get_function_docstring descriptions with server mappings
            if original_name == "get_function_docstring":
                if server == "financial-server":
                    enhanced_description = f"{base_description} | Financial functions: {', '.join(financial_functions[:10])}{'...' if len(financial_functions) > 10 else ''}"
                elif server == "analytics-server":
                    enhanced_description = f"{base_description} | Analytics functions: {', '.join(analytics_functions[:10])}{'...' if len(analytics_functions) > 10 else ''}"
                else:
                    enhanced_description = base_description
            else:
                enhanced_description = base_description
            
            openai_tool = {
                "type": "function",
                "function": {
                    "name": func_name,
                    "description": enhanced_description,
                    "parameters": tool_info.get("inputSchema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
            }
            openai_tools.append(openai_tool)
        
        logger.info(f"Converted {len(openai_tools)} MCP tools with enhanced descriptions")
        return openai_tools
    
    async def call_llm_chat(self, model: str, user_message: str) -> str:
        """Call LLM chat API (legacy method - now uses tool calling)"""
        result = await self.call_llm_chat_with_tools(model, user_message)
        return result["content"]
    
    def massage_file_tool_paths(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Massage file tool paths to use absolute paths for LLM-provided relative filenames"""
        # Get current working directory and append scripts directory
        current_dir = os.getcwd()
        scripts_dir = os.path.join(current_dir, "scripts")
        
        # Create a copy to avoid modifying original arguments
        massaged_args = arguments.copy()
        
        if function_name in ["validation-server__write_file", "validation-server__read_file"]:
            filename = arguments.get("filename", "")
            
            # Only massage if it's a relative path (not already absolute)
            if filename and not os.path.isabs(filename):
                # Prepend current working directory + scripts to relative filename
                absolute_path = os.path.join(scripts_dir, filename)
                massaged_args["filename"] = absolute_path
                
                logger.info(f"🔧 Path massaging: '{filename}' → '{absolute_path}'")
            else:
                logger.info(f"🔧 Path unchanged (already absolute): '{filename}'")
        
        return massaged_args
    
    def validate_mcp_functions(self, tool_calls: list) -> Dict[str, Any]:
        """Validate that all function names are valid MCP functions using MCP client"""
        validation_result = {
            "valid_functions": [],
            "invalid_functions": [],
            "validation_passed": True,
            "validation_errors": []
        }
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "")
            
            if self.mcp_client.validate_function_exists(tool_name):
                validation_result["valid_functions"].append(tool_name)
            else:
                validation_result["invalid_functions"].append(tool_name)
                validation_result["validation_passed"] = False
                validation_result["validation_errors"].append(
                    f"Function '{tool_name}' is not available in MCP servers"
                )
        
        return validation_result
    
    async def generate_tool_calls_only(self, tool_calls: list) -> Dict[str, Any]:
        """Generate tool call format with validation, without executing them"""
        
        # Validate MCP functions first
        validation = self.validate_mcp_functions(tool_calls)
        
        tool_calls_output = {
            "planned_tool_calls": [],
            "execution_plan": "Tool calls generated but not executed (output format only)",
            "validation": validation
        }
        
        # Only process valid tool calls
        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "")
            tool_args = tool_call.get("arguments", {})
            
            # Get server type from MCP client
            tool_info = self.mcp_client.available_tools.get(tool_name, {})
            server_type = tool_info.get("server", "unknown_server")
            
            # Mark validation status
            is_valid = self.mcp_client.validate_function_exists(tool_name)
            status = "valid_mcp_function" if is_valid else "invalid_function"
            
            tool_calls_output["planned_tool_calls"].append({
                "tool_name": tool_name,
                "arguments": tool_args,
                "server": server_type,
                "status": status,
                "valid_mcp": is_valid
            })
        
        return tool_calls_output
    
    async def analyze_question(self, question: str, model: str = "llama3.2") -> Dict[str, Any]:
        """Analyze question and generate validated Python script"""
        try:
            # Ensure MCP client is initialized
            if not await self.ensure_mcp_initialized():
                return {
                    "success": False,
                    "error": "Failed to initialize MCP client"
                }
            
            # DEBUG: Show available MCP functions
            available_tools = self.mcp_client.available_tools
            tools_summary = self.mcp_client.get_tools_summary()
            
            logger.info("=== MCP TOOLS AVAILABLE TO LLM ===")
            for server_name, tool_names in tools_summary.items():
                logger.info(f"Server '{server_name}': {len(tool_names)} tools")
                for i, tool in enumerate(tool_names[:10]):  # Show first 10
                    logger.info(f"  {i+1}. {tool}")
                if len(tool_names) > 10:
                    logger.info(f"  ... and {len(tool_names) - 10} more")
            
            # Check if validation server is available
            validation_available = any("validate_python_script" in tools for tools in tools_summary.values())
            logger.info(f"Validation server available: {validation_available}")
            
            # Simple user message - just the question (system prompt handles script generation + validation)
            user_message = f"Question: {question}"
            
            # Get validated script from LLM using chat API WITH TOOL CALLING
            # The LLM will auto-validate using validate_python_script MCP function
            logger.info(f"Making tool-enabled call to {self.llm_provider.upper()}...")
            script_result = await self.call_llm_chat_with_tools(model, user_message)
            script_response = script_result["content"]
            tool_calls_made = script_result["tool_calls"]
            tool_results = script_result["tool_results"]
            
            logger.info(f"🔧 LLM TOOL CALLING ANALYSIS:")
            logger.info(f"   Tool calls made: {len(tool_calls_made)}")
            logger.info(f"   Tool results received: {len(tool_results)}")
            
            # Log each tool call in detail
            for i, tool_call in enumerate(tool_calls_made):
                logger.info(f"   Tool Call {i+1}:")
                logger.info(f"     Function: {tool_call.get('function', {}).get('name', 'Unknown')}")
                logger.info(f"     Arguments: {tool_call.get('function', {}).get('arguments', {})}")
            
            # Log tool results
            for i, result in enumerate(tool_results):
                logger.info(f"   Tool Result {i+1}:")
                if 'result' in result:
                    logger.info(f"     Success: {str(result['result'])[:200]}{'...' if len(str(result['result'])) > 200 else ''}")
                elif 'error' in result:
                    logger.info(f"     Error: {result['error']}")
            
            logger.info(f"📝 LLM RESPONSE ANALYSIS:")
            logger.info(f"   Response length: {len(script_response)} characters")
            logger.info(f"   Contains 'get_function_docstring': {'get_function_docstring' in script_response}")
            logger.info(f"   Contains 'write_file': {'write_file' in script_response}")
            logger.info(f"   Contains 'validate_python_script': {'validate_python_script' in script_response}")
            logger.info(f"   Contains Python code blocks: {'```python' in script_response}")
            logger.info(f"   Response preview: {script_response[:300]}{'...' if len(script_response) > 300 else ''}")
            
            # Check if we got actual Python code or just planning text
            def is_python_code(text):
                """Check if text contains actual Python code vs planning text"""
                # Look for Python code indicators
                python_indicators = [
                    'def ', 'import ', 'class ', 'if __name__', '#!/usr/bin/env python',
                    'call_mcp_function', 'try:', 'except:', 'for ', 'while ', 'with ',
                    '```python', '```'
                ]
                
                # Check for substantial Python code (not just comments or planning)
                lines = text.split('\n')
                code_lines = 0
                for line in lines:
                    line = line.strip()
                    if any(indicator in line for indicator in python_indicators):
                        code_lines += 1
                    elif line.startswith('#') and len(line) > 10:  # Substantial comments
                        code_lines += 0.5
                
                # Need at least 3 lines of substantial code
                return code_lines >= 3 and len(text) > 200
            
            # Parse and save the generated Python script
            try:
                # Extract the largest Python script from code blocks
                python_scripts = []
                
                # Find all Python code blocks
                import re
                python_blocks = re.findall(r'```python\n(.*?)\n```', script_response, re.DOTALL)
                if python_blocks:
                    python_scripts.extend(python_blocks)
                
                # Find all generic code blocks that might be Python
                generic_blocks = re.findall(r'```\n(.*?)\n```', script_response, re.DOTALL)
                for block in generic_blocks:
                    # Check if it looks like Python (has def, import, class, etc.)
                    if any(keyword in block for keyword in ['def ', 'import ', 'class ', 'if __name__', '#!/usr/bin/env python']):
                        python_scripts.append(block)
                
                if python_scripts:
                    # Take the longest script (most likely the main one)
                    python_script = max(python_scripts, key=len).strip()
                elif is_python_code(script_response):
                    # The entire response is Python code
                    python_script = script_response.strip()
                else:
                    # This is planning text, not Python code - should continue conversation
                    logger.warning(f"⚠️ Got planning text instead of Python code: {script_response[:200]}...")
                    
                    # Return indication that we need to continue the conversation
                    return {
                        "success": False,
                        "error": f"LLM generated planning text instead of Python code. Response: {script_response[:500]}...",
                        "suggestion": "LLM should continue conversation to generate actual Python script",
                        "response_type": "planning_text",
                        "response_content": script_response
                    }
                
                # If we got here, we have actual Python code
                if not python_script or len(python_script) < 50:
                    logger.warning(f"⚠️ Python script too short ({len(python_script)} chars): {python_script}")
                    return {
                        "success": False,
                        "error": f"Generated Python script too short ({len(python_script)} characters)",
                        "script_content": python_script
                    }
                
                # Create script filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                script_filename = f"volatility_analysis_{timestamp}.py"
                
                # Create scripts directory if it doesn't exist
                scripts_dir = os.path.join(os.path.dirname(__file__), "executionServer", "scripts")
                os.makedirs(scripts_dir, exist_ok=True)
                
                # Save the script
                script_path = os.path.join(scripts_dir, script_filename)
                with open(script_path, 'w') as f:
                    f.write(python_script)
                
                logger.info(f"Saved script: {script_path} ({len(python_script)} characters)")
                
                # Check if script contains validation indicators
                validation_passed = "validate_python_script" in script_response and "success" in script_response.lower()
                script_saved = True
                
            except Exception as e:
                logger.error(f"Failed to parse or save script: {e}")
                python_script = script_response
                script_filename = None
                script_path = None
                validation_passed = False
                script_saved = False
            
            # Get available tools count for reporting
            available_tools = self.mcp_client.available_tools
            
            # Generate final structured response with script details
            return {
                "success": True,
                "data": {
                    "description": f"Generated and saved Python script for: {question} {'✅ Script saved successfully' if script_saved else '❌ Failed to save script'}",
                    "body": [
                        {
                            "key": "question",
                            "value": question,
                            "description": "The financial question that was analyzed"
                        },
                        {
                            "key": "script_filename",
                            "value": script_filename,
                            "description": "Filename of the saved Python script"
                        },
                        {
                            "key": "script_path",
                            "value": script_path,
                            "description": "Full path where the script was saved"
                        },
                        {
                            "key": "script_content",
                            "value": python_script if script_saved else None,
                            "description": "The complete Python script content"
                        },
                        {
                            "key": "script_length",
                            "value": len(python_script) if script_saved else len(script_response),
                            "description": "Length of the generated script in characters"
                        },
                        {
                            "key": "validation_status",
                            "value": "Auto-validated by LLM" if validation_passed else "Generated (validation unclear)",
                            "description": "Validation status from LLM generation process"
                        },
                        {
                            "key": "tool_calls_made",
                            "value": len(tool_calls_made),
                            "description": "Number of MCP tool calls made during script generation"
                        },
                        {
                            "key": "tools_used",
                            "value": [call["function"]["name"] for call in tool_calls_made],
                            "description": "List of MCP functions called during generation"
                        },
                        {
                            "key": "real_time_validation",
                            "value": any("validate" in call["function"]["name"] for call in tool_calls_made),
                            "description": "Whether real-time validation was performed during generation"
                        },
                        {
                            "key": "execution_command",
                            "value": f"curl -X POST http://localhost:8013/execute -H 'Content-Type: application/json' -d '{{\"script_name\": \"{script_filename}\"}}'" if script_saved else None,
                            "description": "Command to execute the script via HTTP execution server"
                        },
                        {
                            "key": "mcp_tools_summary",
                            "value": tools_summary,
                            "description": "Summary of available MCP tools by server"
                        },
                        {
                            "key": "validation_server_available",
                            "value": validation_available,
                            "description": "Whether validate_python_script function is available"
                        },
                        {
                            "key": "total_mcp_tools",
                            "value": len(available_tools),
                            "description": "Total number of MCP tools available for script generation"
                        },
                        {
                            "key": "raw_llm_response",
                            "value": script_response,
                            "description": "Complete raw response from LLM (for debugging)"
                        }
                    ],
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "data_sources": ["ollama", "mcp_validation"],
                        "calculation_methods": ["python_script_generation", "llm_auto_validation"],
                        "execution_mode": "script_generation_with_save",
                        "system_prompt_approach": "parameterized_script_with_validation",
                        "validation_enabled": True,
                        "script_saved": script_saved,
                        "system_prompt_cached": self.system_prompt is not None,
                        "conversation_initialized": len(self.conversation_messages) > 0
                    }
                }
            }
                
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close_sessions(self):
        """Cleanup method and close MCP client sessions"""
        await self.mcp_client.close_all_sessions()
        self.system_prompt = None
        self.conversation_messages.clear()
        self.mcp_initialized = False
        logger.info("Cleaned up MCP client, system prompt, and conversation caches")

# Initialize service
llm_service = UniversalLLMToolCallService()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_question(request: QuestionRequest):
    """
    Analyze a financial question and generate tool calls without execution
    """
    try:
        logger.info(f"Received question: {request.question}")
        
        # Generate tool call plan using LLM
        result = await llm_service.analyze_question(request.question, request.model)
        
        return AnalysisResponse(
            success=result["success"],
            data=result.get("data"),
            error=result.get("error"),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/debug/mcp-tools")
async def debug_mcp_tools():
    """Debug endpoint to show available MCP tools"""
    try:
        if not await llm_service.ensure_mcp_initialized():
            return {"error": "MCP client not initialized"}
        
        tools_summary = llm_service.mcp_client.get_tools_summary()
        available_tools = llm_service.mcp_client.available_tools
        
        # Check for validation server specifically
        validation_tools = []
        for tool_name in available_tools.keys():
            if "validate" in tool_name.lower():
                validation_tools.append(tool_name)
        
        return {
            "total_tools": len(available_tools),
            "tools_by_server": tools_summary,
            "validation_tools": validation_tools,
            "validation_available": "validate_python_script" in available_tools,
            "sample_tools": list(available_tools.keys())[:20]  # First 20 tools
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/system-prompt")
async def debug_system_prompt():
    """Debug endpoint to show the system prompt sent to LLM"""
    try:
        system_prompt = await llm_service.get_system_prompt()
        return {
            "system_prompt": system_prompt,
            "length": len(system_prompt),
            "mcp_initialized": llm_service.mcp_initialized
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/models")
async def list_models():
    """List available models based on provider"""
    if llm_service.llm_provider == "anthropic":
        return {
            "provider": "anthropic",
            "models": [
                "claude-3-5-haiku-20241022", 
            ]
        }
    else:  # ollama
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(f"{llm_service.base_url}/api/tags")
                if response.status_code == 200:
                    return {
                        "provider": "ollama",
                        "models": response.json()
                    }
                else:
                    return {"error": "Failed to connect to Ollama"}
        except Exception as e:
            return {"error": str(e)}

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await llm_service.close_sessions()

if __name__ == "__main__":
    import os
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    
    print(f"Starting Universal LLM Script Generation Server ({provider.upper()})...")
    print("Server will be available at: http://localhost:8010")
    print("API Documentation at: http://localhost:8010/docs")
    print("\nTo test the server, send a POST request to /analyze with:")
    
    if provider == "anthropic":
        print('{"question": "What are my portfolio correlations?", "model": "claude-3-5-haiku-20241022"}')
        print("\nMake sure you have:")
        print("1. LLM_PROVIDER=anthropic (default)")
        print("2. ANTHROPIC_API_KEY environment variable set")
    else:
        print('{"question": "What are my portfolio correlations?", "model": "llama3.2"}')
        print("\nMake sure you have:")
        print("1. LLM_PROVIDER=ollama")
        print("2. Ollama running: ollama serve")
        print("3. OLLAMA_BASE_URL (default: http://localhost:11434)")
        print("4. OLLAMA_MODEL (default: llama3.2)")
    
    print("5. MCP servers running (for validation):")
    print("   - Financial server: mcp-server/financial_server.py")
    print("   - Analytics server: mcp-server/analytics_server.py") 
    print("   - Validation server: mcp-server/mcp_script_validation_server.py")
    print("\nThis server will:")
    print("- Connect to MCP servers for function discovery")
    print(f"- Generate parameterized Python scripts using {provider.upper()}")
    print("- Scripts will auto-validate using MCP validation server")
    print("- Use OpenAI-compatible API for tool calling")
    print("- Scripts ready for execution via HTTP execution server")
    
    uvicorn.run(app, host="0.0.0.0", port=8010)