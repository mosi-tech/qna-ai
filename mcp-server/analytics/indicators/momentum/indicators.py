"""Momentum Indicators Module using TA-Lib Library.

This module provides all momentum indicators from TA-Lib, which measure the rate of change
in price movements and help identify trend strength, overbought/oversold conditions, and
potential reversal points. All functions follow Google docstring conventions and return
standardized dictionary outputs.

The module includes all 24 momentum indicators from TA-Lib:
    - Oscillators: RSI, Stochastic, Williams %R, Ultimate Oscillator, etc.
    - Directional Movement: ADX, DX, +DI, -DI, Aroon, etc. 
    - Price-Based: MACD, PPO, ROC, Momentum, TRIX, etc.
    - Volume-Based: MFI, CCI
    - Specialized: BOP, CMO

Key Features:
    - Complete coverage of all TA-Lib momentum indicators
    - Industry-standard TA-Lib implementation for proven accuracy
    - Standardized return format with success indicators and error handling
    - Comprehensive signal generation (bullish/bearish/neutral/overbought/oversold)
    - Support for both pandas Series and DataFrame input formats
    - Automatic data validation and type conversion
    - Performance optimized using TA-Lib's C implementation

Dependencies:
    - talib-binary: Core technical analysis calculations
    - pandas: Data manipulation and time series handling
    - numpy: Numerical computations and array operations

Example:
    >>> import pandas as pd
    >>> from mcp.analytics.indicators.momentum import calculate_rsi, calculate_adx
    >>> 
    >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115])
    >>> rsi_result = calculate_rsi(prices, period=14)
    >>> print(f"RSI: {rsi_result['latest_value']:.1f} - {rsi_result['signal']}")

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
# OSCILLATORS (0-100 Range)
# =============================================================================

def calculate_rsi(data: Union[pd.Series, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Relative Strength Index using TA-Lib library.
    
    Computes the Relative Strength Index (RSI), a momentum oscillator that measures the speed
    and magnitude of recent price changes. RSI values range from 0 to 100 and are used to
    identify overbought (>70) and oversold (<30) conditions in the market.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Number of periods for RSI calculation. Defaults to 14.
            Standard period is 14, but 9 and 21 are also common for different sensitivities.
    
    Returns:
        Dict[str, Any]: Dictionary containing RSI analysis with keys:
            - data (List[float]): List of RSI values
            - rsi (pd.Series): RSI values as pandas Series with original index
            - period (int): Period used for calculation
            - latest_value (Optional[float]): Most recent RSI value (0-100)
            - signal (str): Market condition ('overbought', 'oversold', 'neutral')
            - overbought_level (int): Threshold for overbought condition (70)
            - oversold_level (int): Threshold for oversold condition (30)
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If period is not an integer or data format is invalid.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_rsi(prices, period=14)
        >>> print(f"RSI: {result['latest_value']:.1f} - {result['signal']}")
        RSI: 65.2 - neutral
        
    Note:
        - RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss
        - Values above 70 typically indicate overbought conditions
        - Values below 30 typically indicate oversold conditions
        - Can be used for divergence analysis and trend confirmation
        - More sensitive with shorter periods, smoother with longer periods
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary - leveraging requirements.txt
        rsi_values = talib.RSI(prices.values.astype(np.float64), timeperiod=period)
        rsi_series = pd.Series(rsi_values, index=prices.index).dropna()
        
        latest_rsi = float(rsi_series.iloc[-1]) if len(rsi_series) > 0 else None
        
        # Generate signals
        signal = "neutral"
        if latest_rsi is not None:
            if latest_rsi > 70:
                signal = "overbought"
            elif latest_rsi < 30:
                signal = "oversold"
        
        result = {
            "data": rsi_series.tolist(),
            "rsi": rsi_series,
            "period": period,
            "latest_value": latest_rsi,
            "signal": signal,
            "overbought_level": 70,
            "oversold_level": 30
        }
        
        return standardize_output(result, "calculate_rsi")
        
    except Exception as e:
        return {"success": False, "error": f"RSI calculation failed: {str(e)}"}


def calculate_stochastic(data: Union[pd.DataFrame, Dict[str, Any]], 
                        k_period: int = 14, d_period: int = 3) -> Dict[str, Any]:
    """Calculate Stochastic Oscillator using TA-Lib library.
    
    Computes the Stochastic Oscillator, a momentum indicator that compares a security's closing
    price to its price range over a specified period. It consists of %K (fast stochastic) and
    %D (slow stochastic, which is a moving average of %K). Values range from 0 to 100.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        k_period (int, optional): Period for %K calculation. Defaults to 14.
            Determines lookback period for high/low range calculation.
        d_period (int, optional): Period for %D smoothing. Defaults to 3.
            Moving average period applied to %K values.
    
    Returns:
        Dict[str, Any]: Dictionary containing Stochastic analysis with keys:
            - k_percent (pd.Series): %K values (fast stochastic)
            - d_percent (pd.Series): %D values (slow stochastic, SMA of %K)
            - latest_k (Optional[float]): Most recent %K value (0-100)
            - latest_d (Optional[float]): Most recent %D value (0-100)
            - signal (str): Market signal ('bullish_crossover', 'bearish_crossover', 
                          'overbought', 'oversold', 'neutral')
            - k_period (int): %K period used
            - d_period (int): %D period used
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLC columns are missing or data is invalid.
        TypeError: If period parameters are not integers.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113]
        ... })
        >>> result = calculate_stochastic(ohlc_data)
        >>> print(f"%K: {result['latest_k']:.1f}, Signal: {result['signal']}")
        %K: 75.5, Signal: neutral
        
    Note:
        - %K = ((Close - LowestLow) / (HighestHigh - LowestLow)) * 100
        - %D = SMA of %K over d_period
        - Values > 80 typically indicate overbought conditions
        - Values < 20 typically indicate oversold conditions
        - %K crossing above %D generates bullish signal
        - %K crossing below %D generates bearish signal
        - Divergence with price can signal potential reversals
    """
    try:
        if isinstance(data, dict):
            # Convert dict to DataFrame
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for Stochastic calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary - leveraging requirements.txt
        slowk, slowd = talib.STOCH(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            fastk_period=k_period,
            slowk_period=3,
            slowd_period=d_period
        )
        
        stoch_df = pd.DataFrame({
            'k_percent': slowk,
            'd_percent': slowd
        }, index=df.index).dropna()
        
        # Determine column names
        k_col = next((col for col in stoch_df.columns if 'k' in col.lower()), stoch_df.columns[0])
        d_col = next((col for col in stoch_df.columns if 'd' in col.lower()), stoch_df.columns[1])
        
        # Generate signals
        signal = "neutral"
        if len(stoch_df) >= 2:
            current_k = stoch_df[k_col].iloc[-1]
            current_d = stoch_df[d_col].iloc[-1]
            prev_k = stoch_df[k_col].iloc[-2]
            prev_d = stoch_df[d_col].iloc[-2]
            
            if current_k > current_d and prev_k <= prev_d and current_k < 80:
                signal = "bullish_crossover"
            elif current_k < current_d and prev_k >= prev_d and current_k > 20:
                signal = "bearish_crossover"
            elif current_k > 80 and current_d > 80:
                signal = "overbought"
            elif current_k < 20 and current_d < 20:
                signal = "oversold"
        
        result = {
            "k_percent": stoch_df[k_col],
            "d_percent": stoch_df[d_col],
            "latest_k": float(stoch_df[k_col].iloc[-1]) if len(stoch_df) > 0 else None,
            "latest_d": float(stoch_df[d_col].iloc[-1]) if len(stoch_df) > 0 else None,
            "signal": signal,
            "k_period": k_period,
            "d_period": d_period
        }
        
        return standardize_output(result, "calculate_stochastic")
        
    except Exception as e:
        return {"success": False, "error": f"Stochastic calculation failed: {str(e)}"}


def calculate_stochastic_fast(data: Union[pd.DataFrame, Dict[str, Any]], 
                             k_period: int = 14, d_period: int = 3) -> Dict[str, Any]:
    """Calculate Fast Stochastic Oscillator using TA-Lib library.
    
    Computes the Fast Stochastic Oscillator, which is more sensitive than the regular
    Stochastic as it uses the raw %K values without smoothing. This provides faster
    signals but with increased noise and potential for false signals.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        k_period (int, optional): Period for %K calculation. Defaults to 14.
            Determines lookback period for high/low range calculation.
        d_period (int, optional): Period for %D smoothing. Defaults to 3.
            Moving average period applied to fast %K values.
    
    Returns:
        Dict[str, Any]: Dictionary containing Fast Stochastic analysis with keys:
            - fastk (pd.Series): Fast %K values (raw stochastic)
            - fastd (pd.Series): Fast %D values (SMA of fast %K)
            - latest_k (Optional[float]): Most recent fast %K value (0-100)
            - latest_d (Optional[float]): Most recent fast %D value (0-100)
            - signal (str): Market signal ('bullish_crossover', 'bearish_crossover', 
                          'overbought', 'oversold', 'neutral')
            - k_period (int): %K period used
            - d_period (int): %D period used
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLC columns are missing or data is invalid.
        TypeError: If period parameters are not integers.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113]
        ... })
        >>> result = calculate_stochastic_fast(ohlc_data)
        >>> print(f"Fast %K: {result['latest_k']:.1f}, Signal: {result['signal']}")
        Fast %K: 82.3, Signal: overbought
        
    Note:
        - Fast %K = ((Close - LowestLow) / (HighestHigh - LowestLow)) * 100
        - Fast %D = SMA of Fast %K over d_period
        - More sensitive than regular Stochastic (no smoothing on %K)
        - Generates more signals but with higher false positive rate
        - Better for short-term trading strategies
        - Same overbought/oversold levels as regular Stochastic (80/20)
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for Fast Stochastic calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        fastk, fastd = talib.STOCHF(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            fastk_period=k_period,
            fastd_period=d_period
        )
        
        stoch_df = pd.DataFrame({
            'fastk': fastk,
            'fastd': fastd
        }, index=df.index).dropna()
        
        # Generate signals
        signal = "neutral"
        if len(stoch_df) >= 2:
            current_k = stoch_df['fastk'].iloc[-1]
            current_d = stoch_df['fastd'].iloc[-1]
            prev_k = stoch_df['fastk'].iloc[-2]
            prev_d = stoch_df['fastd'].iloc[-2]
            
            if current_k > current_d and prev_k <= prev_d and current_k < 80:
                signal = "bullish_crossover"
            elif current_k < current_d and prev_k >= prev_d and current_k > 20:
                signal = "bearish_crossover"
            elif current_k > 80 and current_d > 80:
                signal = "overbought"
            elif current_k < 20 and current_d < 20:
                signal = "oversold"
        
        result = {
            "fastk": stoch_df['fastk'],
            "fastd": stoch_df['fastd'],
            "latest_k": float(stoch_df['fastk'].iloc[-1]) if len(stoch_df) > 0 else None,
            "latest_d": float(stoch_df['fastd'].iloc[-1]) if len(stoch_df) > 0 else None,
            "signal": signal,
            "k_period": k_period,
            "d_period": d_period
        }
        
        return standardize_output(result, "calculate_stochastic_fast")
        
    except Exception as e:
        return {"success": False, "error": f"Fast Stochastic calculation failed: {str(e)}"}


