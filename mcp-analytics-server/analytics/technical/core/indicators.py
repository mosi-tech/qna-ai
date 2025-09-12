"""
Core Technical Indicators

This module provides clean, standardized implementations of fundamental technical analysis indicators.
All functions follow consistent patterns:
- Input: pandas Series or DataFrame with OHLCV data
- Output: pandas Series or DataFrame with calculated indicator values
- Parameters: Standard parameter names with sensible defaults
- Error handling: Graceful handling of insufficient data

Dependencies: pandas, numpy, ta (technical analysis library)
"""

import pandas as pd
import numpy as np
import ta
from typing import Union, Optional, Dict, Any


def sma(data: Union[pd.Series, pd.DataFrame], period: int = 20, column: str = 'close') -> pd.Series:
    """
    Simple Moving Average
    
    Args:
        data: Price data (Series or DataFrame)
        period: Period for moving average (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with SMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return prices.rolling(window=period, min_periods=period).mean()


def ema(data: Union[pd.Series, pd.DataFrame], period: int = 20, column: str = 'close') -> pd.Series:
    """
    Exponential Moving Average
    
    Args:
        data: Price data (Series or DataFrame)
        period: Period for moving average (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with EMA values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return prices.ewm(span=period, adjust=False).mean()


def rsi(data: Union[pd.Series, pd.DataFrame], period: int = 14, column: str = 'close') -> pd.Series:
    """
    Relative Strength Index
    
    Args:
        data: Price data (Series or DataFrame)
        period: Period for RSI calculation (default: 14)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with RSI values (0-100)
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return ta.momentum.RSIIndicator(close=prices, window=period).rsi()


def macd(data: Union[pd.Series, pd.DataFrame], fast: int = 12, slow: int = 26, signal: int = 9, 
         column: str = 'close') -> pd.DataFrame:
    """
    MACD (Moving Average Convergence Divergence)
    
    Args:
        data: Price data (Series or DataFrame)
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line EMA period (default: 9)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        DataFrame with columns: macd, signal, histogram
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    macd_indicator = ta.trend.MACD(close=prices, window_fast=fast, window_slow=slow, window_sign=signal)
    
    return pd.DataFrame({
        'macd': macd_indicator.macd(),
        'signal': macd_indicator.macd_signal(),
        'histogram': macd_indicator.macd_diff()
    }, index=prices.index)


def bollinger_bands(data: Union[pd.Series, pd.DataFrame], period: int = 20, std_dev: float = 2.0,
                   column: str = 'close') -> pd.DataFrame:
    """
    Bollinger Bands
    
    Args:
        data: Price data (Series or DataFrame)
        period: Period for moving average (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        DataFrame with columns: upper, middle, lower, width, percent_b
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    bb = ta.volatility.BollingerBands(close=prices, window=period, window_dev=std_dev)
    
    return pd.DataFrame({
        'upper': bb.bollinger_hband(),
        'middle': bb.bollinger_mavg(),
        'lower': bb.bollinger_lband(),
        'width': bb.bollinger_wband(),
        'percent_b': bb.bollinger_pband()
    }, index=prices.index)


def stochastic(data: pd.DataFrame, k_period: int = 14, d_period: int = 3, 
               high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.DataFrame:
    """
    Stochastic Oscillator
    
    Args:
        data: OHLC DataFrame
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        DataFrame with columns: percent_k, percent_d
    """
    stoch = ta.momentum.StochasticOscillator(
        high=data[high_col], low=data[low_col], close=data[close_col],
        window=k_period, smooth_window=d_period
    )
    
    return pd.DataFrame({
        'percent_k': stoch.stoch(),
        'percent_d': stoch.stoch_signal()
    }, index=data.index)


def atr(data: pd.DataFrame, period: int = 14, 
        high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.Series:
    """
    Average True Range
    
    Args:
        data: OHLC DataFrame
        period: Period for ATR (default: 14)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        pandas Series with ATR values
    """
    return ta.volatility.AverageTrueRange(
        high=data[high_col], low=data[low_col], close=data[close_col], window=period
    ).average_true_range()


def adx(data: pd.DataFrame, period: int = 14,
        high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.DataFrame:
    """
    Average Directional Index (ADX) with +DI and -DI
    
    Args:
        data: OHLC DataFrame
        period: Period for ADX (default: 14)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        DataFrame with columns: adx, plus_di, minus_di
    """
    adx_indicator = ta.trend.ADXIndicator(
        high=data[high_col], low=data[low_col], close=data[close_col], window=period
    )
    
    return pd.DataFrame({
        'adx': adx_indicator.adx(),
        'plus_di': adx_indicator.adx_pos(),
        'minus_di': adx_indicator.adx_neg()
    }, index=data.index)


def williams_r(data: pd.DataFrame, period: int = 14,
               high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.Series:
    """
    Williams %R
    
    Args:
        data: OHLC DataFrame
        period: Period for Williams %R (default: 14)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        pandas Series with Williams %R values (-100 to 0)
    """
    return ta.momentum.WilliamsRIndicator(
        high=data[high_col], low=data[low_col], close=data[close_col], lbp=period
    ).williams_r()


def cci(data: pd.DataFrame, period: int = 20,
        high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.Series:
    """
    Commodity Channel Index
    
    Args:
        data: OHLC DataFrame
        period: Period for CCI (default: 20)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        pandas Series with CCI values
    """
    return ta.trend.CCIIndicator(
        high=data[high_col], low=data[low_col], close=data[close_col], window=period
    ).cci()


def obv(data: pd.DataFrame, close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    On Balance Volume
    
    Args:
        data: DataFrame with price and volume data
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with OBV values
    """
    return ta.volume.OnBalanceVolumeIndicator(
        close=data[close_col], volume=data[volume_col]
    ).on_balance_volume()


def vwap(data: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', 
         close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Volume Weighted Average Price
    
    Args:
        data: OHLC+V DataFrame
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with VWAP values
    """
    return ta.volume.VolumeSMAIndicator(
        close=data[close_col], volume=data[volume_col]
    ).volume_sma()


def keltner_channels(data: pd.DataFrame, period: int = 20, multiplier: float = 2.0,
                    high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.DataFrame:
    """
    Keltner Channels
    
    Args:
        data: OHLC DataFrame
        period: Period for EMA and ATR (default: 20)
        multiplier: ATR multiplier (default: 2.0)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        DataFrame with columns: upper, middle, lower
    """
    kc = ta.volatility.KeltnerChannel(
        high=data[high_col], low=data[low_col], close=data[close_col], 
        window=period, window_atr=period, fillna=False, original_version=True
    )
    
    return pd.DataFrame({
        'upper': kc.keltner_channel_hband(),
        'middle': kc.keltner_channel_mband(),
        'lower': kc.keltner_channel_lband()
    }, index=data.index)


def donchian_channels(data: pd.DataFrame, period: int = 20,
                     high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.DataFrame:
    """
    Donchian Channels
    
    Args:
        data: OHLC DataFrame
        period: Period for channel calculation (default: 20)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        DataFrame with columns: upper, middle, lower
    """
    dc = ta.volatility.DonchianChannel(
        high=data[high_col], low=data[low_col], close=data[close_col], window=period
    )
    
    return pd.DataFrame({
        'upper': dc.donchian_channel_hband(),
        'middle': dc.donchian_channel_mband(),
        'lower': dc.donchian_channel_lband()
    }, index=data.index)


def stochastic_rsi(data: Union[pd.Series, pd.DataFrame], period: int = 14, 
                  smooth_k: int = 3, smooth_d: int = 3, column: str = 'close') -> pd.DataFrame:
    """
    Stochastic RSI - RSI applied to Stochastic formula
    
    Args:
        data: Price data (Series or DataFrame)
        period: RSI period (default: 14)
        smooth_k: %K smoothing period (default: 3)
        smooth_d: %D smoothing period (default: 3)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        DataFrame with columns: stoch_rsi_k, stoch_rsi_d
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    stoch_rsi = ta.momentum.StochRSIIndicator(close=prices, window=period, smooth1=smooth_k, smooth2=smooth_d)
    
    return pd.DataFrame({
        'stoch_rsi_k': stoch_rsi.stochrsi_k(),
        'stoch_rsi_d': stoch_rsi.stochrsi_d()
    }, index=prices.index)


def money_flow_index(data: pd.DataFrame, period: int = 14,
                    high_col: str = 'high', low_col: str = 'low', 
                    close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Money Flow Index (MFI) - Volume-weighted RSI
    
    Args:
        data: OHLCV DataFrame
        period: MFI period (default: 14)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with MFI values (0-100)
    """
    return ta.volume.MFIIndicator(
        high=data[high_col], low=data[low_col], close=data[close_col], 
        volume=data[volume_col], window=period
    ).money_flow_index()


def ultimate_oscillator(data: pd.DataFrame, short: int = 7, medium: int = 14, long: int = 28,
                       high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.Series:
    """
    Ultimate Oscillator
    
    Args:
        data: OHLC DataFrame
        short: Short period (default: 7)
        medium: Medium period (default: 14)
        long: Long period (default: 28)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        pandas Series with Ultimate Oscillator values (0-100)
    """
    return ta.momentum.UltimateOscillator(
        high=data[high_col], low=data[low_col], close=data[close_col],
        window1=short, window2=medium, window3=long
    ).ultimate_oscillator()


def awesome_oscillator(data: pd.DataFrame, short: int = 5, long: int = 34,
                      high_col: str = 'high', low_col: str = 'low') -> pd.Series:
    """
    Awesome Oscillator (AO)
    
    Args:
        data: OHLC DataFrame
        short: Short SMA period (default: 5)
        long: Long SMA period (default: 34)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        
    Returns:
        pandas Series with Awesome Oscillator values
    """
    return ta.momentum.AwesomeOscillatorIndicator(
        high=data[high_col], low=data[low_col], window1=short, window2=long
    ).awesome_oscillator()


def rate_of_change(data: Union[pd.Series, pd.DataFrame], period: int = 12, column: str = 'close') -> pd.Series:
    """
    Rate of Change (ROC) / Momentum
    
    Args:
        data: Price data (Series or DataFrame)
        period: Period for ROC calculation (default: 12)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with ROC values (percentage)
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return ta.momentum.ROCIndicator(close=prices, window=period).roc()


def trix(data: Union[pd.Series, pd.DataFrame], period: int = 14, column: str = 'close') -> pd.Series:
    """
    TRIX - Triple Exponential Average Rate of Change
    
    Args:
        data: Price data (Series or DataFrame)
        period: Period for TRIX calculation (default: 14)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with TRIX values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return ta.trend.TRIXIndicator(close=prices, window=period).trix()


def parabolic_sar(data: pd.DataFrame, step: float = 0.02, max_step: float = 0.2,
                 high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.Series:
    """
    Parabolic Stop and Reverse (SAR)
    
    Args:
        data: OHLC DataFrame
        step: Acceleration factor step (default: 0.02)
        max_step: Maximum acceleration factor (default: 0.2)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        pandas Series with Parabolic SAR values
    """
    return ta.trend.PSARIndicator(
        high=data[high_col], low=data[low_col], close=data[close_col],
        step=step, max_step=max_step
    ).psar()


def aroon(data: pd.DataFrame, period: int = 25,
          high_col: str = 'high', low_col: str = 'low') -> pd.DataFrame:
    """
    Aroon Oscillator
    
    Args:
        data: OHLC DataFrame
        period: Aroon period (default: 25)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        
    Returns:
        DataFrame with columns: aroon_up, aroon_down, aroon_indicator
    """
    aroon_indicator = ta.trend.AroonIndicator(high=data[high_col], low=data[low_col], window=period)
    
    return pd.DataFrame({
        'aroon_up': aroon_indicator.aroon_up(),
        'aroon_down': aroon_indicator.aroon_down(),
        'aroon_indicator': aroon_indicator.aroon_indicator()
    }, index=data.index)


def mass_index(data: pd.DataFrame, fast: int = 9, slow: int = 25,
               high_col: str = 'high', low_col: str = 'low') -> pd.Series:
    """
    Mass Index
    
    Args:
        data: OHLC DataFrame
        fast: Fast EMA period (default: 9)
        slow: Slow EMA period (default: 25)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        
    Returns:
        pandas Series with Mass Index values
    """
    return ta.trend.MassIndex(
        high=data[high_col], low=data[low_col], window_fast=fast, window_slow=slow
    ).mass_index()


def chaikin_money_flow(data: pd.DataFrame, period: int = 20,
                      high_col: str = 'high', low_col: str = 'low',
                      close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Chaikin Money Flow (CMF)
    
    Args:
        data: OHLCV DataFrame
        period: CMF period (default: 20)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with CMF values
    """
    return ta.volume.ChaikinMoneyFlowIndicator(
        high=data[high_col], low=data[low_col], close=data[close_col],
        volume=data[volume_col], window=period
    ).chaikin_money_flow()


def accumulation_distribution(data: pd.DataFrame, 
                            high_col: str = 'high', low_col: str = 'low',
                            close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Accumulation/Distribution Line (A/D Line)
    
    Args:
        data: OHLCV DataFrame
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with A/D Line values
    """
    return ta.volume.AccDistIndexIndicator(
        high=data[high_col], low=data[low_col], close=data[close_col], volume=data[volume_col]
    ).acc_dist_index()


def chaikin_oscillator(data: pd.DataFrame, fast: int = 3, slow: int = 10,
                      high_col: str = 'high', low_col: str = 'low',
                      close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Chaikin Oscillator
    
    Args:
        data: OHLCV DataFrame
        fast: Fast EMA period (default: 3)
        slow: Slow EMA period (default: 10)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with Chaikin Oscillator values
    """
    ad_line = accumulation_distribution(data, high_col, low_col, close_col, volume_col)
    return ad_line.ewm(span=fast).mean() - ad_line.ewm(span=slow).mean()


def volume_sma(data: pd.DataFrame, period: int = 20, volume_col: str = 'volume') -> pd.Series:
    """
    Volume Simple Moving Average
    
    Args:
        data: DataFrame with volume data
        period: SMA period (default: 20)
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with Volume SMA values
    """
    return data[volume_col].rolling(window=period, min_periods=period).mean()


def volume_weighted_moving_average(data: pd.DataFrame, period: int = 20,
                                  close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Volume Weighted Moving Average (VWMA)
    
    Args:
        data: DataFrame with price and volume data
        period: VWMA period (default: 20)
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with VWMA values
    """
    return ta.volume.VolumeSMAIndicator(
        close=data[close_col], volume=data[volume_col], window=period
    ).volume_sma()


def ease_of_movement(data: pd.DataFrame, period: int = 14,
                    high_col: str = 'high', low_col: str = 'low', volume_col: str = 'volume') -> pd.Series:
    """
    Ease of Movement (EOM)
    
    Args:
        data: OHLCV DataFrame
        period: EOM period (default: 14)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with EOM values
    """
    return ta.volume.EaseOfMovementIndicator(
        high=data[high_col], low=data[low_col], volume=data[volume_col], window=period
    ).ease_of_movement()


def force_index(data: pd.DataFrame, period: int = 13,
               close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Force Index
    
    Args:
        data: DataFrame with price and volume data
        period: Force Index period (default: 13)
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with Force Index values
    """
    return ta.volume.ForceIndexIndicator(
        close=data[close_col], volume=data[volume_col], window=period
    ).force_index()


def negative_volume_index(data: pd.DataFrame, 
                         close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Negative Volume Index (NVI)
    
    Args:
        data: DataFrame with price and volume data
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with NVI values
    """
    return ta.volume.NegativeVolumeIndexIndicator(
        close=data[close_col], volume=data[volume_col]
    ).negative_volume_index()


def positive_volume_index(data: pd.DataFrame,
                         close_col: str = 'close', volume_col: str = 'volume') -> pd.Series:
    """
    Positive Volume Index (PVI)
    
    Args:
        data: DataFrame with price and volume data
        close_col: Close column name (default: 'close')
        volume_col: Volume column name (default: 'volume')
        
    Returns:
        pandas Series with PVI values
    """
    return ta.volume.PositiveVolumeIndexIndicator(
        close=data[close_col], volume=data[volume_col]
    ).positive_volume_index()


def dpo(data: Union[pd.Series, pd.DataFrame], period: int = 20, column: str = 'close') -> pd.Series:
    """
    Detrended Price Oscillator (DPO)
    
    Args:
        data: Price data (Series or DataFrame)
        period: DPO period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with DPO values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return ta.trend.DPOIndicator(close=prices, window=period).dpo()


def kst(data: Union[pd.Series, pd.DataFrame], r1: int = 10, r2: int = 15, r3: int = 20, r4: int = 30,
        n1: int = 10, n2: int = 10, n3: int = 10, n4: int = 15, column: str = 'close') -> pd.Series:
    """
    Know Sure Thing (KST) Oscillator
    
    Args:
        data: Price data (Series or DataFrame)
        r1, r2, r3, r4: ROC periods (default: 10, 15, 20, 30)
        n1, n2, n3, n4: SMA periods (default: 10, 10, 10, 15)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with KST values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return ta.trend.KSTIndicator(
        close=prices, roc1=r1, roc2=r2, roc3=r3, roc4=r4,
        window1=n1, window2=n2, window3=n3, window4=n4
    ).kst()


def ichimoku(data: pd.DataFrame, tenkan: int = 9, kijun: int = 26, senkou: int = 52,
            high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.DataFrame:
    """
    Ichimoku Kinko Hyo (Ichimoku Cloud)
    
    Args:
        data: OHLC DataFrame
        tenkan: Tenkan-sen period (default: 9)
        kijun: Kijun-sen period (default: 26)
        senkou: Senkou Span B period (default: 52)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        DataFrame with columns: tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span
    """
    ichimoku_indicator = ta.trend.IchimokuIndicator(
        high=data[high_col], low=data[low_col], 
        window1=tenkan, window2=kijun, window3=senkou
    )
    
    return pd.DataFrame({
        'tenkan_sen': ichimoku_indicator.ichimoku_conversion_line(),
        'kijun_sen': ichimoku_indicator.ichimoku_base_line(),
        'senkou_span_a': ichimoku_indicator.ichimoku_a(),
        'senkou_span_b': ichimoku_indicator.ichimoku_b(),
        'chikou_span': data[close_col].shift(-kijun)  # Lagging span
    }, index=data.index)


def supertrend(data: pd.DataFrame, period: int = 10, multiplier: float = 3.0,
              high_col: str = 'high', low_col: str = 'low', close_col: str = 'close') -> pd.DataFrame:
    """
    SuperTrend Indicator
    
    Args:
        data: OHLC DataFrame
        period: ATR period (default: 10)
        multiplier: ATR multiplier (default: 3.0)
        high_col: High column name (default: 'high')
        low_col: Low column name (default: 'low')
        close_col: Close column name (default: 'close')
        
    Returns:
        DataFrame with columns: supertrend, trend (1=bullish, -1=bearish)
    """
    hl2 = (data[high_col] + data[low_col]) / 2
    atr_val = atr(data, period=period, high_col=high_col, low_col=low_col, close_col=close_col)
    
    upper_band = hl2 + (multiplier * atr_val)
    lower_band = hl2 - (multiplier * atr_val)
    
    # Calculate SuperTrend
    supertrend = pd.Series(index=data.index, dtype=float)
    trend = pd.Series(index=data.index, dtype=int)
    
    for i in range(len(data)):
        if i == 0:
            supertrend.iloc[i] = lower_band.iloc[i]
            trend.iloc[i] = 1
        else:
            if data[close_col].iloc[i] > upper_band.iloc[i-1]:
                supertrend.iloc[i] = lower_band.iloc[i]
                trend.iloc[i] = 1
            elif data[close_col].iloc[i] < lower_band.iloc[i-1]:
                supertrend.iloc[i] = upper_band.iloc[i]
                trend.iloc[i] = -1
            else:
                supertrend.iloc[i] = supertrend.iloc[i-1]
                trend.iloc[i] = trend.iloc[i-1]
                
                if trend.iloc[i] == 1 and lower_band.iloc[i] > supertrend.iloc[i-1]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                elif trend.iloc[i] == -1 and upper_band.iloc[i] < supertrend.iloc[i-1]:
                    supertrend.iloc[i] = upper_band.iloc[i]
    
    return pd.DataFrame({
        'supertrend': supertrend,
        'trend': trend
    }, index=data.index)


# Comprehensive registry of all core indicators
CORE_INDICATORS = {
    # Basic Moving Averages
    'sma': sma,
    'ema': ema,
    
    # Momentum Oscillators
    'rsi': rsi,
    'stochastic': stochastic,
    'stochastic_rsi': stochastic_rsi,
    'williams_r': williams_r,
    'cci': cci,
    'money_flow_index': money_flow_index,
    'ultimate_oscillator': ultimate_oscillator,
    'awesome_oscillator': awesome_oscillator,
    'rate_of_change': rate_of_change,
    
    # Trend Indicators
    'macd': macd,
    'adx': adx,
    'trix': trix,
    'parabolic_sar': parabolic_sar,
    'aroon': aroon,
    'mass_index': mass_index,
    'dpo': dpo,
    'kst': kst,
    'ichimoku': ichimoku,
    'supertrend': supertrend,
    
    # Volatility Indicators
    'bollinger_bands': bollinger_bands,
    'atr': atr,
    'keltner_channels': keltner_channels,
    'donchian_channels': donchian_channels,
    
    # Volume Indicators
    'obv': obv,
    'vwap': vwap,
    'chaikin_money_flow': chaikin_money_flow,
    'accumulation_distribution': accumulation_distribution,
    'chaikin_oscillator': chaikin_oscillator,
    'volume_sma': volume_sma,
    'volume_weighted_moving_average': volume_weighted_moving_average,
    'ease_of_movement': ease_of_movement,
    'force_index': force_index,
    'negative_volume_index': negative_volume_index,
    'positive_volume_index': positive_volume_index
}