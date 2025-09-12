#!/usr/bin/env python3
"""
Test Composable Portfolio Functions

Test that atomic functions compose correctly for Q&A workflows
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the analytics directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'analytics'))

from portfolio import (
    calculate_portfolio_returns,
    filter_date_range,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    identify_bear_markets,
    resample_frequency,
    calculate_volatility
)


def generate_test_data():
    """Generate realistic test data"""
    import random
    
    base_date = datetime(2019, 1, 1)
    spy_data = []
    bnd_data = []
    
    spy_price = 280.0
    bnd_price = 80.0
    
    for i in range(1500):  # ~6 years
        date = base_date + timedelta(days=i)
        
        # SPY: Higher return, higher volatility
        spy_return = random.gauss(0.0008, 0.015)  # ~20% annual return, ~24% volatility
        spy_price *= (1 + spy_return)
        
        # BND: Lower return, lower volatility  
        bnd_return = random.gauss(0.0002, 0.005)  # ~5% annual return, ~8% volatility
        bnd_price *= (1 + bnd_return)
        
        spy_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'close': spy_price,
            'open': spy_price * 0.999,
            'high': spy_price * 1.002,
            'low': spy_price * 0.998,
            'volume': random.randint(50000000, 150000000)
        })
        
        bnd_data.append({
            'date': date.strftime('%Y-%m-%d'), 
            'close': bnd_price,
            'open': bnd_price * 0.9995,
            'high': bnd_price * 1.001,
            'low': bnd_price * 0.999,
            'volume': random.randint(1000000, 5000000)
        })
    
    return {"SPY": spy_data, "BND": bnd_data}


def test_workflow_1_sharpe_ratio_2020():
    """Test: What was the Sharpe ratio of a 60/40 portfolio in 2020?"""
    print("🔄 Testing Workflow 1: Sharpe ratio of 60/40 portfolio in 2020")
    
    # Generate data
    data = generate_test_data()
    
    # Step 1: Calculate portfolio returns
    print("   Step 1: Calculate portfolio returns...")
    returns_result = calculate_portfolio_returns(
        data=data,
        weights={"SPY": 0.6, "BND": 0.4}
    )
    
    if not returns_result["success"]:
        print(f"   ❌ Step 1 failed: {returns_result['error']}")
        return False
    
    print(f"   ✅ Step 1: Got {returns_result['num_days']} days of returns")
    
    # Step 2: Filter to 2020
    print("   Step 2: Filter to 2020...")
    filtered_result = filter_date_range(
        data=returns_result,
        start="2020-01-01", 
        end="2020-12-31"
    )
    
    if not filtered_result["success"]:
        print(f"   ❌ Step 2 failed: {filtered_result['error']}")
        return False
    
    print(f"   ✅ Step 2: Filtered to {filtered_result['num_days']} days")
    
    # Step 3: Calculate Sharpe ratio
    print("   Step 3: Calculate Sharpe ratio...")
    sharpe_result = calculate_sharpe_ratio(
        returns=filtered_result,
        risk_free_rate=0.02
    )
    
    if not sharpe_result["success"]:
        print(f"   ❌ Step 3 failed: {sharpe_result['error']}")
        return False
    
    print(f"   ✅ Step 3: Sharpe ratio = {sharpe_result['sharpe_ratio']:.3f}")
    
    # Workflow complete
    print("   🎉 Workflow 1 SUCCESS: Functions composed correctly!")
    print(f"   📊 Result: 60/40 portfolio had Sharpe ratio of {sharpe_result['sharpe_ratio']:.3f} in 2020")
    
    return True


def test_workflow_2_crisis_drawdown():
    """Test: What was the maximum drawdown during 2020 (COVID crash)?"""
    print("\n🔄 Testing Workflow 2: Max drawdown during 2020 COVID crash")
    
    # Generate data
    data = generate_test_data()
    
    # Step 1: Calculate portfolio returns
    returns_result = calculate_portfolio_returns(
        data=data,
        weights={"SPY": 0.7, "BND": 0.3}  # More aggressive portfolio
    )
    
    if not returns_result["success"]:
        print(f"   ❌ Failed: {returns_result['error']}")
        return False
    
    # Step 2: Filter to COVID period
    covid_result = filter_date_range(
        data=returns_result,
        start="2020-02-01",
        end="2020-05-31"
    )
    
    if not covid_result["success"]:
        print(f"   ❌ Failed: {covid_result['error']}")
        return False
    
    # Step 3: Calculate max drawdown
    drawdown_result = calculate_max_drawdown(returns=covid_result)
    
    if not drawdown_result["success"]:
        print(f"   ❌ Failed: {drawdown_result['error']}")
        return False
    
    print(f"   ✅ Max drawdown during COVID: {drawdown_result['max_drawdown_pct']}")
    print(f"   📅 Occurred on: {drawdown_result['max_drawdown_date']}")
    if drawdown_result['recovery_date']:
        print(f"   🔄 Recovered by: {drawdown_result['recovery_date']}")
    
    print("   🎉 Workflow 2 SUCCESS!")
    return True


def test_workflow_3_bear_markets():
    """Test: How many bear markets has the portfolio experienced?"""
    print("\n🔄 Testing Workflow 3: Bear market identification")
    
    # Generate data
    data = generate_test_data()
    
    # Step 1: Calculate portfolio returns
    returns_result = calculate_portfolio_returns(
        data=data,
        weights={"SPY": 1.0}  # 100% stock portfolio
    )
    
    if not returns_result["success"]:
        print(f"   ❌ Failed: {returns_result['error']}")
        return False
    
    # Step 2: Identify bear markets
    bear_result = identify_bear_markets(
        returns=returns_result,
        threshold=-0.20  # -20% drawdown
    )
    
    if not bear_result["success"]:
        print(f"   ❌ Failed: {bear_result['error']}")
        return False
    
    print(f"   ✅ Found {bear_result['num_bear_markets']} bear markets")
    print(f"   📊 Total bear market days: {bear_result['total_bear_days']}")
    
    for i, bear in enumerate(bear_result['bear_markets']):
        print(f"   📉 Bear #{i+1}: {bear['start_date']} to {bear['end_date']} "
              f"(max drawdown: {bear['max_drawdown_pct']})")
    
    print("   🎉 Workflow 3 SUCCESS!")
    return True


def test_workflow_4_volatility_comparison():
    """Test: Compare daily vs monthly volatility"""
    print("\n🔄 Testing Workflow 4: Daily vs monthly volatility comparison")
    
    # Generate data
    data = generate_test_data()
    
    # Step 1: Calculate portfolio returns
    returns_result = calculate_portfolio_returns(
        data=data,
        weights={"SPY": 0.6, "BND": 0.4}
    )
    
    if not returns_result["success"]:
        print(f"   ❌ Failed: {returns_result['error']}")
        return False
    
    # Step 2: Calculate daily volatility
    daily_vol_result = calculate_volatility(returns=returns_result, annualized=True)
    
    if not daily_vol_result["success"]:
        print(f"   ❌ Daily vol failed: {daily_vol_result['error']}")
        return False
    
    # Step 3: Resample to monthly
    monthly_result = resample_frequency(
        data=returns_result,
        frequency="monthly"
    )
    
    if not monthly_result["success"]:
        print(f"   ❌ Resampling failed: {monthly_result['error']}")
        return False
    
    # Step 4: Calculate monthly volatility
    monthly_vol_result = calculate_volatility(returns=monthly_result, annualized=True)
    
    if not monthly_vol_result["success"]:
        print(f"   ❌ Monthly vol failed: {monthly_vol_result['error']}")
        return False
    
    print(f"   ✅ Daily volatility: {daily_vol_result['volatility_pct']}")
    print(f"   ✅ Monthly volatility: {monthly_vol_result['volatility_pct']}")
    print(f"   📊 Based on {daily_vol_result['num_observations']} daily / {monthly_vol_result['num_observations']} monthly observations")
    
    print("   🎉 Workflow 4 SUCCESS!")
    return True


def main():
    """Test all composable workflows"""
    print("🚀 Testing Composable Portfolio Functions")
    print("="*60)
    
    results = {
        'workflow_1_sharpe': False,
        'workflow_2_drawdown': False, 
        'workflow_3_bear_markets': False,
        'workflow_4_volatility': False
    }
    
    try:
        results['workflow_1_sharpe'] = test_workflow_1_sharpe_ratio_2020()
        results['workflow_2_drawdown'] = test_workflow_2_crisis_drawdown()
        results['workflow_3_bear_markets'] = test_workflow_3_bear_markets()
        results['workflow_4_volatility'] = test_workflow_4_volatility_comparison()
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        return False
    
    # Print final results
    print("\n" + "="*60)
    print("📊 COMPOSABILITY TEST RESULTS")
    print("="*60)
    
    all_passed = True
    for workflow_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{workflow_name.upper():25} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    overall_status = "🎉 ALL WORKFLOWS PASSED" if all_passed else "⚠️  SOME WORKFLOWS FAILED"
    print(f"OVERALL STATUS: {overall_status}")
    
    if all_passed:
        print("\n✅ Atomic functions compose correctly!")
        print("✅ Q&A workflows map to function chains")
        print("✅ Each function handles ONE specific task")
        print("✅ Functions chain together for complex analyses")
        print("✅ Ready for MCP Q&A integration!")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)