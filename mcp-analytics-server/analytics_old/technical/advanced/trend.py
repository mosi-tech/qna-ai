"""
Advanced Trend Following Indicators

Missing trend indicators not available in the core module:
- Hull Moving Average (HMA)
- Kaufman Adaptive Moving Average (KAMA)
- Variable Moving Average (VMA)
- Triple Exponential Moving Average (TEMA)
- Zero Lag Exponential Moving Average (ZLEMA)
- McGinley Dynamic
- Arnaud Legoux Moving Average (ALMA)
- Linear Regression Moving Average
- Adaptive Moving Average

All functions follow consistent patterns:
- Input: pandas Series or DataFrame with OHLCV data
- Output: pandas Series or DataFrame with calculated indicator values
- Parameters: Standard parameter names with sensible defaults
"""

import pandas as pd
import numpy as np
from typing import Union, Optional


def hull_moving_average(data: Union[pd.Series, pd.DataFrame], period: int = 16,
                       column: str = 'close') -> pd.Series:
    """
    Hull Moving Average (HMA)
    
    Reduces lag while maintaining smoothness using weighted moving averages.
    
    Args:
        data: Price data (Series or DataFrame)
        period: HMA period (default: 16)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with HMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate weighted moving averages
    wma_half = prices.rolling(window=period//2).apply(
        lambda x: np.sum(x * np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1)), raw=True
    )
    wma_full = prices.rolling(window=period).apply(
        lambda x: np.sum(x * np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1)), raw=True
    )
    
    # Calculate HMA
    raw_hma = 2 * wma_half - wma_full
    hma_period = int(np.sqrt(period))
    
    hma = raw_hma.rolling(window=hma_period).apply(
        lambda x: np.sum(x * np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1)), raw=True
    )
    
    return hma


def kaufman_adaptive_moving_average(data: Union[pd.Series, pd.DataFrame], period: int = 10,
                                   fast_sc: float = 2.0, slow_sc: float = 30.0,
                                   column: str = 'close') -> pd.Series:
    """
    Kaufman Adaptive Moving Average (KAMA)
    
    Adapts to market volatility - moves fast in trending markets, slow in choppy markets.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Efficiency ratio period (default: 10)
        fast_sc: Fast smoothing constant (default: 2.0)
        slow_sc: Slow smoothing constant (default: 30.0)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with KAMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate efficiency ratio
    change = np.abs(prices.diff(period))
    volatility = np.abs(prices.diff()).rolling(window=period).sum()
    efficiency_ratio = change / volatility
    
    # Calculate smoothing constant
    fast_alpha = 2.0 / (fast_sc + 1)
    slow_alpha = 2.0 / (slow_sc + 1)
    smoothing_constant = (efficiency_ratio * (fast_alpha - slow_alpha) + slow_alpha) ** 2
    
    # Calculate KAMA
    kama = pd.Series(index=prices.index, dtype=float)
    kama.iloc[0] = prices.iloc[0]
    
    for i in range(1, len(prices)):
        if pd.notna(smoothing_constant.iloc[i]):
            kama.iloc[i] = kama.iloc[i-1] + smoothing_constant.iloc[i] * (prices.iloc[i] - kama.iloc[i-1])
        else:
            kama.iloc[i] = kama.iloc[i-1]
            
    return kama


def triple_exponential_moving_average(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                                     column: str = 'close') -> pd.Series:
    """
    Triple Exponential Moving Average (TEMA)
    
    Reduces lag by applying exponential smoothing three times.
    
    Args:
        data: Price data (Series or DataFrame)
        period: TEMA period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with TEMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    ema1 = prices.ewm(span=period).mean()
    ema2 = ema1.ewm(span=period).mean()
    ema3 = ema2.ewm(span=period).mean()
    
    tema = 3 * ema1 - 3 * ema2 + ema3
    return tema


def zero_lag_exponential_moving_average(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                                       column: str = 'close') -> pd.Series:
    """
    Zero Lag Exponential Moving Average (ZLEMA)
    
    Attempts to eliminate lag by using momentum to adjust the data.
    
    Args:
        data: Price data (Series or DataFrame)
        period: ZLEMA period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with ZLEMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate lag
    lag = (period - 1) / 2
    
    # Calculate momentum-adjusted prices
    ema_data = prices + (prices - prices.shift(int(lag)))
    
    # Apply EMA to adjusted data
    zlema = ema_data.ewm(span=period).mean()
    return zlema


