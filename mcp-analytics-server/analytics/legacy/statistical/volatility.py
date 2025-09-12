"""
Volatility calculation module for various volatility metrics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from scipy import stats


class VolatilityCalculator:
    """Calculate various volatility metrics from returns data."""
    
    @staticmethod
    def rolling_volatility(returns: List[float], window: int = 30, annualize: bool = True) -> Dict[str, Any]:
        """
        Calculate rolling volatility (standard deviation) of returns.
        
        Args:
            returns: List of daily returns (as percentages)
            window: Rolling window size in periods
            annualize: Whether to annualize volatility (multiply by sqrt(252))
            
        Returns:
            Dictionary with rolling volatility metrics
        """
        if len(returns) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        returns_series = pd.Series(returns)
        rolling_vol = returns_series.rolling(window=window).std()
        
        if annualize:
            rolling_vol = rolling_vol * np.sqrt(252)
        
        rolling_vol_clean = rolling_vol.dropna()
        
        if rolling_vol_clean.empty:
            return {"error": "No valid volatility calculations"}
        
        return {
            "rolling_volatility": rolling_vol_clean.tolist(),
            "current_volatility": rolling_vol_clean.iloc[-1],
            "avg_volatility": rolling_vol_clean.mean(),
            "max_volatility": rolling_vol_clean.max(),
            "min_volatility": rolling_vol_clean.min(),
            "std_volatility": rolling_vol_clean.std(),
            "window_size": window,
            "annualized": annualize,
            "observations": len(rolling_vol_clean)
        }
    
    @staticmethod
    def realized_volatility(returns: List[float], annualize: bool = True) -> float:
        """
        Calculate realized volatility over the entire period.
        
        Args:
            returns: List of returns (as percentages)
            annualize: Whether to annualize volatility
            
        Returns:
            Realized volatility
        """
        if not returns:
            return 0.0
        
        vol = np.std(returns)
        
        if annualize:
            vol = vol * np.sqrt(252)
            
        return float(vol)
    
    @staticmethod
    def volatility_clustering(returns: List[float], window: int = 30) -> Dict[str, Any]:
        """
        Analyze volatility clustering patterns.
        
        Args:
            returns: List of returns (as percentages)
            window: Window size for volatility calculation
            
        Returns:
            Dictionary with clustering analysis
        """
        if len(returns) < window * 2:
            return {"error": "Insufficient data for clustering analysis"}
        
        returns_series = pd.Series(returns)
        
        # Calculate rolling volatility
        rolling_vol = returns_series.rolling(window=window).std()
        rolling_vol_clean = rolling_vol.dropna()
        
        if len(rolling_vol_clean) < 10:
            return {"error": "Insufficient volatility observations"}
        
        # Calculate volatility of volatility
        vol_of_vol = rolling_vol_clean.std()
        
        # High volatility periods (above 75th percentile)
        high_vol_threshold = rolling_vol_clean.quantile(0.75)
        high_vol_periods = (rolling_vol_clean > high_vol_threshold).sum()
        
        # Low volatility periods (below 25th percentile)
        low_vol_threshold = rolling_vol_clean.quantile(0.25)
        low_vol_periods = (rolling_vol_clean < low_vol_threshold).sum()
        
        # Persistence (autocorrelation)
        autocorr = rolling_vol_clean.autocorr(lag=1)
        
        return {
            "volatility_of_volatility": vol_of_vol,
            "high_vol_threshold": high_vol_threshold,
            "low_vol_threshold": low_vol_threshold,
            "high_vol_periods": int(high_vol_periods),
            "low_vol_periods": int(low_vol_periods),
            "volatility_persistence": autocorr,
            "clustering_strength": "High" if autocorr > 0.3 else "Medium" if autocorr > 0.1 else "Low",
            "total_periods": len(rolling_vol_clean)
        }
    
    @staticmethod
    def downside_volatility(returns: List[float], threshold: float = 0.0, annualize: bool = True) -> float:
        """
        Calculate downside volatility (volatility of negative returns).
        
        Args:
            returns: List of returns (as percentages)
            threshold: Threshold below which returns are considered downside
            annualize: Whether to annualize volatility
            
        Returns:
            Downside volatility
        """
        if not returns:
            return 0.0
        
        downside_returns = [r for r in returns if r < threshold]
        
        if len(downside_returns) < 2:
            return 0.0
        
        downside_vol = np.std(downside_returns)
        
        if annualize:
            downside_vol = downside_vol * np.sqrt(252)
            
        return float(downside_vol)
    
    @staticmethod
    def volatility_regime_analysis(returns: List[float], window: int = 30) -> Dict[str, Any]:
        """
        Analyze different volatility regimes.
        
        Args:
            returns: List of returns (as percentages)
            window: Window size for regime detection
            
        Returns:
            Dictionary with regime analysis
        """
        if len(returns) < window * 3:
            return {"error": "Insufficient data for regime analysis"}
        
        returns_series = pd.Series(returns)
        rolling_vol = returns_series.rolling(window=window).std() * np.sqrt(252)
        rolling_vol_clean = rolling_vol.dropna()
        
        if len(rolling_vol_clean) < 20:
            return {"error": "Insufficient volatility observations"}
        
        # Define regimes based on percentiles
        low_threshold = rolling_vol_clean.quantile(0.33)
        high_threshold = rolling_vol_clean.quantile(0.67)
        
        # Classify regimes
        regimes = []
        regime_changes = 0
        current_regime = None
        
        for vol in rolling_vol_clean:
            if vol <= low_threshold:
                regime = "Low"
            elif vol >= high_threshold:
                regime = "High"
            else:
                regime = "Medium"
            
            regimes.append(regime)
            
            if current_regime is not None and regime != current_regime:
                regime_changes += 1
            current_regime = regime
        
        # Calculate regime statistics
        regime_counts = pd.Series(regimes).value_counts().to_dict()
        regime_percentages = {k: v/len(regimes)*100 for k, v in regime_counts.items()}
        
        return {
            "regimes": regimes,
            "regime_counts": regime_counts,
            "regime_percentages": regime_percentages,
            "regime_changes": regime_changes,
            "persistence": 1 - (regime_changes / len(regimes)),
            "low_vol_threshold": low_threshold,
            "high_vol_threshold": high_threshold,
            "current_regime": regimes[-1] if regimes else "Unknown",
            "avg_volatility_by_regime": {
                regime: rolling_vol_clean[pd.Series(regimes) == regime].mean()
                for regime in set(regimes)
            }
        }
    
    @staticmethod
    def volatility_forecasting_simple(returns: List[float], window: int = 30, forecast_horizon: int = 5) -> Dict[str, Any]:
        """
        Simple volatility forecasting using rolling averages.
        
        Args:
            returns: List of returns (as percentages)
            window: Window size for volatility calculation
            forecast_horizon: Number of periods to forecast
            
        Returns:
            Dictionary with volatility forecast
        """
        if len(returns) < window + forecast_horizon:
            return {"error": "Insufficient data for forecasting"}
        
        returns_series = pd.Series(returns)
        
        # Calculate rolling volatility
        rolling_vol = returns_series.rolling(window=window).std() * np.sqrt(252)
        rolling_vol_clean = rolling_vol.dropna()
        
        if len(rolling_vol_clean) < 10:
            return {"error": "Insufficient volatility history"}
        
        # Simple forecast: average of recent volatility
        recent_vol = rolling_vol_clean.tail(window//2).mean()
        long_term_vol = rolling_vol_clean.mean()
        
        # Weighted forecast (60% recent, 40% long-term)
        forecast = 0.6 * recent_vol + 0.4 * long_term_vol
        
        # Confidence intervals (simple approach)
        vol_std = rolling_vol_clean.std()
        confidence_95_lower = forecast - 1.96 * vol_std
        confidence_95_upper = forecast + 1.96 * vol_std
        
        return {
            "volatility_forecast": forecast,
            "recent_volatility": recent_vol,
            "long_term_volatility": long_term_vol,
            "confidence_95_lower": max(0, confidence_95_lower),
            "confidence_95_upper": confidence_95_upper,
            "forecast_horizon": forecast_horizon,
            "model_type": "Simple weighted average",
            "historical_volatility_std": vol_std
        }