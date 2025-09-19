#!/usr/bin/env python3
"""
Test Unified MCP Architecture - Real Data End-to-End

This tests the new unified architecture:
- mcp.financial: Python financial server functions  
- mcp.analytics: Analytics engine
- mcp.tools: Retail tools using REAL data (no mock)
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_financial_functions():
    """Test the financial server functions directly"""
    print("🔗 TESTING FINANCIAL SERVER FUNCTIONS")
    print("-" * 50)
    
    from mcp.financial.functions import (
        alpaca_market_stocks_snapshots,
        alpaca_market_stocks_bars,
        eodhd_fundamentals,
        eodhd_dividends
    )
    
    # Test snapshots
    print("📊 Testing alpaca_market_stocks_snapshots...")
    snapshot_result = alpaca_market_stocks_snapshots("AAPL")
    print(f"   ✅ Success: {snapshot_result['success']}")
    if snapshot_result['success']:
        print(f"   📈 AAPL Price: ${snapshot_result['data']['AAPL']['price']}")
        print(f"   📈 Change: {snapshot_result['data']['AAPL']['change_percent']:+.2f}%")
    
    # Test historical bars
    print("\n📊 Testing alpaca_market_stocks_bars...")
    bars_result = alpaca_market_stocks_bars("AAPL", timeframe="1Day", start="2024-01-01")
    print(f"   ✅ Success: {bars_result['success']}")
    if bars_result['success']:
        print(f"   📈 Bars retrieved: {len(bars_result['data']['AAPL'])}")
        print(f"   📈 Latest close: ${bars_result['data']['AAPL'][-1]['close']}")
    
    # Test fundamentals
    print("\n📊 Testing eodhd_fundamentals...")
    fundamentals_result = eodhd_fundamentals("AAPL.US")
    print(f"   ✅ Success: {fundamentals_result['success']}")
    if fundamentals_result['success']:
        print(f"   🏢 Company: {fundamentals_result['data']['General']['Name']}")
        print(f"   💰 Market Cap: ${fundamentals_result['data']['Valuation']['MarketCapitalization']:,.0f}")
    
    return snapshot_result['success'] and bars_result['success'] and fundamentals_result['success']


def test_analytics_functions():
    """Test the analytics engine functions"""
    print("\n🧮 TESTING ANALYTICS ENGINE FUNCTIONS")
    print("-" * 50)
    
    from mcp.analytics.indicators.technical import calculate_sma, calculate_rsi
    
    # Generate test data
    test_data = [{"close": 100 + i + (i%5)*2} for i in range(50)]
    
    # Test SMA
    print("📊 Testing calculate_sma...")
    sma_result = calculate_sma(test_data, period=20)
    print(f"   ✅ Success: {sma_result['success']}")
    if sma_result['success']:
        print(f"   📈 SMA values calculated: {len(sma_result['data'])}")
        print(f"   📈 Latest SMA: {sma_result['data'][-1]:.2f}")
    
    # Test RSI
    print("\n📊 Testing calculate_rsi...")
    rsi_result = calculate_rsi(test_data, period=14)
    print(f"   ✅ Success: {rsi_result['success']}")
    if rsi_result['success']:
        print(f"   📈 RSI values calculated: {len(rsi_result['data'])}")
        print(f"   📈 Latest RSI: {rsi_result['data'][-1]:.2f}")
    
    return sma_result['success'] and rsi_result['success']


def test_retail_tools_with_real_data():
    """Test retail tools using REAL data (no mock)"""
    print("\n🎯 TESTING RETAIL TOOLS WITH REAL DATA")
    print("-" * 50)
    
    from mcp.tools.tier_1_information import (
        current_price_stats,
        company_profile, 
        valuation_metrics,
        dividend_calendar
    )
    
    # Test current_price_stats with REAL data
    print("💼 Testing current_price_stats with REAL data...")
    price_stats = current_price_stats("AAPL")
    print(f"   ✅ Success: {price_stats['success']}")
    if price_stats['success']:
        print(f"   📈 Current Price: ${price_stats['current_price']}")
        print(f"   📈 52-Week Position: {price_stats['analytics_metrics']['52_week_range']['current_position']:.1%}")
        print(f"   📈 RSI: {price_stats['analytics_metrics']['momentum_metrics']['rsi_14']:.1f}")
        print(f"   📈 Trend: {price_stats['analytics_metrics']['trend_metrics']['trend_direction']}")
        print(f"   🔗 Financial functions used: {price_stats['financial_functions_used']}")
        print(f"   🧮 Analytics functions used: {price_stats['analytics_functions_used']}")
    
    # Test company_profile with REAL data
    print("\n💼 Testing company_profile with REAL data...")
    profile = company_profile("TSLA")
    print(f"   ✅ Success: {profile['success']}")
    if profile['success']:
        print(f"   🏢 Company: {profile['company_name']}")
        print(f"   🏭 Sector: {profile['sector']}")
        print(f"   👥 Employees: {profile['employees']:,}")
        print(f"   📊 PE Ratio: {profile['pe_ratio']}")
    
    # Test valuation_metrics with REAL data
    print("\n💼 Testing valuation_metrics with REAL data...")
    valuation = valuation_metrics("MSFT")
    print(f"   ✅ Success: {valuation['success']}")
    if valuation['success']:
        print(f"   📊 PE Ratio: {valuation['pe_ratio']}")
        print(f"   📊 PB Ratio: {valuation['pb_ratio']}")
        print(f"   📊 ROE: {valuation['roe']:.1%}" if valuation['roe'] else "   📊 ROE: N/A")
        print(f"   💰 Market Cap: ${valuation['market_cap']:,.0f}" if valuation['market_cap'] else "   💰 Market Cap: N/A")
    
    # Test dividend_calendar with REAL data
    print("\n💼 Testing dividend_calendar with REAL data...")
    dividends = dividend_calendar("AAPL", years=2)
    print(f"   ✅ Success: {dividends['success']}")
    if dividends['success']:
        print(f"   💰 Current Yield: {dividends['current_yield']:.2f}%")
        print(f"   💰 Annual Dividend: ${dividends['annual_dividend']:.2f}")
        print(f"   📅 Payment Frequency: {dividends['payment_frequency']}")
        print(f"   📈 Dividend Payments: {dividends['total_payments']}")
    
    return all([
        price_stats['success'],
        profile['success'], 
        valuation['success'],
        dividends['success']
    ])


def main():
    """Run all tests"""
    print("🧪 UNIFIED MCP ARCHITECTURE TEST")
    print("=" * 60)
    print("Testing end-to-end real data flow:")
    print("Financial Server → Analytics Engine → Retail Tools")
    print()
    
    success_count = 0
    total_tests = 3
    
    # Test financial functions
    if test_financial_functions():
        success_count += 1
        print("✅ Financial server functions: PASSED")
    else:
        print("❌ Financial server functions: FAILED")
    
    # Test analytics functions  
    if test_analytics_functions():
        success_count += 1
        print("✅ Analytics engine functions: PASSED")
    else:
        print("❌ Analytics engine functions: FAILED")
    
    # Test retail tools with real data
    if test_retail_tools_with_real_data():
        success_count += 1
        print("✅ Retail tools with real data: PASSED")
    else:
        print("❌ Retail tools with real data: FAILED")
    
    print("\n" + "=" * 60)
    print(f"📈 FINAL RESULTS: {success_count}/{total_tests} test suites passed")
    
    if success_count == total_tests:
        print("🎉 UNIFIED MCP ARCHITECTURE: FULLY OPERATIONAL!")
        print("✅ Real financial data ➜ Analytics calculations ➜ Retail insights")
        print("✅ No mock data - end-to-end real implementation")
        print("✅ Ready for production MCP server deployment")
    else:
        print("❌ Some components need attention")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)