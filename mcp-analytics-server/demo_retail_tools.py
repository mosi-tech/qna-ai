#!/usr/bin/env python3
"""
Demo of Retail Analysis Tools - End-to-End Implementation

This demonstrates how the retail analysis tools work with:
1. MCP Financial Server data (mocked for demo)
2. Our analytics engine calculations
3. Real technical analysis results
"""

import sys
import os
import json
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.tier_1_information import current_price_stats

def demo_current_price_stats():
    """Comprehensive demo of current_price_stats with different scenarios"""
    
    print("🎯 RETAIL ANALYSIS TOOLS DEMO")
    print("=" * 60)
    print("Demo: current-price-stats tool")
    print("- Uses MCP Financial Server for market data")
    print("- Uses Analytics Engine for technical calculations")
    print("")
    
    # Scenario 1: Bullish stock scenario
    print("📈 SCENARIO 1: Bullish Stock (AAPL)")
    print("-" * 40)
    
    # Create mock data for a bullish scenario
    bullish_mock_data = {
        "snapshot": {
            "symbol": "AAPL",
            "price": 185.50,
            "change": 4.25,
            "change_percent": 2.35,
            "volume": 68_000_000,
            "avg_volume": 55_000_000,
            "market_cap": 2_800_000_000_000,
            "high": 187.20,
            "low": 182.10
        },
        "bars": []
    }
    
    # Generate bullish trending data (upward trend)
    np.random.seed(100)
    base_price = 175.0
    bullish_returns = np.random.normal(0.002, 0.015, 50)  # Positive drift, lower volatility
    prices = [base_price]
    for ret in bullish_returns:
        prices.append(prices[-1] * (1 + ret))
    
    bullish_mock_data["bars"] = [{"close": price} for price in prices]
    
    result1 = current_price_stats("AAPL", mock_data=bullish_mock_data)
    
    print(f"📊 Current Price: ${result1['current_price']}")
    print(f"📊 Daily Change: {result1['change_percent']:.2f}%")
    print(f"📊 Volume: {result1['volume']:,} (vs avg {result1['avg_volume']:,})")
    print(f"📊 52-Week Position: {result1['analytics_metrics']['52_week_range']['current_position']:.1%}")
    print(f"📊 Annualized Volatility: {result1['analytics_metrics']['volatility_metrics']['annualized_volatility']:.1%}")
    print(f"📊 RSI (14): {result1['analytics_metrics']['momentum_metrics']['rsi_14']:.1f}")
    print(f"📊 Trend Direction: {result1['analytics_metrics']['trend_metrics']['trend_direction']}")
    print(f"📊 Price vs SMA20: {result1['analytics_metrics']['trend_metrics']['price_vs_sma20_pct']:+.2f}%")
    print()
    
    # Scenario 2: Bearish/Oversold scenario
    print("📉 SCENARIO 2: Bearish/Oversold Stock (TSLA)")
    print("-" * 40)
    
    bearish_mock_data = {
        "snapshot": {
            "symbol": "TSLA", 
            "price": 195.75,
            "change": -8.50,
            "change_percent": -4.15,
            "volume": 125_000_000,
            "avg_volume": 85_000_000,
            "market_cap": 620_000_000_000,
            "high": 201.20,
            "low": 194.80
        },
        "bars": []
    }
    
    # Generate bearish trending data (downward trend, higher volatility)
    np.random.seed(200)
    base_price = 220.0
    bearish_returns = np.random.normal(-0.003, 0.025, 50)  # Negative drift, higher volatility
    prices = [base_price]
    for ret in bearish_returns:
        prices.append(prices[-1] * (1 + ret))
    
    bearish_mock_data["bars"] = [{"close": price} for price in prices]
    
    result2 = current_price_stats("TSLA", mock_data=bearish_mock_data)
    
    print(f"📊 Current Price: ${result2['current_price']}")
    print(f"📊 Daily Change: {result2['change_percent']:+.2f}%")
    print(f"📊 Volume: {result2['volume']:,} (vs avg {result2['avg_volume']:,})")
    print(f"📊 52-Week Position: {result2['analytics_metrics']['52_week_range']['current_position']:.1%}")
    print(f"📊 Annualized Volatility: {result2['analytics_metrics']['volatility_metrics']['annualized_volatility']:.1%}")
    print(f"📊 RSI (14): {result2['analytics_metrics']['momentum_metrics']['rsi_14']:.1f}")
    print(f"📊 Trend Direction: {result2['analytics_metrics']['trend_metrics']['trend_direction']}")
    print(f"📊 Price vs SMA20: {result2['analytics_metrics']['trend_metrics']['price_vs_sma20_pct']:+.2f}%")
    print()
    
    # Scenario 3: Default mock data (no custom data provided)
    print("📊 SCENARIO 3: Default Demo Data (SPY)")
    print("-" * 40)
    
    result3 = current_price_stats("SPY")  # Uses default mock data
    
    print(f"📊 Current Price: ${result3['current_price']}")
    print(f"📊 Daily Change: {result3['change_percent']:+.2f}%")
    print(f"📊 Volume: {result3['volume']:,} (vs avg {result3['avg_volume']:,})")
    print(f"📊 52-Week Position: {result3['analytics_metrics']['52_week_range']['current_position']:.1%}")
    print(f"📊 Annualized Volatility: {result3['analytics_metrics']['volatility_metrics']['annualized_volatility']:.1%}")
    print(f"📊 RSI (14): {result3['analytics_metrics']['momentum_metrics']['rsi_14']:.1f}")
    print(f"📊 Trend Direction: {result3['analytics_metrics']['trend_metrics']['trend_direction']}")
    print(f"📊 Price vs SMA20: {result3['analytics_metrics']['trend_metrics']['price_vs_sma20_pct']:+.2f}%")
    print()
    
    # Show the analytics functions being used
    print("🔧 ANALYTICS ENGINE FUNCTIONS USED:")
    print("-" * 40)
    for func in result1['analytics_functions_used']:
        print(f"✅ {func}")
    print()
    
    print("🔌 MCP FINANCIAL SERVER FUNCTIONS NEEDED:")
    print("-" * 40)
    for func in result1['mcp_functions_used']:
        print(f"🔗 {func}")
    print()
    
    print("✨ SUMMARY:")
    print("-" * 40)
    print("✅ End-to-end implementation working")
    print("✅ Real analytics calculations performed")
    print("✅ Comprehensive market data analysis")
    print("✅ Ready for MCP server integration")
    print("✅ Retail-friendly output format")

if __name__ == "__main__":
    demo_current_price_stats()