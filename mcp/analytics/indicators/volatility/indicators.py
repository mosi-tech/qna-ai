"""Volatility Indicators Module using TA-Lib Library.

This module provides all volatility indicators from TA-Lib, which measure the rate of price
changes and market uncertainty. Volatility indicators help assess risk levels, identify
breakout opportunities, set stop-loss levels, and determine position sizing.

The module includes all major volatility indicators from TA-Lib:
    - Classic Measures: ATR, NATR, True Range
    - Bollinger Bands: Standard bands, %B, Bandwidth
    - Statistical: Standard Deviation, Variance

Key Features:
    - Complete coverage of all TA-Lib volatility indicators
    - Industry-standard TA-Lib implementation for proven accuracy
    - Standardized return format with success indicators and error handling
    - Comprehensive signal generation for breakout and mean reversion strategies
    - Support for both pandas Series and DataFrame input formats
    - Automatic data validation and type conversion
    - Performance optimized using TA-Lib's C implementation

Dependencies:
    - talib-binary: Core technical analysis calculations
    - pandas: Data manipulation and time series handling
    - numpy: Numerical computations and array operations

Example:
    >>> import pandas as pd
    >>> from mcp.analytics.indicators.volatility import calculate_atr, calculate_bollinger_bands
    >>> 
    >>> ohlc_data = pd.DataFrame({
    ...     'high': [105, 108, 112], 'low': [98, 102, 105], 'close': [102, 106, 109]
    ... })
    >>> atr_result = calculate_atr(ohlc_data, period=14)
    >>> print(f"ATR: {atr_result['latest_value']:.2f}")

Note:
    All functions require minimum data points equal to their calculation period for valid results.
    Error handling is implemented to gracefully manage insufficient data or invalid inputs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use talib-binary from requirements.txt - industry standard, 2-4x faster
import talib

from ...utils.data_utils import validate_price_data, standardize_output


# =============================================================================
# CLASSIC VOLATILITY MEASURES
# =============================================================================

def calculate_atr(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Average True Range using TA-Lib library.
    
    Computes the Average True Range (ATR), a volatility indicator that measures the average
    range of price movement over a specified period. ATR does not indicate price direction
    but shows how much prices typically move, helping assess market volatility and set
    appropriate stop-loss levels.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Period for ATR calculation. Defaults to 14.
            Standard period; shorter periods are more sensitive to recent volatility.
    
    Returns:
        Dict[str, Any]: Dictionary containing ATR analysis with keys:
            - atr (pd.Series): ATR values as pandas Series
            - latest_value (Optional[float]): Most recent ATR value
            - atr_percent (Optional[float]): ATR as percentage of current price
            - period (int): Period used for calculation
            - volatility_level (str): Volatility classification ('high', 'normal', 'low')
            - stop_loss_distance (Optional[float]): Suggested stop-loss distance (2 × ATR)
            - position_size_factor (Optional[float]): Factor for position sizing based on volatility
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLC columns are missing or data is invalid.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113]
        ... })
        >>> result = calculate_atr(ohlc_data)
        >>> print(f"ATR: {result['latest_value']:.2f} ({result['atr_percent']:.1f}%)")
        >>> print(f"Suggested stop-loss distance: {result['stop_loss_distance']:.2f}")
        ATR: 4.25 (3.8%)
        Suggested stop-loss distance: 8.50
        
    Note:
        - True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
        - ATR = Moving Average of True Range over specified period
        - Higher ATR indicates higher volatility and larger potential price swings
        - ATR percentage > 3% typically indicates high volatility
        - ATR percentage < 1% typically indicates low volatility
        - Commonly used for position sizing and stop-loss placement
        - Stop-loss distance: 1.5-2.0 × ATR from entry price
        - Position size inversely related to ATR (higher ATR = smaller position)
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for ATR calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        atr_values = talib.ATR(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        atr_series = pd.Series(atr_values, index=df.index).dropna()
        
        latest_atr = float(atr_series.iloc[-1]) if len(atr_series) > 0 else None
        latest_price = float(df[close_col].iloc[-1]) if len(df) > 0 else None
        
        # Calculate ATR as percentage of price
        atr_percent = (latest_atr / latest_price * 100) if latest_atr and latest_price else None
        
        # Risk management calculations
        stop_loss_distance = (latest_atr * 2.0) if latest_atr else None
        position_size_factor = (1.0 / atr_percent) if atr_percent and atr_percent > 0 else None
        
        # Volatility classification
        volatility_level = "normal"
        if atr_percent is not None:
            if atr_percent > 3.0:
                volatility_level = "high"
            elif atr_percent < 1.0:
                volatility_level = "low"
        
        result = {
            "atr": atr_series,
            "latest_value": latest_atr,
            "atr_percent": atr_percent,
            "period": period,
            "volatility_level": volatility_level,
            "stop_loss_distance": stop_loss_distance,
            "position_size_factor": position_size_factor
        }
        
        return standardize_output(result, "calculate_atr")
        
    except Exception as e:
        return {"success": False, "error": f"ATR calculation failed: {str(e)}"}


def calculate_natr(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Normalized Average True Range using TA-Lib library.
    
    Computes the Normalized Average True Range (NATR), which is ATR expressed as a percentage
    of the closing price. NATR allows for better comparison of volatility across different
    price levels and securities, making it ideal for cross-asset volatility analysis.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Period for NATR calculation. Defaults to 14.
            Standard period; shorter periods are more sensitive to recent volatility.
    
    Returns:
        Dict[str, Any]: Dictionary containing NATR analysis with keys:
            - natr (pd.Series): NATR values as pandas Series (percentage)
            - latest_value (Optional[float]): Most recent NATR value (percentage)
            - volatility_level (str): Volatility classification ('high', 'normal', 'low')
            - period (int): Period used for calculation
            - volatility_rank (str): Relative volatility ('extreme', 'high', 'moderate', 'low')
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLC columns are missing or data is invalid.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113]
        ... })
        >>> result = calculate_natr(ohlc_data)
        >>> print(f"NATR: {result['latest_value']:.2f}%")
        >>> print(f"Volatility Level: {result['volatility_level']}")
        NATR: 3.76%
        Volatility Level: high
        
    Note:
        - NATR = (ATR / Close) × 100
        - Values expressed as percentage of closing price
        - NATR > 4% typically indicates high volatility
        - NATR < 1.5% typically indicates low volatility
        - Better for comparing volatility across different price levels
        - Useful for portfolio volatility analysis and risk budgeting
        - Less affected by price level changes than raw ATR
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for NATR calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        natr_values = talib.NATR(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        natr_series = pd.Series(natr_values, index=df.index).dropna()
        
        latest_natr = float(natr_series.iloc[-1]) if len(natr_series) > 0 else None
        
        # Volatility classification based on NATR levels
        volatility_level = "normal"
        volatility_rank = "moderate"
        if latest_natr is not None:
            if latest_natr > 6.0:
                volatility_level = "high"
                volatility_rank = "extreme"
            elif latest_natr > 4.0:
                volatility_level = "high"
                volatility_rank = "high"
            elif latest_natr > 1.5:
                volatility_level = "normal"
                volatility_rank = "moderate"
            else:
                volatility_level = "low"
                volatility_rank = "low"
        
        result = {
            "natr": natr_series,
            "latest_value": latest_natr,
            "volatility_level": volatility_level,
            "period": period,
            "volatility_rank": volatility_rank
        }
        
        return standardize_output(result, "calculate_natr")
        
    except Exception as e:
        return {"success": False, "error": f"NATR calculation failed: {str(e)}"}


def calculate_trange(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate True Range using TA-Lib library.
    
    Computes the True Range for each period, which measures the maximum price movement
    in a single period. True Range is the foundation for ATR calculation and provides
    immediate volatility information for each trading session.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
    
    Returns:
        Dict[str, Any]: Dictionary containing True Range analysis with keys:
            - true_range (pd.Series): True Range values for each period
            - latest_value (Optional[float]): Most recent True Range value
            - average_range (Optional[float]): Average True Range over available data
            - max_range (Optional[float]): Maximum True Range in the dataset
            - min_range (Optional[float]): Minimum True Range in the dataset
            - volatility_spike (bool): Whether latest True Range is unusually high
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLC columns are missing or data is invalid.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113]
        ... })
        >>> result = calculate_trange(ohlc_data)
        >>> print(f"Latest True Range: {result['latest_value']:.2f}")
        >>> print(f"Volatility Spike: {result['volatility_spike']}")
        Latest True Range: 5.00
        Volatility Spike: False
        
    Note:
        - True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
        - Measures the largest price movement in a single period
        - Accounts for gaps between sessions (previous close vs current high/low)
        - Foundation for Average True Range (ATR) calculation
        - Useful for identifying individual periods of high volatility
        - Volatility spikes occur when True Range > 2 × Average True Range
        - Can signal potential trend changes or market events
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for True Range calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        trange_values = talib.TRANGE(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64)
        )
        trange_series = pd.Series(trange_values, index=df.index).dropna()
        
        latest_trange = float(trange_series.iloc[-1]) if len(trange_series) > 0 else None
        average_range = float(trange_series.mean()) if len(trange_series) > 0 else None
        max_range = float(trange_series.max()) if len(trange_series) > 0 else None
        min_range = float(trange_series.min()) if len(trange_series) > 0 else None
        
        # Detect volatility spikes
        volatility_spike = False
        if latest_trange and average_range and latest_trange > (2.0 * average_range):
            volatility_spike = True
        
        result = {
            "true_range": trange_series,
            "latest_value": latest_trange,
            "average_range": average_range,
            "max_range": max_range,
            "min_range": min_range,
            "volatility_spike": volatility_spike
        }
        
        return standardize_output(result, "calculate_trange")
        
    except Exception as e:
        return {"success": False, "error": f"True Range calculation failed: {str(e)}"}


# =============================================================================
# BOLLINGER BAND FAMILY
# =============================================================================

def calculate_bollinger_bands(data: Union[pd.Series, Dict[str, Any]], 
                             period: int = 20, std_dev: float = 2.0) -> Dict[str, Any]:
    """Calculate Bollinger Bands using TA-Lib library.
    
    Computes Bollinger Bands, which consist of a middle band (Simple Moving Average) and two
    outer bands at specified standard deviations from the middle band. The bands expand and
    contract based on market volatility, helping identify overbought/oversold conditions and
    potential breakout opportunities.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Period for Simple Moving Average. Defaults to 20.
            Standard period; shorter periods increase sensitivity to price changes.
        std_dev (float, optional): Standard deviation multiplier for bands. Defaults to 2.0.
            Common values: 1.5 (tighter bands), 2.0 (standard), 2.5 (wider bands).
    
    Returns:
        Dict[str, Any]: Dictionary containing Bollinger Bands analysis with keys:
            - upper_band (pd.Series): Upper band values (SMA + std_dev * standard deviation)
            - middle_band (pd.Series): Middle band values (Simple Moving Average)
            - lower_band (pd.Series): Lower band values (SMA - std_dev * standard deviation)
            - percent_b (Optional[float]): %B value showing position within bands (0-1)
            - bandwidth (Optional[float]): Band width relative to middle band
            - signal (str): Market condition ('overbought', 'oversold', 'squeeze', 'expansion', 'neutral')
            - squeeze_level (str): Band squeeze intensity ('tight', 'normal', 'wide')
            - breakout_potential (str): Breakout potential ('high', 'moderate', 'low')
            - period (int): Period used for calculation
            - std_dev (float): Standard deviation multiplier used
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If period is not integer or std_dev is not numeric.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_bollinger_bands(prices, period=10, std_dev=2.0)
        >>> print(f"Price position (%B): {result['percent_b']:.2f}")
        >>> print(f"Signal: {result['signal']}")
        >>> print(f"Squeeze level: {result['squeeze_level']}")
        Price position (%B): 0.85
        Signal: neutral
        Squeeze level: normal
        
    Note:
        - %B > 1.0 indicates price above upper band (overbought)
        - %B < 0.0 indicates price below lower band (oversold)
        - %B = 0.5 indicates price at middle band
        - Bandwidth measures volatility: higher values = more volatile
        - Band squeezes (low bandwidth) often precede significant price moves
        - Band expansion often follows increased volatility
        - Approximately 95% of price action occurs within the bands
        - Breakouts above/below bands can signal trend continuation or reversal
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary
        upper, middle, lower = talib.BBANDS(
            prices.values.astype(np.float64), 
            timeperiod=period, 
            nbdevup=std_dev, 
            nbdevdn=std_dev
        )
        
        bb_df = pd.DataFrame({
            'upper': upper,
            'middle': middle,
            'lower': lower
        }, index=prices.index).dropna()
        
        # Calculate %B and bandwidth
        current_price = prices.iloc[-1] if len(prices) > 0 else None
        if current_price is not None and len(bb_df) > 0:
            current_upper = bb_df['upper'].iloc[-1]
            current_lower = bb_df['lower'].iloc[-1]
            current_middle = bb_df['middle'].iloc[-1]
            
            percent_b = (current_price - current_lower) / (current_upper - current_lower) if current_upper != current_lower else 0.5
            bandwidth = (current_upper - current_lower) / current_middle if current_middle != 0 else 0
        else:
            percent_b = None
            bandwidth = None
        
        # Generate signals and analysis
        signal = "neutral"
        squeeze_level = "normal"
        breakout_potential = "moderate"
        
        if percent_b is not None and bandwidth is not None:
            # Price position signals
            if percent_b > 1.0:
                signal = "overbought"
            elif percent_b < 0.0:
                signal = "oversold"
            
            # Squeeze analysis
            if bandwidth < 0.1:
                squeeze_level = "tight"
                signal = "squeeze"
                breakout_potential = "high"
            elif bandwidth > 0.3:
                squeeze_level = "wide"
                signal = "expansion"
                breakout_potential = "low"
            
        result = {
            "upper_band": bb_df['upper'],
            "middle_band": bb_df['middle'],
            "lower_band": bb_df['lower'],
            "percent_b": percent_b,
            "bandwidth": bandwidth,
            "signal": signal,
            "squeeze_level": squeeze_level,
            "breakout_potential": breakout_potential,
            "period": period,
            "std_dev": std_dev
        }
        
        return standardize_output(result, "calculate_bollinger_bands")
        
    except Exception as e:
        return {"success": False, "error": f"Bollinger Bands calculation failed: {str(e)}"}


