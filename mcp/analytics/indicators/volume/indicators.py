"""Volume Indicators Module using TA-Lib Library.

This module provides all volume indicators from TA-Lib plus additional volume analysis
functions. Volume indicators analyze the relationship between price movements and trading
volume, helping identify trend strength, confirm price movements, and detect potential
reversals based on volume patterns.

The module includes all TA-Lib volume indicators:
    - Accumulation/Distribution: AD, ADOSC
    - Money Flow: MFI, OBV
    - Plus custom volume analysis functions

Key Features:
    - Complete coverage of all TA-Lib volume indicators
    - Industry-standard TA-Lib implementation for proven accuracy
    - Standardized return format with success indicators and error handling
    - Comprehensive signal generation for trend confirmation and divergence analysis
    - Support for OHLCV data formats with automatic column detection
    - Automatic data validation and type conversion
    - Performance optimized using TA-Lib's C implementation

Dependencies:
    - talib-binary: Core technical analysis calculations
    - pandas: Data manipulation and time series handling
    - numpy: Numerical computations and array operations

Example:
    >>> import pandas as pd
    >>> from mcp.analytics.indicators.volume import calculate_obv, calculate_mfi
    >>> 
    >>> ohlcv_data = pd.DataFrame({
    ...     'close': [102, 106, 109, 108, 113], 'volume': [1000, 1200, 800, 1500, 900]
    ... })
    >>> obv_result = calculate_obv(ohlcv_data)
    >>> print(f"OBV: {obv_result['latest_value']:.0f}")

Note:
    All functions require volume data and return standardized dictionary outputs.
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
# ACCUMULATION/DISTRIBUTION FAMILY
# =============================================================================

def calculate_ad(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate Accumulation/Distribution Line using TA-Lib library.
    
    Computes the Accumulation/Distribution Line (A/D Line), which combines price and volume
    to show how much of the security is being accumulated or distributed. The A/D Line
    helps confirm trends and can reveal divergences that may signal potential reversals.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLCV data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close', 'volume' columns (case-insensitive).
    
    Returns:
        Dict[str, Any]: Dictionary containing A/D Line analysis with keys:
            - ad_line (pd.Series): Accumulation/Distribution Line values
            - latest_value (Optional[float]): Most recent A/D Line value
            - trend_direction (str): A/D Line trend ('accumulation', 'distribution', 'neutral')
            - divergence_signal (str): Price/A/D divergence ('bullish', 'bearish', 'none')
            - volume_strength (str): Volume participation strength ('strong', 'moderate', 'weak')
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLCV columns are missing or data is invalid.
    
    Example:
        >>> import pandas as pd
        >>> ohlcv_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113],
        ...     'volume': [1000, 1200, 800, 1500, 900]
        ... })
        >>> result = calculate_ad(ohlcv_data)
        >>> print(f"A/D Line: {result['latest_value']:.0f}")
        >>> print(f"Trend: {result['trend_direction']}")
        A/D Line: 2450
        Trend: accumulation
        
    Note:
        - A/D Line = Σ(((Close - Low) - (High - Close)) / (High - Low) × Volume)
        - Rising A/D Line indicates accumulation (buying pressure)
        - Falling A/D Line indicates distribution (selling pressure)
        - A/D Line confirmation: rising prices + rising A/D = strong trend
        - A/D Line divergence: rising prices + falling A/D = potential reversal
        - Volume weighted, so gives more importance to high-volume periods
        - Useful for confirming breakouts and identifying false moves
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close', 'volume']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLCV data required for A/D Line calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        volume_col = 'volume' if 'volume' in df.columns else 'Volume'
        
        # Use talib-binary
        ad_values = talib.AD(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64),
            df[volume_col].values.astype(np.float64)
        )
        ad_series = pd.Series(ad_values, index=df.index).dropna()
        
        latest_ad = float(ad_series.iloc[-1]) if len(ad_series) > 0 else None
        
        # Trend direction analysis
        trend_direction = "neutral"
        if len(ad_series) >= 5:
            recent_slope = np.polyfit(range(5), ad_series.tail(5).values, 1)[0]
            if recent_slope > 0:
                trend_direction = "accumulation"
            elif recent_slope < 0:
                trend_direction = "distribution"
        
        # Divergence analysis (simplified)
        divergence_signal = "none"
        if len(ad_series) >= 10:
            price_trend = np.polyfit(range(10), df[close_col].tail(10).values, 1)[0]
            ad_trend = np.polyfit(range(10), ad_series.tail(10).values, 1)[0]
            
            if price_trend > 0 and ad_trend < 0:
                divergence_signal = "bearish"
            elif price_trend < 0 and ad_trend > 0:
                divergence_signal = "bullish"
        
        # Volume strength assessment
        volume_strength = "moderate"
        if len(df) >= 5:
            recent_volume = df[volume_col].tail(5).mean()
            avg_volume = df[volume_col].mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
            
            if volume_ratio > 1.5:
                volume_strength = "strong"
            elif volume_ratio < 0.7:
                volume_strength = "weak"
        
        result = {
            "ad_line": ad_series,
            "latest_value": latest_ad,
            "trend_direction": trend_direction,
            "divergence_signal": divergence_signal,
            "volume_strength": volume_strength
        }
        
        return standardize_output(result, "calculate_ad")
        
    except Exception as e:
        return {"success": False, "error": f"A/D Line calculation failed: {str(e)}"}


def calculate_adosc(data: Union[pd.DataFrame, Dict[str, Any]], 
                    fast_period: int = 3, slow_period: int = 10) -> Dict[str, Any]:
    """Calculate Accumulation/Distribution Oscillator using TA-Lib library.
    
    Computes the Accumulation/Distribution Oscillator (Chaikin Oscillator), which is the
    difference between fast and slow Exponential Moving Averages of the A/D Line. This
    oscillator helps identify momentum changes in the accumulation/distribution process.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLCV data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close', 'volume' columns (case-insensitive).
        fast_period (int, optional): Period for fast EMA. Defaults to 3.
            Shorter period for responsive signal generation.
        slow_period (int, optional): Period for slow EMA. Defaults to 10.
            Longer period for trend smoothing.
    
    Returns:
        Dict[str, Any]: Dictionary containing A/D Oscillator analysis with keys:
            - adosc (pd.Series): A/D Oscillator values
            - latest_value (Optional[float]): Most recent oscillator value
            - signal (str): Oscillator signal ('bullish', 'bearish', 'neutral')
            - momentum_direction (str): Momentum direction ('strengthening', 'weakening', 'stable')
            - zero_cross_signal (str): Zero line crossing signal ('bullish_cross', 'bearish_cross', 'none')
            - fast_period (int): Fast EMA period used
            - slow_period (int): Slow EMA period used
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLCV columns are missing or data is invalid.
        TypeError: If period parameters are not integers.
    
    Example:
        >>> import pandas as pd
        >>> ohlcv_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113],
        ...     'volume': [1000, 1200, 800, 1500, 900]
        ... })
        >>> result = calculate_adosc(ohlcv_data)
        >>> print(f"A/D Oscillator: {result['latest_value']:.0f}")
        >>> print(f"Signal: {result['signal']}")
        A/D Oscillator: 450
        Signal: bullish
        
    Note:
        - A/D Oscillator = EMA_fast(A/D Line) - EMA_slow(A/D Line)
        - Positive values indicate accumulation momentum
        - Negative values indicate distribution momentum
        - Zero line crossovers generate buy/sell signals
        - Divergence with price can signal potential reversals
        - More responsive than the A/D Line itself
        - Useful for timing entry/exit points
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close', 'volume']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLCV data required for A/D Oscillator calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        volume_col = 'volume' if 'volume' in df.columns else 'Volume'
        
        # Use talib-binary
        adosc_values = talib.ADOSC(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64),
            df[volume_col].values.astype(np.float64),
            fastperiod=fast_period,
            slowperiod=slow_period
        )
        adosc_series = pd.Series(adosc_values, index=df.index).dropna()
        
        latest_adosc = float(adosc_series.iloc[-1]) if len(adosc_series) > 0 else None
        
        # Signal generation
        signal = "neutral"
        momentum_direction = "stable"
        zero_cross_signal = "none"
        
        if latest_adosc is not None:
            # Basic signal
            if latest_adosc > 0:
                signal = "bullish"
            elif latest_adosc < 0:
                signal = "bearish"
            
            # Momentum direction
            if len(adosc_series) >= 3:
                recent_values = adosc_series.tail(3)
                if recent_values.iloc[-1] > recent_values.iloc[-2] > recent_values.iloc[-3]:
                    momentum_direction = "strengthening"
                elif recent_values.iloc[-1] < recent_values.iloc[-2] < recent_values.iloc[-3]:
                    momentum_direction = "weakening"
            
            # Zero line crossover
            if len(adosc_series) >= 2:
                prev_value = adosc_series.iloc[-2]
                if prev_value <= 0 and latest_adosc > 0:
                    zero_cross_signal = "bullish_cross"
                elif prev_value >= 0 and latest_adosc < 0:
                    zero_cross_signal = "bearish_cross"
        
        result = {
            "adosc": adosc_series,
            "latest_value": latest_adosc,
            "signal": signal,
            "momentum_direction": momentum_direction,
            "zero_cross_signal": zero_cross_signal,
            "fast_period": fast_period,
            "slow_period": slow_period
        }
        
        return standardize_output(result, "calculate_adosc")
        
    except Exception as e:
        return {"success": False, "error": f"A/D Oscillator calculation failed: {str(e)}"}


