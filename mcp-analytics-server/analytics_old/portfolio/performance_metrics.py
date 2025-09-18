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


# Risk Analysis Functions from financial-analysis-function-library.json
def calculate_max_drawdown(
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


def calculate_var(
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


def calculate_cvar(
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


def calculate_cagr(
    start_value: Union[float, Dict[str, Any]], 
    end_value: Union[float, None] = None, 
    years: Union[float, None] = None
) -> Dict[str, Any]:
    """
    Calculate Compound Annual Growth Rate.
    
    From financial-analysis-function-library.json
    
    Args:
        start_value: Starting value or price series
        end_value: Ending value (if start_value is a number)
        years: Number of years (if start_value is a number)
        
    Returns:
        {
            "cagr": float,
            "cagr_pct": str,
            "total_return": float,
            "years": float,
            "success": bool
        }
    """
    try:
        # Handle different input formats
        if isinstance(start_value, dict) and "prices" in start_value:
            # Price series format
            series = start_value["prices"]
            if len(series) < 2:
                return {"success": False, "error": "Need at least 2 price observations"}
            
            start_val = float(series.iloc[0])
            end_val = float(series.iloc[-1])
            
            # Calculate years from date index if available
            if hasattr(series.index[0], 'year'):
                start_date = series.index[0]
                end_date = series.index[-1]
                years_calc = (end_date - start_date).days / 365.25
            else:
                years_calc = len(series) / 252  # Assume daily data, 252 trading days per year
                
        elif isinstance(start_value, (int, float)) and end_value is not None and years is not None:
            # Direct values format
            start_val = float(start_value)
            end_val = float(end_value)
            years_calc = float(years)
        else:
            return {"success": False, "error": "Invalid input format"}
        
        if start_val <= 0 or end_val <= 0:
            return {"success": False, "error": "Values must be positive"}
        
        if years_calc <= 0:
            return {"success": False, "error": "Years must be positive"}
        
        # Calculate CAGR
        total_return = (end_val / start_val) - 1
        cagr = (end_val / start_val) ** (1 / years_calc) - 1
        
        return {
            "success": True,
            "cagr": float(cagr),
            "cagr_pct": f"{cagr * 100:.2f}%",
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "years": float(years_calc),
            "start_value": float(start_val),
            "end_value": float(end_val)
        }
        
    except Exception as e:
        return {"success": False, "error": f"CAGR calculation failed: {str(e)}"}


def calculate_information_ratio(
    returns: Union[pd.Series, Dict[str, Any]],
    benchmark_returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate Information Ratio vs benchmark.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Portfolio return series
        benchmark_returns: Benchmark return series
        
    Returns:
        {
            "information_ratio": float,
            "excess_return": float,
            "tracking_error": float,
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
        
        portfolio_aligned = aligned_data['portfolio']
        benchmark_aligned = aligned_data['benchmark']
        
        # Calculate excess returns
        excess_returns = portfolio_aligned - benchmark_aligned
        
        # Calculate Information Ratio components
        mean_excess_return = excess_returns.mean()
        tracking_error = excess_returns.std()
        
        if tracking_error == 0:
            return {"success": False, "error": "Zero tracking error - cannot calculate Information Ratio"}
        
        information_ratio = mean_excess_return / tracking_error
        
        # Annualize metrics
        annualized_excess = mean_excess_return * 252
        annualized_tracking_error = tracking_error * np.sqrt(252)
        annualized_ir = annualized_excess / annualized_tracking_error
        
        return {
            "success": True,
            "information_ratio": float(annualized_ir),
            "excess_return": float(annualized_excess),
            "excess_return_pct": f"{annualized_excess * 100:.2f}%",
            "tracking_error": float(annualized_tracking_error),
            "tracking_error_pct": f"{annualized_tracking_error * 100:.2f}%",
            "num_observations": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Information ratio calculation failed: {str(e)}"}


def calculate_treynor_ratio(
    returns: Union[pd.Series, Dict[str, Any]],
    market_returns: Union[pd.Series, Dict[str, Any]],
    risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Calculate Treynor ratio.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Portfolio return series
        market_returns: Market return series
        risk_free_rate: Annual risk-free rate as decimal
        
    Returns:
        {
            "treynor_ratio": float,
            "excess_return": float,
            "beta": float,
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
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        portfolio_series = extract_series(returns)
        market_series = extract_series(market_returns)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_series,
            'market': market_series
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        portfolio_aligned = aligned_data['portfolio']
        market_aligned = aligned_data['market']
        
        # Calculate beta
        covariance = np.cov(portfolio_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        if market_variance == 0:
            return {"success": False, "error": "Market variance is zero"}
        
        beta = covariance / market_variance
        
        if beta == 0:
            return {"success": False, "error": "Zero beta - cannot calculate Treynor ratio"}
        
        # Calculate Treynor ratio components
        daily_rf_rate = risk_free_rate / 252
        portfolio_excess = portfolio_aligned.mean() - daily_rf_rate
        
        # Annualized Treynor ratio
        annualized_excess = portfolio_excess * 252
        treynor_ratio = annualized_excess / beta
        
        return {
            "success": True,
            "treynor_ratio": float(treynor_ratio),
            "excess_return": float(annualized_excess),
            "excess_return_pct": f"{annualized_excess * 100:.2f}%",
            "beta": float(beta),
            "risk_free_rate": risk_free_rate,
            "num_observations": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Treynor ratio calculation failed: {str(e)}"}


# Registry for MCP server
PERFORMANCE_METRICS_FUNCTIONS = {
    'calculate_total_return': calculate_total_return,
    'calculate_annualized_return': calculate_annualized_return,
    'calculate_volatility': calculate_volatility,
    'calculate_sharpe_ratio': calculate_sharpe_ratio,
    'calculate_sortino_ratio': calculate_sortino_ratio,
    'calculate_calmar_ratio': calculate_calmar_ratio,
    # Risk analysis functions from library.json
    'calculate_max_drawdown': calculate_max_drawdown,
    'calculate_var': calculate_var,
    'calculate_cvar': calculate_cvar,
    'calculate_cagr': calculate_cagr,
    'calculate_information_ratio': calculate_information_ratio,
    'calculate_treynor_ratio': calculate_treynor_ratio
}