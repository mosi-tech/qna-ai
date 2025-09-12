"""
Portfolio Data Processing Functions

Atomic functions for processing and transforming portfolio data.
Each function does ONE specific task and composes with others.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


def calculate_portfolio_returns(
    data: Dict[str, List[Dict[str, Any]]], 
    weights: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculate portfolio returns from individual asset data and weights.
    
    Args:
        data: {symbol: [{date, close, ...}]} - Historical price data
        weights: {symbol: weight} - Portfolio weights (should sum to 1.0 or 100.0)
        
    Returns:
        {
            "returns": pd.Series,  # Daily portfolio returns
            "prices": pd.Series,   # Portfolio price index (starts at 100)
            "dates": pd.DatetimeIndex,
            "success": bool
        }
    """
    try:
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 10:  # Assume percentage form
            weights = {k: v/100 for k, v in weights.items()}
        else:
            weights = {k: v/total_weight for k, v in weights.items()}
        
        # Convert data to aligned price series
        price_series = {}
        for symbol, weight in weights.items():
            if symbol not in data:
                return {"success": False, "error": f"No data for symbol {symbol}"}
            
            symbol_data = pd.DataFrame(data[symbol])
            symbol_data['date'] = pd.to_datetime(symbol_data['date'])
            symbol_data.set_index('date', inplace=True)
            
            # Get close prices
            if 'close' in symbol_data.columns:
                prices = symbol_data['close']
            elif 'c' in symbol_data.columns:
                prices = symbol_data['c']
            else:
                return {"success": False, "error": f"No close price found for {symbol}"}
                
            price_series[symbol] = prices
        
        # Align all series
        price_df = pd.DataFrame(price_series).ffill().dropna()
        
        if len(price_df) < 2:
            return {"success": False, "error": "Insufficient aligned data"}
        
        # Calculate individual asset returns
        returns_df = price_df.pct_change().dropna()
        
        # Calculate weighted portfolio returns
        portfolio_returns = pd.Series(0.0, index=returns_df.index)
        for symbol, weight in weights.items():
            portfolio_returns += returns_df[symbol] * weight
        
        # Calculate portfolio price index (starts at 100)
        portfolio_prices = (1 + portfolio_returns).cumprod() * 100
        
        return {
            "success": True,
            "returns": portfolio_returns,
            "prices": portfolio_prices,
            "dates": portfolio_returns.index,
            "num_days": len(portfolio_returns),
            "assets": list(weights.keys()),
            "weights": weights
        }
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio calculation failed: {str(e)}"}


