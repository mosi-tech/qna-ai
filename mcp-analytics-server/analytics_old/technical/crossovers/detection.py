"""
Crossover Detection Functions

This module provides sophisticated crossover detection for technical analysis.
All functions return detailed information about crossovers including:
- Crossover points with timestamps and values
- Crossover strength and momentum
- Volume confirmation (when applicable)
- Signal quality assessment

Dependencies: pandas, numpy, core indicators module
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from ..core.indicators import sma, ema, macd, rsi, stochastic


def moving_average_crossover(data: Union[pd.Series, pd.DataFrame], fast_period: int = 10, 
                           slow_period: int = 20, ma_type: str = 'sma', 
                           column: str = 'close') -> Dict[str, Any]:
    """
    Detect moving average crossovers (Golden Cross / Death Cross)
    
    Args:
        data: Price data (Series or DataFrame)
        fast_period: Fast moving average period (default: 10)
        slow_period: Slow moving average period (default: 20)
        ma_type: Type of MA - 'sma' or 'ema' (default: 'sma')
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        Dictionary with crossover analysis including:
        - crossover_points: List of crossover details
        - current_position: Above/below status
        - signal_strength: Current signal strength
        - total_bullish: Count of bullish crossovers
        - total_bearish: Count of bearish crossovers
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate moving averages
    if ma_type.lower() == 'ema':
        fast_ma = ema(prices, period=fast_period)
        slow_ma = ema(prices, period=slow_period)
    else:
        fast_ma = sma(prices, period=fast_period)
        slow_ma = sma(prices, period=slow_period)
    
    # Detect crossovers
    crossovers = []
    bullish_count = 0
    bearish_count = 0
    
    # Calculate the difference and identify crossover points
    ma_diff = fast_ma - slow_ma
    crossover_mask = (ma_diff.shift(1) * ma_diff < 0) & ~ma_diff.isna() & ~ma_diff.shift(1).isna()
    
    for idx in ma_diff[crossover_mask].index:
        if idx in ma_diff.index and ma_diff.loc[idx] > 0:  # Bullish crossover
            crossover_type = 'bullish'
            bullish_count += 1
        else:  # Bearish crossover
            crossover_type = 'bearish'
            bearish_count += 1
            
        crossovers.append({
            'timestamp': idx,
            'type': crossover_type,
            'price': prices.loc[idx] if idx in prices.index else None,
            'fast_ma': fast_ma.loc[idx] if idx in fast_ma.index else None,
            'slow_ma': slow_ma.loc[idx] if idx in slow_ma.index else None,
            'strength': abs(ma_diff.loc[idx]) if idx in ma_diff.index else 0
        })
    
    # Current status
    current_diff = ma_diff.iloc[-1] if not ma_diff.empty and not pd.isna(ma_diff.iloc[-1]) else 0
    current_position = 'above' if current_diff > 0 else 'below'
    signal_strength = abs(current_diff) / prices.iloc[-1] * 100 if not prices.empty else 0
    
    return {
        'crossover_points': crossovers[-10:],  # Last 10 crossovers
        'current_position': current_position,
        'signal_strength': float(signal_strength),
        'total_bullish': bullish_count,
        'total_bearish': bearish_count,
        'ma_type': ma_type,
        'fast_period': fast_period,
        'slow_period': slow_period
    }


