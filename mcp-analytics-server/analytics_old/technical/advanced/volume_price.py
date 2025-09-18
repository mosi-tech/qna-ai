"""
Volume-Price Analysis Indicators

Volume-price analysis indicators missing from core module:
- Volume Rate of Change (VROC)
- Price Volume Trend (PVT)
- Volume Oscillator
- Klinger Volume Oscillator (different from standard Klinger)
- Arms Index (TRIN)
- Volume Weighted RSI

All functions follow consistent patterns:
- Input: pandas Series or DataFrame with OHLCV data
- Output: pandas Series or DataFrame with calculated indicator values
- Parameters: Standard parameter names with sensible defaults
"""

import pandas as pd
import numpy as np
from typing import Union, Optional


def volume_rate_of_change(data: Union[pd.Series, pd.DataFrame], period: int = 12,
                         column: str = 'volume') -> pd.Series:
    """
    Volume Rate of Change (VROC)
    
    Measures the rate of change in volume over a specified period.
    
    Args:
        data: Volume data (Series or DataFrame)
        period: VROC period (default: 12)
        column: Column name if DataFrame (default: 'volume')
        
    Returns:
        pandas Series with VROC values
    """
    volume = data[column] if isinstance(data, pd.DataFrame) else data
    vroc = ((volume - volume.shift(period)) / volume.shift(period)) * 100
    return vroc


def price_volume_trend(data: pd.DataFrame) -> pd.Series:
    """
    Price Volume Trend (PVT)
    
    Combines price and volume to show the flow of money into and out of a security.
    
    Args:
        data: DataFrame with close and volume columns
        
    Returns:
        pandas Series with PVT values
    """
    if not all(col in data.columns for col in ['close', 'volume']):
        raise ValueError("Data must contain 'close' and 'volume' columns")
    
    # Calculate price change percentage
    price_change_pct = data['close'].pct_change()
    
    # Calculate PVT
    pvt = (price_change_pct * data['volume']).cumsum()
    return pvt


def volume_oscillator(data: Union[pd.Series, pd.DataFrame], fast_period: int = 5,
                     slow_period: int = 10, column: str = 'volume') -> pd.Series:
    """
    Volume Oscillator
    
    Shows the relationship between two different period volume moving averages.
    
    Args:
        data: Volume data (Series or DataFrame)
        fast_period: Fast moving average period (default: 5)
        slow_period: Slow moving average period (default: 10)
        column: Column name if DataFrame (default: 'volume')
        
    Returns:
        pandas Series with volume oscillator values
    """
    volume = data[column] if isinstance(data, pd.DataFrame) else data
    
    fast_ma = volume.rolling(window=fast_period).mean()
    slow_ma = volume.rolling(window=slow_period).mean()
    
    vol_osc = ((fast_ma - slow_ma) / slow_ma) * 100
    return vol_osc


def klinger_volume_oscillator(data: pd.DataFrame, fast_period: int = 34,
                             slow_period: int = 55, signal_period: int = 13) -> pd.DataFrame:
    """
    Klinger Volume Oscillator (Enhanced Version)
    
    Enhanced version of Klinger Oscillator with additional trend filtering.
    
    Args:
        data: DataFrame with OHLCV data
        fast_period: Fast EMA period (default: 34)
        slow_period: Slow EMA period (default: 55)
        signal_period: Signal line period (default: 13)
        
    Returns:
        DataFrame with klinger_vo, signal, and trend columns
    """
    if not all(col in data.columns for col in ['high', 'low', 'close', 'volume']):
        raise ValueError("Data must contain 'high', 'low', 'close', 'volume' columns")
    
    # Calculate typical price and trend
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    dm = data['high'] - data['low']  # Daily range
    cm = typical_price.diff()  # Change in typical price
    
    # Determine trend direction
    trend = np.where(cm > 0, 1, -1)
    
    # Calculate volume force with trend consideration
    sv = data['volume'] * trend * np.abs(2 * cm / dm)
    sv = pd.Series(sv, index=data.index).fillna(0)
    
    # Apply EMAs
    fast_ema = sv.ewm(span=fast_period).mean()
    slow_ema = sv.ewm(span=slow_period).mean()
    
    klinger_vo = fast_ema - slow_ema
    signal = klinger_vo.ewm(span=signal_period).mean()
    
    return pd.DataFrame({
        'klinger_vo': klinger_vo,
        'signal': signal,
        'trend': pd.Series(trend, index=data.index)
    }, index=data.index)


