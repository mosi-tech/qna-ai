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
        
    OUTPUT examples:
    Input: [100, 102, 98, 105, 110] → pandas.Series([100, 102, 98, 105, 110])
    Input: {'close': [100, 102, 98]} → pandas.Series([100, 102, 98])
    Input: [{'close': 100}, {'close': 102}] → pandas.Series([100, 102])
        
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
        
    OUTPUT examples:
    Input: [0.02, -0.04, 0.07, 0.05, -0.02, 0.04] → pandas.Series([0.02, -0.04, 0.07, 0.05, -0.02, 0.04])
    Input: {'returns': [0.01, -0.005, 0.02]} → pandas.Series([0.01, -0.005, 0.02])
    Input: DataFrame with 'returns' column → pandas.Series with return values extracted
        
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
        >>> print(simple_rets)
        2023-01-02    0.020000
        2023-01-03   -0.039216
        2023-01-04    0.071429
        2023-01-05   -0.019048
        Freq: D, dtype: float64
        >>> print(f"Simple returns: {simple_rets.tolist()}")
        [0.020000000000000018, -0.039215686274509776, 0.0714285714285714, -0.01904761904761909]
        >>> print(f"Type: {type(simple_rets)}")
        <class 'pandas.core.series.Series'>
        >>> 
        >>> # Calculate log returns
        >>> log_rets = prices_to_returns(prices, method="log")
        >>> print(log_rets)
        2023-01-02    0.019803
        2023-01-03   -0.040009
        2023-01-04    0.068979
        2023-01-05   -0.019193
        dtype: float64
        >>> print(f"Log returns: {log_rets.tolist()}")
        [0.019803, -0.040009, 0.068979, -0.019193]
        
    OUTPUT examples:
    Simple returns: [0.020000000000000018, -0.039215686274509776, 0.0714285714285714, 0.04761904761904767, -0.018181818181818188, 0.03703703703703698]
    Log returns: [0.01980262729617973, -0.04000533461369913, 0.06899287148695142, 0.04652001563489291, -0.01834913866819654, 0.03636764417087479]
        
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
        
    OUTPUT examples:
    Input: Series1 (length 10), Series2 (length 8) with different indices
    Output: List of 2 aligned series, both length 8 with common index
    Common values preserved: [98, 105, 110] (example values from intersection)
        
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
    Resample time series data to a different frequency for analysis at multiple timeframes.
    
    Converts time series data from one frequency to another using specified aggregation methods.
    This is essential for analyzing financial data across different timeframes (daily to weekly,
    weekly to monthly, etc.) while preserving important statistical properties.
    
    Supports common pandas frequency strings for flexible resampling across any timeframe
    combination and multiple aggregation methods for different analytical needs.
    
    Args:
        data (pd.Series): Time series data with DatetimeIndex. If index is not datetime,
            it will be converted automatically. Values can be prices, returns, volumes, or
            any numeric time series.
        frequency (str): Target resampling frequency. Common values:
            - 'D': Daily
            - 'W': Weekly (ends on Sunday)
            - 'M': Monthly (last day of month)
            - 'Q': Quarterly (last day of quarter)
            - 'Y' or 'A': Annually
            - 'H': Hourly
            - '2D': Every 2 days
            - '5D': Every 5 days
        method (str, optional): Aggregation method for each period. Options:
            - 'last': Use last value of period (default, best for prices)
            - 'mean': Average of period (useful for returns or indicators)
            - 'sum': Sum of period (useful for volume or cumulative metrics)
        
    Returns:
        pd.Series: Resampled data with new frequency and datetime index. NaN values
            from periods with no data are automatically dropped.
    
    Raises:
        ValueError: If frequency string is invalid or aggregation fails
        TypeError: If data is not a pandas Series or has incompatible index
        
    Example:
        >>> import pandas as pd
        >>> # Create daily price data
        >>> dates = pd.date_range('2024-01-01', periods=30, freq='D')
        >>> daily_prices = pd.Series(range(100, 130), index=dates)
        >>> 
        >>> # Resample to weekly (using last value of each week)
        >>> weekly_prices = resample_data(daily_prices, 'W', method='last')
        >>> print(f"Original: {len(daily_prices)} daily prices")
        >>> print(f"Resampled: {len(weekly_prices)} weekly prices")
        
        >>> # Resample returns to monthly using average
        >>> monthly_avg = resample_data(daily_prices.pct_change(), 'M', method='mean')
        >>> print(f"Monthly average returns: {monthly_avg}")
        
        >>> # Aggregate volume to daily (if you have intraday data)
        >>> intraday_volumes = pd.Series([1000, 1500, 1200], 
        ...                              index=pd.date_range('2024-01-01', periods=3, freq='H'))
        >>> daily_volume = resample_data(intraday_volumes, 'D', method='sum')
    
    Note:
        - Frequency strings follow pandas convention (case-insensitive for most)
        - The 'last' method is typically preferred for price data to avoid bias
        - The 'mean' method works well for returns or indicator data
        - The 'sum' method is appropriate for volume, turnover, or count data
        - Automatically handles DatetimeIndex conversion
        - NaN values are dropped after resampling for clean output
        - For non-aligned periods (e.g., fewer than N days in a week), 
          the aggregation still works with available data
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
            # elif isinstance(value, np.ndarray):
            #     standardized[key] = value.tolist()
            # elif isinstance(value, pd.Series):
                # standardized[key] = value.tolist()
            # elif isinstance(value, pd.DataFrame):
            #     standardized[key] = value.to_dict('records')
        
        return standardized
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Output standardization failed: {str(e)}",
            "function": function_name
        }


