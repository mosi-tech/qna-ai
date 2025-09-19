"""
Test script for Tier 2 Performance Analysis Tools
"""

import sys
import os
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin')

from mcp.tools.tier_2_performance import (
    ytd_performance,
    long_term_performance, 
    historical_extremes,
    volatility_analysis,
    max_drawdown_tool
)

def test_tier_2_tools():
    """Test all Tier 2 tools with sample data"""
    print("Testing Tier 2 Performance Analysis Tools")
    print("=" * 50)
    
    test_symbol = "AAPL"
    
    # Test 1: YTD Performance
    print("1. Testing YTD Performance...")
    try:
        result = ytd_performance(test_symbol)
        print(f"   Result keys: {list(result.keys())}")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   YTD Return: {result.get('ytd_return', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 2: Long-term Performance
    print("2. Testing Long-term Performance...")
    try:
        result = long_term_performance(test_symbol, years=3)
        print(f"   Status: {'SUCCESS' if result.get('success', True) else 'FAILED'}")
        if result.get('success', True):
            print(f"   3-Year CAGR: {result.get('annualized_return', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 3: Historical Extremes
    print("3. Testing Historical Extremes...")
    try:
        result = historical_extremes(test_symbol, period_type="yearly")
        print(f"   Status: {'SUCCESS' if result.get('success', True) else 'FAILED'}")
        if result.get('success', True):
            best = result.get('best_period', {})
            print(f"   Best Year: {best.get('return', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 4: Volatility Analysis
    print("4. Testing Volatility Analysis...")
    try:
        result = volatility_analysis(test_symbol, period="90d")
        print(f"   Status: {'SUCCESS' if result.get('success', True) else 'FAILED'}")
        if result.get('success', True):
            print(f"   90-day Volatility: {result.get('current_volatility', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 5: Max Drawdown Tool
    print("5. Testing Max Drawdown Tool...")
    try:
        result = max_drawdown_tool(test_symbol, years=5)
        print(f"   Status: {'SUCCESS' if result.get('success', True) else 'FAILED'}")
        if result.get('success', True):
            print(f"   Max Drawdown: {result.get('max_drawdown', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    print("Tier 2 Testing Complete!")

if __name__ == "__main__":
    test_tier_2_tools()