#!/usr/bin/env python3
"""
MCP Script Validation Server

Provides MCP tools for validating Python scripts in sandboxed environment.
Returns only validation status to LLM, never actual financial data.
"""

import sys
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

# Import shared execution logic
from shared_script_executor import execute_script, check_forbidden_imports

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-script-validation")

# Create MCP server
app = Server("mcp-script-validation-server")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available script validation tools"""
    return [
        Tool(
            name="validate_python_script",
            description="Validate Python script in sandboxed environment with mock data",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_filename": {
                        "type": "string",
                        "description": "Python script filename to validate (must exist in scripts directory)"
                    },
                    "mock": {
                        "type": "boolean", 
                        "default": True,
                        "description": "Use mock data for validation (always true for LLM validation)"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30,
                        "description": "Execution timeout in seconds"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional parameters to inject into script for validation"
                    }
                },
                "required": ["script_filename"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_validation_capabilities",
            description="Get information about validation environment capabilities",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    try:
        logger.info(f"🔧 Validation tool called: {name}")
        
        if name == "validate_python_script":
            return await validate_script(arguments)
        elif name == "get_validation_capabilities":
            return await get_capabilities()
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unknown validation tool: {name}",
                    "available_tools": ["validate_python_script", "get_validation_capabilities"]
                }, indent=2)
            )]
            
    except Exception as e:
        logger.error(f"❌ Tool {name} failed: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"Tool execution failed: {str(e)}",
                "tool": name
            }, indent=2)
        )]

async def validate_script(arguments: dict) -> list[TextContent]:
    """Validate Python script using shared execution logic"""
    script_filename = arguments.get("script_filename", "")
    timeout = arguments.get("timeout", 30)
    parameters = arguments.get("parameters", None)
    
    logger.info(f"🧪 Validating Python script: {script_filename} (timeout={timeout}s)")
    
    # Read script content from file
    import os
    
    # Handle both absolute and relative paths
    if os.path.isabs(script_filename):
        # Use absolute path as provided
        script_path = script_filename
    else:
        # Get the directory where this server script is located
        server_dir = os.path.dirname(os.path.abspath(__file__))
        script_path =  os.path.join(server_dir, "scripts", script_filename)  # current_dir/

    if not os.path.exists(script_path):
        return [TextContent(
            type="text",
            text=json.dumps({
                "valid": False,
                "error": f"Script file not found: {script_path}",
                "error_type": "FileNotFoundError"
            }, indent=2)
        )]
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "valid": False,
                "error": f"Failed to read script file: {str(e)}",
                "error_type": "FileReadError"
            }, indent=2)
        )]
    

    # First, check for forbidden imports
    forbidden_check = check_forbidden_imports(script_content)
    if not forbidden_check["valid"]:
        return [TextContent(
            type="text",
            text=json.dumps(forbidden_check, indent=2)
        )]
    
    
    # Execute script in validation mode (mock=True)
    execution_result = execute_script(
        script_content=script_content,
        mock_mode=True,  # Always validation mode
        timeout=timeout,
        parameters=parameters
    )
    
    # Convert execution result to validation result
    if execution_result["success"]:
        validation_result = {
            "valid": True,
            "message": "Script executed successfully in validation environment",
            "execution_time": execution_result.get("execution_time")
        }
        logger.info("✅ Script validation successful")
    else:
        validation_result = {
            "valid": False,
            "error": execution_result["error"]
        }
        # Include error_traceback if present
        if "error_traceback" in execution_result:
            validation_result["error_traceback"] = execution_result["error_traceback"]
        if "error_type" in execution_result:
            validation_result["error_type"] = execution_result["error_type"]
        logger.warning(f"❌ Script validation failed: {execution_result['error']}")
    
    return [TextContent(
        type="text",
        text=json.dumps(validation_result, indent=2)
    )]

async def get_capabilities() -> list[TextContent]:
    """Get validation environment capabilities"""
    capabilities = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "available_modules": [
            "json", "logging", "datetime", "typing", "random", "os", "sys"
        ],
        "validation_method": "script_execution_with_mock_flag",
        "validation_features": [
            "sandboxed_execution",
            "timeout_protection", 
            "error_classification",
            "mock_mcp_functions"
        ],
        "max_timeout": 60,
        "temp_directory_access": True
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(capabilities, indent=2)
    )]


async def main():
    """Run the MCP script validation server"""
    logger.info("🚀 MCP Script Validation Server starting...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-script-validation-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())