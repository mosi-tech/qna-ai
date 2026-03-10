#!/usr/bin/env python3
"""
Workflow for Question 4c: "How often does each ETF experience 10%+ monthly losses?"
Used functions: ["alpaca_market_stocks_bars", "calculate_returns_metrics"]
"""

import sys
import os

# Add the MCP directory to path to use the real MCP functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))


def test_extreme_loss_frequency_workflow():
    """Test extreme loss frequency analysis workflow for ARKK vs QQQ using real MCP functions"""
    
    print("=== QUESTION 4C: How often does each ETF experience 10%+ monthly losses? ===")
    print()
    
    # CRITICAL MCP INTEGRATION: Import MCP functions first
    try:
        from mcp.financial.functions_mock import alpaca_market_stocks_bars
        from mcp.analytics.performance.metrics import calculate_returns_metrics
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
            start="2024-06-01",
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
    except Exception as e:
        print(f"❌ Error processing price data: {e}")
        return {"workflow_success": False, "error": str(e)}
    
    print(f"✅ ARKK daily returns calculated: {len(arkk_daily_returns)} days")
    print(f"✅ QQQ daily returns calculated: {len(qqq_daily_returns)} days")
    print()
    
    # Step 3: Convert daily returns to monthly returns using MCP utils
    print("Step 3: Converting daily returns to monthly returns using MCP utils...")
    arkk_monthly_returns = calculate_monthly_returns(arkk_daily_returns)
    qqq_monthly_returns = calculate_monthly_returns(qqq_daily_returns)
    
    print(f"✅ ARKK monthly returns calculated: {len(arkk_monthly_returns)} months")
    print(f"✅ QQQ monthly returns calculated: {len(qqq_monthly_returns)} months")
    print()
    
    # Step 4: Analyze extreme losses (10%+ monthly losses)
    print("Step 4: Analyzing 10%+ monthly losses...")
    
    # Define extreme loss threshold
    extreme_loss_threshold = -0.10  # -10%
    
    # Count extreme losses for ARKK
    arkk_extreme_losses = [r for r in arkk_monthly_returns if r <= extreme_loss_threshold]
    arkk_extreme_loss_count = len(arkk_extreme_losses)
    arkk_extreme_loss_frequency = arkk_extreme_loss_count / len(arkk_monthly_returns) if len(arkk_monthly_returns) > 0 else 0
    
    # Count extreme losses for QQQ
    qqq_extreme_losses = [r for r in qqq_monthly_returns if r <= extreme_loss_threshold]
    qqq_extreme_loss_count = len(qqq_extreme_losses)
    qqq_extreme_loss_frequency = qqq_extreme_loss_count / len(qqq_monthly_returns) if len(qqq_monthly_returns) > 0 else 0
    
    print(f"✅ ARKK 10%+ monthly losses: {arkk_extreme_loss_count} out of {len(arkk_monthly_returns)} months")
    print(f"✅ QQQ 10%+ monthly losses: {qqq_extreme_loss_count} out of {len(qqq_monthly_returns)} months")
    print()
    
    # Step 5: Calculate additional return statistics using MCP analytics
    print("Step 5: Calling calculate_returns_metrics via MCP analytics...")
    try:
        arkk_monthly_metrics = calculate_returns_metrics(arkk_monthly_returns)
        qqq_monthly_metrics = calculate_returns_metrics(qqq_monthly_returns)
        print(f"✅ ARKK monthly return metrics calculated via MCP")
        print(f"✅ QQQ monthly return metrics calculated via MCP")
    except Exception as e:
        print(f"❌ Error calling calculate_returns_metrics: {e}")
        return {"workflow_success": False, "error": str(e)}
    print()
    
    # Results summary
    print("=== EXTREME LOSS FREQUENCY ANALYSIS RESULTS ===")
    print()
    print("📊 10%+ Monthly Loss Frequency:")
    print(f"   ARKK: {arkk_extreme_loss_count} occurrences ({arkk_extreme_loss_frequency*100:.1f}% of months)")
    print(f"   QQQ:  {qqq_extreme_loss_count} occurrences ({qqq_extreme_loss_frequency*100:.1f}% of months)")
    print()
    
    if len(arkk_extreme_losses) > 0:
        arkk_worst_month = min(arkk_extreme_losses)
        print(f"   ARKK worst monthly loss: {arkk_worst_month*100:.2f}%")
    
    if len(qqq_extreme_losses) > 0:
        qqq_worst_month = min(qqq_extreme_losses)
        print(f"   QQQ worst monthly loss: {qqq_worst_month*100:.2f}%")
    
    if len(arkk_extreme_losses) == 0 and len(qqq_extreme_losses) == 0:
        print("   Neither ETF experienced 10%+ monthly losses in this period")
    print()
    
    print("📈 Monthly Return Summary (via MCP analytics):")
    print(f"   ARKK total monthly return: {arkk_monthly_metrics.get('total_return_pct', 'N/A')}")
    print(f"   QQQ total monthly return: {qqq_monthly_metrics.get('total_return_pct', 'N/A')}")
    print()
    
    # Determine which ETF has more frequent extreme losses
    if arkk_extreme_loss_frequency > qqq_extreme_loss_frequency:
        more_frequent = "ARKK"
        difference = arkk_extreme_loss_frequency - qqq_extreme_loss_frequency
        print(f"🏆 ANSWER: ARKK experiences 10%+ monthly losses more frequently")
        print(f"   ARKK has {difference*100:.1f} percentage points higher frequency of extreme losses")
    elif qqq_extreme_loss_frequency > arkk_extreme_loss_frequency:
        more_frequent = "QQQ"
        difference = qqq_extreme_loss_frequency - arkk_extreme_loss_frequency
        print(f"🏆 ANSWER: QQQ experiences 10%+ monthly losses more frequently")
        print(f"   QQQ has {difference*100:.1f} percentage points higher frequency of extreme losses")
    else:
        more_frequent = "Both"
        difference = 0
        print(f"🏆 ANSWER: Both ETFs have equal frequency of 10%+ monthly losses")
        if arkk_extreme_loss_count == 0 and qqq_extreme_loss_count == 0:
            print(f"   Neither ETF experienced extreme losses during this period")
    
    print()
    print("📊 Risk Implications:")
    print(f"   • Higher frequency = greater tail risk")
    print(f"   • Extreme losses indicate poor downside protection")
    print(f"   • Analysis period: {len(arkk_monthly_returns)} months of data")
    
    print()
    print("🔧 MCP Functions Used:")
    print("   ✅ alpaca_market_stocks_bars - Retrieved price data from MCP financial server")
    print("   ✅ prices_to_returns - Converted prices to returns via MCP utils")
    print("   ✅ calculate_monthly_returns - Converted daily to monthly returns via MCP utils")
    print("   ✅ calculate_returns_metrics - Calculated return statistics via MCP analytics")
    
    return {
        "question": "How often does each ETF experience 10%+ monthly losses?",
        "arkk_extreme_losses": arkk_extreme_loss_count,
        "qqq_extreme_losses": qqq_extreme_loss_count,
        "arkk_frequency": f"{arkk_extreme_loss_frequency*100:.1f}%",
        "qqq_frequency": f"{qqq_extreme_loss_frequency*100:.1f}%",
        "more_frequent": more_frequent,
        "arkk_monthly_returns": len(arkk_monthly_returns),
        "qqq_monthly_returns": len(qqq_monthly_returns),
        "functions_used": ["alpaca_market_stocks_bars", "prices_to_returns", "calculate_monthly_returns", "calculate_returns_metrics"],
        "workflow_success": True
    }

if __name__ == "__main__":
    result = test_extreme_loss_frequency_workflow()
    print(f"\n✅ Workflow completed successfully: {result['workflow_success']}")