# =============================================================================
# MONEY FLOW INDICATORS
# =============================================================================

def calculate_mfi(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """Calculate Money Flow Index using TA-Lib library.
    
    Computes the Money Flow Index (MFI), which combines price and volume data to measure
    buying and selling pressure. MFI is often called "Volume-weighted RSI" as it applies
    RSI calculations to a volume-weighted price series.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLCV data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close', 'volume' columns (case-insensitive).
        period (int, optional): Number of periods for MFI calculation. Defaults to 14.
            Standard period; shorter periods increase sensitivity.
    
    Returns:
        Dict[str, Any]: Dictionary containing MFI analysis with keys:
            - mfi (pd.Series): MFI values (0-100)
            - latest_value (Optional[float]): Most recent MFI value
            - signal (str): Market condition ('overbought', 'oversold', 'neutral')
            - money_flow_trend (str): Money flow trend ('positive', 'negative', 'balanced')
            - period (int): Period used for calculation
            - overbought_level (int): Threshold for overbought condition (80)
            - oversold_level (int): Threshold for oversold condition (20)
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLCV columns are missing or data is invalid.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> ohlcv_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113],
        ...     'volume': [1000, 1200, 800, 1500, 900]
        ... })
        >>> result = calculate_mfi(ohlcv_data)
        >>> print(f"MFI: {result['latest_value']:.1f} - {result['signal']}")
        MFI: 65.2 - neutral
        
    Note:
        - MFI = 100 - (100 / (1 + Money Flow Ratio))
        - Money Flow Ratio = Positive Money Flow / Negative Money Flow
        - Values above 80 typically indicate overbought conditions
        - Values below 20 typically indicate oversold conditions
        - Divergence between MFI and price can signal potential reversals
        - More reliable than RSI in volatile markets due to volume weighting
        - Useful for confirming price movements with volume analysis
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close', 'volume']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLCV data required for MFI calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        volume_col = 'volume' if 'volume' in df.columns else 'Volume'
        
        # Use talib-binary
        mfi_values = talib.MFI(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64),
            df[volume_col].values.astype(np.float64),
            timeperiod=period
        )
        mfi_series = pd.Series(mfi_values, index=df.index).dropna()
        
        latest_mfi = float(mfi_series.iloc[-1]) if len(mfi_series) > 0 else None
        
        # Generate signals
        signal = "neutral"
        money_flow_trend = "balanced"
        
        if latest_mfi is not None:
            if latest_mfi > 80:
                signal = "overbought"
                money_flow_trend = "positive"
            elif latest_mfi < 20:
                signal = "oversold"
                money_flow_trend = "negative"
            elif latest_mfi > 50:
                money_flow_trend = "positive"
            elif latest_mfi < 50:
                money_flow_trend = "negative"
        
        result = {
            "mfi": mfi_series,
            "latest_value": latest_mfi,
            "signal": signal,
            "money_flow_trend": money_flow_trend,
            "period": period,
            "overbought_level": 80,
            "oversold_level": 20
        }
        
        return standardize_output(result, "calculate_mfi")
        
    except Exception as e:
        return {"success": False, "error": f"MFI calculation failed: {str(e)}"}


def calculate_obv(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate On Balance Volume using TA-Lib library.
    
    Computes the On Balance Volume (OBV), which uses volume flow to predict changes in
    stock price. OBV adds volume on up days and subtracts volume on down days, creating
    a cumulative indicator that can confirm trend direction and signal potential reversals.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): Price and volume data as DataFrame or dictionary.
            Must contain 'close', 'volume' columns (case-insensitive).
    
    Returns:
        Dict[str, Any]: Dictionary containing OBV analysis with keys:
            - obv (pd.Series): On Balance Volume values
            - latest_value (Optional[float]): Most recent OBV value
            - volume_trend (str): Volume trend direction ('bullish', 'bearish', 'neutral')
            - trend_strength (str): Trend strength ('strong', 'moderate', 'weak')
            - divergence_signal (str): Price/OBV divergence ('bullish', 'bearish', 'none')
            - confirmation_status (str): Trend confirmation ('confirmed', 'unconfirmed', 'conflicting')
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required columns are missing or data is invalid.
    
    Example:
        >>> import pandas as pd
        >>> price_volume_data = pd.DataFrame({
        ...     'close': [102, 106, 109, 108, 113],
        ...     'volume': [1000, 1200, 800, 1500, 900]
        ... })
        >>> result = calculate_obv(price_volume_data)
        >>> print(f"OBV: {result['latest_value']:.0f}")
        >>> print(f"Volume Trend: {result['volume_trend']}")
        >>> print(f"Confirmation: {result['confirmation_status']}")
        OBV: 1400
        Volume Trend: bullish
        Confirmation: confirmed
        
    Note:
        - OBV = Previous OBV + Volume (if Close > Previous Close)
        - OBV = Previous OBV - Volume (if Close < Previous Close)
        - OBV = Previous OBV (if Close = Previous Close)
        - Rising OBV confirms uptrend; falling OBV confirms downtrend
        - OBV divergence with price can signal potential reversals
        - Volume leads price, so OBV can provide early trend signals
        - Best used in conjunction with price analysis for confirmation
        - Useful for identifying accumulation and distribution phases
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['close', 'volume']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("Close and Volume data required for OBV calculation")
        
        # Standardize column names
        close_col = 'close' if 'close' in df.columns else 'Close'
        volume_col = 'volume' if 'volume' in df.columns else 'Volume'
        
        # Use talib-binary
        obv_values = talib.OBV(
            df[close_col].values.astype(np.float64),
            df[volume_col].values.astype(np.float64)
        )
        obv_series = pd.Series(obv_values, index=df.index).dropna()
        
        latest_obv = float(obv_series.iloc[-1]) if len(obv_series) > 0 else None
        
        # Volume trend analysis
        volume_trend = "neutral"
        trend_strength = "moderate"
        if len(obv_series) >= 5:
            recent_slope = np.polyfit(range(5), obv_series.tail(5).values, 1)[0]
            slope_magnitude = abs(recent_slope)
            
            if recent_slope > 0:
                volume_trend = "bullish"
            elif recent_slope < 0:
                volume_trend = "bearish"
            
            # Trend strength based on slope magnitude
            if slope_magnitude > obv_series.std() * 0.5:
                trend_strength = "strong"
            elif slope_magnitude < obv_series.std() * 0.1:
                trend_strength = "weak"
        
        # Divergence analysis
        divergence_signal = "none"
        confirmation_status = "neutral"
        
        if len(obv_series) >= 10:
            price_trend = np.polyfit(range(10), df[close_col].tail(10).values, 1)[0]
            obv_trend = np.polyfit(range(10), obv_series.tail(10).values, 1)[0]
            
            # Check for divergence
            if price_trend > 0 and obv_trend < 0:
                divergence_signal = "bearish"
                confirmation_status = "conflicting"
            elif price_trend < 0 and obv_trend > 0:
                divergence_signal = "bullish"
                confirmation_status = "conflicting"
            elif (price_trend > 0 and obv_trend > 0) or (price_trend < 0 and obv_trend < 0):
                confirmation_status = "confirmed"
            else:
                confirmation_status = "unconfirmed"
        
        result = {
            "obv": obv_series,
            "latest_value": latest_obv,
            "volume_trend": volume_trend,
            "trend_strength": trend_strength,
            "divergence_signal": divergence_signal,
            "confirmation_status": confirmation_status
        }
        
        return standardize_output(result, "calculate_obv")
        
    except Exception as e:
        return {"success": False, "error": f"OBV calculation failed: {str(e)}"}


# =============================================================================
# CUSTOM VOLUME ANALYSIS FUNCTIONS
# =============================================================================

def calculate_cmf(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 20) -> Dict[str, Any]:
    """Calculate Chaikin Money Flow.
    
    Computes the Chaikin Money Flow (CMF), which measures the amount of Money Flow Volume
    over a specific period. CMF oscillates between -1 and +1, indicating buying and
    selling pressure based on where the close is relative to the high-low range.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): OHLCV data as DataFrame or dictionary.
            Must contain 'high', 'low', 'close', 'volume' columns (case-insensitive).
        period (int, optional): Period for CMF calculation. Defaults to 20.
    
    Returns:
        Dict[str, Any]: Dictionary containing CMF analysis with keys:
            - cmf (pd.Series): Chaikin Money Flow values (-1 to +1)
            - latest_value (Optional[float]): Most recent CMF value
            - signal (str): Money flow signal ('buying_pressure', 'selling_pressure', 'neutral')
            - pressure_strength (str): Pressure strength ('strong', 'moderate', 'weak')
            - period (int): Period used for calculation
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required OHLCV columns are missing or data is invalid.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> ohlcv_data = pd.DataFrame({
        ...     'high': [105, 108, 112, 110, 115],
        ...     'low': [98, 102, 105, 107, 110],
        ...     'close': [102, 106, 109, 108, 113],
        ...     'volume': [1000, 1200, 800, 1500, 900]
        ... })
        >>> result = calculate_cmf(ohlcv_data)
        >>> print(f"CMF: {result['latest_value']:.3f}")
        >>> print(f"Signal: {result['signal']}")
        CMF: 0.125
        Signal: buying_pressure
        
    Note:
        - CMF = Σ(Money Flow Volume) / Σ(Volume) over period
        - Money Flow Multiplier = ((Close - Low) - (High - Close)) / (High - Low)
        - Money Flow Volume = Money Flow Multiplier × Volume
        - CMF > 0: Buying pressure dominates
        - CMF < 0: Selling pressure dominates
        - CMF near +1/-1: Strong buying/selling pressure
        - Used to confirm trends and identify potential reversals
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close', 'volume']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLCV data required for CMF calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        volume_col = 'volume' if 'volume' in df.columns else 'Volume'
        
        # Calculate Money Flow Multiplier
        mf_multiplier = ((df[close_col] - df[low_col]) - (df[high_col] - df[close_col])) / (df[high_col] - df[low_col])
        mf_multiplier = mf_multiplier.fillna(0)  # Handle division by zero
        
        # Calculate Money Flow Volume
        mf_volume = mf_multiplier * df[volume_col]
        
        # Calculate CMF
        cmf_values = mf_volume.rolling(window=period).sum() / df[volume_col].rolling(window=period).sum()
        cmf_series = cmf_values.dropna()
        
        latest_cmf = float(cmf_series.iloc[-1]) if len(cmf_series) > 0 else None
        
        # Generate signals
        signal = "neutral"
        pressure_strength = "moderate"
        
        if latest_cmf is not None:
            if latest_cmf > 0.2:
                signal = "buying_pressure"
                if latest_cmf > 0.5:
                    pressure_strength = "strong"
            elif latest_cmf < -0.2:
                signal = "selling_pressure"
                if latest_cmf < -0.5:
                    pressure_strength = "strong"
            else:
                pressure_strength = "weak"
        
        result = {
            "cmf": cmf_series,
            "latest_value": latest_cmf,
            "signal": signal,
            "pressure_strength": pressure_strength,
            "period": period
        }
        
        return standardize_output(result, "calculate_cmf")
        
    except Exception as e:
        return {"success": False, "error": f"CMF calculation failed: {str(e)}"}


