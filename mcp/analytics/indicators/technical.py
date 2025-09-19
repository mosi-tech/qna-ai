"""
Technical Indicators using talib-binary

All technical analysis calculations using talib-binary from requirements.txt
From financial-analysis-function-library.json
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use talib-binary from requirements.txt - industry standard, 2-4x faster
import talib

from ..utils.data_utils import validate_price_data, standardize_output


def calculate_sma(data: Union[pd.Series, Dict[str, Any]], period: int = 20) -> Dict[str, Any]:
    """
    Simple Moving Average using talib-binary.
    
    From financial-analysis-function-library.json
    Uses talib-binary library instead of manual calculations - no code duplication
    
    Args:
        data: Price data
        period: Period for SMA
        
    Returns:
        Dict: SMA values
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary - leveraging requirements.txt
        sma_values = talib.SMA(prices.values.astype(np.float64), timeperiod=period)
        sma_series = pd.Series(sma_values, index=prices.index).dropna()
        
        result = {
            "data": sma_series.tolist(),
            "sma": sma_series,
            "period": period,
            "latest_value": float(sma_series.iloc[-1]) if len(sma_series) > 0 else None,
            "trend": "bullish" if len(sma_series) >= 2 and sma_series.iloc[-1] > sma_series.iloc[-2] else "bearish"
        }
        
        return standardize_output(result, "calculate_sma")
        
    except Exception as e:
        return {"success": False, "error": f"SMA calculation failed: {str(e)}"}


def calculate_ema(data: Union[pd.Series, Dict[str, Any]], period: int = 20) -> Dict[str, Any]:
    """
    Exponential Moving Average using talib-binary.
    
    From financial-analysis-function-library.json
    Uses talib-binary library instead of manual calculations - no code duplication
    
    Args:
        data: Price data
        period: Period for EMA
        
    Returns:
        Dict: EMA values
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary - leveraging requirements.txt
        ema_values = talib.EMA(prices.values.astype(np.float64), timeperiod=period)
        ema_series = pd.Series(ema_values, index=prices.index).dropna()
        
        result = {
            "ema": ema_series,
            "period": period,
            "latest_value": float(ema_series.iloc[-1]) if len(ema_series) > 0 else None,
            "trend": "bullish" if len(ema_series) >= 2 and ema_series.iloc[-1] > ema_series.iloc[-2] else "bearish"
        }
        
        return standardize_output(result, "calculate_ema")
        
    except Exception as e:
        return {"success": False, "error": f"EMA calculation failed: {str(e)}"}


def calculate_rsi(data: Union[pd.Series, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """
    Relative Strength Index using talib-binary.
    
    From financial-analysis-function-library.json
    Uses talib-binary library instead of manual calculations - no code duplication
    
    Args:
        data: Price data
        period: Period for RSI
        
    Returns:
        Dict: RSI values and signals
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary - leveraging requirements.txt
        rsi_values = talib.RSI(prices.values.astype(np.float64), timeperiod=period)
        rsi_series = pd.Series(rsi_values, index=prices.index).dropna()
        
        latest_rsi = float(rsi_series.iloc[-1]) if len(rsi_series) > 0 else None
        
        # Generate signals
        signal = "neutral"
        if latest_rsi is not None:
            if latest_rsi > 70:
                signal = "overbought"
            elif latest_rsi < 30:
                signal = "oversold"
        
        result = {
            "data": rsi_series.tolist(),
            "rsi": rsi_series,
            "period": period,
            "latest_value": latest_rsi,
            "signal": signal,
            "overbought_level": 70,
            "oversold_level": 30
        }
        
        return standardize_output(result, "calculate_rsi")
        
    except Exception as e:
        return {"success": False, "error": f"RSI calculation failed: {str(e)}"}