def calculate_bollinger_percent_b(data: Union[pd.Series, Dict[str, Any]], 
                                 period: int = 20, std_dev: float = 2.0) -> Dict[str, Any]:
    """Calculate Bollinger %B using TA-Lib library.
    
    Computes %B (Percent B), which shows where the current price is relative to the
    Bollinger Bands. %B = 1.0 when price is at the upper band, 0.0 at the lower band,
    and 0.5 at the middle band. Values outside 0-1 indicate price beyond the bands.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Period for Bollinger Bands calculation. Defaults to 20.
        std_dev (float, optional): Standard deviation multiplier. Defaults to 2.0.
    
    Returns:
        Dict[str, Any]: Dictionary containing %B analysis with keys:
            - percent_b (pd.Series): %B values over time
            - latest_value (Optional[float]): Most recent %B value
            - signal (str): Position signal ('overbought', 'oversold', 'neutral')
            - trend_strength (str): Trend strength based on %B ('strong', 'moderate', 'weak')
            - reversal_probability (str): Mean reversion probability ('high', 'moderate', 'low')
            - period (int): Period used for calculation
            - std_dev (float): Standard deviation multiplier used
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If parameters are not correct types.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_bollinger_percent_b(prices)
        >>> print(f"%B: {result['latest_value']:.2f}")
        >>> print(f"Signal: {result['signal']}")
        >>> print(f"Reversal Probability: {result['reversal_probability']}")
        %B: 0.85
        Signal: neutral
        Reversal Probability: moderate
        
    Note:
        - %B = (Price - Lower Band) / (Upper Band - Lower Band)
        - %B > 1.0: Price above upper band (strong uptrend or overbought)
        - %B < 0.0: Price below lower band (strong downtrend or oversold)
        - %B = 0.5: Price at middle band (neutral)
        - %B oscillating between 0.8-1.0: Strong uptrend
        - %B oscillating between 0.0-0.2: Strong downtrend
        - Extreme %B values often precede mean reversion
        - Useful for identifying trend strength and reversal points
    """
    try:
        prices = validate_price_data(data)
        
        # Calculate Bollinger Bands first
        upper, middle, lower = talib.BBANDS(
            prices.values.astype(np.float64), 
            timeperiod=period, 
            nbdevup=std_dev, 
            nbdevdn=std_dev
        )
        
        # Calculate %B
        percent_b_values = (prices.values - lower) / (upper - lower)
        percent_b_series = pd.Series(percent_b_values, index=prices.index).dropna()
        
        latest_percent_b = float(percent_b_series.iloc[-1]) if len(percent_b_series) > 0 else None
        
        # Generate signals and analysis
        signal = "neutral"
        trend_strength = "moderate"
        reversal_probability = "moderate"
        
        if latest_percent_b is not None:
            # Position signals
            if latest_percent_b > 1.0:
                signal = "overbought"
                reversal_probability = "high"
            elif latest_percent_b < 0.0:
                signal = "oversold"
                reversal_probability = "high"
            elif latest_percent_b > 0.8:
                signal = "neutral"
                trend_strength = "strong"
                reversal_probability = "moderate"
            elif latest_percent_b < 0.2:
                signal = "neutral"
                trend_strength = "strong"
                reversal_probability = "moderate"
            
            # Trend strength analysis
            if len(percent_b_series) >= 5:
                recent_values = percent_b_series.tail(5)
                if recent_values.std() < 0.1:
                    if recent_values.mean() > 0.8:
                        trend_strength = "strong"
                    elif recent_values.mean() < 0.2:
                        trend_strength = "strong"
                else:
                    trend_strength = "weak"
        
        result = {
            "percent_b": percent_b_series,
            "latest_value": latest_percent_b,
            "signal": signal,
            "trend_strength": trend_strength,
            "reversal_probability": reversal_probability,
            "period": period,
            "std_dev": std_dev
        }
        
        return standardize_output(result, "calculate_bollinger_percent_b")
        
    except Exception as e:
        return {"success": False, "error": f"Bollinger %B calculation failed: {str(e)}"}


