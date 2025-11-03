#!/usr/bin/env python3
"""
Simple test MCP server based on official example
"""

import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# Create the server
server = Server("test-financial-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available financial tools"""
    return [
        types.Tool(
            name="alpaca_market_stocks_bars",
            description="Get historical OHLC price bars for stocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {"type": "string", "description": "Comma-separated stock symbols"},
                    "timeframe": {"type": "string", "description": "Time frame (1Day, 1Hour, etc.)"}
                },
                "required": ["symbols"]
            }
        ),
        types.Tool(
            name="alpaca_market_screener_most_actives", 
            description="Get most active stocks by volume",
            inputSchema={
                "type": "object",
                "properties": {
                    "top": {"type": "integer", "description": "Number of top stocks to return"}
                }
            }
        ),
        types.Tool(
            name="calculate_sma",
            description="Calculate simple moving average",
            inputSchema={
                "type": "object", 
                "properties": {
                    "data": {"type": "array", "description": "Price data"},
                    "period": {"type": "integer", "description": "SMA period"}
                },
                "required": ["data", "period"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    if name == "alpaca_market_stocks_bars":
        return [types.TextContent(
            type="text",
            text=f"Mock OHLC data for {arguments.get('symbols', 'AAPL')}"
        )]
    elif name == "alpaca_market_screener_most_actives":
        return [types.TextContent(
            type="text", 
            text=f"Mock top {arguments.get('top', 5)} active stocks"
        )]
    elif name == "calculate_sma":
        return [types.TextContent(
            type="text",
            text=f"Mock SMA calculation for period {arguments.get('period', 20)}"
        )]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server using official pattern"""
    # Use the stdio_server context manager
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="test-financial-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())