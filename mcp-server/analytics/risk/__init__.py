"""
Risk Analysis Module

Comprehensive risk measurement and analysis for financial instruments and portfolios.
This module implements industry-standard risk metrics using established libraries
(empyrical, scipy) for accurate and reliable risk quantification.

Key Functionality:
    - Volatility analysis (realized volatility, conditional volatility)
    - Downside risk metrics (downside deviation, downside capture ratios)
    - Tail risk measures (Value-at-Risk, Conditional Value-at-Risk)
    - Risk-adjusted performance metrics (Sharpe ratio, Sortino ratio, Information ratio)
    - Correlation and diversification analysis
    - Beta and systematic risk calculation
    - Maximum drawdown and recovery analysis
    - Stress testing and scenario analysis

All metrics use proven statistical methods and industry-standard definitions:
    - Volatility annualized using sqrt(time) scaling
    - Risk-free rate adjustable for different scenarios
    - Multiple return frequency support (daily, weekly, monthly)
    - Robust handling of missing data and edge cases

Example:
    >>> from analytics.risk import calculate_var, calculate_max_drawdown, calculate_sharpe_ratio
    >>> import pandas as pd
    >>> returns = pd.Series([-0.02, 0.01, 0.03, -0.01, 0.02])
    >>> 
    >>> var_95 = calculate_var(returns, confidence=0.95)
    >>> max_dd = calculate_max_drawdown(returns)
    >>> sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.02)

Risk metrics are essential for:
    - Portfolio construction and optimization
    - Risk management and capital allocation
    - Performance evaluation and attribution
    - Regulatory compliance and reporting
    - Investment decision-making
"""

from .metrics import *
from .models import *

