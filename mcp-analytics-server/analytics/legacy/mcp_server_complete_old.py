#!/usr/bin/env python3
"""
Complete MCP Server with all technical analysis functions properly exposed.
This file integrates all technical analysis capabilities with comprehensive MCP support.
"""

import asyncio
import json
import sys
import logging
from typing import Dict, List, Any, Optional, Union
from mcp.server.models import InitializeResult, ServerCapabilities
from mcp.server import McpServer, NotificationOptions
from mcp.server.models import CallToolResult
from mcp.types import Tool, TextContent

# Import all technical analysis modules
from .technical.mcp_technical_complete import (
    calculate_rsi_complete, calculate_macd_complete, calculate_stochastic_complete,
    calculate_adx_complete, calculate_bollinger_bands_complete, calculate_atr_complete,
    calculate_obv_complete, calculate_mfi_complete, get_all_technical_functions, 
    get_function_schemas
)
from .technical.technical_analysis_consolidated import (
    calculate_standard_indicators, calculate_price_patterns, 
    standardize_technical_response
)
from .technical.complete_ta_resilient import (
    calculate_williams_r, calculate_awesome_oscillator, calculate_ultimate_oscillator,
    calculate_rate_of_change, calculate_commodity_channel_index, calculate_aroon,
    calculate_parabolic_sar, calculate_keltner_channels, calculate_donchian_channels,
    calculate_accumulation_distribution, calculate_chaikin_money_flow
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = McpServer("mcp-analytics-server")

class TechnicalAnalyticsMCPServer:
    """
    Complete MCP server for technical analysis with all indicators and patterns.
    """
    
    def __init__(self):
        """Initialize the MCP server with all technical analysis functions."""
        self.technical_functions = get_all_technical_functions()
        self.function_schemas = get_function_schemas()
        
        # Add complete TA resilient functions
        self.technical_functions.update({
            'calculate_williams_r': calculate_williams_r,
            'calculate_awesome_oscillator': calculate_awesome_oscillator,
            'calculate_ultimate_oscillator': calculate_ultimate_oscillator,
            'calculate_rate_of_change': calculate_rate_of_change,
            'calculate_commodity_channel_index': calculate_commodity_channel_index,
            'calculate_aroon': calculate_aroon,
            'calculate_parabolic_sar': calculate_parabolic_sar,
            'calculate_keltner_channels': calculate_keltner_channels,
            'calculate_donchian_channels': calculate_donchian_channels,
            'calculate_accumulation_distribution': calculate_accumulation_distribution,
            'calculate_chaikin_money_flow': calculate_chaikin_money_flow,
            
            # Consolidated functions
            'calculate_standard_indicators': calculate_standard_indicators,
            'calculate_price_patterns': calculate_price_patterns,
            'standardize_technical_response': standardize_technical_response,
        })
        
        self._register_tools()
    
    def _register_tools(self):
        """Register all technical analysis tools with the MCP server."""
        
        # Core Technical Indicators
        @server.call_tool()
        async def calculate_rsi_complete(data: Union[List, Dict], window: int = 14) -> List[TextContent]:
            """Calculate RSI with comprehensive analysis including divergences and overbought/oversold signals."""
            try:
                result = self.technical_functions['calculate_rsi_complete'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_rsi_complete: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_macd_complete(data: Union[List, Dict], fast: int = 12, slow: int = 26, signal: int = 9) -> List[TextContent]:
            """Calculate MACD with crossovers, histogram analysis, and zero line analysis."""
            try:
                result = self.technical_functions['calculate_macd_complete'](data, fast, slow, signal)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_macd_complete: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_bollinger_bands_complete(data: Union[List, Dict], window: int = 20, window_dev: int = 2) -> List[TextContent]:
            """Calculate Bollinger Bands with squeeze analysis, walks, and volatility breakout signals."""
            try:
                result = self.technical_functions['calculate_bollinger_bands_complete'](data, window, window_dev)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_bollinger_bands_complete: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_stochastic_complete(data: Union[List, Dict], k_window: int = 14, d_window: int = 3, smooth_k: int = 3) -> List[TextContent]:
            """Calculate Stochastic Oscillator with crossovers and divergence analysis."""
            try:
                result = self.technical_functions['calculate_stochastic_complete'](data, k_window, d_window, smooth_k)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_stochastic_complete: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_adx_complete(data: Union[List, Dict], window: int = 14) -> List[TextContent]:
            """Calculate ADX with trend strength analysis and directional indicator crossovers."""
            try:
                result = self.technical_functions['calculate_adx_complete'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_adx_complete: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_atr_complete(data: Union[List, Dict], window: int = 14) -> List[TextContent]:
            """Calculate ATR with volatility regime analysis and breakout detection."""
            try:
                result = self.technical_functions['calculate_atr_complete'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_atr_complete: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_obv_complete(data: Union[List, Dict]) -> List[TextContent]:
            """Calculate On-Balance Volume with trend analysis and price-volume divergences."""
            try:
                result = self.technical_functions['calculate_obv_complete'](data)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_obv_complete: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_mfi_complete(data: Union[List, Dict], window: int = 14) -> List[TextContent]:
            """Calculate Money Flow Index with volume-price analysis and money flow ratios."""
            try:
                result = self.technical_functions['calculate_mfi_complete'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_mfi_complete: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        # Additional Technical Indicators
        @server.call_tool()
        async def calculate_williams_r(data: Union[List, Dict], window: int = 14) -> List[TextContent]:
            """Calculate Williams %R oscillator with overbought/oversold analysis."""
            try:
                result = self.technical_functions['calculate_williams_r'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_williams_r: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_awesome_oscillator(data: Union[List, Dict], short_window: int = 5, long_window: int = 34) -> List[TextContent]:
            """Calculate Awesome Oscillator with momentum and saucer signal analysis."""
            try:
                result = self.technical_functions['calculate_awesome_oscillator'](data, short_window, long_window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_awesome_oscillator: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_ultimate_oscillator(data: Union[List, Dict], short: int = 7, medium: int = 14, long: int = 28) -> List[TextContent]:
            """Calculate Ultimate Oscillator with multi-timeframe momentum analysis."""
            try:
                result = self.technical_functions['calculate_ultimate_oscillator'](data, short, medium, long)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_ultimate_oscillator: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_commodity_channel_index(data: Union[List, Dict], window: int = 20) -> List[TextContent]:
            """Calculate Commodity Channel Index with overbought/oversold and trend analysis."""
            try:
                result = self.technical_functions['calculate_commodity_channel_index'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_commodity_channel_index: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_aroon(data: Union[List, Dict], window: int = 25) -> List[TextContent]:
            """Calculate Aroon indicators with trend identification and crossover analysis."""
            try:
                result = self.technical_functions['calculate_aroon'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_aroon: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_parabolic_sar(data: Union[List, Dict], step: float = 0.02, max_step: float = 0.2) -> List[TextContent]:
            """Calculate Parabolic SAR with trend following and reversal signals."""
            try:
                result = self.technical_functions['calculate_parabolic_sar'](data, step, max_step)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_parabolic_sar: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_keltner_channels(data: Union[List, Dict], window: int = 20, atr_window: int = 10, multiplier: float = 2.0) -> List[TextContent]:
            """Calculate Keltner Channels with breakout and squeeze analysis."""
            try:
                result = self.technical_functions['calculate_keltner_channels'](data, window, atr_window, multiplier)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_keltner_channels: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_donchian_channels(data: Union[List, Dict], window: int = 20) -> List[TextContent]:
            """Calculate Donchian Channels with breakout analysis and trend following signals."""
            try:
                result = self.technical_functions['calculate_donchian_channels'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_donchian_channels: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        # Volume Indicators
        @server.call_tool()
        async def calculate_accumulation_distribution(data: Union[List, Dict]) -> List[TextContent]:
            """Calculate Accumulation/Distribution line with volume-price analysis."""
            try:
                result = self.technical_functions['calculate_accumulation_distribution'](data)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_accumulation_distribution: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_chaikin_money_flow(data: Union[List, Dict], window: int = 20) -> List[TextContent]:
            """Calculate Chaikin Money Flow with buying/selling pressure analysis."""
            try:
                result = self.technical_functions['calculate_chaikin_money_flow'](data, window)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_chaikin_money_flow: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        # Consolidated Analysis Functions
        @server.call_tool()
        async def calculate_standard_indicators(data: Union[List, Dict], indicators: Optional[List[str]] = None) -> List[TextContent]:
            """Calculate multiple standard technical indicators in one optimized function."""
            try:
                result = self.technical_functions['calculate_standard_indicators'](data, indicators)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_standard_indicators: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def calculate_price_patterns(data: Union[List, Dict], pattern_types: Optional[List[str]] = None) -> List[TextContent]:
            """Detect common price patterns including support/resistance, gaps, and breakouts."""
            try:
                result = self.technical_functions['calculate_price_patterns'](data, pattern_types)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in calculate_price_patterns: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        @server.call_tool()
        async def comprehensive_technical_analysis(data: Union[List, Dict], 
                                                 indicators: Optional[List[str]] = None,
                                                 patterns: Optional[List[str]] = None) -> List[TextContent]:
            """Generate comprehensive technical analysis combining indicators, patterns, and trading signals."""
            try:
                result = standardize_technical_response(
                    "comprehensive_technical_analysis", 
                    data, 
                    indicators, 
                    patterns
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in comprehensive_technical_analysis: {str(e)}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    def get_available_tools(self) -> List[Tool]:
        """Get list of all available tools for MCP client discovery."""
        tools = []
        
        # Core momentum indicators
        tools.extend([
            Tool(
                name="calculate_rsi_complete",
                description="Calculate RSI with comprehensive analysis including divergences, overbought/oversold signals, and trading recommendations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "OHLCV price data"},
                        "window": {"type": "integer", "default": 14, "description": "RSI calculation window"}
                    },
                    "required": ["data"]
                }
            ),
            Tool(
                name="calculate_macd_complete",
                description="Calculate MACD with crossovers, histogram analysis, zero line crossings, and trend signals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "Price data with close values"},
                        "fast": {"type": "integer", "default": 12, "description": "Fast EMA period"},
                        "slow": {"type": "integer", "default": 26, "description": "Slow EMA period"},
                        "signal": {"type": "integer", "default": 9, "description": "Signal line EMA period"}
                    },
                    "required": ["data"]
                }
            ),
            Tool(
                name="calculate_stochastic_complete", 
                description="Calculate Stochastic Oscillator with crossovers, divergences, and momentum analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "OHLC price data"},
                        "k_window": {"type": "integer", "default": 14, "description": "%K period"},
                        "d_window": {"type": "integer", "default": 3, "description": "%D period"},
                        "smooth_k": {"type": "integer", "default": 3, "description": "%K smoothing"}
                    },
                    "required": ["data"]
                }
            )
        ])
        
        # Trend indicators
        tools.append(
            Tool(
                name="calculate_adx_complete",
                description="Calculate ADX with trend strength analysis, directional indicators, and Wilder's trading signals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "OHLC price data"},
                        "window": {"type": "integer", "default": 14, "description": "ADX calculation window"}
                    },
                    "required": ["data"]
                }
            )
        )
        
        # Volatility indicators
        tools.extend([
            Tool(
                name="calculate_bollinger_bands_complete",
                description="Calculate Bollinger Bands with squeeze analysis, band walks, volatility breakouts, and %B analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "Price data with close values"},
                        "window": {"type": "integer", "default": 20, "description": "Moving average window"},
                        "window_dev": {"type": "integer", "default": 2, "description": "Standard deviation multiplier"}
                    },
                    "required": ["data"]
                }
            ),
            Tool(
                name="calculate_atr_complete",
                description="Calculate ATR with volatility regime analysis, momentum, and breakout detection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "OHLC price data"},
                        "window": {"type": "integer", "default": 14, "description": "ATR calculation window"}
                    },
                    "required": ["data"]
                }
            )
        ])
        
        # Volume indicators
        tools.extend([
            Tool(
                name="calculate_obv_complete",
                description="Calculate On-Balance Volume with trend analysis, divergences, and accumulation/distribution signals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "Price and volume data"}
                    },
                    "required": ["data"]
                }
            ),
            Tool(
                name="calculate_mfi_complete",
                description="Calculate Money Flow Index with volume-price analysis, divergences, and money flow ratios",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "OHLCV price data"},
                        "window": {"type": "integer", "default": 14, "description": "MFI calculation window"}
                    },
                    "required": ["data"]
                }
            )
        ])
        
        # Comprehensive analysis
        tools.append(
            Tool(
                name="comprehensive_technical_analysis",
                description="Generate comprehensive technical analysis combining multiple indicators, patterns, and trading signals with overall market sentiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": ["array", "object"], "description": "Complete OHLCV price data"},
                        "indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of indicators to calculate (rsi, macd, bollinger, sma, ema, stochastic, atr, adx)"
                        },
                        "patterns": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "List of patterns to detect (support_resistance, gaps, breakouts, reversals)"
                        }
                    },
                    "required": ["data"]
                }
            )
        )
        
        return tools

# Initialize server capabilities
@server.initialize()
async def on_initialize() -> InitializeResult:
    """Initialize the MCP server with technical analysis capabilities."""
    logger.info("Initializing MCP Analytics Server with comprehensive technical analysis")
    
    return InitializeResult(
        serverInfo={
            "name": "mcp-analytics-server",
            "version": "1.0.0",
            "description": "Comprehensive technical analysis server with all major indicators and patterns"
        },
        capabilities=ServerCapabilities(
            tools={},
            notifications=NotificationOptions()
        )
    )

# List available tools
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available technical analysis tools."""
    ta_server = TechnicalAnalyticsMCPServer()
    return ta_server.get_available_tools()

# Main server execution
async def main():
    """Main server execution function."""
    logger.info("Starting MCP Analytics Server...")
    
    # Initialize the technical analysis server
    ta_server = TechnicalAnalyticsMCPServer()
    
    # Run the server
    async with server:
        transport = await server.connect_stdio()
        await server.run_until_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)