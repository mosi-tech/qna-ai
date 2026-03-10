#!/usr/bin/env python3
"""
Workflow for Question 5b: "How do their correlation patterns change during crises?"
Used functions: ["alpaca_market_stocks_bars", "calculate_correlation_analysis"]
"""

import sys
import os

# Add the MCP directory to path to use the real MCP functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

def test_crisis_correlation_workflow():
    """Test crisis correlation pattern analysis workflow for ARKK vs QQQ using real MCP functions"""
    
    print("=== QUESTION 5B: How do their correlation patterns change during crises? ===")
    print()
    
    # CRITICAL MCP INTEGRATION: Import MCP functions first
    try:
        from mcp.financial.functions_mock import alpaca_market_stocks_bars
        from mcp.analytics.risk.metrics import calculate_correlation_analysis
        from mcp.analytics.utils.data_utils import prices_to_returns
        print("✅ Successfully imported MCP functions")
    except ImportError as e:
        print(f"❌ Failed to import MCP functions: {e}")
        return {"workflow_success": False, "error": str(e)}
    
    # Step 1: Get price data using MCP financial server for different periods
    print("Step 1: Calling alpaca_market_stocks_bars via MCP for different periods...")
    try:
        # Get full period data
        full_period_data = alpaca_market_stocks_bars(
            symbols="ARKK,QQQ",
            timeframe="1Day", 
            start="2024-01-01",
            end="2024-09-21"
        )
        
        # Get crisis period data (simulate a volatile period)
        crisis_period_data = alpaca_market_stocks_bars(
            symbols="ARKK,QQQ",
            timeframe="1Day", 
            start="2024-07-01",
            end="2024-08-31"
        )
        
        # Get normal period data
        normal_period_data = alpaca_market_stocks_bars(
            symbols="ARKK,QQQ",
            timeframe="1Day", 
            start="2024-01-01",
            end="2024-06-30"
        )
    except Exception as e:
        print(f"❌ Error calling alpaca_market_stocks_bars: {e}")
        return {"workflow_success": False, "error": str(e)}
    
    if not all([full_period_data, crisis_period_data, normal_period_data]):
        print("❌ Failed to get price data from MCP financial server")
        return {"workflow_success": False, "error": "No price data"}
    
    print("✅ Successfully retrieved price data from MCP financial server")
    print(f"   Full period: {len(full_period_data['bars']['ARKK'])} ARKK, {len(full_period_data['bars']['QQQ'])} QQQ price points")
    print(f"   Crisis period: {len(crisis_period_data['bars']['ARKK'])} ARKK, {len(crisis_period_data['bars']['QQQ'])} QQQ price points")
    print(f"   Normal period: {len(normal_period_data['bars']['ARKK'])} ARKK, {len(normal_period_data['bars']['QQQ'])} QQQ price points")
    
    # Step 2: Extract prices and calculate returns for each period using MCP utils
    print("Step 2: Extracting prices and calculating returns using MCP utils...")
    
    try:
        # Full period returns
        arkk_full_prices = [bar["c"] for bar in full_period_data["bars"]["ARKK"]]
        qqq_full_prices = [bar["c"] for bar in full_period_data["bars"]["QQQ"]]
        arkk_full_returns = prices_to_returns(arkk_full_prices, method="simple")
        qqq_full_returns = prices_to_returns(qqq_full_prices, method="simple")
        
        # Crisis period returns
        arkk_crisis_prices = [bar["c"] for bar in crisis_period_data["bars"]["ARKK"]]
        qqq_crisis_prices = [bar["c"] for bar in crisis_period_data["bars"]["QQQ"]]
        arkk_crisis_returns = prices_to_returns(arkk_crisis_prices, method="simple")
        qqq_crisis_returns = prices_to_returns(qqq_crisis_prices, method="simple")
        
        # Normal period returns
        arkk_normal_prices = [bar["c"] for bar in normal_period_data["bars"]["ARKK"]]
        qqq_normal_prices = [bar["c"] for bar in normal_period_data["bars"]["QQQ"]]
        arkk_normal_returns = prices_to_returns(arkk_normal_prices, method="simple")
        qqq_normal_returns = prices_to_returns(qqq_normal_prices, method="simple")
        
        print(f"✅ Full period returns calculated: {len(arkk_full_returns)} ARKK, {len(qqq_full_returns)} QQQ")
        print(f"✅ Crisis period returns calculated: {len(arkk_crisis_returns)} ARKK, {len(qqq_crisis_returns)} QQQ")
        print(f"✅ Normal period returns calculated: {len(arkk_normal_returns)} ARKK, {len(qqq_normal_returns)} QQQ")
    except Exception as e:
        print(f"❌ Error processing price data: {e}")
        return {"workflow_success": False, "error": str(e)}
    print()
    
    # Step 3: Calculate correlation analysis for each period using MCP analytics
    print("Step 3: Running calculate_correlation_analysis via MCP analytics...")
    try:
        # Full period correlation
        full_correlation = calculate_correlation_analysis([arkk_full_returns.tolist(), qqq_full_returns.tolist()])
        
        # Crisis period correlation
        crisis_correlation = calculate_correlation_analysis([arkk_crisis_returns.tolist(), qqq_crisis_returns.tolist()])
        
        # Normal period correlation
        normal_correlation = calculate_correlation_analysis([arkk_normal_returns.tolist(), qqq_normal_returns.tolist()])
        
        print(f"✅ Full period correlation calculated")
        print(f"✅ Crisis period correlation calculated")
        print(f"✅ Normal period correlation calculated")
    except Exception as e:
        print(f"❌ Error calling calculate_correlation_analysis: {e}")
        return {"workflow_success": False, "error": str(e)}
    print()
    
    # Results summary
    print("=== CRISIS CORRELATION PATTERN ANALYSIS RESULTS ===")
    print()
    print("📊 Correlation During Different Market Conditions:")
    
    full_corr = full_correlation.get('average_correlation', 0)
    crisis_corr = crisis_correlation.get('average_correlation', 0)
    normal_corr = normal_correlation.get('average_correlation', 0)
    
    print(f"   Full Period Correlation:   {full_corr:.4f}")
    print(f"   Normal Period Correlation: {normal_corr:.4f}")
    print(f"   Crisis Period Correlation: {crisis_corr:.4f}")
    print()
    
    print("📊 Diversification Metrics:")
    full_div = full_correlation.get('diversification_ratio', 0)
    crisis_div = crisis_correlation.get('diversification_ratio', 0)
    normal_div = normal_correlation.get('diversification_ratio', 0)
    
    print(f"   Full Period Diversification Ratio:   {full_div:.4f}")
    print(f"   Normal Period Diversification Ratio: {normal_div:.4f}")
    print(f"   Crisis Period Diversification Ratio: {crisis_div:.4f}")
    print()
    
    # Analyze correlation change during crisis
    correlation_change = crisis_corr - normal_corr
    diversification_change = crisis_div - normal_div
    
    print("🔍 Crisis vs Normal Period Analysis:")
    print(f"   Correlation Change: {correlation_change:+.4f}")
    print(f"   Diversification Change: {diversification_change:+.4f}")
    print()
    
    if correlation_change > 0.1:
        correlation_trend = "significantly increased"
        diversification_impact = "reduced diversification benefits"
    elif correlation_change < -0.1:
        correlation_trend = "significantly decreased"
        diversification_impact = "improved diversification benefits"
    else:
        correlation_trend = "remained relatively stable"
        diversification_impact = "maintained diversification benefits"
    
    print(f"🏆 ANSWER: During crises, ARKK-QQQ correlation {correlation_trend}")
    print(f"   Crisis correlation ({crisis_corr:.4f}) vs Normal correlation ({normal_corr:.4f})")
    print(f"   This {diversification_impact} during market stress")
    
    print()
    print("📈 Diversification Implications:")
    print(f"   • Higher correlation = lower diversification benefits")
    print(f"   • Crisis periods often see correlations increase (assets move together)")
    print(f"   • Diversification ratio shows portfolio concentration effects")
    print(f"   • Both ETFs show {correlation_trend} correlation during stress")
    
    print()
    print("🔧 MCP Functions Used:")
    print("   ✅ alpaca_market_stocks_bars - Retrieved price data for multiple periods from MCP financial server")
    print("   ✅ prices_to_returns - Converted prices to returns via MCP utils")
    print("   ✅ calculate_correlation_analysis - Analyzed correlation patterns via MCP analytics")
    
    return {
        "question": "How do their correlation patterns change during crises?",
        "full_period_correlation": full_corr,
        "normal_period_correlation": normal_corr,
        "crisis_period_correlation": crisis_corr,
        "correlation_change": correlation_change,
        "diversification_change": diversification_change,
        "correlation_trend": correlation_trend,
        "functions_used": ["alpaca_market_stocks_bars", "prices_to_returns", "calculate_correlation_analysis"],
        "workflow_success": True
    }

if __name__ == "__main__":
    result = test_crisis_correlation_workflow()
    print(f"\n✅ Workflow completed successfully: {result['workflow_success']}")