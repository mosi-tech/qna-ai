"""
Data Processing Utilities

Centralized data processing using libraries from requirements.txt
From financial-analysis-function-library.json
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use libraries from requirements.txt - data comes from mcp-financial-server
from scipy import stats
import empyrical

def validate_price_data(data: Union[pd.Series, pd.DataFrame, List, Dict]) -> pd.Series:
    """
    Validate and convert price data to standardized format.
    
    From financial-analysis-function-library.json
    Uses pandas for standardized data processing
    
    Args:
        data: Price data in various formats
        
    Returns:
        pd.Series: Validated price series
    """
    try:
        if isinstance(data, dict):
            if "prices" in data:
                series = data["prices"]
            elif "close" in data:
                series = data["close"]
            elif "data" in data:
                series = data["data"]
            else:
                # Try to convert dict values to series
                series = pd.Series(list(data.values()))
        elif isinstance(data, (list, np.ndarray)):
            # Check if it's a list of dictionaries (common MCP format)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Extract 'close' values from list of dictionaries
                if "close" in data[0]:
                    series = pd.Series([item["close"] for item in data])
                elif "Close" in data[0]:
                    series = pd.Series([item["Close"] for item in data])
                else:
                    # Use first numeric value from each dict
                    values = []
                    for item in data:
                        for key, value in item.items():
                            if isinstance(value, (int, float)):
                                values.append(value)
                                break
                    series = pd.Series(values)
            else:
                series = pd.Series(data)
        elif isinstance(data, pd.Series):
            series = data.copy()
        elif isinstance(data, pd.DataFrame):
            # If DataFrame, try to get close column or first column
            if "close" in data.columns:
                series = data["close"]
            elif "Close" in data.columns:
                series = data["Close"]
            else:
                series = data.iloc[:, 0]
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        # Convert to numeric and drop NaN
        series = pd.to_numeric(series, errors='coerce').dropna()
        
        if len(series) == 0:
            raise ValueError("No valid price data after cleaning")
        
        return series
        
    except Exception as e:
        raise ValueError(f"Data validation failed: {str(e)}")


def validate_return_data(data: Union[pd.Series, pd.DataFrame, List, Dict]) -> pd.Series:
    """
    Validate and convert return data to standardized format.
    
    From financial-analysis-function-library.json
    Uses pandas for standardized data processing
    
    Args:
        data: Return data in various formats
        
    Returns:
        pd.Series: Validated return series
    """
    try:
        if isinstance(data, dict):
            if "returns" in data:
                series = data["returns"]
            elif "return" in data:
                series = data["return"]
            elif "data" in data:
                series = data["data"]
            else:
                series = pd.Series(list(data.values()))
        elif isinstance(data, (list, np.ndarray)):
            # Check if it's a list of dictionaries (common MCP format)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Extract 'returns' values from list of dictionaries
                if "returns" in data[0]:
                    series = pd.Series([item["returns"] for item in data])
                elif "return" in data[0]:
                    series = pd.Series([item["return"] for item in data])
                else:
                    # Use first numeric value from each dict
                    values = []
                    for item in data:
                        for key, value in item.items():
                            if isinstance(value, (int, float)):
                                values.append(value)
                                break
                    series = pd.Series(values)
            else:
                series = pd.Series(data)
        elif isinstance(data, pd.Series):
            series = data.copy()
        elif isinstance(data, pd.DataFrame):
            if "returns" in data.columns:
                series = data["returns"]
            else:
                series = data.iloc[:, 0]
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        # Convert to numeric and drop NaN
        series = pd.to_numeric(series, errors='coerce').dropna()
        
        if len(series) == 0:
            raise ValueError("No valid return data after cleaning")
        
        return series
        
    except Exception as e:
        raise ValueError(f"Return data validation failed: {str(e)}")


def prices_to_returns(prices: pd.Series, method: str = "simple") -> pd.Series:
    """
    Convert prices to returns using pandas.
    
    From financial-analysis-function-library.json
    Uses pandas built-in methods instead of manual calculation
    
    Args:
        prices: Price series
        method: 'simple' or 'log'
        
    Returns:
        pd.Series: Return series
    """
    try:
        prices = validate_price_data(prices)
        
        if method == "simple":
            returns = prices.pct_change().dropna()
        elif method == "log":
            returns = np.log(prices / prices.shift(1)).dropna()
        else:
            raise ValueError("Method must be 'simple' or 'log'")
        
        return returns
        
    except Exception as e:
        raise ValueError(f"Price to return conversion failed: {str(e)}")


def align_series(*series_list: pd.Series) -> List[pd.Series]:
    """
    Align multiple time series by their common index.
    
    From financial-analysis-function-library.json
    Uses pandas built-in alignment instead of manual indexing
    
    Args:
        *series_list: Multiple pandas Series to align
        
    Returns:
        List[pd.Series]: Aligned series
    """
    try:
        if len(series_list) < 2:
            return list(series_list)
        
        # Create DataFrame to align all series
        df = pd.DataFrame({f"series_{i}": series for i, series in enumerate(series_list)})
        df = df.dropna()
        
        if len(df) == 0:
            raise ValueError("No common data points after alignment")
        
        # Return aligned series
        return [df.iloc[:, i] for i in range(len(series_list))]
        
    except Exception as e:
        raise ValueError(f"Series alignment failed: {str(e)}")


def resample_data(data: pd.Series, frequency: str, method: str = "last") -> pd.Series:
    """
    Resample time series data to different frequency.
    
    From financial-analysis-function-library.json
    Uses pandas resample instead of manual aggregation
    
    Args:
        data: Time series data
        frequency: Target frequency ('D', 'W', 'M', etc.)
        method: Aggregation method ('last', 'mean', 'sum')
        
    Returns:
        pd.Series: Resampled data
    """
    try:
        if not isinstance(data.index, pd.DatetimeIndex):
            # Try to convert index to datetime
            data.index = pd.to_datetime(data.index)
        
        if method == "last":
            resampled = data.resample(frequency).last()
        elif method == "mean":
            resampled = data.resample(frequency).mean()
        elif method == "sum":
            resampled = data.resample(frequency).sum()
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return resampled.dropna()
        
    except Exception as e:
        raise ValueError(f"Data resampling failed: {str(e)}")


def standardize_output(result: Dict[str, Any], function_name: str) -> Dict[str, Any]:
    """
    Standardize function output format.
    
    From financial-analysis-function-library.json
    Ensures consistent output format across all functions
    
    Args:
        result: Function result dictionary
        function_name: Name of the function
        
    Returns:
        Dict: Standardized output
    """
    try:
        standardized = {
            "success": result.get("success", True),
            "function": function_name,
            **result
        }
        
        # Add metadata
        if "success" not in result:
            standardized["success"] = True
        
        # Convert numpy types and pandas types to Python types
        for key, value in standardized.items():
            if isinstance(value, np.floating):
                standardized[key] = float(value)
            elif isinstance(value, np.integer):
                standardized[key] = int(value)
            elif isinstance(value, np.ndarray):
                standardized[key] = value.tolist()
            elif isinstance(value, pd.Series):
                standardized[key] = value.tolist()
            elif isinstance(value, pd.DataFrame):
                standardized[key] = value.to_dict('records')
        
        return standardized
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Output standardization failed: {str(e)}",
            "function": function_name
        }


def calculate_log_returns(prices: Union[pd.Series, Dict[str, Any]]) -> pd.Series:
    """
    Calculate logarithmic returns from prices.
    
    From financial-analysis-function-library.json time_series_processing category
    Wrapper around prices_to_returns with method='log'
    
    Args:
        prices: Price data
        
    Returns:
        pd.Series: Log return series
    """
    return prices_to_returns(prices, method="log")


def calculate_cumulative_returns(returns: Union[pd.Series, List, Dict[str, Any]]) -> pd.Series:
    """
    Calculate cumulative returns from return series.
    
    From financial-analysis-function-library.json time_series_processing category
    Uses pandas built-in methods for cumulative product
    
    Args:
        returns: Return series
        
    Returns:
        pd.Series: Cumulative return series
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Calculate cumulative returns using pandas
        cumulative_returns = (1 + returns_series).cumprod() - 1
        
        return cumulative_returns
        
    except Exception as e:
        raise ValueError(f"Cumulative return calculation failed: {str(e)}")