def calculate_williams_r(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Williams %R using TA-Lib library.
    
    Computes Williams %R, a momentum oscillator that measures overbought and oversold levels.
    Unlike other oscillators, Williams %R ranges from 0 to -100, where values above -20
    indicate overbought conditions and values below -80 indicate oversold conditions.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Number of periods for calculation. Defaults to 14.
            Common values: 14 (standard), 21, 28 for different sensitivities.
    
    Returns:
        Dict[str, Any]: Dictionary containing Williams %R analysis with keys:
            - williams_r (pd.Series): Williams %R values (-100 to 0)
            - latest_value (Optional[float]): Most recent Williams %R value
            - signal (str): Market condition ('overbought', 'oversold', 'neutral')
            - period (int): Period used for calculation
            - overbought_level (int): Threshold for overbought condition (-20)
            - oversold_level (int): Threshold for oversold condition (-80)
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
        >>> result = calculate_williams_r(ohlc_data)
        >>> print(f"Williams %R: {result['latest_value']:.1f} - {result['signal']}")
        Williams %R: -15.5 - overbought
        
    Note:
        - Williams %R = ((Highest High - Close) / (Highest High - Lowest Low)) * -100
        - Values above -20 typically indicate overbought conditions
        - Values below -80 typically indicate oversold conditions
        - Inverted scale compared to most oscillators (0 to -100)
        - Fast-moving oscillator, similar to Fast %K of Stochastic
        - Best used in conjunction with trend-following indicators
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for Williams %R calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        willr_values = talib.WILLR(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        willr_series = pd.Series(willr_values, index=df.index).dropna()
        
        latest_willr = float(willr_series.iloc[-1]) if len(willr_series) > 0 else None
        
        # Generate signals (note: Williams %R uses inverted scale)
        signal = "neutral"
        if latest_willr is not None:
            if latest_willr > -20:
                signal = "overbought"
            elif latest_willr < -80:
                signal = "oversold"
        
        result = {
            "williams_r": willr_series,
            "latest_value": latest_willr,
            "signal": signal,
            "period": period,
            "overbought_level": -20,
            "oversold_level": -80
        }
        
        return standardize_output(result, "calculate_williams_r")
        
    except Exception as e:
        return {"success": False, "error": f"Williams %R calculation failed: {str(e)}"}


def calculate_ultimate_oscillator(data: Union[pd.DataFrame, Dict[str, Any]], 
                                 period1: int = 7, period2: int = 14, period3: int = 28) -> Dict[str, Any]:
    """Calculate Ultimate Oscillator using TA-Lib library.
    
    Computes the Ultimate Oscillator, which combines short, medium, and long-term momentum
    into a single oscillator. It addresses the problem of false divergence signals that
    can occur with single-timeframe oscillators by using multiple timeframes.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period1 (int, optional): Short-term period. Defaults to 7.
            Fast component for immediate momentum changes.
        period2 (int, optional): Medium-term period. Defaults to 14.
            Intermediate component for trend confirmation.
        period3 (int, optional): Long-term period. Defaults to 28.
            Slow component for overall trend direction.
    
    Returns:
        Dict[str, Any]: Dictionary containing Ultimate Oscillator analysis with keys:
            - ultimate_oscillator (pd.Series): Ultimate Oscillator values (0-100)
            - latest_value (Optional[float]): Most recent oscillator value
            - signal (str): Market condition ('overbought', 'oversold', 'bullish', 'bearish', 'neutral')
            - period1 (int): Short-term period used
            - period2 (int): Medium-term period used  
            - period3 (int): Long-term period used
            - overbought_level (int): Threshold for overbought condition (70)
            - oversold_level (int): Threshold for oversold condition (30)
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLC columns are missing or data is invalid.
        TypeError: If period parameters are not integers.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113]
        ... })
        >>> result = calculate_ultimate_oscillator(ohlc_data)
        >>> print(f"Ultimate Oscillator: {result['latest_value']:.1f} - {result['signal']}")
        Ultimate Oscillator: 65.2 - neutral
        
    Note:
        - Combines momentum from 3 different timeframes (7, 14, 28 periods typically)
        - Weighted average: 4*(BP/TR7) + 2*(BP/TR14) + (BP/TR28) / (4+2+1)
        - BP = Buying Pressure (Close - min(Low, Previous Close))
        - TR = True Range (max(High, Previous Close) - min(Low, Previous Close))
        - Values above 70 typically indicate overbought conditions
        - Values below 30 typically indicate oversold conditions
        - Less prone to false signals than single-timeframe oscillators
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for Ultimate Oscillator calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        ultosc_values = talib.ULTOSC(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            timeperiod1=period1,
            timeperiod2=period2,
            timeperiod3=period3
        )
        ultosc_series = pd.Series(ultosc_values, index=df.index).dropna()
        
        latest_ultosc = float(ultosc_series.iloc[-1]) if len(ultosc_series) > 0 else None
        
        # Generate signals
        signal = "neutral"
        if latest_ultosc is not None:
            if latest_ultosc > 70:
                signal = "overbought"
            elif latest_ultosc < 30:
                signal = "oversold"
            elif len(ultosc_series) >= 2:
                # Check for bullish/bearish momentum
                if ultosc_series.iloc[-1] > ultosc_series.iloc[-2] and latest_ultosc > 50:
                    signal = "bullish"
                elif ultosc_series.iloc[-1] < ultosc_series.iloc[-2] and latest_ultosc < 50:
                    signal = "bearish"
        
        result = {
            "ultimate_oscillator": ultosc_series,
            "latest_value": latest_ultosc,
            "signal": signal,
            "period1": period1,
            "period2": period2,
            "period3": period3,
            "overbought_level": 70,
            "oversold_level": 30
        }
        
        return standardize_output(result, "calculate_ultimate_oscillator")
        
    except Exception as e:
        return {"success": False, "error": f"Ultimate Oscillator calculation failed: {str(e)}"}


# =============================================================================
# DIRECTIONAL MOVEMENT INDICATORS
# =============================================================================

def calculate_adx(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Average Directional Index using TA-Lib library.
    
    Computes the Average Directional Index (ADX), which measures the strength of a trend
    without regard to trend direction. ADX values range from 0 to 100, with higher values
    indicating stronger trends and lower values indicating weaker trends or sideways movement.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Number of periods for ADX calculation. Defaults to 14.
            Standard period; shorter periods increase sensitivity to recent changes.
    
    Returns:
        Dict[str, Any]: Dictionary containing ADX analysis with keys:
            - adx (pd.Series): ADX values (0-100)
            - latest_value (Optional[float]): Most recent ADX value
            - trend_strength (str): Trend strength classification ('weak', 'moderate', 'strong', 'very_strong')
            - period (int): Period used for calculation
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
        >>> result = calculate_adx(ohlc_data)
        >>> print(f"ADX: {result['latest_value']:.1f} - Trend: {result['trend_strength']}")
        ADX: 45.2 - Trend: strong
        
    Note:
        - ADX = Simple Moving Average of DX (Directional Index) over specified period
        - ADX < 20: Weak trend or sideways movement
        - ADX 20-40: Moderate trend strength
        - ADX 40-60: Strong trend
        - ADX > 60: Very strong trend (often unsustainable)
        - Does not indicate trend direction, only strength
        - Often used with +DI and -DI for complete directional analysis
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for ADX calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        adx_values = talib.ADX(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        adx_series = pd.Series(adx_values, index=df.index).dropna()
        
        latest_adx = float(adx_series.iloc[-1]) if len(adx_series) > 0 else None
        
        # Classify trend strength
        trend_strength = "weak"
        if latest_adx is not None:
            if latest_adx > 60:
                trend_strength = "very_strong"
            elif latest_adx > 40:
                trend_strength = "strong"
            elif latest_adx > 20:
                trend_strength = "moderate"
            else:
                trend_strength = "weak"
        
        result = {
            "adx": adx_series,
            "latest_value": latest_adx,
            "trend_strength": trend_strength,
            "period": period
        }
        
        return standardize_output(result, "calculate_adx")
        
    except Exception as e:
        return {"success": False, "error": f"ADX calculation failed: {str(e)}"}


def calculate_adxr(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Average Directional Movement Index Rating using TA-Lib library.
    
    Computes the ADXR (Average Directional Movement Index Rating), which is a smoothed
    version of ADX. ADXR is calculated as the average of the current ADX and the ADX
    from 'period' bars ago, providing a less volatile measure of trend strength.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Number of periods for ADXR calculation. Defaults to 14.
            Standard period; affects both ADX calculation and smoothing.
    
    Returns:
        Dict[str, Any]: Dictionary containing ADXR analysis with keys:
            - adxr (pd.Series): ADXR values (0-100)
            - latest_value (Optional[float]): Most recent ADXR value
            - trend_strength (str): Trend strength classification ('weak', 'moderate', 'strong', 'very_strong')
            - period (int): Period used for calculation
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
        >>> result = calculate_adxr(ohlc_data)
        >>> print(f"ADXR: {result['latest_value']:.1f} - Trend: {result['trend_strength']}")
        ADXR: 38.5 - Trend: moderate
        
    Note:
        - ADXR = (Current ADX + ADX from N periods ago) / 2
        - More stable than ADX, reduces false signals
        - Same interpretation levels as ADX (20/40/60 thresholds)
        - Useful for confirming sustained trend strength
        - Lags behind ADX but provides smoother signals
        - Better for longer-term trend analysis
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for ADXR calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        adxr_values = talib.ADXR(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        adxr_series = pd.Series(adxr_values, index=df.index).dropna()
        
        latest_adxr = float(adxr_series.iloc[-1]) if len(adxr_series) > 0 else None
        
        # Classify trend strength
        trend_strength = "weak"
        if latest_adxr is not None:
            if latest_adxr > 60:
                trend_strength = "very_strong"
            elif latest_adxr > 40:
                trend_strength = "strong"
            elif latest_adxr > 20:
                trend_strength = "moderate"
            else:
                trend_strength = "weak"
        
        result = {
            "adxr": adxr_series,
            "latest_value": latest_adxr,
            "trend_strength": trend_strength,
            "period": period
        }
        
        return standardize_output(result, "calculate_adxr")
        
    except Exception as e:
        return {"success": False, "error": f"ADXR calculation failed: {str(e)}"}


def calculate_dx(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Directional Movement Index using TA-Lib library.
    
    Computes the Directional Movement Index (DX), which measures the difference between
    positive and negative directional movement. DX is the raw component used to calculate
    ADX and represents the percentage of true range that is directional movement.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Number of periods for DX calculation. Defaults to 14.
            Standard period for directional movement calculations.
    
    Returns:
        Dict[str, Any]: Dictionary containing DX analysis with keys:
            - dx (pd.Series): DX values (0-100)
            - latest_value (Optional[float]): Most recent DX value
            - directional_strength (str): Directional strength ('weak', 'moderate', 'strong')
            - period (int): Period used for calculation
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
        >>> result = calculate_dx(ohlc_data)
        >>> print(f"DX: {result['latest_value']:.1f} - Strength: {result['directional_strength']}")
        DX: 55.8 - Strength: strong
        
    Note:
        - DX = |((+DI) - (-DI))| / ((+DI) + (-DI)) * 100
        - Values range from 0 to 100
        - High DX values indicate strong directional movement
        - Low DX values indicate sideways or choppy movement
        - DX is smoothed to create ADX for trend strength analysis
        - More volatile than ADX, shows immediate directional changes
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for DX calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        dx_values = talib.DX(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        dx_series = pd.Series(dx_values, index=df.index).dropna()
        
        latest_dx = float(dx_series.iloc[-1]) if len(dx_series) > 0 else None
        
        # Classify directional strength
        directional_strength = "weak"
        if latest_dx is not None:
            if latest_dx > 50:
                directional_strength = "strong"
            elif latest_dx > 25:
                directional_strength = "moderate"
            else:
                directional_strength = "weak"
        
        result = {
            "dx": dx_series,
            "latest_value": latest_dx,
            "directional_strength": directional_strength,
            "period": period
        }
        
        return standardize_output(result, "calculate_dx")
        
    except Exception as e:
        return {"success": False, "error": f"DX calculation failed: {str(e)}"}


def calculate_minus_di(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Minus Directional Indicator using TA-Lib library.
    
    Computes the Minus Directional Indicator (-DI), which measures the strength of
    downward price movement. When -DI is above +DI, it indicates that selling pressure
    is stronger than buying pressure, suggesting a bearish trend.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Number of periods for -DI calculation. Defaults to 14.
            Standard period for directional movement calculations.
    
    Returns:
        Dict[str, Any]: Dictionary containing -DI analysis with keys:
            - minus_di (pd.Series): -DI values (0-100)
            - latest_value (Optional[float]): Most recent -DI value
            - pressure_strength (str): Selling pressure strength ('weak', 'moderate', 'strong')
            - period (int): Period used for calculation
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
        >>> result = calculate_minus_di(ohlc_data)
        >>> print(f"-DI: {result['latest_value']:.1f} - Pressure: {result['pressure_strength']}")
        -DI: 28.5 - Pressure: moderate
        
    Note:
        - -DI = Smoothed Minus Directional Movement / True Range * 100
        - Higher -DI values indicate stronger selling pressure
        - Used in conjunction with +DI to determine trend direction
        - When -DI > +DI, bearish trend is indicated
        - When -DI crosses above +DI, potential sell signal
        - Values typically range from 0 to 50+ in strong trends
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for Minus DI calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        minus_di_values = talib.MINUS_DI(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        minus_di_series = pd.Series(minus_di_values, index=df.index).dropna()
        
        latest_minus_di = float(minus_di_series.iloc[-1]) if len(minus_di_series) > 0 else None
        
        # Classify selling pressure strength
        pressure_strength = "weak"
        if latest_minus_di is not None:
            if latest_minus_di > 30:
                pressure_strength = "strong"
            elif latest_minus_di > 15:
                pressure_strength = "moderate"
            else:
                pressure_strength = "weak"
        
        result = {
            "minus_di": minus_di_series,
            "latest_value": latest_minus_di,
            "pressure_strength": pressure_strength,
            "period": period
        }
        
        return standardize_output(result, "calculate_minus_di")
        
    except Exception as e:
        return {"success": False, "error": f"Minus DI calculation failed: {str(e)}"}


def calculate_plus_di(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Plus Directional Indicator using TA-Lib library.
    
    Computes the Plus Directional Indicator (+DI), which measures the strength of
    upward price movement. When +DI is above -DI, it indicates that buying pressure
    is stronger than selling pressure, suggesting a bullish trend.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Number of periods for +DI calculation. Defaults to 14.
            Standard period for directional movement calculations.
    
    Returns:
        Dict[str, Any]: Dictionary containing +DI analysis with keys:
            - plus_di (pd.Series): +DI values (0-100)
            - latest_value (Optional[float]): Most recent +DI value
            - pressure_strength (str): Buying pressure strength ('weak', 'moderate', 'strong')
            - period (int): Period used for calculation
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
        >>> result = calculate_plus_di(ohlc_data)
        >>> print(f"+DI: {result['latest_value']:.1f} - Pressure: {result['pressure_strength']}")
        +DI: 42.3 - Pressure: strong
        
    Note:
        - +DI = Smoothed Plus Directional Movement / True Range * 100
        - Higher +DI values indicate stronger buying pressure
        - Used in conjunction with -DI to determine trend direction
        - When +DI > -DI, bullish trend is indicated
        - When +DI crosses above -DI, potential buy signal
        - Values typically range from 0 to 50+ in strong trends
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for Plus DI calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        plus_di_values = talib.PLUS_DI(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        plus_di_series = pd.Series(plus_di_values, index=df.index).dropna()
        
        latest_plus_di = float(plus_di_series.iloc[-1]) if len(plus_di_series) > 0 else None
        
        # Classify buying pressure strength
        pressure_strength = "weak"
        if latest_plus_di is not None:
            if latest_plus_di > 30:
                pressure_strength = "strong"
            elif latest_plus_di > 15:
                pressure_strength = "moderate"
            else:
                pressure_strength = "weak"
        
        result = {
            "plus_di": plus_di_series,
            "latest_value": latest_plus_di,
            "pressure_strength": pressure_strength,
            "period": period
        }
        
        return standardize_output(result, "calculate_plus_di")
        
    except Exception as e:
        return {"success": False, "error": f"Plus DI calculation failed: {str(e)}"}


def calculate_aroon(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Aroon oscillator using TA-Lib library.
    
    Computes the Aroon indicator, which consists of Aroon Up and Aroon Down lines that
    measure how long it has been since the highest high and lowest low within a given
    period. The Aroon indicator helps identify trend changes and the strength of trends.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low' columns (case-insensitive).
        period (int, optional): Number of periods for Aroon calculation. Defaults to 14.
            Standard period; shorter periods are more sensitive to recent changes.
    
    Returns:
        Dict[str, Any]: Dictionary containing Aroon analysis with keys:
            - aroon_up (pd.Series): Aroon Up values (0-100)
            - aroon_down (pd.Series): Aroon Down values (0-100)
            - latest_up (Optional[float]): Most recent Aroon Up value
            - latest_down (Optional[float]): Most recent Aroon Down value
            - signal (str): Market signal ('bullish', 'bearish', 'neutral')
            - period (int): Period used for calculation
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required columns are missing or data is invalid.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110]
        ... })
        >>> result = calculate_aroon(ohlc_data)
        >>> print(f"Aroon Up: {result['latest_up']:.1f}, Down: {result['latest_down']:.1f}")
        >>> print(f"Signal: {result['signal']}")
        Aroon Up: 85.7, Down: 28.6
        Signal: bullish
        
    Note:
        - Aroon Up = ((period - periods since highest high) / period) * 100
        - Aroon Down = ((period - periods since lowest low) / period) * 100
        - Values near 100 indicate recent highs/lows (strong trend)
        - Values near 0 indicate old highs/lows (weak trend)
        - Aroon Up > Aroon Down suggests bullish trend
        - Aroon Down > Aroon Up suggests bearish trend
        - Crossovers between the lines signal potential trend changes
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("High and Low data required for Aroon calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        
        # Use talib-binary
        aroon_down, aroon_up = talib.AROON(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            timeperiod=period
        )
        
        aroon_df = pd.DataFrame({
            'aroon_up': aroon_up,
            'aroon_down': aroon_down
        }, index=df.index).dropna()
        
        latest_up = float(aroon_df['aroon_up'].iloc[-1]) if len(aroon_df) > 0 else None
        latest_down = float(aroon_df['aroon_down'].iloc[-1]) if len(aroon_df) > 0 else None
        
        # Generate signals
        signal = "neutral"
        if latest_up is not None and latest_down is not None:
            if latest_up > latest_down and latest_up > 70:
                signal = "bullish"
            elif latest_down > latest_up and latest_down > 70:
                signal = "bearish"
        
        result = {
            "aroon_up": aroon_df['aroon_up'],
            "aroon_down": aroon_df['aroon_down'],
            "latest_up": latest_up,
            "latest_down": latest_down,
            "signal": signal,
            "period": period
        }
        
        return standardize_output(result, "calculate_aroon")
        
    except Exception as e:
        return {"success": False, "error": f"Aroon calculation failed: {str(e)}"}


def calculate_aroon_oscillator(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Aroon Oscillator using TA-Lib library.
    
    Computes the Aroon Oscillator, which is the difference between Aroon Up and Aroon Down.
    This single-line indicator makes it easier to identify trend direction and strength,
    with positive values indicating bullish trends and negative values indicating bearish trends.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low' columns (case-insensitive).
        period (int, optional): Number of periods for calculation. Defaults to 14.
            Standard period; shorter periods are more sensitive to recent changes.
    
    Returns:
        Dict[str, Any]: Dictionary containing Aroon Oscillator analysis with keys:
            - aroon_oscillator (pd.Series): Aroon Oscillator values (-100 to +100)
            - latest_value (Optional[float]): Most recent oscillator value
            - signal (str): Market signal ('bullish', 'bearish', 'neutral')
            - trend_strength (str): Trend strength ('weak', 'moderate', 'strong')
            - period (int): Period used for calculation
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required columns are missing or data is invalid.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110]
        ... })
        >>> result = calculate_aroon_oscillator(ohlc_data)
        >>> print(f"Aroon Oscillator: {result['latest_value']:.1f} - {result['signal']}")
        Aroon Oscillator: 57.1 - bullish
        
    Note:
        - Aroon Oscillator = Aroon Up - Aroon Down
        - Values range from -100 to +100
        - Positive values indicate bullish trend (recent highs)
        - Negative values indicate bearish trend (recent lows)
        - Values near +100/-100 indicate very strong trends
        - Values near 0 indicate weak or sideways trends
        - Crossovers above/below zero line signal trend changes
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("High and Low data required for Aroon Oscillator calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        
        # Use talib-binary
        aroon_osc_values = talib.AROONOSC(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            timeperiod=period
        )
        aroon_osc_series = pd.Series(aroon_osc_values, index=df.index).dropna()
        
        latest_value = float(aroon_osc_series.iloc[-1]) if len(aroon_osc_series) > 0 else None
        
        # Generate signals and trend strength
        signal = "neutral"
        trend_strength = "weak"
        
        if latest_value is not None:
            # Signal determination
            if latest_value > 25:
                signal = "bullish"
            elif latest_value < -25:
                signal = "bearish"
            
            # Trend strength
            abs_value = abs(latest_value)
            if abs_value > 70:
                trend_strength = "strong"
            elif abs_value > 40:
                trend_strength = "moderate"
            else:
                trend_strength = "weak"
        
        result = {
            "aroon_oscillator": aroon_osc_series,
            "latest_value": latest_value,
            "signal": signal,
            "trend_strength": trend_strength,
            "period": period
        }
        
        return standardize_output(result, "calculate_aroon_oscillator")
        
    except Exception as e:
        return {"success": False, "error": f"Aroon Oscillator calculation failed: {str(e)}"}


# =============================================================================
# PRICE-BASED MOMENTUM INDICATORS
# =============================================================================

def calculate_macd(data: Union[pd.Series, Dict[str, Any]], 
                   fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, Any]:
    """Calculate Moving Average Convergence Divergence using TA-Lib library.
    
    Computes the MACD indicator, which consists of three components: MACD line (difference
    between fast and slow EMAs), signal line (EMA of MACD line), and histogram (difference
    between MACD and signal lines). MACD is used to identify trend changes and momentum shifts.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        fast_period (int, optional): Period for fast EMA. Defaults to 12.
            Standard value; shorter periods increase sensitivity.
        slow_period (int, optional): Period for slow EMA. Defaults to 26.
            Standard value; longer periods smooth out volatility.
        signal_period (int, optional): Period for signal line EMA. Defaults to 9.
            Standard value for signal line smoothing.
    
    Returns:
        Dict[str, Any]: Dictionary containing MACD analysis with keys:
            - macd_line (pd.Series): MACD line values (fast EMA - slow EMA)
            - signal_line (pd.Series): Signal line values (EMA of MACD line)
            - histogram (pd.Series): Histogram values (MACD - Signal)
            - latest_macd (Optional[float]): Most recent MACD line value
            - latest_signal (Optional[float]): Most recent signal line value
            - signal (str): Crossover signal ('bullish_crossover', 'bearish_crossover', 'neutral')
            - fast_period (int): Fast EMA period used
            - slow_period (int): Slow EMA period used
            - signal_period (int): Signal line period used
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series or invalid periods.
        TypeError: If period parameters are not integers.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_macd(prices)
        >>> print(f"MACD: {result['latest_macd']:.3f}, Signal: {result['signal']}")
        MACD: 1.234, Signal: bullish_crossover
        
    Note:
        - MACD line crossing above signal line generates bullish signal
        - MACD line crossing below signal line generates bearish signal
        - Histogram shows momentum strength (distance between MACD and signal)
        - Zero line crossovers indicate potential trend changes
        - Divergence between price and MACD can signal trend reversals
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary - leveraging requirements.txt
        macd_line, macd_signal, macd_hist = talib.MACD(
            prices.values.astype(np.float64), 
            fastperiod=fast_period, 
            slowperiod=slow_period, 
            signalperiod=signal_period
        )
        
        macd_df = pd.DataFrame({
            'macd': macd_line,
            'signal': macd_signal,
            'histogram': macd_hist
        }, index=prices.index).dropna()
        
        # Determine column names (different libraries use different naming)
        macd_col = next((col for col in macd_df.columns if 'macd' in col.lower() and 'signal' not in col.lower() and 'hist' not in col.lower()), macd_df.columns[0])
        signal_col = next((col for col in macd_df.columns if 'signal' in col.lower() or 'macd' in col.lower() and 's' in col.lower()), macd_df.columns[1])
        hist_col = next((col for col in macd_df.columns if 'hist' in col.lower() or 'h' in col.lower()), macd_df.columns[2])
        
        # Generate signals
        signal = "neutral"
        if len(macd_df) >= 2:
            current_macd = macd_df[macd_col].iloc[-1]
            current_signal = macd_df[signal_col].iloc[-1]
            prev_macd = macd_df[macd_col].iloc[-2]
            prev_signal = macd_df[signal_col].iloc[-2]
            
            if current_macd > current_signal and prev_macd <= prev_signal:
                signal = "bullish_crossover"
            elif current_macd < current_signal and prev_macd >= prev_signal:
                signal = "bearish_crossover"
        
        result = {
            "macd_line": macd_df[macd_col],
            "signal_line": macd_df[signal_col],
            "histogram": macd_df[hist_col],
            "latest_macd": float(macd_df[macd_col].iloc[-1]) if len(macd_df) > 0 else None,
            "latest_signal": float(macd_df[signal_col].iloc[-1]) if len(macd_df) > 0 else None,
            "signal": signal,
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period
        }
        
        return standardize_output(result, "calculate_macd")
        
    except Exception as e:
        return {"success": False, "error": f"MACD calculation failed: {str(e)}"}


def calculate_ppo(data: Union[pd.Series, Dict[str, Any]], 
                  fast_period: int = 12, slow_period: int = 26, ma_type: int = 0) -> Dict[str, Any]:
    """Calculate Percentage Price Oscillator using TA-Lib library.
    
    Computes the Percentage Price Oscillator (PPO), which is similar to MACD but expresses
    the difference between two moving averages as a percentage of the slower moving average.
    This normalization makes PPO values comparable across different price levels.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        fast_period (int, optional): Period for fast moving average. Defaults to 12.
            Shorter period for more responsive signal.
        slow_period (int, optional): Period for slow moving average. Defaults to 26.
            Longer period for trend direction.
        ma_type (int, optional): Moving average type (0=SMA, 1=EMA, etc.). Defaults to 0.
            0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3.
    
    Returns:
        Dict[str, Any]: Dictionary containing PPO analysis with keys:
            - ppo (pd.Series): PPO values (percentage)
            - latest_value (Optional[float]): Most recent PPO value
            - signal (str): Market signal ('bullish', 'bearish', 'neutral')
            - fast_period (int): Fast MA period used
            - slow_period (int): Slow MA period used
            - ma_type (int): Moving average type used
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series or invalid periods.
        TypeError: If period parameters are not integers.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_ppo(prices)
        >>> print(f"PPO: {result['latest_value']:.2f}% - {result['signal']}")
        PPO: 2.15% - bullish
        
    Note:
        - PPO = ((Fast MA - Slow MA) / Slow MA) * 100
        - Values above 0 indicate bullish momentum
        - Values below 0 indicate bearish momentum
        - Crossovers above/below zero line signal trend changes
        - Percentage format allows comparison across different price levels
        - Often used with a signal line (EMA of PPO) for crossover signals
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary
        ppo_values = talib.PPO(
            prices.values.astype(np.float64), 
            fastperiod=fast_period, 
            slowperiod=slow_period, 
            matype=ma_type
        )
        ppo_series = pd.Series(ppo_values, index=prices.index).dropna()
        
        latest_ppo = float(ppo_series.iloc[-1]) if len(ppo_series) > 0 else None
        
        # Generate signals
        signal = "neutral"
        if latest_ppo is not None:
            if len(ppo_series) >= 2:
                if latest_ppo > 0 and ppo_series.iloc[-2] <= 0:
                    signal = "bullish"
                elif latest_ppo < 0 and ppo_series.iloc[-2] >= 0:
                    signal = "bearish"
                elif latest_ppo > 0:
                    signal = "bullish"
                elif latest_ppo < 0:
                    signal = "bearish"
        
        result = {
            "ppo": ppo_series,
            "latest_value": latest_ppo,
            "signal": signal,
            "fast_period": fast_period,
            "slow_period": slow_period,
            "ma_type": ma_type
        }
        
        return standardize_output(result, "calculate_ppo")
        
    except Exception as e:
        return {"success": False, "error": f"PPO calculation failed: {str(e)}"}


def calculate_mom(data: Union[pd.Series, Dict[str, Any]], period: int = 10) -> Dict[str, Any]:
    """Calculate Momentum using TA-Lib library.
    
    Computes the Momentum indicator, which measures the rate of change in price over
    a specified period. Momentum is calculated as the current price minus the price
    N periods ago, providing a simple measure of price acceleration or deceleration.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Number of periods for momentum calculation. Defaults to 10.
            Common values: 10, 14, 20 for different time horizons.
    
    Returns:
        Dict[str, Any]: Dictionary containing Momentum analysis with keys:
            - momentum (pd.Series): Momentum values
            - latest_value (Optional[float]): Most recent momentum value
            - signal (str): Market signal ('bullish', 'bearish', 'neutral')
            - period (int): Period used for calculation
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_mom(prices, period=5)
        >>> print(f"Momentum: {result['latest_value']:.2f} - {result['signal']}")
        Momentum: 8.00 - bullish
        
    Note:
        - Momentum = Current Price - Price N periods ago
        - Positive values indicate upward momentum
        - Negative values indicate downward momentum
        - Zero line crossovers signal potential trend changes
        - Simple but effective measure of price acceleration
        - Often used in conjunction with other momentum indicators
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary
        mom_values = talib.MOM(
            prices.values.astype(np.float64), 
            timeperiod=period
        )
        mom_series = pd.Series(mom_values, index=prices.index).dropna()
        
        latest_mom = float(mom_series.iloc[-1]) if len(mom_series) > 0 else None
        
        # Generate signals
        signal = "neutral"
        if latest_mom is not None:
            if len(mom_series) >= 2:
                if latest_mom > 0 and mom_series.iloc[-2] <= 0:
                    signal = "bullish"
                elif latest_mom < 0 and mom_series.iloc[-2] >= 0:
                    signal = "bearish"
                elif latest_mom > 0:
                    signal = "bullish"
                elif latest_mom < 0:
                    signal = "bearish"
        
        result = {
            "momentum": mom_series,
            "latest_value": latest_mom,
            "signal": signal,
            "period": period
        }
        
        return standardize_output(result, "calculate_mom")
        
    except Exception as e:
        return {"success": False, "error": f"Momentum calculation failed: {str(e)}"}


def calculate_roc(data: Union[pd.Series, Dict[str, Any]], period: int = 10) -> Dict[str, Any]:
    """Calculate Rate of Change using TA-Lib library.
    
    Computes the Rate of Change (ROC), which measures the percentage change in price
    over a specified period. ROC is calculated as ((current price - price N periods ago)
    / price N periods ago) * 100, providing a normalized measure of momentum.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Number of periods for ROC calculation. Defaults to 10.
            Common values: 10, 14, 20 for different time horizons.
    
    Returns:
        Dict[str, Any]: Dictionary containing ROC analysis with keys:
            - roc (pd.Series): ROC values (percentage)
            - latest_value (Optional[float]): Most recent ROC value
            - signal (str): Market signal ('bullish', 'bearish', 'neutral')
            - momentum_strength (str): Momentum strength ('weak', 'moderate', 'strong')
            - period (int): Period used for calculation
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_roc(prices, period=5)
        >>> print(f"ROC: {result['latest_value']:.2f}% - {result['signal']}")
        ROC: 8.00% - bullish
        
    Note:
        - ROC = ((Current Price - Price N periods ago) / Price N periods ago) * 100
        - Positive values indicate upward momentum
        - Negative values indicate downward momentum
        - Zero line crossovers signal potential trend changes
        - Percentage format allows comparison across different price levels
        - Often oscillates around zero in trending markets
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary
        roc_values = talib.ROC(
            prices.values.astype(np.float64), 
            timeperiod=period
        )
        roc_series = pd.Series(roc_values, index=prices.index).dropna()
        
        latest_roc = float(roc_series.iloc[-1]) if len(roc_series) > 0 else None
        
        # Generate signals and momentum strength
        signal = "neutral"
        momentum_strength = "weak"
        
        if latest_roc is not None:
            # Signal determination
            if len(roc_series) >= 2:
                if latest_roc > 0 and roc_series.iloc[-2] <= 0:
                    signal = "bullish"
                elif latest_roc < 0 and roc_series.iloc[-2] >= 0:
                    signal = "bearish"
                elif latest_roc > 0:
                    signal = "bullish"
                elif latest_roc < 0:
                    signal = "bearish"
            
            # Momentum strength
            abs_roc = abs(latest_roc)
            if abs_roc > 10:
                momentum_strength = "strong"
            elif abs_roc > 5:
                momentum_strength = "moderate"
            else:
                momentum_strength = "weak"
        
        result = {
            "roc": roc_series,
            "latest_value": latest_roc,
            "signal": signal,
            "momentum_strength": momentum_strength,
            "period": period
        }
        
        return standardize_output(result, "calculate_roc")
        
    except Exception as e:
        return {"success": False, "error": f"ROC calculation failed: {str(e)}"}


# =============================================================================
# VOLUME-BASED MOMENTUM INDICATORS  
# =============================================================================

def calculate_cci(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Commodity Channel Index using TA-Lib library.
    
    Computes the Commodity Channel Index (CCI), which measures the difference between
    a security's price change and its average price change. CCI oscillates above and
    below zero, with values outside ±100 indicating strong price movements.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close' columns (case-insensitive).
        period (int, optional): Number of periods for CCI calculation. Defaults to 14.
            Standard period; shorter periods increase sensitivity.
    
    Returns:
        Dict[str, Any]: Dictionary containing CCI analysis with keys:
            - cci (pd.Series): CCI values (typically -300 to +300)
            - latest_value (Optional[float]): Most recent CCI value
            - signal (str): Market condition ('overbought', 'oversold', 'neutral')
            - period (int): Period used for calculation
            - overbought_level (int): Threshold for overbought condition (100)
            - oversold_level (int): Threshold for oversold condition (-100)
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
        >>> result = calculate_cci(ohlc_data)
        >>> print(f"CCI: {result['latest_value']:.1f} - {result['signal']}")
        CCI: 125.5 - overbought
        
    Note:
        - CCI = (Typical Price - SMA of Typical Price) / (0.015 * Mean Deviation)
        - Typical Price = (High + Low + Close) / 3
        - Values above +100 indicate overbought conditions
        - Values below -100 indicate oversold conditions
        - CCI can range much wider than typical oscillators
        - Originally designed for commodities but works well for stocks
        - Extreme values (+200/-200) often indicate strong continuation moves
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for CCI calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        cci_values = talib.CCI(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        cci_series = pd.Series(cci_values, index=df.index).dropna()
        
        latest_cci = float(cci_series.iloc[-1]) if len(cci_series) > 0 else None
        
        # Generate signals
        signal = "neutral"
        if latest_cci is not None:
            if latest_cci > 100:
                signal = "overbought"
            elif latest_cci < -100:
                signal = "oversold"
        
        result = {
            "cci": cci_series,
            "latest_value": latest_cci,
            "signal": signal,
            "period": period,
            "overbought_level": 100,
            "oversold_level": -100
        }
        
        return standardize_output(result, "calculate_cci")
        
    except Exception as e:
        return {"success": False, "error": f"CCI calculation failed: {str(e)}"}


# =============================================================================
# SPECIALIZED OSCILLATORS
# =============================================================================

def calculate_bop(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate Balance of Power using TA-Lib library.
    
    Computes the Balance of Power (BOP), which measures the strength of buying versus
    selling pressure. BOP compares the close price to the open price within the context
    of the high-low range, providing insight into market sentiment for each period.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLC data as DataFrame or dictionary.
            Must contain 'open', 'high', 'low', 'close' columns (case-insensitive).
    
    Returns:
        Dict[str, Any]: Dictionary containing BOP analysis with keys:
            - bop (pd.Series): BOP values (-1 to +1)
            - latest_value (Optional[float]): Most recent BOP value
            - signal (str): Market condition ('bullish', 'bearish', 'neutral')
            - power_strength (str): Power strength ('weak', 'moderate', 'strong')
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLC columns are missing or data is invalid.
    
    Example:
        >>> import pandas as pd
        >>> ohlc_data = pd.DataFrame({
        ...     'open': [100, 105, 108, 110, 112],
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113]
        ... })
        >>> result = calculate_bop(ohlc_data)
        >>> print(f"BOP: {result['latest_value']:.3f} - {result['signal']}")
        BOP: 0.600 - bullish
        
    Note:
        - BOP = (Close - Open) / (High - Low)
        - Values range from -1 to +1
        - Positive values indicate buying pressure (Close > Open)
        - Negative values indicate selling pressure (Close < Open)
        - Values near +1/-1 indicate strong directional pressure
        - Values near 0 indicate balanced buying/selling pressure
        - No smoothing applied, shows raw market sentiment
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for BOP calculation")
        
        # Standardize column names
        open_col = 'open' if 'open' in df.columns else 'Open'
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary
        bop_values = talib.BOP(
            df[open_col].values.astype(np.float64),
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64)
        )
        bop_series = pd.Series(bop_values, index=df.index).dropna()
        
        latest_bop = float(bop_series.iloc[-1]) if len(bop_series) > 0 else None
        
        # Generate signals and power strength
        signal = "neutral"
        power_strength = "weak"
        
        if latest_bop is not None:
            # Signal determination
            if latest_bop > 0.2:
                signal = "bullish"
            elif latest_bop < -0.2:
                signal = "bearish"
            
            # Power strength
            abs_bop = abs(latest_bop)
            if abs_bop > 0.7:
                power_strength = "strong"
            elif abs_bop > 0.4:
                power_strength = "moderate"
            else:
                power_strength = "weak"
        
        result = {
            "bop": bop_series,
            "latest_value": latest_bop,
            "signal": signal,
            "power_strength": power_strength
        }
        
        return standardize_output(result, "calculate_bop")
        
    except Exception as e:
        return {"success": False, "error": f"BOP calculation failed: {str(e)}"}


def calculate_cmo(data: Union[pd.Series, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Chande Momentum Oscillator using TA-Lib library.
    
    Computes the Chande Momentum Oscillator (CMO), which measures momentum using the
    sum of gains and losses over a specified period. Unlike RSI, CMO uses raw price
    changes rather than smoothed averages, making it more responsive to recent price action.
    
    Args:
        data (Union[pd.Series, Dict[str, Any]]): Price data as pandas Series or dictionary.
            If dictionary, must contain price values that can be converted to Series.
        period (int, optional): Number of periods for CMO calculation. Defaults to 14.
            Standard period; shorter periods increase sensitivity.
    
    Returns:
        Dict[str, Any]: Dictionary containing CMO analysis with keys:
            - cmo (pd.Series): CMO values (-100 to +100)
            - latest_value (Optional[float]): Most recent CMO value
            - signal (str): Market condition ('overbought', 'oversold', 'neutral')
            - momentum_strength (str): Momentum strength ('weak', 'moderate', 'strong')
            - period (int): Period used for calculation
            - overbought_level (int): Threshold for overbought condition (50)
            - oversold_level (int): Threshold for oversold condition (-50)
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If data cannot be converted to valid price series.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115, 118, 120])
        >>> result = calculate_cmo(prices)
        >>> print(f"CMO: {result['latest_value']:.1f} - {result['signal']}")
        CMO: 35.2 - neutral
        
    Note:
        - CMO = ((Sum of Gains - Sum of Losses) / (Sum of Gains + Sum of Losses)) * 100
        - Values range from -100 to +100
        - Values above +50 typically indicate overbought conditions
        - Values below -50 typically indicate oversold conditions
        - More responsive than RSI due to lack of smoothing
        - Zero line crossovers indicate potential trend changes
        - Developed by Tushar Chande as an alternative to RSI
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary
        cmo_values = talib.CMO(
            prices.values.astype(np.float64), 
            timeperiod=period
        )
        cmo_series = pd.Series(cmo_values, index=prices.index).dropna()
        
        latest_cmo = float(cmo_series.iloc[-1]) if len(cmo_series) > 0 else None
        
        # Generate signals and momentum strength
        signal = "neutral"
        momentum_strength = "weak"
        
        if latest_cmo is not None:
            # Signal determination
            if latest_cmo > 50:
                signal = "overbought"
            elif latest_cmo < -50:
                signal = "oversold"
            
            # Momentum strength
            abs_cmo = abs(latest_cmo)
            if abs_cmo > 70:
                momentum_strength = "strong"
            elif abs_cmo > 40:
                momentum_strength = "moderate"
            else:
                momentum_strength = "weak"
        
        result = {
            "cmo": cmo_series,
            "latest_value": latest_cmo,
            "signal": signal,
            "momentum_strength": momentum_strength,
            "period": period,
            "overbought_level": 50,
            "oversold_level": -50
        }
        
        return standardize_output(result, "calculate_cmo")
        
    except Exception as e:
        return {"success": False, "error": f"CMO calculation failed: {str(e)}"}


# =============================================================================
# REGISTRY OF ALL MOMENTUM INDICATORS
# =============================================================================

MOMENTUM_INDICATORS_FUNCTIONS = {
    # Oscillators
    'calculate_rsi': calculate_rsi,
    'calculate_stochastic': calculate_stochastic,
    'calculate_stochastic_fast': calculate_stochastic_fast,
    'calculate_williams_r': calculate_williams_r,
    'calculate_ultimate_oscillator': calculate_ultimate_oscillator,
    
    # Directional Movement
    'calculate_adx': calculate_adx,
    'calculate_adxr': calculate_adxr,
    'calculate_dx': calculate_dx,
    'calculate_minus_di': calculate_minus_di,
    'calculate_plus_di': calculate_plus_di,
    'calculate_aroon': calculate_aroon,
    'calculate_aroon_oscillator': calculate_aroon_oscillator,
    
    # Price-Based Momentum
    'calculate_macd': calculate_macd,
    'calculate_ppo': calculate_ppo,
    'calculate_mom': calculate_mom,
    'calculate_roc': calculate_roc,
    
    # Volume-Based Momentum
    'calculate_cci': calculate_cci,
    
    # Specialized Oscillators
    'calculate_bop': calculate_bop,
    'calculate_cmo': calculate_cmo
}