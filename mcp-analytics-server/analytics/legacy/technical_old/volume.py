#!/usr/bin/env python3
"""
Volume Indicators - Single source of truth for all volume-based technical indicators.
Includes OBV, MFI, A/D Line, Chaikin Money Flow, and volume analysis.
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Any, Optional, Union

from .framework import (
    mcp_resilient, standardize_ta_response, detect_divergences,
    calculate_signal_strength, safe_ta_calculation
)

# =============================================================================
# ON-BALANCE VOLUME (OBV)
# =============================================================================

@mcp_resilient(min_periods=1, required_columns=['close', 'volume'])
def calculate_obv(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate On-Balance Volume with comprehensive trend and divergence analysis.
    Single authoritative implementation.
    """
    obv = safe_ta_calculation(ta.volume.on_balance_volume, data['close'], data['volume'])
    if obv is None:
        return {'error': 'OBV calculation failed'}
    
    current_obv = float(obv.iloc[-1])
    current_price = float(data['close'].iloc[-1])
    
    # OBV trend analysis using moving averages
    obv_sma_10 = obv.rolling(window=10).mean()
    obv_sma_20 = obv.rolling(window=20).mean()
    obv_sma_50 = obv.rolling(window=50).mean() if len(obv) >= 50 else obv.rolling(window=len(obv)//2).mean()
    
    # Current position vs moving averages
    above_sma_10 = current_obv > obv_sma_10.iloc[-1] if not pd.isna(obv_sma_10.iloc[-1]) else False
    above_sma_20 = current_obv > obv_sma_20.iloc[-1] if not pd.isna(obv_sma_20.iloc[-1]) else False
    above_sma_50 = current_obv > obv_sma_50.iloc[-1] if not pd.isna(obv_sma_50.iloc[-1]) else False
    
    # OBV momentum analysis
    obv_momentum_short = obv.diff(5).iloc[-1] if len(obv) > 5 else 0
    obv_momentum_long = obv.diff(20).iloc[-1] if len(obv) > 20 else 0
    
    # OBV trend classification
    if above_sma_10 and above_sma_20 and above_sma_50:
        obv_trend = 'strong_accumulation'
        signal = 'bullish'
    elif not above_sma_10 and not above_sma_20 and not above_sma_50:
        obv_trend = 'strong_distribution'
        signal = 'bearish'
    elif above_sma_10 and above_sma_20:
        obv_trend = 'accumulation'
        signal = 'bullish'
    elif not above_sma_10 and not above_sma_20:
        obv_trend = 'distribution'
        signal = 'bearish'
    else:
        obv_trend = 'neutral'
        signal = 'neutral'
    
    # Price-OBV divergence analysis
    divergences = detect_divergences(data['close'], obv, window=20)
    
    # Volume trend analysis (up vs down volume days)
    up_volume_days = 0
    down_volume_days = 0
    total_up_volume = 0
    total_down_volume = 0
    
    for i in range(1, len(data)):
        price_change = data['close'].iloc[i] - data['close'].iloc[i-1]
        volume = data['volume'].iloc[i]
        
        if price_change > 0:
            up_volume_days += 1
            total_up_volume += volume
        elif price_change < 0:
            down_volume_days += 1
            total_down_volume += volume
    
    # Volume ratio analysis
    if total_down_volume > 0:
        volume_ratio = total_up_volume / total_down_volume
        volume_bias = 'bullish' if volume_ratio > 1.2 else 'bearish' if volume_ratio < 0.8 else 'neutral'
    else:
        volume_ratio = float('inf')
        volume_bias = 'bullish'
    
    # Generate trading signals
    trading_signals = []
    
    # Divergence signals
    if len(divergences) > 0:
        latest_div = divergences[-1]
        days_since = (data.index[-1] - latest_div['date']).days
        
        if days_since <= 10:
            if latest_div['type'] == 'bullish_divergence':
                trading_signals.append("Bullish OBV divergence - accumulation despite price weakness")
            else:
                trading_signals.append("Bearish OBV divergence - distribution despite price strength")
    
    # Momentum signals
    if obv_momentum_short > 0 and obv_momentum_long > 0:
        trading_signals.append("OBV showing positive momentum across timeframes - accumulation phase")
    elif obv_momentum_short < 0 and obv_momentum_long < 0:
        trading_signals.append("OBV showing negative momentum across timeframes - distribution phase")
    
    # Trend confirmation signals
    if signal == 'bullish' and data['close'].iloc[-1] > data['close'].iloc[-20]:
        trading_signals.append("OBV confirming price uptrend - healthy buying pressure")
    elif signal == 'bearish' and data['close'].iloc[-1] < data['close'].iloc[-20]:
        trading_signals.append("OBV confirming price downtrend - consistent selling pressure")
    
    # Volume bias signals
    if volume_bias == 'bullish' and signal == 'bullish':
        trading_signals.append("Volume bias supports OBV trend - strong accumulation pattern")
    elif volume_bias == 'bearish' and signal == 'bearish':
        trading_signals.append("Volume bias supports OBV trend - strong distribution pattern")
    
    return standardize_ta_response(
        function_name='calculate_obv',
        indicator_name='OBV',
        current_value=current_obv,
        signal=signal,
        data={
            'trend': obv_trend,
            'values': obv.dropna().tail(50).tolist(),
            'moving_averages': {
                'sma_10': float(obv_sma_10.iloc[-1]) if not pd.isna(obv_sma_10.iloc[-1]) else None,
                'sma_20': float(obv_sma_20.iloc[-1]) if not pd.isna(obv_sma_20.iloc[-1]) else None,
                'sma_50': float(obv_sma_50.iloc[-1]) if not pd.isna(obv_sma_50.iloc[-1]) else None
            },
            'momentum': {
                'short_term': float(obv_momentum_short) if not pd.isna(obv_momentum_short) else 0,
                'long_term': float(obv_momentum_long) if not pd.isna(obv_momentum_long) else 0
            },
            'divergences': divergences[-5:],
            'volume_analysis': {
                'up_volume_days': up_volume_days,
                'down_volume_days': down_volume_days,
                'volume_ratio': float(volume_ratio) if volume_ratio != float('inf') else 'infinite',
                'volume_bias': volume_bias,
                'net_volume_pressure': up_volume_days - down_volume_days
            },
            'position_vs_mas': {
                'above_sma_10': above_sma_10,
                'above_sma_20': above_sma_20,
                'above_sma_50': above_sma_50
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals)
        }
    )

# =============================================================================
# MONEY FLOW INDEX (MFI)
# =============================================================================

@mcp_resilient(min_periods=14, required_columns=['high', 'low', 'close', 'volume'])
def calculate_mfi(data: pd.DataFrame, window: int = 14) -> Dict[str, Any]:
    """
    Calculate Money Flow Index with comprehensive volume-price analysis.
    Single authoritative implementation.
    """
    mfi = safe_ta_calculation(ta.volume.money_flow_index, 
                             data['high'], data['low'], data['close'], data['volume'], window=window)
    if mfi is None:
        return {'error': 'MFI calculation failed'}
    
    current_mfi = float(mfi.iloc[-1])
    
    # MFI signal analysis
    if current_mfi > 80:
        signal = 'extreme_overbought'
        position = 'strong_selling_pressure_expected'
    elif current_mfi > 70:
        signal = 'overbought'
        position = 'selling_pressure_likely'
    elif current_mfi < 20:
        signal = 'extreme_oversold'
        position = 'strong_buying_pressure_expected'
    elif current_mfi < 30:
        signal = 'oversold'
        position = 'buying_pressure_likely'
    elif current_mfi > 50:
        signal = 'bullish'
        position = 'buying_pressure_dominant'
    else:
        signal = 'bearish'
        position = 'selling_pressure_dominant'
    
    # MFI momentum analysis
    mfi_momentum = mfi.diff(5).iloc[-1] if len(mfi) > 5 else 0
    mfi_trend = 'rising' if mfi_momentum > 0 else 'falling' if mfi_momentum < 0 else 'flat'
    
    # MFI divergence analysis
    divergences = detect_divergences(data['close'], mfi, window=15)
    
    # Money flow calculation (for deeper analysis)
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    money_flow = typical_price * data['volume']
    
    # Positive and negative money flow
    positive_flow = []
    negative_flow = []
    
    for i in range(1, len(typical_price)):
        if typical_price.iloc[i] > typical_price.iloc[i-1]:
            positive_flow.append(money_flow.iloc[i])
            negative_flow.append(0)
        elif typical_price.iloc[i] < typical_price.iloc[i-1]:
            positive_flow.append(0)
            negative_flow.append(money_flow.iloc[i])
        else:
            positive_flow.append(0)
            negative_flow.append(0)
    
    # Recent money flow analysis (last window periods)
    recent_positive_flow = sum(positive_flow[-window:]) if len(positive_flow) >= window else sum(positive_flow)
    recent_negative_flow = sum(negative_flow[-window:]) if len(negative_flow) >= window else sum(negative_flow)
    
    if recent_negative_flow > 0:
        money_flow_ratio = recent_positive_flow / recent_negative_flow
        flow_bias = 'strong_bullish' if money_flow_ratio > 2 else 'bullish' if money_flow_ratio > 1.5 else 'bearish' if money_flow_ratio < 0.5 else 'neutral'
    else:
        money_flow_ratio = float('inf')
        flow_bias = 'strong_bullish'
    
    # MFI oscillations (for overbought/oversold persistence)
    overbought_periods = (mfi > 70).sum()
    oversold_periods = (mfi < 30).sum()
    
    # Generate trading signals
    trading_signals = []
    
    # Overbought/Oversold with momentum signals
    if signal in ['overbought', 'extreme_overbought'] and mfi_momentum < 0:
        trading_signals.append("MFI overbought with declining momentum - selling opportunity")
    
    if signal in ['oversold', 'extreme_oversold'] and mfi_momentum > 0:
        trading_signals.append("MFI oversold with rising momentum - buying opportunity")
    
    # Divergence signals
    if len(divergences) > 0:
        latest_div = divergences[-1]
        days_since = (data.index[-1] - latest_div['date']).days
        
        if days_since <= 10:
            if latest_div['type'] == 'bullish_divergence' and signal in ['oversold', 'extreme_oversold']:
                trading_signals.append("Bullish MFI divergence in oversold zone - strong reversal signal")
            elif latest_div['type'] == 'bearish_divergence' and signal in ['overbought', 'extreme_overbought']:
                trading_signals.append("Bearish MFI divergence in overbought zone - strong reversal signal")
    
    # Money flow ratio signals
    if flow_bias == 'strong_bullish' and signal in ['bullish', 'overbought']:
        trading_signals.append("Strong positive money flow supporting upward momentum")
    elif flow_bias == 'bearish' and signal in ['bearish', 'oversold']:
        trading_signals.append("Negative money flow confirming downward pressure")
    
    # Extreme readings
    if current_mfi > 90:
        trading_signals.append("Extreme MFI reading - major reversal potential")
    elif current_mfi < 10:
        trading_signals.append("Extreme MFI reading - major reversal potential")
    
    return standardize_ta_response(
        function_name='calculate_mfi',
        indicator_name='MFI',
        current_value=current_mfi,
        signal=signal,
        data={
            'position': position,
            'values': mfi.dropna().tail(50).tolist(),
            'momentum': float(mfi_momentum) if not pd.isna(mfi_momentum) else 0,
            'trend': mfi_trend,
            'divergences': divergences[-5:],
            'money_flow_analysis': {
                'positive_flow_recent': float(recent_positive_flow),
                'negative_flow_recent': float(recent_negative_flow),
                'flow_ratio': float(money_flow_ratio) if money_flow_ratio != float('inf') else 'infinite',
                'flow_bias': flow_bias,
                'net_flow': float(recent_positive_flow - recent_negative_flow)
            },
            'overbought_oversold_stats': {
                'periods_overbought': int(overbought_periods),
                'periods_oversold': int(oversold_periods),
                'current_extreme': current_mfi > 80 or current_mfi < 20
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'levels': {
                'extreme_overbought': 80,
                'overbought': 70,
                'midline': 50,
                'oversold': 30,
                'extreme_oversold': 20
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# ACCUMULATION/DISTRIBUTION LINE
# =============================================================================

@mcp_resilient(min_periods=1, required_columns=['high', 'low', 'close', 'volume'])
def calculate_ad_line(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate Accumulation/Distribution Line with volume-price analysis.
    """
    ad_line = safe_ta_calculation(ta.volume.acc_dist_index, 
                                 data['high'], data['low'], data['close'], data['volume'])
    if ad_line is None:
        return {'error': 'A/D Line calculation failed'}
    
    current_ad = float(ad_line.iloc[-1])
    
    # A/D Line trend analysis
    ad_sma_20 = ad_line.rolling(window=20).mean()
    ad_momentum = ad_line.diff(10).iloc[-1] if len(ad_line) > 10 else 0
    
    # Signal analysis
    if current_ad > ad_sma_20.iloc[-1] and ad_momentum > 0:
        signal = 'strong_accumulation'
        position = 'bullish'
    elif current_ad < ad_sma_20.iloc[-1] and ad_momentum < 0:
        signal = 'strong_distribution'
        position = 'bearish'
    elif ad_momentum > 0:
        signal = 'accumulation'
        position = 'bullish'
    elif ad_momentum < 0:
        signal = 'distribution'
        position = 'bearish'
    else:
        signal = 'neutral'
        position = 'sideways'
    
    # Divergence analysis
    divergences = detect_divergences(data['close'], ad_line)
    
    # Volume flow analysis
    close_location_value = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])
    clv_average = close_location_value.mean()
    
    # Generate trading signals
    trading_signals = []
    
    if signal == 'strong_accumulation':
        trading_signals.append("A/D Line showing strong accumulation - institutional buying")
    elif signal == 'strong_distribution':
        trading_signals.append("A/D Line showing strong distribution - institutional selling")
    
    if len(divergences) > 0:
        latest_div = divergences[-1]
        if (data.index[-1] - latest_div['date']).days <= 15:
            if latest_div['type'] == 'bullish_divergence':
                trading_signals.append("Bullish A/D Line divergence - accumulation on weakness")
            else:
                trading_signals.append("Bearish A/D Line divergence - distribution on strength")
    
    return standardize_ta_response(
        function_name='calculate_ad_line',
        indicator_name='A/D Line',
        current_value=current_ad,
        signal=signal,
        data={
            'position': position,
            'values': ad_line.dropna().tail(50).tolist(),
            'momentum': float(ad_momentum) if not pd.isna(ad_momentum) else 0,
            'sma_20': float(ad_sma_20.iloc[-1]) if not pd.isna(ad_sma_20.iloc[-1]) else None,
            'divergences': divergences[-5:],
            'volume_analysis': {
                'close_location_value_avg': float(clv_average),
                'accumulation_strength': 'high' if clv_average > 0.1 else 'low' if clv_average < -0.1 else 'moderate'
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals)
        }
    )

# =============================================================================
# CHAIKIN MONEY FLOW
# =============================================================================

@mcp_resilient(min_periods=20, required_columns=['high', 'low', 'close', 'volume'])
def calculate_chaikin_money_flow(data: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
    """
    Calculate Chaikin Money Flow with buying/selling pressure analysis.
    """
    cmf = safe_ta_calculation(ta.volume.chaikin_money_flow, 
                             data['high'], data['low'], data['close'], data['volume'], window=window)
    if cmf is None:
        return {'error': 'Chaikin Money Flow calculation failed'}
    
    current_cmf = float(cmf.iloc[-1])
    
    # CMF signal analysis
    if current_cmf > 0.25:
        signal = 'strong_buying_pressure'
        position = 'bullish'
    elif current_cmf > 0.05:
        signal = 'buying_pressure'
        position = 'bullish'
    elif current_cmf < -0.25:
        signal = 'strong_selling_pressure'
        position = 'bearish'
    elif current_cmf < -0.05:
        signal = 'selling_pressure'
        position = 'bearish'
    else:
        signal = 'balanced_pressure'
        position = 'neutral'
    
    # CMF momentum and trend
    cmf_momentum = cmf.diff(5).iloc[-1] if len(cmf) > 5 else 0
    cmf_trend = 'improving' if cmf_momentum > 0 else 'deteriorating' if cmf_momentum < 0 else 'stable'
    
    # Zero line crossings
    zero_crossings = []
    for i in range(1, len(cmf)):
        if cmf.iloc[i-1] <= 0 and cmf.iloc[i] > 0:
            zero_crossings.append({
                'date': cmf.index[i],
                'type': 'bullish_crossover',
                'value': float(cmf.iloc[i])
            })
        elif cmf.iloc[i-1] >= 0 and cmf.iloc[i] < 0:
            zero_crossings.append({
                'date': cmf.index[i],
                'type': 'bearish_crossover',
                'value': float(cmf.iloc[i])
            })
    
    # CMF persistence analysis
    positive_periods = (cmf > 0).sum()
    negative_periods = (cmf < 0).sum()
    total_periods = len(cmf)
    
    positive_ratio = positive_periods / total_periods if total_periods > 0 else 0.5
    
    # Generate trading signals
    trading_signals = []
    
    # Pressure signals
    if signal == 'strong_buying_pressure':
        trading_signals.append("Strong CMF buying pressure - accumulation phase")
    elif signal == 'strong_selling_pressure':
        trading_signals.append("Strong CMF selling pressure - distribution phase")
    
    # Momentum signals
    if current_cmf > 0 and cmf_momentum > 0:
        trading_signals.append("CMF positive and improving - strengthening buying pressure")
    elif current_cmf < 0 and cmf_momentum < 0:
        trading_signals.append("CMF negative and worsening - strengthening selling pressure")
    
    # Zero line crossing signals
    if len(zero_crossings) > 0:
        latest_crossing = zero_crossings[-1]
        days_since = (data.index[-1] - latest_crossing['date']).days
        
        if days_since <= 5:
            if latest_crossing['type'] == 'bullish_crossover':
                trading_signals.append("Recent CMF bullish crossover - money flow turning positive")
            else:
                trading_signals.append("Recent CMF bearish crossover - money flow turning negative")
    
    # Extreme readings
    if abs(current_cmf) > 0.4:
        trading_signals.append("Extreme CMF reading - potential reversal zone")
    
    return standardize_ta_response(
        function_name='calculate_chaikin_money_flow',
        indicator_name='Chaikin Money Flow',
        current_value=current_cmf,
        signal=signal,
        data={
            'position': position,
            'values': cmf.dropna().tail(50).tolist(),
            'momentum': float(cmf_momentum) if not pd.isna(cmf_momentum) else 0,
            'trend': cmf_trend,
            'zero_crossings': zero_crossings[-10:],
            'pressure_analysis': {
                'positive_periods': int(positive_periods),
                'negative_periods': int(negative_periods),
                'positive_ratio': float(positive_ratio),
                'dominant_pressure': 'buying' if positive_ratio > 0.6 else 'selling' if positive_ratio < 0.4 else 'balanced'
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'thresholds': {
                'strong_buying': 0.25,
                'buying': 0.05,
                'neutral': 0.0,
                'selling': -0.05,
                'strong_selling': -0.25
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# VOLUME MODULE EXPORTS
# =============================================================================

__all__ = [
    'calculate_obv',
    'calculate_mfi',
    'calculate_ad_line',
    'calculate_chaikin_money_flow'
]