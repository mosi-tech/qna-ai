"""
Performance Metrics using empyrical library

All performance calculations using empyrical from requirements.txt
From financial-analysis-function-library.json
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional
import warnings
warnings.filterwarnings('ignore')

# Use empyrical library from requirements.txt - no wheel reinvention
import empyrical

from ..utils.data_utils import validate_return_data, validate_price_data, standardize_output


def calculate_returns_metrics(returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate comprehensive return metrics using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        
    Returns:
        Dict: Comprehensive return metrics
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical library - leveraging requirements.txt
        total_return = empyrical.cum_returns_final(returns_series)
        annual_return = empyrical.annual_return(returns_series)
        cumulative_returns = empyrical.cum_returns(returns_series)
        
        result = {
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "annual_return": float(annual_return),
            "annual_return_pct": f"{annual_return * 100:.2f}%",
            "cumulative_returns": cumulative_returns,
            "num_observations": len(returns_series)
        }
        
        return standardize_output(result, "calculate_returns_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Returns calculation failed: {str(e)}"}


def calculate_risk_metrics(returns: Union[pd.Series, Dict[str, Any]], 
                          risk_free_rate: float = 0.02) -> Dict[str, Any]:
    """
    Calculate comprehensive risk metrics using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        risk_free_rate: Risk-free rate
        
    Returns:
        Dict: Comprehensive risk metrics
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical library - leveraging requirements.txt
        volatility = empyrical.annual_volatility(returns_series)
        sharpe_ratio = empyrical.sharpe_ratio(returns_series, risk_free=risk_free_rate)
        sortino_ratio = empyrical.sortino_ratio(returns_series, required_return=risk_free_rate)
        max_drawdown = empyrical.max_drawdown(returns_series)
        calmar_ratio = empyrical.calmar_ratio(returns_series)
        var_95 = empyrical.value_at_risk(returns_series, cutoff=0.05)
        cvar_95 = empyrical.conditional_value_at_risk(returns_series, cutoff=0.05)
        skewness = empyrical.stats.skew(returns_series)
        kurtosis = empyrical.stats.kurtosis(returns_series)
        
        result = {
            "volatility": float(volatility),
            "volatility_pct": f"{volatility * 100:.2f}%",
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "sortino_ratio": float(sortino_ratio),
            "calmar_ratio": float(calmar_ratio),
            "var_95": float(var_95),
            "var_95_pct": f"{var_95 * 100:.2f}%",
            "cvar_95": float(cvar_95),
            "cvar_95_pct": f"{cvar_95 * 100:.2f}%",
            "skewness": float(skewness),
            "kurtosis": float(kurtosis)
        }
        
        return standardize_output(result, "calculate_risk_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Risk calculation failed: {str(e)}"}


def calculate_benchmark_metrics(returns: Union[pd.Series, Dict[str, Any]],
                                benchmark_returns: Union[pd.Series, Dict[str, Any]],
                                risk_free_rate: float = 0.02) -> Dict[str, Any]:
    """
    Calculate benchmark comparison metrics using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Portfolio returns
        benchmark_returns: Benchmark returns
        risk_free_rate: Risk-free rate
        
    Returns:
        Dict: Benchmark comparison metrics
    """
    try:
        portfolio_returns = validate_return_data(returns)
        benchmark_returns = validate_return_data(benchmark_returns)
        
        # Align series
        from ..utils.data_utils import align_series
        portfolio_aligned, benchmark_aligned = align_series(portfolio_returns, benchmark_returns)
        
        if empyrical is None:
            # Basic calculations
            excess_returns = portfolio_aligned - benchmark_aligned
            tracking_error = excess_returns.std() * np.sqrt(252)
            information_ratio = excess_returns.mean() * 252 / tracking_error if tracking_error > 0 else 0
            
            # Beta calculation
            covariance = np.cov(portfolio_aligned, benchmark_aligned)[0, 1]
            benchmark_variance = np.var(benchmark_aligned)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1
            
            alpha = portfolio_aligned.mean() * 252 - (risk_free_rate + beta * (benchmark_aligned.mean() * 252 - risk_free_rate))
        else:
            # Use empyrical library - leveraging requirements.txt
            alpha = empyrical.alpha(portfolio_aligned, benchmark_aligned, risk_free=risk_free_rate)
            beta = empyrical.beta(portfolio_aligned, benchmark_aligned)
            tracking_error = empyrical.tracking_error(portfolio_aligned, benchmark_aligned)
            information_ratio = empyrical.excess_sharpe(portfolio_aligned, benchmark_aligned)
            up_capture = empyrical.up_capture(portfolio_aligned, benchmark_aligned)
            down_capture = empyrical.down_capture(portfolio_aligned, benchmark_aligned)
        
        result = {
            "alpha": float(alpha),
            "alpha_pct": f"{alpha * 100:.2f}%",
            "beta": float(beta),
            "tracking_error": float(tracking_error),
            "tracking_error_pct": f"{tracking_error * 100:.2f}%",
            "information_ratio": float(information_ratio),
        }
        
        # Add advanced metrics if empyrical available
        if empyrical is not None:
            result.update({
                "up_capture": float(up_capture),
                "down_capture": float(down_capture)
            })
        
        return standardize_output(result, "calculate_benchmark_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Benchmark comparison failed: {str(e)}"}


def calculate_drawdown_analysis(returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate detailed drawdown analysis using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        
    Returns:
        Dict: Drawdown analysis
    """
    try:
        returns_series = validate_return_data(returns)
        
        if empyrical is None:
            # Basic calculations
            cumulative = (1 + returns_series).cumprod()
            running_max = cumulative.expanding().max()
            drawdown_series = (cumulative - running_max) / running_max
            max_drawdown = drawdown_series.min()
        else:
            # Use empyrical library - leveraging requirements.txt
            max_drawdown = empyrical.max_drawdown(returns_series)
            drawdown_series = empyrical.drawdown_details(empyrical.cum_returns(returns_series))
        
        result = {
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "drawdown_series": drawdown_series if isinstance(drawdown_series, pd.Series) else pd.Series(drawdown_series)
        }
        
        return standardize_output(result, "calculate_drawdown_analysis")
        
    except Exception as e:
        return {"success": False, "error": f"Drawdown analysis failed: {str(e)}"}


# Registry using library-based functions - no manual calculations
PERFORMANCE_METRICS_FUNCTIONS = {
    'calculate_returns_metrics': calculate_returns_metrics,
    'calculate_risk_metrics': calculate_risk_metrics,
    'calculate_benchmark_metrics': calculate_benchmark_metrics,
    'calculate_drawdown_analysis': calculate_drawdown_analysis
}