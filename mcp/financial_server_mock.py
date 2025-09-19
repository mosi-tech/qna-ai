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
from mcp import server, get_model_name
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import mock financial functions
from financial.functions_mock import MOCK_FINANCIAL_FUNCTIONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-financial-server-mock")

# Create server instance
app = Server("mcp-financial-server-mock")


@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available financial tools"""
    tools = []
    
    # EODHD API Tools
    tools.extend([
        types.Tool(
            name="eodhd_eod_data",
            description="End-of-day historical OHLC prices with adjustments",
            inputSchema={
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
        ),
        types.Tool(
            name="eodhd_real_time",
            description="Real-time stock prices and market data",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL.US)", "default": "AAPL.US"},
                    "fmt": {"type": "string", "default": "json"}
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="eodhd_fundamentals",
            description="Company fundamental data, financials, ratios",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL.US)", "default": "AAPL.US"}
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="eodhd_dividends",
            description="Dividend payment history with ex-dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL.US)", "default": "AAPL.US"},
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="eodhd_screener",
            description="Stock screener with custom filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {"type": "string", "description": "Screening filters"},
                    "limit": {"type": "integer", "default": 50},
                    "offset": {"type": "integer", "default": 0},
                    "signals": {"type": "string", "description": "Trading signals"}
                },
                "required": []
            }
        )
    ])
    
    # Alpaca Trading API Tools
    tools.extend([
        types.Tool(
            name="alpaca_trading_account",
            description="Get account information including buying power, equity, cash balance",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        types.Tool(
            name="alpaca_trading_positions",
            description="Get all open positions with P&L, market values, quantities",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        types.Tool(
            name="alpaca_trading_position",
            description="Get specific position details for one symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol", "default": "AAPL"}
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="alpaca_trading_orders",
            description="Get order history and status",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["open", "closed", "canceled", "filled"], "default": "open"},
                    "limit": {"type": "integer", "default": 100},
                    "direction": {"type": "string", "enum": ["asc", "desc"], "default": "desc"}
                },
                "required": []
            }
        ),
        types.Tool(
            name="alpaca_trading_portfolio_history",
            description="Portfolio performance history showing value changes over time",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {"type": "string", "enum": ["1D", "7D", "1M", "3M", "12M"], "default": "1D"},
                    "timeframe": {"type": "string", "enum": ["1Min", "5Min", "15Min", "1H", "1D"], "default": "15Min"}
                },
                "required": []
            }
        )
    ])
    
    # Alpaca Market Data API Tools
    tools.extend([
        types.Tool(
            name="alpaca_market_stocks_bars",
            description="Historical OHLC price bars for stocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {"type": "string", "description": "Comma-separated symbols", "default": "AAPL,TSLA"},
                    "timeframe": {"type": "string", "enum": ["1Day", "1Hour", "1Min"], "default": "1Day"},
                    "start": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["symbols"]
            }
        ),
        types.Tool(
            name="alpaca_market_stocks_snapshots",
            description="Current market snapshot with all data",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {"type": "string", "description": "Comma-separated symbols", "default": "AAPL,SPY"}
                },
                "required": ["symbols"]
            }
        ),
        types.Tool(
            name="alpaca_market_screener_most_actives",
            description="Screen for most active stocks by volume",
            inputSchema={
                "type": "object",
                "properties": {
                    "top": {"type": "integer", "default": 10}
                },
                "required": []
            }
        ),
        types.Tool(
            name="alpaca_market_screener_top_gainers",
            description="Screen for biggest stock gainers",
            inputSchema={
                "type": "object",
                "properties": {
                    "top": {"type": "integer", "default": 10}
                },
                "required": []
            }
        ),
        types.Tool(
            name="alpaca_market_screener_top_losers",
            description="Screen for biggest stock losers",
            inputSchema={
                "type": "object",
                "properties": {
                    "top": {"type": "integer", "default": 10}
                },
                "required": []
            }
        )
    ])
    
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing mock tool: {name} with arguments: {arguments}")
        
        if name not in MOCK_FINANCIAL_FUNCTIONS:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}",
                    "available_tools": list(MOCK_FINANCIAL_FUNCTIONS.keys())
                })
            )]
        
        # Execute the function
        function = MOCK_FINANCIAL_FUNCTIONS[name]
        result = function(**arguments)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
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
    logger.info(f"Available functions: {list(MOCK_FINANCIAL_FUNCTIONS.keys())}")
    
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