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
        ),
        Tool(
            name="write_file",
            description="Write content to a file in the scripts directory for validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to write (will be saved in scripts directory)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["filename", "content"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="read_file",
            description="Read content from a file in the scripts directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to read from scripts directory"
                    }
                },
                "required": ["filename"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="list_files",
            description="List all files in the scripts directory",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file from the scripts directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to delete from scripts directory"
                    }
                },
                "required": ["filename"],
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
        elif name == "write_file":
            return await write_file(arguments)
        elif name == "read_file":
            return await read_file(arguments)
        elif name == "list_files":
            return await list_files(arguments)
        elif name == "delete_file":
            return await delete_file(arguments)
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unknown validation tool: {name}",
                    "available_tools": ["validate_python_script", "get_validation_capabilities", "write_file", "read_file", "list_files", "delete_file"]
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
            "mock_mcp_functions",
            "file_management"
        ],
        "max_timeout": 60,
        "temp_directory_access": True,
        "file_tools": ["write_file", "read_file", "list_files", "delete_file"]
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(capabilities, indent=2)
    )]

def get_scripts_directory():
    """Get the scripts directory path"""
    import os
    server_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(server_dir, "scripts")
    # Create directory if it doesn't exist
    os.makedirs(scripts_dir, exist_ok=True)
    return scripts_dir

async def write_file(arguments: dict) -> list[TextContent]:
    """Write content to a file in the scripts directory"""
    filename = arguments.get("filename", "")
    content = arguments.get("content", "")
    
    if not filename:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "Filename is required"
            }, indent=2)
        )]
    
    try:
        import os
        scripts_dir = get_scripts_directory()
        file_path = os.path.join(scripts_dir, filename)
        
        # Security check: ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Invalid filename: path traversal not allowed"
                }, indent=2)
            )]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"📝 File written: {filename} ({len(content)} characters)")
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"File {filename} written successfully",
                "path": file_path,
                "size": len(content)
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"❌ Failed to write file {filename}: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Failed to write file: {str(e)}"
            }, indent=2)
        )]

async def read_file(arguments: dict) -> list[TextContent]:
    """Read content from a file in the scripts directory"""
    filename = arguments.get("filename", "")
    
    if not filename:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "Filename is required"
            }, indent=2)
        )]
    
    try:
        import os
        scripts_dir = get_scripts_directory()
        file_path = os.path.join(scripts_dir, filename)
        
        # Security check: ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Invalid filename: path traversal not allowed"
                }, indent=2)
            )]
        
        if not os.path.exists(file_path):
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"File not found: {filename}"
                }, indent=2)
            )]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"📖 File read: {filename} ({len(content)} characters)")
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "filename": filename,
                "content": content,
                "size": len(content)
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"❌ Failed to read file {filename}: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Failed to read file: {str(e)}"
            }, indent=2)
        )]

async def list_files(arguments: dict) -> list[TextContent]:
    """List all files in the scripts directory"""
    try:
        import os
        scripts_dir = get_scripts_directory()
        
        if not os.path.exists(scripts_dir):
            files = []
        else:
            files = [f for f in os.listdir(scripts_dir) if os.path.isfile(os.path.join(scripts_dir, f))]
        
        logger.info(f"📂 Listed {len(files)} files in scripts directory")
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "scripts_directory": scripts_dir,
                "files": files,
                "count": len(files)
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"❌ Failed to list files: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Failed to list files: {str(e)}"
            }, indent=2)
        )]

async def delete_file(arguments: dict) -> list[TextContent]:
    """Delete a file from the scripts directory"""
    filename = arguments.get("filename", "")
    
    if not filename:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": "Filename is required"
            }, indent=2)
        )]
    
    try:
        import os
        scripts_dir = get_scripts_directory()
        file_path = os.path.join(scripts_dir, filename)
        
        # Security check: ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Invalid filename: path traversal not allowed"
                }, indent=2)
            )]
        
        if not os.path.exists(file_path):
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"File not found: {filename}"
                }, indent=2)
            )]
        
        os.remove(file_path)
        
        logger.info(f"🗑️ File deleted: {filename}")
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"File {filename} deleted successfully"
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"❌ Failed to delete file {filename}: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }, indent=2)
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