def macd_crossover(data: Union[pd.Series, pd.DataFrame], fast: int = 12, slow: int = 26, 
                  signal: int = 9, column: str = 'close') -> Dict[str, Any]:
    """
    Detect MACD line and signal line crossovers
    
    Args:
        data: Price data (Series or DataFrame)
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line EMA period (default: 9)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        Dictionary with MACD crossover analysis
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    macd_data = macd(prices, fast=fast, slow=slow, signal=signal)
    
    # Detect crossovers
    crossovers = []
    bullish_count = 0
    bearish_count = 0
    
    # MACD line crosses above/below signal line
    macd_diff = macd_data['macd'] - macd_data['signal']
    crossover_mask = (macd_diff.shift(1) * macd_diff < 0) & ~macd_diff.isna() & ~macd_diff.shift(1).isna()
    
    for idx in macd_diff[crossover_mask].index:
        if idx in macd_diff.index and macd_diff.loc[idx] > 0:
            crossover_type = 'bullish'
            bullish_count += 1
        else:
            crossover_type = 'bearish'
            bearish_count += 1
            
        crossovers.append({
            'timestamp': idx,
            'type': crossover_type,
            'price': prices.loc[idx] if idx in prices.index else None,
            'macd': macd_data['macd'].loc[idx] if idx in macd_data['macd'].index else None,
            'signal': macd_data['signal'].loc[idx] if idx in macd_data['signal'].index else None,
            'histogram': macd_data['histogram'].loc[idx] if idx in macd_data['histogram'].index else None,
            'strength': abs(macd_diff.loc[idx]) if idx in macd_diff.index else 0
        })
    
    # Current status
    current_diff = macd_diff.iloc[-1] if not macd_diff.empty and not pd.isna(macd_diff.iloc[-1]) else 0
    current_position = 'above' if current_diff > 0 else 'below'
    
    return {
        'crossover_points': crossovers[-10:],
        'current_position': current_position,
        'current_histogram': float(macd_data['histogram'].iloc[-1]) if not macd_data['histogram'].empty else 0,
        'total_bullish': bullish_count,
        'total_bearish': bearish_count,
        'zero_line_position': 'above' if macd_data['macd'].iloc[-1] > 0 else 'below'
    }


def rsi_level_cross(data: Union[pd.Series, pd.DataFrame], period: int = 14, 
                   overbought: float = 70, oversold: float = 30, 
                   column: str = 'close') -> Dict[str, Any]:
    """
    Detect RSI crosses above/below key levels
    
    Args:
        data: Price data (Series or DataFrame)
        period: RSI period (default: 14)
        overbought: Overbought level (default: 70)
        oversold: Oversold level (default: 30)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        Dictionary with RSI level crossover analysis
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    rsi_values = rsi(prices, period=period)
    
    # Detect level crosses
    overbought_crosses = []
    oversold_crosses = []
    
    # Overbought crosses (entering and exiting)
    ob_enter = (rsi_values.shift(1) < overbought) & (rsi_values >= overbought)
    ob_exit = (rsi_values.shift(1) >= overbought) & (rsi_values < overbought)
    
    for idx in rsi_values[ob_enter].index:
        overbought_crosses.append({
            'timestamp': idx,
            'type': 'enter_overbought',
            'rsi_value': rsi_values.loc[idx],
            'price': prices.loc[idx] if idx in prices.index else None
        })
        
    for idx in rsi_values[ob_exit].index:
        overbought_crosses.append({
            'timestamp': idx,
            'type': 'exit_overbought',
            'rsi_value': rsi_values.loc[idx],
            'price': prices.loc[idx] if idx in prices.index else None
        })
    
    # Oversold crosses (entering and exiting)
    os_enter = (rsi_values.shift(1) > oversold) & (rsi_values <= oversold)
    os_exit = (rsi_values.shift(1) <= oversold) & (rsi_values > oversold)
    
    for idx in rsi_values[os_enter].index:
        oversold_crosses.append({
            'timestamp': idx,
            'type': 'enter_oversold',
            'rsi_value': rsi_values.loc[idx],
            'price': prices.loc[idx] if idx in prices.index else None
        })
        
    for idx in rsi_values[os_exit].index:
        oversold_crosses.append({
            'timestamp': idx,
            'type': 'exit_oversold',
            'rsi_value': rsi_values.loc[idx],
            'price': prices.loc[idx] if idx in prices.index else None
        })
    
    current_rsi = rsi_values.iloc[-1] if not rsi_values.empty else 50
    
    return {
        'overbought_crosses': overbought_crosses[-5:],
        'oversold_crosses': oversold_crosses[-5:],
        'current_rsi': float(current_rsi),
        'current_status': ('overbought' if current_rsi >= overbought else 
                          'oversold' if current_rsi <= oversold else 'neutral'),
        'overbought_level': overbought,
        'oversold_level': oversold
    }


