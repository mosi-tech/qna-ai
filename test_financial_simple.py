"""
Simple test of financial functions
"""

import sys
import os
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin')

from mcp.financial import alpaca_market_stocks_bars

def test_financial():
    """Test basic financial function"""
    print("Testing Financial Functions")
    print("=" * 30)
    
    try:
        result = alpaca_market_stocks_bars(
            symbols="AAPL",
            timeframe="1Day",
            start="2024-01-01",
            end="2024-01-31"
        )
        print(f"Result keys: {list(result.keys())}")
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            print(f"Data keys: {list(result.get('data', {}).keys())}")
        else:
            print(f"Error: {result.get('error')}")
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_financial()