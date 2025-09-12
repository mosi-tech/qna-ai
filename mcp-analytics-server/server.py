#!/usr/bin/env python3
"""
MCP Server for Comprehensive Technical Analysis

Exposes 115 professional-grade technical analysis functions through MCP protocol:
- 36 Core Technical Indicators
- 10 Crossover Detection Functions  
- 4 Advanced Pattern Recognition Functions
- 65 Advanced Technical Indicators (Momentum, Trend, Volatility, Statistical, Market Structure, Volume-Price, Cycle Analysis)

All functions follow consistent input/output patterns with professional error handling.
"""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# MCP Protocol imports  
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import our comprehensive analytics system
from analytics.main import analytics_engine
from analytics.technical import get_all_functions, get_function_categories, get_function_count

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-analytics-server")

# Initialize the server
server = Server("mcp-analytics-server")

# Get all available technical analysis functions
all_functions = get_all_functions()
function_categories = get_function_categories()
function_counts = get_function_count()

logger.info(f"🚀 MCP Analytics Server initialized with {len(all_functions)} technical analysis functions")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all 50 technical analysis tools available through MCP."""
    
    tools = []
    
    # Define common price data schema
    price_data_schema = {
        "type": "array",
        "description": "Array of OHLCV price objects",
        "items": {
            "type": "object",
            "properties": {
                "open": {"type": "number", "description": "Opening price"},
                "high": {"type": "number", "description": "High price"},
                "low": {"type": "number", "description": "Low price"},
                "close": {"type": "number", "description": "Closing price"},
                "volume": {"type": "number", "description": "Volume (optional for some indicators)"}
            },
            "required": ["close"]
        },
        "minItems": 10
    }
    
    # Core Indicators - Moving Averages
    tools.extend([
        types.Tool(
            name="sma",
            description="Simple Moving Average - Calculate simple moving average of closing prices",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": price_data_schema,
                    "period": {"type": "integer", "default": 20, "description": "SMA period"},
                    "column": {"type": "string", "default": "close", "description": "Column to use"}
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
                    "data": price_data_schema,
                    "period": {"type": "integer", "default": 20, "description": "EMA period"},
                    "column": {"type": "string", "default": "close", "description": "Column to use"}
                },
                "required": ["data"]
            }
        )
    ])
    
    # Core Indicators - Momentum Oscillators
    momentum_tools = [
        ("rsi", "Relative Strength Index - Momentum oscillator measuring speed and change of price movements (0-100)", {"period": 14}),
        ("stochastic", "Stochastic Oscillator - Compare closing price to price range over time (%K and %D lines)", {"k_period": 14, "d_period": 3}),
        ("stochastic_rsi", "Stochastic RSI - RSI applied to Stochastic formula for enhanced sensitivity", {"period": 14, "smooth_k": 3, "smooth_d": 3}),
        ("williams_r", "Williams %R - Momentum indicator showing overbought/oversold levels (-100 to 0)", {"period": 14}),
        ("cci", "Commodity Channel Index - Identify cyclical trends in securities", {"period": 20}),
        ("money_flow_index", "Money Flow Index - Volume-weighted RSI measuring buying and selling pressure", {"period": 14}),
        ("ultimate_oscillator", "Ultimate Oscillator - Multiple timeframe momentum oscillator", {"short": 7, "medium": 14, "long": 28}),
        ("awesome_oscillator", "Awesome Oscillator - Market momentum indicator using SMA crossover", {"short": 5, "long": 34}),
        ("rate_of_change", "Rate of Change - Momentum indicator measuring percentage change over time", {"period": 12})
    ]
    
    for name, desc, params in momentum_tools:
        schema_props = {"data": price_data_schema}
        schema_props.update({k: {"type": "integer", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"} for k, v in params.items()})
        
        tools.append(types.Tool(
            name=name,
            description=desc,
            inputSchema={
                "type": "object",
                "properties": schema_props,
                "required": ["data"]
            }
        ))
    
    # Core Indicators - Trend Indicators
    trend_tools = [
        ("macd", "MACD - Moving Average Convergence Divergence with signal line and histogram", {"fast": 12, "slow": 26, "signal": 9}),
        ("adx", "Average Directional Index - Measure trend strength with +DI and -DI", {"period": 14}),
        ("trix", "TRIX - Triple Exponential Average rate of change indicator", {"period": 14}),
        ("parabolic_sar", "Parabolic SAR - Stop and Reverse system for trend following", {"step": 0.02, "max_step": 0.2}),
        ("aroon", "Aroon Oscillator - Identify trend changes and strength", {"period": 25}),
        ("mass_index", "Mass Index - Identify potential reversal points using high-low range", {"fast": 9, "slow": 25}),
        ("dpo", "Detrended Price Oscillator - Remove trend to identify cycles", {"period": 20}),
        ("kst", "Know Sure Thing - Momentum oscillator based on ROC smoothed by SMAs", {"r1": 10, "r2": 15, "r3": 20, "r4": 30}),
        ("ichimoku", "Ichimoku Kinko Hyo - Complete trend analysis with cloud and lines", {"tenkan": 9, "kijun": 26, "senkou": 52}),
        ("supertrend", "SuperTrend - Trend following indicator using ATR", {"period": 10, "multiplier": 3.0})
    ]
    
    for name, desc, params in trend_tools:
        schema_props = {"data": price_data_schema}
        for k, v in params.items():
            if isinstance(v, float):
                schema_props[k] = {"type": "number", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
            else:
                schema_props[k] = {"type": "integer", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
        
        tools.append(types.Tool(
            name=name,
            description=desc,
            inputSchema={
                "type": "object",
                "properties": schema_props,
                "required": ["data"]
            }
        ))
    
    # Core Indicators - Volatility Indicators
    volatility_tools = [
        ("bollinger_bands", "Bollinger Bands - Volatility bands with upper, middle, lower, width, and %B", {"period": 20, "std_dev": 2.0}),
        ("atr", "Average True Range - Measure market volatility", {"period": 14}),
        ("keltner_channels", "Keltner Channels - Volatility-based envelopes", {"period": 20, "multiplier": 2.0}),
        ("donchian_channels", "Donchian Channels - Price channel breakout system", {"period": 20})
    ]
    
    for name, desc, params in volatility_tools:
        schema_props = {"data": price_data_schema}
        for k, v in params.items():
            if isinstance(v, float):
                schema_props[k] = {"type": "number", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
            else:
                schema_props[k] = {"type": "integer", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
        
        tools.append(types.Tool(
            name=name,
            description=desc,
            inputSchema={
                "type": "object",
                "properties": schema_props,
                "required": ["data"]
            }
        ))
    
    # Core Indicators - Volume Indicators
    volume_tools = [
        ("obv", "On Balance Volume - Cumulative volume indicator", {}),
        ("vwap", "Volume Weighted Average Price - Average price weighted by volume", {}),
        ("chaikin_money_flow", "Chaikin Money Flow - Money flow over specified period", {"period": 20}),
        ("accumulation_distribution", "Accumulation/Distribution Line - Volume and price analysis", {}),
        ("chaikin_oscillator", "Chaikin Oscillator - Momentum of A/D line", {"fast": 3, "slow": 10}),
        ("volume_sma", "Volume Simple Moving Average - Smooth volume over time", {"period": 20}),
        ("volume_weighted_moving_average", "Volume Weighted Moving Average - Price weighted by volume", {"period": 20}),
        ("ease_of_movement", "Ease of Movement - Relationship between price and volume", {"period": 14}),
        ("force_index", "Force Index - Price change and volume relationship", {"period": 13}),
        ("negative_volume_index", "Negative Volume Index - Track smart money", {}),
        ("positive_volume_index", "Positive Volume Index - Track crowd behavior", {})
    ]
    
    for name, desc, params in volume_tools:
        schema_props = {"data": price_data_schema}
        schema_props.update({k: {"type": "integer", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"} for k, v in params.items()})
        
        tools.append(types.Tool(
            name=name,
            description=desc,
            inputSchema={
                "type": "object",
                "properties": schema_props,
                "required": ["data"]
            }
        ))
    
    # Crossover Detection Functions
    crossover_tools = [
        ("moving_average_crossover", "Moving Average Crossover - Detect Golden Cross and Death Cross signals", {"fast_period": 10, "slow_period": 20, "ma_type": "sma"}),
        ("macd_crossover", "MACD Crossover - MACD line crossing signal line", {"fast": 12, "slow": 26, "signal": 9}),
        ("rsi_level_cross", "RSI Level Cross - RSI crossing overbought/oversold levels", {"period": 14, "overbought": 70, "oversold": 30}),
        ("stochastic_crossover", "Stochastic Crossover - %K and %D line crossovers", {"k_period": 14, "d_period": 3}),
        ("price_channel_breakout", "Price Channel Breakout - Donchian channel breakout detection", {"period": 20}),
        ("bollinger_band_crossover", "Bollinger Band Crossover - Price crossovers with Bollinger Bands", {"period": 20, "std_dev": 2.0}),
        ("adx_directional_crossover", "ADX Directional Crossover - +DI and -DI crossovers for trend changes", {"period": 14}),
        ("price_moving_average_crossover", "Price Moving Average Crossover - Price crossovers above/below single MA", {"period": 20, "ma_type": "sma"}),
        ("zero_line_crossover", "Zero Line Crossover - Oscillator crossovers above/below zero", {"indicator": "macd"}),
        ("multi_timeframe_crossover", "Multi-Timeframe Crossover - 3-MA alignment system", {"fast_period": 5, "medium_period": 10, "slow_period": 20, "ma_type": "ema"})
    ]
    
    for name, desc, params in crossover_tools:
        schema_props = {"data": price_data_schema}
        for k, v in params.items():
            if isinstance(v, str):
                schema_props[k] = {"type": "string", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
            elif isinstance(v, float):
                schema_props[k] = {"type": "number", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
            else:
                schema_props[k] = {"type": "integer", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
        
        tools.append(types.Tool(
            name=name,
            description=desc,
            inputSchema={
                "type": "object",
                "properties": schema_props,
                "required": ["data"]
            }
        ))
    
    # Advanced Pattern Recognition
    pattern_tools = [
        ("bullish_confluence", "Bullish Confluence - Multi-indicator bullish setup detection with scoring", {}),
        ("bearish_confluence", "Bearish Confluence - Multi-indicator bearish setup detection with scoring", {}),
        ("squeeze_pattern", "Squeeze Pattern - Bollinger Band and Keltner Channel squeeze detection", {"bb_period": 20, "kc_period": 20}),
        ("trend_continuation_pattern", "Trend Continuation - Identify trend continuation after pullbacks", {"trend_period": 50, "pullback_period": 10})
    ]
    
    for name, desc, params in pattern_tools:
        schema_props = {"data": price_data_schema}
        schema_props.update({k: {"type": "integer", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"} for k, v in params.items()})
        
        tools.append(types.Tool(
            name=name,
            description=desc,
            inputSchema={
                "type": "object",
                "properties": schema_props,
                "required": ["data"]
            }
        ))
    
    # Advanced Momentum Indicators
    momentum_tools = [
        ("momentum", "Basic Price Momentum - Rate of change over specified period", {"period": 10}),
        ("price_momentum_oscillator", "Normalized Price Momentum - Percentage momentum oscillator", {"period": 10}),
        ("true_strength_index", "True Strength Index - Double-smoothed momentum oscillator", {"long_period": 25, "short_period": 13}),
        ("percentage_price_oscillator", "Percentage Price Oscillator - MACD in percentage terms", {"fast_period": 12, "slow_period": 26}),
        ("elder_ray_index", "Elder Ray Index - Bull/Bear Power relative to EMA", {"period": 13}),
        ("klinger_oscillator", "Klinger Oscillator - Volume-based momentum indicator", {"fast_period": 34, "slow_period": 55, "signal_period": 13}),
        ("stochastic_momentum_index", "Stochastic Momentum Index - Double-smoothed stochastic", {"k_period": 10, "d_period": 3, "k_smooth": 3})
    ]
    
    # Advanced Trend Indicators  
    trend_tools = [
        ("hull_moving_average", "Hull Moving Average - Reduced lag moving average", {"period": 16}),
        ("kaufman_adaptive_moving_average", "Kaufman Adaptive Moving Average - Volatility-adaptive MA", {"period": 10, "fast_sc": 2.0, "slow_sc": 30.0}),
        ("triple_exponential_moving_average", "Triple Exponential Moving Average - Triple smoothed EMA", {"period": 20}),
        ("zero_lag_exponential_moving_average", "Zero Lag Exponential Moving Average - Momentum-adjusted EMA", {"period": 20}),
        ("mcginley_dynamic", "McGinley Dynamic - Market speed adaptive MA", {"period": 14}),
        ("arnaud_legoux_moving_average", "Arnaud Legoux Moving Average - Gaussian-filtered MA", {"period": 21, "offset": 0.85, "sigma": 6.0}),
        ("linear_regression_moving_average", "Linear Regression Moving Average - Regression-based MA", {"period": 14}),
        ("variable_moving_average", "Variable Moving Average - Volatility-based variable MA", {"period": 20})
    ]
    
    # Advanced Volatility Indicators
    volatility_tools = [
        ("standard_deviation", "Rolling Standard Deviation - Price dispersion measure", {"period": 20}),
        ("historical_volatility", "Historical Volatility - Annualized volatility", {"period": 20, "annualize": True}),
        ("garman_klass_volatility", "Garman-Klass Volatility - OHLC-based volatility estimator", {"period": 20, "annualize": True}),
        ("parkinson_volatility", "Parkinson Volatility - High-Low volatility estimator", {"period": 20, "annualize": True}),
        ("rogers_satchell_volatility", "Rogers-Satchell Volatility - Drift-independent volatility", {"period": 20, "annualize": True}),
        ("yang_zhang_volatility", "Yang-Zhang Volatility - Combined overnight/intraday volatility", {"period": 20, "annualize": True}),
        ("relative_volatility_index", "Relative Volatility Index - RSI applied to volatility", {"period": 14}),
        ("volatility_ratio", "Volatility Ratio - Short/long term volatility ratio", {"fast_period": 10, "slow_period": 30}),
        ("volatility_system", "Volatility System - Comprehensive volatility analysis", {"period": 20})
    ]
    
    # Advanced Statistical Indicators
    statistical_tools = [
        ("linear_regression", "Linear Regression - Slope, intercept, R-squared analysis", {"period": 20}),
        ("z_score", "Z-Score - Standard score calculation", {"period": 20}),
        ("skewness", "Rolling Skewness - Distribution asymmetry measure", {"period": 20}),
        ("kurtosis", "Rolling Kurtosis - Distribution tail heaviness", {"period": 20}),
        ("percentile_rank", "Percentile Rank - Current value percentile", {"period": 20}),
        ("sharpe_ratio", "Sharpe Ratio - Risk-adjusted return measure", {"risk_free_rate": 0.02, "period": 60})
    ]
    
    # Market Structure Indicators  
    structure_tools = [
        ("traditional_pivot_points", "Traditional Pivot Points - Classic pivot levels", {}),
        ("fibonacci_pivot_points", "Fibonacci Pivot Points - Fibonacci-based pivot levels", {}),
        ("woodie_pivot_points", "Woodie's Pivot Points - Close-weighted pivot levels", {}),
        ("camarilla_pivot_points", "Camarilla Pivot Points - Intraday-focused pivot levels", {}),
        ("swing_high_low", "Swing High/Low - Swing point detection", {"period": 5}),
        ("support_resistance_levels", "Support/Resistance Levels - Key level identification", {"period": 20, "min_touches": 2, "tolerance": 0.01}),
        ("zigzag_indicator", "ZigZag Indicator - Trend reversal filter", {"threshold": 0.05}),
        ("fractal_analysis", "Fractal Analysis - Williams Fractals detection", {"period": 5})
    ]
    
    # Volume-Price Analysis Indicators
    volume_price_tools = [
        ("volume_rate_of_change", "Volume Rate of Change - Rate of change in volume", {"period": 12}),
        ("price_volume_trend", "Price Volume Trend - Money flow indicator", {}),
        ("volume_oscillator", "Volume Oscillator - Volume moving average relationship", {"fast_period": 5, "slow_period": 10}),
        ("klinger_volume_oscillator", "Klinger Volume Oscillator - Enhanced volume momentum", {"fast_period": 34, "slow_period": 55, "signal_period": 13}),
        ("arms_index", "Arms Index (TRIN) - Trading index indicator", {}),
        ("volume_weighted_rsi", "Volume Weighted RSI - RSI weighted by volume", {"period": 14}),
        ("volume_accumulation_oscillator", "Volume Accumulation Oscillator - Accumulation/distribution", {"period": 14}),
        ("money_flow_oscillator", "Money Flow Oscillator - Money flow momentum", {"period": 10})
    ]
    
    # Cycle Analysis Indicators
    cycle_tools = [
        ("dominant_cycle", "Dominant Cycle - Spectral analysis cycle detection", {"min_period": 8, "max_period": 50}),
        ("cycle_period_detector", "Cycle Period Detector - Autocorrelation cycle detection", {"window_size": 100}),
        ("phase_indicator", "Phase Indicator - Hilbert Transform phase analysis", {"period": 20}),
        ("instantaneous_trendline", "Instantaneous Trendline - MESA adaptive trendline", {"alpha": 0.07}),
        ("cycle_strength_indicator", "Cycle Strength Indicator - Cycle component strength", {"period": 20}),
        ("market_mode_indicator", "Market Mode Indicator - Trending vs cycling mode", {"period": 20})
    ]
    
    # Additional Missing Indicators
    additional_momentum_tools = [
        ("roc_smoothed", "Smoothed Rate of Change - ROC with smoothing", {"period": 12, "smooth_period": 9})
    ]
    
    additional_volatility_tools = [
        ("variance", "Rolling Variance - Price variance measure", {"period": 20}),
        ("vix_style_indicator", "VIX-Style Indicator - Implied volatility-like measure", {"period": 30})
    ]
    
    additional_statistical_tools = [
        ("standard_error_regression", "Standard Error of Regression - Regression accuracy", {"period": 20}),
        ("cointegration_test", "Cointegration Test - Engle-Granger cointegration", {"period": 60}),
        ("hurst_exponent", "Hurst Exponent - Long-term memory measure", {"period": 100}),
        ("t_test_indicator", "T-Test Indicator - Statistical significance test", {"period": 30})
    ]
    
    additional_structure_tools = [
        ("market_profile_basic", "Market Profile Basic - Value area and POC", {"session_hours": 6}),
        ("volume_weighted_average_price_session", "Session VWAP - Session volume weighted price", {"session_length": 390})
    ]
    
    # Add all advanced indicator tools
    all_tool_lists = [
        momentum_tools, trend_tools, volatility_tools, statistical_tools, structure_tools,
        volume_price_tools, cycle_tools, additional_momentum_tools, additional_volatility_tools,
        additional_statistical_tools, additional_structure_tools
    ]
    
    for tool_list in all_tool_lists:
        for name, desc, params in tool_list:
            schema_props = {"data": price_data_schema}
            
            # Add parameters with proper types
            for k, v in params.items():
                if isinstance(v, int):
                    schema_props[k] = {"type": "integer", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
                elif isinstance(v, float):
                    schema_props[k] = {"type": "number", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
                elif isinstance(v, bool):
                    schema_props[k] = {"type": "boolean", "default": v, "description": f"{k.replace('_', ' ').title()} parameter"}
                else:
                    schema_props[k] = {"type": "string", "default": str(v), "description": f"{k.replace('_', ' ').title()} parameter"}
            
            tools.append(types.Tool(
                name=name,
                description=desc,
                inputSchema={
                    "type": "object",
                    "properties": schema_props,
                    "required": ["data"]
                }
            ))
    
    logger.info(f"📊 Exposing {len(tools)} technical analysis tools through MCP")
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute technical analysis functions through MCP."""
    
    try:
        # Validate that the function exists
        if name not in all_functions:
            available_functions = ", ".join(sorted(all_functions))
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Function '{name}' not found. Available functions: {available_functions}",
                    "function": name
                }, indent=2)
            )]
        
        # Extract data and other arguments
        data = arguments.get('data', [])
        function_args = {k: v for k, v in arguments.items() if k != 'data'}
        
        # Validate data
        if not data:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "No data provided",
                    "function": name
                }, indent=2)
            )]
        
        # Execute the function using our analytics engine
        result = analytics_engine.execute_function(name, data=data, **function_args)
        
        # Add execution metadata
        result['mcp_execution'] = {
            'function_name': name,
            'timestamp': datetime.now().isoformat(),
            'server': 'mcp-analytics-server',
            'data_points': len(data)
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"Error executing function {name}: {str(e)}")
        return [types.TextContent(
            type="text", 
            text=json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}",
                "function": name,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        )]


async def main():
    """Run the MCP server."""
    logger.info("🚀 Starting MCP Analytics Server")
    logger.info(f"📊 Available Functions: {function_counts['total']}")
    logger.info(f"   - Core Indicators: {function_counts['core_indicators']}")
    logger.info(f"   - Crossover Detection: {function_counts['crossovers']}")
    logger.info(f"   - Pattern Recognition: {function_counts['patterns']}")
    logger.info(f"   - Advanced Indicators: {function_counts['advanced_indicators']}")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-analytics-server",
                server_version="2.0.0",
                capabilities=types.ServerCapabilities(
                    tools=types.ToolsCapability()
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())