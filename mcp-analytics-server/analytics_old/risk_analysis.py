"""
Risk Analysis Functions

Functions for calculating risk metrics and drawdown analysis, matching the 
categorical structure from financial-analysis-function-library.json

From financial-analysis-function-library.json category: risk_analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional


def calculateMaxDrawdown(
    prices: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate maximum drawdown and recovery periods.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price series or result from other functions
        
    Returns:
        {
            "max_drawdown": float,
            "max_drawdown_pct": str,
            "drawdown_start": str,
            "drawdown_end": str,
            "recovery_date": str,
            "drawdown_duration": int,
            "recovery_duration": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "filtered_data" in prices:
            series = prices["filtered_data"]
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 price observations"}
        
        # Calculate cumulative returns and running maximum
        cumulative = series / series.iloc[0]  # Normalize to start at 1
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        # Find maximum drawdown
        max_drawdown = drawdown.min()
        max_dd_date = drawdown.idxmin()
        
        # Find the peak before the max drawdown
        peak_date = running_max.loc[:max_dd_date].idxmax()
        
        # Find recovery date (if any)
        recovery_date = None
        recovery_duration = None
        
        # Look for recovery after the trough
        post_trough = cumulative.loc[max_dd_date:]
        peak_value = running_max.loc[max_dd_date]
        
        recovery_candidates = post_trough[post_trough >= peak_value]
        if len(recovery_candidates) > 0:
            recovery_date = recovery_candidates.index[0]
            recovery_duration = len(series.loc[max_dd_date:recovery_date]) - 1
        
        # Calculate duration
        drawdown_duration = len(series.loc[peak_date:max_dd_date]) - 1
        
        return {
            "success": True,
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "drawdown_start": peak_date.strftime("%Y-%m-%d") if hasattr(peak_date, 'strftime') else str(peak_date),
            "drawdown_end": max_dd_date.strftime("%Y-%m-%d") if hasattr(max_dd_date, 'strftime') else str(max_dd_date),
            "recovery_date": recovery_date.strftime("%Y-%m-%d") if recovery_date and hasattr(recovery_date, 'strftime') else str(recovery_date),
            "drawdown_duration": drawdown_duration,
            "recovery_duration": recovery_duration,
            "recovered": recovery_date is not None
        }
        
    except Exception as e:
        return {"success": False, "error": f"Max drawdown calculation failed: {str(e)}"}


def calculateVaR(
    returns: Union[pd.Series, Dict[str, Any]], 
    confidence: float = 0.95
) -> Dict[str, Any]:
    """
    Calculate Value at Risk at given confidence level.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series or result from other functions
        confidence: Confidence level (e.g., 0.95 for 95% VaR)
        
    Returns:
        {
            "var": float,
            "var_pct": str,
            "confidence": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 10:
            return {"success": False, "error": "Need at least 10 observations"}
        
        if confidence <= 0 or confidence >= 1:
            return {"success": False, "error": "Confidence must be between 0 and 1"}
        
        # Calculate VaR using historical method
        alpha = 1 - confidence
        var_value = np.percentile(series, alpha * 100)
        
        return {
            "success": True,
            "var": float(var_value),
            "var_pct": f"{var_value * 100:.2f}%",
            "confidence": confidence,
            "confidence_pct": f"{confidence * 100:.0f}%",
            "num_observations": len(series),
            "interpretation": f"Worst case loss in {(1-confidence)*100:.0f}% of cases"
        }
        
    except Exception as e:
        return {"success": False, "error": f"VaR calculation failed: {str(e)}"}


def calculateCVaR(
    returns: Union[pd.Series, Dict[str, Any]], 
    confidence: float = 0.95
) -> Dict[str, Any]:
    """
    Calculate Conditional Value at Risk (Expected Shortfall).
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series or result from other functions
        confidence: Confidence level (e.g., 0.95 for 95% CVaR)
        
    Returns:
        {
            "cvar": float,
            "cvar_pct": str,
            "var": float,
            "confidence": float,
            "num_tail_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 10:
            return {"success": False, "error": "Need at least 10 observations"}
        
        if confidence <= 0 or confidence >= 1:
            return {"success": False, "error": "Confidence must be between 0 and 1"}
        
        # Calculate VaR first
        alpha = 1 - confidence
        var_value = np.percentile(series, alpha * 100)
        
        # Calculate CVaR as average of returns below VaR
        tail_returns = series[series <= var_value]
        cvar_value = tail_returns.mean()
        
        return {
            "success": True,
            "cvar": float(cvar_value),
            "cvar_pct": f"{cvar_value * 100:.2f}%",
            "var": float(var_value),
            "confidence": confidence,
            "confidence_pct": f"{confidence * 100:.0f}%",
            "num_tail_observations": len(tail_returns),
            "total_observations": len(series),
            "interpretation": f"Average loss in worst {(1-confidence)*100:.0f}% of cases"
        }
        
    except Exception as e:
        return {"success": False, "error": f"CVaR calculation failed: {str(e)}"}


def calculateDownsideDeviation(
    returns: Union[pd.Series, Dict[str, Any]],
    target_return: float = 0.0,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate downside deviation relative to target return.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series or result from other functions
        target_return: Target return threshold (annualized)
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "downside_deviation": float,
            "downside_deviation_pct": str,
            "target_return": float,
            "downside_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Convert target return to daily
        daily_target = target_return / trading_days_per_year
        
        # Calculate downside returns (returns below target)
        downside_returns = series[series < daily_target]
        
        if len(downside_returns) == 0:
            return {"success": False, "error": "No downside returns found"}
        
        # Calculate downside deviation
        downside_deviation = np.sqrt(((downside_returns - daily_target) ** 2).mean())
        
        # Annualize the deviation
        annualized_downside_dev = downside_deviation * np.sqrt(trading_days_per_year)
        
        return {
            "success": True,
            "downside_deviation": float(annualized_downside_dev),
            "downside_deviation_pct": f"{annualized_downside_dev * 100:.2f}%",
            "target_return": target_return,
            "downside_observations": len(downside_returns),
            "total_observations": len(series),
            "downside_frequency": len(downside_returns) / len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Downside deviation calculation failed: {str(e)}"}


def calculateUpsideCapture(
    returns: Union[pd.Series, Dict[str, Any]],
    benchmark_returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate upside capture ratio vs benchmark.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Portfolio return series
        benchmark_returns: Benchmark return series
        
    Returns:
        {
            "upside_capture": float,
            "upside_capture_pct": str,
            "portfolio_upside_return": float,
            "benchmark_upside_return": float,
            "upside_periods": int,
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
        
        # Filter for upside periods (benchmark > 0)
        upside_periods = aligned_data[aligned_data['benchmark'] > 0]
        
        if len(upside_periods) == 0:
            return {"success": False, "error": "No upside periods found"}
        
        # Calculate average returns during upside periods
        portfolio_upside = upside_periods['portfolio'].mean()
        benchmark_upside = upside_periods['benchmark'].mean()
        
        if benchmark_upside == 0:
            return {"success": False, "error": "Benchmark upside return is zero"}
        
        # Calculate upside capture ratio
        upside_capture = portfolio_upside / benchmark_upside
        
        # Annualize the returns
        annualized_portfolio = portfolio_upside * 252
        annualized_benchmark = benchmark_upside * 252
        
        return {
            "success": True,
            "upside_capture": float(upside_capture),
            "upside_capture_pct": f"{upside_capture * 100:.2f}%",
            "portfolio_upside_return": float(annualized_portfolio),
            "benchmark_upside_return": float(annualized_benchmark),
            "upside_periods": len(upside_periods),
            "total_periods": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Upside capture calculation failed: {str(e)}"}


def calculateDownsideCapture(
    returns: Union[pd.Series, Dict[str, Any]],
    benchmark_returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate downside capture ratio vs benchmark.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Portfolio return series
        benchmark_returns: Benchmark return series
        
    Returns:
        {
            "downside_capture": float,
            "downside_capture_pct": str,
            "portfolio_downside_return": float,
            "benchmark_downside_return": float,
            "downside_periods": int,
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
        
        # Filter for downside periods (benchmark < 0)
        downside_periods = aligned_data[aligned_data['benchmark'] < 0]
        
        if len(downside_periods) == 0:
            return {"success": False, "error": "No downside periods found"}
        
        # Calculate average returns during downside periods
        portfolio_downside = downside_periods['portfolio'].mean()
        benchmark_downside = downside_periods['benchmark'].mean()
        
        if benchmark_downside == 0:
            return {"success": False, "error": "Benchmark downside return is zero"}
        
        # Calculate downside capture ratio
        downside_capture = portfolio_downside / benchmark_downside
        
        # Annualize the returns
        annualized_portfolio = portfolio_downside * 252
        annualized_benchmark = benchmark_downside * 252
        
        return {
            "success": True,
            "downside_capture": float(downside_capture),
            "downside_capture_pct": f"{downside_capture * 100:.2f}%",
            "portfolio_downside_return": float(annualized_portfolio),
            "benchmark_downside_return": float(annualized_benchmark),
            "downside_periods": len(downside_periods),
            "total_periods": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Downside capture calculation failed: {str(e)}"}


def calculateSkewness(
    returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate skewness of return distribution.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series or result from other functions
        
    Returns:
        {
            "skewness": float,
            "interpretation": str,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 3:
            return {"success": False, "error": "Need at least 3 observations"}
        
        # Calculate skewness
        from scipy.stats import skew
        skewness_value = skew(series, nan_policy='omit')
        
        # Interpret skewness
        if skewness_value > 0.5:
            interpretation = "Right-skewed (positive tail risk)"
        elif skewness_value < -0.5:
            interpretation = "Left-skewed (negative tail risk)"
        else:
            interpretation = "Approximately symmetric"
        
        return {
            "success": True,
            "skewness": float(skewness_value),
            "interpretation": interpretation,
            "num_observations": len(series),
            "mean_return": float(series.mean()),
            "std_return": float(series.std())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Skewness calculation failed: {str(e)}"}


def calculateKurtosis(
    returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate kurtosis (tail heaviness) of return distribution.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series or result from other functions
        
    Returns:
        {
            "kurtosis": float,
            "excess_kurtosis": float,
            "interpretation": str,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 4:
            return {"success": False, "error": "Need at least 4 observations"}
        
        # Calculate kurtosis
        from scipy.stats import kurtosis
        kurtosis_value = kurtosis(series, nan_policy='omit', fisher=False)  # Pearson's definition
        excess_kurtosis = kurtosis_value - 3  # Excess kurtosis
        
        # Interpret excess kurtosis
        if excess_kurtosis > 1:
            interpretation = "Leptokurtic (fat tails, high tail risk)"
        elif excess_kurtosis < -1:
            interpretation = "Platykurtic (thin tails, low tail risk)"
        else:
            interpretation = "Approximately mesokurtic (normal-like tails)"
        
        return {
            "success": True,
            "kurtosis": float(kurtosis_value),
            "excess_kurtosis": float(excess_kurtosis),
            "interpretation": interpretation,
            "num_observations": len(series),
            "mean_return": float(series.mean()),
            "std_return": float(series.std())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Kurtosis calculation failed: {str(e)}"}


# Registry for MCP server
RISK_ANALYSIS_FUNCTIONS = {
    'calculateMaxDrawdown': calculateMaxDrawdown,
    'calculateVaR': calculateVaR,
    'calculateCVaR': calculateCVaR,
    'calculateDownsideDeviation': calculateDownsideDeviation,
    'calculateUpsideCapture': calculateUpsideCapture,
    'calculateDownsideCapture': calculateDownsideCapture,
    'calculateSkewness': calculateSkewness,
    'calculateKurtosis': calculateKurtosis
}