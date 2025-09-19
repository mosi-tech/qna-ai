"""
Test script for Tier 3 Scenario Analysis Tools
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

def test_tier_3_tools():
    """Test all Tier 3 tools with sample data"""
    print("Testing Tier 3 Scenario Analysis Tools")
    print("=" * 50)
    
    test_symbol = "AAPL"
    
    # Test 1: Time Machine Calculator
    print("1. Testing Time Machine Calculator...")
    try:
        result = time_machine_calculator(test_symbol, "2020-03-23", 10000)  # COVID bottom
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Total Return: {result.get('total_return', 'N/A')}%")
            print(f"   Current Value: ${result.get('current_value', 'N/A'):,.2f}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 2: DCA Simulator
    print("2. Testing DCA Simulator...")
    try:
        result = dca_simulator(test_symbol, 1000, "2022-01-01", "monthly")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Total Invested: ${result.get('total_invested', 'N/A'):,.2f}")
            print(f"   Current Value: ${result.get('current_value', 'N/A'):,.2f}")
            print(f"   Total Return: {result.get('total_return', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 3: Crisis Investment Tool
    print("3. Testing Crisis Investment Tool...")
    try:
        result = crisis_investment_tool(test_symbol, "2020_covid_crash", "bottom")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Crisis Return: {result.get('total_return', 'N/A')}%")
            print(f"   Investment Date: {result.get('investment_date', 'N/A')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 4: Perfect Timing Tool
    print("4. Testing Perfect Timing Tool...")
    try:
        result = perfect_timing_tool(test_symbol, 5, "annual")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Perfect Timing Return: {result.get('perfect_timing_return', 'N/A')}%")
            print(f"   Buy & Hold Return: {result.get('buy_hold_return', 'N/A')}%")
            print(f"   Timing Premium: {result.get('timing_premium', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    print("Tier 3 Testing Complete!")

if __name__ == "__main__":
    test_tier_3_tools()