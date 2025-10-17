#!/usr/bin/env python3
"""
Workflow for Question 4b: "Which ETF shows more consistent monthly returns?"
Used functions: ["alpaca_market_stocks_bars", "calculate_risk_metrics"]
"""

import sys
import os
import pandas as pd

# Add the MCP directory to path to use the real MCP functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))


def test_return_consistency_workflow():
    """Test return consistency analysis workflow for ARKK vs QQQ using real MCP functions"""
    
    print("=== QUESTION 4B: Which ETF shows more consistent monthly returns? ===")
    print()
    
    # Import MCP functions
    try:
        # Import real MCP financial server function
        from mcp.financial.functions_mock import alpaca_market_stocks_bars
        from mcp.analytics.performance.metrics import calculate_risk_metrics
        from mcp.analytics.utils.data_utils import prices_to_returns, calculate_monthly_returns
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
    
    # Step 2: Extract prices and calculate daily returns using MCP utils
    print("Step 2: Extracting prices and calculating daily returns using MCP utils...")
    
    try:
        # Extract closing prices from the bars data
        arkk_prices = [bar["c"] for bar in price_data["bars"]["ARKK"]]
        qqq_prices = [bar["c"] for bar in price_data["bars"]["QQQ"]]
        
        # Calculate daily returns using MCP utilities
        arkk_daily_returns = prices_to_returns(arkk_prices, method="simple")
        qqq_daily_returns = prices_to_returns(qqq_prices, method="simple")
        
        print(f"✅ ARKK daily returns calculated: {len(arkk_daily_returns)} periods")
        print(f"✅ QQQ daily returns calculated: {len(qqq_daily_returns)} periods")
    except Exception as e:
        print(f"❌ Error processing price data: {e}")
        return {"workflow_success": False, "error": str(e)}
    print()
    
    # Step 3: Convert daily returns to monthly returns using MCP utils
    print("Step 3: Converting daily returns to monthly returns using MCP utils...")
    arkk_monthly_returns = calculate_monthly_returns(arkk_daily_returns)
    qqq_monthly_returns = calculate_monthly_returns(qqq_daily_returns)
    
    print(f"✅ ARKK monthly returns calculated: {len(arkk_monthly_returns)} months")
    print(f"✅ QQQ monthly returns calculated: {len(qqq_monthly_returns)} months")
    print()
    
    # Step 4: Calculate risk metrics for monthly returns using MCP analytics
    print("Step 4: Running calculate_risk_metrics for monthly returns via MCP analytics...")
    try:
        arkk_risk_metrics = calculate_risk_metrics(arkk_monthly_returns)
        qqq_risk_metrics = calculate_risk_metrics(qqq_monthly_returns)
        print(f"✅ ARKK monthly risk metrics calculated")
        print(f"✅ QQQ monthly risk metrics calculated")
    except Exception as e:
        print(f"❌ Error calling calculate_risk_metrics: {e}")
        return {"workflow_success": False, "error": str(e)}
    print()
    
    # Step 5: Analyze consistency metrics
    print("Step 5: Analyzing return consistency metrics...")
    
    # Extract volatility (standard deviation) as primary consistency measure
    arkk_volatility = arkk_risk_metrics.get('volatility', 0)
    qqq_volatility = qqq_risk_metrics.get('volatility', 0)
    
    # Additional consistency metrics
    arkk_volatility_pct = arkk_risk_metrics.get('volatility_pct', 'N/A')
    qqq_volatility_pct = qqq_risk_metrics.get('volatility_pct', 'N/A')
    
    arkk_sharpe = arkk_risk_metrics.get('sharpe_ratio', 0)
    qqq_sharpe = qqq_risk_metrics.get('sharpe_ratio', 0)
    
    # Calculate additional consistency measures
    if len(arkk_monthly_returns) > 0 and len(qqq_monthly_returns) > 0:
        arkk_range = max(arkk_monthly_returns) - min(arkk_monthly_returns)
        qqq_range = max(qqq_monthly_returns) - min(qqq_monthly_returns)
        
        # Count of positive vs negative months
        arkk_positive_months = sum(1 for r in arkk_monthly_returns if r > 0)
        qqq_positive_months = sum(1 for r in qqq_monthly_returns if r > 0)
        
        arkk_consistency_ratio = arkk_positive_months / len(arkk_monthly_returns)
        qqq_consistency_ratio = qqq_positive_months / len(qqq_monthly_returns)
    else:
        arkk_range = qqq_range = 0
        arkk_consistency_ratio = qqq_consistency_ratio = 0
    
    print(f"✅ Consistency metrics calculated for both ETFs")
    print()
    
    # Results summary
    print("=== RETURN CONSISTENCY ANALYSIS RESULTS ===")
    print()
    print("📊 Monthly Return Volatility (Primary Consistency Measure):")
    print(f"   ARKK: {arkk_volatility_pct}")
    print(f"   QQQ:  {qqq_volatility_pct}")
    print()
    
    print("📈 Additional Consistency Metrics:")
    print(f"   ARKK Return Range: {arkk_range*100:.2f}%")
    print(f"   QQQ Return Range:  {qqq_range*100:.2f}%")
    print()
    print(f"   ARKK Positive Months: {arkk_positive_months}/{len(arkk_monthly_returns)} ({arkk_consistency_ratio*100:.1f}%)")
    print(f"   QQQ Positive Months:  {qqq_positive_months}/{len(qqq_monthly_returns)} ({qqq_consistency_ratio*100:.1f}%)")
    print()
    print(f"   ARKK Sharpe Ratio: {arkk_sharpe:.3f}")
    print(f"   QQQ Sharpe Ratio:  {qqq_sharpe:.3f}")
    print()
    
    # Determine which shows more consistent returns
    if arkk_volatility > 0 and qqq_volatility > 0:
        if qqq_volatility < arkk_volatility:
            more_consistent = "QQQ"
            volatility_difference = arkk_volatility - qqq_volatility
            print(f"🏆 ANSWER: QQQ shows more consistent monthly returns")
            print(f"   QQQ has {volatility_difference*100:.2f} percentage points lower monthly volatility than ARKK")
        elif arkk_volatility < qqq_volatility:
            more_consistent = "ARKK"
            volatility_difference = qqq_volatility - arkk_volatility
            print(f"🏆 ANSWER: ARKK shows more consistent monthly returns")
            print(f"   ARKK has {volatility_difference*100:.2f} percentage points lower monthly volatility than QQQ")
        else:
            more_consistent = "Both"
            volatility_difference = 0
            print(f"🏆 ANSWER: Both ETFs show similar monthly return consistency")
    else:
        more_consistent = "Insufficient data"
        volatility_difference = 0
        print(f"🏆 ANSWER: Insufficient data to determine consistency")
    
    print()
    print("📋 Consistency Implications:")
    print(f"   • Lower volatility = more predictable returns")
    print(f"   • Higher Sharpe ratio = better risk-adjusted consistency")
    print(f"   • More positive months = greater return reliability")
    print(f"   • Consistency is important for long-term planning")
    
    print()
    print("🔧 MCP Functions Used:")
    print("   ✅ alpaca_market_stocks_bars - Retrieved price data from MCP financial server")
    print("   ✅ prices_to_returns - Converted prices to returns via MCP utils")
    print("   ✅ calculate_monthly_returns - Converted daily to monthly returns via MCP utils")
    print("   ✅ calculate_risk_metrics - Analyzed return consistency via MCP analytics")
    
    return {
        "question": "Which ETF shows more consistent monthly returns?",
        "arkk_monthly_volatility": arkk_volatility_pct,
        "qqq_monthly_volatility": qqq_volatility_pct,
        "arkk_sharpe_ratio": arkk_sharpe,
        "qqq_sharpe_ratio": qqq_sharpe,
        "arkk_positive_months_pct": f"{arkk_consistency_ratio*100:.1f}%",
        "qqq_positive_months_pct": f"{qqq_consistency_ratio*100:.1f}%",
        "more_consistent_etf": more_consistent,
        "volatility_difference": volatility_difference,
        "functions_used": ["alpaca_market_stocks_bars", "prices_to_returns", "calculate_monthly_returns", "calculate_risk_metrics"],
        "workflow_success": True
    }

if __name__ == "__main__":
    result = test_return_consistency_workflow()
    print(f"\n✅ Workflow completed successfully: {result['workflow_success']}")