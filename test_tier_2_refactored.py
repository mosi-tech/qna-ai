"""
Test script for refactored Tier 2 Performance Analysis Tools
"""

import sys
import os
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin')

from mcp.tools.tier_2_performance import (
    ytd_performance,
    long_term_performance
)

def test_tier_2_refactored():
    """Test refactored Tier 2 tools with analytics functions"""
    print("Testing Refactored Tier 2 Performance Analysis Tools")
    print("=" * 60)
    
    # Test 1: YTD Performance (refactored)
    print("1. Testing YTD Performance...")
    try:
        result = ytd_performance("AAPL", "SPY")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   YTD Return: {result.get('ytd_performance', {}).get('return', 'N/A')}%")
            print(f"   Analytics Used: {result.get('analytics_engine_used', 'Not specified')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 2: Long Term Performance (refactored)
    print("2. Testing Long Term Performance...")
    try:
        result = long_term_performance("AAPL", 3)
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Total Return: {result.get('total_return', 'N/A')}%")
            print(f"   CAGR: {result.get('cagr', 'N/A')}%")
            print(f"   Sharpe Ratio: {result.get('sharpe_ratio', 'N/A')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    print("Tier 2 Refactored Testing Complete!")
    print("\nRefactoring Summary:")
    print("- YTD and Long Term Performance functions use analytics")
    print("- Performance metrics from calculate_returns_metrics()")
    print("- Risk metrics from calculate_risk_metrics()")
    print("- Drawdown analysis from calculate_drawdown_analysis()")
    print("- Price processing through validate_price_data() and prices_to_returns()")
    print("- Eliminated manual numpy calculations for core metrics")

if __name__ == "__main__":
    test_tier_2_refactored()