"""
Statistical Analysis Functions

Core statistical analysis functions, matching the categorical 
structure from financial-analysis-function-library.json

From financial-analysis-function-library.json category: statistical_analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


def calculatePercentile(
    data: Union[pd.Series, List[float], Dict[str, Any]], 
    percentile: float = 50
) -> Dict[str, Any]:
    """
    Calculate specified percentile of data.
    
    From financial-analysis-function-library.json
    
    Args:
        data: Price or return data
        percentile: Percentile to calculate (0-100)
        
    Returns:
        {
            "percentile_value": float,
            "percentile": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(data, dict) and "returns" in data:
            series = data["returns"]
        elif isinstance(data, dict) and "prices" in data:
            series = data["prices"]
        elif isinstance(data, dict) and "filtered_data" in data:
            series = data["filtered_data"]
        elif isinstance(data, (list, np.ndarray)):
            series = pd.Series(data)
        elif isinstance(data, pd.Series):
            series = data
        else:
            return {"success": False, "error": "Invalid data format"}
        
        if len(series) == 0:
            return {"success": False, "error": "No data provided"}
        
        if not 0 <= percentile <= 100:
            return {"success": False, "error": "Percentile must be between 0 and 100"}
        
        # Calculate percentile
        percentile_value = np.percentile(series.dropna(), percentile)
        
        return {
            "success": True,
            "percentile_value": float(percentile_value),
            "percentile": float(percentile),
            "num_observations": len(series.dropna()),
            "min_value": float(series.min()),
            "max_value": float(series.max()),
            "median": float(series.median())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Percentile calculation failed: {str(e)}"}


def calculateHerfindahlIndex(
    weights: Union[List[float], pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate concentration index for portfolio weights.
    
    From financial-analysis-function-library.json
    
    Args:
        weights: Array of portfolio weights (should sum to 1)
        
    Returns:
        {
            "herfindahl_index": float,
            "equivalent_number": float,
            "concentration_level": str,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(weights, dict) and "weights" in weights:
            weight_series = pd.Series(weights["weights"])
        elif isinstance(weights, dict) and "data" in weights:
            weight_series = pd.Series(weights["data"])
        elif isinstance(weights, (list, np.ndarray)):
            weight_series = pd.Series(weights)
        elif isinstance(weights, pd.Series):
            weight_series = weights
        else:
            return {"success": False, "error": "Invalid weights format"}
        
        if len(weight_series) == 0:
            return {"success": False, "error": "No weights provided"}
        
        # Remove any negative weights and normalize
        weight_series = weight_series[weight_series >= 0]
        
        if weight_series.sum() == 0:
            return {"success": False, "error": "All weights are zero"}
        
        # Normalize weights to sum to 1
        normalized_weights = weight_series / weight_series.sum()
        
        # Calculate Herfindahl Index (sum of squared weights)
        herfindahl_index = (normalized_weights ** 2).sum()
        
        # Equivalent number of assets (1/HHI)
        equivalent_number = 1 / herfindahl_index
        
        # Determine concentration level
        if herfindahl_index > 0.25:
            concentration_level = "Highly Concentrated"
        elif herfindahl_index > 0.15:
            concentration_level = "Moderately Concentrated"
        elif herfindahl_index > 0.10:
            concentration_level = "Somewhat Concentrated"
        else:
            concentration_level = "Well Diversified"
        
        return {
            "success": True,
            "herfindahl_index": float(herfindahl_index),
            "equivalent_number": float(equivalent_number),
            "concentration_level": concentration_level,
            "num_assets": len(normalized_weights),
            "largest_weight": float(normalized_weights.max()),
            "smallest_weight": float(normalized_weights.min())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Herfindahl Index calculation failed: {str(e)}"}


def calculateTrackingError(
    returns: Union[pd.Series, List[float], Dict[str, Any]],
    benchmark_returns: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate tracking error vs benchmark.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Portfolio return series
        benchmark_returns: Benchmark return series
        
    Returns:
        {
            "tracking_error": float,
            "annualized_tracking_error": float,
            "correlation": float,
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
        
        portfolio_series = extract_series(returns)
        benchmark_series = extract_series(benchmark_returns)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_series,
            'benchmark': benchmark_series
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        # Calculate excess returns (tracking difference)
        excess_returns = aligned_data['portfolio'] - aligned_data['benchmark']
        
        # Calculate tracking error (standard deviation of excess returns)
        tracking_error = excess_returns.std()
        annualized_tracking_error = tracking_error * np.sqrt(252)
        
        # Calculate correlation
        correlation = aligned_data['portfolio'].corr(aligned_data['benchmark'])
        
        return {
            "success": True,
            "tracking_error": float(tracking_error),
            "annualized_tracking_error": float(annualized_tracking_error),
            "tracking_error_pct": f"{annualized_tracking_error * 100:.2f}%",
            "correlation": float(correlation),
            "mean_excess_return": float(excess_returns.mean()),
            "num_observations": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Tracking error calculation failed: {str(e)}"}


def calculateOmegaRatio(
    returns: Union[pd.Series, List[float], Dict[str, Any]], 
    threshold: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate Omega ratio.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series data
        threshold: Return threshold (usually 0 or risk-free rate)
        
    Returns:
        {
            "omega_ratio": float,
            "upside_potential": float,
            "downside_risk": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, (list, np.ndarray)):
            series = pd.Series(returns)
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate excess returns relative to threshold
        excess_returns = series - threshold
        
        # Separate gains and losses
        gains = excess_returns[excess_returns > 0]
        losses = excess_returns[excess_returns < 0]
        
        # Calculate upside potential and downside risk
        upside_potential = gains.sum() if len(gains) > 0 else 0
        downside_risk = abs(losses.sum()) if len(losses) > 0 else 0
        
        if downside_risk == 0:
            if upside_potential > 0:
                omega_ratio = float('inf')
            else:
                omega_ratio = 1.0
        else:
            omega_ratio = upside_potential / downside_risk
        
        return {
            "success": True,
            "omega_ratio": float(omega_ratio) if omega_ratio != float('inf') else "infinite",
            "upside_potential": float(upside_potential),
            "downside_risk": float(downside_risk),
            "threshold": float(threshold),
            "gain_periods": len(gains),
            "loss_periods": len(losses),
            "neutral_periods": len(excess_returns[excess_returns == 0])
        }
        
    except Exception as e:
        return {"success": False, "error": f"Omega ratio calculation failed: {str(e)}"}


def calculateBestWorstPeriods(
    returns: Union[pd.Series, List[float], Dict[str, Any]], 
    window_size: int = 30
) -> Dict[str, Any]:
    """
    Identify best and worst performing periods.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series data
        window_size: Rolling window size for analysis
        
    Returns:
        {
            "best_period": Dict,
            "worst_period": Dict,
            "rolling_returns": pd.Series,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, (list, np.ndarray)):
            series = pd.Series(returns)
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < window_size:
            return {"success": False, "error": f"Need at least {window_size} observations"}
        
        # Calculate rolling cumulative returns
        rolling_returns = series.rolling(window=window_size).apply(
            lambda x: (1 + x).prod() - 1, raw=False
        ).dropna()
        
        if len(rolling_returns) == 0:
            return {"success": False, "error": "No valid rolling periods"}
        
        # Find best and worst periods
        best_idx = rolling_returns.idxmax()
        worst_idx = rolling_returns.idxmin()
        
        best_return = rolling_returns[best_idx]
        worst_return = rolling_returns[worst_idx]
        
        # Create period information
        best_period = {
            "return": float(best_return),
            "return_pct": f"{best_return * 100:.2f}%",
            "end_date": str(best_idx) if hasattr(best_idx, 'strftime') else str(best_idx),
            "start_date": str(series.index[series.index.get_loc(best_idx) - window_size + 1]) if hasattr(series.index, 'get_loc') else "N/A"
        }
        
        worst_period = {
            "return": float(worst_return),
            "return_pct": f"{worst_return * 100:.2f}%",
            "end_date": str(worst_idx) if hasattr(worst_idx, 'strftime') else str(worst_idx),
            "start_date": str(series.index[series.index.get_loc(worst_idx) - window_size + 1]) if hasattr(series.index, 'get_loc') else "N/A"
        }
        
        return {
            "success": True,
            "best_period": best_period,
            "worst_period": worst_period,
            "rolling_returns": rolling_returns,
            "window_size": window_size,
            "num_periods": len(rolling_returns),
            "average_rolling_return": float(rolling_returns.mean()),
            "rolling_volatility": float(rolling_returns.std())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Best/worst periods calculation failed: {str(e)}"}


def calculateZScore(
    data: Union[pd.Series, List[float], Dict[str, Any]], 
    window: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate Z-score (standardized score) of data.
    
    From financial-analysis-function-library.json
    
    Args:
        data: Price or return data
        window: Rolling window size (if None, uses entire series)
        
    Returns:
        {
            "z_scores": pd.Series,
            "current_z_score": float,
            "extreme_readings": List,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(data, dict) and "returns" in data:
            series = data["returns"]
        elif isinstance(data, dict) and "prices" in data:
            series = data["prices"]
        elif isinstance(data, dict) and "filtered_data" in data:
            series = data["filtered_data"]
        elif isinstance(data, (list, np.ndarray)):
            series = pd.Series(data)
        elif isinstance(data, pd.Series):
            series = data
        else:
            return {"success": False, "error": "Invalid data format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        if window is None:
            # Calculate Z-score for entire series
            mean_val = series.mean()
            std_val = series.std()
            
            if std_val == 0:
                return {"success": False, "error": "Zero standard deviation - cannot calculate Z-score"}
            
            z_scores = (series - mean_val) / std_val
        else:
            # Calculate rolling Z-score
            if len(series) < window:
                return {"success": False, "error": f"Need at least {window} observations for rolling Z-score"}
            
            rolling_mean = series.rolling(window=window).mean()
            rolling_std = series.rolling(window=window).std()
            
            z_scores = (series - rolling_mean) / rolling_std
            z_scores = z_scores.dropna()
        
        current_z_score = z_scores.iloc[-1] if len(z_scores) > 0 else None
        
        # Identify extreme readings (|Z-score| > 2)
        extreme_threshold = 2.0
        extreme_readings = []
        
        for idx, z_val in z_scores.items():
            if abs(z_val) > extreme_threshold:
                extreme_readings.append({
                    "date": str(idx) if hasattr(idx, 'strftime') else str(idx),
                    "z_score": float(z_val),
                    "extreme_type": "positive" if z_val > 0 else "negative"
                })
        
        return {
            "success": True,
            "z_scores": z_scores,
            "current_z_score": float(current_z_score) if current_z_score is not None else None,
            "extreme_readings": extreme_readings,
            "num_extreme_readings": len(extreme_readings),
            "window_size": window,
            "max_z_score": float(z_scores.max()),
            "min_z_score": float(z_scores.min()),
            "mean_z_score": float(z_scores.mean())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Z-score calculation failed: {str(e)}"}


# Registry for MCP server
STATISTICAL_ANALYSIS_FUNCTIONS = {
    'calculatePercentile': calculatePercentile,
    'calculateHerfindahlIndex': calculateHerfindahlIndex,
    'calculateTrackingError': calculateTrackingError,
    'calculateOmegaRatio': calculateOmegaRatio,
    'calculateBestWorstPeriods': calculateBestWorstPeriods,
    'calculateZScore': calculateZScore
}