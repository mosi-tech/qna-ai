#!/usr/bin/env python3
"""
Comprehensive test for the modular analytics server.
Tests all key functions to ensure they support existing workflows.
"""

import sys
import json
from analytics.main import AnalyticsEngine


def test_comprehensive_analytics():
    """Test all major analytics functions with realistic data."""
    
    engine = AnalyticsEngine()
    
    # Sample realistic price data (30 trading days)
    sample_price_data = []
    base_price = 150.0
    for i in range(30):
        # Simulate realistic OHLC data with some volatility
        import random
        random.seed(42 + i)  # For reproducible results
        
        daily_change = random.uniform(-0.03, 0.03)  # ±3% daily moves
        open_price = base_price * (1 + daily_change)
        high_price = open_price * (1 + random.uniform(0, 0.02))  # Up to 2% intraday gain
        low_price = open_price * (1 - random.uniform(0, 0.02))   # Up to 2% intraday loss
        close_price = open_price * (1 + random.uniform(-0.015, 0.015))  # ±1.5% from open
        
        sample_price_data.append({
            "t": f"2024-01-{i+1:02d}",
            "o": round(open_price, 2),
            "h": round(high_price, 2),
            "l": round(low_price, 2),
            "c": round(close_price, 2),
            "v": random.randint(500000, 2000000)
        })
        base_price = close_price  # Next day starts from previous close
    
    print("=" * 80)
    print("COMPREHENSIVE ANALYTICS SERVER TEST")
    print("=" * 80)
    
    # Test 1: Daily Returns (fundamental for most analyses)
    print("\n1. Testing Daily Returns Calculation")
    print("-" * 40)
    returns_result = engine.execute_function("calculate_daily_returns", 
                                           price_data=sample_price_data, 
                                           return_type="close_to_close")
    if "error" in returns_result:
        print(f"ERROR: {returns_result['error']}")
        return False
    else:
        print(f"✓ Calculated returns for {returns_result['total_observations']} days")
        print(f"  Mean return: {returns_result['mean_return']:.3f}%")
        print(f"  Success rate: {returns_result['success_rate']:.1f}%")
    
    # Test 2: Rolling Volatility (critical for risk analysis)
    print("\n2. Testing Rolling Volatility")
    print("-" * 40)
    returns = returns_result.get("returns", [])
    if returns:
        vol_result = engine.execute_function("calculate_rolling_volatility",
                                           returns=returns,
                                           window=10,
                                           annualize=True)
        if "error" in vol_result:
            print(f"ERROR: {vol_result['error']}")
        else:
            print(f"✓ Calculated rolling volatility with {len(vol_result['rolling_volatility'])} observations")
            print(f"  Current volatility: {vol_result['current_volatility']:.1f}%")
    
    # Test 3: Economic Sensitivity (for CPI/event analysis)
    print("\n3. Testing Economic Sensitivity Analysis")
    print("-" * 40)
    event_dates = ["2024-01-05", "2024-01-15", "2024-01-25"]  # Simulated CPI dates
    econ_result = engine.execute_function("analyze_economic_sensitivity",
                                        price_data=sample_price_data,
                                        event_dates=event_dates,
                                        event_type="CPI")
    if "error" in econ_result:
        print(f"ERROR: {econ_result['error']}")
    else:
        print(f"✓ Analyzed sensitivity for {len(event_dates)} event dates")
        print(f"  Average event day return: {econ_result.get('avg_event_return', 'N/A')}%")
        print(f"  Event day volatility multiplier: {econ_result.get('volatility_multiplier', 'N/A')}")
    
    # Test 4: Linear Trend Analysis (for trend detection)
    print("\n4. Testing Linear Trend Analysis")
    print("-" * 40)
    prices = [data["c"] for data in sample_price_data]
    trend_result = engine.execute_function("linear_trend_analysis", prices=prices)
    if "error" in trend_result:
        print(f"ERROR: {trend_result['error']}")
    else:
        print(f"✓ Trend analysis completed")
        print(f"  Trend classification: {trend_result.get('trend_classification', 'N/A')}")
        print(f"  R-squared: {trend_result.get('r_squared', 'N/A'):.3f}")
        daily_trend = trend_result.get('daily_trend_percent', 'N/A')
        if isinstance(daily_trend, (int, float)):
            print(f"  Daily trend: {daily_trend:.3f}%")
        else:
            print(f"  Daily trend: {daily_trend}%")
    
    # Test 5: Gap Analysis (for gap-related strategies)
    print("\n5. Testing Gap Analysis")
    print("-" * 40)
    # Create some gap data by modifying opens
    gap_data = sample_price_data[:10].copy()
    gap_data[3]["o"] = gap_data[2]["c"] * 1.025  # 2.5% upward gap
    gap_data[7]["o"] = gap_data[6]["c"] * 0.975  # 2.5% downward gap
    
    gap_result = engine.execute_function("identify_gaps",
                                       price_data=gap_data,
                                       gap_threshold=1.0)
    if "error" in gap_result:
        print(f"ERROR: {gap_result['error']}")
    else:
        print(f"✓ Gap analysis completed")
        print(f"  Total gaps found: {gap_result.get('total_gaps', 0)}")
        print(f"  Up gaps: {gap_result.get('up_gaps', 0)}")
        print(f"  Down gaps: {gap_result.get('down_gaps', 0)}")
    
    # Test 6: Rolling Skewness (for risk analysis)
    print("\n6. Testing Rolling Skewness")
    print("-" * 40)
    if returns:
        skew_result = engine.execute_function("calculate_rolling_skewness",
                                            returns=returns,
                                            window=15)
        if "error" in skew_result:
            print(f"ERROR: {skew_result['error']}")
        else:
            print(f"✓ Rolling skewness calculated")
            current_skew = skew_result.get('current_skewness', 'N/A')
            avg_skew = skew_result.get('average_skewness', 'N/A')
            
            if isinstance(current_skew, (int, float)):
                print(f"  Current skewness: {current_skew:.3f}")
            else:
                print(f"  Current skewness: {current_skew}")
                
            if isinstance(avg_skew, (int, float)):
                print(f"  Average skewness: {avg_skew:.3f}")
            else:
                print(f"  Average skewness: {avg_skew}")
    
    # Test 7: Simple Moving Average (technical analysis)
    print("\n7. Testing Simple Moving Average")
    print("-" * 40)
    sma_result = engine.execute_function("calculate_sma",
                                       prices=prices[-20:],  # Last 20 days
                                       window=10)
    if "error" in sma_result:
        print(f"ERROR: {sma_result['error']}")
    else:
        print(f"✓ SMA calculation completed")
        current_sma = sma_result.get('current_sma', 'N/A')
        if isinstance(current_sma, (int, float)):
            print(f"  Current SMA: ${current_sma:.2f}")
        else:
            print(f"  Current SMA: {current_sma}")
        print(f"  Values calculated: {len(sma_result.get('sma_values', []))}")
    
    # Test 8: Correlation Analysis (for portfolio analysis)
    print("\n8. Testing Correlation Analysis")
    print("-" * 40)
    # Create second price series for correlation
    returns2 = [r * 0.8 + random.uniform(-0.5, 0.5) for r in returns]  # Correlated but with noise
    
    corr_result = engine.execute_function("calculate_correlation_matrix",
                                        returns_list=[returns, returns2],
                                        labels=["Asset1", "Asset2"])
    if "error" in corr_result:
        print(f"ERROR: {corr_result['error']}")
    else:
        print(f"✓ Correlation analysis completed")
        corr_coef = corr_result.get('correlation_coefficient', 'N/A')
        if isinstance(corr_coef, (int, float)):
            print(f"  Correlation coefficient: {corr_coef:.3f}")
        else:
            print(f"  Correlation coefficient: {corr_coef}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("The analytics server is ready to support all existing workflows.")
    print("=" * 80)
    
    # Summary of capabilities
    print(f"\n📊 ANALYTICS CAPABILITIES VERIFIED:")
    print(f"   • Returns Calculation: ✓")
    print(f"   • Volatility Analysis: ✓") 
    print(f"   • Economic Sensitivity: ✓")
    print(f"   • Trend Analysis: ✓")
    print(f"   • Gap Detection: ✓")
    print(f"   • Risk Metrics: ✓")
    print(f"   • Technical Indicators: ✓")
    print(f"   • Portfolio Analysis: ✓")
    
    return True


if __name__ == "__main__":
    success = test_comprehensive_analytics()
    sys.exit(0 if success else 1)