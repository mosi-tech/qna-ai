#!/usr/bin/env python3
"""
Trend Indicators - Single source of truth for all trend-based technical indicators.
Includes ADX, CCI, Aroon, Parabolic SAR, and trend analysis functions.
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Any, Optional, Union

from .framework import (
    mcp_resilient, standardize_ta_response, detect_crossovers,
    calculate_signal_strength, safe_ta_calculation
)

# =============================================================================
# ADX (AVERAGE DIRECTIONAL INDEX)
# =============================================================================

@mcp_resilient(min_periods=14, required_columns=['high', 'low', 'close'])
def calculate_adx(data: pd.DataFrame, window: int = 14) -> Dict[str, Any]:
    """
    Calculate ADX with comprehensive trend strength analysis and directional indicators.
    Single authoritative implementation.
    """
    # Calculate ADX components
    adx_indicator = ta.trend.ADXIndicator(data['high'], data['low'], data['close'], window=window)
    adx = adx_indicator.adx()
    di_plus = adx_indicator.adx_pos()
    di_minus = adx_indicator.adx_neg()
    
    if adx is None or len(adx.dropna()) < 10:
        return {'error': 'ADX calculation failed'}
    
    current_adx = float(adx.iloc[-1])
    current_di_plus = float(di_plus.iloc[-1])
    current_di_minus = float(di_minus.iloc[-1])
    
    # Trend strength classification (Wilder's standards)
    if current_adx > 50:
        trend_strength = 'very_strong'
        strength_desc = 'Extremely strong trend'
    elif current_adx > 25:
        trend_strength = 'strong' 
        strength_desc = 'Strong trending market'
    elif current_adx > 20:
        trend_strength = 'moderate'
        strength_desc = 'Moderate trend'
    else:
        trend_strength = 'weak'
        strength_desc = 'Weak or ranging market'
    
    # Directional bias
    if current_di_plus > current_di_minus:
        directional_bias = 'bullish'
        direction_desc = 'Upward directional movement dominant'
    elif current_di_minus > current_di_plus:
        directional_bias = 'bearish'
        direction_desc = 'Downward directional movement dominant'
    else:
        directional_bias = 'neutral'
        direction_desc = 'Balanced directional movement'
    
    # DI crossover analysis
    di_crossovers = detect_crossovers(di_plus, di_minus)
    
    # ADX momentum (rising/falling ADX)
    adx_momentum = adx.diff(5).iloc[-1] if len(adx) > 5 else 0
    adx_trending = 'rising' if adx_momentum > 0 else 'falling' if adx_momentum < 0 else 'flat'
    
    # Generate Wilder's trading signals
    trading_signals = []
    
    # Strong trend continuation signals
    if current_adx > 25 and adx_momentum > 0:
        if directional_bias == 'bullish':
            trading_signals.append("Strong uptrend with rising ADX - trend continuation likely")
        else:
            trading_signals.append("Strong downtrend with rising ADX - trend continuation likely")
    
    # Trend exhaustion signals
    elif current_adx > 40 and adx_momentum < -1:
        trading_signals.append("High ADX with falling momentum - trend may be exhausting")
    
    # Range-bound market signals
    elif current_adx < 20:
        trading_signals.append("Low ADX indicates ranging market - avoid trend-following strategies")
    
    # DI crossover signals
    if len(di_crossovers) > 0:
        latest_crossover = di_crossovers[-1]
        days_since = (data.index[-1] - latest_crossover['date']).days
        
        if days_since <= 5:  # Recent crossover
            if latest_crossover['type'] == 'bullish_crossover' and current_adx > 20:
                trading_signals.append("Recent +DI crossing above -DI with decent ADX - bullish signal")
            elif latest_crossover['type'] == 'bearish_crossover' and current_adx > 20:
                trading_signals.append("Recent -DI crossing above +DI with decent ADX - bearish signal")
    
    # DI spread analysis
    di_spread = abs(current_di_plus - current_di_minus)
    spread_strength = 'wide' if di_spread > 10 else 'narrow'
    
    return standardize_ta_response(
        function_name='calculate_adx',
        indicator_name='ADX',
        current_value=current_adx,
        signal=trend_strength,
        data={
            'trend_strength': trend_strength,
            'strength_description': strength_desc,
            'directional_bias': directional_bias,
            'direction_description': direction_desc,
            'di_plus': float(current_di_plus),
            'di_minus': float(current_di_minus),
            'di_spread': float(di_spread),
            'spread_strength': spread_strength,
            'values': {
                'adx': adx.dropna().tail(50).tolist(),
                'di_plus': di_plus.dropna().tail(50).tolist(),
                'di_minus': di_minus.dropna().tail(50).tolist()
            },
            'adx_momentum': float(adx_momentum) if not pd.isna(adx_momentum) else 0,
            'adx_trending': adx_trending,
            'di_crossovers': di_crossovers[-5:],
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'wilder_levels': {
                'very_strong': 50,
                'strong': 25,
                'moderate': 20,
                'weak': 20
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# CCI (COMMODITY CHANNEL INDEX)
# =============================================================================

@mcp_resilient(min_periods=20, required_columns=['high', 'low', 'close'])
def calculate_cci(data: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
    """
    Calculate Commodity Channel Index with overbought/oversold and trend analysis.
    """
    cci = safe_ta_calculation(ta.trend.cci, data['high'], data['low'], data['close'], window=window)
    if cci is None:
        return {'error': 'CCI calculation failed'}
    
    current_cci = float(cci.iloc[-1])
    
    # Signal analysis using Lambert's levels
    if current_cci > 100:
        signal = 'overbought'
        position = 'strong_uptrend'
    elif current_cci < -100:
        signal = 'oversold'
        position = 'strong_downtrend'
    elif current_cci > 0:
        signal = 'bullish'
        position = 'upward_momentum'
    else:
        signal = 'bearish'
        position = 'downward_momentum'
    
    # Zero line crossings
    zero_crossings = []
    for i in range(1, len(cci)):
        if cci.iloc[i-1] <= 0 and cci.iloc[i] > 0:
            zero_crossings.append({
                'date': cci.index[i],
                'type': 'bullish_momentum',
                'value': float(cci.iloc[i])
            })
        elif cci.iloc[i-1] >= 0 and cci.iloc[i] < 0:
            zero_crossings.append({
                'date': cci.index[i],
                'type': 'bearish_momentum',
                'value': float(cci.iloc[i])
            })
    
    # Extreme level analysis
    extreme_readings = []
    for i, value in enumerate(cci):
        if abs(value) > 200:  # Extreme readings
            extreme_readings.append({
                'date': cci.index[i],
                'value': float(value),
                'type': 'extreme_overbought' if value > 200 else 'extreme_oversold'
            })
    
    # Generate trading signals
    trading_signals = []
    cci_momentum = cci.diff(3).iloc[-1] if len(cci) > 3 else 0
    
    if current_cci > 100 and cci_momentum < 0:
        trading_signals.append("CCI overbought with negative momentum - reversal signal")
    elif current_cci < -100 and cci_momentum > 0:
        trading_signals.append("CCI oversold with positive momentum - reversal signal")
    
    if len(zero_crossings) > 0 and (data.index[-1] - zero_crossings[-1]['date']).days <= 3:
        if zero_crossings[-1]['type'] == 'bullish_momentum':
            trading_signals.append("Recent CCI zero line break - bullish momentum")
        else:
            trading_signals.append("Recent CCI zero line break - bearish momentum")
    
    if len(extreme_readings) > 0 and (data.index[-1] - extreme_readings[-1]['date']).days <= 5:
        if extreme_readings[-1]['type'] == 'extreme_overbought':
            trading_signals.append("Recent extreme CCI reading - strong reversal potential")
        else:
            trading_signals.append("Recent extreme CCI reading - strong reversal potential")
    
    return standardize_ta_response(
        function_name='calculate_cci',
        indicator_name='CCI',
        current_value=current_cci,
        signal=signal,
        data={
            'position': position,
            'values': cci.dropna().tail(50).tolist(),
            'momentum': float(cci_momentum) if not pd.isna(cci_momentum) else 0,
            'zero_crossings': zero_crossings[-5:],
            'extreme_readings': extreme_readings[-5:],
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'lambert_levels': {
                'extreme_overbought': 200,
                'overbought': 100,
                'zero_line': 0,
                'oversold': -100,
                'extreme_oversold': -200
            },
            'statistics': {
                'average': float(cci.mean()),
                'volatility': float(cci.std()),
                'maximum': float(cci.max()),
                'minimum': float(cci.min())
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# AROON INDICATOR
# =============================================================================

@mcp_resilient(min_periods=25, required_columns=['high', 'low'])
def calculate_aroon(data: pd.DataFrame, window: int = 25) -> Dict[str, Any]:
    """
    Calculate Aroon indicators with trend identification and crossover analysis.
    """
    aroon = ta.trend.AroonIndicator(data['high'], data['low'], window=window)
    aroon_up = aroon.aroon_up()
    aroon_down = aroon.aroon_down()
    
    if aroon_up is None or len(aroon_up.dropna()) < 10:
        return {'error': 'Aroon calculation failed'}
    
    current_aroon_up = float(aroon_up.iloc[-1])
    current_aroon_down = float(aroon_down.iloc[-1])
    
    # Signal analysis
    if current_aroon_up > 70 and current_aroon_down < 30:
        signal = 'strong_uptrend'
        position = 'bullish_trend'
    elif current_aroon_down > 70 and current_aroon_up < 30:
        signal = 'strong_downtrend'
        position = 'bearish_trend'
    elif current_aroon_up > 50 and current_aroon_up > current_aroon_down:
        signal = 'uptrend'
        position = 'bullish_momentum'
    elif current_aroon_down > 50 and current_aroon_down > current_aroon_up:
        signal = 'downtrend'
        position = 'bearish_momentum'
    else:
        signal = 'consolidation'
        position = 'range_bound'
    
    # Crossover detection
    crossovers = detect_crossovers(aroon_up, aroon_down)
    
    # Parallel movement (both high or both low)
    both_high = current_aroon_up > 70 and current_aroon_down > 70
    both_low = current_aroon_up < 30 and current_aroon_down < 30
    
    # Generate trading signals
    trading_signals = []
    
    if len(crossovers) > 0:
        latest_crossover = crossovers[-1]
        days_since = (data.index[-1] - latest_crossover['date']).days
        
        if days_since <= 3:
            if latest_crossover['type'] == 'bullish_crossover':
                trading_signals.append("Aroon Up crossing above Aroon Down - new uptrend beginning")
            else:
                trading_signals.append("Aroon Down crossing above Aroon Up - new downtrend beginning")
    
    if signal == 'strong_uptrend':
        trading_signals.append("Strong Aroon uptrend signal - bullish momentum")
    elif signal == 'strong_downtrend':
        trading_signals.append("Strong Aroon downtrend signal - bearish momentum")
    
    if both_high:
        trading_signals.append("Both Aroon indicators high - market consolidation likely")
    elif both_low:
        trading_signals.append("Both Aroon indicators low - weak trend, consolidation")
    
    # Trend strength
    trend_strength = abs(current_aroon_up - current_aroon_down)
    strength_category = 'strong' if trend_strength > 40 else 'moderate' if trend_strength > 20 else 'weak'
    
    return standardize_ta_response(
        function_name='calculate_aroon',
        indicator_name='Aroon',
        current_value=(current_aroon_up + current_aroon_down) / 2,  # Average for current_value
        signal=signal,
        data={
            'aroon_up': float(current_aroon_up),
            'aroon_down': float(current_aroon_down),
            'position': position,
            'values': {
                'aroon_up': aroon_up.dropna().tail(50).tolist(),
                'aroon_down': aroon_down.dropna().tail(50).tolist()
            },
            'crossovers': crossovers[-5:],
            'trend_strength': float(trend_strength),
            'strength_category': strength_category,
            'parallel_movement': {
                'both_high': both_high,
                'both_low': both_low
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'thresholds': {
                'strong_trend': 70,
                'weak_trend': 30,
                'midline': 50
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# PARABOLIC SAR
# =============================================================================

@mcp_resilient(min_periods=10, required_columns=['high', 'low', 'close'])
def calculate_parabolic_sar(data: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> Dict[str, Any]:
    """
    Calculate Parabolic SAR with trend following and reversal signals.
    """
    sar = safe_ta_calculation(ta.trend.PSARIndicator, data['high'], data['low'], data['close'], 
                             step=step, max_step=max_step)
    if sar is None:
        return {'error': 'Parabolic SAR calculation failed'}
    
    psar_values = sar.psar()
    current_sar = float(psar_values.iloc[-1])
    current_price = float(data['close'].iloc[-1])
    
    # Signal analysis
    if current_price > current_sar:
        signal = 'bullish'
        position = 'uptrend'
        trend_direction = 'up'
    else:
        signal = 'bearish'
        position = 'downtrend'
        trend_direction = 'down'
    
    # SAR reversal points
    reversals = []
    for i in range(1, len(psar_values)):
        prev_price = data['close'].iloc[i-1]
        curr_price = data['close'].iloc[i]
        prev_sar = psar_values.iloc[i-1]
        curr_sar = psar_values.iloc[i]
        
        # Bullish reversal (price crosses above SAR)
        if prev_price <= prev_sar and curr_price > curr_sar:
            reversals.append({
                'date': data.index[i],
                'type': 'bullish_reversal',
                'price': float(curr_price),
                'sar': float(curr_sar)
            })
        
        # Bearish reversal (price crosses below SAR)
        elif prev_price >= prev_sar and curr_price < curr_sar:
            reversals.append({
                'date': data.index[i],
                'type': 'bearish_reversal',
                'price': float(curr_price),
                'sar': float(curr_sar)
            })
    
    # Distance analysis
    sar_distance = abs(current_price - current_sar)
    distance_percent = (sar_distance / current_price) * 100
    
    # Generate trading signals
    trading_signals = []
    
    if len(reversals) > 0:
        latest_reversal = reversals[-1]
        days_since = (data.index[-1] - latest_reversal['date']).days
        
        if days_since <= 2:  # Recent reversal
            if latest_reversal['type'] == 'bullish_reversal':
                trading_signals.append("Recent SAR bullish reversal - new uptrend signal")
            else:
                trading_signals.append("Recent SAR bearish reversal - new downtrend signal")
    
    if signal == 'bullish' and distance_percent > 2:
        trading_signals.append("Price well above SAR - strong uptrend continuation")
    elif signal == 'bearish' and distance_percent > 2:
        trading_signals.append("Price well below SAR - strong downtrend continuation")
    
    if distance_percent < 0.5:
        trading_signals.append("Price close to SAR - potential trend reversal zone")
    
    return standardize_ta_response(
        function_name='calculate_parabolic_sar',
        indicator_name='Parabolic SAR',
        current_value=current_sar,
        signal=signal,
        data={
            'position': position,
            'trend_direction': trend_direction,
            'current_price': float(current_price),
            'values': psar_values.dropna().tail(50).tolist(),
            'distance': float(sar_distance),
            'distance_percent': float(distance_percent),
            'reversals': reversals[-10:],  # Last 10 reversals
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'acceleration_factor': {
                'step': step,
                'max_step': max_step
            }
        },
        metadata={'step': step, 'max_step': max_step}
    )

# =============================================================================
# TREND MODULE EXPORTS
# =============================================================================

__all__ = [
    'calculate_adx',
    'calculate_cci',
    'calculate_aroon',
    'calculate_parabolic_sar'
]