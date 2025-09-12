#!/usr/bin/env python3
"""
Momentum Indicators - Single source of truth for all momentum-based technical indicators.
Includes RSI, MACD, Stochastic, Williams %R, Awesome Oscillator, Ultimate Oscillator, ROC.
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Any, Optional, Union

from .framework import (
    mcp_resilient, standardize_ta_response, detect_crossovers, 
    detect_divergences, calculate_signal_strength, safe_ta_calculation
)

# =============================================================================
# RSI (RELATIVE STRENGTH INDEX)
# =============================================================================

@mcp_resilient(min_periods=14, required_columns=['close'])
def calculate_rsi(data: pd.DataFrame, window: int = 14) -> Dict[str, Any]:
    """
    Calculate RSI with comprehensive analysis including divergences and trading signals.
    Single authoritative implementation.
    """
    # Calculate RSI
    rsi = safe_ta_calculation(ta.momentum.rsi, data['close'], window=window)
    if rsi is None:
        return {'error': 'RSI calculation failed'}
    
    current_rsi = float(rsi.iloc[-1])
    
    # Signal classification
    if current_rsi > 70:
        signal = 'overbought'
        position = 'sell_zone'
    elif current_rsi < 30:
        signal = 'oversold'
        position = 'buy_zone'
    elif current_rsi > 60:
        signal = 'strong'
        position = 'bullish'
    elif current_rsi < 40:
        signal = 'weak'
        position = 'bearish'
    else:
        signal = 'neutral'
        position = 'range_bound'
    
    # RSI momentum and trend
    rsi_momentum = rsi.diff(5).iloc[-1] if len(rsi) > 5 else 0
    rsi_trend = 'rising' if rsi_momentum > 0 else 'falling' if rsi_momentum < 0 else 'flat'
    
    # Divergence analysis
    divergences = detect_divergences(data['close'], rsi, window=20)
    
    # Generate trading signals
    trading_signals = []
    
    if signal == 'oversold' and rsi_momentum > 0:
        trading_signals.append("RSI oversold with upward momentum - potential buy signal")
    if signal == 'overbought' and rsi_momentum < 0:
        trading_signals.append("RSI overbought with downward momentum - potential sell signal")
    if len(divergences) > 0 and divergences[-1]['type'] == 'bearish_divergence':
        trading_signals.append("Bearish RSI divergence - consider taking profits")
    if len(divergences) > 0 and divergences[-1]['type'] == 'bullish_divergence':
        trading_signals.append("Bullish RSI divergence - potential reversal signal")
    
    # Support and resistance levels
    rsi_levels = {
        'extreme_overbought': 80,
        'overbought': 70,
        'midline': 50,
        'oversold': 30,
        'extreme_oversold': 20
    }
    
    return standardize_ta_response(
        function_name='calculate_rsi',
        indicator_name='RSI',
        current_value=current_rsi,
        signal=signal,
        data={
            'position': position,
            'values': rsi.dropna().tail(50).tolist(),
            'momentum': float(rsi_momentum) if not pd.isna(rsi_momentum) else 0,
            'trend': rsi_trend,
            'levels': rsi_levels,
            'divergences': divergences[-3:],
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'statistics': {
                'average': float(rsi.mean()),
                'volatility': float(rsi.std()),
                'periods_overbought': int((rsi > 70).sum()),
                'periods_oversold': int((rsi < 30).sum())
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# MACD (MOVING AVERAGE CONVERGENCE DIVERGENCE)
# =============================================================================

@mcp_resilient(min_periods=26, required_columns=['close'])
def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
    """
    Calculate MACD with crossovers, histogram analysis, and zero line analysis.
    Single authoritative implementation.
    """
    # Calculate MACD components
    macd_indicator = ta.trend.MACD(data['close'], window_fast=fast, window_slow=slow, window_sign=signal)
    macd_line = macd_indicator.macd()
    signal_line = macd_indicator.macd_signal()
    histogram = macd_indicator.macd_diff()
    
    if macd_line is None or len(macd_line.dropna()) < 10:
        return {'error': 'MACD calculation failed'}
    
    # Current values
    current_macd = float(macd_line.iloc[-1])
    current_signal = float(signal_line.iloc[-1])
    current_histogram = float(histogram.iloc[-1])
    
    # Signal analysis
    if current_macd > current_signal:
        if current_macd > 0:
            signal_interpretation = 'strong_bullish'
        else:
            signal_interpretation = 'bullish'
    else:
        if current_macd < 0:
            signal_interpretation = 'strong_bearish'
        else:
            signal_interpretation = 'bearish'
    
    # Crossover detection
    crossovers = detect_crossovers(macd_line, signal_line)
    
    # Zero line crossings
    zero_crossings = []
    for i in range(1, len(macd_line)):
        if macd_line.iloc[i-1] <= 0 and macd_line.iloc[i] > 0:
            zero_crossings.append({
                'date': macd_line.index[i],
                'type': 'bullish_zero_cross',
                'value': float(macd_line.iloc[i])
            })
        elif macd_line.iloc[i-1] >= 0 and macd_line.iloc[i] < 0:
            zero_crossings.append({
                'date': macd_line.index[i],
                'type': 'bearish_zero_cross',
                'value': float(macd_line.iloc[i])
            })
    
    # Histogram analysis
    histogram_momentum = histogram.diff().iloc[-1] if len(histogram) > 1 else 0
    histogram_trend = 'increasing' if histogram_momentum > 0 else 'decreasing'
    
    # Generate trading signals
    trading_signals = []
    
    if len(crossovers) > 0:
        last_crossover = crossovers[-1]
        if last_crossover['type'] == 'bullish_crossover':
            trading_signals.append("MACD bullish crossover - momentum turning positive")
        else:
            trading_signals.append("MACD bearish crossover - momentum turning negative")
    
    if current_histogram > 0 and histogram_trend == 'increasing':
        trading_signals.append("MACD histogram expanding - strengthening bullish momentum")
    elif current_histogram < 0 and histogram_trend == 'decreasing':
        trading_signals.append("MACD histogram expanding - strengthening bearish momentum")
    
    if len(zero_crossings) > 0 and (data.index[-1] - zero_crossings[-1]['date']).days <= 5:
        if zero_crossings[-1]['type'] == 'bullish_zero_cross':
            trading_signals.append("Recent MACD zero line break - trend turning bullish")
        else:
            trading_signals.append("Recent MACD zero line break - trend turning bearish")
    
    return standardize_ta_response(
        function_name='calculate_macd',
        indicator_name='MACD',
        current_value=current_macd,
        signal=signal_interpretation,
        data={
            'macd_line': float(current_macd),
            'signal_line': float(current_signal),
            'histogram': float(current_histogram),
            'values': {
                'macd': macd_line.dropna().tail(50).tolist(),
                'signal': signal_line.dropna().tail(50).tolist(),
                'histogram': histogram.dropna().tail(50).tolist()
            },
            'crossovers': crossovers[-5:],
            'zero_crossings': zero_crossings[-3:],
            'histogram_analysis': {
                'momentum': float(histogram_momentum) if not pd.isna(histogram_momentum) else 0,
                'trend': histogram_trend,
                'strength': 'strong' if abs(current_histogram) > histogram.std() else 'moderate'
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals)
        },
        metadata={'fast': fast, 'slow': slow, 'signal': signal}
    )

# =============================================================================
# STOCHASTIC OSCILLATOR
# =============================================================================

@mcp_resilient(min_periods=14, required_columns=['high', 'low', 'close'])
def calculate_stochastic(data: pd.DataFrame, k_window: int = 14, d_window: int = 3, smooth_k: int = 3) -> Dict[str, Any]:
    """
    Calculate Stochastic Oscillator with crossovers and divergence analysis.
    Single authoritative implementation.
    """
    # Calculate Stochastic
    stoch = ta.momentum.StochasticOscillator(
        data['high'], data['low'], data['close'], 
        window=k_window, smooth_window=smooth_k
    )
    k_percent = stoch.stoch()
    d_percent = stoch.stoch_signal()
    
    if k_percent is None or len(k_percent.dropna()) < 10:
        return {'error': 'Stochastic calculation failed'}
    
    current_k = float(k_percent.iloc[-1])
    current_d = float(d_percent.iloc[-1])
    
    # Signal analysis
    if current_k > 80 and current_d > 80:
        signal = 'overbought'
        position = 'sell_zone'
    elif current_k < 20 and current_d < 20:
        signal = 'oversold'
        position = 'buy_zone'
    elif current_k > current_d:
        signal = 'bullish'
        position = 'bullish_momentum'
    else:
        signal = 'bearish'
        position = 'bearish_momentum'
    
    # Crossover detection
    crossovers = detect_crossovers(k_percent, d_percent)
    
    # Divergence analysis
    divergences = detect_divergences(data['close'], k_percent)
    
    # Generate trading signals
    trading_signals = []
    
    if signal == 'oversold' and len(crossovers) > 0 and crossovers[-1]['type'] == 'bullish_crossover':
        trading_signals.append("Stochastic oversold with bullish crossover - strong buy signal")
    
    if signal == 'overbought' and len(crossovers) > 0 and crossovers[-1]['type'] == 'bearish_crossover':
        trading_signals.append("Stochastic overbought with bearish crossover - strong sell signal")
    
    if len(divergences) > 0:
        latest_div = divergences[-1]
        if latest_div['type'] == 'bullish_divergence' and signal == 'oversold':
            trading_signals.append("Bullish divergence in oversold zone - reversal likely")
        elif latest_div['type'] == 'bearish_divergence' and signal == 'overbought':
            trading_signals.append("Bearish divergence in overbought zone - reversal likely")
    
    return standardize_ta_response(
        function_name='calculate_stochastic',
        indicator_name='Stochastic',
        current_value=current_k,
        signal=signal,
        data={
            'k_percent': float(current_k),
            'd_percent': float(current_d),
            'position': position,
            'values': {
                'k': k_percent.dropna().tail(50).tolist(),
                'd': d_percent.dropna().tail(50).tolist()
            },
            'crossovers': crossovers[-5:],
            'divergences': divergences[-3:],
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'levels': {
                'overbought': 80,
                'oversold': 20,
                'midline': 50
            }
        },
        metadata={
            'k_window': k_window,
            'd_window': d_window,
            'smooth_k': smooth_k
        }
    )

# =============================================================================
# WILLIAMS %R
# =============================================================================

@mcp_resilient(min_periods=14, required_columns=['high', 'low', 'close'])
def calculate_williams_r(data: pd.DataFrame, window: int = 14) -> Dict[str, Any]:
    """
    Calculate Williams %R oscillator with overbought/oversold analysis.
    """
    williams_r = safe_ta_calculation(ta.momentum.williams_r, data['high'], data['low'], data['close'], window)
    if williams_r is None:
        return {'error': 'Williams %R calculation failed'}
    
    current_wr = float(williams_r.iloc[-1])
    
    # Signal analysis (Williams %R is inverted: -20 to -100)
    if current_wr > -20:
        signal = 'overbought'
        position = 'sell_zone'
    elif current_wr < -80:
        signal = 'oversold' 
        position = 'buy_zone'
    else:
        signal = 'neutral'
        position = 'range_bound'
    
    # Momentum analysis
    wr_momentum = williams_r.diff(5).iloc[-1] if len(williams_r) > 5 else 0
    
    # Generate trading signals
    trading_signals = []
    if signal == 'oversold' and wr_momentum > 0:
        trading_signals.append("Williams %R oversold with upward momentum - buy signal")
    if signal == 'overbought' and wr_momentum < 0:
        trading_signals.append("Williams %R overbought with downward momentum - sell signal")
    
    return standardize_ta_response(
        function_name='calculate_williams_r',
        indicator_name='Williams %R',
        current_value=current_wr,
        signal=signal,
        data={
            'position': position,
            'values': williams_r.dropna().tail(50).tolist(),
            'momentum': float(wr_momentum) if not pd.isna(wr_momentum) else 0,
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'levels': {
                'overbought': -20,
                'oversold': -80,
                'midline': -50
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# AWESOME OSCILLATOR
# =============================================================================

@mcp_resilient(min_periods=34, required_columns=['high', 'low'])
def calculate_awesome_oscillator(data: pd.DataFrame, short_window: int = 5, long_window: int = 34) -> Dict[str, Any]:
    """
    Calculate Awesome Oscillator with momentum and saucer signal analysis.
    """
    ao = safe_ta_calculation(ta.momentum.awesome_oscillator_indicator, 
                            data['high'], data['low'], window1=short_window, window2=long_window)
    if ao is None:
        return {'error': 'Awesome Oscillator calculation failed'}
    
    current_ao = float(ao.iloc[-1])
    
    # Signal analysis
    if current_ao > 0:
        signal = 'bullish'
        position = 'above_zero'
    else:
        signal = 'bearish'
        position = 'below_zero'
    
    # Zero line crossings
    zero_crossings = []
    for i in range(1, len(ao)):
        if ao.iloc[i-1] <= 0 and ao.iloc[i] > 0:
            zero_crossings.append({
                'date': ao.index[i],
                'type': 'bullish_zero_cross',
                'value': float(ao.iloc[i])
            })
        elif ao.iloc[i-1] >= 0 and ao.iloc[i] < 0:
            zero_crossings.append({
                'date': ao.index[i],
                'type': 'bearish_zero_cross',
                'value': float(ao.iloc[i])
            })
    
    # Generate trading signals
    trading_signals = []
    ao_momentum = ao.diff().iloc[-1]
    
    if current_ao > 0 and ao_momentum > 0:
        trading_signals.append("AO positive and rising - bullish momentum strengthening")
    elif current_ao < 0 and ao_momentum < 0:
        trading_signals.append("AO negative and falling - bearish momentum strengthening")
    
    if len(zero_crossings) > 0 and (data.index[-1] - zero_crossings[-1]['date']).days <= 3:
        if zero_crossings[-1]['type'] == 'bullish_zero_cross':
            trading_signals.append("Recent AO zero line break - bullish signal")
        else:
            trading_signals.append("Recent AO zero line break - bearish signal")
    
    return standardize_ta_response(
        function_name='calculate_awesome_oscillator',
        indicator_name='Awesome Oscillator',
        current_value=current_ao,
        signal=signal,
        data={
            'position': position,
            'values': ao.dropna().tail(50).tolist(),
            'momentum': float(ao_momentum) if not pd.isna(ao_momentum) else 0,
            'zero_crossings': zero_crossings[-5:],
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals)
        },
        metadata={'short_window': short_window, 'long_window': long_window}
    )

# =============================================================================
# ULTIMATE OSCILLATOR
# =============================================================================

@mcp_resilient(min_periods=28, required_columns=['high', 'low', 'close'])
def calculate_ultimate_oscillator(data: pd.DataFrame, short: int = 7, medium: int = 14, long: int = 28) -> Dict[str, Any]:
    """
    Calculate Ultimate Oscillator with multi-timeframe momentum analysis.
    """
    uo = safe_ta_calculation(ta.momentum.ultimate_oscillator, 
                            data['high'], data['low'], data['close'], 
                            window1=short, window2=medium, window3=long)
    if uo is None:
        return {'error': 'Ultimate Oscillator calculation failed'}
    
    current_uo = float(uo.iloc[-1])
    
    # Signal analysis
    if current_uo > 70:
        signal = 'overbought'
        position = 'sell_zone'
    elif current_uo < 30:
        signal = 'oversold'
        position = 'buy_zone'
    else:
        signal = 'neutral'
        position = 'range_bound'
    
    # Momentum analysis
    uo_momentum = uo.diff(5).iloc[-1] if len(uo) > 5 else 0
    
    # Generate trading signals
    trading_signals = []
    if signal == 'oversold' and uo_momentum > 0:
        trading_signals.append("Ultimate Oscillator oversold with upward momentum - buy signal")
    if signal == 'overbought' and uo_momentum < 0:
        trading_signals.append("Ultimate Oscillator overbought with downward momentum - sell signal")
    
    return standardize_ta_response(
        function_name='calculate_ultimate_oscillator',
        indicator_name='Ultimate Oscillator',
        current_value=current_uo,
        signal=signal,
        data={
            'position': position,
            'values': uo.dropna().tail(50).tolist(),
            'momentum': float(uo_momentum) if not pd.isna(uo_momentum) else 0,
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'levels': {
                'overbought': 70,
                'oversold': 30,
                'midline': 50
            }
        },
        metadata={'short': short, 'medium': medium, 'long': long}
    )

# =============================================================================
# RATE OF CHANGE (ROC)
# =============================================================================

@mcp_resilient(min_periods=10, required_columns=['close'])
def calculate_rate_of_change(data: pd.DataFrame, window: int = 10) -> Dict[str, Any]:
    """
    Calculate Rate of Change momentum indicator.
    """
    roc = safe_ta_calculation(ta.momentum.roc, data['close'], window=window)
    if roc is None:
        return {'error': 'ROC calculation failed'}
    
    current_roc = float(roc.iloc[-1])
    
    # Signal analysis
    if current_roc > 5:
        signal = 'strong_bullish'
        position = 'strong_uptrend'
    elif current_roc > 0:
        signal = 'bullish'
        position = 'uptrend'
    elif current_roc < -5:
        signal = 'strong_bearish'
        position = 'strong_downtrend'
    elif current_roc < 0:
        signal = 'bearish'
        position = 'downtrend'
    else:
        signal = 'neutral'
        position = 'sideways'
    
    # Zero line crossings
    zero_crossings = []
    for i in range(1, len(roc)):
        if roc.iloc[i-1] <= 0 and roc.iloc[i] > 0:
            zero_crossings.append({
                'date': roc.index[i],
                'type': 'bullish_momentum',
                'value': float(roc.iloc[i])
            })
        elif roc.iloc[i-1] >= 0 and roc.iloc[i] < 0:
            zero_crossings.append({
                'date': roc.index[i],
                'type': 'bearish_momentum',
                'value': float(roc.iloc[i])
            })
    
    # Generate trading signals
    trading_signals = []
    roc_momentum = roc.diff().iloc[-1]
    
    if current_roc > 0 and roc_momentum > 0:
        trading_signals.append("ROC positive and accelerating - strong bullish momentum")
    elif current_roc < 0 and roc_momentum < 0:
        trading_signals.append("ROC negative and accelerating - strong bearish momentum")
    
    return standardize_ta_response(
        function_name='calculate_rate_of_change',
        indicator_name='Rate of Change',
        current_value=current_roc,
        signal=signal,
        data={
            'position': position,
            'values': roc.dropna().tail(50).tolist(),
            'momentum': float(roc_momentum) if not pd.isna(roc_momentum) else 0,
            'zero_crossings': zero_crossings[-5:],
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'statistics': {
                'average': float(roc.mean()),
                'volatility': float(roc.std()),
                'maximum': float(roc.max()),
                'minimum': float(roc.min())
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# MOMENTUM MODULE EXPORTS
# =============================================================================

__all__ = [
    'calculate_rsi',
    'calculate_macd', 
    'calculate_stochastic',
    'calculate_williams_r',
    'calculate_awesome_oscillator',
    'calculate_ultimate_oscillator',
    'calculate_rate_of_change'
]