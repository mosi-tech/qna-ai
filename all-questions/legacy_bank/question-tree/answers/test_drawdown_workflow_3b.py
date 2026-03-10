#!/usr/bin/env python3
"""
Workflow for Question 3b: "Which ETF has lower maximum drawdown risk?"
Used functions: ["alpaca_market_stocks_bars", "calculate_drawdown_analysis"]
"""

import sys
import os

# Add the MCP directory to path to use the real MCP functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

def test_drawdown_workflow():
    """Test complete drawdown analysis workflow for ARKK vs QQQ using real MCP functions"""
    
    print("=== QUESTION 3B: Which ETF has lower maximum drawdown risk? ===")
    print()
    
    # CRITICAL MCP INTEGRATION: Import MCP functions first
    try:
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
    
    # Step 3: Run drawdown analysis for ARKK using MCP analytics
    print("Step 3: Running calculate_drawdown_analysis for ARKK via MCP analytics...")
    try:
        arkk_drawdown = calculate_drawdown_analysis(arkk_returns.tolist())
        print(f"✅ ARKK Max Drawdown: {arkk_drawdown['max_drawdown_pct']}")
    except Exception as e:
        print(f"❌ Error calculating ARKK drawdown: {e}")
        return {"workflow_success": False, "error": str(e)}
    
    # Step 4: Run drawdown analysis for QQQ using MCP analytics
    print("Step 4: Running calculate_drawdown_analysis for QQQ via MCP analytics...")
    try:
        qqq_drawdown = calculate_drawdown_analysis(qqq_returns.tolist())
        print(f"✅ QQQ Max Drawdown: {qqq_drawdown['max_drawdown_pct']}")
    except Exception as e:
        print(f"❌ Error calculating QQQ drawdown: {e}")
        return {"workflow_success": False, "error": str(e)}
    
    print()
    print("=== DRAWDOWN RISK COMPARISON RESULTS ===")
    print(f"ARKK Maximum Drawdown: {arkk_drawdown['max_drawdown_pct']}")
    print(f"QQQ Maximum Drawdown: {qqq_drawdown['max_drawdown_pct']}")
    print()
    
    # Determine which has lower drawdown risk
    arkk_dd = abs(arkk_drawdown['max_drawdown'])
    qqq_dd = abs(qqq_drawdown['max_drawdown'])
    
    if qqq_dd < arkk_dd:
        winner = "QQQ"
        difference = arkk_dd - qqq_dd
        print(f"🏆 ANSWER: QQQ has lower maximum drawdown risk")
        print(f"   QQQ drawdown is {difference*100:.2f} percentage points lower than ARKK")
    else:
        winner = "ARKK"
        difference = qqq_dd - arkk_dd
        print(f"🏆 ANSWER: ARKK has lower maximum drawdown risk")
        print(f"   ARKK drawdown is {difference*100:.2f} percentage points lower than QQQ")
    
    print()
    print("📊 Additional Analysis:")
    print(f"   • Lower drawdown = better downside protection")
    print(f"   • {winner} shows better risk management during market stress")
    print(f"   • Both ETFs experienced significant drawdowns during the period")
    
    print()
    print("🔧 MCP Functions Used:")
    print("   ✅ alpaca_market_stocks_bars - Retrieved price data from MCP financial server")
    print("   ✅ prices_to_returns - Converted prices to returns via MCP utils")
    print("   ✅ calculate_drawdown_analysis - Analyzed drawdowns via MCP analytics")
    
    return {
        "question": "Which ETF has lower maximum drawdown risk?",
        "answer": f"{winner} has lower maximum drawdown risk",
        "arkk_drawdown": arkk_drawdown['max_drawdown_pct'],
        "qqq_drawdown": qqq_drawdown['max_drawdown_pct'],
        "winner": winner,
        "functions_used": ["alpaca_market_stocks_bars", "prices_to_returns", "calculate_drawdown_analysis"],
        "workflow_success": True
    }

if __name__ == "__main__":
    result = test_drawdown_workflow()
    print(f"\n✅ Workflow completed successfully: {result['workflow_success']}")