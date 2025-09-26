"""Comparison Analysis Package.

This package provides comprehensive financial comparison and analysis tools using industry-standard
libraries like empyrical and pandas for statistical analysis. The module implements atomic comparison
functions for assets, strategies, portfolios, and fundamental analysis with standardized outputs
and comprehensive error handling.

Modules:
    metrics: All comparison analysis functions with standardized outputs

Available Comparison Functions:
    Performance Comparison:
        - compare_performance_metrics: Compare key performance metrics between two assets/strategies
        - compare_risk_metrics: Compare comprehensive risk metrics and distributions
        - compare_drawdowns: Analyze and compare drawdown characteristics over time
    
    Market Analysis:
        - compare_volatility_profiles: Compare rolling volatility patterns and stability
        - compare_correlation_stability: Analyze correlation changes and regime patterns
        - compare_liquidity: Compare trading volume and liquidity characteristics
    
    Portfolio/Fund Analysis:
        - compare_sector_exposure: Compare sector allocation and concentration metrics
        - compare_expense_ratios: Compare fund costs and long-term impact analysis
        - compare_fundamental: Compare fundamental valuation and financial health metrics

Features:
    - Industry-standard empyrical library implementation for proven accuracy
    - Comprehensive winner determination with category-based scoring
    - Support for both price and return data with automatic alignment
    - Standardized return format with success indicators and error handling
    - Statistical significance testing and confidence intervals where applicable
    - Performance optimized using pandas and numpy for large datasets
    - Google docstring documentation with examples and interpretation guidance

Example:
    >>> from mcp.analytics.comparison import compare_performance_metrics, compare_risk_metrics
    >>> import pandas as pd
    >>> 
    >>> # Compare two assets' performance
    >>> returns_spy = pd.Series([0.01, -0.02, 0.015, 0.008, -0.005])
    >>> returns_qqq = pd.Series([0.02, -0.025, 0.018, 0.012, -0.008])
    >>> 
    >>> # Performance comparison
    >>> perf_comparison = compare_performance_metrics(returns_spy, returns_qqq)
    >>> print(f"Winner: {perf_comparison['summary']['overall_winner']}")
    >>> print(f"Annual Return Difference: {perf_comparison['metrics_comparison']['annual_return']['difference']:.2%}")
    >>> 
    >>> # Risk analysis
    >>> risk_comparison = compare_risk_metrics(returns_spy, returns_qqq)
    >>> print(f"Lower Risk Asset: {risk_comparison['summary']['lower_risk_asset']}")
    >>> print(f"Volatility Difference: {risk_comparison['risk_comparison']['volatility']['difference']:.3f}")

Note:
    - All functions require aligned time series data for accurate comparison
    - Statistical comparisons use empyrical library for industry-standard calculations
    - Winner determination is based on category-specific criteria (higher returns vs lower risk)
    - Functions handle missing data and provide detailed error messages
    - Results include both absolute differences and relative performance metrics
"""

from .metrics import *