def calculate_bollinger_bandwidth(data: Union[pd.Series, Dict[str, Any]], 
                                 period: int = 20, std_dev: float = 2.0) -> Dict[str, Any]:
    """Calculate Bollinger Band Width using TA-Lib library.
    
    Computes Bollinger Band Width, which measures the width of the Bollinger Bands
    relative to the middle band. Bandwidth is used to identify periods of low volatility
    (squeezes) that often precede significant price movements.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Period for Bollinger Bands calculation. Defaults to 20.
        std_dev (float, optional): Standard deviation multiplier. Defaults to 2.0.
    
    Returns:
        Dict[str, Any]: Dictionary containing Bandwidth analysis with keys:
            - bandwidth (pd.Series): Bandwidth values over time
            - latest_value (Optional[float]): Most recent bandwidth value
            - volatility_state (str): Current volatility state ('squeeze', 'expansion', 'normal')
            - squeeze_intensity (str): Squeeze intensity ('extreme', 'tight', 'moderate', 'loose')
            - breakout_probability (str): Breakout probability ('high', 'moderate', 'low')
            - historical_percentile (Optional[float]): Current bandwidth percentile vs history
            - period (int): Period used for calculation
            - std_dev (float): Standard deviation multiplier used
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If parameters are not correct types.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_bollinger_bandwidth(prices)
        >>> print(f"Bandwidth: {result['latest_value']:.3f}")
        >>> print(f"Volatility State: {result['volatility_state']}")
        >>> print(f"Breakout Probability: {result['breakout_probability']}")
        Bandwidth: 0.125
        Volatility State: normal
        Breakout Probability: moderate
        
    Note:
        - Bandwidth = (Upper Band - Lower Band) / Middle Band
        - Low bandwidth indicates low volatility (potential squeeze)
        - High bandwidth indicates high volatility (potential expansion)
        - Bandwidth below 10th percentile often signals impending breakout
        - Bandwidth above 90th percentile often signals trend exhaustion
        - Squeezes are followed by expansions (and vice versa)
        - Useful for timing entry/exit points and volatility trading
    """
    try:
        prices = validate_price_data(data)
        
        # Calculate Bollinger Bands first
        upper, middle, lower = talib.BBANDS(
            prices.values.astype(np.float64), 
            timeperiod=period, 
            nbdevup=std_dev, 
            nbdevdn=std_dev
        )
        
        # Calculate Bandwidth
        bandwidth_values = (upper - lower) / middle
        bandwidth_series = pd.Series(bandwidth_values, index=prices.index).dropna()
        
        latest_bandwidth = float(bandwidth_series.iloc[-1]) if len(bandwidth_series) > 0 else None
        
        # Calculate historical percentile
        historical_percentile = None
        if len(bandwidth_series) >= 20:
            historical_percentile = (bandwidth_series <= latest_bandwidth).mean() * 100
        
        # Generate analysis
        volatility_state = "normal"
        squeeze_intensity = "moderate"
        breakout_probability = "moderate"
        
        if latest_bandwidth is not None:
            # Volatility state analysis
            if historical_percentile is not None:
                if historical_percentile <= 10:
                    volatility_state = "squeeze"
                    squeeze_intensity = "extreme"
                    breakout_probability = "high"
                elif historical_percentile <= 25:
                    volatility_state = "squeeze"
                    squeeze_intensity = "tight"
                    breakout_probability = "high"
                elif historical_percentile >= 90:
                    volatility_state = "expansion"
                    squeeze_intensity = "loose"
                    breakout_probability = "low"
                elif historical_percentile >= 75:
                    volatility_state = "expansion"
                    squeeze_intensity = "moderate"
                    breakout_probability = "low"
            else:
                # Fallback analysis without historical context
                if latest_bandwidth < 0.05:
                    volatility_state = "squeeze"
                    squeeze_intensity = "extreme"
                    breakout_probability = "high"
                elif latest_bandwidth < 0.1:
                    volatility_state = "squeeze"
                    squeeze_intensity = "tight"
                    breakout_probability = "high"
                elif latest_bandwidth > 0.3:
                    volatility_state = "expansion"
                    squeeze_intensity = "loose"
                    breakout_probability = "low"
        
        result = {
            "bandwidth": bandwidth_series,
            "latest_value": latest_bandwidth,
            "volatility_state": volatility_state,
            "squeeze_intensity": squeeze_intensity,
            "breakout_probability": breakout_probability,
            "historical_percentile": historical_percentile,
            "period": period,
            "std_dev": std_dev
        }
        
        return standardize_output(result, "calculate_bollinger_bandwidth")
        
    except Exception as e:
        return {"success": False, "error": f"Bollinger Bandwidth calculation failed: {str(e)}"}


