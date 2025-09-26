"""Volume Indicators Package.

This package provides comprehensive volume analysis indicators using the industry-standard
TA-Lib library. Volume indicators analyze the relationship between price movements and
trading volume, helping identify the strength of trends, confirm price movements, and
detect potential reversals based on volume patterns.

Modules:
    indicators: All volume indicator calculations with standardized outputs

Available Volume Indicators:
    Accumulation/Distribution Family:
        - calculate_ad: Accumulation/Distribution Line (Chaikin A/D Line)
        - calculate_adosc: Accumulation/Distribution Oscillator (Chaikin Oscillator)
    
    Money Flow Indicators:
        - calculate_mfi: Money Flow Index (Volume-weighted RSI)
        - calculate_obv: On Balance Volume for trend confirmation
        - calculate_cmf: Chaikin Money Flow for buying/selling pressure
    
    Volume Price Trend:
        - calculate_vpt: Volume Price Trend indicator
        - calculate_pvt: Price Volume Trend for trend analysis
    
    Volume Moving Averages:
        - calculate_volume_sma: Simple Moving Average of volume
        - calculate_volume_ema: Exponential Moving Average of volume
        - calculate_vwap: Volume Weighted Average Price
    
    Volume Oscillators:
        - calculate_volume_oscillator: Volume oscillator for momentum
        - calculate_volume_rate_of_change: Volume rate of change
    
    Advanced Volume Analysis:
        - calculate_ease_of_movement: Ease of Movement indicator
        - calculate_negative_volume_index: Negative Volume Index
        - calculate_positive_volume_index: Positive Volume Index

Features:
    - Complete coverage of all TA-Lib volume indicators plus advanced volume analysis
    - Industry-standard TA-Lib implementation for proven accuracy
    - Comprehensive signal generation for trend confirmation and divergence analysis
    - Support for OHLCV (Open, High, Low, Close, Volume) data formats
    - Automatic data validation and standardized error handling
    - Performance optimized using TA-Lib's C implementation
    - Google docstring documentation with examples and volume analysis notes

Example:
    >>> from mcp.analytics.indicators.volume import calculate_obv, calculate_mfi, calculate_ad
    >>> import pandas as pd
    >>> 
    >>> # Basic volume analysis
    >>> ohlcv_data = pd.DataFrame({
    ...     'high': [105, 108, 112, 110, 115],
    ...     'low': [98, 102, 105, 107, 110],
    ...     'close': [102, 106, 109, 108, 113],
    ...     'volume': [1000, 1200, 800, 1500, 900]
    ... })
    >>> 
    >>> # On Balance Volume
    >>> obv = calculate_obv(ohlcv_data)
    >>> print(f"OBV: {obv['latest_value']:.0f}")
    >>> print(f"Volume Trend: {obv['volume_trend']}")
    >>> 
    >>> # Money Flow Index
    >>> mfi = calculate_mfi(ohlcv_data)
    >>> print(f"MFI: {mfi['latest_value']:.1f} - {mfi['signal']}")
    >>> 
    >>> # Accumulation/Distribution Line
    >>> ad = calculate_ad(ohlcv_data)
    >>> print(f"A/D Line: {ad['latest_value']:.0f}")

Note:
    - Volume indicators require OHLCV data (Open, High, Low, Close, Volume)
    - Volume confirms price movements: rising prices with rising volume = strong trend
    - Volume divergence can signal potential trend reversals
    - Volume spikes often occur at trend turning points
    - All indicators return standardized dictionary outputs with success flags
"""

from .indicators import *

