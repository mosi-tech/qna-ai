"""
Market Structure Indicators

Market structure analysis indicators:
- Pivot Points (Traditional, Fibonacci, Woodie's, Camarilla)
- Support and Resistance levels
- Swing High/Low detection
- Market Profile concepts
- Fractal analysis
- Zigzag indicator

All functions follow consistent patterns:
- Input: pandas Series or DataFrame with OHLCV data
- Output: pandas Series or DataFrame with calculated indicator values
- Parameters: Standard parameter names with sensible defaults
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, List, Tuple


def traditional_pivot_points(data: pd.DataFrame) -> pd.DataFrame:
    """
    Traditional Pivot Points
    
    Calculates traditional pivot point levels using previous period's OHLC.
    
    Args:
        data: DataFrame with OHLC data
        
    Returns:
        DataFrame with pivot point levels: pp, r1, r2, r3, s1, s2, s3
    """
    if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
        raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
    
    # Use previous day's data for calculation
    high = data['high'].shift(1)
    low = data['low'].shift(1)
    close = data['close'].shift(1)
    
    # Pivot Point
    pp = (high + low + close) / 3
    
    # Resistance levels
    r1 = 2 * pp - low
    r2 = pp + (high - low)
    r3 = high + 2 * (pp - low)
    
    # Support levels
    s1 = 2 * pp - high
    s2 = pp - (high - low)
    s3 = low - 2 * (high - pp)
    
    return pd.DataFrame({
        'pp': pp,
        'r1': r1, 'r2': r2, 'r3': r3,
        's1': s1, 's2': s2, 's3': s3
    }, index=data.index)


def fibonacci_pivot_points(data: pd.DataFrame) -> pd.DataFrame:
    """
    Fibonacci Pivot Points
    
    Uses Fibonacci ratios for support and resistance calculation.
    
    Args:
        data: DataFrame with OHLC data
        
    Returns:
        DataFrame with Fibonacci pivot levels
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("Data must contain 'high', 'low', 'close' columns")
    
    # Use previous day's data
    high = data['high'].shift(1)
    low = data['low'].shift(1) 
    close = data['close'].shift(1)
    
    # Pivot Point
    pp = (high + low + close) / 3
    range_hl = high - low
    
    # Fibonacci levels
    r1 = pp + 0.382 * range_hl
    r2 = pp + 0.618 * range_hl
    r3 = pp + range_hl
    
    s1 = pp - 0.382 * range_hl
    s2 = pp - 0.618 * range_hl
    s3 = pp - range_hl
    
    return pd.DataFrame({
        'pp': pp,
        'r1': r1, 'r2': r2, 'r3': r3,
        's1': s1, 's2': s2, 's3': s3
    }, index=data.index)


def woodie_pivot_points(data: pd.DataFrame) -> pd.DataFrame:
    """
    Woodie's Pivot Points
    
    Gives more weight to closing price in pivot calculation.
    
    Args:
        data: DataFrame with OHLC data
        
    Returns:
        DataFrame with Woodie's pivot levels
    """
    if not all(col in data.columns for col in ['high', 'low', 'close', 'open']):
        raise ValueError("Data must contain 'high', 'low', 'close', 'open' columns")
    
    # Use previous day's data
    high = data['high'].shift(1)
    low = data['low'].shift(1)
    close = data['close'].shift(1) 
    open_price = data['open']  # Current day's open
    
    # Woodie's Pivot Point
    pp = (high + low + 2 * close) / 4
    
    # Resistance levels
    r1 = 2 * pp - low
    r2 = pp + high - low
    r3 = r1 + high - low
    
    # Support levels  
    s1 = 2 * pp - high
    s2 = pp - high + low
    s3 = s1 - high + low
    
    return pd.DataFrame({
        'pp': pp,
        'r1': r1, 'r2': r2, 'r3': r3,
        's1': s1, 's2': s2, 's3': s3
    }, index=data.index)


