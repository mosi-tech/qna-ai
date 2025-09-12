"""
Portfolio Risk Analysis Functions

Atomic functions for calculating risk metrics and drawdown analysis.
Each function handles ONE specific risk calculation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional


def calculate_drawdown_series(
    returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate running drawdown series from returns.
    
    Args:
        returns: pd.Series of returns or result from other functions
        
    Returns:
        {
            "drawdown_series": pd.Series,  # Running drawdown values
            "underwater_curve": pd.Series,  # Same as drawdown_series
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
        
        # Calculate cumulative returns and running maximum
        cumulative = (1 + series).cumprod()
        running_max = cumulative.expanding().max()
        
        # Calculate drawdown series
        drawdown = (cumulative - running_max) / running_max
        
        return {
            "success": True,
            "drawdown_series": drawdown,
            "underwater_curve": drawdown,  # Same thing, different name
            "num_points": len(drawdown),
            "start_date": drawdown.index[0].strftime("%Y-%m-%d"),
            "end_date": drawdown.index[-1].strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        return {"success": False, "error": f"Drawdown series calculation failed: {str(e)}"}


def calculate_max_drawdown(
    returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate maximum drawdown and related statistics.
    
    Args:
        returns: pd.Series of returns or result from other functions
        
    Returns:
        {
            "max_drawdown": float,
            "max_drawdown_pct": str,
            "max_drawdown_date": str,
            "recovery_date": str or None,
            "underwater_days": int,
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
        
        # Calculate drawdown series
        cumulative = (1 + series).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        # Find maximum drawdown
        max_drawdown = drawdown.min()
        max_dd_date = drawdown.idxmin()
        
        # Find recovery date (first date after max drawdown where drawdown = 0)
        recovery_date = None
        after_max_dd = drawdown[drawdown.index > max_dd_date]
        recovery_mask = after_max_dd >= -0.001  # Within 0.1% of zero
        
        if recovery_mask.any():
            recovery_date = after_max_dd[recovery_mask].index[0].strftime("%Y-%m-%d")
        
        # Count underwater days (drawdown < -1%)
        underwater_days = (drawdown < -0.01).sum()
        
        return {
            "success": True,
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "max_drawdown_date": max_dd_date.strftime("%Y-%m-%d"),
            "recovery_date": recovery_date,
            "underwater_days": int(underwater_days),
            "total_days": len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Max drawdown calculation failed: {str(e)}"}


def calculate_var(
    returns: Union[pd.Series, Dict[str, Any]],
    confidence_level: float = 0.05
) -> Dict[str, Any]:
    """
    Calculate Value at Risk (VaR) at specified confidence level.
    
    Args:
        returns: pd.Series of returns or result from other functions
        confidence_level: Confidence level (0.05 = 5% VaR)
        
    Returns:
        {
            "var": float,  # VaR as negative number
            "var_pct": str,
            "confidence_level": float,
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
            return {"success": False, "error": "Need at least 10 observations for VaR"}
        
        # Calculate VaR using empirical quantile
        var = series.quantile(confidence_level)
        
        return {
            "success": True,
            "var": float(var),
            "var_pct": f"{var * 100:.2f}%",
            "confidence_level": confidence_level,
            "confidence_pct": f"{(1-confidence_level)*100:.0f}%",
            "num_observations": len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"VaR calculation failed: {str(e)}"}


def calculate_cvar(
    returns: Union[pd.Series, Dict[str, Any]],
    confidence_level: float = 0.05
) -> Dict[str, Any]:
    """
    Calculate Conditional Value at Risk (Expected Shortfall).
    
    Args:
        returns: pd.Series of returns or result from other functions
        confidence_level: Confidence level (0.05 = 5% CVaR)
        
    Returns:
        {
            "cvar": float,  # CVaR as negative number
            "cvar_pct": str,
            "var": float,  # Also return VaR for comparison
            "tail_observations": int,
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
            return {"success": False, "error": "Need at least 10 observations for CVaR"}
        
        # Calculate VaR first
        var = series.quantile(confidence_level)
        
        # Calculate CVaR as mean of returns below VaR
        tail_returns = series[series <= var]
        
        if len(tail_returns) == 0:
            return {"success": False, "error": "No tail returns for CVaR calculation"}
        
        cvar = tail_returns.mean()
        
        return {
            "success": True,
            "cvar": float(cvar),
            "cvar_pct": f"{cvar * 100:.2f}%",
            "var": float(var),
            "var_pct": f"{var * 100:.2f}%",
            "tail_observations": len(tail_returns),
            "confidence_level": confidence_level
        }
        
    except Exception as e:
        return {"success": False, "error": f"CVaR calculation failed: {str(e)}"}


def calculate_beta(
    portfolio_returns: Union[pd.Series, Dict[str, Any]],
    market_returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate portfolio beta relative to market benchmark.
    
    Args:
        portfolio_returns: Portfolio return series
        market_returns: Market/benchmark return series
        
    Returns:
        {
            "beta": float,
            "correlation": float,
            "r_squared": float,
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(portfolio_returns, dict) and "returns" in portfolio_returns:
            port_series = portfolio_returns["returns"]
        elif isinstance(portfolio_returns, dict) and "filtered_data" in portfolio_returns:
            port_series = portfolio_returns["filtered_data"]
        elif isinstance(portfolio_returns, pd.Series):
            port_series = portfolio_returns
        else:
            return {"success": False, "error": "Invalid portfolio returns format"}
            
        if isinstance(market_returns, dict) and "returns" in market_returns:
            market_series = market_returns["returns"]
        elif isinstance(market_returns, dict) and "filtered_data" in market_returns:
            market_series = market_returns["filtered_data"]
        elif isinstance(market_returns, pd.Series):
            market_series = market_returns
        else:
            return {"success": False, "error": "Invalid market returns format"}
        
        # Align the series
        aligned = pd.DataFrame({
            'portfolio': port_series,
            'market': market_series
        }).dropna()
        
        if len(aligned) < 10:
            return {"success": False, "error": "Insufficient aligned data for beta calculation"}
        
        # Calculate beta using covariance / variance
        covariance = aligned['portfolio'].cov(aligned['market'])
        market_variance = aligned['market'].var()
        
        if market_variance == 0:
            return {"success": False, "error": "Zero market variance - cannot calculate beta"}
        
        beta = covariance / market_variance
        
        # Calculate correlation and R-squared
        correlation = aligned['portfolio'].corr(aligned['market'])
        r_squared = correlation ** 2
        
        return {
            "success": True,
            "beta": float(beta),
            "correlation": float(correlation),
            "r_squared": float(r_squared),
            "observations": len(aligned)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Beta calculation failed: {str(e)}"}


def identify_bear_markets(
    returns: Union[pd.Series, Dict[str, Any]],
    threshold: float = -0.20
) -> Dict[str, Any]:
    """
    Identify bear market periods (drawdowns exceeding threshold).
    
    Args:
        returns: pd.Series of returns or result from other functions
        threshold: Drawdown threshold for bear market (-0.20 = -20%)
        
    Returns:
        {
            "bear_markets": List[Dict],  # [{"start": date, "end": date, "drawdown": float}]
            "num_bear_markets": int,
            "total_bear_days": int,
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
        
        # Calculate drawdown series
        cumulative = (1 + series).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        # Find bear market periods
        bear_mask = drawdown <= threshold
        bear_markets = []
        total_bear_days = 0
        
        if bear_mask.any():
            # Find contiguous bear market periods
            bear_periods = []
            in_bear = False
            start_date = None
            
            for date, is_bear in bear_mask.items():
                if is_bear and not in_bear:
                    # Start of bear market
                    in_bear = True
                    start_date = date
                elif not is_bear and in_bear:
                    # End of bear market
                    in_bear = False
                    bear_periods.append((start_date, date))
                    
            # Handle case where bear market extends to end of data
            if in_bear:
                bear_periods.append((start_date, drawdown.index[-1]))
            
            # Create bear market summaries
            for start, end in bear_periods:
                bear_period_dd = drawdown[start:end]
                max_dd = bear_period_dd.min()
                duration = len(bear_period_dd)
                
                bear_markets.append({
                    "start_date": start.strftime("%Y-%m-%d"),
                    "end_date": end.strftime("%Y-%m-%d"),
                    "max_drawdown": float(max_dd),
                    "max_drawdown_pct": f"{max_dd * 100:.1f}%",
                    "duration_days": duration
                })
                
                total_bear_days += duration
        
        return {
            "success": True,
            "bear_markets": bear_markets,
            "num_bear_markets": len(bear_markets),
            "total_bear_days": total_bear_days,
            "threshold": threshold,
            "threshold_pct": f"{threshold * 100:.0f}%"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Bear market identification failed: {str(e)}"}


# Registry for MCP server
RISK_ANALYSIS_FUNCTIONS = {
    'calculate_drawdown_series': calculate_drawdown_series,
    'calculate_max_drawdown': calculate_max_drawdown,
    'calculate_var': calculate_var,
    'calculate_cvar': calculate_cvar,
    'calculate_beta': calculate_beta,
    'identify_bear_markets': identify_bear_markets
}