def arms_index(data: pd.DataFrame, advancing_vol: Optional[pd.Series] = None,
               declining_vol: Optional[pd.Series] = None) -> pd.Series:
    """
    Arms Index (TRIN - Trading Index)
    
    Measures the relationship between advancing and declining stocks and their volume.
    For single stock, uses high/low logic as proxy.
    
    Args:
        data: DataFrame with OHLCV data
        advancing_vol: Optional series of advancing volume (for market-wide calculation)
        declining_vol: Optional series of declining volume (for market-wide calculation)
        
    Returns:
        pandas Series with TRIN values
    """
    if advancing_vol is not None and declining_vol is not None:
        # Market-wide calculation
        advancing_issues = len([1])  # Placeholder - would need market data
        declining_issues = len([1])  # Placeholder - would need market data
        
        adv_dec_ratio = advancing_issues / declining_issues
        adv_dec_vol_ratio = advancing_vol / declining_vol
        
        trin = adv_dec_ratio / adv_dec_vol_ratio
        return trin
    else:
        # Single stock approximation using price action
        if not all(col in data.columns for col in ['high', 'low', 'close', 'volume']):
            raise ValueError("Data must contain 'high', 'low', 'close', 'volume' columns")
        
        # Use close vs midpoint as advancing/declining proxy
        midpoint = (data['high'] + data['low']) / 2
        up_moves = data['close'] > midpoint
        down_moves = data['close'] < midpoint
        
        # Calculate volume ratios
        up_volume = np.where(up_moves, data['volume'], 0)
        down_volume = np.where(down_moves, data['volume'], 0)
        
        # Smooth to avoid division by zero
        up_vol_ma = pd.Series(up_volume).rolling(window=5).mean()
        down_vol_ma = pd.Series(down_volume).rolling(window=5).mean()
        
        # Calculate Arms Index approximation
        trin = (up_vol_ma + 1) / (down_vol_ma + 1)  # Add 1 to avoid zero division
        
        return trin


def volume_weighted_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Volume Weighted RSI
    
    RSI calculation weighted by volume to give more importance to high-volume periods.
    
    Args:
        data: DataFrame with close and volume columns
        period: RSI period (default: 14)
        
    Returns:
        pandas Series with Volume Weighted RSI values
    """
    if not all(col in data.columns for col in ['close', 'volume']):
        raise ValueError("Data must contain 'close' and 'volume' columns")
    
    # Calculate price changes
    price_change = data['close'].diff()
    
    # Separate gains and losses weighted by volume
    gains = np.where(price_change > 0, price_change * data['volume'], 0)
    losses = np.where(price_change < 0, -price_change * data['volume'], 0)
    
    gains_series = pd.Series(gains, index=data.index)
    losses_series = pd.Series(losses, index=data.index)
    
    # Calculate volume-weighted averages
    gain_vol_sum = gains_series.rolling(window=period).sum()
    loss_vol_sum = losses_series.rolling(window=period).sum()
    total_vol = data['volume'].rolling(window=period).sum()
    
    # Volume-weighted average gains and losses
    avg_gain = gain_vol_sum / total_vol
    avg_loss = loss_vol_sum / total_vol
    
    # Calculate RSI
    rs = avg_gain / (avg_loss + 1e-10)  # Add small value to avoid division by zero
    vw_rsi = 100 - (100 / (1 + rs))
    
    return vw_rsi


def volume_accumulation_oscillator(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Volume Accumulation Oscillator
    
    Measures the accumulation or distribution based on volume and price action.
    
    Args:
        data: DataFrame with OHLCV data
        period: Oscillator period (default: 14)
        
    Returns:
        pandas Series with Volume Accumulation Oscillator values
    """
    if not all(col in data.columns for col in ['high', 'low', 'close', 'volume']):
        raise ValueError("Data must contain 'high', 'low', 'close', 'volume' columns")
    
    # Calculate Close Location Value (CLV)
    clv = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])
    clv = clv.fillna(0)  # Handle division by zero when high == low
    
    # Volume weighted CLV
    volume_clv = clv * data['volume']
    
    # Create oscillator using rolling sum
    accumulation = volume_clv.rolling(window=period).sum()
    total_volume = data['volume'].rolling(window=period).sum()
    
    vao = (accumulation / total_volume) * 100
    return vao


def money_flow_oscillator(data: pd.DataFrame, period: int = 10) -> pd.Series:
    """
    Money Flow Oscillator
    
    Similar to MFI but designed as an oscillator around zero line.
    
    Args:
        data: DataFrame with OHLCV data
        period: Oscillator period (default: 10)
        
    Returns:
        pandas Series with Money Flow Oscillator values
    """
    if not all(col in data.columns for col in ['high', 'low', 'close', 'volume']):
        raise ValueError("Data must contain 'high', 'low', 'close', 'volume' columns")
    
    # Calculate typical price and money flow
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    money_flow = typical_price * data['volume']
    
    # Separate positive and negative money flow
    price_change = typical_price.diff()
    positive_mf = np.where(price_change > 0, money_flow, 0)
    negative_mf = np.where(price_change < 0, money_flow, 0)
    
    # Rolling sums
    positive_mf_sum = pd.Series(positive_mf).rolling(window=period).sum()
    negative_mf_sum = pd.Series(negative_mf).rolling(window=period).sum()
    
    # Money Flow Oscillator (centered around 0)
    mf_oscillator = ((positive_mf_sum - negative_mf_sum) / 
                     (positive_mf_sum + negative_mf_sum + 1e-10)) * 100
    
    return mf_oscillator


# Registry of all volume-price analysis functions
VOLUME_PRICE_INDICATORS = {
    'volume_rate_of_change': volume_rate_of_change,
    'price_volume_trend': price_volume_trend,
    'volume_oscillator': volume_oscillator,
    'klinger_volume_oscillator': klinger_volume_oscillator,
    'arms_index': arms_index,
    'volume_weighted_rsi': volume_weighted_rsi,
    'volume_accumulation_oscillator': volume_accumulation_oscillator,
    'money_flow_oscillator': money_flow_oscillator
}


def get_volume_price_function_names():
    """Get list of all volume-price analysis function names"""
    return list(VOLUME_PRICE_INDICATORS.keys())