"""Performance Analysis Package.

This package provides comprehensive performance analysis tools for financial portfolios and assets
using the industry-standard empyrical library. The module implements performance metrics from the
financial-analysis-function-library.json with focus on proven accuracy through established
libraries rather than manual calculations.

Modules:
    metrics: All performance analysis functions with standardized outputs

Available Performance Analysis Functions:
    Core Return Metrics:
        - calculate_returns_metrics: Comprehensive return analysis (total, annual, cumulative)
        - calculate_risk_metrics: Complete risk assessment (volatility, Sharpe, drawdown, VaR)
        - calculate_benchmark_metrics: Relative performance analysis (alpha, beta, tracking error)
        - calculate_drawdown_analysis: Detailed drawdown analysis with time series
    
    Specialized Return Calculations:
        - calculate_annualized_return: Annualized return from price series
        - calculate_cagr: Compound Annual Growth Rate calculation
        - calculate_total_return: Total return including dividends
        - calculate_win_rate: Percentage of positive return periods
    
    Risk-Adjusted Performance:
        - calculate_calmar_ratio: Return to maximum drawdown ratio
        - calculate_omega_ratio: Probability-weighted ratio of gains vs losses
        - calculate_downside_deviation: Downside risk measurement
        - calculate_upside_capture: Upside market participation
        - calculate_downside_capture: Downside market protection
    
    Advanced Analysis:
        - calculate_best_worst_periods: Rolling period performance extremes
        - calculate_dividend_yield: Dividend yield calculation
        - analyze_leverage_fund: Leveraged fund analysis with decay effects

Features:
    - Industry-standard empyrical library implementation for proven accuracy
    - Comprehensive performance metrics covering returns, risk, and relative performance
    - Advanced risk-adjusted ratios (Sharpe, Sortino, Calmar, Omega)
    - Benchmark comparison metrics (alpha, beta, tracking error, capture ratios)
    - Detailed drawdown analysis with recovery time measurement
    - Specialized analysis for leveraged funds and dividend-paying assets
    - Standardized return format with success indicators and detailed error handling
    - Google docstring documentation with examples and interpretation guidance

Example:
    >>> from mcp.analytics.performance import calculate_returns_metrics, calculate_risk_metrics
    >>> import pandas as pd
    >>> import numpy as np
    >>> 
    >>> # Create sample return data
    >>> dates = pd.date_range('2020-01-01', periods=252, freq='D')
    >>> returns = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
    >>> 
    >>> # Calculate comprehensive return metrics
    >>> return_metrics = calculate_returns_metrics(returns)
    >>> print(f"Total Return: {return_metrics['total_return_pct']}")
    >>> print(f"Annual Return: {return_metrics['annual_return_pct']}")
    >>> 
    >>> # Calculate risk metrics
    >>> risk_metrics = calculate_risk_metrics(returns, risk_free_rate=0.02)
    >>> print(f"Sharpe Ratio: {risk_metrics['sharpe_ratio']:.3f}")
    >>> print(f"Max Drawdown: {risk_metrics['max_drawdown_pct']}")
    >>> print(f"VaR 95%: {risk_metrics['var_95_pct']}")

Note:
    - All functions use empyrical library for industry-standard calculations
    - Performance metrics are calculated using proven financial formulas
    - Risk-free rate defaults to 2% but can be adjusted for current market conditions
    - VaR and CVaR calculations use historical simulation methodology
    - Drawdown analysis includes both maximum drawdown and complete drawdown series
    - Benchmark metrics require aligned time series data for accurate comparison
    - Functions handle missing data gracefully with appropriate error messages
"""

from .metrics import *

__all__ = [
    'PERFORMANCE_METRICS_FUNCTIONS',
    'calculate_returns_metrics',
    'calculate_risk_metrics',
    'calculate_benchmark_metrics',
    'calculate_drawdown_analysis'
]