def camarilla_pivot_points(data: pd.DataFrame) -> pd.DataFrame:
    """
    Camarilla Pivot Points
    
    Uses smaller multipliers, focusing on intraday trading.
    
    Args:
        data: DataFrame with OHLC data
        
    Returns:
        DataFrame with Camarilla pivot levels
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("Data must contain 'high', 'low', 'close' columns")
    
    # Use previous day's data
    high = data['high'].shift(1)
    low = data['low'].shift(1)
    close = data['close'].shift(1)
    
    range_hl = high - low
    
    # Camarilla levels
    r1 = close + range_hl * 1.1 / 12
    r2 = close + range_hl * 1.1 / 6  
    r3 = close + range_hl * 1.1 / 4
    r4 = close + range_hl * 1.1 / 2
    
    s1 = close - range_hl * 1.1 / 12
    s2 = close - range_hl * 1.1 / 6
    s3 = close - range_hl * 1.1 / 4
    s4 = close - range_hl * 1.1 / 2
    
    return pd.DataFrame({
        'pp': close,
        'r1': r1, 'r2': r2, 'r3': r3, 'r4': r4,
        's1': s1, 's2': s2, 's3': s3, 's4': s4
    }, index=data.index)


def swing_high_low(data: pd.DataFrame, period: int = 5) -> pd.DataFrame:
    """
    Swing High/Low Detection
    
    Identifies swing highs and lows in price data.
    
    Args:
        data: DataFrame with OHLC data
        period: Period for swing detection (default: 5)
        
    Returns:
        DataFrame with swing_high and swing_low columns
    """
    if not all(col in data.columns for col in ['high', 'low']):
        raise ValueError("Data must contain 'high', 'low' columns")
    
    high = data['high']
    low = data['low']
    
    # Initialize swing arrays
    swing_high = pd.Series(np.nan, index=data.index)
    swing_low = pd.Series(np.nan, index=data.index)
    
    for i in range(period, len(data) - period):
        # Check for swing high
        center_high = high.iloc[i]
        left_highs = high.iloc[i-period:i]
        right_highs = high.iloc[i+1:i+period+1]
        
        if all(center_high >= left_highs) and all(center_high >= right_highs):
            swing_high.iloc[i] = center_high
            
        # Check for swing low  
        center_low = low.iloc[i]
        left_lows = low.iloc[i-period:i]
        right_lows = low.iloc[i+1:i+period+1]
        
        if all(center_low <= left_lows) and all(center_low <= right_lows):
            swing_low.iloc[i] = center_low
    
    return pd.DataFrame({
        'swing_high': swing_high,
        'swing_low': swing_low
    }, index=data.index)


def support_resistance_levels(data: pd.DataFrame, period: int = 20,
                             min_touches: int = 2, tolerance: float = 0.01) -> pd.DataFrame:
    """
    Support and Resistance Level Detection
    
    Identifies key support and resistance levels based on price touches.
    
    Args:
        data: DataFrame with OHLC data  
        period: Period for level detection (default: 20)
        min_touches: Minimum touches to confirm level (default: 2)
        tolerance: Price tolerance as percentage (default: 0.01 = 1%)
        
    Returns:
        DataFrame with support and resistance levels
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("Data must contain 'high', 'low', 'close' columns")
    
    # Get swing points
    swings = swing_high_low(data, period//4)
    
    # Extract non-null swing levels
    swing_highs = swings['swing_high'].dropna()
    swing_lows = swings['swing_low'].dropna()
    
    # Find resistance levels
    resistance_levels = []
    for level in swing_highs:
        touches = sum(abs(data['high'] - level) <= level * tolerance)
        if touches >= min_touches:
            resistance_levels.append(level)
    
    # Find support levels  
    support_levels = []
    for level in swing_lows:
        touches = sum(abs(data['low'] - level) <= level * tolerance)
        if touches >= min_touches:
            support_levels.append(level)
    
    # Create result DataFrame
    max_levels = max(len(support_levels), len(resistance_levels))
    
    support_cols = {}
    resistance_cols = {}
    
    for i in range(max_levels):
        if i < len(support_levels):
            support_cols[f'support_{i+1}'] = support_levels[i]
        if i < len(resistance_levels):
            resistance_cols[f'resistance_{i+1}'] = resistance_levels[i]
    
    # Broadcast to full index
    result_data = {}
    for col, val in {**support_cols, **resistance_cols}.items():
        result_data[col] = pd.Series(val, index=data.index)
    
    return pd.DataFrame(result_data, index=data.index)


def zigzag_indicator(data: Union[pd.Series, pd.DataFrame], threshold: float = 0.05,
                    column: str = 'close') -> pd.DataFrame:
    """
    ZigZag Indicator
    
    Filters out small price movements to show significant reversals.
    
    Args:
        data: Price data (Series or DataFrame)
        threshold: Minimum percentage change to register (default: 0.05 = 5%)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        DataFrame with zigzag values and signals
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    zigzag = pd.Series(np.nan, index=prices.index)
    direction = pd.Series(0, index=prices.index)  # 1 for up, -1 for down
    
    # Initialize
    zigzag.iloc[0] = prices.iloc[0]
    last_pivot = prices.iloc[0]
    last_pivot_idx = 0
    current_direction = 0
    
    for i in range(1, len(prices)):
        current_price = prices.iloc[i]
        
        # Calculate percentage change from last pivot
        pct_change = (current_price - last_pivot) / last_pivot
        
        if current_direction == 0:
            # No direction established yet
            if abs(pct_change) >= threshold:
                current_direction = 1 if pct_change > 0 else -1
                zigzag.iloc[i] = current_price
                direction.iloc[i] = current_direction
                last_pivot = current_price
                last_pivot_idx = i
        
        elif current_direction == 1:
            # Currently in uptrend
            if current_price > last_pivot:
                # New high, update pivot
                zigzag.iloc[last_pivot_idx] = np.nan  # Clear old pivot
                zigzag.iloc[i] = current_price
                direction.iloc[i] = 1
                last_pivot = current_price
                last_pivot_idx = i
            elif pct_change <= -threshold:
                # Reversal to downtrend
                current_direction = -1
                zigzag.iloc[i] = current_price
                direction.iloc[i] = -1
                last_pivot = current_price
                last_pivot_idx = i
        
        else:  # current_direction == -1
            # Currently in downtrend
            if current_price < last_pivot:
                # New low, update pivot
                zigzag.iloc[last_pivot_idx] = np.nan  # Clear old pivot
                zigzag.iloc[i] = current_price
                direction.iloc[i] = -1
                last_pivot = current_price
                last_pivot_idx = i
            elif pct_change >= threshold:
                # Reversal to uptrend
                current_direction = 1
                zigzag.iloc[i] = current_price
                direction.iloc[i] = 1
                last_pivot = current_price
                last_pivot_idx = i
    
    return pd.DataFrame({
        'zigzag': zigzag,
        'direction': direction
    }, index=prices.index)


def market_profile_basic(data: pd.DataFrame, session_hours: int = 6) -> pd.DataFrame:
    """
    Basic Market Profile Analysis
    
    Simplified market profile showing value areas and point of control.
    
    Args:
        data: DataFrame with OHLCV data
        session_hours: Hours per trading session (default: 6)
        
    Returns:
        DataFrame with poc (Point of Control), value_area_high, value_area_low
    """
    if not all(col in data.columns for col in ['high', 'low', 'close', 'volume']):
        raise ValueError("Data must contain 'high', 'low', 'close', 'volume' columns")
    
    poc = pd.Series(index=data.index, dtype=float)
    vah = pd.Series(index=data.index, dtype=float)  # Value Area High
    val = pd.Series(index=data.index, dtype=float)  # Value Area Low
    
    # Use rolling window to simulate sessions
    session_length = session_hours
    
    for i in range(session_length, len(data)):
        session_data = data.iloc[i-session_length:i]
        
        # Create price-volume histogram
        price_range = session_data['high'].max() - session_data['low'].min()
        if price_range > 0:
            # Divide price range into bins
            num_bins = min(20, max(5, int(price_range / (session_data['close'].std() * 0.1))))
            
            bins = np.linspace(session_data['low'].min(), session_data['high'].max(), num_bins)
            volume_profile = np.zeros(num_bins - 1)
            
            # Distribute volume across price levels
            for _, row in session_data.iterrows():
                # Simple approximation: distribute volume evenly across OHLC range
                prices = [row['open'], row['high'], row['low'], row['close']]
                for price in prices:
                    if not np.isnan(price):
                        bin_idx = min(len(volume_profile) - 1, 
                                     max(0, int((price - bins[0]) / (bins[1] - bins[0]))))
                        volume_profile[bin_idx] += row['volume'] / 4
            
            # Find Point of Control (highest volume price level)
            poc_idx = np.argmax(volume_profile)
            poc.iloc[i] = (bins[poc_idx] + bins[poc_idx + 1]) / 2
            
            # Find Value Area (70% of volume)
            total_volume = volume_profile.sum()
            target_volume = total_volume * 0.7
            
            # Expand around POC to capture 70% of volume
            current_volume = volume_profile[poc_idx]
            left_idx = right_idx = poc_idx
            
            while current_volume < target_volume and (left_idx > 0 or right_idx < len(volume_profile) - 1):
                left_volume = volume_profile[left_idx - 1] if left_idx > 0 else 0
                right_volume = volume_profile[right_idx + 1] if right_idx < len(volume_profile) - 1 else 0
                
                if left_volume >= right_volume and left_idx > 0:
                    left_idx -= 1
                    current_volume += volume_profile[left_idx]
                elif right_idx < len(volume_profile) - 1:
                    right_idx += 1
                    current_volume += volume_profile[right_idx]
                else:
                    break
            
            vah.iloc[i] = bins[right_idx + 1] if right_idx < len(bins) - 1 else bins[-1]
            val.iloc[i] = bins[left_idx]
    
    return pd.DataFrame({
        'poc': poc,
        'value_area_high': vah,
        'value_area_low': val
    }, index=data.index)


def volume_weighted_average_price_session(data: pd.DataFrame, session_length: int = 390) -> pd.Series:
    """
    Session VWAP
    
    Volume Weighted Average Price calculated over trading sessions.
    
    Args:
        data: DataFrame with price and volume data
        session_length: Length of trading session in periods (default: 390 for minutes in trading day)
        
    Returns:
        pandas Series with session VWAP values
    """
    if not all(col in data.columns for col in ['close', 'volume']):
        raise ValueError("Data must contain 'close' and 'volume' columns")
    
    session_vwap = pd.Series(index=data.index, dtype=float)
    
    # Calculate typical price if OHLC available
    if all(col in data.columns for col in ['high', 'low', 'close']):
        typical_price = (data['high'] + data['low'] + data['close']) / 3
    else:
        typical_price = data['close']
    
    for i in range(session_length, len(data)):
        session_data = data.iloc[i-session_length:i]
        session_typical = typical_price.iloc[i-session_length:i]
        
        # Calculate VWAP for session
        pv = (session_typical * session_data['volume']).sum()
        total_volume = session_data['volume'].sum()
        
        if total_volume > 0:
            session_vwap.iloc[i] = pv / total_volume
    
    return session_vwap


def fractal_analysis(data: pd.DataFrame, period: int = 5) -> pd.DataFrame:
    """
    Fractal Analysis
    
    Identifies fractal highs and lows (Williams Fractals).
    
    Args:
        data: DataFrame with OHLC data
        period: Period for fractal detection (default: 5, must be odd)
        
    Returns:
        DataFrame with fractal_high and fractal_low columns
    """
    if not all(col in data.columns for col in ['high', 'low']):
        raise ValueError("Data must contain 'high', 'low' columns")
    
    if period % 2 == 0:
        period += 1  # Ensure odd number
    
    high = data['high']
    low = data['low']
    center = period // 2
    
    fractal_high = pd.Series(np.nan, index=data.index)
    fractal_low = pd.Series(np.nan, index=data.index)
    
    for i in range(center, len(data) - center):
        # Check for fractal high
        center_high = high.iloc[i]
        surrounding_highs = [high.iloc[i+j] for j in range(-center, center+1) if j != 0]
        
        if all(center_high > h for h in surrounding_highs):
            fractal_high.iloc[i] = center_high
        
        # Check for fractal low
        center_low = low.iloc[i]
        surrounding_lows = [low.iloc[i+j] for j in range(-center, center+1) if j != 0]
        
        if all(center_low < l for l in surrounding_lows):
            fractal_low.iloc[i] = center_low
    
    return pd.DataFrame({
        'fractal_high': fractal_high,
        'fractal_low': fractal_low
    }, index=data.index)


# Registry of all market structure functions
MARKET_STRUCTURE_INDICATORS = {
    'traditional_pivot_points': traditional_pivot_points,
    'fibonacci_pivot_points': fibonacci_pivot_points,
    'woodie_pivot_points': woodie_pivot_points,
    'camarilla_pivot_points': camarilla_pivot_points,
    'swing_high_low': swing_high_low,
    'support_resistance_levels': support_resistance_levels,
    'zigzag_indicator': zigzag_indicator,
    'fractal_analysis': fractal_analysis,
    'market_profile_basic': market_profile_basic,
    'volume_weighted_average_price_session': volume_weighted_average_price_session
}


def get_market_structure_function_names():
    """Get list of all market structure function names"""
    return list(MARKET_STRUCTURE_INDICATORS.keys())