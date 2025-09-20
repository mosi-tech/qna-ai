"""
Portfolio Management Module

All portfolio optimization using PyPortfolioOpt and cvxpy from requirements.txt
Portfolio analysis functions from financial-analysis-function-library.json
"""

from .optimization import *
from .simulation import *
from .metrics import (
    calculate_portfolio_metrics,
    analyze_portfolio_concentration,
    calculate_portfolio_beta,
    analyze_portfolio_turnover,
    calculate_active_share,
    perform_attribution,
    calculate_portfolio_var,
    stress_test_portfolio,
    PORTFOLIO_ANALYSIS_FUNCTIONS
)

__all__ = [
    'PORTFOLIO_OPTIMIZATION_FUNCTIONS',
    'PORTFOLIO_SIMULATION_FUNCTIONS',
    'PORTFOLIO_ANALYSIS_FUNCTIONS',
    'optimize_portfolio',
    'calculate_efficient_frontier',
    'optimize_max_sharpe',
    'optimize_min_volatility',
    'calculate_risk_parity',
    'simulate_dca_strategy',
    'backtest_strategy',
    'calculate_portfolio_metrics',
    'analyze_portfolio_concentration',
    'calculate_portfolio_beta',
    'analyze_portfolio_turnover',
    'calculate_active_share',
    'perform_attribution',
    'calculate_portfolio_var',
    'stress_test_portfolio'
]