def stochastic_crossover(data: pd.DataFrame, k_period: int = 14, d_period: int = 3,
                        high_col: str = 'high', low_col: str = 'low', 
                        close_col: str = 'close') -> Dict[str, Any]:
    """
    Detect Stochastic %K and %D crossovers
    
    Args:
        data: OHLC DataFrame
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        Dictionary with Stochastic crossover analysis
    """
    stoch_data = stochastic(data, k_period=k_period, d_period=d_period, 
                           high_col=high_col, low_col=low_col, close_col=close_col)
    
    crossovers = []
    bullish_count = 0
    bearish_count = 0
    
    # %K crosses above/below %D
    stoch_diff = stoch_data['percent_k'] - stoch_data['percent_d']
    crossover_mask = (stoch_diff.shift(1) * stoch_diff < 0) & ~stoch_diff.isna() & ~stoch_diff.shift(1).isna()
    
    for idx in stoch_diff[crossover_mask].index:
        if idx in stoch_diff.index and stoch_diff.loc[idx] > 0:
            crossover_type = 'bullish'
            bullish_count += 1
        else:
            crossover_type = 'bearish'
            bearish_count += 1
            
        crossovers.append({
            'timestamp': idx,
            'type': crossover_type,
            'price': data[close_col].loc[idx] if idx in data[close_col].index else None,
            'percent_k': stoch_data['percent_k'].loc[idx] if idx in stoch_data['percent_k'].index else None,
            'percent_d': stoch_data['percent_d'].loc[idx] if idx in stoch_data['percent_d'].index else None,
            'strength': abs(stoch_diff.loc[idx]) if idx in stoch_diff.index else 0
        })
    
    current_k = stoch_data['percent_k'].iloc[-1] if not stoch_data['percent_k'].empty else 50
    current_d = stoch_data['percent_d'].iloc[-1] if not stoch_data['percent_d'].empty else 50
    
    return {
        'crossover_points': crossovers[-10:],
        'current_percent_k': float(current_k),
        'current_percent_d': float(current_d),
        'current_position': 'above' if current_k > current_d else 'below',
        'total_bullish': bullish_count,
        'total_bearish': bearish_count
    }


def price_channel_breakout(data: pd.DataFrame, period: int = 20, 
                          high_col: str = 'high', low_col: str = 'low', 
                          close_col: str = 'close') -> Dict[str, Any]:
    """
    Detect breakouts above/below price channels (Donchian Channels)
    
    Args:
        data: OHLC DataFrame
        period: Channel period (default: 20)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        Dictionary with breakout analysis
    """
    from ..core.indicators import donchian_channels
    
    channels = donchian_channels(data, period=period, high_col=high_col, low_col=low_col, close_col=close_col)
    closes = data[close_col]
    
    breakouts = []
    bullish_count = 0
    bearish_count = 0
    
    # Bullish breakout: close above upper channel
    bullish_breakout = (closes.shift(1) <= channels['upper'].shift(1)) & (closes > channels['upper'])
    
    for idx in closes[bullish_breakout].index:
        bullish_count += 1
        breakouts.append({
            'timestamp': idx,
            'type': 'bullish_breakout',
            'price': closes.loc[idx],
            'channel_level': channels['upper'].loc[idx] if idx in channels['upper'].index else None,
            'strength': ((closes.loc[idx] - channels['upper'].loc[idx]) / channels['upper'].loc[idx] * 100) 
                       if idx in channels['upper'].index else 0
        })
    
    # Bearish breakdown: close below lower channel
    bearish_breakdown = (closes.shift(1) >= channels['lower'].shift(1)) & (closes < channels['lower'])
    
    for idx in closes[bearish_breakdown].index:
        bearish_count += 1
        breakouts.append({
            'timestamp': idx,
            'type': 'bearish_breakdown',
            'price': closes.loc[idx],
            'channel_level': channels['lower'].loc[idx] if idx in channels['lower'].index else None,
            'strength': ((channels['lower'].loc[idx] - closes.loc[idx]) / channels['lower'].loc[idx] * 100)
                       if idx in channels['lower'].index else 0
        })
    
    current_price = closes.iloc[-1]
    current_upper = channels['upper'].iloc[-1]
    current_lower = channels['lower'].iloc[-1]
    
    return {
        'breakout_points': sorted(breakouts, key=lambda x: x['timestamp'])[-10:],
        'current_price': float(current_price),
        'current_upper_channel': float(current_upper),
        'current_lower_channel': float(current_lower),
        'channel_position': (
            'above' if current_price > current_upper else
            'below' if current_price < current_lower else
            'within'
        ),
        'total_bullish_breakouts': bullish_count,
        'total_bearish_breakouts': bearish_count
    }