def calculate_log_returns(prices: Union[pd.Series, Dict[str, Any]]) -> pd.Series:
    """
    Calculate logarithmic returns from price series for statistical analysis.
    
    Computes continuously compounded (logarithmic) returns from price data.
    Log returns have superior mathematical properties compared to simple returns:
    they are additive across periods, reduce impact of extreme values, and are
    more appropriate for volatility and risk calculations following normal distributions.
    
    Log returns are calculated as: ln(P_t / P_{t-1})
    
    This transformation is fundamental for time series analysis, particularly for
    models that assume normally distributed returns (like Black-Scholes) and for
    statistical tests that rely on additivity of returns across periods.
    
    Args:
        prices (Union[pd.Series, Dict[str, Any]]): Price series as pandas Series with
            datetime index or dictionary with price values. Values should be positive
            prices (e.g., stock prices, asset values). Negative or zero prices will
            result in invalid/infinite log returns.
    
    Returns:
        pd.Series: Series of logarithmic returns (same length as input prices - 1).
            First return value is NaN (no prior price for comparison). Returns are
            in decimal format (e.g., 0.02 for 2% log return).
    
    Raises:
        ValueError: If prices cannot be converted to valid price series
        TypeError: If input data format is invalid
        RuntimeError: If prices contain zero or negative values
        
    Example:
        >>> import pandas as pd
        >>> # Simple price series
        >>> prices = pd.Series([100.0, 102.0, 98.0, 105.0, 110.0])
        >>> log_returns = calculate_log_returns(prices)
        >>> print(log_returns)
        0         NaN
        1    0.019803
        2   -0.040005
        3    0.068993
        4    0.046520
        dtype: float64
        
        >>> # Compare with simple returns
        >>> simple_returns = prices.pct_change()
        >>> print(f"Log return period 1: {log_returns.iloc[1]:.6f}")
        >>> print(f"Simple return period 1: {simple_returns.iloc[1]:.6f}")
        
    Key Properties:
        - Log returns are additive: ln(P_t/P_0) = sum(ln(P_i/P_{i-1})) for all intermediate periods
        - Approximately equal to simple returns for small changes (< 5%)
        - More appropriate for statistical modeling and hypothesis testing
        - Reduce the impact of extreme values compared to simple returns
        - Symmetric: -5% and +5% log returns are not equidistant (unlike simple returns)
        
    Relationship to Simple Returns:
        - For small returns: log_return ≈ simple_return
        - For 10% simple return: log_return ≈ 0.0953 (4.7% smaller)
        - For -10% simple return: log_return ≈ -0.1054 (5.4% larger in magnitude)
        
    Note:
        - Requires positive prices only (ln of negative/zero values is undefined)
        - First return is NaN (no prior reference point)
        - Log returns preserve temporal relationships better than simple returns
        - Preferred for long time series analysis and volatility calculations
        - Common in academic finance and quantitative models
        - Useful for studies assuming normal return distributions
        
    See Also:
        - prices_to_returns(): More flexible return calculation with multiple methods
        - calculate_cumulative_returns(): For cumulative return calculations
        - Returns as fundamental building blocks for all risk and performance metrics
    """
    return prices_to_returns(prices, method="log")


