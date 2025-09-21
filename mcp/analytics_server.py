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
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import analytics functions
from analytics.indicators.technical import TECHNICAL_INDICATORS_FUNCTIONS
from analytics.portfolio.metrics import PORTFOLIO_ANALYSIS_FUNCTIONS
from analytics.performance.metrics import PERFORMANCE_METRICS_FUNCTIONS
from analytics.risk.metrics import RISK_METRICS_FUNCTIONS
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
    
    # Combine all analytics function registries
    all_functions = {
        **TECHNICAL_INDICATORS_FUNCTIONS,
        **PORTFOLIO_ANALYSIS_FUNCTIONS, 
        **PERFORMANCE_METRICS_FUNCTIONS,
        **RISK_METRICS_FUNCTIONS,
        **DATA_UTILS_FUNCTIONS
    }
    
    # Generate tools dynamically from all available functions
    function_schemas = {
        # Technical Indicators
        "calculate_sma": {
            "description": "Simple Moving Average - Calculate simple moving average of closing prices",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "description": "Price data array"},
                    "period": {"type": "integer", "default": 20}
                },
                "required": ["data"]
            }
        },
        "calculate_ema": {
            "description": "Exponential Moving Average - Calculate exponential moving average",
            "inputSchema": {
                "type": "object", 
                "properties": {
                    "data": {"type": "array", "description": "Price data array"},
                    "period": {"type": "integer", "default": 20}
                },
                "required": ["data"]
            }
        },
        "calculate_rsi": {
            "description": "Relative Strength Index - Momentum oscillator (0-100)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "description": "Price data array"},
                    "period": {"type": "integer", "default": 14}
                },
                "required": ["data"]
            }
        },
        "calculate_macd": {
            "description": "MACD - Moving Average Convergence Divergence",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "description": "Price data array"},
                    "fast_period": {"type": "integer", "default": 12},
                    "slow_period": {"type": "integer", "default": 26},
                    "signal_period": {"type": "integer", "default": 9}
                },
                "required": ["data"]
            }
        },
        "calculate_bollinger_bands": {
            "description": "Bollinger Bands - Volatility bands analysis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "description": "Price data array"},
                    "period": {"type": "integer", "default": 20},
                    "std_dev": {"type": "number", "default": 2.0}
                },
                "required": ["data"]
            }
        },
        "calculate_atr": {
            "description": "Average True Range - Measure market volatility",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "description": "OHLC data array"},
                    "period": {"type": "integer", "default": 14}
                },
                "required": ["data"]
            }
        },
        "calculate_stochastic": {
            "description": "Stochastic Oscillator - %K and %D momentum indicators",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {"type": "array", "description": "OHLC data array"},
                    "k_period": {"type": "integer", "default": 14},
                    "d_period": {"type": "integer", "default": 3}
                },
                "required": ["data"]
            }
        },
        "detect_sma_crossover": {
            "description": "Detect SMA crossover signals for trend analysis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prices": {"type": "array", "description": "Price data array"},
                    "fast_period": {"type": "integer", "default": 20},
                    "slow_period": {"type": "integer", "default": 50}
                },
                "required": ["prices"]
            }
        },
        "detect_ema_crossover": {
            "description": "Detect EMA crossover signals for trend analysis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prices": {"type": "array", "description": "Price data array"},
                    "fast_period": {"type": "integer", "default": 12},
                    "slow_period": {"type": "integer", "default": 26}
                },
                "required": ["prices"]
            }
        },
        # Portfolio Analysis
        "calculate_portfolio_metrics": {
            "description": "Comprehensive portfolio metrics including returns, risk, and Sharpe ratio",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "weights": {"type": "array", "description": "Portfolio weights"},
                    "returns": {"type": "array", "description": "Asset returns matrix"},
                    "benchmark_returns": {"type": "array", "description": "Benchmark returns (optional)"},
                    "risk_free_rate": {"type": "number", "default": 0.02}
                },
                "required": ["weights", "returns"]
            }
        },
        "analyze_portfolio_concentration": {
            "description": "Analyze portfolio concentration and diversification metrics",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "weights": {"type": "array", "description": "Portfolio weights"},
                    "asset_names": {"type": "array", "description": "Asset names (optional)"}
                },
                "required": ["weights"]
            }
        },
        "calculate_portfolio_beta": {
            "description": "Calculate portfolio beta using individual asset betas",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "weights": {"type": "array", "description": "Portfolio weights"},
                    "asset_betas": {"type": "array", "description": "Individual asset betas"}
                },
                "required": ["weights", "asset_betas"]
            }
        },
        "calculate_active_share": {
            "description": "Calculate active share vs benchmark portfolio",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "portfolio_weights": {"type": "array", "description": "Portfolio weights"},
                    "benchmark_weights": {"type": "array", "description": "Benchmark weights"},
                    "asset_names": {"type": "array", "description": "Asset names (optional)"}
                },
                "required": ["portfolio_weights", "benchmark_weights"]
            }
        },
        "calculate_portfolio_var": {
            "description": "Calculate portfolio Value at Risk using covariance matrix",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "weights": {"type": "array", "description": "Portfolio weights"},
                    "covariance_matrix": {"type": "array", "description": "Asset covariance matrix"},
                    "confidence": {"type": "number", "default": 0.05},
                    "time_horizon": {"type": "integer", "default": 1}
                },
                "required": ["weights", "covariance_matrix"]
            }
        },
        "stress_test_portfolio": {
            "description": "Perform portfolio stress testing under various scenarios",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "weights": {"type": "array", "description": "Portfolio weights"},
                    "returns": {"type": "array", "description": "Historical asset returns"},
                    "scenarios": {"type": "array", "description": "Custom stress scenarios (optional)"}
                },
                "required": ["weights", "returns"]
            }
        },
        # Performance Metrics
        "calculate_returns_metrics": {
            "description": "Calculate comprehensive return metrics including total and annual returns",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "returns": {"type": "array", "description": "Return series"}
                },
                "required": ["returns"]
            }
        },
        "calculate_risk_metrics": {
            "description": "Calculate comprehensive risk metrics including volatility, Sharpe, Sortino",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "returns": {"type": "array", "description": "Return series"},
                    "risk_free_rate": {"type": "number", "default": 0.02}
                },
                "required": ["returns"]
            }
        },
        "calculate_benchmark_metrics": {
            "description": "Calculate benchmark comparison metrics including alpha and beta",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "returns": {"type": "array", "description": "Portfolio returns"},
                    "benchmark_returns": {"type": "array", "description": "Benchmark returns"},
                    "risk_free_rate": {"type": "number", "default": 0.02}
                },
                "required": ["returns", "benchmark_returns"]
            }
        },
        "calculate_drawdown_analysis": {
            "description": "Calculate detailed drawdown analysis and recovery periods",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "returns": {"type": "array", "description": "Return series"}
                },
                "required": ["returns"]
            }
        },
        # Risk Metrics
        "calculate_var": {
            "description": "Calculate Value at Risk using multiple methods",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "returns": {"type": "array", "description": "Return series"},
                    "confidence_level": {"type": "number", "default": 0.05},
                    "method": {"type": "string", "default": "historical"}
                },
                "required": ["returns"]
            }
        },
        "calculate_cvar": {
            "description": "Calculate Conditional Value at Risk (Expected Shortfall)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "returns": {"type": "array", "description": "Return series"},
                    "confidence_level": {"type": "number", "default": 0.05}
                },
                "required": ["returns"]
            }
        },
        "calculate_correlation_analysis": {
            "description": "Calculate correlation analysis for multiple assets",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "returns": {"type": "array", "description": "Multi-asset return matrix"},
                    "method": {"type": "string", "default": "pearson"}
                },
                "required": ["returns"]
            }
        },
        "calculate_beta_analysis": {
            "description": "Calculate comprehensive beta analysis vs market",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "asset_returns": {"type": "array", "description": "Asset return series"},
                    "market_returns": {"type": "array", "description": "Market return series"},
                    "risk_free_rate": {"type": "number", "default": 0.02}
                },
                "required": ["asset_returns", "market_returns"]
            }
        }
    }
    
    # Create tools for available functions
    for func_name, func in all_functions.items():
        if func_name in function_schemas:
            schema = function_schemas[func_name]
            tools.append(types.Tool(
                name=func_name,
                description=schema['description'],
                inputSchema=schema["inputSchema"]
            ))
    
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing analytics tool: {name} with arguments keys: {list(arguments.keys())}")
        
        # Combine all analytics function registries
        all_functions = {
            **TECHNICAL_INDICATORS_FUNCTIONS,
            **PORTFOLIO_ANALYSIS_FUNCTIONS, 
            **PERFORMANCE_METRICS_FUNCTIONS,
            **RISK_METRICS_FUNCTIONS,
            **DATA_UTILS_FUNCTIONS
        }
        
        if name not in all_functions:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown analytics tool: {name}",
                    "available_tools": list(all_functions.keys())
                })
            )]
        
        # Execute the analytics function
        function = all_functions[name]
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
    # Combine all function registries for logging
    all_functions = {
        **TECHNICAL_INDICATORS_FUNCTIONS,
        **PORTFOLIO_ANALYSIS_FUNCTIONS, 
        **PERFORMANCE_METRICS_FUNCTIONS,
        **RISK_METRICS_FUNCTIONS,
        **DATA_UTILS_FUNCTIONS
    }
    logger.info(f"Available analytics functions: {list(all_functions.keys())}")
    logger.info(f"Total functions exposed: {len(all_functions)}")
    
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