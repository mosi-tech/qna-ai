"""
Portfolio Performance Analysis

Retail-friendly performance metrics and comparisons.
Focus on metrics that matter to regular investors.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


def portfolio_performance_analyzer(
    portfolio_returns: List[float],
    benchmark_returns: Optional[List[float]] = None,
    portfolio_name: str = "Your Portfolio",
    benchmark_name: str = "S&P 500"
) -> Dict[str, Any]:
    """
    Analyze portfolio performance with retail-friendly metrics
    
    Perfect for: "How is my portfolio actually performing?"
    
    Args:
        portfolio_returns: List of portfolio returns (decimal format, e.g., 0.05 for 5%)
        benchmark_returns: List of benchmark returns for comparison
        portfolio_name: Name for the portfolio
        benchmark_name: Name for the benchmark
        
    Returns:
        Dict with comprehensive performance analysis
    """
    
    returns = np.array(portfolio_returns)
    
    # Basic performance metrics
    total_return = (np.prod(1 + returns) - 1) * 100
    annualized_return = (np.prod(1 + returns) ** (252 / len(returns)) - 1) * 100
    volatility = np.std(returns) * np.sqrt(252) * 100
    
    # Risk metrics
    sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
    
    # Drawdown analysis
    cumulative = np.cumprod(1 + returns)
    rolling_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - rolling_max) / rolling_max
    max_drawdown = np.min(drawdowns) * 100
    
    # Win/loss analysis
    positive_days = np.sum(returns > 0)
    negative_days = np.sum(returns < 0)
    win_rate = (positive_days / len(returns)) * 100
    
    # Best/worst periods
    best_day = np.max(returns) * 100
    worst_day = np.min(returns) * 100
    
    # Performance categories
    if annualized_return > 15:
        performance_grade = "Excellent (A+)"
    elif annualized_return > 12:
        performance_grade = "Very Good (A)"
    elif annualized_return > 8:
        performance_grade = "Good (B)"
    elif annualized_return > 5:
        performance_grade = "Average (C)"
    else:
        performance_grade = "Below Average (D)"
    
    # Risk assessment
    if volatility < 10:
        risk_level = "Low"
    elif volatility < 20:
        risk_level = "Moderate"
    elif volatility < 30:
        risk_level = "High"
    else:
        risk_level = "Very High"
    
    result = {
        "success": True,
        "portfolio_name": portfolio_name,
        "analysis_period": f"{len(returns)} trading days",
        "performance_metrics": {
            "total_return": f"{total_return:.1f}%",
            "annualized_return": f"{annualized_return:.1f}%",
            "volatility": f"{volatility:.1f}%",
            "sharpe_ratio": f"{sharpe_ratio:.2f}",
            "max_drawdown": f"{abs(max_drawdown):.1f}%"
        },
        "performance_grade": performance_grade,
        "risk_assessment": {
            "risk_level": risk_level,
            "win_rate": f"{win_rate:.1f}%",
            "best_day": f"+{best_day:.1f}%",
            "worst_day": f"{worst_day:.1f}%"
        },
        "plain_english_summary": (
            f"{portfolio_name} earned {annualized_return:.1f}% annually with {risk_level.lower()} risk. "
            f"Your worst temporary loss was {abs(max_drawdown):.1f}%. "
            f"You had positive returns {win_rate:.0f}% of the time. "
            f"Overall grade: {performance_grade}."
        )
    }
    
    # Add benchmark comparison if provided
    if benchmark_returns is not None:
        bench_returns = np.array(benchmark_returns)
        bench_total_return = (np.prod(1 + bench_returns) - 1) * 100
        bench_annualized = (np.prod(1 + bench_returns) ** (252 / len(bench_returns)) - 1) * 100
        bench_volatility = np.std(bench_returns) * np.sqrt(252) * 100
        
        # Calculate alpha (excess return)
        alpha = annualized_return - bench_annualized
        
        # Calculate beta (systematic risk)
        covariance = np.cov(returns, bench_returns)[0, 1]
        benchmark_variance = np.var(bench_returns)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
        
        result["benchmark_comparison"] = {
            "benchmark_name": benchmark_name,
            "benchmark_return": f"{bench_annualized:.1f}%",
            "alpha": f"{alpha:+.1f}%",
            "beta": f"{beta:.2f}",
            "outperformance": f"{alpha:+.1f}%",
            "relative_performance": "outperformed" if alpha > 0 else "underperformed"
        }
        
        result["plain_english_summary"] += (
            f" Compared to {benchmark_name}, you {result['benchmark_comparison']['relative_performance']} "
            f"by {abs(alpha):.1f}% annually."
        )
    
    return result


def risk_return_metrics(
    portfolio_data: List[Dict[str, float]],
    risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Calculate risk-return metrics for portfolio analysis
    
    Perfect for: "How much risk am I taking for my returns?"
    
    Args:
        portfolio_data: List of dicts with 'return' and optionally 'date' keys
        risk_free_rate: Risk-free rate for Sharpe ratio calculation
        
    Returns:
        Dict with risk-return analysis
    """
    
    returns = [d['return'] for d in portfolio_data]
    returns_array = np.array(returns)
    
    # Calculate metrics
    mean_return = np.mean(returns_array) * 252  # Annualized
    volatility = np.std(returns_array) * np.sqrt(252)  # Annualized
    sharpe_ratio = (mean_return - risk_free_rate) / volatility if volatility > 0 else 0
    
    # Calculate Sortino ratio (downside deviation)
    downside_returns = returns_array[returns_array < 0]
    downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
    sortino_ratio = (mean_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
    
    # Value at Risk (95% confidence)
    var_95 = np.percentile(returns_array, 5) * 100
    
    # Maximum consecutive losses
    consecutive_losses = 0
    max_consecutive_losses = 0
    for ret in returns_array:
        if ret < 0:
            consecutive_losses += 1
            max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        else:
            consecutive_losses = 0
    
    # Risk-return assessment
    if sharpe_ratio > 1.5:
        risk_return_grade = "Excellent"
    elif sharpe_ratio > 1.0:
        risk_return_grade = "Good"
    elif sharpe_ratio > 0.5:
        risk_return_grade = "Average"
    else:
        risk_return_grade = "Poor"
    
    return {
        "success": True,
        "risk_metrics": {
            "volatility": f"{volatility:.1f}%",
            "downside_deviation": f"{downside_deviation:.1f}%",
            "value_at_risk_95": f"{var_95:.1f}%",
            "max_consecutive_losses": max_consecutive_losses
        },
        "return_metrics": {
            "annualized_return": f"{mean_return:.1f}%",
            "sharpe_ratio": f"{sharpe_ratio:.2f}",
            "sortino_ratio": f"{sortino_ratio:.2f}"
        },
        "risk_return_assessment": {
            "grade": risk_return_grade,
            "interpretation": _interpret_sharpe_ratio(sharpe_ratio)
        },
        "plain_english_summary": (
            f"Your risk-adjusted returns are {risk_return_grade.lower()}. "
            f"For every unit of risk, you're earning {sharpe_ratio:.2f} units of return. "
            f"Your worst expected daily loss (95% confidence) is {abs(var_95):.1f}%."
        )
    }


def benchmark_comparison(
    portfolio_returns: List[float],
    benchmark_returns: List[float],
    portfolio_name: str = "Your Portfolio",
    benchmark_name: str = "S&P 500"
) -> Dict[str, Any]:
    """
    Compare portfolio performance to benchmark
    
    Perfect for: "How am I doing vs the market?"
    
    Args:
        portfolio_returns: Portfolio daily returns
        benchmark_returns: Benchmark daily returns  
        portfolio_name: Name of portfolio
        benchmark_name: Name of benchmark
        
    Returns:
        Dict with detailed comparison analysis
    """
    
    portfolio = np.array(portfolio_returns)
    benchmark = np.array(benchmark_returns)
    
    # Ensure same length
    min_length = min(len(portfolio), len(benchmark))
    portfolio = portfolio[:min_length]
    benchmark = benchmark[:min_length]
    
    # Performance metrics
    port_total = (np.prod(1 + portfolio) - 1) * 100
    bench_total = (np.prod(1 + benchmark) - 1) * 100
    
    port_annual = (np.prod(1 + portfolio) ** (252 / len(portfolio)) - 1) * 100
    bench_annual = (np.prod(1 + benchmark) ** (252 / len(benchmark)) - 1) * 100
    
    # Risk metrics
    port_vol = np.std(portfolio) * np.sqrt(252) * 100
    bench_vol = np.std(benchmark) * np.sqrt(252) * 100
    
    # Beta calculation
    covariance = np.cov(portfolio, benchmark)[0, 1]
    benchmark_variance = np.var(benchmark)
    beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
    
    # Alpha calculation
    alpha = port_annual - bench_annual
    
    # Correlation
    correlation = np.corrcoef(portfolio, benchmark)[0, 1]
    
    # Tracking error
    tracking_error = np.std(portfolio - benchmark) * np.sqrt(252) * 100
    
    # Information ratio
    information_ratio = alpha / tracking_error if tracking_error > 0 else 0
    
    # Up/Down capture
    up_market_days = benchmark > 0
    down_market_days = benchmark < 0
    
    up_capture = (np.mean(portfolio[up_market_days]) / np.mean(benchmark[up_market_days]) * 100) if np.any(up_market_days) else 100
    down_capture = (np.mean(portfolio[down_market_days]) / np.mean(benchmark[down_market_days]) * 100) if np.any(down_market_days) else 100
    
    return {
        "success": True,
        "comparison_summary": {
            "portfolio_name": portfolio_name,
            "benchmark_name": benchmark_name,
            "analysis_period": f"{len(portfolio)} trading days"
        },
        "performance_comparison": {
            "portfolio_return": f"{port_annual:.1f}%",
            "benchmark_return": f"{bench_annual:.1f}%",
            "outperformance": f"{alpha:+.1f}%",
            "alpha": f"{alpha:+.1f}%"
        },
        "risk_comparison": {
            "portfolio_volatility": f"{port_vol:.1f}%",
            "benchmark_volatility": f"{bench_vol:.1f}%",
            "beta": f"{beta:.2f}",
            "correlation": f"{correlation:.2f}",
            "tracking_error": f"{tracking_error:.1f}%"
        },
        "style_analysis": {
            "up_market_capture": f"{up_capture:.0f}%",
            "down_market_capture": f"{down_capture:.0f}%",
            "information_ratio": f"{information_ratio:.2f}"
        },
        "interpretation": {
            "beta_meaning": _interpret_beta(beta),
            "alpha_meaning": _interpret_alpha(alpha),
            "overall_assessment": _overall_assessment(alpha, beta, tracking_error)
        },
        "plain_english_summary": (
            f"{portfolio_name} returned {port_annual:.1f}% vs {bench_annual:.1f}% for {benchmark_name}. "
            f"You {'outperformed' if alpha > 0 else 'underperformed'} by {abs(alpha):.1f}% annually. "
            f"Your portfolio is {_risk_description(beta)} the market with {correlation:.0%} correlation."
        )
    }


def _interpret_sharpe_ratio(sharpe: float) -> str:
    """Interpret Sharpe ratio for retail investors"""
    if sharpe > 2.0:
        return "Outstanding risk-adjusted returns"
    elif sharpe > 1.5:
        return "Very good risk-adjusted returns"
    elif sharpe > 1.0:
        return "Good risk-adjusted returns"
    elif sharpe > 0.5:
        return "Acceptable risk-adjusted returns"
    else:
        return "Poor risk-adjusted returns - too much risk for the return"


def _interpret_beta(beta: float) -> str:
    """Interpret beta for retail investors"""
    if beta > 1.2:
        return "High volatility - moves more than market"
    elif beta > 0.8:
        return "Similar volatility to market"
    else:
        return "Low volatility - moves less than market"


def _interpret_alpha(alpha: float) -> str:
    """Interpret alpha for retail investors"""
    if alpha > 3:
        return "Excellent - generating significant excess returns"
    elif alpha > 1:
        return "Good - beating the market consistently"
    elif alpha > -1:
        return "Average - roughly matching market performance"
    else:
        return "Poor - underperforming the market"


def _risk_description(beta: float) -> str:
    """Risk description based on beta"""
    if beta > 1.2:
        return "riskier than"
    elif beta > 0.8:
        return "similar risk to"
    else:
        return "less risky than"


def _overall_assessment(alpha: float, beta: float, tracking_error: float) -> str:
    """Overall portfolio assessment"""
    if alpha > 2 and beta < 1.2:
        return "Excellent - outperforming with reasonable risk"
    elif alpha > 0 and tracking_error < 8:
        return "Good - beating market with controlled risk"
    elif abs(alpha) < 2:
        return "Average - roughly market-like performance"
    else:
        return "Needs improvement - high risk or poor returns"


# Registry of performance functions
PERFORMANCE_FUNCTIONS = {
    'portfolio_performance_analyzer': portfolio_performance_analyzer,
    'risk_return_metrics': risk_return_metrics,
    'benchmark_comparison': benchmark_comparison
}


def get_performance_function_names():
    """Get list of all performance function names"""
    return list(PERFORMANCE_FUNCTIONS.keys())