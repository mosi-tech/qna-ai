#!/usr/bin/env python3
"""
MCP Financial Server - Real Implementation

Real MCP server that connects to actual financial APIs.
Requires proper API keys and credentials to function.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional

# MCP Server Framework
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import real financial functions and schema utilities
from financial.functions_real import REAL_FINANCIAL_FUNCTIONS
from schema_utils import initialize_schema_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-financial-server-real")

# Create server instance
app = Server("mcp-financial-server-real")

# Cache for generated schemas - populated once at startup
_schema_cache = {}

@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available financial tools using dynamic schema generation"""
    # Use cached schemas for performance
    tools = []
    
    for func_name, schema in _schema_cache.items():
        tools.append(types.Tool(
            name=func_name,
            description=schema['description'],
            inputSchema=schema['inputSchema']
        ))
    
    logger.debug(f"Returned {len(tools)} financial tools from cache")
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing real tool: {name} with arguments: {arguments}")
        
        if name not in REAL_FINANCIAL_FUNCTIONS:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}",
                    "available_tools": list(REAL_FINANCIAL_FUNCTIONS.keys())
                })
            )]
        
        # Execute the function
        function = REAL_FINANCIAL_FUNCTIONS[name]
        result = function(**arguments)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"Real tool execution failed: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "tool": name,
                "arguments": arguments,
                "note": "Check API credentials and network connectivity"
            })
        )]


async def main():
    """Run the MCP Financial Server (Real Implementation)"""
    logger.info("Starting MCP Financial Server (Real Implementation)...")
    logger.info("Note: Requires ALPACA_API_KEY, ALPACA_SECRET_KEY, and EODHD_API_KEY environment variables")
    
    # Initialize schema cache once at startup
    global _schema_cache
    _schema_cache = initialize_schema_cache(REAL_FINANCIAL_FUNCTIONS)
    
    logger.info(f"Total functions exposed: {len(_schema_cache)}")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream,
            InitializationOptions(
                server_name="mcp-financial-server-real",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())