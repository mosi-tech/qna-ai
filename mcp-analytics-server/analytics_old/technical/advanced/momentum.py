"""
Advanced Momentum Indicators

Missing momentum indicators not available in the core module:
- Momentum (basic price momentum)
- True Strength Index (TSI)
- Price Oscillator (PPO)
- Percentage Price Oscillator
- Elder Ray Index (Bull/Bear Power)
- Klinger Oscillator

All functions follow consistent patterns:
- Input: pandas Series or DataFrame with OHLCV data
- Output: pandas Series or DataFrame with calculated indicator values
- Parameters: Standard parameter names with sensible defaults
- Error handling: Graceful handling of insufficient data
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, Dict, Any


def momentum(data: Union[pd.Series, pd.DataFrame], period: int = 10, 
             column: str = 'close') -> pd.Series:
    """
    Basic Price Momentum
    
    Measures rate of change in price over specified period.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Period for momentum calculation (default: 10)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with momentum values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return prices.diff(period)


def price_momentum_oscillator(data: Union[pd.Series, pd.DataFrame], period: int = 10,
                             column: str = 'close') -> pd.Series:
    """
    Price Momentum Oscillator (normalized momentum)
    
    Args:
        data: Price data (Series or DataFrame)
        period: Period for momentum calculation (default: 10)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with normalized momentum values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    momentum_vals = prices.diff(period)
    return (momentum_vals / prices.shift(period)) * 100


def true_strength_index(data: Union[pd.Series, pd.DataFrame], long_period: int = 25,
                       short_period: int = 13, column: str = 'close') -> pd.Series:
    """
    True Strength Index (TSI)
    
    Double-smoothed momentum oscillator that filters out price noise.
    
    Args:
        data: Price data (Series or DataFrame)  
        long_period: Long smoothing period (default: 25)
        short_period: Short smoothing period (default: 13)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with TSI values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate price changes
    price_change = prices.diff()
    
    # Double smooth price changes
    first_smooth = price_change.ewm(span=long_period).mean()
    double_smooth = first_smooth.ewm(span=short_period).mean()
    
    # Double smooth absolute price changes
    abs_first_smooth = price_change.abs().ewm(span=long_period).mean()
    abs_double_smooth = abs_first_smooth.ewm(span=short_period).mean()
    
    # Calculate TSI
    tsi = 100 * (double_smooth / abs_double_smooth)
    return tsi


def percentage_price_oscillator(data: Union[pd.Series, pd.DataFrame], fast_period: int = 12,
                               slow_period: int = 26, column: str = 'close') -> pd.Series:
    """
    Percentage Price Oscillator (PPO)
    
    Similar to MACD but shows percentage difference between two moving averages.
    
    Args:
        data: Price data (Series or DataFrame)
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with PPO values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    fast_ema = prices.ewm(span=fast_period).mean()
    slow_ema = prices.ewm(span=slow_period).mean()
    
    ppo = ((fast_ema - slow_ema) / slow_ema) * 100
    return ppo


def elder_ray_index(data: pd.DataFrame, period: int = 13) -> pd.DataFrame:
    """
    Elder Ray Index (Bull Power & Bear Power)
    
    Measures buying and selling pressure relative to moving average.
    
    Args:
        data: DataFrame with OHLC data
        period: EMA period (default: 13)
        
    Returns:
        DataFrame with columns: bull_power, bear_power, ema
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("Data must contain 'high', 'low', 'close' columns")
    
    ema_13 = data['close'].ewm(span=period).mean()
    bull_power = data['high'] - ema_13
    bear_power = data['low'] - ema_13
    
    return pd.DataFrame({
        'bull_power': bull_power,
        'bear_power': bear_power,  
        'ema': ema_13
    }, index=data.index)


