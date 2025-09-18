"""
Portfolio Data Processing Functions

Atomic functions for processing and transforming portfolio data.
Each function does ONE specific task and composes with others.

Extended with Time Series Processing functions from financial-analysis-function-library.json
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


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


# Time Series Processing Functions from financial-analysis-function-library.json
def calculate_returns(
    prices: Union[pd.Series, List[float], Dict[str, Any]], 
    period: str = "daily"
) -> Dict[str, Any]:
    """
    Calculate price returns for given period.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price data as pd.Series, list, or result from other functions
        period: "daily", "weekly", "monthly"
        
    Returns:
        {
            "returns": pd.Series,  # Return values
            "period": str,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "filtered_data" in prices:
            series = prices["filtered_data"]
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 price observations"}
        
        # Calculate returns
        returns = series.pct_change().dropna()
        
        # Convert to different periods if needed
        if period == "weekly":
            returns = (1 + returns).resample('W').prod() - 1
        elif period == "monthly":
            returns = (1 + returns).resample('M').prod() - 1
        elif period != "daily":
            return {"success": False, "error": f"Unsupported period: {period}"}
        
        return {
            "success": True,
            "returns": returns,
            "period": period,
            "num_observations": len(returns),
            "mean_return": float(returns.mean()),
            "std_return": float(returns.std())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Returns calculation failed: {str(e)}"}


def calculate_log_returns(
    prices: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate logarithmic returns.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price data as pd.Series, list, or result from other functions
        
    Returns:
        {
            "log_returns": pd.Series,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "filtered_data" in prices:
            series = prices["filtered_data"]
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 price observations"}
        
        # Calculate log returns
        log_returns = np.log(series / series.shift(1)).dropna()
        
        return {
            "success": True,
            "log_returns": log_returns,
            "num_observations": len(log_returns),
            "mean_log_return": float(log_returns.mean()),
            "std_log_return": float(log_returns.std())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Log returns calculation failed: {str(e)}"}


def calculate_cumulative_returns(
    returns: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate cumulative returns from return series.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return data as pd.Series, list, or result from other functions
        
    Returns:
        {
            "cumulative_returns": pd.Series,
            "total_return": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "log_returns" in returns:
            series = returns["log_returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, (list, np.ndarray)):
            series = pd.Series(returns)
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) == 0:
            return {"success": False, "error": "No return data"}
        
        # Calculate cumulative returns
        cumulative_returns = (1 + series).cumprod() - 1
        total_return = cumulative_returns.iloc[-1]
        
        return {
            "success": True,
            "cumulative_returns": cumulative_returns,
            "total_return": float(total_return),
            "num_observations": len(cumulative_returns),
            "start_date": series.index[0].strftime("%Y-%m-%d") if hasattr(series.index[0], 'strftime') else "N/A",
            "end_date": series.index[-1].strftime("%Y-%m-%d") if hasattr(series.index[-1], 'strftime') else "N/A"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Cumulative returns calculation failed: {str(e)}"}


def calculate_beta(
    stock_returns: Union[pd.Series, List[float], Dict[str, Any]],
    market_returns: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate beta coefficient vs market.
    
    From financial-analysis-function-library.json
    
    Args:
        stock_returns: Stock return data
        market_returns: Market return data
        
    Returns:
        {
            "beta": float,
            "correlation": float,
            "r_squared": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, (list, np.ndarray)):
                return pd.Series(data)
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        stock_series = extract_series(stock_returns)
        market_series = extract_series(market_returns)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'stock': stock_series,
            'market': market_series
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        stock_aligned = aligned_data['stock']
        market_aligned = aligned_data['market']
        
        # Calculate beta using covariance and variance
        covariance = np.cov(stock_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        if market_variance == 0:
            return {"success": False, "error": "Market variance is zero"}
        
        beta = covariance / market_variance
        correlation = np.corrcoef(stock_aligned, market_aligned)[0, 1]
        r_squared = correlation ** 2
        
        return {
            "success": True,
            "beta": float(beta),
            "correlation": float(correlation),
            "r_squared": float(r_squared),
            "num_observations": len(aligned_data),
            "covariance": float(covariance),
            "market_variance": float(market_variance)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Beta calculation failed: {str(e)}"}


def calculate_correlation(
    series1: Union[pd.Series, List[float], Dict[str, Any]],
    series2: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate correlation between two series.
    
    From financial-analysis-function-library.json
    
    Args:
        series1: First data series
        series2: Second data series
        
    Returns:
        {
            "correlation": float,
            "p_value": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, (list, np.ndarray)):
                return pd.Series(data)
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        s1 = extract_series(series1)
        s2 = extract_series(series2)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'series1': s1,
            'series2': s2
        }).dropna()
        
        if len(aligned_data) < 3:
            return {"success": False, "error": "Need at least 3 aligned observations"}
        
        # Calculate correlation
        from scipy.stats import pearsonr
        correlation, p_value = pearsonr(aligned_data['series1'], aligned_data['series2'])
        
        return {
            "success": True,
            "correlation": float(correlation),
            "p_value": float(p_value),
            "num_observations": len(aligned_data),
            "significance": "significant" if p_value < 0.05 else "not significant"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Correlation calculation failed: {str(e)}"}


def calculate_correlation_matrix(
    series_dict: Dict[str, Union[pd.Series, List[float]]]
) -> Dict[str, Any]:
    """
    Calculate correlation matrix for multiple series.
    
    From financial-analysis-function-library.json
    
    Args:
        series_dict: Dictionary of {name: series} data
        
    Returns:
        {
            "correlation_matrix": pd.DataFrame,
            "num_observations": int,
            "series_names": List[str],
            "success": bool
        }
    """
    try:
        if not isinstance(series_dict, dict) or len(series_dict) < 2:
            return {"success": False, "error": "Need at least 2 series in dictionary format"}
        
        # Convert all series to pandas Series and align
        data_df = pd.DataFrame()
        
        for name, series in series_dict.items():
            if isinstance(series, (list, np.ndarray)):
                data_df[name] = pd.Series(series)
            elif isinstance(series, pd.Series):
                data_df[name] = series
            else:
                return {"success": False, "error": f"Invalid format for series '{name}'"}
        
        # Drop rows with any NaN values
        data_df = data_df.dropna()
        
        if len(data_df) < 3:
            return {"success": False, "error": "Need at least 3 aligned observations"}
        
        # Calculate correlation matrix
        correlation_matrix = data_df.corr()
        
        return {
            "success": True,
            "correlation_matrix": correlation_matrix,
            "num_observations": len(data_df),
            "series_names": list(series_dict.keys()),
            "matrix_size": f"{len(series_dict)}x{len(series_dict)}"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Correlation matrix calculation failed: {str(e)}"}


# Registry for MCP server
DATA_PROCESSING_FUNCTIONS = {
    'calculate_portfolio_returns': calculate_portfolio_returns,
    'filter_date_range': filter_date_range,
    'resample_frequency': resample_frequency,
    'align_data_series': align_data_series,
    'fill_missing_data': fill_missing_data,
    # Time series processing functions from library.json
    'calculate_returns': calculate_returns,
    'calculate_log_returns': calculate_log_returns,
    'calculate_cumulative_returns': calculate_cumulative_returns,
    'calculate_beta': calculate_beta,
    'calculate_correlation': calculate_correlation,
    'calculate_correlation_matrix': calculate_correlation_matrix
}