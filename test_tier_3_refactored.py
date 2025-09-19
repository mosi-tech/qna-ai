"""
Test script for refactored Tier 3 Scenario Analysis Tools
"""

import sys
import os
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin')

from mcp.tools.tier_3_scenario_analysis import (
    time_machine_calculator,
    dca_simulator,
    crisis_investment_tool,
    perfect_timing_tool
)

def test_tier_3_refactored():
    """Test all Tier 3 tools with analytics refactoring"""
    print("Testing Refactored Tier 3 Scenario Analysis Tools")
    print("=" * 60)
    
    # Test 1: Time Machine Calculator (already refactored)
    print("1. Testing Time Machine Calculator...")
    try:
        result = time_machine_calculator("AAPL", "2020-01-01", 10000, True)
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Total Return: {result.get('total_return', 'N/A')}%")
            print(f"   Analytics Used: {result.get('analytics_functions_used', [])}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 2: DCA Simulator (refactored)
    print("2. Testing DCA Simulator...")
    try:
        result = dca_simulator("AAPL", 500, "2022-01-01", "monthly")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Total Return: {result.get('total_return', 'N/A')}%")
            print(f"   Analytics Used: {result.get('analytics_functions_used', [])}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 3: Crisis Investment Tool (refactored)
    print("3. Testing Crisis Investment Tool...")
    try:
        result = crisis_investment_tool("SPY", "2020_covid_crash", "bottom")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Total Return: {result.get('total_return', 'N/A')}%")
            print(f"   Analytics Used: {result.get('analytics_functions_used', [])}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 4: Perfect Timing Tool (refactored)  
    print("4. Testing Perfect Timing Tool...")
    try:
        result = perfect_timing_tool("AAPL", 2, "annual")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Perfect Timing Return: {result.get('perfect_timing_return', 'N/A')}%")
            print(f"   Buy Hold Return: {result.get('buy_hold_return', 'N/A')}%")
            print(f"   Analytics Used: {result.get('analytics_functions_used', [])}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    print("Tier 3 Refactored Testing Complete!")
    print("\nRefactoring Summary:")
    print("- All tools now use validate_price_data() and prices_to_returns()")
    print("- Performance metrics from calculate_returns_metrics()")
    print("- Risk metrics from calculate_risk_metrics()")
    print("- Drawdown analysis from calculate_drawdown_analysis()")
    print("- Eliminated manual numpy calculations")

if __name__ == "__main__":
    test_tier_3_refactored()