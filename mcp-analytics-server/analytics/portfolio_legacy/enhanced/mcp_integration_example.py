"""
MCP Integration Example for Enhanced Portfolio Functions

This file demonstrates how to integrate the enhanced portfolio analysis functions
with the existing MCP analytics server to expose them as tools.

The enhanced functions are designed to work seamlessly with:
- Existing MCP financial data server (Alpaca, EODHD)
- Existing technical analysis functions (115 indicators)
- Multi-tier complexity (retail/professional/quantitative)
"""

import json
from typing import Dict, Any, List
import mcp.types as types


def create_enhanced_portfolio_tools() -> List[types.Tool]:
    """
    Create MCP tool definitions for enhanced portfolio functions
    
    This shows how to expose the sophisticated portfolio tools through MCP
    while maintaining the retail-friendly interface.
    """
    
    tools = []
    
    # Enhanced Portfolio Analyzer Tool
    tools.append(types.Tool(
        name="enhanced_portfolio_analyzer",
        description="Multi-tier portfolio analysis with real market data - supports retail, professional, and quantitative modes",
        inputSchema={
            "type": "object",
            "properties": {
                # RETAIL MODE - Simple inputs
                "portfolio_assets": {
                    "type": "object",
                    "description": "Portfolio allocation as {symbol: weight_percentage}",
                    "example": {"VTI": 60, "BND": 40}
                },
                "initial_investment": {
                    "type": "number",
                    "default": 100000,
                    "description": "Initial investment amount in dollars"
                },
                "monthly_contribution": {
                    "type": "number",
                    "default": 0,
                    "description": "Monthly contribution amount"
                },
                
                # CONFIGURATION
                "analysis_mode": {
                    "type": "string",
                    "enum": ["retail", "professional", "quantitative"],
                    "default": "retail",
                    "description": "Analysis complexity level"
                },
                "lookback_years": {
                    "type": "integer", 
                    "default": 5,
                    "description": "Years of historical data to analyze"
                },
                
                # PROFESSIONAL MODE - Advanced options
                "use_technical_indicators": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include technical indicator analysis"
                },
                "stress_test_periods": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Custom stress test periods (e.g., ['2008-01-01:2009-12-31'])"
                },
                "custom_benchmarks": {
                    "type": "array", 
                    "items": {"type": "string"},
                    "description": "Custom benchmark symbols for comparison"
                },
                
                # PRESET OPTIONS - Retail shortcuts
                "portfolio_preset": {
                    "type": "string",
                    "enum": ["3_fund", "4_fund", "target_date", "factor_tilt"],
                    "description": "Use predefined portfolio allocation"
                }
            },
            "required": []  # No required fields - uses sensible defaults
        }
    ))
    
    # Configurable Rebalancing Analyzer Tool  
    tools.append(types.Tool(
        name="configurable_rebalancing_analyzer", 
        description="Advanced rebalancing strategy analysis with real market data and transaction costs",
        inputSchema={
            "type": "object",
            "properties": {
                "assets": {
                    "type": "object",
                    "description": "Portfolio assets as {symbol: weight_percentage}",
                    "example": {"VTI": 60, "BND": 40}
                },
                "initial_investment": {
                    "type": "number",
                    "default": 100000,
                    "description": "Initial investment amount"
                },
                "rebalancing_strategy": {
                    "type": "string",
                    "enum": ["calendar", "threshold", "momentum", "mean_reversion", "volatility_target", "technical_signals"],
                    "default": "threshold",
                    "description": "Rebalancing methodology"
                },
                "rebalancing_frequency": {
                    "type": "string",
                    "enum": ["monthly", "quarterly", "yearly"],
                    "default": "quarterly",
                    "description": "Calendar rebalancing frequency"
                },
                "drift_threshold": {
                    "type": "number",
                    "default": 5.0,
                    "description": "Percentage drift threshold for rebalancing"
                },
                "transaction_cost_bps": {
                    "type": "number", 
                    "default": 5.0,
                    "description": "Transaction costs in basis points"
                },
                "analysis_mode": {
                    "type": "string",
                    "enum": ["retail", "professional", "quantitative"],
                    "default": "retail",
                    "description": "Analysis detail level"
                },
                "lookback_years": {
                    "type": "integer",
                    "default": 5,
                    "description": "Years of historical data for analysis"
                }
            },
            "required": ["assets"]
        }
    ))
    
    return tools