def klinger_oscillator(data: pd.DataFrame, fast_period: int = 34, slow_period: int = 55,
                      signal_period: int = 13) -> pd.DataFrame:
    """
    Klinger Oscillator
    
    Volume-based oscillator that identifies long-term money flow trends.
    
    Args:
        data: DataFrame with OHLCV data
        fast_period: Fast EMA period (default: 34)
        slow_period: Slow EMA period (default: 55)
        signal_period: Signal line EMA period (default: 13)
        
    Returns:
        DataFrame with columns: klinger, signal
    """
    if not all(col in data.columns for col in ['high', 'low', 'close', 'volume']):
        raise ValueError("Data must contain 'high', 'low', 'close', 'volume' columns")
    
    # Calculate typical price and its change
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    typical_price_change = typical_price.diff()
    
    # Calculate Volume Force
    volume_force = np.where(typical_price_change > 0, data['volume'], -data['volume'])
    volume_force = pd.Series(volume_force, index=data.index)
    
    # Calculate Klinger Oscillator
    fast_ema = volume_force.ewm(span=fast_period).mean()
    slow_ema = volume_force.ewm(span=slow_period).mean()
    klinger = fast_ema - slow_ema
    
    # Signal line
    signal = klinger.ewm(span=signal_period).mean()
    
    return pd.DataFrame({
        'klinger': klinger,
        'signal': signal
    }, index=data.index)


def roc_smoothed(data: Union[pd.Series, pd.DataFrame], period: int = 12,
                smooth_period: int = 9, column: str = 'close') -> pd.Series:
    """
    Smoothed Rate of Change (ROC)
    
    Rate of change with additional smoothing using moving average.
    
    Args:
        data: Price data (Series or DataFrame)
        period: ROC period (default: 12)
        smooth_period: Smoothing period (default: 9)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with smoothed ROC values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate basic ROC
    roc = ((prices - prices.shift(period)) / prices.shift(period)) * 100
    
    # Apply smoothing
    roc_smoothed = roc.rolling(window=smooth_period).mean()
    return roc_smoothed


def stochastic_momentum_index(data: pd.DataFrame, k_period: int = 10, d_period: int = 3,
                             k_smooth: int = 3) -> pd.DataFrame:
    """
    Stochastic Momentum Index (SMI)
    
    Refined version of stochastic that uses double smoothing.
    
    Args:
        data: DataFrame with OHLC data
        k_period: %K period (default: 10)
        d_period: %D period (default: 3)
        k_smooth: %K smoothing period (default: 3)
        
    Returns:
        DataFrame with columns: smi_k, smi_d
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("Data must contain 'high', 'low', 'close' columns")
    
    # Calculate highest high and lowest low
    highest_high = data['high'].rolling(window=k_period).max()
    lowest_low = data['low'].rolling(window=k_period).min()
    
    # Calculate raw SMI
    hl_diff = highest_high - lowest_low
    close_diff = data['close'] - ((highest_high + lowest_low) / 2)
    
    # Double smoothing
    smooth_close_diff = close_diff.rolling(window=k_smooth).mean().rolling(window=d_period).mean()
    smooth_hl_diff = hl_diff.rolling(window=k_smooth).mean().rolling(window=d_period).mean()
    
    smi_k = 100 * (smooth_close_diff / (smooth_hl_diff / 2))
    smi_d = smi_k.rolling(window=d_period).mean()
    
    return pd.DataFrame({
        'smi_k': smi_k,
        'smi_d': smi_d
    }, index=data.index)


# Registry of all advanced momentum functions
ADVANCED_MOMENTUM_INDICATORS = {
    'momentum': momentum,
    'price_momentum_oscillator': price_momentum_oscillator,
    'true_strength_index': true_strength_index,
    'percentage_price_oscillator': percentage_price_oscillator,
    'elder_ray_index': elder_ray_index,
    'klinger_oscillator': klinger_oscillator,
    'roc_smoothed': roc_smoothed,
    'stochastic_momentum_index': stochastic_momentum_index
}


def get_momentum_function_names():
    """Get list of all advanced momentum function names"""
    return list(ADVANCED_MOMENTUM_INDICATORS.keys())