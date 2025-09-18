"""
Time Series Processing Functions

Functions to process and transform time series data, matching the categorical 
structure from financial-analysis-function-library.json

From financial-analysis-function-library.json category: time_series_processing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def calculateReturns(
    prices: Union[pd.Series, List[float], Dict[str, Any]], 
    period: str = "daily"
) -> Dict[str, Any]:
    """
    Calculate price returns for given period.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price data as pd.Series, list, or result from other functions
        period: "daily", "weekly", "monthly"
        
    Returns:
        {
            "returns": pd.Series,  # Return values
            "period": str,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "filtered_data" in prices:
            series = prices["filtered_data"]
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 price observations"}
        
        # Calculate returns
        returns = series.pct_change().dropna()
        
        # Convert to different periods if needed
        if period == "weekly":
            returns = (1 + returns).resample('W').prod() - 1
        elif period == "monthly":
            returns = (1 + returns).resample('M').prod() - 1
        elif period != "daily":
            return {"success": False, "error": f"Unsupported period: {period}"}
        
        return {
            "success": True,
            "returns": returns,
            "period": period,
            "num_observations": len(returns),
            "mean_return": float(returns.mean()),
            "std_return": float(returns.std())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Returns calculation failed: {str(e)}"}


def calculateLogReturns(
    prices: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate logarithmic returns.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price data as pd.Series, list, or result from other functions
        
    Returns:
        {
            "log_returns": pd.Series,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "filtered_data" in prices:
            series = prices["filtered_data"]
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 price observations"}
        
        # Calculate log returns
        log_returns = np.log(series / series.shift(1)).dropna()
        
        return {
            "success": True,
            "log_returns": log_returns,
            "num_observations": len(log_returns),
            "mean_log_return": float(log_returns.mean()),
            "std_log_return": float(log_returns.std())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Log returns calculation failed: {str(e)}"}


def calculateCumulativeReturns(
    returns: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate cumulative returns from return series.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return data as pd.Series, list, or result from other functions
        
    Returns:
        {
            "cumulative_returns": pd.Series,
            "total_return": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "log_returns" in returns:
            series = returns["log_returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, (list, np.ndarray)):
            series = pd.Series(returns)
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) == 0:
            return {"success": False, "error": "No return data"}
        
        # Calculate cumulative returns
        cumulative_returns = (1 + series).cumprod() - 1
        total_return = cumulative_returns.iloc[-1]
        
        return {
            "success": True,
            "cumulative_returns": cumulative_returns,
            "total_return": float(total_return),
            "num_observations": len(cumulative_returns),
            "start_date": series.index[0].strftime("%Y-%m-%d") if hasattr(series.index[0], 'strftime') else "N/A",
            "end_date": series.index[-1].strftime("%Y-%m-%d") if hasattr(series.index[-1], 'strftime') else "N/A"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Cumulative returns calculation failed: {str(e)}"}


def calculateRollingVolatility(
    returns: Union[pd.Series, List[float], Dict[str, Any]], 
    window: int = 30
) -> Dict[str, Any]:
    """
    Calculate rolling volatility over specified window.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return data as pd.Series, list, or result from other functions
        window: Rolling window size
        
    Returns:
        {
            "rolling_volatility": pd.Series,
            "annualized_volatility": pd.Series,
            "window": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "log_returns" in returns:
            series = returns["log_returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, (list, np.ndarray)):
            series = pd.Series(returns)
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < window:
            return {"success": False, "error": f"Need at least {window} observations"}
        
        # Calculate rolling volatility
        rolling_vol = series.rolling(window=window).std()
        annualized_vol = rolling_vol * np.sqrt(252)  # Annualize assuming 252 trading days
        
        return {
            "success": True,
            "rolling_volatility": rolling_vol,
            "annualized_volatility": annualized_vol,
            "window": window,
            "num_observations": len(rolling_vol.dropna()),
            "mean_volatility": float(annualized_vol.mean())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Rolling volatility calculation failed: {str(e)}"}


def calculateBeta(
    stock_returns: Union[pd.Series, List[float], Dict[str, Any]],
    market_returns: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate beta coefficient vs market.
    
    From financial-analysis-function-library.json
    
    Args:
        stock_returns: Stock return data
        market_returns: Market return data
        
    Returns:
        {
            "beta": float,
            "correlation": float,
            "r_squared": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, (list, np.ndarray)):
                return pd.Series(data)
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        stock_series = extract_series(stock_returns)
        market_series = extract_series(market_returns)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'stock': stock_series,
            'market': market_series
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        stock_aligned = aligned_data['stock']
        market_aligned = aligned_data['market']
        
        # Calculate beta using covariance and variance
        covariance = np.cov(stock_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        if market_variance == 0:
            return {"success": False, "error": "Market variance is zero"}
        
        beta = covariance / market_variance
        correlation = np.corrcoef(stock_aligned, market_aligned)[0, 1]
        r_squared = correlation ** 2
        
        return {
            "success": True,
            "beta": float(beta),
            "correlation": float(correlation),
            "r_squared": float(r_squared),
            "num_observations": len(aligned_data),
            "covariance": float(covariance),
            "market_variance": float(market_variance)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Beta calculation failed: {str(e)}"}


def calculateCorrelation(
    series1: Union[pd.Series, List[float], Dict[str, Any]],
    series2: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate correlation between two series.
    
    From financial-analysis-function-library.json
    
    Args:
        series1: First data series
        series2: Second data series
        
    Returns:
        {
            "correlation": float,
            "p_value": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, (list, np.ndarray)):
                return pd.Series(data)
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        s1 = extract_series(series1)
        s2 = extract_series(series2)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'series1': s1,
            'series2': s2
        }).dropna()
        
        if len(aligned_data) < 3:
            return {"success": False, "error": "Need at least 3 aligned observations"}
        
        # Calculate correlation
        from scipy.stats import pearsonr
        correlation, p_value = pearsonr(aligned_data['series1'], aligned_data['series2'])
        
        return {
            "success": True,
            "correlation": float(correlation),
            "p_value": float(p_value),
            "num_observations": len(aligned_data),
            "significance": "significant" if p_value < 0.05 else "not significant"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Correlation calculation failed: {str(e)}"}


def calculateCorrelationMatrix(
    series_dict: Dict[str, Union[pd.Series, List[float]]]
) -> Dict[str, Any]:
    """
    Calculate correlation matrix for multiple series.
    
    From financial-analysis-function-library.json
    
    Args:
        series_dict: Dictionary of {name: series} data
        
    Returns:
        {
            "correlation_matrix": pd.DataFrame,
            "num_observations": int,
            "series_names": List[str],
            "success": bool
        }
    """
    try:
        if not isinstance(series_dict, dict) or len(series_dict) < 2:
            return {"success": False, "error": "Need at least 2 series in dictionary format"}
        
        # Convert all series to pandas Series and align
        data_df = pd.DataFrame()
        
        for name, series in series_dict.items():
            if isinstance(series, (list, np.ndarray)):
                data_df[name] = pd.Series(series)
            elif isinstance(series, pd.Series):
                data_df[name] = series
            else:
                return {"success": False, "error": f"Invalid format for series '{name}'"}
        
        # Drop rows with any NaN values
        data_df = data_df.dropna()
        
        if len(data_df) < 3:
            return {"success": False, "error": "Need at least 3 aligned observations"}
        
        # Calculate correlation matrix
        correlation_matrix = data_df.corr()
        
        return {
            "success": True,
            "correlation_matrix": correlation_matrix,
            "num_observations": len(data_df),
            "series_names": list(series_dict.keys()),
            "matrix_size": f"{len(series_dict)}x{len(series_dict)}"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Correlation matrix calculation failed: {str(e)}"}


def calculateSMA(
    prices: Union[pd.Series, List[float], Dict[str, Any]], 
    period: int = 20
) -> Dict[str, Any]:
    """
    Calculate Simple Moving Average.
    
    From financial-analysis-function-library.json
    Possible duplicate implementation - this functionality exists in technical indicators
    
    Args:
        prices: Price data as pd.Series, list, or result from other functions
        period: SMA period
        
    Returns:
        {
            "sma": pd.Series,
            "period": int,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "close" in prices:
            series = prices["close"]
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < period:
            return {"success": False, "error": f"Need at least {period} observations"}
        
        # Calculate SMA
        sma = series.rolling(window=period).mean()
        
        return {
            "success": True,
            "sma": sma,
            "period": period,
            "num_observations": len(sma.dropna()),
            "last_value": float(sma.iloc[-1]) if not sma.isna().iloc[-1] else None
        }
        
    except Exception as e:
        return {"success": False, "error": f"SMA calculation failed: {str(e)}"}


def calculateEMA(
    prices: Union[pd.Series, List[float], Dict[str, Any]], 
    period: int = 20
) -> Dict[str, Any]:
    """
    Calculate Exponential Moving Average.
    
    From financial-analysis-function-library.json
    Possible duplicate implementation - this functionality exists in technical indicators
    
    Args:
        prices: Price data as pd.Series, list, or result from other functions
        period: EMA period
        
    Returns:
        {
            "ema": pd.Series,
            "period": int,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "close" in prices:
            series = prices["close"]
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < period:
            return {"success": False, "error": f"Need at least {period} observations"}
        
        # Calculate EMA
        ema = series.ewm(span=period).mean()
        
        return {
            "success": True,
            "ema": ema,
            "period": period,
            "num_observations": len(ema),
            "last_value": float(ema.iloc[-1])
        }
        
    except Exception as e:
        return {"success": False, "error": f"EMA calculation failed: {str(e)}"}


def detectSMACrossover(
    prices: Union[pd.Series, List[float], Dict[str, Any]], 
    fast_period: int = 20, 
    slow_period: int = 50
) -> Dict[str, Any]:
    """
    Detect SMA crossover signals.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price data
        fast_period: Fast SMA period
        slow_period: Slow SMA period
        
    Returns:
        {
            "crossover_signals": pd.Series,
            "fast_sma": pd.Series,
            "slow_sma": pd.Series,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "close" in prices:
            series = prices["close"]
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < slow_period:
            return {"success": False, "error": f"Need at least {slow_period} observations"}
        
        # Calculate SMAs
        fast_sma = series.rolling(window=fast_period).mean()
        slow_sma = series.rolling(window=slow_period).mean()
        
        # Detect crossovers
        # 1 = bullish crossover (fast above slow), -1 = bearish crossover (fast below slow), 0 = no signal
        prev_position = (fast_sma.shift(1) > slow_sma.shift(1)).astype(int)
        curr_position = (fast_sma > slow_sma).astype(int)
        
        crossover_signals = curr_position - prev_position
        
        return {
            "success": True,
            "crossover_signals": crossover_signals,
            "fast_sma": fast_sma,
            "slow_sma": slow_sma,
            "fast_period": fast_period,
            "slow_period": slow_period,
            "num_signals": len(crossover_signals[crossover_signals != 0])
        }
        
    except Exception as e:
        return {"success": False, "error": f"SMA crossover detection failed: {str(e)}"}


def detectEMACrossover(
    prices: Union[pd.Series, List[float], Dict[str, Any]], 
    fast_period: int = 12, 
    slow_period: int = 26
) -> Dict[str, Any]:
    """
    Detect EMA crossover signals.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price data
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        
    Returns:
        {
            "crossover_signals": pd.Series,
            "fast_ema": pd.Series,
            "slow_ema": pd.Series,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "close" in prices:
            series = prices["close"]
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < slow_period:
            return {"success": False, "error": f"Need at least {slow_period} observations"}
        
        # Calculate EMAs
        fast_ema = series.ewm(span=fast_period).mean()
        slow_ema = series.ewm(span=slow_period).mean()
        
        # Detect crossovers
        # 1 = bullish crossover (fast above slow), -1 = bearish crossover (fast below slow), 0 = no signal
        prev_position = (fast_ema.shift(1) > slow_ema.shift(1)).astype(int)
        curr_position = (fast_ema > slow_ema).astype(int)
        
        crossover_signals = curr_position - prev_position
        
        return {
            "success": True,
            "crossover_signals": crossover_signals,
            "fast_ema": fast_ema,
            "slow_ema": slow_ema,
            "fast_period": fast_period,
            "slow_period": slow_period,
            "num_signals": len(crossover_signals[crossover_signals != 0])
        }
        
    except Exception as e:
        return {"success": False, "error": f"EMA crossover detection failed: {str(e)}"}


# Registry for MCP server
TIME_SERIES_PROCESSING_FUNCTIONS = {
    'calculateReturns': calculateReturns,
    'calculateLogReturns': calculateLogReturns,
    'calculateCumulativeReturns': calculateCumulativeReturns,
    'calculateRollingVolatility': calculateRollingVolatility,
    'calculateBeta': calculateBeta,
    'calculateCorrelation': calculateCorrelation,
    'calculateCorrelationMatrix': calculateCorrelationMatrix,
    'calculateSMA': calculateSMA,
    'calculateEMA': calculateEMA,
    'detectSMACrossover': detectSMACrossover,
    'detectEMACrossover': detectEMACrossover
}