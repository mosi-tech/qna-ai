"""
Portfolio Performance Metrics Functions

Atomic functions for calculating performance and risk metrics.
Each function takes processed returns and calculates ONE specific metric.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional


def calculate_total_return(
    returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate total return over the entire period.
    
    Args:
        returns: pd.Series of returns or result from other functions
        
    Returns:
        {
            "total_return": float,  # Total return as decimal (0.20 = 20%)
            "total_return_pct": str,  # Formatted percentage
            "num_days": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) == 0:
            return {"success": False, "error": "No returns data"}
        
        # Calculate cumulative return
        total_return = (1 + series).prod() - 1
        
        return {
            "success": True,
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "num_days": len(series),
            "start_date": series.index[0].strftime("%Y-%m-%d"),
            "end_date": series.index[-1].strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        return {"success": False, "error": f"Total return calculation failed: {str(e)}"}


def calculate_annualized_return(
    returns: Union[pd.Series, Dict[str, Any]],
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate annualized return from return series.
    
    Args:
        returns: pd.Series of returns or result from other functions
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "annualized_return": float,
            "annualized_return_pct": str,
            "years_analyzed": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) == 0:
            return {"success": False, "error": "No returns data"}
        
        # Calculate total return and annualize
        total_return = (1 + series).prod() - 1
        years = len(series) / trading_days_per_year
        
        if years <= 0:
            return {"success": False, "error": "Invalid time period"}
        
        annualized_return = (1 + total_return) ** (1/years) - 1
        
        return {
            "success": True,
            "annualized_return": float(annualized_return),
            "annualized_return_pct": f"{annualized_return * 100:.2f}%",
            "years_analyzed": round(years, 2),
            "total_return": float(total_return)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Annualized return calculation failed: {str(e)}"}


def calculate_volatility(
    returns: Union[pd.Series, Dict[str, Any]],
    annualized: bool = True,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate volatility (standard deviation of returns).
    
    Args:
        returns: pd.Series of returns or result from other functions
        annualized: Whether to annualize the volatility
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "volatility": float,
            "volatility_pct": str,
            "annualized": bool,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate standard deviation
        volatility = series.std()
        
        if annualized:
            volatility *= np.sqrt(trading_days_per_year)
        
        return {
            "success": True,
            "volatility": float(volatility),
            "volatility_pct": f"{volatility * 100:.2f}%",
            "annualized": annualized,
            "num_observations": len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Volatility calculation failed: {str(e)}"}


def calculate_sharpe_ratio(
    returns: Union[pd.Series, Dict[str, Any]],
    risk_free_rate: float = 0.02,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate Sharpe ratio (risk-adjusted return).
    
    Args:
        returns: pd.Series of returns or result from other functions
        risk_free_rate: Annual risk-free rate as decimal
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "sharpe_ratio": float,
            "excess_return": float,
            "volatility": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate components
        daily_rf_rate = risk_free_rate / trading_days_per_year
        excess_returns = series - daily_rf_rate
        
        mean_excess = excess_returns.mean()
        volatility = excess_returns.std()
        
        if volatility == 0:
            return {"success": False, "error": "Zero volatility - cannot calculate Sharpe ratio"}
        
        # Annualized Sharpe ratio
        sharpe_ratio = (mean_excess / volatility) * np.sqrt(trading_days_per_year)
        
        # Annualized excess return
        annualized_excess = mean_excess * trading_days_per_year
        annualized_volatility = volatility * np.sqrt(trading_days_per_year)
        
        return {
            "success": True,
            "sharpe_ratio": float(sharpe_ratio),
            "excess_return": float(annualized_excess),
            "volatility": float(annualized_volatility),
            "risk_free_rate": risk_free_rate
        }
        
    except Exception as e:
        return {"success": False, "error": f"Sharpe ratio calculation failed: {str(e)}"}


def calculate_sortino_ratio(
    returns: Union[pd.Series, Dict[str, Any]],
    risk_free_rate: float = 0.02,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate Sortino ratio (downside risk-adjusted return).
    
    Args:
        returns: pd.Series of returns or result from other functions
        risk_free_rate: Annual risk-free rate as decimal
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "sortino_ratio": float,
            "excess_return": float,
            "downside_deviation": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate components
        daily_rf_rate = risk_free_rate / trading_days_per_year
        excess_returns = series - daily_rf_rate
        
        # Only consider negative excess returns for downside deviation
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return {"success": False, "error": "No downside returns - cannot calculate Sortino ratio"}
        
        mean_excess = excess_returns.mean()
        downside_deviation = np.sqrt((downside_returns ** 2).mean())
        
        # Annualized Sortino ratio
        sortino_ratio = (mean_excess / downside_deviation) * np.sqrt(trading_days_per_year)
        
        # Annualized metrics
        annualized_excess = mean_excess * trading_days_per_year
        annualized_downside_dev = downside_deviation * np.sqrt(trading_days_per_year)
        
        return {
            "success": True,
            "sortino_ratio": float(sortino_ratio),
            "excess_return": float(annualized_excess),
            "downside_deviation": float(annualized_downside_dev),
            "downside_days": len(downside_returns),
            "total_days": len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Sortino ratio calculation failed: {str(e)}"}


def calculate_calmar_ratio(
    returns: Union[pd.Series, Dict[str, Any]],
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate Calmar ratio (annualized return / max drawdown).
    
    Args:
        returns: pd.Series of returns or result from other functions
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "calmar_ratio": float,
            "annualized_return": float,
            "max_drawdown": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate annualized return
        total_return = (1 + series).prod() - 1
        years = len(series) / trading_days_per_year
        annualized_return = (1 + total_return) ** (1/years) - 1
        
        # Calculate max drawdown
        cumulative = (1 + series).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        if max_drawdown == 0:
            return {"success": False, "error": "Zero max drawdown - cannot calculate Calmar ratio"}
        
        calmar_ratio = annualized_return / abs(max_drawdown)
        
        return {
            "success": True,
            "calmar_ratio": float(calmar_ratio),
            "annualized_return": float(annualized_return),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Calmar ratio calculation failed: {str(e)}"}


# Registry for MCP server
PERFORMANCE_METRICS_FUNCTIONS = {
    'calculate_total_return': calculate_total_return,
    'calculate_annualized_return': calculate_annualized_return,
    'calculate_volatility': calculate_volatility,
    'calculate_sharpe_ratio': calculate_sharpe_ratio,
    'calculate_sortino_ratio': calculate_sortino_ratio,
    'calculate_calmar_ratio': calculate_calmar_ratio
}