def bollinger_band_crossover(data: Union[pd.Series, pd.DataFrame], period: int = 20, 
                            std_dev: float = 2.0, column: str = 'close') -> Dict[str, Any]:
    """
    Detect price crossovers with Bollinger Bands
    
    Args:
        data: Price data (Series or DataFrame)
        period: Bollinger Band period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        Dictionary with Bollinger Band crossover analysis
    """
    from ..core.indicators import bollinger_bands
    
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    bb = bollinger_bands(prices, period=period, std_dev=std_dev)
    
    crossovers = []
    upper_touches = 0
    lower_touches = 0
    
    # Detect crossovers above upper band
    upper_cross = (prices.shift(1) <= bb['upper'].shift(1)) & (prices > bb['upper'])
    for idx in prices[upper_cross].index:
        upper_touches += 1
        crossovers.append({
            'timestamp': idx,
            'type': 'upper_breakout',
            'price': prices.loc[idx],
            'band_level': bb['upper'].loc[idx] if idx in bb['upper'].index else None,
            'percent_b': bb['percent_b'].loc[idx] if idx in bb['percent_b'].index else None,
            'strength': ((prices.loc[idx] - bb['upper'].loc[idx]) / bb['upper'].loc[idx] * 100) 
                       if idx in bb['upper'].index else 0
        })
    
    # Detect crossovers below lower band
    lower_cross = (prices.shift(1) >= bb['lower'].shift(1)) & (prices < bb['lower'])
    for idx in prices[lower_cross].index:
        lower_touches += 1
        crossovers.append({
            'timestamp': idx,
            'type': 'lower_breakdown',
            'price': prices.loc[idx],
            'band_level': bb['lower'].loc[idx] if idx in bb['lower'].index else None,
            'percent_b': bb['percent_b'].loc[idx] if idx in bb['percent_b'].index else None,
            'strength': ((bb['lower'].loc[idx] - prices.loc[idx]) / bb['lower'].loc[idx] * 100)
                       if idx in bb['lower'].index else 0
        })
    
    # Return to middle band detection
    middle_returns = []
    outside_band = (prices > bb['upper']) | (prices < bb['lower'])
    inside_return = outside_band.shift(1) & ~outside_band
    
    for idx in prices[inside_return].index:
        middle_returns.append({
            'timestamp': idx,
            'type': 'return_to_middle',
            'price': prices.loc[idx],
            'percent_b': bb['percent_b'].loc[idx] if idx in bb['percent_b'].index else None
        })
    
    current_price = prices.iloc[-1]
    current_upper = bb['upper'].iloc[-1]
    current_lower = bb['lower'].iloc[-1]
    current_percent_b = bb['percent_b'].iloc[-1] if not bb['percent_b'].empty else 0.5
    
    return {
        'crossover_points': sorted(crossovers, key=lambda x: x['timestamp'])[-10:],
        'middle_returns': middle_returns[-5:],
        'current_price': float(current_price),
        'current_upper_band': float(current_upper),
        'current_lower_band': float(current_lower),
        'current_percent_b': float(current_percent_b),
        'band_position': (
            'above_upper' if current_price > current_upper else
            'below_lower' if current_price < current_lower else
            'within_bands'
        ),
        'total_upper_touches': upper_touches,
        'total_lower_touches': lower_touches,
        'squeeze_level': float(bb['width'].iloc[-1]) if not bb['width'].empty else 0
    }