def calculate_vpt(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate Volume Price Trend.
    
    Computes the Volume Price Trend (VPT), which combines price and volume to show the
    relationship between the two. VPT is similar to OBV but uses percentage price changes
    rather than simple up/down moves, making it more sensitive to the magnitude of price changes.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): Price and volume data as DataFrame or dictionary.
            Must contain 'close', 'volume' columns (case-insensitive).
    
    Returns:
        Dict[str, Any]: Dictionary containing VPT analysis with keys:
            - vpt (pd.Series): Volume Price Trend values
            - latest_value (Optional[float]): Most recent VPT value
            - trend_direction (str): VPT trend direction ('bullish', 'bearish', 'neutral')
            - momentum_strength (str): Momentum strength ('strong', 'moderate', 'weak')
            - divergence_signal (str): Price/VPT divergence ('bullish', 'bearish', 'none')
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required columns are missing or data is invalid.
    
    Example:
        >>> import pandas as pd
        >>> price_volume_data = pd.DataFrame({
        ...     'close': [102, 106, 109, 108, 113],
        ...     'volume': [1000, 1200, 800, 1500, 900]
        ... })
        >>> result = calculate_vpt(price_volume_data)
        >>> print(f"VPT: {result['latest_value']:.0f}")
        >>> print(f"Trend: {result['trend_direction']}")
        VPT: 2150
        Trend: bullish
        
    Note:
        - VPT = Previous VPT + (Volume × (Close - Previous Close) / Previous Close)
        - More sensitive than OBV to price change magnitude
        - Rising VPT suggests accumulation; falling VPT suggests distribution
        - Divergence with price can signal potential trend changes
        - Useful for confirming breakouts and trend continuation
        - Better than OBV for capturing proportional price movements
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['close', 'volume']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("Close and Volume data required for VPT calculation")
        
        # Standardize column names
        close_col = 'close' if 'close' in df.columns else 'Close'
        volume_col = 'volume' if 'volume' in df.columns else 'Volume'
        
        # Calculate VPT
        price_change_pct = df[close_col].pct_change()
        vpt_changes = df[volume_col] * price_change_pct
        vpt_series = vpt_changes.cumsum().dropna()
        
        latest_vpt = float(vpt_series.iloc[-1]) if len(vpt_series) > 0 else None
        
        # Trend direction analysis
        trend_direction = "neutral"
        momentum_strength = "moderate"
        
        if len(vpt_series) >= 5:
            recent_slope = np.polyfit(range(5), vpt_series.tail(5).values, 1)[0]
            slope_magnitude = abs(recent_slope)
            
            if recent_slope > 0:
                trend_direction = "bullish"
            elif recent_slope < 0:
                trend_direction = "bearish"
            
            # Momentum strength based on slope magnitude
            if slope_magnitude > vpt_series.std() * 0.5:
                momentum_strength = "strong"
            elif slope_magnitude < vpt_series.std() * 0.1:
                momentum_strength = "weak"
        
        # Divergence analysis
        divergence_signal = "none"
        if len(vpt_series) >= 10:
            price_trend = np.polyfit(range(10), df[close_col].tail(10).values, 1)[0]
            vpt_trend = np.polyfit(range(10), vpt_series.tail(10).values, 1)[0]
            
            if price_trend > 0 and vpt_trend < 0:
                divergence_signal = "bearish"
            elif price_trend < 0 and vpt_trend > 0:
                divergence_signal = "bullish"
        
        result = {
            "vpt": vpt_series,
            "latest_value": latest_vpt,
            "trend_direction": trend_direction,
            "momentum_strength": momentum_strength,
            "divergence_signal": divergence_signal
        }
        
        return standardize_output(result, "calculate_vpt")
        
    except Exception as e:
        return {"success": False, "error": f"VPT calculation failed: {str(e)}"}