def mcginley_dynamic(data: Union[pd.Series, pd.DataFrame], period: int = 14,
                    column: str = 'close') -> pd.Series:
    """
    McGinley Dynamic
    
    Adaptive moving average that adjusts to market speed changes.
    
    Args:
        data: Price data (Series or DataFrame)
        period: McGinley Dynamic period (default: 14)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with McGinley Dynamic values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    md = pd.Series(index=prices.index, dtype=float)
    md.iloc[0] = prices.iloc[0]
    
    for i in range(1, len(prices)):
        if pd.notna(md.iloc[i-1]) and md.iloc[i-1] != 0:
            factor = (prices.iloc[i] / md.iloc[i-1]) ** 4
            md.iloc[i] = md.iloc[i-1] + (prices.iloc[i] - md.iloc[i-1]) / (period * factor)
        else:
            md.iloc[i] = prices.iloc[i]
            
    return md


def arnaud_legoux_moving_average(data: Union[pd.Series, pd.DataFrame], period: int = 21,
                                offset: float = 0.85, sigma: float = 6.0,
                                column: str = 'close') -> pd.Series:
    """
    Arnaud Legoux Moving Average (ALMA)
    
    Uses Gaussian filter to reduce lag while maintaining smoothness.
    
    Args:
        data: Price data (Series or DataFrame)
        period: ALMA period (default: 21)
        offset: Phase/offset (default: 0.85, range 0-1)
        sigma: Smoothness (default: 6.0)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with ALMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate weights
    m = offset * (period - 1)
    s = period / sigma
    
    alma = pd.Series(index=prices.index, dtype=float)
    
    for i in range(period - 1, len(prices)):
        weights = []
        weighted_sum = 0
        weight_sum = 0
        
        for j in range(period):
            weight = np.exp(-((j - m) ** 2) / (2 * s ** 2))
            weighted_sum += prices.iloc[i - period + 1 + j] * weight
            weight_sum += weight
            
        alma.iloc[i] = weighted_sum / weight_sum
        
    return alma


def linear_regression_moving_average(data: Union[pd.Series, pd.DataFrame], period: int = 14,
                                    column: str = 'close') -> pd.Series:
    """
    Linear Regression Moving Average (LRMA)
    
    Uses linear regression to create a moving average that anticipates direction.
    
    Args:
        data: Price data (Series or DataFrame)
        period: LRMA period (default: 14)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with LRMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    def linear_regression_forecast(y):
        """Calculate linear regression forecast for last point"""
        if len(y) < 2:
            return y.iloc[-1]
        
        x = np.arange(len(y))
        
        # Calculate linear regression coefficients
        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x * x)
        
        # Slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Forecast for next period
        return slope * (len(y) - 1) + intercept
    
    lrma = prices.rolling(window=period).apply(linear_regression_forecast, raw=False)
    return lrma


def variable_moving_average(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                           column: str = 'close') -> pd.Series:
    """
    Variable Moving Average (VMA)
    
    Adjusts smoothing based on relative volatility.
    
    Args:
        data: Price data (Series or DataFrame)
        period: VMA period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with VMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate volatility index
    std = prices.rolling(window=period).std()
    std_ma = std.rolling(window=period).mean()
    vi = std / std_ma
    
    # Variable smoothing constant
    alpha = 2.0 / (period + 1)
    vma_alpha = alpha * vi
    
    # Calculate VMA
    vma = pd.Series(index=prices.index, dtype=float)
    vma.iloc[0] = prices.iloc[0]
    
    for i in range(1, len(prices)):
        if pd.notna(vma_alpha.iloc[i]):
            smoothing = min(vma_alpha.iloc[i], 1.0)  # Cap at 1.0
            vma.iloc[i] = vma.iloc[i-1] + smoothing * (prices.iloc[i] - vma.iloc[i-1])
        else:
            vma.iloc[i] = vma.iloc[i-1]
            
    return vma


# Registry of all advanced trend functions
ADVANCED_TREND_INDICATORS = {
    'hull_moving_average': hull_moving_average,
    'kaufman_adaptive_moving_average': kaufman_adaptive_moving_average,
    'triple_exponential_moving_average': triple_exponential_moving_average,
    'zero_lag_exponential_moving_average': zero_lag_exponential_moving_average,
    'mcginley_dynamic': mcginley_dynamic,
    'arnaud_legoux_moving_average': arnaud_legoux_moving_average,
    'linear_regression_moving_average': linear_regression_moving_average,
    'variable_moving_average': variable_moving_average
}


def get_trend_function_names():
    """Get list of all advanced trend function names"""
    return list(ADVANCED_TREND_INDICATORS.keys())