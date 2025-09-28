#!/usr/bin/env python3
"""
MCP Analytics Server

Python-based MCP server that provides technical analysis and portfolio analytics:
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
- Risk metrics (VaR, Sharpe ratio, volatility, etc.)
- Portfolio optimization and allocation
- Performance analysis

This server works in conjunction with the financial server to provide
comprehensive market analysis capabilities.
"""

import asyncio
import json
import logging
import inspect
import re
from typing import Dict, List, Any, Optional, get_type_hints

# MCP Server Framework
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import analytics functions and schema utilities
import analytics
from schema_utils import initialize_schema_cache, extract_schema_from_docstring, python_type_to_json_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-analytics-server")

# Create server instance
app = Server("mcp-analytics-server")

# Cache for generated schemas - populated once at startup
_schema_cache = {}

def initialize_analytics_schema_cache():
    """Initialize the schema cache at startup to avoid repeated generation."""
    global _schema_cache
    
    # Automatically discover all analytics functions
    all_functions = {}
    
    # Get all callable functions from the analytics module
    for name, obj in inspect.getmembers(analytics):
        if (inspect.isfunction(obj) and 
            not name.startswith('_') and  # Skip private functions
            hasattr(obj, '__module__') and  # Has module info
            obj.__module__ and obj.__module__.startswith('analytics.')):  # From analytics package
            all_functions[name] = obj
    
    logger.info(f"Auto-discovered {len(all_functions)} analytics functions")
    
    # Use shared schema utility
    _schema_cache = initialize_schema_cache(all_functions)



# Register all analytics functions as MCP tools
@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available analytics tools"""
    # Use cached schemas for performance
    tools = []
    
    # Add all analytics function tools
    for func_name, schema in _schema_cache.items():
        # Build Tool with all available schema fields
        tool_kwargs = {
            "name": func_name,
            "description": schema['description'],
            "inputSchema": schema['inputSchema']
        }
        
        # Add title if present
        if 'title' in schema:
            tool_kwargs["title"] = schema['title']
        
        # Add optional fields if present
        if 'outputSchema' in schema:
            tool_kwargs["outputSchema"] = schema['outputSchema']
        
        if 'annotations' in schema:
            tool_kwargs["annotations"] = schema['annotations']
            
        tools.append(types.Tool(**tool_kwargs))
    
    
    logger.debug(f"Returned {len(tools)} analytics tools from cache")
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing analytics tool: {name} with arguments keys: {list(arguments.keys())}")
        
        # Handle analytics functions
        if hasattr(analytics, name):
            # Execute the analytics function
            function = getattr(analytics, name)
            result = function(**arguments)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            # Get all available functions for error message
            available_functions = [n for n, obj in inspect.getmembers(analytics) 
                                 if inspect.isfunction(obj) and not n.startswith('_')]
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown analytics tool: {name}",
                    "available_tools": available_functions
                })
            )]
        
    except Exception as e:
        logger.error(f"Analytics tool execution failed: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Analytics tool execution failed: {str(e)}"
            })
        )]


async def main():
    """Run the MCP Analytics Server"""
    logger.info("Starting MCP Analytics Server...")
    
    # Initialize schema cache once at startup
    initialize_analytics_schema_cache()
    
    logger.info(f"Total functions exposed: {len(_schema_cache)}")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-analytics-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())