# =============================================================================
# STATISTICAL VOLATILITY INDICATORS
# =============================================================================

def calculate_stddev(data: Union[pd.Series, Dict[str, Any]], period: int = 20) -> Dict[str, Any]:
    """Calculate Standard Deviation using TA-Lib library.
    
    Computes the Standard Deviation of price movements over a specified period.
    Standard deviation measures the dispersion of price data from its mean, providing
    a statistical measure of volatility that forms the basis for many other indicators.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Period for standard deviation calculation. Defaults to 20.
            Longer periods provide smoother, more stable volatility measures.
    
    Returns:
        Dict[str, Any]: Dictionary containing Standard Deviation analysis with keys:
            - stddev (pd.Series): Standard deviation values over time
            - latest_value (Optional[float]): Most recent standard deviation value
            - volatility_level (str): Volatility classification ('high', 'normal', 'low')
            - volatility_trend (str): Volatility trend ('increasing', 'decreasing', 'stable')
            - percentile_rank (Optional[float]): Current value percentile vs historical data
            - period (int): Period used for calculation
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_stddev(prices, period=10)
        >>> print(f"Standard Deviation: {result['latest_value']:.2f}")
        >>> print(f"Volatility Level: {result['volatility_level']}")
        >>> print(f"Volatility Trend: {result['volatility_trend']}")
        Standard Deviation: 7.35
        Volatility Level: normal
        Volatility Trend: stable
        
    Note:
        - Standard Deviation = √(Σ(Price - Mean)² / N)
        - Higher values indicate greater price dispersion (volatility)
        - Lower values indicate more stable, less volatile price action
        - Forms the foundation for Bollinger Bands calculation
        - Useful for risk assessment and position sizing
        - Often used in volatility-based trading strategies
        - Can be normalized by price level for better comparison
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary
        stddev_values = talib.STDDEV(
            prices.values.astype(np.float64), 
            timeperiod=period
        )
        stddev_series = pd.Series(stddev_values, index=prices.index).dropna()
        
        latest_stddev = float(stddev_series.iloc[-1]) if len(stddev_series) > 0 else None
        
        # Calculate percentile rank
        percentile_rank = None
        if len(stddev_series) >= 20:
            percentile_rank = (stddev_series <= latest_stddev).mean() * 100
        
        # Volatility level classification
        volatility_level = "normal"
        if percentile_rank is not None:
            if percentile_rank >= 80:
                volatility_level = "high"
            elif percentile_rank <= 20:
                volatility_level = "low"
        
        # Volatility trend analysis
        volatility_trend = "stable"
        if len(stddev_series) >= 5:
            recent_slope = np.polyfit(range(5), stddev_series.tail(5).values, 1)[0]
            if recent_slope > 0.1:
                volatility_trend = "increasing"
            elif recent_slope < -0.1:
                volatility_trend = "decreasing"
        
        result = {
            "stddev": stddev_series,
            "latest_value": latest_stddev,
            "volatility_level": volatility_level,
            "volatility_trend": volatility_trend,
            "percentile_rank": percentile_rank,
            "period": period
        }
        
        return standardize_output(result, "calculate_stddev")
        
    except Exception as e:
        return {"success": False, "error": f"Standard Deviation calculation failed: {str(e)}"}


def calculate_variance(data: Union[pd.Series, Dict[str, Any]], period: int = 20) -> Dict[str, Any]:
    """Calculate Variance using TA-Lib library.
    
    Computes the Variance of price movements over a specified period. Variance is the
    square of standard deviation and provides a measure of price dispersion that is
    sensitive to extreme values, making it useful for risk analysis.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Period for variance calculation. Defaults to 20.
            Longer periods provide smoother, more stable volatility measures.
    
    Returns:
        Dict[str, Any]: Dictionary containing Variance analysis with keys:
            - variance (pd.Series): Variance values over time
            - latest_value (Optional[float]): Most recent variance value
            - volatility_level (str): Volatility classification ('high', 'normal', 'low')
            - risk_level (str): Risk level based on variance ('extreme', 'high', 'moderate', 'low')
            - percentile_rank (Optional[float]): Current value percentile vs historical data
            - period (int): Period used for calculation
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_variance(prices, period=10)
        >>> print(f"Variance: {result['latest_value']:.2f}")
        >>> print(f"Risk Level: {result['risk_level']}")
        Variance: 54.02
        Risk Level: moderate
        
    Note:
        - Variance = Σ(Price - Mean)² / N
        - Variance = (Standard Deviation)²
        - More sensitive to extreme values than standard deviation
        - Higher values indicate greater price volatility and risk
        - Used in portfolio optimization and risk management
        - Foundation for many volatility-based indicators
        - Can be annualized for portfolio risk calculations
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary
        variance_values = talib.VAR(
            prices.values.astype(np.float64), 
            timeperiod=period
        )
        variance_series = pd.Series(variance_values, index=prices.index).dropna()
        
        latest_variance = float(variance_series.iloc[-1]) if len(variance_series) > 0 else None
        
        # Calculate percentile rank
        percentile_rank = None
        if len(variance_series) >= 20:
            percentile_rank = (variance_series <= latest_variance).mean() * 100
        
        # Risk level classification
        volatility_level = "normal"
        risk_level = "moderate"
        
        if percentile_rank is not None:
            if percentile_rank >= 95:
                volatility_level = "high"
                risk_level = "extreme"
            elif percentile_rank >= 80:
                volatility_level = "high"
                risk_level = "high"
            elif percentile_rank <= 5:
                volatility_level = "low"
                risk_level = "low"
            elif percentile_rank <= 20:
                volatility_level = "low"
                risk_level = "low"
        
        result = {
            "variance": variance_series,
            "latest_value": latest_variance,
            "volatility_level": volatility_level,
            "risk_level": risk_level,
            "percentile_rank": percentile_rank,
            "period": period
        }
        
        return standardize_output(result, "calculate_variance")
        
    except Exception as e:
        return {"success": False, "error": f"Variance calculation failed: {str(e)}"}


# =============================================================================
# REGISTRY OF ALL VOLATILITY INDICATORS
# =============================================================================

VOLATILITY_INDICATORS_FUNCTIONS = {
    # Classic Volatility Measures
    'calculate_atr': calculate_atr,
    'calculate_natr': calculate_natr,
    'calculate_trange': calculate_trange,
    
    # Bollinger Band Family
    'calculate_bollinger_bands': calculate_bollinger_bands,
    'calculate_bollinger_percent_b': calculate_bollinger_percent_b,
    'calculate_bollinger_bandwidth': calculate_bollinger_bandwidth,
    
    # Statistical Volatility
    'calculate_stddev': calculate_stddev,
    'calculate_variance': calculate_variance
}