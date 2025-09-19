"""
Test YTD Performance only
"""

import sys
import os
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin')

from mcp.financial import alpaca_market_stocks_bars

def test_ytd_simple():
    """Simple YTD test following mock data format"""
    print("Testing YTD Performance Manually")
    print("=" * 35)
    
    # Test getting data first
    symbol = "AAPL"
    result = alpaca_market_stocks_bars(symbols=symbol, timeframe="1Day")
    
    print(f"Result keys: {list(result.keys())}")
    if "bars" in result:
        print(f"Bars keys: {list(result['bars'].keys())}")
        if symbol in result["bars"]:
            bars = result["bars"][symbol]
            print(f"Number of bars: {len(bars)}")
            if bars:
                print(f"First bar keys: {list(bars[0].keys())}")
                print(f"First bar: {bars[0]}")
                
                # Calculate simple return
                if len(bars) > 1:
                    start_price = bars[0]["c"]
                    end_price = bars[-1]["c"]
                    ytd_return = (end_price / start_price - 1) * 100
                    print(f"YTD Return: {ytd_return:.2f}%")

if __name__ == "__main__":
    test_ytd_simple()