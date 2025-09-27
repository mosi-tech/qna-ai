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
    
    
    logger.debug(f"Returned {len(tools)} financial tools from cache")
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing mock tool: {name} with arguments: {arguments}")
        
        # Handle financial functions
        if name in MOCK_FINANCIAL_FUNCTIONS:
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
                    "available_tools": list(MOCK_FINANCIAL_FUNCTIONS.keys())
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