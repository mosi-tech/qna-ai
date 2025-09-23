"""Data processing utilities for financial analysis and MCP server integration.

This module provides essential data validation, transformation, and utility functions
for the MCP analytics server. It handles data format standardization, time series
processing, and output formatting to ensure consistent data flow throughout the
analytics pipeline.

The module includes:
- Data validation functions for prices and returns in various formats
- Time series transformation utilities (returns calculation, resampling)
- Series alignment and data cleaning functions
- Output standardization for MCP server compatibility

All functions are designed to handle common data formats from MCP financial servers
and external APIs, ensuring robust data processing regardless of input format.

Example:
    Basic data processing workflow:
    
    >>> from mcp.analytics.utils.data_utils import validate_price_data, prices_to_returns
    >>> import pandas as pd
    >>> # Handle various price data formats
    >>> price_dict = {'2023-01-01': 100, '2023-01-02': 102, '2023-01-03': 98}
    >>> prices = validate_price_data(price_dict)
    >>> returns = prices_to_returns(prices)
    >>> print(f"Generated {len(returns)} return observations")
    
Note:
    All functions use pandas and numpy for efficient data processing and
    return standardized formats compatible with the MCP analytics ecosystem.
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
    """Validate and standardize price data from various input formats.
    
    This function handles the complexity of different price data formats commonly
    encountered in financial APIs and MCP servers. It automatically detects the
    data structure and extracts price information while performing data cleaning
    and validation to ensure consistent output format.
    
    Args:
        data: Price data in any of the following formats:
            - pandas Series: Direct price series (preferred format)
            - pandas DataFrame: Uses 'close'/'Close' column or first column
            - Dictionary: Looks for 'prices', 'close', 'data' keys or uses values directly
            - List: Simple numeric list or list of dictionaries with price fields
            - List of dicts: Extracts 'close'/'Close' or first numeric value
            
    Returns:
        pd.Series: Validated price series with numeric values and NaN values removed.
            Index preserved from original data when available.
            
    Raises:
        ValueError: If data type is unsupported, no valid price data found after
            cleaning, or data structure cannot be interpreted as price data.
            
    Example:
        >>> import pandas as pd
        >>> # Handle different input formats
        >>> dict_data = {'2023-01-01': 100.5, '2023-01-02': 102.3, '2023-01-03': 98.7}
        >>> prices1 = validate_price_data(dict_data)
        >>> 
        >>> # List of dictionaries (common MCP format)
        >>> mcp_data = [
        ...     {'timestamp': '2023-01-01', 'close': 100.5, 'volume': 1000},
        ...     {'timestamp': '2023-01-02', 'close': 102.3, 'volume': 1200}
        ... ]
        >>> prices2 = validate_price_data(mcp_data)
        >>> 
        >>> # DataFrame with multiple columns
        >>> df_data = pd.DataFrame({
        ...     'open': [100, 101], 'high': [102, 104], 'low': [99, 100], 'close': [101, 103]
        ... })
        >>> prices3 = validate_price_data(df_data)  # Uses 'close' column
        >>> 
        >>> print(f"Prices1 length: {len(prices1)}, type: {type(prices1)}")
        
    Note:
        - Automatically converts all values to numeric, coercing errors to NaN
        - Removes NaN values after conversion for clean price series
        - Preserves original index when input has datetime or meaningful index
        - For DataFrames, prioritizes 'close' > 'Close' > first column
        - For dictionaries, prioritizes 'prices' > 'close' > 'data' > direct values
        - List of dictionaries extracts first numeric value if no price fields found
        - Returns empty series if no valid data points remain after cleaning
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
    """Validate and standardize return data from various input formats.
    
    Similar to validate_price_data but specifically designed for return data
    which may have different field names and characteristics. This function
    handles the various ways return data can be structured and ensures
    consistent output for return-based calculations.
    
    Args:
        data: Return data in any of the following formats:
            - pandas Series: Direct return series (preferred format)
            - pandas DataFrame: Uses 'returns' column or first column
            - Dictionary: Looks for 'returns', 'return', 'data' keys or uses values directly
            - List: Simple numeric list or list of dictionaries with return fields
            - List of dicts: Extracts 'returns'/'return' or first numeric value
            
    Returns:
        pd.Series: Validated return series with numeric values and NaN values removed.
            Index preserved from original data when available.
            
    Raises:
        ValueError: If data type is unsupported, no valid return data found after
            cleaning, or data structure cannot be interpreted as return data.
            
    Example:
        >>> import pandas as pd
        >>> # Handle different return data formats
        >>> return_dict = {'2023-01-01': 0.01, '2023-01-02': -0.02, '2023-01-03': 0.015}
        >>> returns1 = validate_return_data(return_dict)
        >>> 
        >>> # List of return calculations
        >>> return_list = [0.01, -0.005, 0.02, -0.01]
        >>> returns2 = validate_return_data(return_list)
        >>> 
        >>> # DataFrame with return column
        >>> df_returns = pd.DataFrame({
        ...     'date': pd.date_range('2023-01-01', periods=3),
        ...     'returns': [0.01, -0.02, 0.015]
        ... })
        >>> returns3 = validate_return_data(df_returns)
        >>> 
        >>> print(f"Returns range: {returns3.min():.3f} to {returns3.max():.3f}")
        
    Note:
        - Designed specifically for return data (typically between -1 and 1)
        - Automatically converts all values to numeric, coercing errors to NaN
        - Removes NaN values after conversion for clean return series
        - For DataFrames, prioritizes 'returns' > first column
        - For dictionaries, prioritizes 'returns' > 'return' > 'data' > direct values
        - Preserves original datetime index when available for time series analysis
        - Return data validation is similar to price validation but with return-specific field names
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
    """Convert price series to returns using standard financial calculations.
    
    This function transforms price data into return data using either simple
    (arithmetic) returns or logarithmic returns. Both methods are commonly
    used in financial analysis, with simple returns being more intuitive
    and log returns having better statistical properties for analysis.
    
    Args:
        prices: Price series to convert. Will be validated using validate_price_data
            to ensure consistent input format. Must contain at least 2 price points
            to calculate returns.
        method: Return calculation method. Options:
            - "simple": Simple returns = (P_t - P_{t-1}) / P_{t-1}
            - "log": Logarithmic returns = ln(P_t / P_{t-1})
            Defaults to "simple".
            
    Returns:
        pd.Series: Return series with one fewer observation than input prices.
            Index aligned to the later price date for each return calculation.
            NaN values automatically removed.
            
    Raises:
        ValueError: If invalid method specified or price conversion fails.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> # Create sample price series
        >>> prices = pd.Series([100, 102, 98, 105, 103],
        ...                   index=pd.date_range('2023-01-01', periods=5))
        >>> 
        >>> # Calculate simple returns
        >>> simple_rets = prices_to_returns(prices, method="simple")
        >>> print(f"Simple returns: {simple_rets.tolist()}")
        >>> # Output: [0.02, -0.0392, 0.0714, -0.0190]
        >>> 
        >>> # Calculate log returns
        >>> log_rets = prices_to_returns(prices, method="log")
        >>> print(f"Log returns: {log_rets.tolist()}")
        >>> 
        >>> # Log returns are approximately equal to simple returns for small changes
        >>> diff = abs(simple_rets - log_rets).max()
        >>> print(f"Max difference: {diff:.6f}")  # Should be small for normal returns
        
    Note:
        - Simple returns are easier to interpret (0.02 = 2% gain)
        - Log returns have better properties for statistical analysis and aggregation
        - Log returns can be summed across time: total_return = sum(log_returns)
        - Simple returns must be compounded: total_return = prod(1 + simple_returns) - 1
        - Log returns are approximately equal to simple returns for small changes (<10%)
        - Uses pandas pct_change() for simple returns and numpy log for logarithmic returns
        - Output length is always len(prices) - 1 due to differencing
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
    """Align multiple time series by their common index for consistent analysis.
    
    This function is essential for financial analysis involving multiple data series
    (e.g., comparing stock returns, calculating correlations, or portfolio analysis).
    It ensures all series have the same index points, removing periods where any
    series has missing data.
    
    Args:
        *series_list: Variable number of pandas Series to align. Each series
            should have a meaningful index (preferably datetime) for alignment.
            Requires at least 2 series for alignment to be meaningful.
            
    Returns:
        List[pd.Series]: List of aligned series in the same order as input.
            All returned series will have identical indices containing only
            the intersection of all input series indices. NaN values are removed.
            
    Raises:
        ValueError: If fewer than 2 series provided or no common data points
            exist after alignment.
            
    Example:
        >>> import pandas as pd
        >>> # Create series with different but overlapping indices
        >>> series1 = pd.Series([1, 2, 3, 4], index=['A', 'B', 'C', 'D'])
        >>> series2 = pd.Series([10, 20, 30], index=['B', 'C', 'E'])  # Missing 'A', 'D'
        >>> series3 = pd.Series([100, 200, 300], index=['A', 'B', 'C'])  # Missing 'D', 'E'
        >>> 
        >>> # Align series - only 'B' and 'C' are common to all
        >>> aligned = align_series(series1, series2, series3)
        >>> print(f"Aligned indices: {aligned[0].index.tolist()}")  # ['B', 'C']
        >>> print(f"Series 1 aligned: {aligned[0].tolist()}")  # [2, 3]
        >>> print(f"Series 2 aligned: {aligned[1].tolist()}")  # [10, 20]
        >>> print(f"Series 3 aligned: {aligned[2].tolist()}")  # [100, 200]
        >>> 
        >>> # Common use case: align stock returns for correlation analysis
        >>> stock_a_returns = pd.Series([0.01, 0.02, -0.01], 
        ...                           index=pd.date_range('2023-01-01', periods=3))
        >>> stock_b_returns = pd.Series([0.015, -0.005], 
        ...                           index=pd.date_range('2023-01-02', periods=2))
        >>> aligned_returns = align_series(stock_a_returns, stock_b_returns)
        >>> correlation = aligned_returns[0].corr(aligned_returns[1])
        
    Note:
        - Uses pandas DataFrame inner join for efficient alignment
        - Preserves original data types and names when possible
        - Essential for financial calculations requiring synchronized data
        - Common use cases: correlation analysis, portfolio calculations, regression
        - Automatically handles different index types (datetime, string, numeric)
        - Returns empty series if no common index points exist
        - Order of returned series matches order of input series
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
    """Standardize function output format for MCP server compatibility.
    
    This function ensures all analytics functions return consistently formatted
    results that are compatible with the MCP server architecture. It handles
    data type conversion, adds metadata, and ensures JSON serializability for
    network transmission.
    
    Args:
        result: Function result dictionary containing the analysis results.
            Should contain the actual results and any relevant metadata.
        function_name: Name of the calling function for tracking and debugging.
            Used to identify the source of results in logs and error messages.
            
    Returns:
        Dict[str, Any]: Standardized output dictionary with:
            - success: Boolean indicating successful execution (defaults to True)
            - function: Name of the function that generated the results
            - All original result keys with converted data types
            - Metadata fields for MCP compatibility
            
    Raises:
        Exception: Returns error dictionary if standardization fails, containing
            success=False, error message, and function name for debugging.
            
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> # Example function result with mixed data types
        >>> raw_result = {
        ...     'analysis_type': 'correlation',
        ...     'correlation_value': np.float64(0.85),
        ...     'sample_size': np.int32(100),
        ...     'price_series': pd.Series([100, 102, 98]),
        ...     'data_frame': pd.DataFrame({'A': [1, 2], 'B': [3, 4]}),
        ...     'numpy_array': np.array([1, 2, 3])
        ... }
        >>> 
        >>> standardized = standardize_output(raw_result, 'calculate_correlation')
        >>> print(f"Success: {standardized['success']}")  # True
        >>> print(f"Function: {standardized['function']}")  # 'calculate_correlation'
        >>> print(f"Correlation: {standardized['correlation_value']}")  # 0.85 (Python float)
        >>> print(type(standardized['price_series']))  # <class 'list'>
        >>> print(type(standardized['data_frame']))   # <class 'list'> (records format)
        
    Note:
        - Converts numpy scalar types (float64, int32, etc.) to Python native types
        - Converts pandas Series to Python lists for JSON compatibility
        - Converts pandas DataFrames to list of records format
        - Converts numpy arrays to Python lists
        - Preserves all original keys and adds 'success' and 'function' metadata
        - Ensures all output is JSON serializable for MCP network transmission
        - Handles nested data structures recursively
        - Returns error format if conversion fails to maintain API consistency
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


# Registry of utility functions - all using proven libraries
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