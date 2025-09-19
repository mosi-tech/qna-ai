"""
Test script for Tier 4 Comparison Tools
"""

import sys
import os
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin')

from mcp.tools.tier_4_comparison import (
    stock_battle,
    etf_head_to_head,
    sector_showdown,
    style_comparison
)

def test_tier_4_tools():
    """Test all Tier 4 tools with sample data"""
    print("Testing Tier 4 Comparison Tools")
    print("=" * 50)
    
    # Test 1: Stock Battle
    print("1. Testing Stock Battle...")
    try:
        result = stock_battle("AAPL", "MSFT", "3y")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Overall Winner: {result.get('battle_outcome', {}).get('overall_winner', 'N/A')}")
            print(f"   Performance Leader: {result.get('winner_by_category', {}).get('performance', 'N/A')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            if 'traceback' in result:
                print(f"   Traceback: {result['traceback']}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 2: ETF Head-to-Head
    print("2. Testing ETF Head-to-Head...")
    try:
        result = etf_head_to_head("SPY", "VTI")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Performance Leader: {result.get('recommendation', {}).get('for_performance', 'N/A')}")
            print(f"   Cost Leader: {result.get('recommendation', {}).get('for_cost_conscious', 'N/A')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 3: Sector Showdown
    print("3. Testing Sector Showdown...")
    try:
        result = sector_showdown(["Technology", "Healthcare", "Financial"], "1y")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Winning Sector: {result.get('sector_showdown_summary', {}).get('winner', 'N/A')}")
            print(f"   Performance Spread: {result.get('sector_showdown_summary', {}).get('performance_spread', 'N/A')}%")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    
    # Test 4: Style Comparison
    print("4. Testing Style Comparison...")
    try:
        result = style_comparison("growth", "value", "3y")
        has_error = 'error' in result or result.get('success') == False
        print(f"   Status: {'FAILED' if has_error else 'SUCCESS'}")
        if not has_error:
            print(f"   Performance Leader: {result.get('style_comparison_metrics', {}).get('performance_advantage', {}).get('leader', 'N/A')}")
            print(f"   Current Leader: {result.get('current_leadership', {}).get('current_leader', 'N/A')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   EXCEPTION: {str(e)}")
    
    print()
    print("Tier 4 Testing Complete!")

if __name__ == "__main__":
    test_tier_4_tools()