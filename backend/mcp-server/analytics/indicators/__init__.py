"""Technical Indicators Package.

This package provides comprehensive technical analysis indicators using the industry-standard
TA-Lib library for financial market analysis. All indicators follow Google docstring conventions
and return standardized dictionary outputs with success indicators and error handling.

Modules:
    technical: Trend indicators (SMA, EMA, crossovers)
    momentum: All momentum indicators (RSI, MACD, Stochastic, ADX, etc.)
    volatility: All volatility indicators (ATR, Bollinger Bands, etc.)
    volume: All volume indicators (OBV, MFI, A/D Line, etc.)

Available Indicators:
    Trend Indicators (from technical module):
        - calculate_sma: Simple Moving Average with trend analysis
        - calculate_ema: Exponential Moving Average with enhanced responsiveness
        - detect_sma_crossover: SMA crossover signals (Golden/Death cross)
        - detect_ema_crossover: EMA crossover signals for trend changes
    
    Momentum Indicators (from momentum submodule - 18 indicators):
        - calculate_rsi: Relative Strength Index with overbought/oversold signals
        - calculate_macd: MACD with signal line and histogram analysis
        - calculate_stochastic: Stochastic Oscillator with %K and %D signals
        - calculate_williams_r: Williams %R momentum oscillator
        - calculate_adx: Average Directional Index for trend strength
        - calculate_aroon: Aroon oscillator for trend identification
        - calculate_mfi: Money Flow Index using price and volume
        - calculate_cci: Commodity Channel Index
        - Plus 10+ additional momentum indicators (ADX family, PPO, ROC, etc.)
    
    Volatility Indicators (from volatility submodule - 8 indicators):
        - calculate_atr: Average True Range with volatility classification
        - calculate_natr: Normalized Average True Range
        - calculate_bollinger_bands: Bollinger Bands with %B and bandwidth
        - calculate_bollinger_percent_b: %B indicator for band position
        - calculate_bollinger_bandwidth: Band width for squeeze detection
        - calculate_stddev: Standard Deviation for statistical volatility
        - calculate_variance: Variance for risk measurement
        - calculate_trange: True Range for single-period volatility
        
    Volume Indicators (from volume submodule - 7 indicators):
        - calculate_obv: On Balance Volume for trend confirmation
        - calculate_ad: Accumulation/Distribution Line
        - calculate_adosc: Accumulation/Distribution Oscillator
        - calculate_mfi: Money Flow Index (also in momentum)
        - calculate_cmf: Chaikin Money Flow
        - calculate_vpt: Volume Price Trend
        - calculate_volume_sma: Volume Simple Moving Average

Note:
    This package now implements 40+ indicators from TA-Lib, organized by category in dedicated
    submodules for better organization and maintainability. Each category can be imported
    independently or used together for comprehensive technical analysis.

Features:
    - Industry-standard TA-Lib implementation for proven accuracy
    - Comprehensive signal generation (bullish/bearish/neutral/overbought/oversold)
    - Support for pandas Series and dictionary input formats
    - Automatic data validation and standardized error handling
    - Performance optimized using TA-Lib's C implementation

Example:
    >>> from mcp.analytics.indicators.technical import calculate_sma
    >>> from mcp.analytics.indicators.volatility import calculate_bollinger_bands
    >>> from mcp.analytics.indicators.momentum import calculate_rsi, calculate_macd, calculate_adx
    >>> import pandas as pd
    >>> 
    >>> # Price data
    >>> prices = pd.Series([100, 102, 98, 105, 110, 108, 112, 115])
    >>> 
    >>> # Trend analysis
    >>> sma = calculate_sma(prices, period=5)
    >>> print(f"SMA: {sma['latest_value']:.2f} - Trend: {sma['trend']}")
    >>> 
    >>> # Momentum analysis  
    >>> rsi = calculate_rsi(prices, period=14)
    >>> print(f"RSI: {rsi['latest_value']:.1f} - Signal: {rsi['signal']}")
    >>> 
    >>> # For OHLC indicators
    >>> ohlc_data = pd.DataFrame({'high': [105, 108], 'low': [98, 102], 'close': [102, 106]})
    >>> adx = calculate_adx(ohlc_data)
    >>> print(f"Trend Strength: {adx['trend_strength']}")
"""

from .technical import *
from .momentum import *
from .volatility import *
from .volume import *