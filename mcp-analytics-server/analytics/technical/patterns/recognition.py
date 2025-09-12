"""
Advanced Pattern Recognition

This module identifies sophisticated technical patterns using core indicators and crossover functions.
Patterns include multi-timeframe analysis, confluence detection, and probability scoring.

Dependencies: pandas, numpy, core indicators, crossover detection
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ..core.indicators import (sma, ema, rsi, macd, bollinger_bands, stochastic, 
                              atr, adx, williams_r)
from ..crossovers.detection import moving_average_crossover, macd_crossover, rsi_level_cross


def bullish_confluence(data: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', 
                      close_col: str = 'close', volume_col: str = 'volume') -> Dict[str, Any]:
    """
    Identify bullish confluence patterns combining multiple indicators
    
    Args:
        data: OHLCV DataFrame
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        Dictionary with bullish confluence analysis and scoring
    """
    closes = data[close_col]
    confluence_score = 0
    signals = {}
    
    # 1. Moving Average alignment (20%)
    sma_20 = sma(closes, period=20)
    sma_50 = sma(closes, period=50)
    if not sma_20.empty and not sma_50.empty and closes.iloc[-1] > sma_20.iloc[-1] > sma_50.iloc[-1]:
        confluence_score += 20
        signals['ma_alignment'] = 'bullish'
    else:
        signals['ma_alignment'] = 'neutral'
    
    # 2. RSI in bullish range but not overbought (15%)
    rsi_values = rsi(closes, period=14)
    current_rsi = rsi_values.iloc[-1] if not rsi_values.empty else 50
    if 45 <= current_rsi <= 65:
        confluence_score += 15
        signals['rsi_position'] = 'bullish_range'
    elif current_rsi > 70:
        signals['rsi_position'] = 'overbought'
    elif current_rsi < 30:
        signals['rsi_position'] = 'oversold'
    else:
        signals['rsi_position'] = 'neutral'
    
    # 3. MACD bullish crossover (20%)
    macd_cross = macd_crossover(closes, fast=12, slow=26, signal=9)
    recent_crossovers = [c for c in macd_cross['crossover_points'] if c['type'] == 'bullish']
    if recent_crossovers and len(recent_crossovers) > 0:
        # Check if recent crossover (within last 5 periods)
        last_bullish = max(recent_crossovers, key=lambda x: x['timestamp'])
        if len(closes) - closes.index.get_loc(last_bullish['timestamp']) <= 5:
            confluence_score += 20
            signals['macd_crossover'] = 'recent_bullish'
        else:
            signals['macd_crossover'] = 'old_bullish'
    else:
        signals['macd_crossover'] = 'none'
    
    # 4. Volume confirmation (15%)
    if volume_col in data.columns:
        vol_sma = sma(data[volume_col], period=20)
        if not vol_sma.empty and data[volume_col].iloc[-1] > vol_sma.iloc[-1] * 1.2:
            confluence_score += 15
            signals['volume_confirmation'] = 'above_average'
        else:
            signals['volume_confirmation'] = 'below_average'
    else:
        signals['volume_confirmation'] = 'no_data'
    
    # 5. ADX trending strength (10%)
    adx_data = adx(data, period=14, high_col=high_col, low_col=low_col, close_col=close_col)
    current_adx = adx_data['adx'].iloc[-1] if not adx_data['adx'].empty else 20
    current_plus_di = adx_data['plus_di'].iloc[-1] if not adx_data['plus_di'].empty else 20
    current_minus_di = adx_data['minus_di'].iloc[-1] if not adx_data['minus_di'].empty else 20
    
    if current_adx > 25 and current_plus_di > current_minus_di:
        confluence_score += 10
        signals['trend_strength'] = 'strong_bullish'
    elif current_plus_di > current_minus_di:
        confluence_score += 5
        signals['trend_strength'] = 'weak_bullish'
    else:
        signals['trend_strength'] = 'bearish'
    
    # 6. Bollinger Band position (10%)
    bb = bollinger_bands(closes, period=20, std_dev=2.0)
    current_price = closes.iloc[-1]
    current_middle = bb['middle'].iloc[-1] if not bb['middle'].empty else current_price
    current_upper = bb['upper'].iloc[-1] if not bb['upper'].empty else current_price
    
    if current_price > current_middle and current_price < current_upper:
        confluence_score += 10
        signals['bb_position'] = 'upper_half'
    elif current_price > current_upper:
        signals['bb_position'] = 'above_upper'
    elif current_price < current_middle:
        signals['bb_position'] = 'lower_half'
    else:
        signals['bb_position'] = 'neutral'
    
    # 7. Price momentum (10%)
    price_change_5d = ((current_price - closes.iloc[-6]) / closes.iloc[-6] * 100) if len(closes) >= 6 else 0
    if price_change_5d > 2:
        confluence_score += 10
        signals['momentum'] = 'strong_positive'
    elif price_change_5d > 0:
        confluence_score += 5
        signals['momentum'] = 'positive'
    else:
        signals['momentum'] = 'negative'
    
    return {
        'confluence_score': confluence_score,
        'strength': (
            'very_strong' if confluence_score >= 80 else
            'strong' if confluence_score >= 60 else
            'moderate' if confluence_score >= 40 else
            'weak'
        ),
        'signals': signals,
        'recommendation': (
            'strong_buy' if confluence_score >= 75 else
            'buy' if confluence_score >= 55 else
            'hold' if confluence_score >= 35 else
            'weak'
        )
    }


def bearish_confluence(data: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', 
                      close_col: str = 'close', volume_col: str = 'volume') -> Dict[str, Any]:
    """
    Identify bearish confluence patterns combining multiple indicators
    
    Args:
        data: OHLCV DataFrame
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        Dictionary with bearish confluence analysis and scoring
    """
    closes = data[close_col]
    confluence_score = 0
    signals = {}
    
    # 1. Moving Average alignment (20%)
    sma_20 = sma(closes, period=20)
    sma_50 = sma(closes, period=50)
    if not sma_20.empty and not sma_50.empty and closes.iloc[-1] < sma_20.iloc[-1] < sma_50.iloc[-1]:
        confluence_score += 20
        signals['ma_alignment'] = 'bearish'
    else:
        signals['ma_alignment'] = 'neutral'
    
    # 2. RSI in bearish range but not oversold (15%)
    rsi_values = rsi(closes, period=14)
    current_rsi = rsi_values.iloc[-1] if not rsi_values.empty else 50
    if 35 <= current_rsi <= 55:
        confluence_score += 15
        signals['rsi_position'] = 'bearish_range'
    elif current_rsi < 30:
        signals['rsi_position'] = 'oversold'
    elif current_rsi > 70:
        signals['rsi_position'] = 'overbought'
    else:
        signals['rsi_position'] = 'neutral'
    
    # 3. MACD bearish crossover (20%)
    macd_cross = macd_crossover(closes, fast=12, slow=26, signal=9)
    recent_crossovers = [c for c in macd_cross['crossover_points'] if c['type'] == 'bearish']
    if recent_crossovers and len(recent_crossovers) > 0:
        last_bearish = max(recent_crossovers, key=lambda x: x['timestamp'])
        if len(closes) - closes.index.get_loc(last_bearish['timestamp']) <= 5:
            confluence_score += 20
            signals['macd_crossover'] = 'recent_bearish'
        else:
            signals['macd_crossover'] = 'old_bearish'
    else:
        signals['macd_crossover'] = 'none'
    
    # 4. Volume confirmation (15%)
    if volume_col in data.columns:
        vol_sma = sma(data[volume_col], period=20)
        if not vol_sma.empty and data[volume_col].iloc[-1] > vol_sma.iloc[-1] * 1.2:
            confluence_score += 15
            signals['volume_confirmation'] = 'above_average'
        else:
            signals['volume_confirmation'] = 'below_average'
    else:
        signals['volume_confirmation'] = 'no_data'
    
    # 5. ADX trending strength (10%)
    adx_data = adx(data, period=14, high_col=high_col, low_col=low_col, close_col=close_col)
    current_adx = adx_data['adx'].iloc[-1] if not adx_data['adx'].empty else 20
    current_plus_di = adx_data['plus_di'].iloc[-1] if not adx_data['plus_di'].empty else 20
    current_minus_di = adx_data['minus_di'].iloc[-1] if not adx_data['minus_di'].empty else 20
    
    if current_adx > 25 and current_minus_di > current_plus_di:
        confluence_score += 10
        signals['trend_strength'] = 'strong_bearish'
    elif current_minus_di > current_plus_di:
        confluence_score += 5
        signals['trend_strength'] = 'weak_bearish'
    else:
        signals['trend_strength'] = 'bullish'
    
    # 6. Bollinger Band position (10%)
    bb = bollinger_bands(closes, period=20, std_dev=2.0)
    current_price = closes.iloc[-1]
    current_middle = bb['middle'].iloc[-1] if not bb['middle'].empty else current_price
    current_lower = bb['lower'].iloc[-1] if not bb['lower'].empty else current_price
    
    if current_price < current_middle and current_price > current_lower:
        confluence_score += 10
        signals['bb_position'] = 'lower_half'
    elif current_price < current_lower:
        signals['bb_position'] = 'below_lower'
    elif current_price > current_middle:
        signals['bb_position'] = 'upper_half'
    else:
        signals['bb_position'] = 'neutral'
    
    # 7. Price momentum (10%)
    price_change_5d = ((current_price - closes.iloc[-6]) / closes.iloc[-6] * 100) if len(closes) >= 6 else 0
    if price_change_5d < -2:
        confluence_score += 10
        signals['momentum'] = 'strong_negative'
    elif price_change_5d < 0:
        confluence_score += 5
        signals['momentum'] = 'negative'
    else:
        signals['momentum'] = 'positive'
    
    return {
        'confluence_score': confluence_score,
        'strength': (
            'very_strong' if confluence_score >= 80 else
            'strong' if confluence_score >= 60 else
            'moderate' if confluence_score >= 40 else
            'weak'
        ),
        'signals': signals,
        'recommendation': (
            'strong_sell' if confluence_score >= 75 else
            'sell' if confluence_score >= 55 else
            'hold' if confluence_score >= 35 else
            'weak'
        )
    }


def squeeze_pattern(data: pd.DataFrame, bb_period: int = 20, kc_period: int = 20,
                   high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> Dict[str, Any]:
    """
    Identify Bollinger Band / Keltner Channel squeeze patterns
    
    Args:
        data: OHLC DataFrame
        bb_period: Bollinger Band period (default: 20)
        kc_period: Keltner Channel period (default: 20)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        Dictionary with squeeze pattern analysis
    """
    from ..core.indicators import keltner_channels
    
    closes = data[close_col]
    bb = bollinger_bands(closes, period=bb_period, std_dev=2.0)
    kc = keltner_channels(data, period=kc_period, multiplier=2.0, 
                         high_col=high_col, low_col=low_col, close_col=close_col)
    
    # Squeeze occurs when Bollinger Bands are inside Keltner Channels
    squeeze_condition = (bb['upper'] < kc['upper']) & (bb['lower'] > kc['lower'])
    squeeze_release = squeeze_condition.shift(1) & ~squeeze_condition
    
    # Find squeeze periods
    squeeze_periods = []
    in_squeeze = False
    squeeze_start = None
    
    for i, (idx, is_squeeze) in enumerate(squeeze_condition.items()):
        if is_squeeze and not in_squeeze:
            in_squeeze = True
            squeeze_start = idx
        elif not is_squeeze and in_squeeze:
            in_squeeze = False
            squeeze_periods.append({
                'start': squeeze_start,
                'end': idx,
                'duration': i - squeeze_condition.index.get_loc(squeeze_start),
                'release_direction': 'bullish' if closes.loc[idx] > bb['middle'].loc[idx] else 'bearish'
            })
    
    # Current squeeze status
    current_squeeze = squeeze_condition.iloc[-1] if not squeeze_condition.empty else False
    
    # Calculate squeeze strength (how tight the bands are)
    bb_width = bb['width']
    avg_bb_width = bb_width.rolling(window=50).mean()
    current_squeeze_strength = (avg_bb_width.iloc[-1] - bb_width.iloc[-1]) / avg_bb_width.iloc[-1] * 100 if not avg_bb_width.empty else 0
    
    return {
        'current_squeeze': bool(current_squeeze),
        'squeeze_strength': float(current_squeeze_strength),
        'recent_squeezes': squeeze_periods[-5:],
        'squeeze_duration': len([x for x in squeeze_condition.iloc[-20:] if x]) if len(squeeze_condition) >= 20 else 0,
        'expected_breakout': 'imminent' if current_squeeze and current_squeeze_strength > 50 else 'moderate',
        'volatility_compression': float(bb_width.iloc[-1]) if not bb_width.empty else 0
    }


def trend_continuation_pattern(data: pd.DataFrame, trend_period: int = 50, 
                              pullback_period: int = 10, close_col: str = 'close') -> Dict[str, Any]:
    """
    Identify trend continuation patterns after pullbacks
    
    Args:
        data: OHLC DataFrame  
        trend_period: Period to determine primary trend (default: 50)
        pullback_period: Period to identify pullback (default: 10)
        close_col: Close column name (default: 'close')
        
    Returns:
        Dictionary with trend continuation analysis
    """
    closes = data[close_col]
    
    # Determine primary trend using longer-term SMA
    long_sma = sma(closes, period=trend_period)
    primary_trend = 'bullish' if closes.iloc[-1] > long_sma.iloc[-1] else 'bearish'
    
    # Recent pullback analysis
    recent_high = closes.iloc[-pullback_period:].max()
    recent_low = closes.iloc[-pullback_period:].min()
    current_price = closes.iloc[-1]
    
    # Calculate pullback depth
    if primary_trend == 'bullish':
        pullback_depth = ((recent_high - current_price) / recent_high) * 100
        # Look for bounce from support (20, 50 SMA)
        sma_20 = sma(closes, period=20)
        sma_50 = sma(closes, period=50)
        
        support_test = (
            abs(current_price - sma_20.iloc[-1]) / sma_20.iloc[-1] * 100 < 2 or
            abs(current_price - sma_50.iloc[-1]) / sma_50.iloc[-1] * 100 < 2
        )
        
        continuation_probability = (
            80 if pullback_depth > 3 and pullback_depth < 15 and support_test else
            60 if pullback_depth > 1 and pullback_depth < 20 else
            30
        )
    else:
        pullback_depth = ((current_price - recent_low) / recent_low) * 100
        # Look for rejection from resistance
        sma_20 = sma(closes, period=20)
        sma_50 = sma(closes, period=50)
        
        resistance_test = (
            abs(current_price - sma_20.iloc[-1]) / sma_20.iloc[-1] * 100 < 2 or
            abs(current_price - sma_50.iloc[-1]) / sma_50.iloc[-1] * 100 < 2
        )
        
        continuation_probability = (
            80 if pullback_depth > 3 and pullback_depth < 15 and resistance_test else
            60 if pullback_depth > 1 and pullback_depth < 20 else
            30
        )
    
    return {
        'primary_trend': primary_trend,
        'pullback_depth_percent': float(pullback_depth),
        'continuation_probability': continuation_probability,
        'pattern_quality': (
            'excellent' if continuation_probability >= 70 else
            'good' if continuation_probability >= 50 else
            'fair'
        ),
        'entry_signal': continuation_probability >= 60,
        'risk_level': 'low' if pullback_depth < 10 else 'medium' if pullback_depth < 20 else 'high'
    }


# Registry of all pattern recognition functions
PATTERN_FUNCTIONS = {
    'bullish_confluence': bullish_confluence,
    'bearish_confluence': bearish_confluence,
    'squeeze_pattern': squeeze_pattern,
    'trend_continuation_pattern': trend_continuation_pattern
}