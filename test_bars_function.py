#!/usr/bin/env python3
"""
Test the alpaca_market_stocks_bars function directly to debug the date parsing issue
"""

import sys
sys.path.append('mcp-server/financial')

try:
    from functions_mock import alpaca_market_stocks_bars
    
    print("Testing alpaca_market_stocks_bars function...")
    
    # Test 1: Basic call (this works)
    print("\n1. Testing basic call with just symbols:")
    try:
        result1 = alpaca_market_stocks_bars("AAPL")
        print(f"✅ Success: {len(result1.get('bars', {}).get('AAPL', []))} bars returned")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: With timeframe (this works)
    print("\n2. Testing with timeframe:")
    try:
        result2 = alpaca_market_stocks_bars("AAPL", "1Day")
        print(f"✅ Success: {len(result2.get('bars', {}).get('AAPL', []))} bars returned")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: With start date (this fails)
    print("\n3. Testing with start date:")
    try:
        result3 = alpaca_market_stocks_bars("AAPL", "1Day", "2023-01-01")
        print(f"✅ Success: {len(result3.get('bars', {}).get('AAPL', []))} bars returned")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: With both dates (this fails)
    print("\n4. Testing with both start and end dates:")
    try:
        result4 = alpaca_market_stocks_bars("AAPL", "1Day", "2023-01-01", "2024-12-20")
        print(f"✅ Success: {len(result4.get('bars', {}).get('AAPL', []))} bars returned")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Multiple symbols without dates (this might fail)
    print("\n5. Testing multiple symbols without dates:")
    try:
        result5 = alpaca_market_stocks_bars("AAPL,SPY")
        bars = result5.get('bars', {})
        print(f"✅ Success: AAPL={len(bars.get('AAPL', []))}, SPY={len(bars.get('SPY', []))} bars")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Multiple symbols with dates (this probably fails)
    print("\n6. Testing multiple symbols with dates:")
    try:
        result6 = alpaca_market_stocks_bars("AAPL,SPY", "1Day", "2023-01-01", "2024-12-20")
        bars = result6.get('bars', {})
        print(f"✅ Success: AAPL={len(bars.get('AAPL', []))}, SPY={len(bars.get('SPY', []))} bars")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the right directory and the module exists")