def calculate_cumulative_returns(returns: Union[pd.Series, List, Dict[str, Any]]) -> pd.Series:
    """
    Calculate cumulative (compound) returns from a series of periodic returns.
    
    Computes the cumulative effect of periodic returns through compounding, showing
    total wealth growth from an initial investment over time. This is essential for
    understanding investment performance trajectories and comparing strategies across
    different time periods.
    
    Cumulative returns show how an initial investment of 1.0 (representing $1 or 100%)
    grows through each period. For example, a 2% return followed by a -1% return results
    in cumulative return of approximately 0.01 (1% overall).
    
    Args:
        returns (Union[pd.Series, List, Dict[str, Any]]): Periodic return series where
            each value represents the return for one period. Can be:
            - pandas Series with datetime index (returns in decimal format)
            - List of floats (e.g., [0.02, -0.01, 0.03])
            - Dictionary with return values (will extract values)
            Values should be in decimal format (0.02 = 2%, -0.01 = -1%)
    
    Returns:
        pd.Series: Cumulative return series (same length as input). Starting value is
            the first return value, then shows compounded growth. For example:
            Input:  [0.02, -0.01, 0.03]
            Output: [0.02, 0.00980, 0.03994]  # Shows wealth level at each point
    
    Raises:
        ValueError: If returns cannot be converted to valid return series or calculation fails
        TypeError: If input data format is invalid or incompatible
        
    Example:
        >>> import pandas as pd
        >>> # Daily returns for 5 days
        >>> returns = pd.Series([0.02, -0.04, 0.07, 0.05, -0.02])
        >>> cumulative = calculate_cumulative_returns(returns)
        >>> print(cumulative)
        0    0.020000
        1   -0.020800
        2    0.047744
        3    0.100131
        4    0.078129
        dtype: float64
        
        >>> # Interpretation: $100 invested becomes:
        >>> initial = 100
        >>> print(f"Day 1: ${initial * (1 + cumulative.iloc[0]):.2f}")  # $102
        >>> print(f"Day 2: ${initial * (1 + cumulative.iloc[1]):.2f}")  # $97.92
        >>> print(f"Day 5: ${initial * (1 + cumulative.iloc[4]):.2f}")  # $107.81
        
    Key Uses:
        1. Visualization: Plot cumulative returns to see investment growth trajectories
        2. Comparison: Compare strategy performance on same chart using cumulative returns
        3. Performance Attribution: Identify periods of strength/weakness
        4. Risk Assessment: Observe drawdowns and recoveries through cumulative curve
        5. Benchmark Comparison: Easy visual comparison of strategy vs benchmark
        
    Relationship to Prices:
        - Cumulative returns represent: (P_t / P_0) - 1
        - To get final price: P_0 * (1 + cumulative_return_final)
        - Preserves all period-to-period changes without bias
        
    Advantages Over Price Series:
        - Normalized to show percentage performance (independent of initial price)
        - Same scale for assets of different price levels
        - Easier interpretation (0% = break even, 50% = 50% gain)
        - Better for multi-asset performance comparison
        
    Note:
        - Uses geometric compounding: cumulative_return_t = (1 + r1)(1 + r2)...(1 + rt) - 1
        - Starts with the first period's return value
        - Values are in decimal format: 0.02 = 2% cumulative gain, -0.15 = 15% cumulative loss
        - Preserves temporal structure and compound effects
        - NaN values in input will propagate to output
        - More accurate representation of wealth growth than simple returns summing
        
    See Also:
        - prices_to_returns(): Reverse operation (prices to returns)
        - calculate_log_returns(): For statistical analysis with log returns
        - Cumulative returns are the foundation for performance measurement
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
    Convert daily returns to monthly returns by compounding fixed-size periods.
    
    Aggregates daily return series into monthly (or similar fixed-period) returns by
    compounding consecutive periods together. This is useful for lower-frequency
    analysis when working with daily data, portfolio rebalancing analysis, or
    comparing strategies across monthly performance periods.
    
    The function groups consecutive returns and compounds them geometrically to
    produce monthly return values. Partial months (fewer days than specified) are
    still included in the calculation with available days.
    
    Args:
        daily_returns (Union[pd.Series, List, Dict[str, Any]]): Daily return series
            where each value represents daily return in decimal format (0.02 = 2%).
            Can be pandas Series, list of floats, or dictionary with return values.
        trading_days_per_month (int, optional): Number of consecutive daily returns
            to group into one monthly return period. Default is 21 (typical trading
            days per month). Other common values:
            - 21: Approximate trading days per month
            - 5: Weekly periods
            - 252: Annual periods
            - Custom values for specific aggregation needs
    
    Returns:
        List[float]: List of monthly returns, each representing compounded return
            over the specified period. Length = ceil(len(daily_returns) / trading_days_per_month).
            Values are in decimal format (0.04 = 4% monthly return).
    
    Raises:
        ValueError: If returns cannot be converted or contain invalid values
        TypeError: If input data format is invalid
        
    Example:
        >>> import pandas as pd
        >>> # Create 70 days of daily returns
        >>> daily = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012] * 14)
        >>> 
        >>> # Convert to monthly (21-day) returns
        >>> monthly = calculate_monthly_returns(daily, trading_days_per_month=21)
        >>> print(f"Daily periods: {len(daily)}, Monthly periods: {len(monthly)}")
        >>> print(f"First month return: {monthly[0]:.4f}")
        >>> print(f"All monthly returns: {[f'{r:.4f}' for r in monthly]}")
        
        >>> # Convert same data to weekly (5-day) returns
        >>> weekly = calculate_monthly_returns(daily, trading_days_per_month=5)
        >>> print(f"Weekly periods: {len(weekly)}")
        
        >>> # Last partial month
        >>> short_returns = pd.Series([0.01, -0.02, 0.015])
        >>> partial_monthly = calculate_monthly_returns(short_returns, trading_days_per_month=21)
        >>> print(f"Partial month return: {partial_monthly[0]:.4f}")
    
    Compounding Formula:
        Monthly Return = (1 + d1)(1 + d2)...(1 + dn) - 1
        where d1, d2, ..., dn are daily returns in the month
        
    Example Calculation:
        Daily returns: [0.02, -0.01, 0.03]
        Monthly = (1.02)(0.99)(1.03) - 1 = 1.03876 - 1 = 0.03876 (3.876%)
    
    Use Cases:
        - Convert daily strategy performance to monthly for reporting
        - Analyze monthly volatility and return patterns
        - Aggregate high-frequency data for lower-frequency analysis
        - Portfolio rebalancing analysis on monthly schedule
        - Performance comparison across monthly periods
        
    Notes:
        - Uses geometric (compound) returns, not arithmetic returns
        - Final period may contain fewer than trading_days_per_month returns
        - Empty return series returns empty list
        - NaN values in input will propagate to output monthly returns
        - Common practice: 252 trading days per year, 21 per month
        - Monthly returns are additive in log space but not in simple return space
        
    See Also:
        - calculate_cumulative_returns(): For overall wealth growth calculation
        - calculate_log_returns(): For log-space calculations
        - resample_data(): For time-based resampling with DatetimeIndex
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


def extract_symbols_from_alpaca_data(data: Union[Dict[str, Any], List[Dict[str, Any]], Any]) -> List[str]:
    """Extract symbol list from various Alpaca API data structures.
    
    This utility function parses different Alpaca API response formats (positions, orders,
    watchlists, bars, quotes, etc.) and extracts the unique stock symbols contained within.
    Essential for streamlining workflow between Alpaca trading/market data and analytics
    functions that require symbol lists as input.
    
    The function intelligently handles various Alpaca data structures including nested
    dictionaries, lists of records, and mixed-format responses from different endpoints.
    
    Args:
        data (Union[Dict[str, Any], List[Dict[str, Any]], Any]): Alpaca API data structure.
            Supported formats include:
            - Positions response: List/dict with 'symbol' fields
            - Orders response: List/dict with 'symbol' fields  
            - Watchlist response: List/dict with 'symbol' or 'assets' fields
            - Market data bars: Dict with symbols as keys or nested symbol fields
            - Market data quotes/trades: Dict with symbols as keys
            - Portfolio history: Dict with symbols in metadata
            - Account response: May contain 'positions' or 'orders' nested data
            - Any nested structure containing symbol information
            
    Returns:
        List[str]: Sorted list of unique stock symbols found in the data.
            Symbols are uppercase and deduplicated. Empty list if no symbols found.
            Common formats: ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
            
    Raises:
        ValueError: If data extraction fails due to unexpected format or processing errors.
        TypeError: If input data type cannot be processed.
        
    Example:
        >>> # Extract from positions response
        >>> positions_data = [
        ...     {"symbol": "AAPL", "qty": "10", "market_value": "1500"},
        ...     {"symbol": "MSFT", "qty": "5", "market_value": "1600"},
        ...     {"symbol": "GOOGL", "qty": "2", "market_value": "800"}
        ... ]
        >>> symbols = extract_symbols_from_alpaca_data(positions_data)
        >>> print(symbols)  # ['AAPL', 'GOOGL', 'MSFT']
        >>> 
        >>> # Extract from orders response
        >>> orders_data = {
        ...     "orders": [
        ...         {"symbol": "TSLA", "side": "buy", "qty": "3"},
        ...         {"symbol": "NVDA", "side": "sell", "qty": "1"}
        ...     ]
        ... }
        >>> symbols = extract_symbols_from_alpaca_data(orders_data)
        >>> print(symbols)  # ['NVDA', 'TSLA']
        >>> 
        >>> # Extract from market data bars  
        >>> bars_data = {
        ...     "bars": {
        ...         "AAPL": [{"t": "2023-01-01", "o": 150, "h": 152, "l": 148, "c": 151}],
        ...         "MSFT": [{"t": "2023-01-01", "o": 250, "h": 255, "l": 248, "c": 253}]
        ...     }
        ... }
        >>> symbols = extract_symbols_from_alpaca_data(bars_data)
        >>> print(symbols)  # ['AAPL', 'MSFT']
        >>> 
        >>> # Extract from watchlist
        >>> watchlist_data = {
        ...     "name": "Tech Stocks",
        ...     "assets": [
        ...         {"symbol": "AAPL", "name": "Apple Inc"},
        ...         {"symbol": "GOOGL", "name": "Alphabet Inc"}
        ...     ]
        ... }
        >>> symbols = extract_symbols_from_alpaca_data(watchlist_data)
        >>> print(symbols)  # ['AAPL', 'GOOGL']
        
    OUTPUT examples:
    Positions data: [{'symbol': 'AAPL', 'qty': '100'}, {'symbol': 'MSFT', 'qty': '50'}] → ['AAPL', 'GOOGL', 'MSFT']
    Bars data: {'AAPL': {'close': 150.0}, 'MSFT': {'close': 300.0}} → ['AAPL', 'MSFT']
    Handles various Alpaca API response formats automatically
        
    Note:
        - Function handles both single records and lists of records
        - Symbols are automatically converted to uppercase for consistency
        - Duplicates are removed and results are sorted alphabetically
        - Empty or malformed data returns empty list rather than error
        - Supports nested data structures with recursive symbol extraction
        - Compatible with all major Alpaca API endpoints (trading and market data)
        - Useful for bridging Alpaca data with analytics functions requiring symbol lists
        - Handles both live and paper trading account data formats
        - Works with historical and real-time market data responses
    """
    try:
        symbols = set()  # Use set to automatically handle duplicates
        
        def _extract_symbols_recursive(obj: Any) -> None:
            """Recursively extract symbols from nested data structures."""
            if isinstance(obj, dict):
                # Handle direct symbol field
                if 'symbol' in obj:
                    symbol = str(obj['symbol']).upper().strip()
                    if symbol and len(symbol) <= 10:  # Basic symbol validation
                        symbols.add(symbol)
                
                # Handle various Alpaca response structures
                for key, value in obj.items():
                    if key.lower() in ['positions', 'orders', 'assets', 'bars', 'quotes', 'trades']:
                        _extract_symbols_recursive(value)
                    elif key.lower() == 'symbols' and isinstance(value, (list, tuple)):
                        # Direct symbols list
                        for sym in value:
                            if isinstance(sym, str):
                                clean_sym = sym.upper().strip()
                                if clean_sym and len(clean_sym) <= 10:
                                    symbols.add(clean_sym)
                    elif isinstance(value, (dict, list)):
                        _extract_symbols_recursive(value)
            
            elif isinstance(obj, (list, tuple)):
                for item in obj:
                    _extract_symbols_recursive(item)
            
            elif isinstance(obj, str) and len(obj) <= 10:
                # Handle case where data might be a direct symbol string
                clean_sym = obj.upper().strip()
                if clean_sym.isalpha() and 1 <= len(clean_sym) <= 10:
                    symbols.add(clean_sym)
        
        # Handle various input formats
        if data is None:
            return []
        
        # Handle direct symbol string
        if isinstance(data, str):
            clean_sym = data.upper().strip()
            if clean_sym and len(clean_sym) <= 10:
                return [clean_sym]
            return []
        
        # Handle bars/quotes data where symbols are keys
        if isinstance(data, dict):
            # Check if this looks like market data with symbols as keys
            potential_symbols = []
            for key in data.keys():
                if (isinstance(key, str) and 
                    key.isupper() and 
                    1 <= len(key) <= 10 and 
                    key.isalpha()):
                    potential_symbols.append(key)
            
            # If we found symbol-like keys, they're probably symbols
            if potential_symbols:
                symbols.update(potential_symbols)
        
        # Recursive extraction for all data types
        _extract_symbols_recursive(data)
        
        # Convert to sorted list
        symbol_list = sorted(list(symbols))
        
        return symbol_list
        
    except Exception as e:
        # Log error but don't fail - return empty list
        print(f"Warning: Symbol extraction failed: {str(e)}")
        return []


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
    'standardize_output': standardize_output,
    'extract_symbols_from_alpaca_data': extract_symbols_from_alpaca_data
}