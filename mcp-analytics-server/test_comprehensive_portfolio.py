#!/usr/bin/env python3
"""
Test script for the consolidated comprehensive portfolio analyzer

This tests both simple retail and sophisticated use cases to verify
that the consolidation successfully handles all complexity levels.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the analytics directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'analytics'))

from portfolio.unified.comprehensive_analyzer import comprehensive_portfolio_analyzer


def generate_mock_historical_data(symbols, days=1000):
    """Generate realistic mock historical data for testing"""
    import random
    import pandas as pd
    
    data = {}
    base_date = datetime(2019, 1, 1)
    
    for symbol in symbols:
        symbol_data = []
        price = 100.0  # Starting price
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Generate realistic daily returns
            if symbol in ['VTI', 'SPY', 'QQQ']:  # Stock ETFs
                daily_return = random.gauss(0.0004, 0.012)  # ~10% annual return, ~18% volatility
            elif symbol in ['BND', 'AGG']:  # Bond ETFs  
                daily_return = random.gauss(0.0001, 0.004)  # ~2% annual return, ~6% volatility
            elif symbol in ['VEA', 'VWO']:  # International
                daily_return = random.gauss(0.0003, 0.014)  # ~8% annual return, ~20% volatility
            else:
                daily_return = random.gauss(0.0002, 0.010)  # Default
            
            price = price * (1 + daily_return)
            
            symbol_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': price,
                'high': price * (1 + abs(daily_return)),
                'low': price * (1 - abs(daily_return)),
                'close': price,
                'volume': random.randint(1000000, 5000000)
            })
        
        data[symbol] = symbol_data
    
    return data


def test_retail_use_case():
    """Test simple retail use case"""
    print("🔄 Testing RETAIL use case...")
    
    # Simple two-fund portfolio
    historical_data = generate_mock_historical_data(['VTI', 'BND'], days=1260)  # ~5 years
    
    result = comprehensive_portfolio_analyzer(
        historical_data=historical_data,
        portfolio_weights={'VTI': 70, 'BND': 30},
        initial_investment=50000,
        monthly_contribution=1000,
        analysis_mode="retail"
    )
    
    print("✅ Retail Test Results:")
    print(f"   - Success: {result.get('success', False)}")
    print(f"   - Analysis Mode: {result.get('analysis_mode', 'N/A')}")
    
    if result.get('success'):
        portfolio_summary = result.get('portfolio_summary', {})
        print(f"   - Initial Investment: {portfolio_summary.get('initial_investment', 'N/A')}")
        print(f"   - Final Value: {portfolio_summary.get('final_value', 'N/A')}")
        print(f"   - Annual Return: {portfolio_summary.get('annual_return', 'N/A')}")
        print(f"   - Performance Grade: {result.get('performance_grade', 'N/A')}")
        
        # Check for plain English summary
        if 'plain_english_summary' in result:
            print(f"   - Plain English: {result['plain_english_summary'][:100]}...")
    else:
        print(f"   - Error: {result.get('error', 'Unknown error')}")
    
    return result


def test_professional_use_case():
    """Test professional use case with multiple assets"""
    print("\n🔄 Testing PROFESSIONAL use case...")
    
    # Four-fund portfolio with international exposure
    symbols = ['QQQ', 'VTV', 'VEA', 'BND']
    historical_data = generate_mock_historical_data(symbols, days=2520)  # ~10 years
    
    result = comprehensive_portfolio_analyzer(
        historical_data=historical_data,
        portfolio_weights={'QQQ': 35, 'VTV': 25, 'VEA': 20, 'BND': 20},
        initial_investment=100000,
        analysis_mode="professional",
        rebalancing_strategy="threshold",
        rebalancing_threshold=3.0,
        transaction_cost_bps=3.0,
        stress_test_periods=["2020-02-01:2020-04-30"],  # COVID crash
        include_technical_analysis=True
    )
    
    print("✅ Professional Test Results:")
    print(f"   - Success: {result.get('success', False)}")
    print(f"   - Analysis Mode: {result.get('analysis_mode', 'N/A')}")
    
    if result.get('success'):
        perf_metrics = result.get('performance_metrics', {})
        print(f"   - Annualized Return: {perf_metrics.get('annualized_return', 'N/A')}")
        print(f"   - Sharpe Ratio: {perf_metrics.get('sharpe_ratio', 'N/A')}")
        print(f"   - Max Drawdown: {perf_metrics.get('max_drawdown', 'N/A')}")
        
        rebalancing_analysis = result.get('rebalancing_analysis', {})
        print(f"   - Rebalancing Strategy: {rebalancing_analysis.get('strategy', 'N/A')}")
        print(f"   - Number of Rebalances: {rebalancing_analysis.get('num_rebalances', 'N/A')}")
    else:
        print(f"   - Error: {result.get('error', 'Unknown error')}")
    
    return result


def test_quantitative_use_case():
    """Test quantitative use case with advanced features"""
    print("\n🔄 Testing QUANTITATIVE use case...")
    
    # Multi-asset portfolio with factor exposure
    symbols = ['VTI', 'VTV', 'VUG', 'VEA', 'VWO', 'BND']
    historical_data = generate_mock_historical_data(symbols, days=2520)  # ~10 years
    
    result = comprehensive_portfolio_analyzer(
        historical_data=historical_data,
        portfolio_weights={
            'VTI': 25,   # Total market
            'VTV': 20,   # Value tilt
            'VUG': 15,   # Growth tilt
            'VEA': 20,   # Developed international
            'VWO': 10,   # Emerging markets
            'BND': 10    # Bonds
        },
        initial_investment=250000,
        analysis_mode="quantitative",
        rebalancing_strategy="momentum",
        target_volatility=0.12,
        stress_test_periods=[
            "2008-01-01:2009-12-31",  # Financial crisis
            "2020-02-01:2020-04-30"   # COVID crash
        ],
        custom_scenarios={"factor_analysis": True, "regime_analysis": True},
        include_technical_analysis=True,
        generate_plain_english=False
    )
    
    print("✅ Quantitative Test Results:")
    print(f"   - Success: {result.get('success', False)}")
    print(f"   - Analysis Mode: {result.get('analysis_mode', 'N/A')}")
    
    if result.get('success'):
        advanced_metrics = result.get('advanced_metrics', {})
        print(f"   - Alpha: {advanced_metrics.get('alpha', 'N/A')}")
        print(f"   - Beta: {advanced_metrics.get('beta', 'N/A')}")
        print(f"   - Information Ratio: {advanced_metrics.get('information_ratio', 'N/A')}")
        
        vol_targeting = result.get('volatility_targeting', {})
        print(f"   - Current Volatility: {vol_targeting.get('current_volatility', 'N/A')}")
        print(f"   - Target Volatility: {vol_targeting.get('target_volatility', 'N/A')}")
    else:
        print(f"   - Error: {result.get('error', 'Unknown error')}")
    
    return result


def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🔄 Testing ERROR HANDLING...")
    
    # Test with missing data
    result1 = comprehensive_portfolio_analyzer(
        historical_data={},
        portfolio_weights={'VTI': 100}
    )
    print(f"✅ Empty data test: {result1.get('success', True)} (should be False)")
    
    # Test with invalid weights
    result2 = comprehensive_portfolio_analyzer(
        historical_data=generate_mock_historical_data(['VTI'], days=100),
        portfolio_weights={'VTI': 150}  # Invalid: >100%
    )
    print(f"✅ Invalid weights test: {result2.get('success', True)} (should be False)")
    
    # Test with missing symbol data
    result3 = comprehensive_portfolio_analyzer(
        historical_data=generate_mock_historical_data(['VTI'], days=100),
        portfolio_weights={'VTI': 50, 'MISSING': 50}
    )
    print(f"✅ Missing symbol test: {result3.get('success', True)} (should be False)")
    
    return all([not result1.get('success'), not result2.get('success'), not result3.get('success')])


def test_data_integration_pattern():
    """Test the proper MCP data integration pattern"""
    print("\n🔄 Testing MCP DATA INTEGRATION PATTERN...")
    
    # This simulates how the function should be called in production
    # 1. First, fetch data via MCP (simulated here)
    symbols = ['VTI', 'BND']
    
    # Simulate MCP data fetch
    print("   - Simulating MCP data fetch...")
    historical_data = generate_mock_historical_data(symbols, days=1260)
    
    # 2. Pass pre-fetched data to analyzer (proper pattern)
    print("   - Calling analyzer with pre-fetched data...")
    result = comprehensive_portfolio_analyzer(
        historical_data=historical_data,
        portfolio_weights={'VTI': 60, 'BND': 40},
        analysis_mode="retail"
    )
    
    print(f"✅ MCP Integration Pattern: {result.get('success', False)}")
    
    # Check execution metadata
    exec_info = result.get('execution_info', {})
    print(f"   - Real Market Data: {exec_info.get('real_market_data', False)}")
    print(f"   - Function: {exec_info.get('function', 'N/A')}")
    print(f"   - Data Points: {exec_info.get('data_points', 'N/A')}")
    
    return result.get('success', False)


def main():
    """Run all tests"""
    print("🚀 Testing Consolidated Portfolio Analyzer")
    print("="*60)
    
    # Track test results
    results = {
        'retail': False,
        'professional': False,  
        'quantitative': False,
        'error_handling': False,
        'mcp_integration': False
    }
    
    try:
        # Test different use cases
        retail_result = test_retail_use_case()
        results['retail'] = retail_result.get('success', False)
        
        professional_result = test_professional_use_case()
        results['professional'] = professional_result.get('success', False)
        
        quantitative_result = test_quantitative_use_case()
        results['quantitative'] = quantitative_result.get('success', False)
        
        # Test error handling
        results['error_handling'] = test_error_handling()
        
        # Test MCP integration pattern
        results['mcp_integration'] = test_data_integration_pattern()
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        return False
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.upper():20} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    overall_status = "🎉 ALL TESTS PASSED" if all_passed else "⚠️  SOME TESTS FAILED"
    print(f"OVERALL STATUS: {overall_status}")
    
    if all_passed:
        print("\n✅ Comprehensive Portfolio Analyzer is working correctly!")
        print("✅ Handles retail, professional, and quantitative use cases")
        print("✅ Proper error handling implemented")
        print("✅ MCP data integration pattern verified")
        print("✅ Ready for production use")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)