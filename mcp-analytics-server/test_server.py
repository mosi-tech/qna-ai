#!/usr/bin/env python3
"""
Test script for the MCP Analytics Server functions
"""

import json
import pandas as pd
import numpy as np
from scipy import stats

# Sample test data
sample_price_data = [
    {"t": "2024-01-01", "o": 100, "h": 102, "l": 98, "c": 101},
    {"t": "2024-01-02", "o": 101, "h": 103, "l": 99, "c": 102},
    {"t": "2024-01-03", "o": 102, "h": 104, "l": 100, "c": 103},
    {"t": "2024-01-04", "o": 103, "h": 105, "l": 101, "c": 104},
    {"t": "2024-01-05", "o": 104, "h": 106, "l": 102, "c": 105}
]

def test_daily_returns():
    """Test daily returns calculation"""
    print("Testing daily returns calculation...")
    
    # Replicate the logic from calculate_daily_returns
    df = pd.DataFrame(sample_price_data)
    df['t'] = pd.to_datetime(df['t'])
    df = df.sort_values('t')
    df['return'] = df['c'].pct_change() * 100
    returns = df['return'].dropna().tolist()
    
    result = {
        "returns": returns,
        "mean_return": np.mean(returns),
        "std_return": np.std(returns),
        "positive_days": sum(1 for r in returns if r > 0),
        "negative_days": sum(1 for r in returns if r < 0),
        "success_rate": sum(1 for r in returns if r > 0) / len(returns) * 100
    }
    
    print("Daily Returns Result:")
    print(json.dumps(result, indent=2))
    print("-" * 50)

def test_rolling_volatility():
    """Test rolling volatility calculation"""
    print("Testing rolling volatility calculation...")
    
    # Sample returns
    returns = [1.2, -0.8, 1.5, 0.3, -1.1, 2.1, -0.5, 1.8, -0.3, 0.9] * 5  # 50 days
    
    returns_series = pd.Series(returns)
    rolling_vol = returns_series.rolling(window=10).std() * np.sqrt(252)  # Annualized
    
    result = {
        "rolling_volatility": rolling_vol.dropna().tolist(),
        "current_volatility": rolling_vol.iloc[-1] if not rolling_vol.empty else None,
        "avg_volatility": rolling_vol.mean(),
        "max_volatility": rolling_vol.max(),
        "min_volatility": rolling_vol.min()
    }
    
    print("Rolling Volatility Result:")
    print(json.dumps(result, indent=2))
    print("-" * 50)

def test_correlation_matrix():
    """Test correlation matrix calculation"""
    print("Testing correlation matrix calculation...")
    
    returns_data = {
        "AAPL": [1.2, -0.8, 1.5, 0.3, -1.1, 2.1, -0.5],
        "TSLA": [2.1, -1.5, 2.8, 0.1, -2.2, 3.1, -1.0],
        "SPY": [0.8, -0.5, 1.2, 0.2, -0.8, 1.5, -0.3]
    }
    
    df = pd.DataFrame(returns_data)
    correlation_matrix = df.corr(method="pearson")
    
    # Find least and most correlated pairs
    corr_pairs = []
    symbols = list(returns_data.keys())
    
    for i, symbol1 in enumerate(symbols):
        for j, symbol2 in enumerate(symbols):
            if i < j:
                corr_value = correlation_matrix.loc[symbol1, symbol2]
                corr_pairs.append({
                    "pair": [symbol1, symbol2],
                    "correlation": corr_value
                })
    
    corr_pairs.sort(key=lambda x: abs(x["correlation"]))
    
    result = {
        "correlation_matrix": correlation_matrix.to_dict(),
        "least_correlated_pairs": corr_pairs[:3],
        "most_correlated_pairs": sorted(corr_pairs, key=lambda x: abs(x["correlation"]), reverse=True)[:3],
        "method": "pearson"
    }
    
    print("Correlation Matrix Result:")
    print(json.dumps(result, indent=2))
    print("-" * 50)

def test_economic_sensitivity():
    """Test economic sensitivity analysis"""
    print("Testing economic sensitivity analysis...")
    
    # Extended price data for CPI analysis
    extended_price_data = [
        {"t": "2024-01-10", "o": 100, "h": 102, "l": 98, "c": 101},  # CPI day
        {"t": "2024-01-11", "o": 101, "h": 103, "l": 99, "c": 102},
        {"t": "2024-02-13", "o": 102, "h": 105, "l": 100, "c": 104}, # CPI day
        {"t": "2024-02-14", "o": 104, "h": 106, "l": 102, "c": 105},
        {"t": "2024-03-12", "o": 105, "h": 108, "l": 103, "c": 107}, # CPI day
    ]
    
    cpi_dates = ["2024-01-10", "2024-02-13", "2024-03-12"]
    
    df = pd.DataFrame(extended_price_data)
    df['t'] = pd.to_datetime(df['t'])
    df = df.sort_values('t')
    df['daily_return'] = ((df['c'] - df['o']) / df['o']) * 100
    df['date'] = df['t'].dt.date
    
    event_dates_parsed = [pd.to_datetime(date).date() for date in cpi_dates]
    
    event_day_returns = df[df['date'].isin(event_dates_parsed)]['daily_return'].tolist()
    non_event_returns = df[~df['date'].isin(event_dates_parsed)]['daily_return'].tolist()
    
    result = {
        "event_type": "CPI",
        "total_events": len(event_dates_parsed),
        "events_with_data": len(event_day_returns),
        "avg_event_day_return": np.mean(event_day_returns),
        "avg_normal_day_return": np.mean(non_event_returns) if non_event_returns else 0,
        "event_success_rate": len([r for r in event_day_returns if r > 0]) / len(event_day_returns) * 100,
        "event_day_returns": event_day_returns,
        "best_event_return": max(event_day_returns),
        "worst_event_return": min(event_day_returns)
    }
    
    print("Economic Sensitivity Result:")
    print(json.dumps(result, indent=2))
    print("-" * 50)

def main():
    """Run all tests"""
    print("Starting MCP Analytics Server Tests...")
    print("=" * 60)
    
    test_daily_returns()
    test_rolling_volatility() 
    test_correlation_matrix()
    test_economic_sensitivity()
    
    print("All tests completed!")

if __name__ == "__main__":
    main()