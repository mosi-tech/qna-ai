#!/usr/bin/env python3
"""
Complete Workflow Example: "How did a portfolio with AAPL, MSFT, GOOGL at 40%, 35%, 25% perform over last 10 years?"

This demonstrates the EXACT composable functions needed for this user question.
"""

import sys
import os
from datetime import datetime

# Add analytics to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'analytics'))

from portfolio import (
    # Step 1: Date calculation
    calculate_relative_date_range,
    
    # Step 2: Portfolio calculation  
    calculate_portfolio_returns,
    filter_date_range,
    
    # Step 3: Performance metrics
    calculate_total_return,
    calculate_annualized_return,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    
    # Step 4: Time breakdown
    identify_time_periods,
    
    # Step 5: Comparison (if benchmark provided)
    calculate_alpha,
    calculate_relative_performance
)


def simulate_stock_data():
    """Generate realistic test data for AAPL, MSFT, GOOGL"""
    import random
    from datetime import timedelta
    
    base_date = datetime(2014, 1, 1)  # 10+ years ago
    
    # Starting prices (approximate historical)
    prices = {"AAPL": 75.0, "MSFT": 37.0, "GOOGL": 558.0}
    
    # Generate 10+ years of data
    stock_data = {"AAPL": [], "MSFT": [], "GOOGL": []}
    
    for i in range(3800):  # ~10+ years of data
        date = base_date + timedelta(days=i)
        
        for symbol in ["AAPL", "MSFT", "GOOGL"]:
            # Different characteristics per stock
            if symbol == "AAPL":
                daily_return = random.gauss(0.0015, 0.022)  # ~40% annual, ~35% vol
            elif symbol == "MSFT": 
                daily_return = random.gauss(0.0012, 0.018)  # ~30% annual, ~28% vol
            else:  # GOOGL
                daily_return = random.gauss(0.0010, 0.020)  # ~25% annual, ~32% vol
            
            prices[symbol] *= (1 + daily_return)
            
            stock_data[symbol].append({
                'date': date.strftime('%Y-%m-%d'),
                'close': round(prices[symbol], 2),
                'open': round(prices[symbol] * 0.999, 2),
                'high': round(prices[symbol] * 1.01, 2),
                'low': round(prices[symbol] * 0.99, 2),
                'volume': random.randint(10000000, 50000000)
            })
    
    return stock_data


