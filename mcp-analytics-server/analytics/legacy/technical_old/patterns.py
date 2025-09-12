#!/usr/bin/env python3
"""
Pattern Detection - Single source of truth for price pattern recognition and analysis.
Includes support/resistance, gaps, breakouts, and basic pattern detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union

from .framework import (
    mcp_resilient, standardize_ta_response, calculate_signal_strength
)

# =============================================================================
# SUPPORT AND RESISTANCE DETECTION
# =============================================================================

@mcp_resilient(min_periods=50, required_columns=['high', 'low', 'close'])
def detect_support_resistance(data: pd.DataFrame, window: int = 20, min_touches: int = 2) -> Dict[str, Any]:
    """
    Detect support and resistance levels using pivot points and touch analysis.
    """
    # Find pivot highs and lows
    highs = []
    lows = []
    
    for i in range(window, len(data) - window):
        # Pivot high
        if all(data['high'].iloc[i] >= data['high'].iloc[i-j] for j in range(1, window+1)) and \
           all(data['high'].iloc[i] >= data['high'].iloc[i+j] for j in range(1, window+1)):
            highs.append((data.index[i], data['high'].iloc[i]))
        
        # Pivot low
        if all(data['low'].iloc[i] <= data['low'].iloc[i-j] for j in range(1, window+1)) and \
           all(data['low'].iloc[i] <= data['low'].iloc[i+j] for j in range(1, window+1)):
            lows.append((data.index[i], data['low'].iloc[i]))
    
    # Cluster similar levels (within 2% of each other)
    def cluster_levels(levels, tolerance=0.02):
        if not levels:
            return []
        
        clustered = []
        sorted_levels = sorted(levels, key=lambda x: x[1])
        
        current_cluster = [sorted_levels[0]]
        
        for i in range(1, len(sorted_levels)):
            if abs(sorted_levels[i][1] - current_cluster[-1][1]) / current_cluster[-1][1] <= tolerance:
                current_cluster.append(sorted_levels[i])
            else:
                if len(current_cluster) >= min_touches:
                    avg_level = sum(level[1] for level in current_cluster) / len(current_cluster)
                    clustered.append({
                        'level': float(avg_level),
                        'touches': len(current_cluster),
                        'first_touch': current_cluster[0][0],
                        'last_touch': current_cluster[-1][0],
                        'strength': len(current_cluster)
                    })
                current_cluster = [sorted_levels[i]]
        
        # Don't forget the last cluster
        if len(current_cluster) >= min_touches:
            avg_level = sum(level[1] for level in current_cluster) / len(current_cluster)
            clustered.append({
                'level': float(avg_level),
                'touches': len(current_cluster),
                'first_touch': current_cluster[0][0],
                'last_touch': current_cluster[-1][0],
                'strength': len(current_cluster)
            })
        
        return clustered
    
    resistance_levels = cluster_levels(highs)
    support_levels = cluster_levels(lows)
    
    # Current price analysis
    current_price = float(data['close'].iloc[-1])
    
    # Find nearest levels
    resistances_above = [r for r in resistance_levels if r['level'] > current_price]
    supports_below = [s for s in support_levels if s['level'] < current_price]
    
    nearest_resistance = min(resistances_above, key=lambda x: x['level'])['level'] if resistances_above else None
    nearest_support = max(supports_below, key=lambda x: x['level'])['level'] if supports_below else None
    
    # Generate trading signals
    trading_signals = []
    
    if nearest_resistance and current_price > nearest_resistance * 0.99:
        trading_signals.append(f"Price approaching resistance at {nearest_resistance:.2f}")
    
    if nearest_support and current_price < nearest_support * 1.01:
        trading_signals.append(f"Price approaching support at {nearest_support:.2f}")
    
    # Check for breakouts
    for resistance in resistance_levels:
        if current_price > resistance['level'] * 1.005:  # 0.5% above resistance
            days_since = (data.index[-1] - resistance['last_touch']).days
            if days_since <= 30:
                trading_signals.append(f"Resistance breakout at {resistance['level']:.2f} - bullish signal")
    
    for support in support_levels:
        if current_price < support['level'] * 0.995:  # 0.5% below support
            days_since = (data.index[-1] - support['last_touch']).days
            if days_since <= 30:
                trading_signals.append(f"Support breakdown at {support['level']:.2f} - bearish signal")
    
    return standardize_ta_response(
        function_name='detect_support_resistance',
        indicator_name='Support/Resistance',
        current_value=current_price,
        signal='levels_detected',
        data={
            'current_price': current_price,
            'resistance_levels': resistance_levels,
            'support_levels': support_levels,
            'nearest_resistance': nearest_resistance,
            'nearest_support': nearest_support,
            'key_levels': {
                'strong_resistance': [r['level'] for r in resistance_levels if r['strength'] >= 3],
                'strong_support': [s['level'] for s in support_levels if s['strength'] >= 3]
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals)
        },
        metadata={'window': window, 'min_touches': min_touches}
    )

# =============================================================================
# GAP DETECTION AND ANALYSIS
# =============================================================================

@mcp_resilient(min_periods=10, required_columns=['open', 'high', 'low', 'close'])
def detect_gaps(data: pd.DataFrame, gap_threshold: float = 0.01) -> Dict[str, Any]:
    """
    Detect and analyze price gaps with fill probability and significance assessment.
    """
    gaps = []
    
    for i in range(1, len(data)):
        prev_close = data['close'].iloc[i-1]
        current_open = data['open'].iloc[i]
        current_high = data['high'].iloc[i]
        current_low = data['low'].iloc[i]
        current_close = data['close'].iloc[i]
        
        # Calculate gap size
        gap_size = (current_open - prev_close) / prev_close
        
        if abs(gap_size) > gap_threshold:
            # Determine gap type
            if gap_size > 0:
                gap_type = 'gap_up'
                gap_high = current_open
                gap_low = prev_close
            else:
                gap_type = 'gap_down'
                gap_high = prev_close
                gap_low = current_open
            
            # Check if gap was filled on the same day
            filled_same_day = (gap_type == 'gap_up' and current_low <= prev_close) or \
                             (gap_type == 'gap_down' and current_high >= prev_close)
            
            gap_info = {
                'date': data.index[i],
                'type': gap_type,
                'size_percent': float(gap_size * 100),
                'size_points': float(abs(current_open - prev_close)),
                'prev_close': float(prev_close),
                'open': float(current_open),
                'gap_high': float(gap_high),
                'gap_low': float(gap_low),
                'filled_same_day': filled_same_day,
                'volume': float(data['volume'].iloc[i]) if 'volume' in data.columns else None
            }
            
            gaps.append(gap_info)
    
    # Analyze gap fills for unfilled gaps
    for gap in gaps:
        if not gap['filled_same_day']:
            gap_date_idx = data.index.get_loc(gap['date'])
            filled = False
            fill_date = None
            
            # Check subsequent days for gap fill
            for j in range(gap_date_idx + 1, len(data)):
                if gap['type'] == 'gap_up' and data['low'].iloc[j] <= gap['gap_low']:
                    filled = True
                    fill_date = data.index[j]
                    break
                elif gap['type'] == 'gap_down' and data['high'].iloc[j] >= gap['gap_high']:
                    filled = True
                    fill_date = data.index[j]
                    break
            
            gap['filled'] = filled
            gap['fill_date'] = fill_date
            if filled and fill_date:
                gap['days_to_fill'] = (fill_date - gap['date']).days
    
    # Recent gaps analysis
    recent_gaps = [g for g in gaps if (data.index[-1] - g['date']).days <= 30]
    unfilled_gaps = [g for g in gaps if not g.get('filled', False)]
    
    # Gap statistics
    if gaps:
        avg_gap_size = np.mean([abs(g['size_percent']) for g in gaps])
        gap_frequency = len(gaps) / len(data) * 100
        fill_rate = sum(1 for g in gaps if g.get('filled', False)) / len(gaps) * 100
    else:
        avg_gap_size = 0
        gap_frequency = 0
        fill_rate = 0
    
    # Generate trading signals
    trading_signals = []
    
    # Recent unfilled gaps
    for gap in unfilled_gaps:
        days_ago = (data.index[-1] - gap['date']).days
        if days_ago <= 10:
            if gap['type'] == 'gap_up':
                trading_signals.append(f"Unfilled gap up at {gap['gap_low']:.2f} - potential downside target")
            else:
                trading_signals.append(f"Unfilled gap down at {gap['gap_high']:.2f} - potential upside target")
    
    # Large recent gaps
    for gap in recent_gaps:
        if abs(gap['size_percent']) > 3:  # Gaps larger than 3%
            trading_signals.append(f"Significant {gap['type'].replace('_', ' ')} of {abs(gap['size_percent']):.1f}%")
    
    return standardize_ta_response(
        function_name='detect_gaps',
        indicator_name='Price Gaps',
        current_value=len(gaps),
        signal='gaps_detected',
        data={
            'total_gaps': len(gaps),
            'recent_gaps': recent_gaps,
            'unfilled_gaps': unfilled_gaps[-10:],  # Last 10 unfilled gaps
            'statistics': {
                'average_gap_size_percent': float(avg_gap_size),
                'gap_frequency_percent': float(gap_frequency),
                'fill_rate_percent': float(fill_rate),
                'gaps_up': len([g for g in gaps if g['type'] == 'gap_up']),
                'gaps_down': len([g for g in gaps if g['type'] == 'gap_down'])
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals)
        },
        metadata={'gap_threshold_percent': gap_threshold * 100}
    )

# =============================================================================
# BREAKOUT DETECTION
# =============================================================================

@mcp_resilient(min_periods=20, required_columns=['high', 'low', 'close'])
def detect_breakouts(data: pd.DataFrame, window: int = 20, volume_confirmation: bool = True) -> Dict[str, Any]:
    """
    Detect breakout patterns with volume confirmation and follow-through analysis.
    """
    # Calculate dynamic support/resistance using rolling max/min
    resistance = data['high'].rolling(window=window).max()
    support = data['low'].rolling(window=window).min()
    
    breakouts = []
    
    for i in range(window, len(data)):
        current_close = data['close'].iloc[i]
        current_high = data['high'].iloc[i]
        current_low = data['low'].iloc[i]
        
        # Previous period levels
        prev_resistance = resistance.iloc[i-1]
        prev_support = support.iloc[i-1]
        
        volume_surge = False
        if 'volume' in data.columns and i > 0:
            avg_volume = data['volume'].iloc[max(0, i-10):i].mean()
            current_volume = data['volume'].iloc[i]
            volume_surge = current_volume > avg_volume * 1.5  # 50% above average
        
        # Resistance breakout
        if current_close > prev_resistance:
            breakout_strength = (current_close - prev_resistance) / prev_resistance * 100
            
            breakout_info = {
                'date': data.index[i],
                'type': 'resistance_breakout',
                'level': float(prev_resistance),
                'close_price': float(current_close),
                'breakout_strength_percent': float(breakout_strength),
                'volume_confirmation': volume_surge if volume_confirmation else True,
                'intraday_follow_through': current_high > prev_resistance * 1.01
            }
            
            breakouts.append(breakout_info)
        
        # Support breakdown
        elif current_close < prev_support:
            breakdown_strength = (prev_support - current_close) / prev_support * 100
            
            breakout_info = {
                'date': data.index[i],
                'type': 'support_breakdown',
                'level': float(prev_support),
                'close_price': float(current_close),
                'breakout_strength_percent': float(breakdown_strength),
                'volume_confirmation': volume_surge if volume_confirmation else True,
                'intraday_follow_through': current_low < prev_support * 0.99
            }
            
            breakouts.append(breakout_info)
    
    # Analyze breakout success rates (follow-through in next 5 days)
    successful_breakouts = 0
    
    for breakout in breakouts:
        breakout_idx = data.index.get_loc(breakout['date'])
        
        if breakout_idx + 5 < len(data):
            future_prices = data['close'].iloc[breakout_idx+1:breakout_idx+6]
            
            if breakout['type'] == 'resistance_breakout':
                success = any(price > breakout['close_price'] * 1.02 for price in future_prices)  # 2% follow-through
            else:  # support_breakdown
                success = any(price < breakout['close_price'] * 0.98 for price in future_prices)  # 2% follow-through
            
            breakout['successful'] = success
            if success:
                successful_breakouts += 1
    
    # Recent breakouts
    recent_breakouts = [b for b in breakouts if (data.index[-1] - b['date']).days <= 10]
    
    # Generate trading signals
    trading_signals = []
    
    for breakout in recent_breakouts:
        if breakout['volume_confirmation']:
            if breakout['type'] == 'resistance_breakout':
                trading_signals.append(f"Recent resistance breakout at {breakout['level']:.2f} with volume - bullish signal")
            else:
                trading_signals.append(f"Recent support breakdown at {breakout['level']:.2f} with volume - bearish signal")
    
    # Current price near breakout levels
    current_price = data['close'].iloc[-1]
    current_resistance = resistance.iloc[-1]
    current_support = support.iloc[-1]
    
    if current_price > current_resistance * 0.995:  # Within 0.5% of resistance
        trading_signals.append("Price near resistance breakout zone - watch for confirmation")
    
    if current_price < current_support * 1.005:  # Within 0.5% of support
        trading_signals.append("Price near support breakdown zone - watch for confirmation")
    
    # Success rate analysis
    success_rate = (successful_breakouts / len(breakouts) * 100) if breakouts else 0
    
    return standardize_ta_response(
        function_name='detect_breakouts',
        indicator_name='Breakouts',
        current_value=len(breakouts),
        signal='breakouts_detected',
        data={
            'total_breakouts': len(breakouts),
            'recent_breakouts': recent_breakouts,
            'successful_breakouts': successful_breakouts,
            'success_rate_percent': float(success_rate),
            'current_levels': {
                'resistance': float(current_resistance),
                'support': float(current_support),
                'price': float(current_price),
                'distance_to_resistance_percent': float((current_resistance - current_price) / current_price * 100),
                'distance_to_support_percent': float((current_price - current_support) / current_price * 100)
            },
            'breakout_types': {
                'resistance_breakouts': len([b for b in breakouts if b['type'] == 'resistance_breakout']),
                'support_breakdowns': len([b for b in breakouts if b['type'] == 'support_breakdown'])
            },
            'trading_signals': trading_signals,
            'signal_strength': calculate_signal_strength(trading_signals)
        },
        metadata={'window': window, 'volume_confirmation': volume_confirmation}
    )

# =============================================================================
# PATTERNS MODULE EXPORTS
# =============================================================================

__all__ = [
    'detect_support_resistance',
    'detect_gaps', 
    'detect_breakouts'
]