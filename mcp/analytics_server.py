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
from typing import Dict, List, Any, Optional

# MCP Server Framework
from mcp import server, get_model_name
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import analytics functions
from analytics.indicators.technical import (
    calculate_sma, calculate_ema, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_stochastic, calculate_atr,
    TECHNICAL_INDICATORS_FUNCTIONS
)
from analytics.utils.data_utils import DATA_UTILS_FUNCTIONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-analytics-server")

# Create server instance
app = Server("mcp-analytics-server")

# Register all analytics functions as MCP tools
@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available analytics tools"""
    tools = []
    
    # Technical Indicators
    tools.extend([
        types.Tool(
            name="sma",
            description="Simple Moving Average - Calculate simple moving average of closing prices",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Array of OHLCV price objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "close": {"type": "number", "description": "Closing price"},
                                "high": {"type": "number", "description": "High price"},
                                "low": {"type": "number", "description": "Low price"},
                                "open": {"type": "number", "description": "Opening price"},
                                "volume": {"type": "number", "description": "Volume (optional)"}
                            },
                            "required": ["close"]
                        },
                        "minItems": 10
                    },
                    "period": {
                        "type": "integer",
                        "description": "SMA period",
                        "default": 20
                    },
                    "column": {
                        "type": "string",
                        "description": "Column to use",
                        "default": "close"
                    }
                },
                "required": ["data"]
            }
        ),
        types.Tool(
            name="ema",
            description="Exponential Moving Average - Calculate exponential moving average with greater weight on recent prices",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Array of OHLCV price objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "close": {"type": "number", "description": "Closing price"},
                                "high": {"type": "number", "description": "High price"},
                                "low": {"type": "number", "description": "Low price"},
                                "open": {"type": "number", "description": "Opening price"},
                                "volume": {"type": "number", "description": "Volume (optional)"}
                            },
                            "required": ["close"]
                        },
                        "minItems": 10
                    },
                    "period": {
                        "type": "integer",
                        "description": "EMA period",
                        "default": 20
                    },
                    "column": {
                        "type": "string",
                        "description": "Column to use",
                        "default": "close"
                    }
                },
                "required": ["data"]
            }
        ),
        types.Tool(
            name="rsi",
            description="Relative Strength Index - Momentum oscillator measuring speed and change of price movements (0-100)",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Array of OHLCV price objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "close": {"type": "number", "description": "Closing price"},
                                "high": {"type": "number", "description": "High price"},
                                "low": {"type": "number", "description": "Low price"},
                                "open": {"type": "number", "description": "Opening price"},
                                "volume": {"type": "number", "description": "Volume (optional)"}
                            },
                            "required": ["close"]
                        },
                        "minItems": 10
                    },
                    "period": {
                        "type": "integer",
                        "description": "Period parameter",
                        "default": 14
                    }
                },
                "required": ["data"]
            }
        ),
        types.Tool(
            name="macd",
            description="MACD - Moving Average Convergence Divergence with signal line and histogram",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Array of OHLCV price objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "close": {"type": "number", "description": "Closing price"},
                                "high": {"type": "number", "description": "High price"},
                                "low": {"type": "number", "description": "Low price"},
                                "open": {"type": "number", "description": "Opening price"},
                                "volume": {"type": "number", "description": "Volume (optional)"}
                            },
                            "required": ["close"]
                        },
                        "minItems": 10
                    },
                    "fast": {
                        "type": "integer",
                        "description": "Fast parameter",
                        "default": 12
                    },
                    "slow": {
                        "type": "integer",
                        "description": "Slow parameter", 
                        "default": 26
                    },
                    "signal": {
                        "type": "integer",
                        "description": "Signal parameter",
                        "default": 9
                    }
                },
                "required": ["data"]
            }
        ),
        types.Tool(
            name="bollinger_bands",
            description="Bollinger Bands - Volatility bands with upper, middle, lower, width, and %B",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Array of OHLCV price objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "close": {"type": "number", "description": "Closing price"},
                                "high": {"type": "number", "description": "High price"},
                                "low": {"type": "number", "description": "Low price"},
                                "open": {"type": "number", "description": "Opening price"},
                                "volume": {"type": "number", "description": "Volume (optional)"}
                            },
                            "required": ["close"]
                        },
                        "minItems": 10
                    },
                    "period": {
                        "type": "integer",
                        "description": "Period parameter",
                        "default": 20
                    },
                    "std_dev": {
                        "type": "number",
                        "description": "Std Dev parameter",
                        "default": 2
                    }
                },
                "required": ["data"]
            }
        ),
        types.Tool(
            name="atr",
            description="Average True Range - Measure market volatility",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Array of OHLCV price objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "close": {"type": "number", "description": "Closing price"},
                                "high": {"type": "number", "description": "High price"},
                                "low": {"type": "number", "description": "Low price"},
                                "open": {"type": "number", "description": "Opening price"},
                                "volume": {"type": "number", "description": "Volume (optional)"}
                            },
                            "required": ["close"]
                        },
                        "minItems": 10
                    },
                    "period": {
                        "type": "integer",
                        "description": "Period parameter",
                        "default": 14
                    }
                },
                "required": ["data"]
            }
        )
    ])
    
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing analytics tool: {name} with arguments keys: {list(arguments.keys())}")
        
        # Map MCP tool names to Python function names
        function_map = {
            "sma": "calculate_sma",
            "ema": "calculate_ema",
            "rsi": "calculate_rsi",
            "macd": "calculate_macd",
            "bollinger_bands": "calculate_bollinger_bands",
            "stochastic": "calculate_stochastic",
            "atr": "calculate_atr"
        }
        
        if name not in function_map:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown analytics tool: {name}"
                })
            )]
        
        function_name = function_map[name]
        
        if function_name not in TECHNICAL_INDICATORS_FUNCTIONS:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Analytics function not found: {function_name}"
                })
            )]
        
        # Execute the analytics function
        function = TECHNICAL_INDICATORS_FUNCTIONS[function_name]
        result = function(**arguments)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
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
    logger.info(f"Available analytics functions: {list(TECHNICAL_INDICATORS_FUNCTIONS.keys())}")
    
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