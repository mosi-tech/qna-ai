"""Volatility Indicators Package.

This package provides comprehensive volatility analysis indicators using the industry-standard
TA-Lib library. Volatility indicators measure the rate of price changes and market uncertainty,
helping traders assess risk levels, identify breakout opportunities, and set appropriate
stop-loss levels.

Modules:
    indicators: All volatility indicator calculations with standardized outputs

Available Volatility Indicators:
    Classic Volatility Measures:
        - calculate_atr: Average True Range for measuring price volatility
        - calculate_natr: Normalized Average True Range (ATR as percentage)
        - calculate_trange: True Range for single-period volatility measurement
    
    Bollinger Band Family:
        - calculate_bollinger_bands: Bollinger Bands with upper, middle, and lower bands
        - calculate_bollinger_percent_b: %B indicator showing position within bands
        - calculate_bollinger_bandwidth: Bandwidth showing band width relative to middle
    
    Statistical Volatility:
        - calculate_stddev: Standard Deviation of price movements
        - calculate_variance: Variance of price movements
    
    Advanced Volatility:
        - calculate_volatility_system: Multi-timeframe volatility analysis
        - calculate_volatility_breakout: Volatility-based breakout signals

Features:
    - Complete coverage of all TA-Lib volatility indicators
    - Industry-standard TA-Lib implementation for proven accuracy
    - Comprehensive signal generation for breakout and mean reversion strategies
    - Support for both pandas Series and DataFrame input formats
    - Automatic data validation and standardized error handling
    - Performance optimized using TA-Lib's C implementation
    - Google docstring documentation with examples and risk management notes

Example:
    >>> from mcp.analytics.indicators.volatility import calculate_atr, calculate_bollinger_bands
    >>> import pandas as pd
    >>> 
    >>> # Basic volatility analysis
    >>> ohlc_data = pd.DataFrame({
    ...     'high': [105, 108, 112, 110, 115],
    ...     'low': [98, 102, 105, 107, 110],
    ...     'close': [102, 106, 109, 108, 113]
    ... })
    >>> atr = calculate_atr(ohlc_data, period=14)
    >>> print(f"ATR: {atr['latest_value']:.2f} ({atr['atr_percent']:.1f}%)")
    >>> print(f"Volatility Level: {atr['volatility_level']}")
    >>> 
    >>> # Bollinger Bands analysis
    >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115])
    >>> bb = calculate_bollinger_bands(prices, period=20, std_dev=2.0)
    >>> print(f"Price Position: {bb['percent_b']:.2f}")
    >>> print(f"Signal: {bb['signal']}")

Note:
    - Volatility indicators are essential for risk management and position sizing
    - High volatility often precedes significant price movements
    - Low volatility (band squeezes) often precede breakouts
    - ATR is commonly used for stop-loss placement (1.5-2.0 × ATR)
    - All indicators return standardized dictionary outputs with success flags
"""

from .indicators import *

__all__ = [
    # Classic Volatility Measures
    'calculate_atr',
    'calculate_natr',
    'calculate_trange',
    
    # Bollinger Band Family
    'calculate_bollinger_bands',
    'calculate_bollinger_percent_b',
    'calculate_bollinger_bandwidth',
    
    # Statistical Volatility
    'calculate_stddev',
    'calculate_variance',
    
    # Registry
    'VOLATILITY_INDICATORS_FUNCTIONS'
]