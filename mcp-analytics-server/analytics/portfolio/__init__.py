"""
Portfolio Management Module

All portfolio optimization using PyPortfolioOpt and cvxpy from requirements.txt
From financial-analysis-function-library.json
"""

from .optimization import *
from .simulation import *

__all__ = [
    'PORTFOLIO_OPTIMIZATION_FUNCTIONS',
    'PORTFOLIO_SIMULATION_FUNCTIONS',
    'optimize_portfolio',
    'calculate_efficient_frontier',
    'optimize_max_sharpe',
    'optimize_min_volatility',
    'calculate_risk_parity',
    'simulate_dca_strategy',
    'backtest_strategy'
]