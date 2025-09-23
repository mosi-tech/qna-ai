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
        self.system_prompt_path = "system-prompt.txt"
        self.ollama_base_url = "http://localhost:11434"
        self.mcp_servers = {
            "mcp-financial-server": "http://localhost:8001",
            "mcp-analytics-server": "http://localhost:8002"
        }
        self.available_tools = {}
        
    async def load_system_prompt(self) -> str:
        """Load the system prompt from file"""
        try:
            with open(self.system_prompt_path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            return "You are a helpful financial analysis assistant that generates tool calls for financial data analysis."
    
    async def check_mcp_server(self, server_name: str) -> bool:
        """Check if MCP server is running"""
        if server_name not in self.mcp_servers:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.mcp_servers[server_name]}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"MCP server {server_name} not available: {e}")
            return False
    
    async def discover_tools(self) -> Dict[str, Any]:
        """Discover available tools from MCP servers"""
        if self.available_tools:
            return self.available_tools
            
        all_tools = {}
        
        # Check financial server
        if await self.check_mcp_server("mcp-financial-server"):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{self.mcp_servers['mcp-financial-server']}/tools")
                    if response.status_code == 200:
                        financial_tools = response.json()
                        logger.info(f"Discovered financial tools: {financial_tools}")
                        
                        # Process tools from native MCP server
                        if isinstance(financial_tools, dict) and "tools" in financial_tools:
                            for tool in financial_tools["tools"]:
                                tool_name = tool.get("name", "unknown_tool")
                                all_tools[tool_name] = {
                                    "name": tool_name,
                                    "description": tool.get("description", "Financial tool"),
                                    "parameters": tool.get("inputSchema", {}).get("properties", {}),
                                    "server": "mcp-financial-server"
                                }
                        
                        logger.info(f"Discovered {len(financial_tools.get('tools', []))} financial tools")
                    
            except Exception as e:
                logger.error(f"Failed to get tools from financial server: {e}")
        
        # Check analytics server
        if await self.check_mcp_server("mcp-analytics-server"):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{self.mcp_servers['mcp-analytics-server']}/tools")
                    if response.status_code == 200:
                        analytics_tools = response.json()
                        logger.info(f"Discovered analytics tools: {analytics_tools}")
                        
                        # Process tools from native MCP server
                        if isinstance(analytics_tools, dict) and "tools" in analytics_tools:
                            for tool in analytics_tools["tools"]:
                                tool_name = tool.get("name", "unknown_tool")
                                all_tools[tool_name] = {
                                    "name": tool_name,
                                    "description": tool.get("description", "Analytics tool"),
                                    "parameters": tool.get("inputSchema", {}).get("properties", {}),
                                    "server": "mcp-analytics-server"
                                }
                        
                        logger.info(f"Discovered {len(analytics_tools.get('tools', []))} analytics tools")
                    
            except Exception as e:
                logger.error(f"Failed to get tools from analytics server: {e}")
        
        # If no tools discovered, add fallback tools
        if not all_tools:
            logger.warning("No tools discovered from MCP servers, using fallback tools")
            all_tools = {
                "alpaca_market_stocks_bars": {
                    "name": "alpaca_market_stocks_bars",
                    "description": "Get historical OHLC price bars for stocks",
                    "parameters": {"symbols": "string", "timeframe": "string", "start": "string", "end": "string"},
                    "server": "mcp-financial-server"
                },
                "alpaca_market_stocks_snapshots": {
                    "name": "alpaca_market_stocks_snapshots", 
                    "description": "Get current market snapshot with all data",
                    "parameters": {"symbols": "string"},
                    "server": "mcp-financial-server"
                },
                "alpaca_market_screener_most_actives": {
                    "name": "alpaca_market_screener_most_actives",
                    "description": "Get most active stocks by volume", 
                    "parameters": {"top": "integer"},
                    "server": "mcp-financial-server"
                },
                "calculate_sma": {
                    "name": "calculate_sma",
                    "description": "Calculate simple moving average of closing prices",
                    "parameters": {"data": "array", "period": "integer"}, 
                    "server": "mcp-analytics-server"
                },
                "calculate_rsi": {
                    "name": "calculate_rsi",
                    "description": "Calculate Relative Strength Index momentum oscillator",
                    "parameters": {"data": "array", "period": "integer"},
                    "server": "mcp-analytics-server"
                },
                "calculate_portfolio_metrics": {
                    "name": "calculate_portfolio_metrics", 
                    "description": "Calculate comprehensive portfolio metrics including returns and risk",
                    "parameters": {"weights": "array", "returns": "array"},
                    "server": "mcp-analytics-server"
                }
            }
        
        self.available_tools = all_tools
        return all_tools
    
    async def call_ollama(self, model: str, prompt: str, system_prompt: str) -> str:
        """Call Ollama API directly"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "system": system_prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
    
    async def generate_tool_calls_only(self, tools_needed: list) -> Dict[str, Any]:
        """Generate tool call format without actually executing them"""
        tool_calls_output = {
            "planned_tool_calls": [],
            "execution_plan": "Tool calls generated but not executed (output format only)"
        }
        
        for tool_call in tools_needed:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})
            
            # Determine server type
            server_type = "mcp-financial-server" if tool_name.startswith(("alpaca", "eodhd")) else "mcp-analytics-server"
            
            tool_calls_output["planned_tool_calls"].append({
                "tool_name": tool_name,
                "arguments": tool_args,
                "server": server_type,
                "status": "planned_only"
            })
        
        return tool_calls_output
    
    async def analyze_question(self, question: str, model: str = "llama3.2") -> Dict[str, Any]:
        """Analyze question and generate tool calls without execution"""
        try:
            # Discover available tools from MCP servers
            available_tools = await self.discover_tools()
            
            # Load system prompt
            system_prompt = await self.load_system_prompt()
            
            # Create tool list for Ollama
            tools_description = []
            for tool_name, tool_info in available_tools.items():
                params = list(tool_info.get("parameters", {}).keys())
                tools_description.append(f"- {tool_name}: {tool_info['description']} (params: {', '.join(params)})")
            
            # Ask Ollama to plan the analysis using DSL format
            planning_prompt = f"""
            Question: {question}
            
            Available MCP functions:
            {chr(10).join(tools_description)}
            
            Analyze the question and generate function calls using the DSL format specified in your system prompt.
            Return only valid JSON with "steps" array where each step has "fn" and "args".
            """
            
            # Get tool planning from Ollama
            tool_plan = await self.call_ollama(model, planning_prompt, system_prompt)
            
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
            
            # Generate tool calls output (no execution)
            tool_calls_data = await self.generate_tool_calls_only(tool_calls)
            
            # Generate final structured response
            return {
                "success": True,
                "data": {
                    "description": f"Tool call plan for: {question}",
                    "body": [
                        {
                            "key": "question",
                            "value": question,
                            "description": "The financial question that was analyzed"
                        },
                        {
                            "key": "tool_calls_planned",
                            "value": len(tool_calls),
                            "description": "Number of MCP tool calls that would be executed"
                        },
                        {
                            "key": "dsl_response",
                            "value": dsl_response,
                            "description": "Raw DSL format response with steps array"
                        },
                        {
                            "key": "tool_calls",
                            "value": tool_calls_data,
                            "description": "Converted tool calls from DSL format"
                        }
                    ],
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "data_sources": ["ollama", "mcp_tool_discovery"],
                        "calculation_methods": ["tool_call_planning"],
                        "execution_mode": "planning_only"
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
        """Cleanup method (no persistent connections to close)"""
        self.available_tools.clear()
        logger.info("Cleaned up tool cache")

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
    print("- Connect to native MCP servers via HTTP to discover available tools")
    print("- Generate appropriate tool calls for financial questions")
    print("- Return tool call plans WITHOUT executing them")
    print("- No FastMCP dependency required")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)