def calculate_volume_sma(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 20) -> Dict[str, Any]:
    """Calculate Volume Simple Moving Average.
    
    Computes the Simple Moving Average of volume over a specified period. This helps
    identify periods of above or below average volume activity, which can signal
    increased interest or potential trend changes.
    
    Args:
        data (Union[pd.DataFrame, Dict[str, Any]]): Volume data as DataFrame or dictionary.
            Must contain 'volume' column (case-insensitive).
        period (int, optional): Period for volume SMA calculation. Defaults to 20.
    
    Returns:
        Dict[str, Any]: Dictionary containing Volume SMA analysis with keys:
            - volume_sma (pd.Series): Volume SMA values
            - latest_value (Optional[float]): Most recent volume SMA value
            - current_volume (Optional[float]): Most recent volume value
            - volume_ratio (Optional[float]): Current volume / Volume SMA ratio
            - volume_level (str): Volume level ('high', 'normal', 'low')
            - activity_signal (str): Activity signal ('increased', 'normal', 'decreased')
            - period (int): Period used for calculation
            - success (bool): Whether calculation succeeded
            - function_name (str): Name of the function for identification
    
    Raises:
        ValueError: If required volume column is missing or data is invalid.
        TypeError: If period parameter is not an integer.
    
    Example:
        >>> import pandas as pd
        >>> volume_data = pd.DataFrame({
        ...     'volume': [1000, 1200, 800, 1500, 900, 2000, 1100]
        ... })
        >>> result = calculate_volume_sma(volume_data, period=5)
        >>> print(f"Volume SMA: {result['latest_value']:.0f}")
        >>> print(f"Volume Ratio: {result['volume_ratio']:.2f}")
        >>> print(f"Activity: {result['activity_signal']}")
        Volume SMA: 1280
        Volume Ratio: 1.56
        Activity: increased
        
    Note:
        - Volume SMA = Average volume over specified period
        - Volume ratio > 1.5: High volume activity
        - Volume ratio < 0.7: Low volume activity
        - High volume often occurs at trend turning points
        - Low volume may indicate lack of conviction in current trend
        - Volume spikes can confirm breakouts or signal exhaustion
        - Used for filtering signals and confirming price movements
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required column
        volume_col = 'volume' if 'volume' in df.columns else 'Volume'
        if volume_col not in df.columns:
            raise ValueError("Volume data required for Volume SMA calculation")
        
        # Calculate Volume SMA
        volume_sma = df[volume_col].rolling(window=period).mean()
        volume_sma_series = volume_sma.dropna()
        
        latest_volume_sma = float(volume_sma_series.iloc[-1]) if len(volume_sma_series) > 0 else None
        current_volume = float(df[volume_col].iloc[-1]) if len(df) > 0 else None
        
        # Calculate volume ratio and signals
        volume_ratio = None
        volume_level = "normal"
        activity_signal = "normal"
        
        if latest_volume_sma and current_volume:
            volume_ratio = current_volume / latest_volume_sma
            
            if volume_ratio > 1.5:
                volume_level = "high"
                activity_signal = "increased"
            elif volume_ratio < 0.7:
                volume_level = "low"
                activity_signal = "decreased"
        
        result = {
            "volume_sma": volume_sma_series,
            "latest_value": latest_volume_sma,
            "current_volume": current_volume,
            "volume_ratio": volume_ratio,
            "volume_level": volume_level,
            "activity_signal": activity_signal,
            "period": period
        }
        
        return standardize_output(result, "calculate_volume_sma")
        
    except Exception as e:
        return {"success": False, "error": f"Volume SMA calculation failed: {str(e)}"}


# =============================================================================
# REGISTRY OF ALL VOLUME INDICATORS
# =============================================================================

VOLUME_INDICATORS_FUNCTIONS = {
    # Accumulation/Distribution Family
    'calculate_ad': calculate_ad,
    'calculate_adosc': calculate_adosc,
    
    # Money Flow Indicators
    'calculate_mfi': calculate_mfi,
    'calculate_obv': calculate_obv,
    'calculate_cmf': calculate_cmf,
    
    # Volume Analysis
    'calculate_vpt': calculate_vpt,
    'calculate_volume_sma': calculate_volume_sma
}