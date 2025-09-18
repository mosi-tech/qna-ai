"""
Advanced Volatility Indicators

Missing volatility indicators not available in the core module:
- Standard Deviation
- Historical Volatility
- Garman-Klass Volatility
- Parkinson's Volatility
- Rogers-Satchell Volatility
- Yang-Zhang Volatility
- Relative Volatility Index (RVI)
- Volatility Ratio

All functions follow consistent patterns:
- Input: pandas Series or DataFrame with OHLCV data
- Output: pandas Series or DataFrame with calculated indicator values
- Parameters: Standard parameter names with sensible defaults
"""

import pandas as pd
import numpy as np
from typing import Union, Optional


def standard_deviation(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                      column: str = 'close') -> pd.Series:
    """
    Rolling Standard Deviation
    
    Measures price dispersion from the mean.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Rolling period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with standard deviation values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    return prices.rolling(window=period).std()


def historical_volatility(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                         annualize: bool = True, column: str = 'close') -> pd.Series:
    """
    Historical Volatility
    
    Annualized standard deviation of returns.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Rolling period (default: 20)
        annualize: Whether to annualize the volatility (default: True)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with historical volatility values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    returns = prices.pct_change()
    vol = returns.rolling(window=period).std()
    
    if annualize:
        vol *= np.sqrt(252)  # Assume 252 trading days per year
    
    return vol


def garman_klass_volatility(data: pd.DataFrame, period: int = 20,
                           annualize: bool = True) -> pd.Series:
    """
    Garman-Klass Volatility Estimator
    
    Uses high, low, open, close prices for better volatility estimation.
    
    Args:
        data: DataFrame with OHLC data
        period: Rolling period (default: 20)
        annualize: Whether to annualize the volatility (default: True)
        
    Returns:
        pandas Series with Garman-Klass volatility values
    """
    if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
        raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
    
    # Garman-Klass estimator
    log_hl = np.log(data['high'] / data['low'])
    log_co = np.log(data['close'] / data['open'])
    
    gk_vol = 0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2
    rolling_gk_vol = gk_vol.rolling(window=period).mean()
    
    vol = np.sqrt(rolling_gk_vol)
    
    if annualize:
        vol *= np.sqrt(252)
    
    return vol


def parkinson_volatility(data: pd.DataFrame, period: int = 20,
                        annualize: bool = True) -> pd.Series:
    """
    Parkinson's Volatility Estimator
    
    Uses only high and low prices to estimate volatility.
    
    Args:
        data: DataFrame with OHLC data
        period: Rolling period (default: 20)
        annualize: Whether to annualize the volatility (default: True)
        
    Returns:
        pandas Series with Parkinson volatility values
    """
    if not all(col in data.columns for col in ['high', 'low']):
        raise ValueError("Data must contain 'high', 'low' columns")
    
    # Parkinson estimator
    log_hl = np.log(data['high'] / data['low'])
    parkinson_vol = log_hl**2 / (4 * np.log(2))
    rolling_parkinson_vol = parkinson_vol.rolling(window=period).mean()
    
    vol = np.sqrt(rolling_parkinson_vol)
    
    if annualize:
        vol *= np.sqrt(252)
    
    return vol


def rogers_satchell_volatility(data: pd.DataFrame, period: int = 20,
                              annualize: bool = True) -> pd.Series:
    """
    Rogers-Satchell Volatility Estimator
    
    Drift-independent volatility estimator using OHLC data.
    
    Args:
        data: DataFrame with OHLC data
        period: Rolling period (default: 20)
        annualize: Whether to annualize the volatility (default: True)
        
    Returns:
        pandas Series with Rogers-Satchell volatility values
    """
    if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
        raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
    
    # Rogers-Satchell estimator
    log_ho = np.log(data['high'] / data['open'])
    log_hc = np.log(data['high'] / data['close'])
    log_lo = np.log(data['low'] / data['open'])
    log_lc = np.log(data['low'] / data['close'])
    
    rs_vol = log_ho * log_hc + log_lo * log_lc
    rolling_rs_vol = rs_vol.rolling(window=period).mean()
    
    vol = np.sqrt(rolling_rs_vol)
    
    if annualize:
        vol *= np.sqrt(252)
    
    return vol


def yang_zhang_volatility(data: pd.DataFrame, period: int = 20,
                         annualize: bool = True) -> pd.Series:
    """
    Yang-Zhang Volatility Estimator
    
    Combines overnight and intraday volatility estimates.
    
    Args:
        data: DataFrame with OHLC data
        period: Rolling period (default: 20)
        annualize: Whether to annualize the volatility (default: True)
        
    Returns:
        pandas Series with Yang-Zhang volatility values
    """
    if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
        raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
    
    # Overnight volatility (close to open)
    log_co = np.log(data['open'] / data['close'].shift(1))
    overnight_vol = log_co.rolling(window=period).var()
    
    # Open to close volatility
    log_oc = np.log(data['close'] / data['open'])
    oc_vol = log_oc.rolling(window=period).var()
    
    # Rogers-Satchell component
    log_ho = np.log(data['high'] / data['open'])
    log_hc = np.log(data['high'] / data['close'])
    log_lo = np.log(data['low'] / data['open'])
    log_lc = np.log(data['low'] / data['close'])
    
    rs_vol = (log_ho * log_hc + log_lo * log_lc).rolling(window=period).mean()
    
    # Yang-Zhang estimator
    k = 0.34 / (1.34 + (period + 1) / (period - 1))
    yz_vol = overnight_vol + k * oc_vol + (1 - k) * rs_vol
    
    vol = np.sqrt(yz_vol)
    
    if annualize:
        vol *= np.sqrt(252)
    
    return vol


