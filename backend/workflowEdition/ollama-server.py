#!/usr/bin/env python3
"""
Ollama with Native MCP Integration Server

This server accepts questions via HTTP API, sends them to Ollama with direct MCP server connections,
and returns the formatted JSON response.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import httpx
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
    model: str = "gpt-oss:20b"

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class OllamaToolCallService:
    def __init__(self):
        # Use absolute path for system prompt file
        import os
        self.system_prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system-prompt.txt")
        self.ollama_base_url = "http://localhost:11434"
        self.system_prompt = None  # Cache for system prompt
        self.conversation_messages = []  # Store conversation history
        self.mcp_client = mcp_client  # Use singleton MCP client
        self.mcp_initialized = False
        
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
        
        # Add dynamically discovered MCP functions if client is initialized
        if self.mcp_initialized and self.mcp_client.available_tools:
            tools_summary = self.mcp_client.get_tools_summary()
            
            tools_info = []
            for server_name, tool_names in tools_summary.items():
                # Show up to 15 tools per server, then summarize
                displayed_tools = tool_names[:15]
                tools_line = f"**{server_name}**: {', '.join(displayed_tools)}"
                if len(tool_names) > 15:
                    tools_line += f" (and {len(tool_names) - 15} more)"
                tools_info.append(tools_line)
            
            self.system_prompt = f"""{base_prompt}

**Dynamically Discovered MCP Functions:**
{chr(10).join(tools_info)}

Use only the exact function names listed above. All functions have been discovered from live MCP servers."""
        else:
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
    
    async def call_ollama_chat(self, model: str, user_message: str) -> str:
        """Call Ollama chat API with conversation context"""
        try:
            # Initialize conversation if needed (system prompt set once)
            await self.initialize_conversation(model)
            
            # Add user message to conversation
            messages = self.conversation_messages + [
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Get assistant response
                assistant_response = result.get("message", {}).get("content", "")
                
                # Update conversation history (optional - for future multi-turn support)
                # self.conversation_messages.extend([
                #     {"role": "user", "content": user_message},
                #     {"role": "assistant", "content": assistant_response}
                # ])
                
                return assistant_response
                
        except Exception as e:
            logger.error(f"Ollama chat API call failed: {e}")
            raise
    
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
        """Analyze question and generate tool calls without execution"""
        try:
            # Ensure MCP client is initialized
            if not await self.ensure_mcp_initialized():
                return {
                    "success": False,
                    "error": "Failed to initialize MCP client"
                }
            
            # Simple user message - just the question (system prompt set once in conversation)
            user_message = f"Question: {question}"
            
            # Get tool planning from Ollama using chat API
            tool_plan = await self.call_ollama_chat(model, user_message)
            
            # Parse DSL format response
            try:
                if '```json' in tool_plan:
                    start = tool_plan.find('```json') + 7
                    end = tool_plan.find('```', start)
                    json_text = tool_plan[start:end].strip()
                else:
                    json_text = tool_plan.strip()
                
                dsl_response = json.loads(json_text)
                
                # Convert DSL format to tool calls format
                tool_calls = []
                if "steps" in dsl_response and isinstance(dsl_response["steps"], list):
                    for step in dsl_response["steps"]:
                        if "fn" in step and "args" in step:
                            tool_calls.append({
                                "name": step["fn"],
                                "arguments": step["args"]
                            })
                
            except Exception as e:
                logger.error(f"Failed to parse DSL response: {e}")
                tool_calls = []
                dsl_response = {"steps": []}
            
            # Generate tool calls output with validation (no execution)
            tool_calls_data = await self.generate_tool_calls_only(tool_calls)
            validation = tool_calls_data.get("validation", {})
            
            # Get available tools count for reporting
            available_tools = self.mcp_client.available_tools
            
            # Generate final structured response
            return {
                "success": True,
                "data": {
                    "description": f"Tool call plan for: {question} {'✅ All functions valid' if validation.get('validation_passed', False) else '❌ Contains invalid functions'}",
                    "body": [
                        {
                            "key": "question",
                            "value": question,
                            "description": "The financial question that was analyzed"
                        },
                        {
                            "key": "mcp_validation",
                            "value": validation,
                            "description": "Validation results showing which functions are valid MCP functions"
                        },
                        {
                            "key": "valid_mcp_functions",
                            "value": len(validation.get("valid_functions", [])),
                            "description": "Number of valid MCP functions in the generated plan"
                        },
                        {
                            "key": "invalid_functions",
                            "value": validation.get("invalid_functions", []),
                            "description": "List of invalid function names that are not valid MCP functions"
                        },
                        {
                            "key": "available_tools",
                            "value": len(available_tools),
                            "description": "Number of MCP tools discovered from servers"
                        },
                        {
                            "key": "tool_calls_planned",
                            "value": len(tool_calls),
                            "description": "Number of tool calls generated by the LLM"
                        },
                        {
                            "key": "dsl_response",
                            "value": dsl_response,
                            "description": "Raw DSL format response with steps array"
                        },
                        {
                            "key": "tool_calls",
                            "value": tool_calls_data,
                            "description": "Converted tool calls from DSL format with validation status"
                        }
                    ],
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "data_sources": ["ollama", "mcp_orchestration"],
                        "calculation_methods": ["tool_call_planning", "mcp_function_validation"],
                        "execution_mode": "planning_only",
                        "system_prompt_approach": "strict_mcp_enforcement",
                        "validation_enabled": True,
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
ollama_service = OllamaToolCallService()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_question(request: QuestionRequest):
    """
    Analyze a financial question and generate tool calls without execution
    """
    try:
        logger.info(f"Received question: {request.question}")
        
        # Generate tool call plan using Ollama
        result = await ollama_service.analyze_question(request.question, request.model)
        
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

@app.get("/models")
async def list_models():
    """List available ollama models"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                return {"models": response.json()}
            else:
                return {"error": "Failed to connect to Ollama"}
    except Exception as e:
        return {"error": str(e)}

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await ollama_service.close_sessions()

if __name__ == "__main__":
    print("Starting Ollama Native MCP Tool Call Generator Server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation at: http://localhost:8000/docs")
    print("\nTo test the server, send a POST request to /analyze with:")
    print('{"question": "What are the top 5 most active stocks today?", "model": "llama3.2"}')
    print("\nMake sure you have:")
    print("1. Ollama running: ollama serve")
    print("2. Required model pulled: ollama pull llama3.2")
    print("3. MCP servers running:")
    print("   - Financial server: http://localhost:8001")
    print("   - Analytics server: http://localhost:8002")
    print("\nThis server will:")
    print("- Use proper MCP client to connect to MCP servers via stdio")
    print("- Dynamically discover available MCP functions from connected servers")
    print("- Provide discovered functions to LLM for accurate orchestration planning")
    print("- Validate generated function names against actual MCP server implementations")
    print("- Use Ollama chat API with real-time MCP function discovery")
    print("- Generate appropriate MCP tool calls with full validation")
    print("- Return tool call plans WITHOUT executing them")
    print("- True MCP client integration with stdio server connections")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)