def answer_user_question():
    """
    USER QUESTION: "How did a portfolio with AAPL, MSFT, GOOGL at 40%, 35%, 25% perform over last 10 years?"
    
    COMPOSABLE WORKFLOW:
    """
    print("🤖 User Question: How did a portfolio with AAPL, MSFT, GOOGL at 40%, 35%, 25% perform over last 10 years?")
    print("\n📋 Breaking down into composable function steps...")
    
    # STEP 1: Calculate "last 10 years" date range
    print("\n1️⃣ Step 1: Calculate date range for 'last 10 years'")
    date_range = calculate_relative_date_range(
        reference_date="today",
        years_back=10
    )
    
    if not date_range["success"]:
        print(f"❌ Date calculation failed: {date_range['error']}")
        return
        
    print(f"✅ Date range: {date_range['start_date']} to {date_range['end_date']} ({date_range['period_description']})")
    
    # STEP 2: Calculate portfolio returns from individual stocks
    print("\n2️⃣ Step 2: Calculate portfolio returns from AAPL, MSFT, GOOGL with 40%, 35%, 25% weights")
    
    # Get historical data (simulated here, would come from MCP financial server)
    stock_data = simulate_stock_data()
    
    portfolio_returns = calculate_portfolio_returns(
        data=stock_data,
        weights={"AAPL": 0.40, "MSFT": 0.35, "GOOGL": 0.25}
    )
    
    if not portfolio_returns["success"]:
        print(f"❌ Portfolio calculation failed: {portfolio_returns['error']}")
        return
        
    print(f"✅ Portfolio returns calculated: {portfolio_returns['num_days']} days of data")
    
    # STEP 3: Filter to the specific 10-year period
    print("\n3️⃣ Step 3: Filter returns to the 10-year period")
    
    filtered_returns = filter_date_range(
        data=portfolio_returns,
        start=date_range["start_date"],
        end=date_range["end_date"]
    )
    
    if not filtered_returns["success"]:
        print(f"❌ Date filtering failed: {filtered_returns['error']}")
        return
        
    print(f"✅ Filtered to 10-year period: {filtered_returns['num_days']} days")
    
    # STEP 4: Calculate core performance metrics
    print("\n4️⃣ Step 4: Calculate performance metrics")
    
    # Total return
    total_return = calculate_total_return(filtered_returns)
    print(f"   📈 Total Return: {total_return['total_return_pct']}")
    
    # Annualized return  
    annual_return = calculate_annualized_return(filtered_returns)
    print(f"   📊 Annualized Return: {annual_return['annualized_return_pct']} per year")
    
    # Volatility
    volatility = calculate_volatility(filtered_returns)
    print(f"   📉 Volatility: {volatility['volatility_pct']}")
    
    # Sharpe ratio
    sharpe = calculate_sharpe_ratio(filtered_returns, risk_free_rate=0.02)
    print(f"   ⚡ Sharpe Ratio: {sharpe['sharpe_ratio']:.3f}")
    
    # Max drawdown
    max_dd = calculate_max_drawdown(filtered_returns)
    print(f"   📉 Max Drawdown: {max_dd['max_drawdown_pct']} (on {max_dd['max_drawdown_date']})")
    
    # STEP 5: Break down performance by year
    print("\n5️⃣ Step 5: Year-by-year breakdown")
    
    yearly_breakdown = identify_time_periods(filtered_returns, period_type="yearly")
    
    if yearly_breakdown["success"]:
        print(f"   📅 Performance by year ({yearly_breakdown['num_periods']} years):")
        for period in yearly_breakdown["periods"]:
            print(f"      {period['period_name']}: {period['total_return']*100:.1f}% ({period['num_days']} days)")
    
    # STEP 6: Summary for user
    print("\n📋 ANSWER SUMMARY:")
    print("="*60)
    print(f"Your portfolio (40% AAPL, 35% MSFT, 25% GOOGL) over the last 10 years:")
    print(f"• Grew by {total_return['total_return_pct']} total ({annual_return['annualized_return_pct']} annually)")
    print(f"• Had {volatility['volatility_pct']} volatility")  
    print(f"• Achieved a Sharpe ratio of {sharpe['sharpe_ratio']:.2f}")
    print(f"• Worst decline was {max_dd['max_drawdown_pct']}")
    if max_dd['recovery_date']:
        print(f"• Recovered from max drawdown by {max_dd['recovery_date']}")
    print("="*60)
    
    # STEP 7: Optional - Compare to benchmark (if S&P 500 data available)
    print("\n6️⃣ Optional Step: Compare to S&P 500 benchmark")
    print("   (Would use calculate_alpha, calculate_relative_performance if benchmark data available)")
    
    print("\n✅ COMPLETE WORKFLOW SUCCESS!")
    print(f"📊 Used {len([f for f in [date_range, portfolio_returns, filtered_returns, total_return, annual_return, volatility, sharpe, max_dd, yearly_breakdown] if f.get('success')])} composable functions")


def list_functions_needed():
    """List all composable functions needed for this workflow"""
    
    functions_used = [
        ("calculate_relative_date_range", "Convert 'last 10 years' to specific dates"),
        ("calculate_portfolio_returns", "Combine AAPL+MSFT+GOOGL with 40%+35%+25% weights"),
        ("filter_date_range", "Extract the specific 10-year period"),
        ("calculate_total_return", "Total growth over the period"),
        ("calculate_annualized_return", "Average annual growth rate"),
        ("calculate_volatility", "Risk/volatility measure"),
        ("calculate_sharpe_ratio", "Risk-adjusted return"),
        ("calculate_max_drawdown", "Worst decline and recovery"),
        ("identify_time_periods", "Year-by-year breakdown")
    ]
    
    optional_functions = [
        ("calculate_alpha", "Alpha vs S&P 500 benchmark"),
        ("calculate_relative_performance", "Outperformance statistics"),
        ("calculate_rolling_metrics", "Rolling 1-year returns")
    ]
    
    print("📋 COMPOSABLE FUNCTIONS FOR USER QUESTION:")
    print("Question: 'How did a portfolio with AAPL, MSFT, GOOGL at 40%, 35%, 25% perform over last 10 years?'")
    print("\n✅ CORE FUNCTIONS NEEDED:")
    for i, (func_name, description) in enumerate(functions_used, 1):
        print(f"   {i}. {func_name}() - {description}")
    
    print("\n🔧 OPTIONAL FUNCTIONS (for enhanced analysis):")
    for i, (func_name, description) in enumerate(optional_functions, 1):
        print(f"   {i}. {func_name}() - {description}")
    
    print(f"\n📊 TOTAL: {len(functions_used)} core functions + {len(optional_functions)} optional = Full analysis")


if __name__ == "__main__":
    print("🚀 COMPLETE COMPOSABLE WORKFLOW DEMONSTRATION")
    print("="*80)
    
    # First show what functions we need
    list_functions_needed()
    
    print("\n" + "="*80)
    
    # Then demonstrate the actual workflow
    answer_user_question()