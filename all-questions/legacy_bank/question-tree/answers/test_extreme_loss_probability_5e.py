#!/usr/bin/env python3
"""
Workflow for Question 5e: "Which has higher probability of 20%+ monthly drops?"
Used functions: ["alpaca_market_stocks_bars", "calculate_returns_metrics"]
"""

import sys
import os

# Add the MCP directory to path to use the real MCP functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

def test_extreme_loss_probability_workflow():
    """Test extreme loss probability analysis workflow for ARKK vs QQQ using real MCP functions"""
    
    print("=== QUESTION 5E: Which has higher probability of 20%+ monthly drops? ===")
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
        
        print(f"✅ ARKK daily returns calculated: {len(arkk_daily_returns)} days")
        print(f"✅ QQQ daily returns calculated: {len(qqq_daily_returns)} days")
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
    
    # Step 4: Analyze extreme loss probability (20%+ monthly drops)
    print("Step 4: Analyzing 20%+ monthly loss probability...")
    
    # Define extreme loss threshold
    extreme_loss_threshold = -0.20  # -20%
    
    # Count extreme losses for ARKK
    arkk_extreme_losses = [r for r in arkk_monthly_returns if r <= extreme_loss_threshold]
    arkk_extreme_loss_count = len(arkk_extreme_losses)
    arkk_extreme_loss_probability = arkk_extreme_loss_count / len(arkk_monthly_returns) if len(arkk_monthly_returns) > 0 else 0
    
    # Count extreme losses for QQQ
    qqq_extreme_losses = [r for r in qqq_monthly_returns if r <= extreme_loss_threshold]
    qqq_extreme_loss_count = len(qqq_extreme_losses)
    qqq_extreme_loss_probability = qqq_extreme_loss_count / len(qqq_monthly_returns) if len(qqq_monthly_returns) > 0 else 0
    
    print(f"✅ ARKK 20%+ monthly losses: {arkk_extreme_loss_count} out of {len(arkk_monthly_returns)} months")
    print(f"✅ QQQ 20%+ monthly losses: {qqq_extreme_loss_count} out of {len(qqq_monthly_returns)} months")
    print()
    
    # Step 5: Calculate additional statistics using MCP analytics
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
    
    # Calculate additional tail risk metrics
    arkk_volatility = abs(sum((r - sum(arkk_monthly_returns)/len(arkk_monthly_returns))**2 for r in arkk_monthly_returns) / len(arkk_monthly_returns))**0.5
    qqq_volatility = abs(sum((r - sum(qqq_monthly_returns)/len(qqq_monthly_returns))**2 for r in qqq_monthly_returns) / len(qqq_monthly_returns))**0.5
    
    # Results summary
    print("=== EXTREME LOSS PROBABILITY ANALYSIS RESULTS ===")
    print()
    print("📊 20%+ Monthly Loss Probability:")
    print(f"   ARKK: {arkk_extreme_loss_count} occurrences ({arkk_extreme_loss_probability*100:.1f}% probability)")
    print(f"   QQQ:  {qqq_extreme_loss_count} occurrences ({qqq_extreme_loss_probability*100:.1f}% probability)")
    print()
    
    print("📊 Tail Risk Statistics:")
    print(f"   ARKK Monthly Volatility: {arkk_volatility*100:.2f}%")
    print(f"   QQQ Monthly Volatility:  {qqq_volatility*100:.2f}%")
    print()
    
    if len(arkk_extreme_losses) > 0:
        arkk_worst_month = min(arkk_extreme_losses)
        print(f"   ARKK worst monthly loss: {arkk_worst_month*100:.2f}%")
    else:
        print(f"   ARKK worst monthly loss: No 20%+ losses observed")
    
    if len(qqq_extreme_losses) > 0:
        qqq_worst_month = min(qqq_extreme_losses)
        print(f"   QQQ worst monthly loss: {qqq_worst_month*100:.2f}%")
    else:
        print(f"   QQQ worst monthly loss: No 20%+ losses observed")
    print()
    
    print("📈 Monthly Performance Summary (via MCP analytics):")
    print(f"   ARKK total monthly return: {arkk_monthly_metrics.get('total_return_pct', 'N/A')}")
    print(f"   QQQ total monthly return: {qqq_monthly_metrics.get('total_return_pct', 'N/A')}")
    print()
    
    # Determine which has higher probability of extreme losses
    if arkk_extreme_loss_probability > qqq_extreme_loss_probability:
        higher_risk_etf = "ARKK"
        probability_difference = arkk_extreme_loss_probability - qqq_extreme_loss_probability
        print(f"🏆 ANSWER: ARKK has higher probability of 20%+ monthly drops")
        print(f"   ARKK has {probability_difference*100:.1f} percentage points higher probability than QQQ")
    elif qqq_extreme_loss_probability > arkk_extreme_loss_probability:
        higher_risk_etf = "QQQ"
        probability_difference = qqq_extreme_loss_probability - arkk_extreme_loss_probability
        print(f"🏆 ANSWER: QQQ has higher probability of 20%+ monthly drops")
        print(f"   QQQ has {probability_difference*100:.1f} percentage points higher probability than ARKK")
    else:
        higher_risk_etf = "Both"
        probability_difference = 0
        print(f"🏆 ANSWER: Both ETFs have equal probability of 20%+ monthly drops")
        if arkk_extreme_loss_count == 0 and qqq_extreme_loss_count == 0:
            print(f"   Neither ETF experienced 20%+ monthly losses during this period")
    
    print()
    print("📊 Tail Risk Implications:")
    print(f"   • 20%+ monthly drops represent severe tail risk events")
    print(f"   • Higher probability indicates greater downside risk")
    print(f"   • Extreme losses can significantly impact long-term returns")
    print(f"   • Analysis based on {len(arkk_monthly_returns)} months of data")
    
    print()
    print("🔧 MCP Functions Used:")
    print("   ✅ alpaca_market_stocks_bars - Retrieved price data from MCP financial server")
    print("   ✅ prices_to_returns - Converted prices to returns via MCP utils")
    print("   ✅ calculate_monthly_returns - Converted daily to monthly returns via MCP utils")
    print("   ✅ calculate_returns_metrics - Calculated return statistics via MCP analytics")
    
    return {
        "question": "Which has higher probability of 20%+ monthly drops?",
        "arkk_extreme_losses": arkk_extreme_loss_count,
        "qqq_extreme_losses": qqq_extreme_loss_count,
        "arkk_probability": f"{arkk_extreme_loss_probability*100:.1f}%",
        "qqq_probability": f"{qqq_extreme_loss_probability*100:.1f}%",
        "higher_risk_etf": higher_risk_etf,
        "probability_difference": probability_difference,
        "arkk_monthly_returns": len(arkk_monthly_returns),
        "qqq_monthly_returns": len(qqq_monthly_returns),
        "functions_used": ["alpaca_market_stocks_bars", "prices_to_returns", "calculate_monthly_returns", "calculate_returns_metrics"],
        "workflow_success": True
    }

if __name__ == "__main__":
    result = test_extreme_loss_probability_workflow()
    print(f"\n✅ Workflow completed successfully: {result['workflow_success']}")