#!/usr/bin/env python3
"""
MCP Financial Server - Unified Implementation

Python-based MCP server that provides financial data from multiple APIs:
- Alpaca Trading API  
- Alpaca Market Data API
- EODHD API

Supports both mock (for development) and real (for production) implementations.
Set USE_MOCK_FINANCIAL_DATA=false to use real APIs with credentials.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional

# MCP Server Framework
from mcp import server, get_model_name
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import financial functions
from financial import FINANCIAL_FUNCTIONS, IMPLEMENTATION, USE_MOCK

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-financial-server")

# Create server instance
app = Server("mcp-financial-server")


@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available financial tools dynamically based on implementation"""
    tools = []
    
    # Generate tools dynamically from available functions
    function_schemas = {
        # EODHD API
        "eodhd_eod_data": {
            "description": "End-of-day historical OHLC prices with adjustments",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL.US)", "default": "AAPL.US"},
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "period": {"type": "string", "enum": ["d", "w", "m"], "default": "d"},
                    "order": {"type": "string", "enum": ["a", "d"], "default": "a"}
                },
                "required": ["symbol"]
            }
        },
        "eodhd_real_time": {
            "description": "Real-time stock prices and market data",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL.US)", "default": "AAPL.US"},
                    "fmt": {"type": "string", "default": "json"}
                },
                "required": ["symbol"]
            }
        },
        "eodhd_fundamentals": {
            "description": "Company fundamental data, financials, ratios",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL.US)", "default": "AAPL.US"}
                },
                "required": ["symbol"]
            }
        },
        "eodhd_dividends": {
            "description": "Dividend payment history with ex-dates",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL.US)", "default": "AAPL.US"},
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["symbol"]
            }
        },
        "eodhd_screener": {
            "description": "Stock screener with custom filters",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filters": {"type": "string", "description": "Screening filters"},
                    "limit": {"type": "integer", "default": 50},
                    "offset": {"type": "integer", "default": 0},
                    "signals": {"type": "string", "description": "Trading signals"}
                },
                "required": []
            }
        },
        # Alpaca Trading API
        "alpaca_trading_account": {
            "description": "Get account information including buying power, equity, cash balance",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "alpaca_trading_positions": {
            "description": "Get all open positions with P&L, market values, quantities",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "alpaca_trading_position": {
            "description": "Get specific position details for one symbol",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol", "default": "AAPL"}
                },
                "required": ["symbol"]
            }
        },
        # Alpaca Market Data API
        "alpaca_market_stocks_bars": {
            "description": "Historical OHLC price bars for stocks",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbols": {"type": "string", "description": "Comma-separated symbols", "default": "AAPL,TSLA"},
                    "timeframe": {"type": "string", "enum": ["1Day", "1Hour", "1Min"], "default": "1Day"},
                    "start": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["symbols"]
            }
        },
        "alpaca_market_stocks_snapshots": {
            "description": "Current market snapshot with all data",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbols": {"type": "string", "description": "Comma-separated symbols", "default": "AAPL,SPY"}
                },
                "required": ["symbols"]
            }
        },
        "alpaca_market_screener_most_actives": {
            "description": "Screen for most active stocks by volume",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "top": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    }
    
    # Create tools for available functions
    for func_name, func in FINANCIAL_FUNCTIONS.items():
        if func_name in function_schemas:
            schema = function_schemas[func_name]
            tools.append(types.Tool(
                name=func_name,
                description=f"{schema['description']} [{IMPLEMENTATION}]",
                inputSchema=schema["inputSchema"]
            ))
    
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing tool ({IMPLEMENTATION}): {name} with arguments: {arguments}")
        
        if name not in FINANCIAL_FUNCTIONS:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}",
                    "implementation": IMPLEMENTATION,
                    "available_tools": list(FINANCIAL_FUNCTIONS.keys())
                })
            )]
        
        # Execute the function
        function = FINANCIAL_FUNCTIONS[name]
        result = function(**arguments)
        
        # Add metadata about implementation
        if isinstance(result, dict) and "error" not in result:
            result["_meta"] = {
                "implementation": IMPLEMENTATION,
                "use_mock": USE_MOCK,
                "function": name
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "implementation": IMPLEMENTATION,
                "tool": name,
                "arguments": arguments
            })
        )]


async def main():
    """Run the MCP Financial Server"""
    logger.info("Starting MCP Financial Server...")
    logger.info(f"Implementation: {IMPLEMENTATION}")
    logger.info(f"Use mock data: {USE_MOCK}")
    logger.info(f"Available functions: {list(FINANCIAL_FUNCTIONS.keys())}")
    
    server_name = f"mcp-financial-server-{IMPLEMENTATION}"
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream,
            InitializationOptions(
                server_name=server_name,
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())