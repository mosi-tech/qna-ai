#!/usr/bin/env python3
"""
Analytics wrapper that can be called directly from the workflow system.
This provides engine/compute capabilities without requiring full MCP setup.
"""

import sys
import json
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime

class FinancialAnalytics:
    """Financial analytics engine for computing complex metrics."""
    
    @staticmethod
    def calculate_daily_returns(price_data, return_type="close_to_close"):
        """Calculate daily returns from OHLC price data."""
        if not price_data or len(price_data) < 2:
            return {"error": "Insufficient price data"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t')
        
        if return_type == "close_to_close":
            df['return'] = df['c'].pct_change() * 100
        elif return_type == "open_to_close":
            df['return'] = ((df['c'] - df['o']) / df['o']) * 100
        elif return_type == "close_to_open":
            df['return'] = ((df['o'] - df['c'].shift(1)) / df['c'].shift(1)) * 100
        
        returns = df['return'].dropna().tolist()
        
        return {
            "returns": returns,
            "mean_return": np.mean(returns),
            "std_return": np.std(returns),
            "positive_days": sum(1 for r in returns if r > 0),
            "negative_days": sum(1 for r in returns if r < 0),
            "success_rate": sum(1 for r in returns if r > 0) / len(returns) * 100
        }
    
    @staticmethod
    def calculate_rolling_volatility(returns, window=30, annualize=True):
        """Calculate rolling volatility."""
        if len(returns) < window:
            return {"error": "Insufficient data for rolling window"}
        
        returns_series = pd.Series(returns)
        rolling_vol = returns_series.rolling(window=window).std()
        
        if annualize:
            rolling_vol = rolling_vol * np.sqrt(252)
        
        return {
            "rolling_volatility": rolling_vol.dropna().tolist(),
            "current_volatility": rolling_vol.iloc[-1] if not rolling_vol.empty else None,
            "avg_volatility": rolling_vol.mean(),
            "max_volatility": rolling_vol.max(),
            "min_volatility": rolling_vol.min()
        }
    
    @staticmethod
    def calculate_rolling_skewness(returns, window=30):
        """Calculate rolling skewness."""
        if len(returns) < window:
            return {"error": "Insufficient data for rolling window"}
        
        returns_series = pd.Series(returns)
        rolling_skew = returns_series.rolling(window=window).skew()
        
        return {
            "rolling_skewness": rolling_skew.dropna().tolist(),
            "current_skewness": rolling_skew.iloc[-1] if not rolling_skew.empty else None,
            "avg_skewness": rolling_skew.mean(),
            "interpretation": "Positive skew indicates momentum patterns. Negative skew indicates mean-reversion patterns."
        }
    
    @staticmethod
    def calculate_correlation_matrix(returns_data, method="pearson"):
        """Calculate correlation matrix between return series."""
        df = pd.DataFrame(returns_data)
        correlation_matrix = df.corr(method=method)
        
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
        
        # Sort by correlation (least correlated first)
        corr_pairs.sort(key=lambda x: abs(x["correlation"]))
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "least_correlated_pairs": corr_pairs[:3],
            "most_correlated_pairs": sorted(corr_pairs, key=lambda x: abs(x["correlation"]), reverse=True)[:3],
            "method": method
        }
    
    @staticmethod
    def calculate_trend_analysis(prices, timestamps=None):
        """Perform trend analysis using linear regression."""
        if len(prices) < 10:
            return {"error": "Insufficient data for trend analysis"}
        
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Calculate trend angle
        angle_rad = np.arctan(slope)
        angle_deg = np.degrees(angle_rad)
        
        # Categorize trend
        if angle_deg > 45:
            trend_category = "steep_upward"
        elif angle_deg > 15:
            trend_category = "moderate_upward"
        elif angle_deg > -15:
            trend_category = "sideways"
        elif angle_deg > -45:
            trend_category = "moderate_downward"
        else:
            trend_category = "steep_downward"
        
        # Calculate total return
        total_return = ((y[-1] - y[0]) / y[0]) * 100
        
        return {
            "slope": slope,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "trend_angle_degrees": angle_deg,
            "trend_category": trend_category,
            "total_return_percent": total_return,
            "trend_strength": "strong" if r_value ** 2 > 0.7 else "moderate" if r_value ** 2 > 0.4 else "weak"
        }
    
    @staticmethod
    def analyze_economic_sensitivity(price_data, event_dates, event_type="CPI"):
        """Analyze performance on economic event dates."""
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t')
        
        # Calculate daily returns
        df['daily_return'] = ((df['c'] - df['o']) / df['o']) * 100
        df['date'] = df['t'].dt.date
        
        # Convert event dates
        event_dates_parsed = [pd.to_datetime(date).date() for date in event_dates]
        
        # Filter for event days
        event_day_returns = df[df['date'].isin(event_dates_parsed)]['daily_return'].tolist()
        non_event_returns = df[~df['date'].isin(event_dates_parsed)]['daily_return'].tolist()
        
        if not event_day_returns:
            return {"error": "No data found for event dates"}
        
        return {
            "event_type": event_type,
            "total_events": len(event_dates_parsed),
            "events_with_data": len(event_day_returns),
            "avg_event_day_return": np.mean(event_day_returns),
            "avg_normal_day_return": np.mean(non_event_returns) if non_event_returns else 0,
            "event_success_rate": len([r for r in event_day_returns if r > 0]) / len(event_day_returns) * 100,
            "normal_success_rate": len([r for r in non_event_returns if r > 0]) / len(non_event_returns) * 100 if non_event_returns else 0,
            "event_volatility": np.std(event_day_returns),
            "normal_volatility": np.std(non_event_returns) if non_event_returns else 0,
            "volatility_multiplier": np.std(event_day_returns) / np.std(non_event_returns) if non_event_returns and np.std(non_event_returns) > 0 else 0,
            "event_day_returns": event_day_returns,
            "best_event_return": max(event_day_returns),
            "worst_event_return": min(event_day_returns)
        }

def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python analytics_wrapper.py <function_name> [json_args]")
        sys.exit(1)
    
    function_name = sys.argv[1]
    
    # Parse JSON arguments if provided
    args = {}
    if len(sys.argv) > 2:
        try:
            args = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print("Error: Invalid JSON arguments")
            sys.exit(1)
    
    analytics = FinancialAnalytics()
    
    # Route to appropriate function
    if hasattr(analytics, function_name):
        result = getattr(analytics, function_name)(**args)
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: Function '{function_name}' not found")
        sys.exit(1)

if __name__ == "__main__":
    main()