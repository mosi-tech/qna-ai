"""
Technical analysis utilities for MCP analytics server.
Provides shared technical analysis functions and pattern detection utilities.
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Tuple, Optional, Any
from scipy import stats
import logging

logger = logging.getLogger(__name__)

def calculate_multiple_timeframe_rsi(df: pd.DataFrame, 
                                   periods: List[int] = [14, 21, 50]) -> Dict:
    """
    Calculate RSI for multiple timeframes using ta library.
    
    Args:
        df: DataFrame with 'close' column
        periods: List of RSI periods to calculate
        
    Returns:
        dict: RSI values for each timeframe
    """
    rsi_data = {}
    
    for period in periods:
        try:
            rsi_values = ta.momentum.rsi(df['close'], window=period)
            rsi_data[f"rsi_{period}"] = {
                "current": float(rsi_values.iloc[-1]) if not pd.isna(rsi_values.iloc[-1]) else None,
                "previous": float(rsi_values.iloc[-2]) if len(rsi_values) > 1 and not pd.isna(rsi_values.iloc[-2]) else None,
                "values": rsi_values.dropna().tail(10).tolist(),
                "overbought": rsi_values.iloc[-1] > 70 if not pd.isna(rsi_values.iloc[-1]) else False,
                "oversold": rsi_values.iloc[-1] < 30 if not pd.isna(rsi_values.iloc[-1]) else False
            }
        except Exception as e:
            logger.warning(f"Failed to calculate RSI for period {period}: {str(e)}")
            rsi_data[f"rsi_{period}"] = None
    
    return rsi_data

def detect_divergence_patterns(price_series: pd.Series, indicator_series: pd.Series, 
                              lookback: int = 20, min_peaks: int = 2) -> Dict:
    """
    Detect bullish and bearish divergence patterns between price and indicator.
    
    Args:
        price_series: Price data (usually high for bearish, low for bullish divergence)
        indicator_series: Technical indicator values (e.g., RSI, MACD)
        lookback: Number of periods to look back for peaks/troughs
        min_peaks: Minimum number of peaks/troughs required
        
    Returns:
        dict: Detected divergence patterns with details
    """
    try:
        # Find peaks and troughs using rolling windows
        price_peaks = find_peaks_and_troughs(price_series, lookback, "peaks")
        price_troughs = find_peaks_and_troughs(price_series, lookback, "troughs")
        indicator_peaks = find_peaks_and_troughs(indicator_series, lookback, "peaks")
        indicator_troughs = find_peaks_and_troughs(indicator_series, lookback, "troughs")
        
        # Detect bearish divergence (higher price peaks, lower indicator peaks)
        bearish_divergences = []
        if len(price_peaks) >= min_peaks and len(indicator_peaks) >= min_peaks:
            for i in range(1, min(len(price_peaks), len(indicator_peaks))):
                price_higher = price_peaks.iloc[i]['value'] > price_peaks.iloc[i-1]['value']
                indicator_lower = indicator_peaks.iloc[i]['value'] < indicator_peaks.iloc[i-1]['value']
                
                if price_higher and indicator_lower:
                    strength = calculate_divergence_strength(
                        price_peaks.iloc[i]['value'], price_peaks.iloc[i-1]['value'],
                        indicator_peaks.iloc[i]['value'], indicator_peaks.iloc[i-1]['value']
                    )
                    
                    bearish_divergences.append({
                        "type": "bearish",
                        "strength": strength,
                        "price_peak_1": float(price_peaks.iloc[i-1]['value']),
                        "price_peak_2": float(price_peaks.iloc[i]['value']),
                        "indicator_peak_1": float(indicator_peaks.iloc[i-1]['value']),
                        "indicator_peak_2": float(indicator_peaks.iloc[i]['value']),
                        "date_1": price_peaks.iloc[i-1]['date'],
                        "date_2": price_peaks.iloc[i]['date']
                    })
        
        # Detect bullish divergence (lower price troughs, higher indicator troughs)
        bullish_divergences = []
        if len(price_troughs) >= min_peaks and len(indicator_troughs) >= min_peaks:
            for i in range(1, min(len(price_troughs), len(indicator_troughs))):
                price_lower = price_troughs.iloc[i]['value'] < price_troughs.iloc[i-1]['value']
                indicator_higher = indicator_troughs.iloc[i]['value'] > indicator_troughs.iloc[i-1]['value']
                
                if price_lower and indicator_higher:
                    strength = calculate_divergence_strength(
                        price_troughs.iloc[i]['value'], price_troughs.iloc[i-1]['value'],
                        indicator_troughs.iloc[i]['value'], indicator_troughs.iloc[i-1]['value']
                    )
                    
                    bullish_divergences.append({
                        "type": "bullish",
                        "strength": strength,
                        "price_trough_1": float(price_troughs.iloc[i-1]['value']),
                        "price_trough_2": float(price_troughs.iloc[i]['value']),
                        "indicator_trough_1": float(indicator_troughs.iloc[i-1]['value']),
                        "indicator_trough_2": float(indicator_troughs.iloc[i]['value']),
                        "date_1": price_troughs.iloc[i-1]['date'],
                        "date_2": price_troughs.iloc[i]['date']
                    })
        
        return {
            "bullish_divergences": bullish_divergences,
            "bearish_divergences": bearish_divergences,
            "total_divergences": len(bullish_divergences) + len(bearish_divergences),
            "strongest_signal": get_strongest_divergence(bullish_divergences + bearish_divergences)
        }
        
    except Exception as e:
        logger.error(f"Divergence detection failed: {str(e)}")
        return {"bullish_divergences": [], "bearish_divergences": [], "total_divergences": 0}

def find_peaks_and_troughs(series: pd.Series, window: int, type_: str) -> pd.DataFrame:
    """
    Find peaks or troughs in a time series.
    
    Args:
        series: Time series data
        window: Rolling window size for peak/trough detection
        type_: "peaks" or "troughs"
        
    Returns:
        DataFrame: Detected peaks or troughs with dates and values
    """
    if type_ == "peaks":
        condition = series == series.rolling(window=window, center=True).max()
    else:  # troughs
        condition = series == series.rolling(window=window, center=True).min()
    
    peaks_troughs = series[condition].dropna()
    
    result_df = pd.DataFrame({
        'date': peaks_troughs.index,
        'value': peaks_troughs.values
    }).reset_index(drop=True)
    
    return result_df

def calculate_divergence_strength(price_1: float, price_2: float, 
                                indicator_1: float, indicator_2: float) -> float:
    """
    Calculate the strength of a divergence pattern.
    
    Args:
        price_1, price_2: Price values for comparison
        indicator_1, indicator_2: Indicator values for comparison
        
    Returns:
        float: Divergence strength (0-1)
    """
    try:
        price_change = abs((price_2 - price_1) / price_1) if price_1 != 0 else 0
        indicator_change = abs((indicator_2 - indicator_1) / indicator_1) if indicator_1 != 0 else 0
        
        # Strength is based on the magnitude of opposing movements
        strength = min(price_change + indicator_change, 1.0)
        return float(strength)
    except:
        return 0.0

def get_strongest_divergence(divergences: List[Dict]) -> Optional[Dict]:
    """Get the strongest divergence from a list."""
    if not divergences:
        return None
    
    return max(divergences, key=lambda x: x.get("strength", 0))

def calculate_trend_strength(df: pd.DataFrame, **kwargs) -> Dict:
    """
    Calculate comprehensive trend strength metrics using multiple indicators.
    
    Args:
        df: DataFrame with OHLC data
        **kwargs: Additional parameters
        
    Returns:
        dict: Trend strength analysis
    """
    try:
        trend_metrics = {}
        
        # Moving average trend
        ma_short = kwargs.get('ma_short', 20)
        ma_long = kwargs.get('ma_long', 50)
        
        sma_short = ta.trend.sma_indicator(df['close'], window=ma_short)
        sma_long = ta.trend.sma_indicator(df['close'], window=ma_long)
        
        current_price = df['close'].iloc[-1]
        ma_trend = "bullish" if current_price > sma_short.iloc[-1] > sma_long.iloc[-1] else \
                  "bearish" if current_price < sma_short.iloc[-1] < sma_long.iloc[-1] else "neutral"
        
        # ADX trend strength
        adx = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
        adx_value = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0
        
        # Trend strength classification
        if adx_value > 25:
            adx_strength = "strong"
        elif adx_value > 20:
            adx_strength = "moderate"
        else:
            adx_strength = "weak"
        
        # MACD trend confirmation
        macd_line = ta.trend.macd_diff(df['close'])
        macd_signal = "bullish" if macd_line.iloc[-1] > 0 else "bearish"
        
        # Volume trend confirmation
        volume_sma = df['volume'].rolling(window=20).mean()
        volume_trend = "increasing" if df['volume'].iloc[-1] > volume_sma.iloc[-1] else "decreasing"
        
        # Composite trend score
        trend_score = calculate_composite_trend_score(ma_trend, adx_strength, macd_signal, volume_trend)
        
        return {
            "overall_trend": determine_overall_trend(ma_trend, macd_signal, trend_score),
            "trend_strength": adx_strength,
            "adx_value": float(adx_value),
            "moving_average_trend": ma_trend,
            "macd_signal": macd_signal,
            "volume_trend": volume_trend,
            "composite_score": trend_score,
            "confidence": calculate_trend_confidence(trend_score, adx_value)
        }
        
    except Exception as e:
        logger.error(f"Trend strength calculation failed: {str(e)}")
        return {"overall_trend": "neutral", "trend_strength": "weak", "confidence": 0.0}

def calculate_composite_trend_score(ma_trend: str, adx_strength: str, 
                                  macd_signal: str, volume_trend: str) -> float:
    """Calculate composite trend score from multiple indicators."""
    score = 0.0
    
    # Moving average component (40% weight)
    if ma_trend == "bullish":
        score += 0.4
    elif ma_trend == "bearish":
        score -= 0.4
    
    # ADX strength component (25% weight)
    if adx_strength == "strong":
        score += 0.25 if score > 0 else -0.25
    elif adx_strength == "moderate":
        score += 0.15 if score > 0 else -0.15
    
    # MACD component (25% weight)
    if macd_signal == "bullish":
        score += 0.25
    elif macd_signal == "bearish":
        score -= 0.25
    
    # Volume component (10% weight)
    if volume_trend == "increasing":
        score += 0.1 if score > 0 else -0.1
    
    return max(-1.0, min(1.0, score))  # Clamp to [-1, 1]

def determine_overall_trend(ma_trend: str, macd_signal: str, trend_score: float) -> str:
    """Determine overall trend from components."""
    if trend_score > 0.3:
        return "bullish"
    elif trend_score < -0.3:
        return "bearish"
    else:
        return "neutral"

def calculate_trend_confidence(trend_score: float, adx_value: float) -> float:
    """Calculate confidence in trend assessment."""
    score_confidence = abs(trend_score)  # Higher absolute score = higher confidence
    adx_confidence = min(adx_value / 50, 1.0)  # ADX contribution to confidence
    
    return (score_confidence * 0.7 + adx_confidence * 0.3)

def detect_support_resistance_levels(df: pd.DataFrame, window: int = 20, 
                                   min_touches: int = 2) -> Dict:
    """
    Detect support and resistance levels using pivot points.
    
    Args:
        df: DataFrame with OHLC data
        window: Window for pivot detection
        min_touches: Minimum touches required for a valid level
        
    Returns:
        dict: Support and resistance levels
    """
    try:
        # Find pivot highs and lows
        pivot_highs = find_peaks_and_troughs(df['high'], window, "peaks")
        pivot_lows = find_peaks_and_troughs(df['low'], window, "troughs")
        
        # Group similar levels (within 1% of each other)
        tolerance = 0.01
        resistance_levels = group_similar_levels(pivot_highs['value'].tolist(), tolerance, min_touches)
        support_levels = group_similar_levels(pivot_lows['value'].tolist(), tolerance, min_touches)
        
        current_price = df['close'].iloc[-1]
        
        # Find nearest levels
        nearest_resistance = find_nearest_level(current_price, resistance_levels, "above")
        nearest_support = find_nearest_level(current_price, support_levels, "below")
        
        return {
            "support_levels": [{"level": level, "strength": strength, "touches": touches} 
                             for level, strength, touches in support_levels],
            "resistance_levels": [{"level": level, "strength": strength, "touches": touches}
                                for level, strength, touches in resistance_levels],
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "current_price": float(current_price),
            "price_position": calculate_price_position(current_price, support_levels, resistance_levels)
        }
        
    except Exception as e:
        logger.error(f"Support/resistance detection failed: {str(e)}")
        return {"support_levels": [], "resistance_levels": [], "current_price": 0.0}

def group_similar_levels(levels: List[float], tolerance: float, min_touches: int) -> List[Tuple[float, float, int]]:
    """Group similar price levels within tolerance."""
    grouped_levels = []
    used_indices = set()
    
    for i, level in enumerate(levels):
        if i in used_indices:
            continue
            
        similar_levels = [level]
        touches = 1
        
        for j, other_level in enumerate(levels[i+1:], i+1):
            if j not in used_indices and abs(level - other_level) / level <= tolerance:
                similar_levels.append(other_level)
                touches += 1
                used_indices.add(j)
        
        if touches >= min_touches:
            avg_level = sum(similar_levels) / len(similar_levels)
            strength = min(touches / 5.0, 1.0)  # Normalize strength
            grouped_levels.append((avg_level, strength, touches))
        
        used_indices.add(i)
    
    return sorted(grouped_levels, key=lambda x: x[1], reverse=True)  # Sort by strength

def find_nearest_level(current_price: float, levels: List[Tuple[float, float, int]], 
                      direction: str) -> Optional[Dict]:
    """Find the nearest support or resistance level."""
    if not levels:
        return None
    
    if direction == "above":
        candidates = [(level, strength, touches) for level, strength, touches in levels if level > current_price]
        if candidates:
            nearest = min(candidates, key=lambda x: x[0])
            return {"level": nearest[0], "strength": nearest[1], "touches": nearest[2], 
                   "distance_percent": (nearest[0] - current_price) / current_price * 100}
    else:  # below
        candidates = [(level, strength, touches) for level, strength, touches in levels if level < current_price]
        if candidates:
            nearest = max(candidates, key=lambda x: x[0])
            return {"level": nearest[0], "strength": nearest[1], "touches": nearest[2],
                   "distance_percent": (current_price - nearest[0]) / current_price * 100}
    
    return None

def calculate_price_position(current_price: float, support_levels: List, resistance_levels: List) -> str:
    """Calculate where current price sits relative to support and resistance."""
    if not support_levels and not resistance_levels:
        return "unknown"
    
    # Count levels above and below
    supports_below = sum(1 for level, _, _ in support_levels if level < current_price)
    resistances_above = sum(1 for level, _, _ in resistance_levels if level > current_price)
    
    if supports_below > 0 and resistances_above > 0:
        return "between_levels"
    elif resistances_above > 0:
        return "below_resistance"
    elif supports_below > 0:
        return "above_support"
    else:
        return "outside_levels"

def calculate_volatility_metrics(df: pd.DataFrame, window: int = 20) -> Dict:
    """
    Calculate comprehensive volatility metrics.
    
    Args:
        df: DataFrame with OHLC data
        window: Rolling window for calculations
        
    Returns:
        dict: Volatility metrics
    """
    try:
        # True Range and ATR
        atr = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=window)
        current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0
        
        # Historical volatility (annualized)
        returns = df['close'].pct_change().dropna()
        hist_vol = returns.rolling(window=window).std() * np.sqrt(252) * 100  # Annualized %
        current_hist_vol = hist_vol.iloc[-1] if not pd.isna(hist_vol.iloc[-1]) else 0
        
        # Bollinger Band width as volatility measure
        bb_upper = ta.volatility.bollinger_hband(df['close'], window=window)
        bb_lower = ta.volatility.bollinger_lband(df['close'], window=window)
        bb_middle = ta.volatility.bollinger_mavg(df['close'], window=window)
        bb_width = ((bb_upper - bb_lower) / bb_middle * 100).iloc[-1] if len(bb_upper) > 0 else 0
        
        # Volatility regime classification
        vol_percentile = hist_vol.rank(pct=True).iloc[-1] if len(hist_vol) > 0 else 0.5
        
        if vol_percentile > 0.8:
            vol_regime = "high"
        elif vol_percentile > 0.6:
            vol_regime = "elevated"
        elif vol_percentile < 0.2:
            vol_regime = "low"
        else:
            vol_regime = "normal"
        
        return {
            "current_atr": float(current_atr),
            "historical_volatility_percent": float(current_hist_vol),
            "bollinger_band_width_percent": float(bb_width),
            "volatility_regime": vol_regime,
            "volatility_percentile": float(vol_percentile),
            "interpretation": interpret_volatility_regime(vol_regime, current_hist_vol)
        }
        
    except Exception as e:
        logger.error(f"Volatility calculation failed: {str(e)}")
        return {"current_atr": 0, "historical_volatility_percent": 0, "volatility_regime": "unknown"}

def interpret_volatility_regime(regime: str, vol_value: float) -> str:
    """Provide interpretation of volatility regime."""
    interpretations = {
        "low": f"Low volatility ({vol_value:.1f}%) suggests stable price action, potential for breakout",
        "normal": f"Normal volatility ({vol_value:.1f}%) indicates typical market conditions",
        "elevated": f"Elevated volatility ({vol_value:.1f}%) suggests increased uncertainty",
        "high": f"High volatility ({vol_value:.1f}%) indicates significant market stress or opportunity"
    }
    return interpretations.get(regime, f"Volatility: {vol_value:.1f}%")