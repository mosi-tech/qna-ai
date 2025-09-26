#!/usr/bin/env python3
"""
MCP Validation Server - Standalone MCP server for workflow validation

Provides MCP tools for validating workflow steps during creation phase.
"""

import json
import logging
import asyncio
from typing import Any, Sequence
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Import validation functions
from validation_server import MCP_VALIDATION_FUNCTIONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-validation-server")

# Create MCP server
app = Server("mcp-validation-server")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available validation tools"""
    return [
        Tool(
            name="get_available_functions",
            description="Get all available MCP functions with their schemas for workflow planning",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_schemas": {
                        "type": "object",
                        "description": "Function schemas dictionary provided by LLM from MCP discovery"
                    }
                },
                "required": ["function_schemas"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_function_schema", 
            description="Get detailed schema for a specific MCP function",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the MCP function to get schema for"
                    },
                    "function_schemas": {
                        "type": "object",
                        "description": "Function schemas dictionary provided by LLM from MCP discovery"
                    }
                },
                "required": ["function_name", "function_schemas"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="validate_workflow_step",
            description="Validate a single workflow step against available schemas",
            inputSchema={
                "type": "object", 
                "properties": {
                    "step_definition": {
                        "type": "object",
                        "description": "Workflow step to validate",
                        "properties": {
                            "type": {"type": "string", "enum": ["mcp_call", "python_function"]},
                            "fn": {"type": "string", "description": "Function name for mcp_call"},
                            "args": {"type": "object", "description": "Arguments for mcp_call"},
                            "function_file": {"type": "string", "description": "File path for python_function"},
                            "function_name": {"type": "string", "description": "Function name for python_function"},
                            "input_variables": {"type": "array", "items": {"type": "string"}},
                            "output_variable": {"type": "string", "description": "Variable name for step output"}
                        },
                        "required": ["type"]
                    },
                    "function_schemas": {
                        "type": "object",
                        "description": "Function schemas dictionary provided by LLM from MCP discovery"
                    }
                },
                "required": ["step_definition", "function_schemas"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="validate_template_variables",
            description="Validate that template variables in arguments can be resolved",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_string": {
                        "type": "string", 
                        "description": "String containing template variables like {{variable_name}}"
                    },
                    "available_variables": {
                        "type": "object",
                        "description": "Dictionary of available variables with their metadata"
                    }
                },
                "required": ["template_string", "available_variables"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="validate_complete_workflow",
            description="Validate entire workflow for step compatibility and data flow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_definition": {
                        "type": "object",
                        "properties": {
                            "steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "type": {"type": "string", "enum": ["mcp_call", "python_function"]},
                                        "fn": {"type": "string"},
                                        "args": {"type": "object"},
                                        "function_file": {"type": "string"},
                                        "function_name": {"type": "string"},
                                        "input_variables": {"type": "array", "items": {"type": "string"}},
                                        "output_variable": {"type": "string"}
                                    },
                                    "required": ["type"]
                                }
                            }
                        },
                        "required": ["steps"]
                    },
                    "function_schemas": {
                        "type": "object",
                        "description": "Function schemas dictionary provided by LLM from MCP discovery"
                    }
                },
                "required": ["workflow_definition", "function_schemas"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="suggest_next_step",
            description="Suggest next workflow step based on current state and goal",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_workflow": {
                        "type": "object",
                        "properties": {
                            "steps": {"type": "array", "items": {"type": "object"}}
                        }
                    },
                    "goal_description": {
                        "type": "string",
                        "description": "Description of the analysis goal"
                    },
                    "function_schemas": {
                        "type": "object",
                        "description": "Function schemas dictionary provided by LLM from MCP discovery"
                    }
                },
                "required": ["current_workflow", "goal_description", "function_schemas"],
                "additionalProperties": False
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    try:
        logger.info(f"🔧 Calling validation tool: {name}")
        
        if name not in MCP_VALIDATION_FUNCTIONS:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unknown validation tool: {name}",
                    "available_tools": list(MCP_VALIDATION_FUNCTIONS.keys())
                }, indent=2)
            )]
        
        # Call the validation function
        validation_function = MCP_VALIDATION_FUNCTIONS[name]
        
        # Handle different argument patterns
        if name == "get_available_functions":
            result = validation_function(arguments["function_schemas"])
        elif name == "get_function_schema":
            result = validation_function(arguments["function_name"], arguments["function_schemas"])
        elif name == "validate_workflow_step":
            result = validation_function(arguments["step_definition"], arguments["function_schemas"])
        elif name == "validate_template_variables":
            result = validation_function(arguments["template_string"], arguments["available_variables"])
        elif name == "validate_complete_workflow":
            result = validation_function(arguments["workflow_definition"], arguments["function_schemas"])
        elif name == "suggest_next_step":
            result = validation_function(arguments["current_workflow"], arguments["goal_description"], arguments["function_schemas"])
        else:
            result = {"error": f"Handler not implemented for {name}"}
        
        logger.info(f"✅ Validation tool {name} completed")
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"❌ Tool {name} failed: {e}")
        import traceback
        return [TextContent(
            type="text", 
            text=json.dumps({
                "error": f"Tool execution failed: {str(e)}",
                "traceback": traceback.format_exc()
            }, indent=2)
        )]

async def main():
    """Run the MCP validation server"""
    logger.info("🚀 Schema-agnostic MCP Validation Server starting...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-validation-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())