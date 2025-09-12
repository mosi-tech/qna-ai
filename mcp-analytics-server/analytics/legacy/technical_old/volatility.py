#!/usr/bin/env python3
"""
Volatility Indicators - Single source of truth for all volatility-based technical indicators.
Includes Bollinger Bands, ATR, Keltner Channels, Donchian Channels.
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Any, Optional, Union

from .framework import (
    mcp_resilient, standardize_ta_response, calculate_signal_strength, safe_ta_calculation
)

# =============================================================================
# BOLLINGER BANDS
# =============================================================================

@mcp_resilient(min_periods=20, required_columns=['close'])
def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20, window_dev: int = 2) -> Dict[str, Any]:
    """
    Calculate Bollinger Bands with comprehensive squeeze and walk analysis.
    Single authoritative implementation.
    """
    # Calculate Bollinger Bands
    bollinger = ta.volatility.BollingerBands(data['close'], window=window, window_dev=window_dev)
    upper_band = bollinger.bollinger_hband()
    middle_band = bollinger.bollinger_mavg()
    lower_band = bollinger.bollinger_lband()
    bb_width = bollinger.bollinger_wband()
    percent_b = bollinger.bollinger_pband()
    
    if upper_band is None or len(upper_band.dropna()) < 10:
        return {'error': 'Bollinger Bands calculation failed'}
    
    current_price = float(data['close'].iloc[-1])
    current_upper = float(upper_band.iloc[-1])
    current_middle = float(middle_band.iloc[-1])
    current_lower = float(lower_band.iloc[-1])
    current_width = float(bb_width.iloc[-1])
    current_percent_b = float(percent_b.iloc[-1])
    
    # Position analysis
    if current_percent_b > 1:
        signal = 'overbought'
        position = 'above_upper_band'
    elif current_percent_b < 0:
        signal = 'oversold'
        position = 'below_lower_band'
    elif current_percent_b > 0.8:
        signal = 'approaching_overbought'
        position = 'near_upper_band'
    elif current_percent_b < 0.2:
        signal = 'approaching_oversold'
        position = 'near_lower_band'
    else:
        signal = 'neutral'
        position = 'middle_range'
    
    # Squeeze analysis
    avg_width = bb_width.mean()
    squeeze_threshold = avg_width * 0.8
    current_squeeze = current_width < squeeze_threshold
    
    # Historical squeezes
    squeeze_periods = []
    in_squeeze = False
    squeeze_start = None
    
    for i, width in enumerate(bb_width):
        if not in_squeeze and width < squeeze_threshold:
            in_squeeze = True
            squeeze_start = i
        elif in_squeeze and width >= squeeze_threshold:
            in_squeeze = False
            if squeeze_start is not None:
                squeeze_periods.append({
                    'start': data.index[squeeze_start],
                    'end': data.index[i-1],
                    'duration': i - squeeze_start,
                    'min_width': float(bb_width.iloc[squeeze_start:i].min())
                })
    
    # Band walks (consecutive closes outside bands)
    walks = []
    current_walk = None
    
    for i in range(len(data)):
        if i >= len(percent_b):
            continue
            
        pb_value = percent_b.iloc[i] if not pd.isna(percent_b.iloc[i]) else 0.5
        
        if pb_value > 1:  # Above upper band
            if current_walk is None or current_walk['type'] != 'upper_walk':
                if current_walk is not None:
                    walks.append(current_walk)
                current_walk = {
                    'type': 'upper_walk',
                    'start': data.index[i],
                    'duration': 1,
                    'max_percent_b': pb_value,
                    'end': data.index[i]
                }
            else:
                current_walk['duration'] += 1
                current_walk['max_percent_b'] = max(current_walk['max_percent_b'], pb_value)
                current_walk['end'] = data.index[i]
                
        elif pb_value < 0:  # Below lower band
            if current_walk is None or current_walk['type'] != 'lower_walk':
                if current_walk is not None:
                    walks.append(current_walk)
                current_walk = {
                    'type': 'lower_walk',
                    'start': data.index[i],
                    'duration': 1,
                    'min_percent_b': pb_value,
                    'end': data.index[i]
                }
            else:
                current_walk['duration'] += 1
                current_walk['min_percent_b'] = min(current_walk['min_percent_b'], pb_value)
                current_walk['end'] = data.index[i]
        else:
            if current_walk is not None:
                walks.append(current_walk)
                current_walk = None
    
    # Add current walk if it exists
    if current_walk is not None:
        walks.append(current_walk)
    
    # Volatility regime analysis
    if current_width < avg_width * 0.8:
        volatility_regime = 'low'
        regime_desc = 'Low volatility environment'
    elif current_width > avg_width * 1.2:
        volatility_regime = 'high'
        regime_desc = 'High volatility environment'
    else:
        volatility_regime = 'normal'
        regime_desc = 'Normal volatility environment'
    
    # Generate trading signals
    trading_signals = []
    
    if current_squeeze and current_width == bb_width.tail(20).min():
        trading_signals.append("Bollinger Band squeeze at minimum - volatility breakout imminent")
    
    if position == 'below_lower_band' and data['close'].iloc[-1] > data['close'].iloc[-2]:
        trading_signals.append("Bounce from lower Bollinger Band - potential reversal")
    
    if position == 'above_upper_band' and data['close'].iloc[-1] < data['close'].iloc[-2]:
        trading_signals.append("Rejection at upper Bollinger Band - potential reversal")
    
    if current_walk and current_walk['type'] == 'upper_walk' and current_walk['duration'] > 3:
        trading_signals.append("Extended upper band walk - strong bullish momentum")
    
    if current_walk and current_walk['type'] == 'lower_walk' and current_walk['duration'] > 3:
        trading_signals.append("Extended lower band walk - strong bearish momentum")
    
    return standardize_ta_response(
        function_name='calculate_bollinger_bands',
        indicator_name='Bollinger Bands',
        current_value=current_percent_b,
        signal=signal,
        data={
            'bands': {
                'upper': float(current_upper),
                'middle': float(current_middle),
                'lower': float(current_lower)
            },
            'position': position,
            'percent_b': float(current_percent_b),
            'bandwidth': float(current_width),
            'values': {
                'upper': upper_band.dropna().tail(50).tolist(),
                'middle': middle_band.dropna().tail(50).tolist(),
                'lower': lower_band.dropna().tail(50).tolist()
            },
            'squeeze_analysis': {
                'current_squeeze': current_squeeze,
                'squeeze_periods': squeeze_periods[-3:],
                'avg_bandwidth': float(avg_width),
                'squeeze_threshold': float(squeeze_threshold)
            },
            'walk_analysis': {
                'recent_walks': walks[-5:],
                'current_walk': current_walk
            },
            'volatility_regime': volatility_regime,
            'regime_description': regime_desc,
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals)
        },
        metadata={'window': window, 'std_dev': window_dev}
    )

# =============================================================================
# ATR (AVERAGE TRUE RANGE)
# =============================================================================

@mcp_resilient(min_periods=14, required_columns=['high', 'low', 'close'])
def calculate_atr(data: pd.DataFrame, window: int = 14) -> Dict[str, Any]:
    """
    Calculate ATR with comprehensive volatility regime analysis.
    Single authoritative implementation.
    """
    atr = safe_ta_calculation(ta.volatility.average_true_range, 
                             data['high'], data['low'], data['close'], window=window)
    if atr is None:
        return {'error': 'ATR calculation failed'}
    
    current_atr = float(atr.iloc[-1])
    current_price = float(data['close'].iloc[-1])
    
    # Volatility regime analysis
    avg_atr = float(atr.mean())
    atr_std = float(atr.std())
    
    if current_atr > avg_atr + atr_std:
        volatility_regime = 'high'
        regime_desc = 'High volatility - large price movements expected'
    elif current_atr < avg_atr - atr_std:
        volatility_regime = 'low'
        regime_desc = 'Low volatility - range-bound conditions likely'
    else:
        volatility_regime = 'normal'
        regime_desc = 'Normal volatility environment'
    
    # ATR momentum
    atr_momentum = atr.diff(5).iloc[-1] if len(atr) > 5 else 0
    atr_trend = 'increasing' if atr_momentum > 0 else 'decreasing' if atr_momentum < 0 else 'stable'
    
    # ATR-based price targets and stop losses
    atr_multiplier_1 = current_atr * 1.0
    atr_multiplier_2 = current_atr * 2.0
    atr_multiplier_3 = current_atr * 3.0
    
    price_targets = {
        'support_1x': current_price - atr_multiplier_1,
        'support_2x': current_price - atr_multiplier_2,
        'resistance_1x': current_price + atr_multiplier_1,
        'resistance_2x': current_price + atr_multiplier_2,
        'stop_loss_tight': atr_multiplier_1,
        'stop_loss_wide': atr_multiplier_2
    }
    
    # Volatility breakouts (daily range > 1.5 * ATR)
    daily_ranges = data['high'] - data['low']
    atr_breakouts = []
    
    for i in range(len(daily_ranges)):
        if i >= len(atr):
            continue
        
        if daily_ranges.iloc[i] > atr.iloc[i] * 1.5:
            atr_breakouts.append({
                'date': data.index[i],
                'daily_range': float(daily_ranges.iloc[i]),
                'atr': float(atr.iloc[i]),
                'breakout_ratio': float(daily_ranges.iloc[i] / atr.iloc[i])
            })
    
    # ATR percentile analysis
    atr_percentile = (atr <= current_atr).sum() / len(atr) * 100
    
    # Generate trading signals
    trading_signals = []
    
    if volatility_regime == 'low' and atr_trend == 'increasing':
        trading_signals.append("ATR rising from low levels - volatility expansion beginning")
    
    if volatility_regime == 'high' and atr_trend == 'decreasing':
        trading_signals.append("ATR falling from high levels - volatility contraction likely")
    
    if len(atr_breakouts) > 0:
        latest_breakout = atr_breakouts[-1]
        days_since = (data.index[-1] - latest_breakout['date']).days
        if days_since <= 3:
            trading_signals.append("Recent ATR breakout - increased volatility and momentum")
    
    if atr_percentile > 90:
        trading_signals.append("ATR at 90th percentile - extremely high volatility")
    elif atr_percentile < 10:
        trading_signals.append("ATR at 10th percentile - extremely low volatility")
    
    # Position sizing recommendation
    if volatility_regime == 'high':
        position_sizing = 'reduce_position_size'
    elif volatility_regime == 'low':
        position_sizing = 'can_increase_position_size'
    else:
        position_sizing = 'normal_position_size'
    
    return standardize_ta_response(
        function_name='calculate_atr',
        indicator_name='ATR',
        current_value=current_atr,
        signal=volatility_regime,
        data={
            'volatility_regime': volatility_regime,
            'regime_description': regime_desc,
            'average_atr': float(avg_atr),
            'relative_position': float(current_atr / avg_atr),
            'percentile': float(atr_percentile),
            'values': atr.dropna().tail(50).tolist(),
            'momentum': float(atr_momentum) if not pd.isna(atr_momentum) else 0,
            'trend': atr_trend,
            'price_targets': {k: float(v) for k, v in price_targets.items()},
            'volatility_breakouts': atr_breakouts[-10:],
            'position_sizing_advice': position_sizing,
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'statistics': {
                'minimum': float(atr.min()),
                'maximum': float(atr.max()),
                'std_dev': float(atr_std)
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# KELTNER CHANNELS
# =============================================================================

@mcp_resilient(min_periods=20, required_columns=['high', 'low', 'close'])
def calculate_keltner_channels(data: pd.DataFrame, window: int = 20, atr_window: int = 10, multiplier: float = 2.0) -> Dict[str, Any]:
    """
    Calculate Keltner Channels with breakout and squeeze analysis.
    """
    keltner = ta.volatility.KeltnerChannel(data['high'], data['low'], data['close'], 
                                          window=window, window_atr=atr_window, fillna=False)
    upper_channel = keltner.keltner_channel_hband()
    middle_channel = keltner.keltner_channel_mband()
    lower_channel = keltner.keltner_channel_lband()
    
    if upper_channel is None or len(upper_channel.dropna()) < 10:
        return {'error': 'Keltner Channels calculation failed'}
    
    current_price = float(data['close'].iloc[-1])
    current_upper = float(upper_channel.iloc[-1])
    current_middle = float(middle_channel.iloc[-1])
    current_lower = float(lower_channel.iloc[-1])
    
    # Position analysis
    if current_price > current_upper:
        signal = 'breakout_above'
        position = 'above_upper_channel'
    elif current_price < current_lower:
        signal = 'breakout_below'
        position = 'below_lower_channel'
    elif current_price > current_middle:
        signal = 'bullish'
        position = 'upper_half'
    else:
        signal = 'bearish'
        position = 'lower_half'
    
    # Channel width analysis
    channel_width = upper_channel - lower_channel
    avg_width = channel_width.mean()
    current_width = float(channel_width.iloc[-1])
    
    # Squeeze detection
    squeeze_threshold = avg_width * 0.8
    current_squeeze = current_width < squeeze_threshold
    
    # Breakout analysis
    breakouts = []
    for i in range(1, len(data)):
        if i >= len(upper_channel) or i >= len(lower_channel):
            continue
            
        prev_price = data['close'].iloc[i-1]
        curr_price = data['close'].iloc[i]
        
        # Upper breakout
        if prev_price <= upper_channel.iloc[i-1] and curr_price > upper_channel.iloc[i]:
            breakouts.append({
                'date': data.index[i],
                'type': 'upper_breakout',
                'price': float(curr_price),
                'channel_level': float(upper_channel.iloc[i])
            })
        
        # Lower breakout
        elif prev_price >= lower_channel.iloc[i-1] and curr_price < lower_channel.iloc[i]:
            breakouts.append({
                'date': data.index[i],
                'type': 'lower_breakout',
                'price': float(curr_price),
                'channel_level': float(lower_channel.iloc[i])
            })
    
    # Generate trading signals
    trading_signals = []
    
    if current_squeeze:
        trading_signals.append("Keltner Channel squeeze - breakout anticipated")
    
    if len(breakouts) > 0:
        latest_breakout = breakouts[-1]
        days_since = (data.index[-1] - latest_breakout['date']).days
        
        if days_since <= 2:
            if latest_breakout['type'] == 'upper_breakout':
                trading_signals.append("Recent upper Keltner breakout - bullish momentum")
            else:
                trading_signals.append("Recent lower Keltner breakout - bearish momentum")
    
    if signal == 'breakout_above' and current_price > current_upper * 1.01:
        trading_signals.append("Strong breakout above Keltner upper channel - trend continuation")
    
    if signal == 'breakout_below' and current_price < current_lower * 0.99:
        trading_signals.append("Strong breakdown below Keltner lower channel - trend continuation")
    
    return standardize_ta_response(
        function_name='calculate_keltner_channels',
        indicator_name='Keltner Channels',
        current_value=current_price,
        signal=signal,
        data={
            'channels': {
                'upper': float(current_upper),
                'middle': float(current_middle),
                'lower': float(current_lower)
            },
            'position': position,
            'channel_width': float(current_width),
            'avg_width': float(avg_width),
            'squeeze_detected': current_squeeze,
            'values': {
                'upper': upper_channel.dropna().tail(50).tolist(),
                'middle': middle_channel.dropna().tail(50).tolist(),
                'lower': lower_channel.dropna().tail(50).tolist()
            },
            'breakouts': breakouts[-10:],
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'width_analysis': {
                'current_vs_average': float(current_width / avg_width),
                'percentile': float((channel_width <= current_width).sum() / len(channel_width) * 100)
            }
        },
        metadata={'window': window, 'atr_window': atr_window, 'multiplier': multiplier}
    )

# =============================================================================
# DONCHIAN CHANNELS
# =============================================================================

@mcp_resilient(min_periods=20, required_columns=['high', 'low', 'close'])
def calculate_donchian_channels(data: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
    """
    Calculate Donchian Channels with breakout analysis and trend following signals.
    """
    donchian = ta.volatility.DonchianChannel(data['high'], data['low'], data['close'], 
                                            window=window, offset=0, fillna=False)
    upper_channel = donchian.donchian_channel_hband()
    middle_channel = donchian.donchian_channel_mband()  
    lower_channel = donchian.donchian_channel_lband()
    
    if upper_channel is None or len(upper_channel.dropna()) < 10:
        return {'error': 'Donchian Channels calculation failed'}
    
    current_price = float(data['close'].iloc[-1])
    current_upper = float(upper_channel.iloc[-1])
    current_middle = float(middle_channel.iloc[-1])
    current_lower = float(lower_channel.iloc[-1])
    
    # Position analysis
    if current_price >= current_upper:
        signal = 'breakout_above'
        position = 'new_high_breakout'
    elif current_price <= current_lower:
        signal = 'breakout_below'
        position = 'new_low_breakdown'
    elif current_price > current_middle:
        signal = 'bullish'
        position = 'upper_half'
    else:
        signal = 'bearish'
        position = 'lower_half'
    
    # Channel width and range analysis
    channel_width = upper_channel - lower_channel
    current_width = float(channel_width.iloc[-1])
    avg_width = float(channel_width.mean())
    width_percentile = (channel_width <= current_width).sum() / len(channel_width) * 100
    
    # Breakout detection (price touching channel boundaries)
    breakouts = []
    for i in range(len(data)):
        if i >= len(upper_channel) or i >= len(lower_channel):
            continue
            
        curr_price = data['close'].iloc[i]
        
        # New high breakout
        if curr_price >= upper_channel.iloc[i]:
            breakouts.append({
                'date': data.index[i],
                'type': 'new_high_breakout',
                'price': float(curr_price),
                'channel_level': float(upper_channel.iloc[i])
            })
        
        # New low breakdown  
        elif curr_price <= lower_channel.iloc[i]:
            breakouts.append({
                'date': data.index[i],
                'type': 'new_low_breakdown',
                'price': float(curr_price),
                'channel_level': float(lower_channel.iloc[i])
            })
    
    # Time since last breakout
    days_since_breakout = None
    if breakouts:
        days_since_breakout = (data.index[-1] - breakouts[-1]['date']).days
    
    # Generate trading signals (Turtle Trading style)
    trading_signals = []
    
    if signal == 'breakout_above':
        trading_signals.append(f"New {window}-period high breakout - strong bullish signal")
    
    if signal == 'breakout_below':
        trading_signals.append(f"New {window}-period low breakdown - strong bearish signal")
    
    if days_since_breakout is not None and days_since_breakout <= 1:
        if breakouts[-1]['type'] == 'new_high_breakout':
            trading_signals.append("Fresh breakout to new highs - momentum entry signal")
        else:
            trading_signals.append("Fresh breakdown to new lows - momentum entry signal")
    
    if width_percentile > 80:
        trading_signals.append("Donchian channels very wide - high volatility period")
    elif width_percentile < 20:
        trading_signals.append("Donchian channels narrow - low volatility, breakout pending")
    
    # Trend strength based on position in channel
    if current_price > current_middle:
        channel_position = (current_price - current_lower) / (current_upper - current_lower)
        trend_strength = 'strong' if channel_position > 0.8 else 'moderate'
    else:
        channel_position = (current_upper - current_price) / (current_upper - current_lower)
        trend_strength = 'strong' if channel_position > 0.8 else 'moderate'
    
    return standardize_ta_response(
        function_name='calculate_donchian_channels',
        indicator_name='Donchian Channels',
        current_value=current_price,
        signal=signal,
        data={
            'channels': {
                'upper': float(current_upper),
                'middle': float(current_middle),  
                'lower': float(current_lower)
            },
            'position': position,
            'channel_width': float(current_width),
            'width_percentile': float(width_percentile),
            'trend_strength': trend_strength,
            'values': {
                'upper': upper_channel.dropna().tail(50).tolist(),
                'middle': middle_channel.dropna().tail(50).tolist(),
                'lower': lower_channel.dropna().tail(50).tolist()
            },
            'breakouts': breakouts[-10:],
            'days_since_last_breakout': days_since_breakout,
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals),
            'turtle_signals': {
                'entry_long': signal == 'breakout_above',
                'entry_short': signal == 'breakout_below',
                'exit_condition': 'price_crosses_middle_band'
            }
        },
        metadata={'window': window}
    )

# =============================================================================
# VOLATILITY MODULE EXPORTS
# =============================================================================

__all__ = [
    'calculate_bollinger_bands',
    'calculate_atr',
    'calculate_keltner_channels', 
    'calculate_donchian_channels'
]