def adx_directional_crossover(data: pd.DataFrame, period: int = 14,
                             high_col: str = 'high', low_col: str = 'low', 
                             close_col: str = 'close') -> Dict[str, Any]:
    """
    Detect ADX +DI and -DI crossovers for trend direction changes
    
    Args:
        data: OHLC DataFrame
        period: ADX period (default: 14)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        Dictionary with ADX directional crossover analysis
    """
    from ..core.indicators import adx
    
    adx_data = adx(data, period=period, high_col=high_col, low_col=low_col, close_col=close_col)
    
    crossovers = []
    bullish_count = 0
    bearish_count = 0
    
    # +DI crosses above -DI (bullish)
    di_diff = adx_data['plus_di'] - adx_data['minus_di']
    crossover_mask = (di_diff.shift(1) <= 0) & (di_diff > 0)
    
    for idx in di_diff[crossover_mask].index:
        bullish_count += 1
        crossovers.append({
            'timestamp': idx,
            'type': 'bullish_di_cross',
            'price': data[close_col].loc[idx] if idx in data[close_col].index else None,
            'plus_di': adx_data['plus_di'].loc[idx] if idx in adx_data['plus_di'].index else None,
            'minus_di': adx_data['minus_di'].loc[idx] if idx in adx_data['minus_di'].index else None,
            'adx': adx_data['adx'].loc[idx] if idx in adx_data['adx'].index else None,
            'strength': abs(di_diff.loc[idx]) if idx in di_diff.index else 0
        })
    
    # +DI crosses below -DI (bearish)
    crossover_mask = (di_diff.shift(1) >= 0) & (di_diff < 0)
    
    for idx in di_diff[crossover_mask].index:
        bearish_count += 1
        crossovers.append({
            'timestamp': idx,
            'type': 'bearish_di_cross',
            'price': data[close_col].loc[idx] if idx in data[close_col].index else None,
            'plus_di': adx_data['plus_di'].loc[idx] if idx in adx_data['plus_di'].index else None,
            'minus_di': adx_data['minus_di'].loc[idx] if idx in adx_data['minus_di'].index else None,
            'adx': adx_data['adx'].loc[idx] if idx in adx_data['adx'].index else None,
            'strength': abs(di_diff.loc[idx]) if idx in di_diff.index else 0
        })
    
    current_plus_di = adx_data['plus_di'].iloc[-1] if not adx_data['plus_di'].empty else 20
    current_minus_di = adx_data['minus_di'].iloc[-1] if not adx_data['minus_di'].empty else 20
    current_adx = adx_data['adx'].iloc[-1] if not adx_data['adx'].empty else 20
    
    return {
        'crossover_points': sorted(crossovers, key=lambda x: x['timestamp'])[-10:],
        'current_plus_di': float(current_plus_di),
        'current_minus_di': float(current_minus_di),
        'current_adx': float(current_adx),
        'current_trend': 'bullish' if current_plus_di > current_minus_di else 'bearish',
        'trend_strength': (
            'very_strong' if current_adx > 50 else
            'strong' if current_adx > 25 else
            'weak'
        ),
        'total_bullish_crosses': bullish_count,
        'total_bearish_crosses': bearish_count
    }