def filter_date_range(
    data: Union[pd.Series, Dict[str, Any]], 
    start: str, 
    end: str
) -> Dict[str, Any]:
    """
    Filter time series data to specific date range.
    
    Args:
        data: pd.Series or result from calculate_portfolio_returns
        start: Start date string "YYYY-MM-DD"
        end: End date string "YYYY-MM-DD"
        
    Returns:
        {
            "filtered_data": pd.Series,
            "start_date": str,
            "end_date": str,
            "num_days": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(data, dict) and "returns" in data:
            series = data["returns"]
        elif isinstance(data, pd.Series):
            series = data
        else:
            return {"success": False, "error": "Invalid data format"}
        
        # Parse dates
        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)
        
        # Filter series
        mask = (series.index >= start_date) & (series.index <= end_date)
        filtered = series[mask]
        
        if len(filtered) == 0:
            return {"success": False, "error": f"No data in range {start} to {end}"}
        
        return {
            "success": True,
            "filtered_data": filtered,
            "start_date": filtered.index[0].strftime("%Y-%m-%d"),
            "end_date": filtered.index[-1].strftime("%Y-%m-%d"),
            "num_days": len(filtered),
            "original_days": len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Date filtering failed: {str(e)}"}


def resample_frequency(
    data: Union[pd.Series, Dict[str, Any]], 
    frequency: str
) -> Dict[str, Any]:
    """
    Resample time series to different frequency.
    
    Args:
        data: pd.Series or result from other functions
        frequency: "daily", "weekly", "monthly", "quarterly", "yearly"
        
    Returns:
        {
            "resampled_data": pd.Series,
            "frequency": str,
            "num_periods": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(data, dict) and "returns" in data:
            series = data["returns"]
        elif isinstance(data, dict) and "filtered_data" in data:
            series = data["filtered_data"]
        elif isinstance(data, pd.Series):
            series = data
        else:
            return {"success": False, "error": "Invalid data format"}
        
        # Map frequency strings to pandas codes
        freq_map = {
            "daily": "D",
            "weekly": "W",
            "monthly": "M", 
            "quarterly": "Q",
            "yearly": "Y"
        }
        
        if frequency not in freq_map:
            return {"success": False, "error": f"Invalid frequency: {frequency}"}
        
        # Resample returns data
        freq_code = freq_map[frequency]
        if frequency == "daily":
            resampled = series  # No change needed
        else:
            # For returns, we need to compound them over periods
            resampled = (1 + series).resample(freq_code).prod() - 1
        
        return {
            "success": True,
            "resampled_data": resampled,
            "frequency": frequency,
            "num_periods": len(resampled),
            "original_days": len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Resampling failed: {str(e)}"}


def align_data_series(*series_list) -> Dict[str, Any]:
    """
    Align multiple time series to common date range.
    
    Args:
        *series_list: Multiple pd.Series objects
        
    Returns:
        {
            "aligned_series": List[pd.Series],
            "common_start": str,
            "common_end": str,
            "num_days": int,
            "success": bool
        }
    """
    try:
        if len(series_list) < 2:
            return {"success": False, "error": "Need at least 2 series to align"}
        
        # Find common date range
        all_series = []
        for series in series_list:
            if isinstance(series, dict) and "returns" in series:
                all_series.append(series["returns"])
            elif isinstance(series, pd.Series):
                all_series.append(series)
            else:
                return {"success": False, "error": "Invalid series format"}
        
        # Combine into DataFrame and align
        df = pd.DataFrame({f"series_{i}": s for i, s in enumerate(all_series)})
        df = df.fillna(method='ffill').dropna()
        
        if len(df) == 0:
            return {"success": False, "error": "No overlapping data"}
        
        aligned_series = [df[f"series_{i}"] for i in range(len(all_series))]
        
        return {
            "success": True,
            "aligned_series": aligned_series,
            "common_start": df.index[0].strftime("%Y-%m-%d"),
            "common_end": df.index[-1].strftime("%Y-%m-%d"),
            "num_days": len(df),
            "num_series": len(aligned_series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Alignment failed: {str(e)}"}


def fill_missing_data(
    data: Union[pd.Series, Dict[str, Any]], 
    method: str = "forward"
) -> Dict[str, Any]:
    """
    Fill missing values in time series.
    
    Args:
        data: pd.Series or result from other functions
        method: "forward", "backward", "interpolate", "drop"
        
    Returns:
        {
            "filled_data": pd.Series,
            "method": str,
            "missing_count": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(data, dict) and "returns" in data:
            series = data["returns"].copy()
        elif isinstance(data, dict) and "filtered_data" in data:
            series = data["filtered_data"].copy()
        elif isinstance(data, pd.Series):
            series = data.copy()
        else:
            return {"success": False, "error": "Invalid data format"}
        
        original_missing = series.isnull().sum()
        
        # Apply filling method
        if method == "forward":
            filled = series.fillna(method='ffill')
        elif method == "backward":
            filled = series.fillna(method='bfill')
        elif method == "interpolate":
            filled = series.interpolate()
        elif method == "drop":
            filled = series.dropna()
        else:
            return {"success": False, "error": f"Invalid method: {method}"}
        
        return {
            "success": True,
            "filled_data": filled,
            "method": method,
            "missing_count": original_missing,
            "final_length": len(filled)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Data filling failed: {str(e)}"}


# Registry for MCP server
DATA_PROCESSING_FUNCTIONS = {
    'calculate_portfolio_returns': calculate_portfolio_returns,
    'filter_date_range': filter_date_range,
    'resample_frequency': resample_frequency,
    'align_data_series': align_data_series,
    'fill_missing_data': fill_missing_data
}