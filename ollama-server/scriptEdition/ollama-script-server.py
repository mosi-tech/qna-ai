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
            self.default_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
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
    
    async def warm_anthropic_cache(self, model: str) -> bool:
        """Warm Anthropic prompt cache - try all tools first, fallback to batching if rate limited"""
        try:
            import asyncio
            
            logger.info("🔥 Warming Anthropic prompt cache...")
            
            # Get system prompt and tools (reuse existing methods)
            system_prompt = await self.get_system_prompt()
            mcp_tools = self.get_mcp_tools_for_openai()
            
            # First, cache system prompt only
            success = await self._cache_system_prompt(model, system_prompt)
            if not success:
                return False
            
            # Try to cache all tools at once (most token efficient)
            if mcp_tools:
                total_tools = len(mcp_tools)
                logger.info(f"📦 Attempting to cache all {total_tools} tools at once...")
                
                success = await self._cache_all_tools(model, system_prompt, mcp_tools)
                if success:
                    logger.info("✅ All tools cached successfully in single request")
                    return True
                
                # Fallback to batch caching if all-at-once failed
                logger.info("📦 Falling back to batch caching due to rate limits...")
                success = await self._cache_tools_in_batches(model, system_prompt, mcp_tools)
                
            logger.info("✅ Cache warming completed")
            return True
                    
        except Exception as e:
            logger.warning(f"⚠️ Cache warming failed: {e}")
            return False
    
    async def _cache_system_prompt(self, model: str, system_prompt: str, max_retries: int = 3) -> bool:
        """Cache system prompt with retry logic"""
        for attempt in range(max_retries):
            try:
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
                    "messages": [
                        {"role": "user", "content": "Warming system prompt cache."}
                    ],
                    "max_tokens": 5
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/messages",
                        json=request_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'usage' in response_data:
                            input_tokens = response_data['usage'].get('input_tokens', 0)
                            logger.info(f"✅ System prompt cached - used {input_tokens} input tokens")
                        else:
                            logger.info("✅ System prompt cached successfully")
                        return True
                    elif response.status_code == 429:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"⚠️ Rate limit hit caching system prompt, attempt {attempt + 1}/{max_retries}, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"⚠️ Failed to cache system prompt: {response.status_code}")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Error caching system prompt attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        logger.warning(f"⚠️ Failed to cache system prompt after {max_retries} attempts")
        return False
    
    async def _cache_all_tools(self, model: str, system_prompt: str, all_tools: list, max_retries: int = 2) -> bool:
        """Try to cache all tools at once - most token efficient approach"""
        import asyncio
        
        for attempt in range(max_retries):
            try:
                # Convert all tools to Anthropic format
                anthropic_tools = []
                for i, tool in enumerate(all_tools):
                    anthropic_tool = {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    }
                    
                    # Add cache control to the last tool
                    if i == len(all_tools) - 1:
                        anthropic_tool["cache_control"] = {
                            "type": "ephemeral",
                            "ttl": "1h"
                        }
                    
                    anthropic_tools.append(anthropic_tool)
                
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
                    "messages": [
                        {"role": "user", "content": f"Warming cache with all {len(all_tools)} tools."}
                    ],
                    "tools": anthropic_tools,
                    "max_tokens": 5
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "anthropic-beta": "tools-2024-05-16"
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/messages",
                        json=request_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'usage' in response_data:
                            input_tokens = response_data['usage'].get('input_tokens', 0)
                            logger.info(f"✅ All {len(all_tools)} tools cached - used {input_tokens} input tokens")
                        else:
                            logger.info(f"✅ All {len(all_tools)} tools cached successfully")
                        return True
                    elif response.status_code == 429:
                        logger.warning(f"⚠️ Rate limit hit caching all tools, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # Exponential backoff
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.warning("⚠️ Rate limit hit - will fallback to batch caching")
                            return False
                    else:
                        logger.warning(f"⚠️ Failed to cache all tools: {response.status_code}")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Error caching all tools attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        return False
    
    async def _cache_tools_in_batches(self, model: str, system_prompt: str, all_tools: list) -> bool:
        """Fallback: progressive reduction - try all minus 10, minus 20, etc. until success, then cache remaining"""
        import asyncio
        
        total_tools = len(all_tools)
        reduction_step = 10
        
        logger.info(f"📦 Progressive reduction caching for {total_tools} tools...")
        
        # Try progressively smaller sets: all-10, all-20, all-30, etc.
        for reduction in range(reduction_step, total_tools, reduction_step):
            tools_to_cache = all_tools[:-reduction]  # Remove last 'reduction' tools
            remaining_tools = all_tools[-reduction:]  # Tools we removed
            
            logger.info(f"📦 Trying to cache {len(tools_to_cache)} tools (removing last {reduction})")
            
            success = await self._cache_tools_batch(model, system_prompt, tools_to_cache)
            if success:
                logger.info(f"✅ Successfully cached {len(tools_to_cache)} tools")
                
                # Now cache the remaining tools in small batches
                if remaining_tools:
                    logger.info(f"📦 Caching remaining {len(remaining_tools)} tools in batches...")
                    await self._cache_remaining_tools(model, system_prompt, remaining_tools)
                
                return True
            else:
                logger.warning(f"⚠️ Still rate limited with {len(tools_to_cache)} tools, reducing further...")
                await asyncio.sleep(1)
        
        # If we get here, even small sets are rate limited - try very small batches
        logger.warning("⚠️ All reductions failed, falling back to small individual batches...")
        await self._cache_remaining_tools(model, system_prompt, all_tools, batch_size=5)
        return True
    
    async def _cache_remaining_tools(self, model: str, system_prompt: str, remaining_tools: list, batch_size: int = 10) -> bool:
        """Cache remaining tools in small batches"""
        import asyncio
        
        total_remaining = len(remaining_tools)
        total_batches = (total_remaining + batch_size - 1) // batch_size
        
        for batch_start in range(0, total_remaining, batch_size):
            batch_end = min(batch_start + batch_size, total_remaining)
            batch_tools = remaining_tools[batch_start:batch_end]
            batch_num = (batch_start // batch_size) + 1
            
            logger.info(f"📦 Caching remaining batch {batch_num}/{total_batches} ({len(batch_tools)} tools)")
            
            success = await self._cache_tools_batch(model, system_prompt, batch_tools)
            if not success:
                logger.warning(f"⚠️ Failed to cache remaining batch {batch_num}")
            
            # Small delay between batches
            if batch_end < total_remaining:
                await asyncio.sleep(1)
        
        return True
    
    async def _cache_tools_batch(self, model: str, system_prompt: str, tools_batch: list, max_retries: int = 3) -> bool:
        """Cache a cumulative batch of tools with retry logic - EVERY batch gets cache control"""
        import asyncio
        
        for attempt in range(max_retries):
            try:
                # Convert tools to Anthropic format
                anthropic_tools = []
                for i, tool in enumerate(tools_batch):
                    anthropic_tool = {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    }
                    
                    # Add cache control to EVERY last tool in EVERY batch
                    if i == len(tools_batch) - 1:
                        anthropic_tool["cache_control"] = {
                            "type": "ephemeral",
                            "ttl": "1h"
                        }
                    
                    anthropic_tools.append(anthropic_tool)
                
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
                    "messages": [
                        {"role": "user", "content": f"Warming tools cache ({len(tools_batch)} tools cumulative)."}
                    ],
                    "tools": anthropic_tools,
                    "max_tokens": 5
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "anthropic-beta": "tools-2024-05-16"
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/messages",
                        json=request_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'usage' in response_data:
                            input_tokens = response_data['usage'].get('input_tokens', 0)
                            logger.info(f"✅ {len(tools_batch)} tools cached cumulatively - used {input_tokens} input tokens")
                        else:
                            logger.info(f"✅ {len(tools_batch)} tools cached cumulatively")
                        return True
                    elif response.status_code == 429:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"⚠️ Rate limit hit caching tools batch, attempt {attempt + 1}/{max_retries}, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"⚠️ Failed to cache tools batch: {response.status_code}")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Error caching tools batch attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        logger.warning(f"⚠️ Failed to cache tools batch after {max_retries} attempts")
        return False
    
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
                    
                    # Add tools if available - send tools in EVERY iteration for continued tool calling
                    if mcp_tools:
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
                        
                        # Check stop reason - if end_turn, LLM considers task complete
                        stop_reason = result.get("stop_reason", "")
                        logger.info(f"🛑 Anthropic stop_reason: {stop_reason}")
                        
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
                                # CRITICAL: Block forbidden financial/analytics function calls
                                if self.is_forbidden_function_call(function_name):
                                    forbidden_msg = f"❌ FORBIDDEN: Cannot call '{function_name}'. You can only use get_function_docstring() to inquire about function documentation. Write scripts that call these functions instead of executing them directly."
                                    logger.warning(f"🚫 Blocked forbidden function call: {function_name}")
                                    tool_results.append({
                                        "call": tool_call,
                                        "result": forbidden_msg
                                    })
                                    continue
                                
                                # Path massaging for file tools before calling MCP
                                if function_name in ["validation-server__write_file", "validation-server__read_file", "validation-server__validate_python_script"]:
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
                                    "tool_use_id": tool_use_id,
                                    "type": "tool_result",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": tool_content
                                        }
                                    ]
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
                        # No tool calls - check if we should continue or stop
                        content = message.get("content", "")
                        logger.info(f"🔄 No tool calls in iteration {iteration_count}, content: {content[:100]}...")
                        
                        # Check if LLM indicated it's done (for Anthropic)
                        llm_indicated_done = False
                        if self.llm_provider == "anthropic" and "stop_reason" in locals():
                            llm_indicated_done = stop_reason == "end_turn"
                            logger.info(f"🛑 LLM indicated done (end_turn): {llm_indicated_done}")
                        
                        # Check if we've completed the task (validation tool was called and succeeded)
                        validation_completed = any(
                            "validate_python_script" in call["function"]["name"] 
                            for call in all_tool_calls
                        )
                        
                        # Check if we have substantial Python code (task completion indicator)
                        has_python_code = (
                            "```python" in content or 
                            "def " in content or 
                            "import " in content or
                            len(content) > 500  # Substantial content
                        )
                        
                        if validation_completed or has_python_code or llm_indicated_done:
                            # Task appears complete
                            logger.info(f"🏁 Task completed after {iteration_count} iterations (validation: {validation_completed}, code: {has_python_code}, llm_done: {llm_indicated_done})")
                            return {
                                "content": content,
                                "tool_calls": all_tool_calls,
                                "tool_results": all_tool_results,
                                "iterations": iteration_count,
                                "stop_reason": stop_reason if self.llm_provider == "anthropic" else None
                            }
                        else:
                            # This is likely planning text - continue conversation
                            logger.info(f"🔄 Planning text detected, continuing conversation...")
                            
                            # Add the planning text to conversation and continue
                            if self.llm_provider == "anthropic":
                                messages.append(message["assistant_message"] if "assistant_message" in message else {
                                    "role": "assistant",
                                    "content": [{"type": "text", "text": content}]
                                })
                                
                                # Add a user message prompting for immediate tool calls
                                messages.append({
                                    "role": "user",
                                    "content": "Please proceed with the specific tool calls you mentioned. Use get_function_docstring() or write_file() now - don't just describe what you plan to do."
                                })
                            else:
                                # Ollama format
                                messages.append(message)
                                messages.append({
                                    "role": "user",
                                    "content": "Please proceed with the specific tool calls you mentioned. Use get_function_docstring() or write_file() now - don't just describe what you plan to do."
                                })
                            
                            # Continue the loop to get the actual script
                            continue
                
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
    
    def is_forbidden_function_call(self, function_name: str) -> bool:
        """Check if function call is forbidden (financial/analytics server functions except get_function_docstring)"""
        import re
        
        # Allow get_function_docstring from any server
        if function_name.endswith("get_function_docstring"):
            return False
        
        # Block all other financial-server and analytics-server functions
        forbidden_pattern = r"^(financial-server__|analytics-server__)"
        return bool(re.match(forbidden_pattern, function_name))
    
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
        
        elif function_name == "validation-server__validate_python_script":
            script_filename = arguments.get("script_filename", "")
            
            # Only massage if it's a relative path (not already absolute)
            if script_filename and not os.path.isabs(script_filename):
                # Prepend current working directory + scripts to relative filename
                absolute_path = os.path.join(scripts_dir, script_filename)
                massaged_args["script_filename"] = absolute_path
                
                logger.info(f"🔧 Path massaging (validate): '{script_filename}' → '{absolute_path}'")
            else:
                logger.info(f"🔧 Path unchanged (validate, already absolute): '{script_filename}'")
        
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
            
            # No script parsing needed - LLM should use tool calls (write_file → validate_python_script)
            validation_passed = any("validate" in call["function"]["name"] for call in tool_calls_made)
            script_saved = any("write_file" in call["function"]["name"] for call in tool_calls_made)
            
            # Extract script filename from write_file tool calls
            script_filename = None
            for call in tool_calls_made:
                if "write_file" in call["function"]["name"]:
                    filename = call["function"]["arguments"].get("filename")
                    if filename and filename.endswith('.py'):
                        script_filename = filename
                        break
            
            # Get available tools count for reporting
            available_tools = self.mcp_client.available_tools
            
            # Generate final structured response with tool call details
            return {
                "success": True,
                "data": {
                    "description": f"LLM processed financial question using tool calls: {question} {'✅ Script saved via tool calls' if script_saved else '❌ No script saved'}",
                    "body": [
                        {
                            "key": "question",
                            "value": question,
                            "description": "The financial question that was analyzed"
                        },
                        {
                            "key": "tool_calling_approach",
                            "value": "MCP validation workflow",
                            "description": "LLM used tool calls (write_file → validate_python_script) instead of direct script generation"
                        },
                        {
                            "key": "script_saved_via_tools",
                            "value": script_saved,
                            "description": "Whether script was saved via write_file tool call"
                        },
                        {
                            "key": "validation_attempted",
                            "value": validation_passed,
                            "description": "Whether validation was attempted via validate_python_script tool call"
                        },
                        {
                            "key": "workflow_status",
                            "value": "Tool-based workflow completed" if script_saved and validation_passed else "Partial tool workflow",
                            "description": "Status of the MCP tool-based script generation and validation workflow"
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

def print_progress(step: str, current: int, total: int, details: str = ""):
    """Print startup progress to terminal"""
    progress = int((current / total) * 30) if total > 0 else 0
    bar = "█" * progress + "░" * (30 - progress)
    percentage = int((current / total) * 100) if total > 0 else 0
    
    print(f"\r🚀 [{bar}] {percentage:3d}% | {step:<25} {details}", end="", flush=True)
    if current >= total:
        print()  # New line when complete

@app.on_event("startup")
async def startup_event():
    """Initialize MCP and warm cache on startup with progress display"""
    print("\n" + "="*80)
    print("🚀 FINANCIAL ANALYSIS SERVER STARTUP")
    print("="*80)
    
    total_steps = 3 if llm_service.llm_provider == "anthropic" else 2
    current_step = 0
    
    try:
        # Step 1: Initialize MCP client
        current_step += 1
        print_progress("Initializing MCP", current_step - 1, total_steps, "connecting to servers...")
        success = await llm_service.ensure_mcp_initialized()
        if success:
            tool_count = len(llm_service.mcp_client.available_tools) if llm_service.mcp_client else 0
            print_progress("MCP Initialized", current_step, total_steps, f"({tool_count} tools available)")
        else:
            print_progress("MCP Failed", current_step, total_steps, "(continuing without MCP)")
        
        # Step 2: Load system prompt
        current_step += 1
        print_progress("Loading System Prompt", current_step - 1, total_steps, "reading configuration...")
        await llm_service.get_system_prompt()
        print_progress("System Prompt Loaded", current_step, total_steps, f"({len(llm_service.system_prompt)} chars)")
        
        # Step 3: Warm Anthropic cache (if using Anthropic)
        if llm_service.llm_provider == "anthropic":
            current_step += 1
            print_progress("Warming Cache", current_step - 1, total_steps, "optimizing response times...")
            cache_success = await llm_service.warm_anthropic_cache(llm_service.default_model)
            if cache_success:
                print_progress("Cache Warmed", current_step, total_steps, "(1h TTL active)")
            else:
                print_progress("Cache Skipped", current_step, total_steps, "(will work without cache)")
        
        print("\n" + "✅ SERVER READY!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        print("="*80)

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

@app.post("/debug/test-tool-result-processing")
async def test_tool_result_processing():
    """Test endpoint to verify tool result processing without calling LLM"""
    try:
        if not await llm_service.ensure_mcp_initialized():
            return {"error": "MCP client not initialized"}
        
        # Simulate a validation tool call that should include error_traceback
        test_tool_calls = [
            {
                "type": "function",
                "function": {
                    "name": "validation-server__validate_python_script",
                    "arguments": {
                        "script_filename": "test_internal_error.py"
                    }
                },
                "anthropic_block": {"id": "test_id_123"}
            }
        ]
        
        logger.info("🧪 Testing tool result processing with validation call")
        
        # Execute the tool call (same logic as in call_llm_chat_with_tools)
        tool_results = []
        for i, tool_call in enumerate(test_tool_calls):
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            
            logger.info(f"🔧 Executing test tool: {function_name}")
            
            # Path massaging for file tools
            if function_name in ["validation-server__write_file", "validation-server__read_file", "validation-server__validate_python_script"]:
                arguments = llm_service.massage_file_tool_paths(function_name, arguments)
            
            # Execute MCP function
            result_data = await llm_service.mcp_client.call_tool(function_name, arguments)
            
            # Extract content from MCP CallToolResult
            if hasattr(result_data, 'content'):
                if hasattr(result_data.content[0], 'text'):
                    extracted_result = result_data.content[0].text
                else:
                    extracted_result = str(result_data.content[0])
            else:
                extracted_result = result_data
            
            tool_results.append({
                "call": tool_call,
                "result": extracted_result
            })
            
            logger.info(f"✅ Test tool call executed")
            logger.info(f"   Full result: {extracted_result}")
        
        # Parse the extracted result to see if error_traceback is present
        try:
            parsed_result = json.loads(extracted_result)
            has_error_traceback = "error_traceback" in parsed_result
            error_traceback_preview = parsed_result.get("error_traceback", "")[:200] if has_error_traceback else None
        except:
            parsed_result = None
            has_error_traceback = False
            error_traceback_preview = None
        
        return {
            "test_successful": True,
            "tool_calls_made": len(test_tool_calls),
            "extracted_result_length": len(extracted_result),
            "extracted_result_preview": extracted_result[:500] + "..." if len(extracted_result) > 500 else extracted_result,
            "has_error_traceback": has_error_traceback,
            "error_traceback_preview": error_traceback_preview,
            "parsed_result_keys": list(parsed_result.keys()) if parsed_result else None
        }
        
    except Exception as e:
        logger.error(f"❌ Test tool result processing failed: {e}")
        return {"error": str(e), "test_successful": False}

@app.get("/models")
async def list_models():
    """List available models based on provider"""
    if llm_service.llm_provider == "anthropic":
        anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
        return {
            "provider": "anthropic",
            "models": [
                anthropic_model, 
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
        anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
        print(f'{{"question": "What are my portfolio correlations?", "model": "{anthropic_model}"}}')
        print("\nMake sure you have:")
        print("1. LLM_PROVIDER=anthropic (default)")
        print("2. ANTHROPIC_API_KEY environment variable set")
        print(f"3. Model: {anthropic_model} (set via ANTHROPIC_MODEL or default)")
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