def price_moving_average_crossover(data: Union[pd.Series, pd.DataFrame], period: int = 20, 
                                  ma_type: str = 'sma', column: str = 'close') -> Dict[str, Any]:
    """
    Detect price crossovers above/below a single moving average
    
    Args:
        data: Price data (Series or DataFrame)
        period: Moving average period (default: 20)
        ma_type: Type of MA - 'sma' or 'ema' (default: 'sma')
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        Dictionary with price vs MA crossover analysis
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate moving average
    if ma_type.lower() == 'ema':
        ma = ema(prices, period=period)
    else:
        ma = sma(prices, period=period)
    
    crossovers = []
    bullish_count = 0
    bearish_count = 0
    
    # Price crosses above MA (bullish)
    bullish_cross = (prices.shift(1) <= ma.shift(1)) & (prices > ma)
    for idx in prices[bullish_cross].index:
        bullish_count += 1
        crossovers.append({
            'timestamp': idx,
            'type': 'price_above_ma',
            'price': prices.loc[idx],
            'ma_value': ma.loc[idx] if idx in ma.index else None,
            'strength': ((prices.loc[idx] - ma.loc[idx]) / ma.loc[idx] * 100) 
                       if idx in ma.index else 0
        })
    
    # Price crosses below MA (bearish)
    bearish_cross = (prices.shift(1) >= ma.shift(1)) & (prices < ma)
    for idx in prices[bearish_cross].index:
        bearish_count += 1
        crossovers.append({
            'timestamp': idx,
            'type': 'price_below_ma',
            'price': prices.loc[idx],
            'ma_value': ma.loc[idx] if idx in ma.index else None,
            'strength': ((ma.loc[idx] - prices.loc[idx]) / ma.loc[idx] * 100) 
                       if idx in ma.index else 0
        })
    
    current_price = prices.iloc[-1]
    current_ma = ma.iloc[-1] if not ma.empty else current_price
    
    return {
        'crossover_points': sorted(crossovers, key=lambda x: x['timestamp'])[-10:],
        'current_price': float(current_price),
        'current_ma': float(current_ma),
        'current_position': 'above' if current_price > current_ma else 'below',
        'distance_percent': ((current_price - current_ma) / current_ma * 100),
        'total_bullish_crosses': bullish_count,
        'total_bearish_crosses': bearish_count,
        'ma_type': ma_type,
        'period': period
    }


def zero_line_crossover(data: Union[pd.Series, pd.DataFrame], indicator: str = 'macd', 
                       column: str = 'close', **kwargs) -> Dict[str, Any]:
    """
    Detect oscillator crossovers above/below zero line
    
    Args:
        data: Price data (Series or DataFrame)
        indicator: Indicator type ('macd', 'roc', 'awesome_oscillator')
        column: Column name if DataFrame (default: 'close')
        **kwargs: Additional parameters for the indicator
        
    Returns:
        Dictionary with zero line crossover analysis
    """
    from ..core.indicators import macd as macd_calc, rate_of_change, awesome_oscillator
    
    # Calculate the indicator
    if indicator == 'macd':
        macd_data = macd_calc(data, column=column, **kwargs)
        oscillator = macd_data['macd']
    elif indicator == 'roc':
        oscillator = rate_of_change(data, column=column, **kwargs)
    elif indicator == 'awesome_oscillator':
        oscillator = awesome_oscillator(data, **kwargs)
    else:
        raise ValueError(f"Unsupported indicator: {indicator}")
    
    crossovers = []
    bullish_count = 0
    bearish_count = 0
    
    # Crosses above zero (bullish)
    bullish_cross = (oscillator.shift(1) <= 0) & (oscillator > 0)
    for idx in oscillator[bullish_cross].index:
        bullish_count += 1
        crossovers.append({
            'timestamp': idx,
            'type': 'above_zero',
            'value': oscillator.loc[idx],
            'strength': float(oscillator.loc[idx])
        })
    
    # Crosses below zero (bearish)
    bearish_cross = (oscillator.shift(1) >= 0) & (oscillator < 0)
    for idx in oscillator[bearish_cross].index:
        bearish_count += 1
        crossovers.append({
            'timestamp': idx,
            'type': 'below_zero',
            'value': oscillator.loc[idx],
            'strength': float(abs(oscillator.loc[idx]))
        })
    
    current_value = oscillator.iloc[-1] if not oscillator.empty else 0
    
    return {
        'crossover_points': sorted(crossovers, key=lambda x: x['timestamp'])[-10:],
        'current_value': float(current_value),
        'current_position': 'above_zero' if current_value > 0 else 'below_zero',
        'total_bullish_crosses': bullish_count,
        'total_bearish_crosses': bearish_count,
        'indicator': indicator,
        'distance_from_zero': float(abs(current_value))
    }


def multi_timeframe_crossover(data: Union[pd.Series, pd.DataFrame], fast_period: int = 5, 
                             medium_period: int = 10, slow_period: int = 20,
                             ma_type: str = 'ema', column: str = 'close') -> Dict[str, Any]:
    """
    Detect multi-timeframe moving average crossovers (3 MAs)
    
    Args:
        data: Price data (Series or DataFrame)
        fast_period: Fast MA period (default: 5)
        medium_period: Medium MA period (default: 10)
        slow_period: Slow MA period (default: 20)
        ma_type: Type of MA - 'sma' or 'ema' (default: 'ema')
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        Dictionary with multi-timeframe crossover analysis
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate moving averages
    if ma_type.lower() == 'ema':
        fast_ma = ema(prices, period=fast_period)
        medium_ma = ema(prices, period=medium_period)
        slow_ma = ema(prices, period=slow_period)
    else:
        fast_ma = sma(prices, period=fast_period)
        medium_ma = sma(prices, period=medium_period)
        slow_ma = sma(prices, period=slow_period)
    
    # Detect alignment patterns
    alignment_signals = []
    
    for i in range(max(fast_period, medium_period, slow_period), len(prices)):
        idx = prices.index[i]
        
        fast_val = fast_ma.loc[idx] if idx in fast_ma.index else None
        medium_val = medium_ma.loc[idx] if idx in medium_ma.index else None
        slow_val = slow_ma.loc[idx] if idx in slow_ma.index else None
        
        if all(val is not None for val in [fast_val, medium_val, slow_val]):
            # Perfect bullish alignment: Fast > Medium > Slow
            if fast_val > medium_val > slow_val:
                prev_idx = prices.index[i-1]
                prev_fast = fast_ma.loc[prev_idx] if prev_idx in fast_ma.index else None
                prev_medium = medium_ma.loc[prev_idx] if prev_idx in medium_ma.index else None
                prev_slow = slow_ma.loc[prev_idx] if prev_idx in slow_ma.index else None
                
                # Check if this is a new alignment
                if not (prev_fast and prev_medium and prev_slow and 
                       prev_fast > prev_medium > prev_slow):
                    alignment_signals.append({
                        'timestamp': idx,
                        'type': 'bullish_alignment',
                        'price': prices.loc[idx],
                        'fast_ma': fast_val,
                        'medium_ma': medium_val,
                        'slow_ma': slow_val,
                        'strength': (fast_val - slow_val) / slow_val * 100
                    })
            
            # Perfect bearish alignment: Fast < Medium < Slow
            elif fast_val < medium_val < slow_val:
                prev_idx = prices.index[i-1]
                prev_fast = fast_ma.loc[prev_idx] if prev_idx in fast_ma.index else None
                prev_medium = medium_ma.loc[prev_idx] if prev_idx in medium_ma.index else None
                prev_slow = slow_ma.loc[prev_idx] if prev_idx in slow_ma.index else None
                
                # Check if this is a new alignment
                if not (prev_fast and prev_medium and prev_slow and 
                       prev_fast < prev_medium < prev_slow):
                    alignment_signals.append({
                        'timestamp': idx,
                        'type': 'bearish_alignment',
                        'price': prices.loc[idx],
                        'fast_ma': fast_val,
                        'medium_ma': medium_val,
                        'slow_ma': slow_val,
                        'strength': (slow_val - fast_val) / slow_val * 100
                    })
    
    # Current status
    current_fast = fast_ma.iloc[-1] if not fast_ma.empty else 0
    current_medium = medium_ma.iloc[-1] if not medium_ma.empty else 0
    current_slow = slow_ma.iloc[-1] if not slow_ma.empty else 0
    
    if current_fast > current_medium > current_slow:
        current_alignment = 'bullish'
    elif current_fast < current_medium < current_slow:
        current_alignment = 'bearish'
    else:
        current_alignment = 'mixed'
    
    return {
        'alignment_signals': alignment_signals[-10:],
        'current_alignment': current_alignment,
        'current_fast_ma': float(current_fast),
        'current_medium_ma': float(current_medium),
        'current_slow_ma': float(current_slow),
        'ma_spread': float(abs(current_fast - current_slow)),
        'total_bullish_alignments': len([s for s in alignment_signals if s['type'] == 'bullish_alignment']),
        'total_bearish_alignments': len([s for s in alignment_signals if s['type'] == 'bearish_alignment']),
        'periods': {'fast': fast_period, 'medium': medium_period, 'slow': slow_period},
        'ma_type': ma_type
    }


# Registry of all crossover detection functions
CROSSOVER_FUNCTIONS = {
    'moving_average_crossover': moving_average_crossover,
    'macd_crossover': macd_crossover,
    'rsi_level_cross': rsi_level_cross,
    'stochastic_crossover': stochastic_crossover,
    'price_channel_breakout': price_channel_breakout,
    'bollinger_band_crossover': bollinger_band_crossover,
    'adx_directional_crossover': adx_directional_crossover,
    'price_moving_average_crossover': price_moving_average_crossover,
    'zero_line_crossover': zero_line_crossover,
    'multi_timeframe_crossover': multi_timeframe_crossover
}