"""
Range analysis utilities for calculating trading range tightness and related metrics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class RangeAnalyzer:
    """Analyze trading range patterns and tightness."""
    
    @staticmethod
    def calculate_weekly_range_tightness(weekly_data: List[Dict]) -> Dict[str, Any]:
        """
        Calculate weekly trading range tightness metrics.
        
        Args:
            weekly_data: List of weekly OHLC dictionaries with 'h', 'l', 'c' keys
            
        Returns:
            Dictionary with range tightness analysis
        """
        if not weekly_data or len(weekly_data) < 2:
            return {"error": "Insufficient weekly data"}
        
        df = pd.DataFrame(weekly_data)
        
        # Calculate weekly range percentages
        df['range_percent'] = ((df['h'] - df['l']) / df['c']) * 100
        df['range_absolute'] = df['h'] - df['l']
        
        # Calculate statistics
        weekly_ranges = df['range_percent'].tolist()
        
        return {
            "weeks_analyzed": len(weekly_ranges),
            "weekly_ranges": weekly_ranges,
            "avg_weekly_range": np.mean(weekly_ranges),
            "median_weekly_range": np.median(weekly_ranges),
            "min_weekly_range": np.min(weekly_ranges),
            "max_weekly_range": np.max(weekly_ranges),
            "std_weekly_range": np.std(weekly_ranges),
            "range_consistency": 1 / (1 + np.std(weekly_ranges)),  # Higher = more consistent
            "tight_weeks_count": sum(1 for r in weekly_ranges if r < np.mean(weekly_ranges) * 0.75),
            "wide_weeks_count": sum(1 for r in weekly_ranges if r > np.mean(weekly_ranges) * 1.25)
        }
    
    @staticmethod
    def calculate_daily_range_metrics(price_data: List[Dict]) -> Dict[str, Any]:
        """
        Calculate daily trading range metrics.
        
        Args:
            price_data: List of daily OHLC dictionaries
            
        Returns:
            Dictionary with daily range analysis
        """
        if not price_data:
            return {"error": "No price data provided"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        # Calculate daily metrics
        df['true_range'] = np.maximum(
            df['h'] - df['l'],
            np.maximum(
                abs(df['h'] - df['c'].shift(1)),
                abs(df['l'] - df['c'].shift(1))
            )
        )
        df['range_percent'] = ((df['h'] - df['l']) / df['c']) * 100
        df['body_percent'] = (abs(df['c'] - df['o']) / df['o']) * 100
        df['upper_wick'] = df['h'] - np.maximum(df['o'], df['c'])
        df['lower_wick'] = np.minimum(df['o'], df['c']) - df['l']
        
        # Remove NaN values
        df = df.dropna()
        
        if len(df) == 0:
            return {"error": "No valid range data after processing"}
        
        return {
            "days_analyzed": len(df),
            "avg_true_range": df['true_range'].mean(),
            "avg_range_percent": df['range_percent'].mean(),
            "avg_body_percent": df['body_percent'].mean(),
            "range_consistency": 1 / (1 + df['range_percent'].std()),
            "tight_range_days": sum(1 for r in df['range_percent'] if r < df['range_percent'].mean() * 0.5),
            "wide_range_days": sum(1 for r in df['range_percent'] if r > df['range_percent'].mean() * 2.0),
            "doji_days": sum(1 for b in df['body_percent'] if b < 0.5),  # Very small bodies
            "avg_upper_wick": df['upper_wick'].mean(),
            "avg_lower_wick": df['lower_wick'].mean()
        }