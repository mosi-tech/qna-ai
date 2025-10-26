"""Momentum Indicators Package.

This package provides comprehensive momentum analysis indicators using the industry-standard
TA-Lib library. Momentum indicators measure the rate of change in price movements and help
identify overbought/oversold conditions, trend strength, and potential reversal points.

Modules:
    indicators: All momentum indicator calculations with standardized outputs

Available Momentum Indicators:
    Oscillators (0-100 Range):
        - calculate_rsi: Relative Strength Index with overbought/oversold signals
        - calculate_stochastic: Stochastic Oscillator with %K and %D values
        - calculate_stochastic_fast: Fast Stochastic Oscillator 
        - calculate_williams_r: Williams %R momentum oscillator
        - calculate_ultimate_oscillator: Ultimate Oscillator combining multiple timeframes
    
    Directional Movement:
        - calculate_adx: Average Directional Index for trend strength
        - calculate_adxr: Average Directional Movement Index Rating
        - calculate_dx: Directional Movement Index
        - calculate_minus_di: Minus Directional Indicator
        - calculate_plus_di: Plus Directional Indicator
        - calculate_aroon: Aroon oscillator for trend identification
        - calculate_aroon_oscillator: Aroon Oscillator derived value
    
    Price-Based Momentum:
        - calculate_macd: Moving Average Convergence Divergence
        - calculate_macd_ext: Extended MACD with custom MA types
        - calculate_macd_fix: Fixed MACD with specified signal period
        - calculate_ppo: Percentage Price Oscillator
        - calculate_apo: Absolute Price Oscillator
        - calculate_mom: Momentum (price change over N periods)
        - calculate_roc: Rate of Change percentage
        - calculate_rocp: Rate of Change percentage (alternative calculation)
        - calculate_rocr: Rate of Change ratio
        - calculate_rocr100: Rate of Change ratio * 100
        - calculate_trix: TRIX - 1-day Rate of Change of Triple Smoothed EMA
    
    Volume-Based Momentum:
        - calculate_mfi: Money Flow Index using price and volume
        - calculate_cci: Commodity Channel Index
    
    Specialized Oscillators:
        - calculate_bop: Balance of Power
        - calculate_cmo: Chande Momentum Oscillator

Features:
    - Complete coverage of all 24 TA-Lib momentum indicators
    - Industry-standard TA-Lib implementation for proven accuracy
    - Comprehensive signal generation (bullish/bearish/neutral/overbought/oversold)
    - Support for pandas Series and DataFrame input formats
    - Automatic data validation and standardized error handling
    - Performance optimized using TA-Lib's C implementation
    - Google docstring documentation with examples and technical notes

Example:
    >>> from mcp.analytics.indicators.momentum import calculate_rsi, calculate_adx, calculate_williams_r
    >>> import pandas as pd
    >>> 
    >>> # Basic momentum analysis
    >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115])
    >>> rsi = calculate_rsi(prices, period=14)
    >>> print(f"RSI: {rsi['latest_value']:.1f} - Signal: {rsi['signal']}")
    >>> 
    >>> # Trend strength analysis (requires OHLC data)
    >>> ohlc_data = pd.DataFrame({
    ...     'high': [105, 108, 112, 110, 115],
    ...     'low': [98, 102, 105, 107, 110],
    ...     'close': [102, 106, 109, 108, 113]
    ... })
    >>> adx = calculate_adx(ohlc_data, period=14)
    >>> print(f"Trend Strength (ADX): {adx['latest_value']:.1f}")
    >>> 
    >>> # Overbought/oversold analysis
    >>> williams = calculate_williams_r(ohlc_data, period=14)
    >>> print(f"Williams %R: {williams['signal']}")

Note:
    - Oscillators typically range from 0-100 with overbought (>70-80) and oversold (<20-30) levels
    - Directional indicators help determine trend strength and direction
    - Volume-based indicators require both price and volume data
    - All indicators return standardized dictionary outputs with success flags
"""

from .indicators import *

