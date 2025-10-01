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
            self.default_model = "claude-3-5-sonnet-20241022"
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
        """Get system prompt with dynamically discovered MCP tools (cached)"""
        if self.system_prompt:
            return self.system_prompt
            
        # Load base system prompt
        base_prompt = await self.load_system_prompt()
        
        # COMMENTED OUT: Dynamic tool discovery for system prompt
        # The system prompt already contains instructions to use MCP functions directly
        # No need to inject discovered tools into the prompt
        
        # # Add dynamically discovered MCP functions if client is initialized
        # if self.mcp_initialized and self.mcp_client.available_tools:
        #     tools_summary = self.mcp_client.get_tools_summary()
        #     
        #     tools_info = []
        #     for server_name, tool_names in tools_summary.items():
        #         # Show up to 15 tools per server, then summarize
        #         displayed_tools = tool_names[:15]
        #         tools_line = f"**{server_name}**: {', '.join(displayed_tools)}"
        #         if len(tool_names) > 15:
        #             tools_line += f" (and {len(tool_names) - 15} more)"
        #         tools_info.append(tools_line)
        #     
        #     self.system_prompt = f"""{base_prompt}
        # 
        # **Dynamically Discovered MCP Functions:**
        # {chr(10).join(tools_info)}
        # 
        # Use only the exact function names listed above. All functions have been discovered from live MCP servers."""
        # else:
        #     self.system_prompt = base_prompt
        
        # Use base system prompt as-is since it already contains MCP instructions
        self.system_prompt = base_prompt
            
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
                    "Authorization": f"Bearer {self.api_key}",
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
                        request_data = {
                            "model": model,
                            "messages": messages,
                            "max_tokens": 4000
                        }
                    else:  # ollama
                        request_data = {
                            "model": model,
                            "messages": messages,
                            "stream": False  # Ensure no streaming for Ollama
                        }
                    
                    # Add tools if available
                    if mcp_tools:
                        request_data["tools"] = mcp_tools
                    
                    # Log request details
                    logger.info(f"📤 LLM Request (iteration {iteration_count}):")
                    logger.info(f"   Model: {model}")
                    logger.info(f"   Messages count: {len(messages)}")
                    logger.info(f"   Tools count: {len(mcp_tools) if mcp_tools else 0}")
                    logger.info(f"   Last message preview: {messages[-1]['content'][:150]}{'...' if len(messages[-1]['content']) > 150 else ''}")
                    
                    # Configure endpoint based on provider
                    if self.llm_provider == "anthropic":
                        endpoint = f"{self.base_url}/chat/completions"
                    else:  # ollama
                        endpoint = f"{self.base_url}/api/chat"
                    
                    logger.info(f"🌐 Sending request to {endpoint}")
                    response = await client.post(
                        endpoint,
                        json=request_data,
                        headers=headers
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    logger.info(f"📥 LLM Response received (iteration {iteration_count})")
                    
                    # Handle different response formats
                    if self.llm_provider == "anthropic":
                        # OpenAI format response - get first choice
                        choices = result.get("choices", [])
                        if not choices:
                            raise Exception("No choices in Anthropic response")
                        message = choices[0].get("message", {})
                    else:  # ollama
                        # Ollama format response - get message directly
                        message = result.get("message", {})
                    
                    # Log response details
                    content = message.get("content", "")
                    logger.info(f"📥 LLM Response content preview: {content[:200]}{'...' if len(content) > 200 else ''}")
                    
                    # Check if there are tool calls
                    tool_calls = message.get("tool_calls", [])
                    logger.info(f"🔧 Tool calls in response: {len(tool_calls)}")
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
                        
                        # Add assistant message with tool calls to conversation
                        messages.append(message)
                        
                        # Add tool results as user message (for next iteration)
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
                        
                        logger.info(f"📝 Tool results message preview: {tool_results_text[:400]}{'...' if len(tool_results_text) > 400 else ''}")
                        
                        # Add tool results as user message and continue the loop
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
        """Convert ALL MCP tools to OpenAI tool format (like Claude Code)"""
        if not self.mcp_client.available_tools:
            return []
        
        openai_tools = []
        
        # Convert ALL available MCP functions (like Claude Code does)
        for func_name, tool_info in self.mcp_client.available_tools.items():
            openai_tool = {
                "type": "function",
                "function": {
                    "name": func_name,
                    "description": tool_info.get("description", f"MCP function: {func_name}"),
                    "parameters": tool_info.get("inputSchema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
            }
            openai_tools.append(openai_tool)
        
        logger.info(f"Converted {len(openai_tools)} MCP tools for OpenAI format (ALL available tools)")
        return openai_tools
    
    async def call_llm_chat(self, model: str, user_message: str) -> str:
        """Call LLM chat API (legacy method - now uses tool calling)"""
        result = await self.call_llm_chat_with_tools(model, user_message)
        return result["content"]
    
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
            
            logger.info(f"LLM made {len(tool_calls_made)} tool calls during generation")
            
            # Parse and save the generated Python script
            try:
                # Extract Python script from code blocks
                if '```python' in script_response:
                    start = script_response.find('```python') + 9
                    end = script_response.find('```', start)
                    python_script = script_response[start:end].strip()
                elif '```' in script_response:
                    start = script_response.find('```') + 3
                    end = script_response.find('```', start)
                    python_script = script_response[start:end].strip()
                else:
                    # Fallback: treat entire response as script (unlikely but safe)
                    python_script = script_response.strip()
                
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
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022", 
                "claude-3-opus-20240229"
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
        print('{"question": "What are my portfolio correlations?", "model": "claude-3-5-sonnet-20241022"}')
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