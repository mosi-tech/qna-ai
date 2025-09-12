"""
Rolling metrics calculation module for time-series analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from scipy import stats


class RollingMetrics:
    """Calculate various rolling window metrics for financial time series."""
    
    @staticmethod
    def rolling_skewness(returns: List[float], window: int = 30) -> Dict[str, Any]:
        """
        Calculate rolling skewness of return distributions.
        
        Args:
            returns: List of returns (as percentages)
            window: Rolling window size
            
        Returns:
            Dictionary with rolling skewness metrics
        """
        if len(returns) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        returns_series = pd.Series(returns)
        rolling_skew = returns_series.rolling(window=window).skew()
        rolling_skew_clean = rolling_skew.dropna()
        
        if rolling_skew_clean.empty:
            return {"error": "No valid skewness calculations"}
        
        return {
            "rolling_skewness": rolling_skew_clean.tolist(),
            "current_skewness": rolling_skew_clean.iloc[-1],
            "avg_skewness": rolling_skew_clean.mean(),
            "max_skewness": rolling_skew_clean.max(),
            "min_skewness": rolling_skew_clean.min(),
            "skewness_volatility": rolling_skew_clean.std(),
            "positive_skew_periods": sum(1 for s in rolling_skew_clean if s > 0),
            "negative_skew_periods": sum(1 for s in rolling_skew_clean if s < 0),
            "window_size": window,
            "interpretation": RollingMetrics._interpret_skewness(rolling_skew_clean.iloc[-1]),
            "observations": len(rolling_skew_clean)
        }
    
    @staticmethod
    def rolling_kurtosis(returns: List[float], window: int = 30) -> Dict[str, Any]:
        """
        Calculate rolling kurtosis of return distributions.
        
        Args:
            returns: List of returns (as percentages)
            window: Rolling window size
            
        Returns:
            Dictionary with rolling kurtosis metrics
        """
        if len(returns) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        returns_series = pd.Series(returns)
        rolling_kurt = returns_series.rolling(window=window).kurt()
        rolling_kurt_clean = rolling_kurt.dropna()
        
        if rolling_kurt_clean.empty:
            return {"error": "No valid kurtosis calculations"}
        
        return {
            "rolling_kurtosis": rolling_kurt_clean.tolist(),
            "current_kurtosis": rolling_kurt_clean.iloc[-1],
            "avg_kurtosis": rolling_kurt_clean.mean(),
            "max_kurtosis": rolling_kurt_clean.max(),
            "min_kurtosis": rolling_kurt_clean.min(),
            "kurtosis_volatility": rolling_kurt_clean.std(),
            "excess_kurtosis_periods": sum(1 for k in rolling_kurt_clean if k > 0),  # >0 means leptokurtic
            "window_size": window,
            "interpretation": RollingMetrics._interpret_kurtosis(rolling_kurt_clean.iloc[-1]),
            "observations": len(rolling_kurt_clean)
        }
    
    @staticmethod
    def rolling_sharpe_ratio(returns: List[float], window: int = 30, risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """
        Calculate rolling Sharpe ratio.
        
        Args:
            returns: List of returns (as percentages)
            window: Rolling window size
            risk_free_rate: Annual risk-free rate (as decimal)
            
        Returns:
            Dictionary with rolling Sharpe ratio metrics
        """
        if len(returns) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        returns_series = pd.Series(returns)
        
        # Convert daily risk-free rate
        daily_rf_rate = (risk_free_rate / 252) * 100  # Convert to percentage
        
        # Calculate rolling mean and std
        rolling_mean = returns_series.rolling(window=window).mean()
        rolling_std = returns_series.rolling(window=window).std()
        
        # Calculate Sharpe ratio (annualized)
        rolling_sharpe = ((rolling_mean - daily_rf_rate) * np.sqrt(252)) / (rolling_std * np.sqrt(252))
        rolling_sharpe_clean = rolling_sharpe.dropna()
        
        if rolling_sharpe_clean.empty:
            return {"error": "No valid Sharpe ratio calculations"}
        
        return {
            "rolling_sharpe_ratio": rolling_sharpe_clean.tolist(),
            "current_sharpe_ratio": rolling_sharpe_clean.iloc[-1],
            "avg_sharpe_ratio": rolling_sharpe_clean.mean(),
            "max_sharpe_ratio": rolling_sharpe_clean.max(),
            "min_sharpe_ratio": rolling_sharpe_clean.min(),
            "sharpe_volatility": rolling_sharpe_clean.std(),
            "positive_sharpe_periods": sum(1 for s in rolling_sharpe_clean if s > 0),
            "excellent_sharpe_periods": sum(1 for s in rolling_sharpe_clean if s > 1.0),
            "window_size": window,
            "risk_free_rate_used": risk_free_rate,
            "interpretation": RollingMetrics._interpret_sharpe_ratio(rolling_sharpe_clean.iloc[-1]),
            "observations": len(rolling_sharpe_clean)
        }
    
    @staticmethod
    def rolling_beta(returns: List[float], market_returns: List[float], window: int = 30) -> Dict[str, Any]:
        """
        Calculate rolling beta relative to market.
        
        Args:
            returns: Security returns
            market_returns: Market benchmark returns
            window: Rolling window size
            
        Returns:
            Dictionary with rolling beta metrics
        """
        if len(returns) != len(market_returns):
            return {"error": "Security and market return series must have same length"}
        
        if len(returns) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        returns_series = pd.Series(returns)
        market_series = pd.Series(market_returns)
        
        # Calculate rolling covariance and market variance
        rolling_cov = returns_series.rolling(window=window).cov(market_series)
        rolling_market_var = market_series.rolling(window=window).var()
        
        # Calculate rolling beta
        rolling_beta = rolling_cov / rolling_market_var
        rolling_beta_clean = rolling_beta.dropna()
        
        if rolling_beta_clean.empty:
            return {"error": "No valid beta calculations"}
        
        return {
            "rolling_beta": rolling_beta_clean.tolist(),
            "current_beta": rolling_beta_clean.iloc[-1],
            "avg_beta": rolling_beta_clean.mean(),
            "max_beta": rolling_beta_clean.max(),
            "min_beta": rolling_beta_clean.min(),
            "beta_volatility": rolling_beta_clean.std(),
            "high_beta_periods": sum(1 for b in rolling_beta_clean if b > 1.2),
            "low_beta_periods": sum(1 for b in rolling_beta_clean if b < 0.8),
            "window_size": window,
            "interpretation": RollingMetrics._interpret_beta(rolling_beta_clean.iloc[-1]),
            "observations": len(rolling_beta_clean)
        }
    
    @staticmethod
    def rolling_information_ratio(returns: List[float], benchmark_returns: List[float], window: int = 30) -> Dict[str, Any]:
        """
        Calculate rolling information ratio.
        
        Args:
            returns: Portfolio/security returns
            benchmark_returns: Benchmark returns
            window: Rolling window size
            
        Returns:
            Dictionary with rolling information ratio metrics
        """
        if len(returns) != len(benchmark_returns):
            return {"error": "Return series must have same length"}
        
        if len(returns) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        returns_series = pd.Series(returns)
        benchmark_series = pd.Series(benchmark_returns)
        
        # Calculate excess returns
        excess_returns = returns_series - benchmark_series
        
        # Calculate rolling mean and std of excess returns
        rolling_excess_mean = excess_returns.rolling(window=window).mean()
        rolling_excess_std = excess_returns.rolling(window=window).std()
        
        # Calculate information ratio (annualized)
        rolling_ir = (rolling_excess_mean * np.sqrt(252)) / (rolling_excess_std * np.sqrt(252))
        rolling_ir_clean = rolling_ir.dropna()
        
        if rolling_ir_clean.empty:
            return {"error": "No valid information ratio calculations"}
        
        return {
            "rolling_information_ratio": rolling_ir_clean.tolist(),
            "current_information_ratio": rolling_ir_clean.iloc[-1],
            "avg_information_ratio": rolling_ir_clean.mean(),
            "max_information_ratio": rolling_ir_clean.max(),
            "min_information_ratio": rolling_ir_clean.min(),
            "ir_volatility": rolling_ir_clean.std(),
            "positive_ir_periods": sum(1 for ir in rolling_ir_clean if ir > 0),
            "strong_ir_periods": sum(1 for ir in rolling_ir_clean if ir > 0.5),
            "window_size": window,
            "interpretation": RollingMetrics._interpret_information_ratio(rolling_ir_clean.iloc[-1]),
            "observations": len(rolling_ir_clean)
        }
    
    @staticmethod
    def rolling_max_drawdown(returns: List[float], window: int = 30) -> Dict[str, Any]:
        """
        Calculate rolling maximum drawdown.
        
        Args:
            returns: List of returns (as percentages)
            window: Rolling window size
            
        Returns:
            Dictionary with rolling max drawdown metrics
        """
        if len(returns) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        # Convert returns to price series (cumulative)
        returns_decimal = [r / 100 for r in returns]
        cumulative_returns = [1.0]  # Start at 1
        
        for r in returns_decimal:
            cumulative_returns.append(cumulative_returns[-1] * (1 + r))
        
        cumulative_returns = cumulative_returns[1:]  # Remove initial 1
        price_series = pd.Series(cumulative_returns)
        
        # Calculate rolling max drawdown
        rolling_max_dd = []
        
        for i in range(window - 1, len(price_series)):
            window_prices = price_series.iloc[i-window+1:i+1]
            running_max = window_prices.expanding().max()
            drawdowns = (window_prices - running_max) / running_max
            max_dd = drawdowns.min()
            rolling_max_dd.append(max_dd * 100)  # Convert to percentage
        
        if not rolling_max_dd:
            return {"error": "No valid max drawdown calculations"}
        
        return {
            "rolling_max_drawdown": rolling_max_dd,
            "current_max_drawdown": rolling_max_dd[-1],
            "avg_max_drawdown": np.mean(rolling_max_dd),
            "worst_max_drawdown": min(rolling_max_dd),
            "best_max_drawdown": max(rolling_max_dd),
            "max_drawdown_volatility": np.std(rolling_max_dd),
            "severe_drawdown_periods": sum(1 for dd in rolling_max_dd if dd < -10),
            "window_size": window,
            "observations": len(rolling_max_dd)
        }
    
    @staticmethod
    def _interpret_skewness(skewness: float) -> str:
        """Interpret skewness value."""
        if skewness > 1:
            return "Highly positive skewed (momentum-like, occasional large gains)"
        elif skewness > 0.5:
            return "Moderately positive skewed (some momentum characteristics)"
        elif skewness > -0.5:
            return "Approximately symmetric distribution"
        elif skewness > -1:
            return "Moderately negative skewed (some mean-reversion characteristics)"
        else:
            return "Highly negative skewed (mean-reversion, occasional large losses)"
    
    @staticmethod
    def _interpret_kurtosis(kurtosis: float) -> str:
        """Interpret kurtosis value."""
        if kurtosis > 3:
            return "Leptokurtic (fat tails, higher probability of extreme events)"
        elif kurtosis < -0.5:
            return "Platykurtic (thin tails, lower probability of extreme events)"
        else:
            return "Approximately normal distribution (mesokurtic)"
    
    @staticmethod
    def _interpret_sharpe_ratio(sharpe: float) -> str:
        """Interpret Sharpe ratio value."""
        if sharpe > 2:
            return "Excellent risk-adjusted performance"
        elif sharpe > 1:
            return "Good risk-adjusted performance"
        elif sharpe > 0:
            return "Positive risk-adjusted performance"
        else:
            return "Poor risk-adjusted performance"
    
    @staticmethod
    def _interpret_beta(beta: float) -> str:
        """Interpret beta value."""
        if beta > 1.3:
            return "High beta (very sensitive to market movements)"
        elif beta > 1.1:
            return "Above-market beta (more sensitive to market)"
        elif beta > 0.9:
            return "Market-like beta (similar sensitivity to market)"
        elif beta > 0.7:
            return "Below-market beta (less sensitive to market)"
        else:
            return "Low beta (low sensitivity to market movements)"
    
    @staticmethod
    def _interpret_information_ratio(ir: float) -> str:
        """Interpret information ratio value."""
        if ir > 0.75:
            return "Excellent active management (strong excess returns)"
        elif ir > 0.5:
            return "Good active management"
        elif ir > 0:
            return "Positive active management"
        else:
            return "Poor active management (underperforming benchmark)"