def calculate_monthly_returns(daily_returns: Union[pd.Series, List, Dict[str, Any]], trading_days_per_month: int = 21) -> List[float]:
    """
    Convert daily returns to monthly returns using compounding.
    
    From financial-analysis-function-library.json time_series_processing category
    Groups daily returns into monthly periods and compounds them
    
    Args:
        daily_returns: Daily return series
        trading_days_per_month: Number of trading days to group per month (default: 21)
        
    Returns:
        List[float]: Monthly return series
    """
    try:
        returns_series = validate_return_data(daily_returns)
        
        if len(returns_series) == 0:
            return []
        
        # Convert to list for processing
        returns_list = returns_series.tolist()
        monthly_returns = []
        
        # Group daily returns into months
        for i in range(0, len(returns_list), trading_days_per_month):
            month_returns = returns_list[i:i + trading_days_per_month]
            if len(month_returns) > 0:
                # Calculate compound monthly return: (1+r1)(1+r2)...(1+rn) - 1
                compound_return = 1.0
                for daily_return in month_returns:
                    compound_return *= (1 + daily_return)
                monthly_return = compound_return - 1
                monthly_returns.append(monthly_return)
        
        return monthly_returns
        
    except Exception as e:
        raise ValueError(f"Monthly return calculation failed: {str(e)}")


# Registry of utility functions
DATA_UTILS_FUNCTIONS = {
    'validate_price_data': validate_price_data,
    'validate_return_data': validate_return_data,
    'prices_to_returns': prices_to_returns,
    'calculate_log_returns': calculate_log_returns,
    'calculate_cumulative_returns': calculate_cumulative_returns,
    'calculate_monthly_returns': calculate_monthly_returns,
    'align_series': align_series,
    'resample_data': resample_data,
    'standardize_output': standardize_output
}