def calculate_macd(data: Union[pd.Series, Dict[str, Any]], 
                   fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, Any]:
    """
    MACD using TA-Lib.
    
    From financial-analysis-function-library.json
    Uses TA-Lib library instead of manual calculations - no code duplication
    
    Args:
        data: Price data
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period
        
    Returns:
        Dict: MACD line, signal line, histogram
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary - leveraging requirements.txt
        macd_line, macd_signal, macd_hist = talib.MACD(
            prices.values.astype(np.float64), 
            fastperiod=fast_period, 
            slowperiod=slow_period, 
            signalperiod=signal_period
        )
        
        macd_df = pd.DataFrame({
            'macd': macd_line,
            'signal': macd_signal,
            'histogram': macd_hist
        }, index=prices.index).dropna()
        
        # Determine column names (different libraries use different naming)
        macd_col = next((col for col in macd_df.columns if 'macd' in col.lower() and 'signal' not in col.lower() and 'hist' not in col.lower()), macd_df.columns[0])
        signal_col = next((col for col in macd_df.columns if 'signal' in col.lower() or 'macd' in col.lower() and 's' in col.lower()), macd_df.columns[1])
        hist_col = next((col for col in macd_df.columns if 'hist' in col.lower() or 'h' in col.lower()), macd_df.columns[2])
        
        # Generate signals
        signal = "neutral"
        if len(macd_df) >= 2:
            current_macd = macd_df[macd_col].iloc[-1]
            current_signal = macd_df[signal_col].iloc[-1]
            prev_macd = macd_df[macd_col].iloc[-2]
            prev_signal = macd_df[signal_col].iloc[-2]
            
            if current_macd > current_signal and prev_macd <= prev_signal:
                signal = "bullish_crossover"
            elif current_macd < current_signal and prev_macd >= prev_signal:
                signal = "bearish_crossover"
        
        result = {
            "macd_line": macd_df[macd_col],
            "signal_line": macd_df[signal_col],
            "histogram": macd_df[hist_col],
            "latest_macd": float(macd_df[macd_col].iloc[-1]) if len(macd_df) > 0 else None,
            "latest_signal": float(macd_df[signal_col].iloc[-1]) if len(macd_df) > 0 else None,
            "signal": signal,
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period
        }
        
        return standardize_output(result, "calculate_macd")
        
    except Exception as e:
        return {"success": False, "error": f"MACD calculation failed: {str(e)}"}


def calculate_bollinger_bands(data: Union[pd.Series, Dict[str, Any]], 
                             period: int = 20, std_dev: float = 2.0) -> Dict[str, Any]:
    """
    Bollinger Bands using TA-Lib.
    
    From financial-analysis-function-library.json
    Uses TA-Lib library instead of manual calculations - no code duplication
    
    Args:
        data: Price data
        period: Period for moving average
        std_dev: Standard deviation multiplier
        
    Returns:
        Dict: Upper band, middle band, lower band
    """
    try:
        prices = validate_price_data(data)
        
        # Use talib-binary - leveraging requirements.txt
        upper, middle, lower = talib.BBANDS(
            prices.values.astype(np.float64), 
            timeperiod=period, 
            nbdevup=std_dev, 
            nbdevdn=std_dev
        )
        
        bb_df = pd.DataFrame({
            'upper': upper,
            'middle': middle,
            'lower': lower
        }, index=prices.index).dropna()
        
        # Determine column names
        upper_col = next((col for col in bb_df.columns if 'upper' in col.lower() or 'u' in col), bb_df.columns[0])
        middle_col = next((col for col in bb_df.columns if 'middle' in col.lower() or 'm' in col), bb_df.columns[1])
        lower_col = next((col for col in bb_df.columns if 'lower' in col.lower() or 'l' in col), bb_df.columns[2])
        
        # Calculate %B and bandwidth
        current_price = prices.iloc[-1] if len(prices) > 0 else None
        if current_price is not None and len(bb_df) > 0:
            current_upper = bb_df[upper_col].iloc[-1]
            current_lower = bb_df[lower_col].iloc[-1]
            percent_b = (current_price - current_lower) / (current_upper - current_lower) if current_upper != current_lower else 0.5
            bandwidth = (current_upper - current_lower) / bb_df[middle_col].iloc[-1] if bb_df[middle_col].iloc[-1] != 0 else 0
        else:
            percent_b = None
            bandwidth = None
        
        # Generate signals
        signal = "neutral"
        if percent_b is not None:
            if percent_b > 1:
                signal = "overbought"
            elif percent_b < 0:
                signal = "oversold"
        
        result = {
            "upper_band": bb_df[upper_col],
            "middle_band": bb_df[middle_col],
            "lower_band": bb_df[lower_col],
            "percent_b": percent_b,
            "bandwidth": bandwidth,
            "signal": signal,
            "period": period,
            "std_dev": std_dev
        }
        
        return standardize_output(result, "calculate_bollinger_bands")
        
    except Exception as e:
        return {"success": False, "error": f"Bollinger Bands calculation failed: {str(e)}"}


def calculate_stochastic(data: Union[pd.DataFrame, Dict[str, Any]], 
                        k_period: int = 14, d_period: int = 3) -> Dict[str, Any]:
    """
    Stochastic Oscillator using TA-Lib.
    
    From financial-analysis-function-library.json
    Uses TA-Lib library instead of manual calculations - no code duplication
    
    Args:
        data: OHLC data
        k_period: %K period
        d_period: %D period
        
    Returns:
        Dict: %K and %D values
    """
    try:
        if isinstance(data, dict):
            # Convert dict to DataFrame
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for Stochastic calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low' 
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary - leveraging requirements.txt
        slowk, slowd = talib.STOCH(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64), 
            df[close_col].values.astype(np.float64),
            fastk_period=k_period,
            slowk_period=3,
            slowd_period=d_period
        )
        
        stoch_df = pd.DataFrame({
            'k_percent': slowk,
            'd_percent': slowd
        }, index=df.index).dropna()
        
        # Determine column names
        k_col = next((col for col in stoch_df.columns if 'k' in col.lower()), stoch_df.columns[0])
        d_col = next((col for col in stoch_df.columns if 'd' in col.lower()), stoch_df.columns[1])
        
        # Generate signals
        signal = "neutral"
        if len(stoch_df) >= 2:
            current_k = stoch_df[k_col].iloc[-1]
            current_d = stoch_df[d_col].iloc[-1]
            prev_k = stoch_df[k_col].iloc[-2]
            prev_d = stoch_df[d_col].iloc[-2]
            
            if current_k > current_d and prev_k <= prev_d and current_k < 80:
                signal = "bullish_crossover"
            elif current_k < current_d and prev_k >= prev_d and current_k > 20:
                signal = "bearish_crossover"
            elif current_k > 80 and current_d > 80:
                signal = "overbought"
            elif current_k < 20 and current_d < 20:
                signal = "oversold"
        
        result = {
            "k_percent": stoch_df[k_col],
            "d_percent": stoch_df[d_col],
            "latest_k": float(stoch_df[k_col].iloc[-1]) if len(stoch_df) > 0 else None,
            "latest_d": float(stoch_df[d_col].iloc[-1]) if len(stoch_df) > 0 else None,
            "signal": signal,
            "k_period": k_period,
            "d_period": d_period
        }
        
        return standardize_output(result, "calculate_stochastic")
        
    except Exception as e:
        return {"success": False, "error": f"Stochastic calculation failed: {str(e)}"}


def calculate_atr(data: Union[pd.DataFrame, Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
    """
    Average True Range using TA-Lib.
    
    From financial-analysis-function-library.json
    Uses TA-Lib library instead of manual calculations - no code duplication
    
    Args:
        data: OHLC data
        period: Period for ATR
        
    Returns:
        Dict: ATR values
    """
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure we have required columns
        required_cols = ['high', 'low', 'close']
        if not all(col in df.columns or col.title() in df.columns for col in required_cols):
            raise ValueError("OHLC data required for ATR calculation")
        
        # Standardize column names
        high_col = 'high' if 'high' in df.columns else 'High'
        low_col = 'low' if 'low' in df.columns else 'Low'
        close_col = 'close' if 'close' in df.columns else 'Close'
        
        # Use talib-binary - leveraging requirements.txt
        atr_values = talib.ATR(
            df[high_col].values.astype(np.float64),
            df[low_col].values.astype(np.float64),
            df[close_col].values.astype(np.float64),
            timeperiod=period
        )
        atr_series = pd.Series(atr_values, index=df.index).dropna()
        
        latest_atr = float(atr_series.iloc[-1]) if len(atr_series) > 0 else None
        latest_price = float(df[close_col].iloc[-1]) if len(df) > 0 else None
        
        # Calculate ATR as percentage of price
        atr_percent = (latest_atr / latest_price * 100) if latest_atr and latest_price else None
        
        result = {
            "atr": atr_series,
            "latest_value": latest_atr,
            "atr_percent": atr_percent,
            "period": period,
            "volatility_level": "high" if atr_percent and atr_percent > 3 else "normal" if atr_percent and atr_percent > 1 else "low"
        }
        
        return standardize_output(result, "calculate_atr")
        
    except Exception as e:
        return {"success": False, "error": f"ATR calculation failed: {str(e)}"}


# Registry of technical indicator functions - all using libraries
TECHNICAL_INDICATORS_FUNCTIONS = {
    'calculate_sma': calculate_sma,
    'calculate_ema': calculate_ema,
    'calculate_rsi': calculate_rsi,
    'calculate_macd': calculate_macd,
    'calculate_bollinger_bands': calculate_bollinger_bands,
    'calculate_stochastic': calculate_stochastic,
    'calculate_atr': calculate_atr
}