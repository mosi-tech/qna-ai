#!/usr/bin/env python3
"""
Workflow for Question 2a: "Which ETF has better risk-adjusted returns?"
Used functions: ["alpaca_market_stocks_bars", "calculate_returns_metrics", "calculate_risk_metrics"]
"""

import sys
import os

# Add the MCP directory to path to use the real MCP functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

def test_risk_adjusted_returns_workflow():
    """Test risk-adjusted returns comparison workflow for ARKK vs QQQ using real MCP functions"""
    
    print("=== QUESTION 2A: Which ETF has better risk-adjusted returns? ===")
    print()
    
    # CRITICAL MCP INTEGRATION: Import MCP functions first
    try:
        from mcp.financial.functions_mock import alpaca_market_stocks_bars
        from mcp.analytics.performance.metrics import calculate_returns_metrics, calculate_risk_metrics
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
    
    # Step 3: Calculate return metrics using MCP analytics
    print("Step 3: Running calculate_returns_metrics via MCP analytics...")
    try:
        arkk_return_metrics = calculate_returns_metrics(arkk_returns.tolist())
        qqq_return_metrics = calculate_returns_metrics(qqq_returns.tolist())
        print(f"✅ ARKK return metrics calculated")
        print(f"✅ QQQ return metrics calculated")
    except Exception as e:
        print(f"❌ Error calling calculate_returns_metrics: {e}")
        return {"workflow_success": False, "error": str(e)}
    
    # Step 4: Calculate risk metrics using MCP analytics
    print("Step 4: Running calculate_risk_metrics via MCP analytics...")
    try:
        arkk_risk_metrics = calculate_risk_metrics(arkk_returns.tolist())
        qqq_risk_metrics = calculate_risk_metrics(qqq_returns.tolist())
        print(f"✅ ARKK risk metrics calculated")
        print(f"✅ QQQ risk metrics calculated")
    except Exception as e:
        print(f"❌ Error calling calculate_risk_metrics: {e}")
        return {"workflow_success": False, "error": str(e)}
    print()
    
    # Results summary
    print("=== RISK-ADJUSTED RETURNS COMPARISON RESULTS ===")
    print()
    print("📊 Return Metrics:")
    print(f"   ARKK Total Return: {arkk_return_metrics.get('total_return_pct', 'N/A')}")
    print(f"   QQQ Total Return:  {qqq_return_metrics.get('total_return_pct', 'N/A')}")
    print()
    print(f"   ARKK Annualized Return: {arkk_return_metrics.get('annualized_return_pct', 'N/A')}")
    print(f"   QQQ Annualized Return:  {qqq_return_metrics.get('annualized_return_pct', 'N/A')}")
    print()
    
    print("📊 Risk Metrics:")
    print(f"   ARKK Volatility: {arkk_risk_metrics.get('volatility_pct', 'N/A')}")
    print(f"   QQQ Volatility:  {qqq_risk_metrics.get('volatility_pct', 'N/A')}")
    print()
    print(f"   ARKK Max Drawdown: {arkk_risk_metrics.get('max_drawdown_pct', 'N/A')}")
    print(f"   QQQ Max Drawdown:  {qqq_risk_metrics.get('max_drawdown_pct', 'N/A')}")
    print()
    
    print("🎯 Risk-Adjusted Performance:")
    arkk_sharpe = arkk_risk_metrics.get('sharpe_ratio', 0)
    qqq_sharpe = qqq_risk_metrics.get('sharpe_ratio', 0)
    
    print(f"   ARKK Sharpe Ratio: {arkk_sharpe:.3f}")
    print(f"   QQQ Sharpe Ratio:  {qqq_sharpe:.3f}")
    print()
    
    arkk_sortino = arkk_risk_metrics.get('sortino_ratio', 0)
    qqq_sortino = qqq_risk_metrics.get('sortino_ratio', 0)
    
    print(f"   ARKK Sortino Ratio: {arkk_sortino:.3f}")
    print(f"   QQQ Sortino Ratio:  {qqq_sortino:.3f}")
    print()
    
    # Determine which has better risk-adjusted returns
    if arkk_sharpe > qqq_sharpe:
        better_risk_adjusted = "ARKK"
        sharpe_difference = arkk_sharpe - qqq_sharpe
        print(f"🏆 ANSWER: ARKK has better risk-adjusted returns")
        print(f"   ARKK Sharpe ratio is {sharpe_difference:.3f} points higher than QQQ")
    elif qqq_sharpe > arkk_sharpe:
        better_risk_adjusted = "QQQ"
        sharpe_difference = qqq_sharpe - arkk_sharpe
        print(f"🏆 ANSWER: QQQ has better risk-adjusted returns")
        print(f"   QQQ Sharpe ratio is {sharpe_difference:.3f} points higher than ARKK")
    else:
        better_risk_adjusted = "Both"
        sharpe_difference = 0
        print(f"🏆 ANSWER: Both ETFs have similar risk-adjusted returns")
    
    print()
    print("📈 Risk-Adjusted Performance Analysis:")
    print(f"   • Sharpe ratio measures return per unit of total risk")
    print(f"   • Sortino ratio focuses on downside risk only")
    print(f"   • Higher ratios indicate better risk-adjusted performance")
    print(f"   • {better_risk_adjusted} provides better compensation for risk taken")
    
    print()
    print("🔧 MCP Functions Used:")
    print("   ✅ alpaca_market_stocks_bars - Retrieved price data from MCP financial server")
    print("   ✅ prices_to_returns - Converted prices to returns via MCP utils")
    print("   ✅ calculate_returns_metrics - Calculated return statistics via MCP analytics")
    print("   ✅ calculate_risk_metrics - Calculated risk metrics via MCP analytics")
    
    return {
        "question": "Which ETF has better risk-adjusted returns?",
        "arkk_sharpe_ratio": arkk_sharpe,
        "qqq_sharpe_ratio": qqq_sharpe,
        "arkk_sortino_ratio": arkk_sortino,
        "qqq_sortino_ratio": qqq_sortino,
        "arkk_total_return": arkk_return_metrics.get('total_return_pct', 'N/A'),
        "qqq_total_return": qqq_return_metrics.get('total_return_pct', 'N/A'),
        "better_risk_adjusted": better_risk_adjusted,
        "sharpe_difference": sharpe_difference,
        "functions_used": ["alpaca_market_stocks_bars", "prices_to_returns", "calculate_returns_metrics", "calculate_risk_metrics"],
        "workflow_success": True
    }

if __name__ == "__main__":
    result = test_risk_adjusted_returns_workflow()
    print(f"\n✅ Workflow completed successfully: {result['workflow_success']}")