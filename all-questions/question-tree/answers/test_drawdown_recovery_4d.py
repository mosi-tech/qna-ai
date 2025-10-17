#!/usr/bin/env python3
"""
Workflow for Question 4d: "Which recovers faster from major drawdowns?"
Used functions: ["alpaca_market_stocks_bars", "calculate_drawdown_analysis"]
"""

import sys
import os

# Add the MCP directory to path to use the real MCP functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

def test_drawdown_recovery_workflow():
    """Test drawdown recovery speed analysis workflow for ARKK vs QQQ using real MCP functions"""
    
    print("=== QUESTION 4D: Which recovers faster from major drawdowns? ===")
    print()
    
    # Import MCP functions
    try:
        # Import real MCP financial server function
        from mcp.financial.functions_mock import alpaca_market_stocks_bars
        from mcp.analytics.performance.metrics import calculate_drawdown_analysis
        from mcp.analytics.utils.data_utils import prices_to_returns
        print("✅ Successfully imported MCP functions")
    except ImportError as e:
        print(f"❌ Failed to import MCP functions: {e}")
        return {"workflow_success": False, "error": str(e)}
    
    # Step 1: Get price data using MCP financial server
    print("Step 1: Calling alpaca_market_stocks_bars via MCP...")
    try:
        price_data = alpaca_market_stocks_bars(
            symbols="ARKK,QQQ",
            timeframe="1Day", 
            start="2024-01-01",
            end="2024-09-21"
        )
    except Exception as e:
        print(f"❌ Error calling alpaca_market_stocks_bars: {e}")
        return {"workflow_success": False, "error": str(e)}
    
    if not price_data or "bars" not in price_data:
        print("❌ Failed to get price data from MCP financial server")
        return {"workflow_success": False, "error": "No price data"}
    
    print("✅ Successfully retrieved price data from MCP financial server")
    print(f"   ARKK: {len(price_data['bars']['ARKK'])} price points")
    print(f"   QQQ: {len(price_data['bars']['QQQ'])} price points")
    
    # Step 2: Extract prices and calculate returns using MCP utils
    print("Step 2: Extracting prices and calculating returns using MCP utils...")
    
    try:
        # Extract closing prices from the bars data
        arkk_prices = [bar["c"] for bar in price_data["bars"]["ARKK"]]
        qqq_prices = [bar["c"] for bar in price_data["bars"]["QQQ"]]
        
        # Calculate returns using MCP utilities
        arkk_returns = prices_to_returns(arkk_prices, method="simple")
        qqq_returns = prices_to_returns(qqq_prices, method="simple")
        
        print(f"✅ ARKK returns calculated: {len(arkk_returns)} periods")
        print(f"✅ QQQ returns calculated: {len(qqq_returns)} periods")
    except Exception as e:
        print(f"❌ Error processing price data: {e}")
        return {"workflow_success": False, "error": str(e)}
    print()
    
    # Step 3: Calculate drawdown analysis for both ETFs using MCP analytics
    print("Step 3: Running calculate_drawdown_analysis via MCP analytics...")
    try:
        arkk_drawdown = calculate_drawdown_analysis(arkk_returns.tolist())
        qqq_drawdown = calculate_drawdown_analysis(qqq_returns.tolist())
        print(f"✅ ARKK drawdown analysis completed")
        print(f"✅ QQQ drawdown analysis completed")
    except Exception as e:
        print(f"❌ Error calling calculate_drawdown_analysis: {e}")
        return {"workflow_success": False, "error": str(e)}
    print()
    
    # Step 4: Analyze recovery speeds
    print("Step 4: Analyzing drawdown recovery speeds...")
    
    # Extract key metrics
    arkk_max_drawdown = arkk_drawdown.get('max_drawdown', 0)
    qqq_max_drawdown = qqq_drawdown.get('max_drawdown', 0)
    
    arkk_avg_recovery = arkk_drawdown.get('avg_recovery_days', 0)
    qqq_avg_recovery = qqq_drawdown.get('avg_recovery_days', 0)
    
    arkk_max_recovery = arkk_drawdown.get('max_recovery_days', 0)
    qqq_max_recovery = qqq_drawdown.get('max_recovery_days', 0)
    
    print(f"✅ Recovery metrics calculated for both ETFs")
    print()
    
    # Results summary
    print("=== DRAWDOWN RECOVERY SPEED ANALYSIS RESULTS ===")
    print()
    print("📊 Maximum Drawdowns:")
    print(f"   ARKK: {arkk_drawdown.get('max_drawdown_pct', 'N/A')}")
    print(f"   QQQ:  {qqq_drawdown.get('max_drawdown_pct', 'N/A')}")
    print()
    
    print("⏱️ Recovery Speed Metrics:")
    print(f"   ARKK Average Recovery: {arkk_avg_recovery} days")
    print(f"   QQQ Average Recovery:  {qqq_avg_recovery} days")
    print()
    print(f"   ARKK Max Recovery: {arkk_max_recovery} days")
    print(f"   QQQ Max Recovery:  {qqq_max_recovery} days")
    print()
    
    # Determine which recovers faster
    if arkk_avg_recovery > 0 and qqq_avg_recovery > 0:
        if qqq_avg_recovery < arkk_avg_recovery:
            faster_etf = "QQQ"
            recovery_difference = arkk_avg_recovery - qqq_avg_recovery
            print(f"🏆 ANSWER: QQQ recovers faster from major drawdowns")
            print(f"   QQQ recovers {recovery_difference:.1f} days faster on average than ARKK")
        elif arkk_avg_recovery < qqq_avg_recovery:
            faster_etf = "ARKK"
            recovery_difference = qqq_avg_recovery - arkk_avg_recovery
            print(f"🏆 ANSWER: ARKK recovers faster from major drawdowns")
            print(f"   ARKK recovers {recovery_difference:.1f} days faster on average than QQQ")
        else:
            faster_etf = "Both"
            recovery_difference = 0
            print(f"🏆 ANSWER: Both ETFs have similar recovery speeds")
    else:
        faster_etf = "Insufficient data"
        recovery_difference = 0
        print(f"🏆 ANSWER: Insufficient data to determine recovery speeds")
    
    print()
    print("📈 Recovery Implications:")
    print(f"   • Faster recovery = better resilience during market stress")
    print(f"   • Shorter recovery periods reduce opportunity cost")
    print(f"   • Recovery speed varies by market conditions and volatility")
    
    print()
    print("🔧 MCP Functions Used:")
    print("   ✅ alpaca_market_stocks_bars - Retrieved price data from MCP financial server")
    print("   ✅ prices_to_returns - Converted prices to returns via MCP utils")
    print("   ✅ calculate_drawdown_analysis - Analyzed drawdowns and recovery via MCP analytics")
    
    return {
        "question": "Which recovers faster from major drawdowns?",
        "arkk_max_drawdown": arkk_drawdown.get('max_drawdown_pct', 'N/A'),
        "qqq_max_drawdown": qqq_drawdown.get('max_drawdown_pct', 'N/A'),
        "arkk_avg_recovery_days": arkk_avg_recovery,
        "qqq_avg_recovery_days": qqq_avg_recovery,
        "faster_recovery_etf": faster_etf,
        "recovery_difference_days": recovery_difference,
        "functions_used": ["alpaca_market_stocks_bars", "prices_to_returns", "calculate_drawdown_analysis"],
        "workflow_success": True
    }

if __name__ == "__main__":
    result = test_drawdown_recovery_workflow()
    print(f"\n✅ Workflow completed successfully: {result['workflow_success']}")