async def handle_enhanced_portfolio_calls(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle MCP calls to enhanced portfolio functions
    
    This shows how the enhanced functions integrate with MCP server while
    using real financial data from the MCP financial server.
    """
    
    try:
        # Import the enhanced functions
        from .data_driven_analyzer import enhanced_portfolio_analyzer, AnalysisConfig
        from .configurable_rebalancing import configurable_rebalancing_analyzer, RebalancingConfig, RebalancingStrategy
        
        # Get MCP financial server functions (these would be passed in from main server)
        # For demonstration, showing the integration pattern
        async def mcp_get_historical_data(function: str, **kwargs):
            """Wrapper to call MCP financial server functions"""
            # This would call the actual MCP financial server
            # e.g., alpaca-market_stocks-bars, eodhd_eod-data
            return await call_mcp_financial_server(function, **kwargs)
        
        async def mcp_technical_analysis(indicator: str, **kwargs):
            """Wrapper to call MCP technical analysis functions"""  
            # This would call the existing 115 technical indicators
            return await call_mcp_analytics_server(indicator, **kwargs)
        
        if name == "enhanced_portfolio_analyzer":
            # Extract configuration
            config = AnalysisConfig(
                mode=arguments.get("analysis_mode", "retail"),
                lookback_years=arguments.get("lookback_years", 5),
                use_technical_indicators=arguments.get("use_technical_indicators", False),
                stress_test_periods=arguments.get("stress_test_periods"),
                custom_benchmarks=arguments.get("custom_benchmarks")
            )
            
            # Call enhanced analyzer with real MCP data integration
            result = await enhanced_portfolio_analyzer(
                portfolio_assets=arguments.get("portfolio_assets"),
                initial_investment=arguments.get("initial_investment", 100000),
                monthly_contribution=arguments.get("monthly_contribution", 0),
                config=config,
                mcp_get_historical_data=mcp_get_historical_data,
                mcp_technical_indicators=mcp_technical_analysis,
                portfolio_preset=arguments.get("portfolio_preset")
            )
            
        elif name == "configurable_rebalancing_analyzer":
            # Extract rebalancing configuration
            strategy_map = {
                "calendar": RebalancingStrategy.CALENDAR,
                "threshold": RebalancingStrategy.THRESHOLD,
                "momentum": RebalancingStrategy.MOMENTUM,
                "mean_reversion": RebalancingStrategy.MEAN_REVERSION,
                "volatility_target": RebalancingStrategy.VOLATILITY_TARGET,
                "technical_signals": RebalancingStrategy.TECHNICAL_SIGNALS
            }
            
            config = RebalancingConfig(
                strategy=strategy_map.get(arguments.get("rebalancing_strategy", "threshold")),
                frequency=arguments.get("rebalancing_frequency", "quarterly"),
                drift_threshold=arguments.get("drift_threshold", 5.0),
                transaction_cost_bps=arguments.get("transaction_cost_bps", 5.0),
                lookback_years=arguments.get("lookback_years", 5)
            )
            
            result = await configurable_rebalancing_analyzer(
                assets=arguments["assets"],
                initial_investment=arguments.get("initial_investment", 100000),
                config=config,
                mcp_get_historical_data=mcp_get_historical_data,
                mcp_technical_analysis=mcp_technical_analysis,
                analysis_mode=arguments.get("analysis_mode", "retail")
            )
        
        else:
            result = {
                "success": False,
                "error": f"Unknown enhanced function: {name}"
            }
        
        # Add MCP execution metadata
        result["mcp_execution"] = {
            "function_name": name,
            "analysis_mode": arguments.get("analysis_mode", "retail"),
            "real_data_integration": True,
            "server": "enhanced-portfolio-analytics"
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Enhanced analysis failed: {str(e)}",
                "function": name
            }, indent=2)
        )]


async def call_mcp_financial_server(function: str, **kwargs) -> Dict[str, Any]:
    """
    Mock function showing how to integrate with MCP financial server
    
    In actual implementation, this would call the real MCP financial server
    functions like alpaca-market_stocks-bars, eodhd_eod-data, etc.
    """
    
    # This would be replaced with actual MCP financial server calls
    return {
        "success": True,
        "data": "Real market data would be returned here",
        "source": f"mcp-financial-server:{function}",
        "parameters": kwargs
    }


async def call_mcp_analytics_server(indicator: str, **kwargs) -> Dict[str, Any]:
    """
    Mock function showing how to integrate with existing technical analysis
    
    In actual implementation, this would call the existing 115 technical
    indicator functions already available in the MCP analytics server.
    """
    
    return {
        "success": True,
        "indicator": indicator,
        "data": "Technical indicator results would be here",
        "source": "mcp-analytics-server:technical"
    }


# Example usage for different user types

RETAIL_USAGE_EXAMPLE = {
    "function": "enhanced_portfolio_analyzer",
    "arguments": {
        "portfolio_assets": {"VTI": 70, "BND": 30},
        "initial_investment": 25000,
        "monthly_contribution": 1000,
        "analysis_mode": "retail"
    },
    "expected_output": {
        "plain_english_summary": "Your portfolio would have grown $25,000 to $47,500 over 5 years...",
        "performance_grade": "Good",
        "vs_market": {"outperformed": True, "alpha": "+1.2%"},
        "data_driven": True,
        "real_market_performance": True
    }
}

PROFESSIONAL_USAGE_EXAMPLE = {
    "function": "configurable_rebalancing_analyzer", 
    "arguments": {
        "assets": {"QQQ": 40, "VTV": 30, "VEA": 20, "BND": 10},
        "rebalancing_strategy": "technical_signals",
        "transaction_cost_bps": 3.0,
        "analysis_mode": "professional",
        "lookback_years": 10
    },
    "expected_output": {
        "strategy_performance": {"risk_adjusted_return": 1.45, "maximum_drawdown": "-18.2%"},
        "transaction_analysis": {"total_costs": "$1,247", "cost_drag": "0.15%"},
        "optimization_suggestions": ["Consider dynamic threshold based on volatility"]
    }
}