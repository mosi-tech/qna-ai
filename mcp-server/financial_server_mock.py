#!/usr/bin/env python3
"""
MCP Financial Server - Mock Implementation

Mock MCP server that provides realistic financial data for development and testing.
Follows exact API specifications without requiring real API keys.
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

# Import mock financial functions and schema utilities
from financial.functions_mock import MOCK_FINANCIAL_FUNCTIONS
from schema_utils import initialize_schema_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-financial-server-mock")

# Create server instance
app = Server("mcp-financial-server-mock")

# Cache for generated schemas - populated once at startup
_schema_cache = {}

# Output schemas for financial functions
OUTPUT_SCHEMAS = {
    "alpaca_trading_positions": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol"},
                "qty": {"type": "number", "description": "Quantity held"},
                "market_value": {"type": "number", "description": "Current market value"},
                "unrealized_pl": {"type": "number", "description": "Unrealized P&L"}
            }
        }
    },
    "alpaca_market_stocks_bars": {
        "type": "object",
        "properties": {
            "bars": {
                "type": "object",
                "description": "OHLC bars by symbol",
                "patternProperties": {
                    "^[A-Z]+$": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "t": {"type": "string", "description": "timestamp"},
                                "o": {"type": "number", "description": "open price"},
                                "h": {"type": "number", "description": "high price"},
                                "l": {"type": "number", "description": "low price"},
                                "c": {"type": "number", "description": "close price"},
                                "v": {"type": "number", "description": "volume"}
                            }
                        }
                    }
                }
            }
        }
    },
    "alpaca_market_stocks_snapshots": {
        "type": "object",
        "properties": {
            "snapshots": {
                "type": "object",
                "patternProperties": {
                    "^[A-Z]+$": {
                        "type": "object",
                        "properties": {
                            "dailyBar": {"type": "object"},
                            "latestQuote": {"type": "object"},
                            "latestTrade": {"type": "object"}
                        }
                    }
                }
            }
        }
    }
}


def _get_output_schema_for_function(func_name: str) -> Dict[str, Any]:
    """Get output schema for specific function"""
    if func_name in OUTPUT_SCHEMAS:
        return OUTPUT_SCHEMAS[func_name]
    elif "positions" in func_name:
        return OUTPUT_SCHEMAS["alpaca_trading_positions"]
    elif "bars" in func_name:
        return OUTPUT_SCHEMAS["alpaca_market_stocks_bars"] 
    elif "snapshots" in func_name:
        return OUTPUT_SCHEMAS["alpaca_market_stocks_snapshots"]
    else:
        return {"type": "object", "description": f"Output from {func_name}"}


def _get_function_parameters(func_name: str) -> Dict[str, Any]:
    """Get parameter definitions for specific function"""
    return {
        "required": [],
        "optional": [],
        "types": {}
    }


@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available financial tools using dynamic schema generation"""
    # Use cached schemas for performance
    tools = []
    
    # Add all financial function tools
    for func_name, schema in _schema_cache.items():
        tools.append(types.Tool(
            name=func_name,
            description=schema['description'],
            inputSchema=schema['inputSchema']
        ))
    
    # Add schema discovery tools for distributed validation
    tools.extend([
        types.Tool(
            name="get_financial_function_schemas",
            description="Get all financial function schemas for workflow validation",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_financial_function_schema",
            description="Get schema for specific financial function",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the financial function to get schema for"
                    }
                },
                "required": ["function_name"],
                "additionalProperties": False
            }
        )
    ])
    
    logger.debug(f"Returned {len(tools)} financial tools from cache (including schema tools)")
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing mock tool: {name} with arguments: {arguments}")
        
        # Handle schema discovery tools
        if name == "get_financial_function_schemas":
            # Return all financial function schemas with output schemas
            schemas_with_output = {}
            for func_name, schema in _schema_cache.items():
                schemas_with_output[func_name] = {
                    "source": "financial",
                    "description": schema["description"],
                    "input_schema": schema["inputSchema"],
                    "output_schema": _get_output_schema_for_function(func_name),
                    "parameters": _get_function_parameters(func_name)
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "functions": schemas_with_output,
                    "count": len(schemas_with_output),
                    "source": "financial",
                    "server": "mcp-financial-server"
                }, indent=2)
            )]
        
        elif name == "get_financial_function_schema":
            function_name = arguments["function_name"]
            if function_name not in _schema_cache:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Function '{function_name}' not found",
                        "available_functions": list(_schema_cache.keys())[:10],
                        "suggestions": [fn for fn in _schema_cache.keys() if function_name.lower() in fn.lower()][:5]
                    })
                )]
            
            schema = _schema_cache[function_name]
            detailed_schema = {
                "function_name": function_name,
                "source": "financial",
                "description": schema["description"],
                "input_schema": schema["inputSchema"],
                "output_schema": _get_output_schema_for_function(function_name),
                "parameters": _get_function_parameters(function_name)
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(detailed_schema, indent=2)
            )]
        
        # Handle regular financial functions
        elif name in MOCK_FINANCIAL_FUNCTIONS:
            # Execute the function
            function = MOCK_FINANCIAL_FUNCTIONS[name]
            result = function(**arguments)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}",
                    "available_tools": list(MOCK_FINANCIAL_FUNCTIONS.keys()) + ["get_financial_function_schemas", "get_financial_function_schema"]
                })
            )]
        
    except Exception as e:
        logger.error(f"Mock tool execution failed: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "tool": name,
                "arguments": arguments
            })
        )]


async def main():
    """Run the MCP Financial Server (Mock)"""
    logger.info("Starting MCP Financial Server (Mock Implementation)...")
    
    # Initialize schema cache once at startup
    global _schema_cache
    _schema_cache = initialize_schema_cache(MOCK_FINANCIAL_FUNCTIONS)
    
    logger.info(f"Total functions exposed: {len(_schema_cache)}")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream,
            InitializationOptions(
                server_name="mcp-financial-server-mock",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())