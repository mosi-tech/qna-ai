#!/usr/bin/env python3
"""
MCP Server for Enhanced Execution Engine

This MCP server provides tools to execute financial analysis workflows
through the Enhanced Execution Engine, making it easy to debug and test.
"""

import asyncio
import json
import logging
import httpx
from datetime import datetime
from typing import Dict, Any, List

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-execution-server")

# Initialize MCP server
server = Server("mcp-execution-server")

# Enhanced Execution Engine URL
EXECUTION_ENGINE_URL = "http://localhost:8003"

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available execution tools"""
    return [
        Tool(
            name="execute_workflow",
            description="Execute a financial analysis workflow using the Enhanced Execution Engine",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The financial question to analyze"
                    },
                    "plan": {
                        "type": "object",
                        "description": "The execution plan with MCP steps or Python fallback",
                        "properties": {
                            "steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "fn": {"type": "string"},
                                        "args": {"type": "object"}
                                    },
                                    "required": ["fn", "args"]
                                }
                            },
                            "python_fallback": {
                                "type": "object",
                                "properties": {
                                    "data_needed": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "fn": {"type": "string"},
                                                "args": {"type": "object"}
                                            }
                                        }
                                    },
                                    "script_reference": {"type": "string"},
                                    "function_name": {"type": "string"}
                                }
                            }
                        }
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of the analysis"
                    }
                },
                "required": ["question", "plan"]
            }
        ),
        Tool(
            name="execute_workflow_from_file",
            description="Execute a workflow from a saved workflow file",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_file": {
                        "type": "string",
                        "description": "Path to workflow JSON file (e.g., 'ollama-server/workflow/workflow_name.json')"
                    }
                },
                "required": ["workflow_file"]
            }
        ),
        Tool(
            name="check_execution_engine_status",
            description="Check if the Enhanced Execution Engine is running and healthy",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_available_workflows",
            description="List all saved workflow files",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search (default: 'ollama-server/workflow')",
                        "default": "ollama-server/workflow"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "execute_workflow":
            return await execute_workflow(arguments)
        elif name == "execute_workflow_from_file":
            return await execute_workflow_from_file(arguments)
        elif name == "check_execution_engine_status":
            return await check_execution_engine_status()
        elif name == "list_available_workflows":
            return await list_available_workflows(arguments)
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def execute_workflow(arguments: dict) -> list[types.TextContent]:
    """Execute a workflow using the Enhanced Execution Engine"""
    question = arguments.get("question")
    plan = arguments.get("plan")
    description = arguments.get("description", f"Execution for: {question}")
    
    # Prepare request payload
    payload = {
        "question": question,
        "plan": plan,
        "description": description
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{EXECUTION_ENGINE_URL}/execute",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Format the response nicely
                formatted_result = format_execution_result(result)
                return [types.TextContent(type="text", text=formatted_result)]
            else:
                error_msg = f"Execution failed with status {response.status_code}: {response.text}"
                return [types.TextContent(type="text", text=error_msg)]
                
    except httpx.ConnectError:
        return [types.TextContent(
            type="text", 
            text="❌ Cannot connect to Enhanced Execution Engine at http://localhost:8003\n\nPlease start the engine with:\n```bash\npython ollama-server/execution-engine-enhanced.py\n```"
        )]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Execution error: {str(e)}")]

async def execute_workflow_from_file(arguments: dict) -> list[types.TextContent]:
    """Execute a workflow from a saved file"""
    workflow_file = arguments.get("workflow_file")
    
    try:
        # Load workflow from file
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        # Execute the workflow
        return await execute_workflow(workflow_data)
        
    except FileNotFoundError:
        return [types.TextContent(type="text", text=f"Workflow file not found: {workflow_file}")]
    except json.JSONDecodeError:
        return [types.TextContent(type="text", text=f"Invalid JSON in workflow file: {workflow_file}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error loading workflow: {str(e)}")]

async def check_execution_engine_status() -> list[types.TextContent]:
    """Check if the Enhanced Execution Engine is running"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{EXECUTION_ENGINE_URL}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                status_text = f"""✅ Enhanced Execution Engine Status: HEALTHY

Server: {EXECUTION_ENGINE_URL}
Status: {health_data.get('status', 'unknown')}
Available Tools: {health_data.get('available_tools', 0)}
MCP Servers: {', '.join(health_data.get('mcp_servers', []))}
Features: {', '.join(health_data.get('features', []))}
Timestamp: {health_data.get('timestamp', 'unknown')}"""
                return [types.TextContent(type="text", text=status_text)]
            else:
                return [types.TextContent(
                    type="text", 
                    text=f"❌ Engine responded with status {response.status_code}: {response.text}"
                )]
                
    except httpx.ConnectError:
        return [types.TextContent(
            type="text", 
            text="❌ Enhanced Execution Engine is NOT running\n\nStart it with:\n```bash\npython ollama-server/execution-engine-enhanced.py\n```"
        )]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Health check error: {str(e)}")]

async def list_available_workflows(arguments: dict) -> list[types.TextContent]:
    """List all available workflow files"""
    directory = arguments.get("directory", "ollama-server/workflow")
    
    try:
        import os
        import glob
        
        pattern = os.path.join(directory, "*.json")
        workflow_files = glob.glob(pattern)
        
        if not workflow_files:
            return [types.TextContent(type="text", text=f"No workflow files found in {directory}")]
        
        # Sort by modification time (newest first)
        workflow_files.sort(key=os.path.getmtime, reverse=True)
        
        result = f"📁 Available Workflows ({len(workflow_files)} files):\n\n"
        
        for i, file_path in enumerate(workflow_files, 1):
            filename = os.path.basename(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # Try to extract question from file
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    question = data.get('question', 'Unknown question')
                    question_preview = question[:60] + "..." if len(question) > 60 else question
            except:
                question_preview = "Could not read question"
            
            result += f"{i}. **{filename}**\n"
            result += f"   📝 {question_preview}\n"
            result += f"   🕒 {mod_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error listing workflows: {str(e)}")]

def format_execution_result(result: dict) -> str:
    """Format execution result for display"""
    if not result.get("success"):
        return f"❌ Execution Failed\n\nError: {result.get('error', 'Unknown error')}"
    
    data = result.get("data", {})
    description = data.get("description", "Analysis completed")
    body = data.get("body", [])
    metadata = data.get("metadata", {})
    
    formatted = f"✅ Execution Successful\n\n**Description**: {description}\n\n"
    
    # Add key results
    if body:
        formatted += "**Results**:\n"
        for item in body[:10]:  # Limit to first 10 items
            key = item.get("key", "unknown")
            value = item.get("value", "")
            desc = item.get("description", "")
            
            # Format value nicely
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, indent=2)[:200] + "..." if len(str(value)) > 200 else json.dumps(value, indent=2)
            else:
                value_str = str(value)
            
            formatted += f"- **{key}**: {value_str}\n"
            if desc:
                formatted += f"  _{desc}_\n"
            formatted += "\n"
    
    # Add metadata
    if metadata:
        formatted += "**Metadata**:\n"
        for key, value in metadata.items():
            if key != "body":  # Skip body as it's already shown
                formatted += f"- **{key}**: {value}\n"
    
    return formatted

async def main():
    # Import here to avoid issues with event loop
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-execution-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())