"""
Portfolio Comparison Functions

Atomic functions for comparing portfolio performance against benchmarks
and calculating relative performance metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional, List


def calculate_tracking_error(
    portfolio_returns: Union[pd.Series, Dict[str, Any]],
    benchmark_returns: Union[pd.Series, Dict[str, Any]],
    annualized: bool = True,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate tracking error between portfolio and benchmark.
    
    Args:
        portfolio_returns: Portfolio return series
        benchmark_returns: Benchmark return series
        annualized: Whether to annualize tracking error
        trading_days_per_year: Trading days per year
        
    Returns:
        {
            "tracking_error": float,
            "tracking_error_pct": str,
            "correlation": float,
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
            
        if isinstance(benchmark_returns, dict) and "returns" in benchmark_returns:
            bench_series = benchmark_returns["returns"]
        elif isinstance(benchmark_returns, dict) and "filtered_data" in benchmark_returns:
            bench_series = benchmark_returns["filtered_data"]
        elif isinstance(benchmark_returns, pd.Series):
            bench_series = benchmark_returns
        else:
            return {"success": False, "error": "Invalid benchmark returns format"}
        
        # Align series
        aligned = pd.DataFrame({
            'portfolio': port_series,
            'benchmark': bench_series
        }).dropna()
        
        if len(aligned) < 10:
            return {"success": False, "error": "Insufficient aligned data"}
        
        # Calculate excess returns
        excess_returns = aligned['portfolio'] - aligned['benchmark']
        
        # Calculate tracking error (standard deviation of excess returns)
        tracking_error = excess_returns.std()
        
        if annualized:
            tracking_error *= np.sqrt(trading_days_per_year)
        
        # Calculate correlation
        correlation = aligned['portfolio'].corr(aligned['benchmark'])
        
        return {
            "success": True,
            "tracking_error": float(tracking_error),
            "tracking_error_pct": f"{tracking_error * 100:.2f}%",
            "correlation": float(correlation),
            "annualized": annualized,
            "observations": len(aligned)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Tracking error calculation failed: {str(e)}"}


def calculate_information_ratio(
    portfolio_returns: Union[pd.Series, Dict[str, Any]],
    benchmark_returns: Union[pd.Series, Dict[str, Any]],
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate information ratio (excess return / tracking error).
    
    Args:
        portfolio_returns: Portfolio return series
        benchmark_returns: Benchmark return series
        trading_days_per_year: Trading days per year
        
    Returns:
        {
            "information_ratio": float,
            "excess_return": float,
            "tracking_error": float,
            "success": bool
        }
    """
    try:
        # Handle input formats (same as tracking_error function)
        if isinstance(portfolio_returns, dict) and "returns" in portfolio_returns:
            port_series = portfolio_returns["returns"]
        elif isinstance(portfolio_returns, dict) and "filtered_data" in portfolio_returns:
            port_series = portfolio_returns["filtered_data"]
        elif isinstance(portfolio_returns, pd.Series):
            port_series = portfolio_returns
        else:
            return {"success": False, "error": "Invalid portfolio returns format"}
            
        if isinstance(benchmark_returns, dict) and "returns" in benchmark_returns:
            bench_series = benchmark_returns["returns"]
        elif isinstance(benchmark_returns, dict) and "filtered_data" in benchmark_returns:
            bench_series = benchmark_returns["filtered_data"]
        elif isinstance(benchmark_returns, pd.Series):
            bench_series = benchmark_returns
        else:
            return {"success": False, "error": "Invalid benchmark returns format"}
        
        # Align series
        aligned = pd.DataFrame({
            'portfolio': port_series,
            'benchmark': bench_series
        }).dropna()
        
        if len(aligned) < 10:
            return {"success": False, "error": "Insufficient aligned data"}
        
        # Calculate excess returns
        excess_returns = aligned['portfolio'] - aligned['benchmark']
        
        # Annualized excess return
        mean_excess = excess_returns.mean() * trading_days_per_year
        
        # Annualized tracking error
        tracking_error = excess_returns.std() * np.sqrt(trading_days_per_year)
        
        if tracking_error == 0:
            return {"success": False, "error": "Zero tracking error - cannot calculate information ratio"}
        
        # Information ratio
        information_ratio = mean_excess / tracking_error
        
        return {
            "success": True,
            "information_ratio": float(information_ratio),
            "excess_return": float(mean_excess),
            "excess_return_pct": f"{mean_excess * 100:.2f}%",
            "tracking_error": float(tracking_error),
            "tracking_error_pct": f"{tracking_error * 100:.2f}%"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Information ratio calculation failed: {str(e)}"}


def calculate_alpha(
    portfolio_returns: Union[pd.Series, Dict[str, Any]],
    benchmark_returns: Union[pd.Series, Dict[str, Any]],
    risk_free_rate: float = 0.02,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate Jensen's alpha (portfolio alpha vs benchmark).
    
    Args:
        portfolio_returns: Portfolio return series
        benchmark_returns: Benchmark return series  
        risk_free_rate: Annual risk-free rate
        trading_days_per_year: Trading days per year
        
    Returns:
        {
            "alpha": float,
            "alpha_pct": str,
            "beta": float,
            "r_squared": float,
            "success": bool
        }
    """
    try:
        # Handle input formats (same pattern)
        if isinstance(portfolio_returns, dict) and "returns" in portfolio_returns:
            port_series = portfolio_returns["returns"]
        elif isinstance(portfolio_returns, dict) and "filtered_data" in portfolio_returns:
            port_series = portfolio_returns["filtered_data"]
        elif isinstance(portfolio_returns, pd.Series):
            port_series = portfolio_returns
        else:
            return {"success": False, "error": "Invalid portfolio returns format"}
            
        if isinstance(benchmark_returns, dict) and "returns" in benchmark_returns:
            bench_series = benchmark_returns["returns"]
        elif isinstance(benchmark_returns, dict) and "filtered_data" in benchmark_returns:
            bench_series = benchmark_returns["filtered_data"]
        elif isinstance(benchmark_returns, pd.Series):
            bench_series = benchmark_returns
        else:
            return {"success": False, "error": "Invalid benchmark returns format"}
        
        # Align series
        aligned = pd.DataFrame({
            'portfolio': port_series,
            'benchmark': bench_series
        }).dropna()
        
        if len(aligned) < 10:
            return {"success": False, "error": "Insufficient aligned data"}
        
        # Calculate excess returns (subtract risk-free rate)
        daily_rf = risk_free_rate / trading_days_per_year
        portfolio_excess = aligned['portfolio'] - daily_rf
        benchmark_excess = aligned['benchmark'] - daily_rf
        
        # Calculate beta
        covariance = portfolio_excess.cov(benchmark_excess)
        benchmark_variance = benchmark_excess.var()
        
        if benchmark_variance == 0:
            return {"success": False, "error": "Zero benchmark variance"}
        
        beta = covariance / benchmark_variance
        
        # Calculate alpha using CAPM: alpha = portfolio_return - (rf + beta * (benchmark_return - rf))
        portfolio_mean = portfolio_excess.mean() * trading_days_per_year
        benchmark_mean = benchmark_excess.mean() * trading_days_per_year
        
        alpha = portfolio_mean - (beta * benchmark_mean)
        
        # Calculate R-squared
        correlation = portfolio_excess.corr(benchmark_excess)
        r_squared = correlation ** 2
        
        return {
            "success": True,
            "alpha": float(alpha),
            "alpha_pct": f"{alpha * 100:.2f}%",
            "beta": float(beta),
            "r_squared": float(r_squared),
            "correlation": float(correlation)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Alpha calculation failed: {str(e)}"}


def compare_performance_metrics(
    *return_series_list
) -> Dict[str, Any]:
    """
    Compare performance metrics across multiple return series.
    
    Args:
        *return_series_list: Multiple return series (can be dicts or pd.Series)
        
    Returns:
        {
            "comparison_table": Dict,  # Metrics for each series
            "rankings": Dict,  # Rankings by each metric  
            "best_performer": str,
            "success": bool
        }
    """
    try:
        if len(return_series_list) < 2:
            return {"success": False, "error": "Need at least 2 series to compare"}
        
        # Extract series and create names
        series_dict = {}
        for i, data in enumerate(return_series_list):
            if isinstance(data, dict) and "returns" in data:
                series_dict[f"Series_{i+1}"] = data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                series_dict[f"Series_{i+1}"] = data["filtered_data"]
            elif isinstance(data, pd.Series):
                series_dict[f"Series_{i+1}"] = data
            else:
                return {"success": False, "error": f"Invalid format for series {i+1}"}
        
        # Calculate metrics for each series
        comparison_table = {}
        for name, series in series_dict.items():
            if len(series) < 10:
                continue
                
            total_return = (1 + series).prod() - 1
            years = len(series) / 252
            annualized_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
            volatility = series.std() * np.sqrt(252)
            sharpe = (annualized_return - 0.02) / volatility if volatility > 0 else 0
            
            # Drawdown calculation
            cumulative = (1 + series).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            comparison_table[name] = {
                "total_return": float(total_return),
                "total_return_pct": f"{total_return * 100:.2f}%",
                "annualized_return": float(annualized_return),
                "annualized_return_pct": f"{annualized_return * 100:.2f}%",
                "volatility": float(volatility),
                "volatility_pct": f"{volatility * 100:.2f}%",
                "sharpe_ratio": float(sharpe),
                "max_drawdown": float(max_drawdown),
                "max_drawdown_pct": f"{max_drawdown * 100:.2f}%"
            }
        
        # Create rankings
        rankings = {}
        metrics = ["total_return", "annualized_return", "sharpe_ratio"]
        
        for metric in metrics:
            sorted_series = sorted(
                comparison_table.items(),
                key=lambda x: x[1][metric],
                reverse=True
            )
            rankings[f"best_{metric}"] = sorted_series[0][0]
            rankings[f"{metric}_ranking"] = [name for name, _ in sorted_series]
        
        # Overall best performer (by Sharpe ratio)
        best_performer = rankings["best_sharpe_ratio"]
        
        return {
            "success": True,
            "comparison_table": comparison_table,
            "rankings": rankings,
            "best_performer": best_performer,
            "num_series": len(comparison_table)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Performance comparison failed: {str(e)}"}


def calculate_relative_performance(
    portfolio_returns: Union[pd.Series, Dict[str, Any]],
    benchmark_returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate relative performance metrics vs benchmark.
    
    Args:
        portfolio_returns: Portfolio return series
        benchmark_returns: Benchmark return series
        
    Returns:
        {
            "outperformance": float,  # Total outperformance
            "outperformance_pct": str,
            "win_rate": float,  # % of periods outperforming
            "avg_outperformance": float,  # Average when winning
            "avg_underperformance": float,  # Average when losing
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
            
        if isinstance(benchmark_returns, dict) and "returns" in benchmark_returns:
            bench_series = benchmark_returns["returns"]
        elif isinstance(benchmark_returns, dict) and "filtered_data" in benchmark_returns:
            bench_series = benchmark_returns["filtered_data"]
        elif isinstance(benchmark_returns, pd.Series):
            bench_series = benchmark_returns
        else:
            return {"success": False, "error": "Invalid benchmark returns format"}
        
        # Align series
        aligned = pd.DataFrame({
            'portfolio': port_series,
            'benchmark': bench_series
        }).dropna()
        
        if len(aligned) < 10:
            return {"success": False, "error": "Insufficient aligned data"}
        
        # Calculate relative performance
        relative_returns = aligned['portfolio'] - aligned['benchmark']
        
        # Total outperformance
        portfolio_total = (1 + aligned['portfolio']).prod() - 1
        benchmark_total = (1 + aligned['benchmark']).prod() - 1
        total_outperformance = portfolio_total - benchmark_total
        
        # Win/loss statistics
        wins = relative_returns > 0
        win_rate = wins.mean()
        
        winning_periods = relative_returns[wins]
        losing_periods = relative_returns[~wins]
        
        avg_outperformance = winning_periods.mean() if len(winning_periods) > 0 else 0
        avg_underperformance = losing_periods.mean() if len(losing_periods) > 0 else 0
        
        return {
            "success": True,
            "outperformance": float(total_outperformance),
            "outperformance_pct": f"{total_outperformance * 100:.2f}%",
            "win_rate": float(win_rate),
            "win_rate_pct": f"{win_rate * 100:.1f}%",
            "avg_outperformance": float(avg_outperformance),
            "avg_outperformance_pct": f"{avg_outperformance * 100:.3f}%",
            "avg_underperformance": float(avg_underperformance),
            "avg_underperformance_pct": f"{avg_underperformance * 100:.3f}%",
            "total_periods": len(aligned)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Relative performance calculation failed: {str(e)}"}


# Registry for MCP server
COMPARISON_FUNCTIONS = {
    'calculate_tracking_error': calculate_tracking_error,
    'calculate_information_ratio': calculate_information_ratio,
    'calculate_alpha': calculate_alpha,
    'compare_performance_metrics': compare_performance_metrics,
    'calculate_relative_performance': calculate_relative_performance
}