def relative_volatility_index(data: Union[pd.Series, pd.DataFrame], period: int = 14,
                             column: str = 'close') -> pd.Series:
    """
    Relative Volatility Index (RVI)
    
    RSI applied to standard deviation instead of price changes.
    
    Args:
        data: Price data (Series or DataFrame)
        period: RVI period (default: 14)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with RVI values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate standard deviation of price changes
    price_changes = prices.diff()
    std_dev = price_changes.rolling(window=10).std()  # Use 10-period for std calculation
    
    # Apply RSI logic to standard deviation
    std_up = np.where(std_dev > std_dev.shift(1), std_dev, 0)
    std_down = np.where(std_dev < std_dev.shift(1), std_dev, 0)
    
    std_up_ma = pd.Series(std_up).rolling(window=period).mean()
    std_down_ma = pd.Series(std_down).rolling(window=period).mean()
    
    rvi = 100 * std_up_ma / (std_up_ma + std_down_ma)
    return rvi


def volatility_ratio(data: Union[pd.Series, pd.DataFrame], fast_period: int = 10,
                    slow_period: int = 30, column: str = 'close') -> pd.Series:
    """
    Volatility Ratio
    
    Ratio of short-term to long-term volatility.
    
    Args:
        data: Price data (Series or DataFrame)
        fast_period: Fast volatility period (default: 10)
        slow_period: Slow volatility period (default: 30)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with volatility ratio values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    returns = prices.pct_change()
    
    fast_vol = returns.rolling(window=fast_period).std()
    slow_vol = returns.rolling(window=slow_period).std()
    
    vol_ratio = fast_vol / slow_vol
    return vol_ratio


def variance(data: Union[pd.Series, pd.DataFrame], period: int = 20,
            column: str = 'close') -> pd.Series:
    """
    Rolling Variance
    
    Measures price variance over rolling window.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Rolling period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with variance values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    returns = prices.pct_change()
    return returns.rolling(window=period).var()


def vix_style_indicator(data: pd.DataFrame, period: int = 30) -> pd.Series:
    """
    VIX-Style Volatility Indicator
    
    Implied volatility-like indicator using options pricing concepts
    adapted for historical data.
    
    Args:
        data: DataFrame with OHLCV data
        period: Calculation period (default: 30)
        
    Returns:
        pandas Series with VIX-style values
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("Data must contain 'high', 'low', 'close' columns")
    
    # Calculate daily returns
    returns = data['close'].pct_change()
    
    # Calculate realized variance using Garman-Klass method
    log_hl = np.log(data['high'] / data['low'])
    log_co = np.log(data['close'] / data['open']) if 'open' in data.columns else returns
    
    # Garman-Klass estimator
    gk_var = 0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2
    
    # Rolling average of variance
    rolling_var = gk_var.rolling(window=period).mean()
    
    # Convert to VIX-like scale (annualized volatility * 100)
    vix_style = np.sqrt(rolling_var * 252) * 100
    
    return vix_style


def volatility_system(data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    """
    Comprehensive Volatility System
    
    Combines multiple volatility estimators for comprehensive analysis.
    
    Args:
        data: DataFrame with OHLCV data
        period: Rolling period (default: 20)
        
    Returns:
        DataFrame with multiple volatility measures
    """
    if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
        raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
    
    return pd.DataFrame({
        'historical_vol': historical_volatility(data, period),
        'garman_klass_vol': garman_klass_volatility(data, period),
        'parkinson_vol': parkinson_volatility(data, period),
        'rogers_satchell_vol': rogers_satchell_volatility(data, period),
        'yang_zhang_vol': yang_zhang_volatility(data, period),
        'volatility_ratio': volatility_ratio(data, period//2, period)
    }, index=data.index)


# Registry of all advanced volatility functions
ADVANCED_VOLATILITY_INDICATORS = {
    'standard_deviation': standard_deviation,
    'historical_volatility': historical_volatility,
    'garman_klass_volatility': garman_klass_volatility,
    'parkinson_volatility': parkinson_volatility,
    'rogers_satchell_volatility': rogers_satchell_volatility,
    'yang_zhang_volatility': yang_zhang_volatility,
    'relative_volatility_index': relative_volatility_index,
    'volatility_ratio': volatility_ratio,
    'variance': variance,
    'vix_style_indicator': vix_style_indicator,
    'volatility_system': volatility_system
}


def get_volatility_function_names():
    """Get list of all advanced volatility function names"""
    return list(ADVANCED_VOLATILITY_INDICATORS.keys())